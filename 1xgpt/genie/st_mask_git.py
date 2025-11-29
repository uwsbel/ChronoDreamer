import math

import mup
import torch
import torch.nn as nn
import torch.nn.functional as F
from einops import rearrange
from huggingface_hub import PyTorchModelHubMixin
from tqdm import tqdm
from transformers.utils import ModelOutput

from genie.factorization_utils import FactorizedEmbedding, factorize_labels
from genie.config import GenieConfig
from genie.st_transformer import STTransformerDecoder


def cosine_schedule(u):
    """ u in [0, 1] """
    if isinstance(u, torch.Tensor):
        cls = torch
    elif isinstance(u, float):
        cls = math
    else:
        raise NotImplementedError(f"Unexpected {type(u)=} {u=}")

    return cls.cos(u * cls.pi / 2)


class STMaskGIT(nn.Module, PyTorchModelHubMixin):
    # Next-Token prediction as done in https://arxiv.org/pdf/2402.15391.pdf
    def __init__(self, config: GenieConfig):
        super().__init__()
        self.h = self.w = math.isqrt(config.S)
        assert self.h**2 == config.S, "Expected S to be square"

        self.decoder = STTransformerDecoder(config)

        # Position embeddings: S+1 to include action token per frame
        self.pos_embed_TSC = torch.nn.Parameter(
            torch.zeros(1, config.T, config.S + 1, config.d_model)
        )
        self.mask_token_id = config.image_vocab_size

        self.token_embed = FactorizedEmbedding(
            factored_vocab_size=config.factored_vocab_size,
            num_factored_vocabs=config.num_factored_vocabs,
            d_model=config.d_model,
            mask_token_id=self.mask_token_id,
        )

        # Action embedding with proper scaling
        # Actions are 3 floats - normalize and project to d_model
        self.action_embed = nn.Sequential(
            nn.Linear(3, config.d_model),
            nn.LayerNorm(config.d_model),  # Ensures similar scale to token embeddings
        )

        cls = FixedMuReadout if config.use_mup else nn.Linear
        self.out_x_proj = cls(config.d_model, config.factored_vocab_size * config.num_factored_vocabs)
        
        self.out_contact_proj = cls(config.d_model, config.factored_vocab_size * config.num_factored_vocabs)
        
        self.config = config

    def embed_with_actions(
        self, 
        x_TS: torch.LongTensor, 
        actions: torch.FloatTensor
    ) -> torch.FloatTensor:
        """
        Embed video tokens and prepend action token to each frame.
        
        Args:
            x_TS: (B, T, S) - video token ids
            actions: (B, T, 3) - action vectors for ALL frames
            
        Returns:
            x_TSC: (B, T, S+1, d_model) - with action as first token per frame
        """
        B, T, S = x_TS.shape
        
        # Embed video tokens: (B, T, S, d_model)
        video_emb = self.token_embed(x_TS)
        
        # Embed and normalize actions: (B, T, d_model)
        action_emb = self.action_embed(actions)
        action_emb = action_emb.unsqueeze(2)  # (B, T, 1, d_model)
        
        # Concatenate: [action, video_tokens] for each frame
        x_TSC = torch.cat([action_emb, video_emb], dim=2)  # (B, T, S+1, d_model)
        
        return x_TSC


    def generate(
        self,
        input_ids: torch.LongTensor,
        attention_mask: torch.LongTensor,
        max_new_tokens: int,
        actions: torch.FloatTensor = None,  # Changed: full actions sequence
        min_new_tokens: int = None,
        return_logits: int = False,
        return_contact: bool = False,
        maskgit_steps: int = 1,
        temperature: float = 0.0,
    ) -> tuple[torch.LongTensor, torch.FloatTensor]:
        """..."""
        assert min_new_tokens in (None, max_new_tokens)
        assert max_new_tokens % self.config.S == 0
        num_new_frames = max_new_tokens // self.config.S

        inputs_THW = rearrange(input_ids.clone(), "b (t h w) -> b t h w", h=self.h, w=self.w)
        num_prompt_frames = inputs_THW.size(1)
        
        inputs_masked_THW = torch.cat([
            inputs_THW,
            torch.full((input_ids.size(0), num_new_frames, self.h, self.w),
                       self.mask_token_id, dtype=torch.long, device=input_ids.device)
        ], dim=1)

        # Handle missing actions
        total_frames = inputs_masked_THW.size(1)
        if actions is None:
            actions = torch.zeros(input_ids.size(0), total_frames, 3, 
                                  device=input_ids.device, dtype=torch.float32)

        all_factored_logits = []
        for timestep in range(num_prompt_frames, total_frames):
            sample_HW, factored_logits = self.maskgit_generate(
                inputs_masked_THW,
                timestep,
                actions=actions,  # Pass full actions
                maskgit_steps=maskgit_steps,
                temperature=temperature
            )
            inputs_masked_THW[:, timestep] = sample_HW
            all_factored_logits.append(factored_logits)

        predicted_video_tokens = rearrange(inputs_masked_THW, "B T H W -> B (T H W)")
        
        contact_tokens = None
        if return_contact:
            contact_tokens = self.generate_contact(
                inputs_masked_THW, 
                actions=actions,
                num_prompt_frames=num_prompt_frames,
                temperature=temperature
            )
        
        if return_contact:
            if return_logits:
                return predicted_video_tokens, contact_tokens, torch.stack(all_factored_logits, dim=3)
            else:
                return predicted_video_tokens, contact_tokens
        else:
            if return_logits:
                return predicted_video_tokens, torch.stack(all_factored_logits, dim=3)
            else:
                return predicted_video_tokens

    @torch.no_grad()
    def generate_contact(
        self,
        video_THW: torch.LongTensor,
        actions: torch.FloatTensor = None,  # Changed: full actions
        num_prompt_frames: int = None,
        temperature: float = 0.0,
    ) -> torch.LongTensor:
        """Generate contact predictions."""
        bs, t, h, w = video_THW.shape
        num_future_frames = t - num_prompt_frames
        
        # Handle missing actions
        if actions is None:
            actions = torch.zeros(bs, t, 3, device=video_THW.device, dtype=torch.float32)
        
        # MASK future video frames
        video_THW_masked = video_THW.clone()
        video_THW_masked[:, num_prompt_frames:] = self.mask_token_id
        
        x_TS = rearrange(video_THW_masked, "B T H W -> B T (H W)")
        
        # Embed with all actions
        x_TSC = self.embed_with_actions(x_TS, actions)
        x_TSC = self.decoder(x_TSC + self.pos_embed_TSC)
        
        # Extract video tokens (remove action token)
        x_TSC_video = x_TSC[:, :, 1:, :]
        
        contact_logits_TSC = self.out_contact_proj(x_TSC_video)
        contact_logits_CTHW = rearrange(contact_logits_TSC, "B T (H W) C -> B C T H W", H=h, W=w)
        contact_logits_future = contact_logits_CTHW[:, :, num_prompt_frames:]
        
        factored_logits = rearrange(
            contact_logits_future,
            "b (num_vocabs vocab_size) t h w -> b vocab_size num_vocabs t h w",
            vocab_size=self.config.factored_vocab_size,
            num_vocabs=self.config.num_factored_vocabs
        )
        
        contact_tokens = torch.zeros((bs, num_future_frames, h, w), dtype=torch.long, device=video_THW.device)
        
        for t_idx in range(num_future_frames):
            frame_logits = factored_logits[:, :, :, t_idx]
            frame_probs = torch.nn.functional.softmax(frame_logits, dim=1)
            
            samples_HW = torch.zeros((bs, h, w), dtype=torch.long, device=video_THW.device)
            for probs in frame_probs.flip(2).unbind(2):
                if temperature <= 1e-8:
                    sample = probs.argmax(dim=1)
                else:
                    dist = torch.distributions.categorical.Categorical(
                        probs=rearrange(probs, "b vocab_size h w -> b h w vocab_size") / temperature
                    )
                    sample = dist.sample()
                samples_HW *= self.config.factored_vocab_size
                samples_HW += sample
            
            contact_tokens[:, t_idx] = samples_HW
        
        return contact_tokens

    @staticmethod
    def init_mask(prompt_THW):
        # since we generate 1 image at a time, the mask should be for a single frame, not across all frames.
        T, H, W = prompt_THW.size(1), prompt_THW.size(2), prompt_THW.size(3)
        unmasked = torch.zeros(prompt_THW.size(0), H * W, dtype=torch.bool, device=prompt_THW.device)
        return unmasked

    @torch.no_grad()
    def maskgit_generate(
        self,
        prompt_THW: torch.LongTensor,
        out_t: int,
        actions: torch.FloatTensor = None,  # Changed: full actions
        maskgit_steps: int = 1,
        temperature: float = 0.0,
        unmask_mode: str = "random",
    ) -> tuple[torch.LongTensor, torch.FloatTensor]:
        """..."""
        assert out_t, "maskgit_generate requires out_t > 0"
        assert torch.all(prompt_THW[:, out_t:] == self.mask_token_id)

        bs, t, h, w = prompt_THW.size()
        
        # Handle missing actions
        if actions is None:
            actions = torch.zeros(bs, t, 3, device=prompt_THW.device, dtype=torch.float32)

        unmasked = self.init_mask(prompt_THW)

        logits_CTHW = self.compute_logits(prompt_THW, actions)
        logits_CHW = logits_CTHW[:, :, out_t]
        orig_logits_CHW = logits_CHW.clone()
        
        for step in tqdm(range(maskgit_steps)):
            if step > 0:
                logits_CHW = self.compute_logits(prompt_THW, actions)[:, :, out_t]
        
            factored_logits = rearrange(logits_CHW, "b (num_vocabs vocab_size) h w -> b vocab_size num_vocabs h w",
                                        vocab_size=self.config.factored_vocab_size,
                                        num_vocabs=self.config.num_factored_vocabs)

            factored_probs = torch.nn.functional.softmax(factored_logits, dim=1)

            samples_HW = torch.zeros((bs, h, w), dtype=torch.long, device=prompt_THW.device)
            confidences_HW = torch.ones((bs, h, w), dtype=torch.float, device=prompt_THW.device)
            for probs in factored_probs.flip(2).unbind(2):
                if temperature <= 1e-8:
                    sample = probs.argmax(dim=1)
                else:
                    dist = torch.distributions.categorical.Categorical(
                        probs=rearrange(probs, "b vocab_size ... -> b ... vocab_size") / temperature
                    )
                    sample = dist.sample()
                samples_HW *= self.config.factored_vocab_size
                samples_HW += sample
                confidences_HW *= torch.gather(probs, 1, sample.unsqueeze(1)).squeeze(1)

            prev_unmasked = unmasked.clone()
            prev_img_flat = rearrange(prompt_THW[:, out_t], "B H W -> B (H W)")
            samples_flat = samples_HW.reshape(bs, self.config.S)

            if step != maskgit_steps - 1:
                n = math.ceil(cosine_schedule((step + 1) / maskgit_steps) * self.config.S)

                if unmask_mode == "greedy":
                    confidences_flat = confidences_HW.reshape(bs, self.config.S)
                elif unmask_mode == "random":
                    confidences_flat = torch.rand_like(confidences_HW).reshape(bs, self.config.S)
                else:
                    raise NotImplementedError

                confidences_flat[unmasked] = torch.inf
                least_confident_tokens = torch.argsort(confidences_flat, dim=1)
                unmasked.scatter_(1, least_confident_tokens[:, n:], True)
                samples_flat.scatter_(1, least_confident_tokens[:, :n], self.mask_token_id)

            samples_flat[prev_unmasked] = prev_img_flat[prev_unmasked]
            samples_HW = samples_flat.reshape(-1, h, w)
            prompt_THW[:, out_t] = samples_HW

        return samples_HW, rearrange(
            orig_logits_CHW, "B (num_vocabs vocab_size) H W -> B vocab_size num_vocabs H W",
            vocab_size=self.config.factored_vocab_size, num_vocabs=self.config.num_factored_vocabs, H=h, W=w
        )

    def compute_loss_and_acc(self, logits_CTHW, targets_THW, relevant_mask_THW):
        # Video token prediction
        targets_THW = targets_THW.clone()
        logits_CTHW, targets_THW = logits_CTHW[:, :, 1:], targets_THW[:, 1:]  # first frame always unmasked

        factored_logits = rearrange(logits_CTHW,
                                    "b (num_vocabs vocab_size) t h w -> b vocab_size num_vocabs t h w",
                                    vocab_size=self.config.factored_vocab_size,
                                    num_vocabs=self.config.num_factored_vocabs)
        
        # FIX: Pass config values instead of using defaults
        factored_targets = factorize_labels(
            targets_THW, 
            num_factored_vocabs=self.config.num_factored_vocabs,
            factored_vocab_size=self.config.factored_vocab_size
        )

        loss_THW = F.cross_entropy(factored_logits, factored_targets, reduction="none").sum(dim=1)
        acc_THW = (factored_logits.argmax(dim=1) == factored_targets).all(dim=1)

        # Compact debug
        t_stats = (factored_targets.shape, int(factored_targets.min()), int(factored_targets.max()), len(torch.unique(factored_targets)))
        l_stats = (loss_THW.min().item(), loss_THW.max().item(), loss_THW[relevant_mask_THW].mean().item())
        a_stats = (acc_THW[relevant_mask_THW].sum().item(), relevant_mask_THW.sum().item(), acc_THW[relevant_mask_THW].float().mean().item())
        print(f"[Video] targets={t_stats}, loss(min/max/masked)={l_stats[0]:.2f}/{l_stats[1]:.2f}/{l_stats[2]:.2f}, acc={a_stats[0]}/{a_stats[1]}={a_stats[2]:.4f}", flush=True)

        # Compute the mean masked error.
        # Multiply loss values by mask instead of indexing them, more computationally efficient.
        num_masked_tokens = torch.sum(relevant_mask_THW)
        relevant_loss = torch.sum(loss_THW * relevant_mask_THW) / num_masked_tokens
        relevant_acc = torch.sum(acc_THW * relevant_mask_THW).float() / num_masked_tokens

        # only optimize on the masked/noised logits?
        return relevant_loss, relevant_acc

    def compute_contact_loss_and_acc(self, logits_CTHW, targets_THW, relevant_mask_THW):
        """
        Compute contact prediction loss using Focal Loss for sparse/imbalanced data.
        logits_CTHW: (B, C, T-1, H, W) - logits for future frames
        targets_THW: (B, T-1, H, W) - contact labels for future frames
        relevant_mask_THW: (B, T-1, H, W) - mask indicating which tokens were masked
        """
        
        factored_logits = rearrange(logits_CTHW,
                                    "b (num_vocabs vocab_size) t h w -> b vocab_size num_vocabs t h w",
                                    vocab_size=self.config.factored_vocab_size,
                                    num_vocabs=self.config.num_factored_vocabs)
        
        factored_targets = factorize_labels(
            targets_THW, 
            num_factored_vocabs=self.config.num_factored_vocabs,
            factored_vocab_size=self.config.factored_vocab_size
        )

        factored_stats = (factored_targets.shape, int(factored_targets.min()), int(factored_targets.max()), len(torch.unique(factored_targets)))
        print(f"[Contact] targets: shape/min/max/unique={factored_stats}", flush=True)

        # Focal Loss: (1 - p_t)^gamma * CE
        gamma = 0.0
        ce_loss = F.cross_entropy(factored_logits, factored_targets, reduction="none")
        p_t = torch.exp(-ce_loss)
        focal_weight = (1 - p_t) ** gamma
        focal_loss = focal_weight * ce_loss
        loss_THW = focal_loss.sum(dim=1)
        
        acc_THW = (factored_logits.argmax(dim=1) == factored_targets).all(dim=1)

        # Compact debug
        l_stats = (loss_THW.min().item(), loss_THW.max().item(), loss_THW[relevant_mask_THW].mean().item())
        a_stats = (acc_THW[relevant_mask_THW].sum().item(), relevant_mask_THW.sum().item(), acc_THW[relevant_mask_THW].float().mean().item())
        print(f"[Contact] loss(min/max/masked)={l_stats[0]:.2f}/{l_stats[1]:.2f}/{l_stats[2]:.2f}, acc={a_stats[2]:.4f}", flush=True)

        # Compute the mean masked error
        num_masked_tokens = torch.sum(relevant_mask_THW)
        relevant_loss = torch.sum(loss_THW * relevant_mask_THW) / num_masked_tokens
        relevant_acc = torch.sum(acc_THW * relevant_mask_THW).float() / num_masked_tokens

        return relevant_loss, relevant_acc

    def compute_logits(self, x_THW, actions=None):  # Changed signature
        x_TS = rearrange(x_THW, "B T H W -> B T (H W)")
        
        # Handle missing actions
        if actions is None:
            actions = torch.zeros(x_THW.size(0), x_THW.size(1), 3, 
                                  device=x_THW.device, dtype=torch.float32)
        
        # Embed with actions
        x_TSC = self.embed_with_actions(x_TS, actions)
        x_TSC = self.decoder(x_TSC + self.pos_embed_TSC)
        
        # Extract video tokens (remove action token)
        x_TSC_video = x_TSC[:, :, 1:, :]
        
        x_next_TSC = self.out_x_proj(x_TSC_video)
        logits_CTHW = rearrange(x_next_TSC, "B T (H W) C -> B C T H W", H=self.h, W=self.w)
        return logits_CTHW

    def forward(self, input_ids, labels, actions=None, contact_labels=None, **kwargs):
        T, H, W = self.config.T, self.h, self.w
        x_THW = rearrange(input_ids, "B (T H W) -> B T H W", T=T, H=H, W=W)
        x_TS = rearrange(x_THW, "B T H W -> B T (H W)")

        # Handle missing actions
        if actions is None:
            actions = torch.zeros(input_ids.size(0), T, 3, 
                                  device=input_ids.device, dtype=torch.float32)
        
        # Embed with actions
        x_TSC = self.embed_with_actions(x_TS, actions)
        x_TSC = self.decoder(x_TSC + self.pos_embed_TSC)
        
        # Extract video tokens (remove action token)
        x_TSC_video = x_TSC[:, :, 1:, :]
        
        video_logits_TSC = self.out_x_proj(x_TSC_video)
        logits_CTHW = rearrange(video_logits_TSC, "B T (H W) C -> B C T H W", H=H, W=W)

        labels = rearrange(labels, "B (T H W) -> B T H W", T=T, H=H, W=W)

        relevant_mask = x_THW[:, 1:] == self.mask_token_id
        video_loss, video_acc = self.compute_loss_and_acc(logits_CTHW, labels, relevant_mask)

        contact_loss = torch.tensor(0.0, device=input_ids.device)
        contact_acc = torch.tensor(0.0, device=input_ids.device)
        if contact_labels is not None:
            contact_logits_TSC = self.out_contact_proj(x_TSC_video)
            contact_logits_CTHW = rearrange(contact_logits_TSC, "B T (H W) C -> B C T H W", H=H, W=W)
            
            contact_logits_future = contact_logits_CTHW[:, :, 1:]
            contact_labels_THW = rearrange(contact_labels, "B (T H W) -> B T H W", T=T, H=H, W=W)
            contact_labels_future = contact_labels_THW[:, 1:]
            
            contact_loss, contact_acc = self.compute_contact_loss_and_acc(
                contact_logits_future, contact_labels_future, relevant_mask
            )
        
        contact_weight = getattr(self.config, 'contact_loss_weight', 1.0)
        total_loss = video_loss + contact_weight * contact_loss

        return ModelOutput(
            loss=total_loss, 
            video_loss=video_loss,
            contact_loss=contact_loss,
            acc=video_acc,
            contact_acc=contact_acc,
            logits=logits_CTHW
        )

    def init_weights(self):
        """ Works with and without muP. """
        std = 0.02
        for module in self.modules():
            if isinstance(module, nn.Linear):
                if hasattr(module.weight, "infshape"):  # muP
                    mup.normal_(module.weight, mean=0.0, std=std)
                else:
                    module.weight.data.normal_(mean=0.0, std=std)

                if module.bias is not None:
                    module.bias.data.zero_()
            elif isinstance(module, nn.Embedding):
                module.weight.data.normal_(mean=0.0, std=std)
                if module.padding_idx is not None:
                    module.weight.data[module.padding_idx].zero_()

    def set_mup_shapes(self, rescale_params=False):
        base_config = self.config.shallow_copy()
        base_config.num_heads = 8
        base_config.d_model = 256  # currently hardcoding to this shape
        base_model = STMaskGIT(base_config)

        mup.set_base_shapes(self, base_model, rescale_params=rescale_params)
        
    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        """ Extra logic for muP. """
        model = super().from_pretrained(*args, **kwargs)
        if model.config.use_mup:
            model.set_mup_shapes(rescale_params=False)

        return model


class FixedMuReadout(mup.MuReadout):
    def forward(self, x):
        """
        Using `return super(mup.MuReadout, self).forward(self.output_mult * x / self.width_mult())` with `torch.compile`
        results in two divisions by `self.width_mult()` for some reason
        """
        # return F.linear(self.output_mult * x / self.width_mult(), self.weight, self.bias)  # equivalent
        return nn.Linear.forward(self, self.output_mult * x / self.width_mult())

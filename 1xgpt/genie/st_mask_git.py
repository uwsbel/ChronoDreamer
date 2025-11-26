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

        self.pos_embed_TSC = torch.nn.Parameter(torch.zeros(1, config.T, config.S, config.d_model))
        self.mask_token_id = config.image_vocab_size

        self.token_embed = FactorizedEmbedding(  # also works for num_factored_vocabs = 1
            factored_vocab_size=config.factored_vocab_size,
            num_factored_vocabs=config.num_factored_vocabs,
            d_model=config.d_model,
            mask_token_id=self.mask_token_id,
        )

        cls = FixedMuReadout if config.use_mup else nn.Linear
        self.out_x_proj = cls(config.d_model, config.factored_vocab_size * config.num_factored_vocabs)
        
        # Contact prediction head
        contact_vocab_size = getattr(config, 'contact_vocab_size', config.image_vocab_size)
        self.out_contact_proj = cls(config.d_model, config.factored_vocab_size * config.num_factored_vocabs)
        
        self.config = config


    def generate(
        self,
        input_ids: torch.LongTensor,
        attention_mask: torch.LongTensor,
        max_new_tokens: int,
        history_actions: torch.FloatTensor = None,
        future_actions: torch.FloatTensor = None,
        min_new_tokens: int = None,
        return_logits: int = False,
        return_contact: bool = False,  # NEW: option to return contact predictions
        maskgit_steps: int = 1,
        temperature: float = 0.0,
    ) -> tuple[torch.LongTensor, torch.FloatTensor]:
        """
        Args designed to match the format of Llama.
        We ignore `attention_mask`, and use `max_new_tokens` to determine the number of frames to generate.

        Returns: 
            If return_contact:
                (video_tokens, contact_tokens) or (video_tokens, contact_tokens, factored_logits)
            Else:
                video_tokens or (video_tokens, factored_logits)
        """
        assert min_new_tokens in (None, max_new_tokens), \
            "Expecting `min_new_tokens`, if specified, to match `max_new_tokens`."

        assert max_new_tokens % self.config.S == 0, "Expecting `max_new_tokens` to be a multiple of `self.config.S`."
        num_new_frames = max_new_tokens // self.config.S

        inputs_THW = rearrange(input_ids.clone(), "b (t h w) -> b t h w", h=self.h, w=self.w)
        inputs_masked_THW = torch.cat([
            inputs_THW,
            torch.full((input_ids.size(0), num_new_frames, self.h, self.w),
                       self.mask_token_id, dtype=torch.long, device=input_ids.device)
        ], dim=1)

        all_factored_logits = []
        for timestep in range(inputs_THW.size(1), inputs_THW.size(1) + num_new_frames):
            # could change sampling hparams
            sample_HW, factored_logits = self.maskgit_generate(
                inputs_masked_THW,
                timestep,
                history_actions=history_actions,
                future_actions=future_actions,
                maskgit_steps=maskgit_steps,
                temperature=temperature
            )
            inputs_masked_THW[:, timestep] = sample_HW
            all_factored_logits.append(factored_logits)

        predicted_video_tokens = rearrange(inputs_masked_THW, "B T H W -> B (T H W)")
        
        # Generate contact predictions if requested
        contact_tokens = None
        if return_contact:
            contact_tokens = self.generate_contact(
                inputs_masked_THW, 
                history_actions=history_actions,
                future_actions=future_actions,
                num_prompt_frames=inputs_THW.size(1),
                temperature=temperature
            )
        
        # Return based on options
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
        history_actions: torch.FloatTensor = None,
        future_actions: torch.FloatTensor = None,
        num_prompt_frames: int = None,
        temperature: float = 0.0,
    ) -> torch.LongTensor:
        """
        Generate contact predictions given ONLY the history video tokens.
        Future frames are masked to match training distribution.
        
        Args:
            video_THW: (B, T, H, W) - full video sequence (prompt + generated)
            num_prompt_frames: number of prompt/history frames
            
        Returns:
            contact_tokens: (B, num_future_frames, H, W) - predicted contact for future frames
        """
        bs, t, h, w = video_THW.shape
        num_future_frames = t - num_prompt_frames
        
        # MASK future frames - contact prediction should only use history tokens!
        # This matches training where future frames are masked
        video_THW_masked = video_THW.clone()
        video_THW_masked[:, num_prompt_frames:] = self.mask_token_id
        
        # Get hidden states from the transformer (using masked input)
        x_TS = rearrange(video_THW_masked, "B T H W -> B T (H W)")
        x_TSC = self.token_embed(x_TS)
        x_TSC = self.decoder(x_TSC + self.pos_embed_TSC,
                            history_actions=history_actions,
                            future_actions=future_actions)
        
        # Get contact logits
        contact_logits_TSC = self.out_contact_proj(x_TSC)
        contact_logits_CTHW = rearrange(contact_logits_TSC, "B T (H W) C -> B C T H W", H=h, W=w)
        
        # Only take future frames
        contact_logits_future = contact_logits_CTHW[:, :, num_prompt_frames:]  # (B, C, num_future, H, W)
        
        # Convert logits to tokens (greedy or sampled)
        factored_logits = rearrange(
            contact_logits_future,
            "b (num_vocabs vocab_size) t h w -> b vocab_size num_vocabs t h w",
            vocab_size=self.config.factored_vocab_size,
            num_vocabs=self.config.num_factored_vocabs
        )
        
        # Sample or argmax for each position
        contact_tokens = torch.zeros((bs, num_future_frames, h, w), dtype=torch.long, device=video_THW.device)
        
        for t_idx in range(num_future_frames):
            frame_logits = factored_logits[:, :, :, t_idx]  # (B, vocab_size, num_vocabs, H, W)
            frame_probs = torch.nn.functional.softmax(frame_logits, dim=1)
            
            samples_HW = torch.zeros((bs, h, w), dtype=torch.long, device=video_THW.device)
            for probs in frame_probs.flip(2).unbind(2):  # iterate over factored vocabs
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
        history_actions: torch.FloatTensor = None,  # Add this
        future_actions: torch.FloatTensor = None,   # Add this
        maskgit_steps: int = 1,
        temperature: float = 0.0,
        unmask_mode: str = "random",
    ) -> tuple[torch.LongTensor, torch.FloatTensor]:
        """
        Performs MaskGIT-style inference to predict frame `out_t`.

        Args:
            prompt_THW: Unfactorized token ids, size (B, T, H, W)
            out_t: Will return predicted unfactorized token ids for this frame.
                Should be >= 1 as the 0th frame is assumed to be given.
                Expects all future frames to be fully masked.
            maskgit_steps: The number of MaskGIT-style inference steps to take.
            temperature: Sampling temperature.
                In the factorized case, sampling is performed for each factorized vocabulary independently.
                If temperature is <= 1e-8, will be greedy (i.e. argmax) instead of actual sampling.
            unmask_mode: The method to determine tokens to unmask during each step of MaskGIT inference.
                Options:
                    - "greedy" for unmasking the most confident tokens, which is matches the original MaskGIT
                    - "random" for randomly choosing tokens to unmask
                "greedy" tends to copy the previous frame, so we default to "random" instead.

        Returns: (sample_HW, factored_logits)
            sample_HW: size (B, H, W) corresponding to predicted unfactorized token ids for frame `out_t`.
            factored_logits: size (B, factored_vocab_size, num_factored_vocabs, H, W).
        """
        # assume we have pre-masked z{out_t}...zT with all masks
        assert out_t, "maskgit_generate requires out_t > 0"
        assert torch.all(prompt_THW[:, out_t:] == self.mask_token_id), \
            f"when generating z{out_t}, frames {out_t} and later must be masked"

        bs, t, h, w = prompt_THW.size(0), prompt_THW.size(1), prompt_THW.size(2), prompt_THW.size(3)

        # this will be modified in place on each iteration of this loop
        unmasked = self.init_mask(prompt_THW)

        # Pass actions to compute_logits
        logits_CTHW = self.compute_logits(prompt_THW, history_actions, future_actions)
        logits_CHW = logits_CTHW[:, :, out_t]
        orig_logits_CHW = logits_CHW.clone()
        
        for step in tqdm(range(maskgit_steps)):
            if step > 0:
                # Pass actions here too
                logits_CHW = self.compute_logits(prompt_THW, history_actions, future_actions)[:, :, out_t]
        
            factored_logits = rearrange(logits_CHW, "b (num_vocabs vocab_size) h w -> b vocab_size num_vocabs h w",
                                        vocab_size=self.config.factored_vocab_size,
                                        num_vocabs=self.config.num_factored_vocabs)

            factored_probs = torch.nn.functional.softmax(factored_logits, dim=1)

            samples_HW = torch.zeros((bs, h, w), dtype=torch.long, device=prompt_THW.device)
            confidences_HW = torch.ones((bs, h, w), dtype=torch.float, device=prompt_THW.device)
            for probs in factored_probs.flip(2).unbind(2):
                if temperature <= 1e-8:  # greedy sampling
                    sample = probs.argmax(dim=1)
                else:
                    # Categorical expects last dim to be channel dim
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

            if step != maskgit_steps - 1:  # skip masking for last maskgit step
                # use cosine mask scheduling function, n is how many of frame out_t to mask
                n = math.ceil(cosine_schedule((step + 1) / maskgit_steps) * self.config.S)

                if unmask_mode == "greedy":
                    # set the n patches with the least confidence to mask_token
                    confidences_flat = confidences_HW.reshape(bs, self.config.S)
                elif unmask_mode == "random":
                    # randomize confidences, so that patches are randomly masked
                    confidences_flat = torch.rand_like(confidences_HW).reshape(bs, self.config.S)
                    # not probability distribution anymore, but only relative order matters
                else:
                    raise NotImplementedError(f"Expected `unmask_mode` to be one of ['greedy', 'random'], "
                                              f"got {unmask_mode}")

                confidences_flat[unmasked] = torch.inf
                least_confident_tokens = torch.argsort(confidences_flat, dim=1)
                # unmask the (self.config.S - n) most confident tokens
                unmasked.scatter_(1, least_confident_tokens[:, n:], True)
                samples_flat.scatter_(1, least_confident_tokens[:, :n], self.mask_token_id)

            # copy previously unmasked values from prompt input into sample
            samples_flat[prev_unmasked] = prev_img_flat[prev_unmasked]
            samples_HW = samples_flat.reshape(-1, h, w)

            # feed back to iteratively decode
            prompt_THW[:, out_t] = samples_HW

        # Return the final sample and logits
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


        print(f"\nTargets debug:")
        print(f"  factored_targets shape: {factored_targets.shape}")
        print(f"  factored_targets min: {factored_targets.min().item()}")
        print(f"  factored_targets max: {factored_targets.max().item()}")
        print(f"  unique targets: {torch.unique(factored_targets).shape[0]}")

        # DEBUG: Print shapes and sample values
        print(f"\n=== Loss/Accuracy Debug ===")
        print(f"loss_THW shape: {loss_THW.shape}")
        print(f"acc_THW shape: {acc_THW.shape}")
        print(f"relevant_mask_THW shape: {relevant_mask_THW.shape}")
        
        print(f"\nLoss values (first 10 masked positions):")
        masked_losses = loss_THW[relevant_mask_THW][:10]
        print(f"  {masked_losses.tolist()}")
        
        print(f"\nAccuracy values (first 10 masked positions):")
        masked_accs = acc_THW[relevant_mask_THW][:10]
        print(f"  {masked_accs.tolist()}")
        
        print(f"\nLoss statistics:")
        print(f"  Min loss: {loss_THW.min().item():.3f}")
        print(f"  Max loss: {loss_THW.max().item():.3f}")
        print(f"  Mean loss (all): {loss_THW.mean().item():.3f}")
        print(f"  Mean loss (masked): {loss_THW[relevant_mask_THW].mean().item():.3f}")
        
        print(f"\nAccuracy statistics:")
        print(f"  Correct predictions (masked): {acc_THW[relevant_mask_THW].sum().item()}")
        print(f"  Total masked tokens: {relevant_mask_THW.sum().item()}")
        print(f"  Accuracy (masked): {acc_THW[relevant_mask_THW].float().mean().item():.4f}")
        

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
        
         # DEBUG: Check input BEFORE factorization
        stats = (int(targets_THW.min()), int(targets_THW.max()), len(torch.unique(targets_THW)))
        print(f"[Contact] BEFORE factorize: shape={targets_THW.shape}, min/max/unique={stats}", flush=True)
        factored_logits = rearrange(logits_CTHW,
                                    "b (num_vocabs vocab_size) t h w -> b vocab_size num_vocabs t h w",
                                    vocab_size=self.config.factored_vocab_size,
                                    num_vocabs=self.config.num_factored_vocabs)
        
        factored_targets = factorize_labels(
            targets_THW, 
            num_factored_vocabs=self.config.num_factored_vocabs,
            factored_vocab_size=self.config.factored_vocab_size
        )

        factored_stats = (int(factored_targets.min()), int(factored_targets.max()), len(torch.unique(factored_targets)))
        print(f"[Contact] AFTER factorize: shape={factored_targets.shape}, min/max/unique={factored_stats}", flush=True)

        # Focal Loss: (1 - p_t)^gamma * CE
        # gamma=2.0 focuses more on hard examples (non-black contact regions)
        gamma = 0.0
        ce_loss = F.cross_entropy(factored_logits, factored_targets, reduction="none")  # (B, num_vocabs, T-1, H, W)
        p_t = torch.exp(-ce_loss)  # probability of correct class
        focal_weight = (1 - p_t) ** gamma
        focal_loss = focal_weight * ce_loss
        loss_THW = focal_loss.sum(dim=1)  # sum over num_vocabs dimension
        
        acc_THW = (factored_logits.argmax(dim=1) == factored_targets).all(dim=1)

        print(f"\n=== [Contact] Loss/Accuracy Debug (Focal Loss gamma={gamma}) ===")
        print(f"loss_THW shape: {loss_THW.shape}")
        print(f"acc_THW shape: {acc_THW.shape}")
        print(f"relevant_mask_THW shape: {relevant_mask_THW.shape}")

        print(f"\n[Contact] Loss values (first 10 masked positions):")
        masked_losses = loss_THW[relevant_mask_THW][:10]
        print(f"  {masked_losses.tolist()}")

        print(f"\n[Contact] Accuracy values (first 10 masked positions):")
        masked_accs = acc_THW[relevant_mask_THW][:10]
        print(f"  {masked_accs.tolist()}")

        print(f"\n[Contact] Loss statistics:")
        print(f"  Min loss: {loss_THW.min().item():.3f}")
        print(f"  Max loss: {loss_THW.max().item():.3f}")
        print(f"  Mean loss (all): {loss_THW.mean().item():.3f}")
        print(f"  Mean loss (masked): {loss_THW[relevant_mask_THW].mean().item():.3f}")

        print(f"\n[Contact] Accuracy statistics:")
        print(f"  Correct predictions (masked): {acc_THW[relevant_mask_THW].sum().item()}")
        print(f"  Total masked tokens: {relevant_mask_THW.sum().item()}")
        print(f"  Accuracy (masked): {acc_THW[relevant_mask_THW].float().mean().item():.4f}")

        # Compute the mean masked error
        num_masked_tokens = torch.sum(relevant_mask_THW)
        relevant_loss = torch.sum(loss_THW * relevant_mask_THW) / num_masked_tokens
        relevant_acc = torch.sum(acc_THW * relevant_mask_THW).float() / num_masked_tokens

        return relevant_loss, relevant_acc

    def compute_logits(self, x_THW, history_actions=None, future_actions=None):
        # x_THW: (B, T, H, W) - contains history frames + masked future frames
        x_TS = rearrange(x_THW, "B T H W -> B T (H W)")  # (B, T, S)
        x_TSC = self.token_embed(x_TS)  # (B, T, S, d_model)

        # Pass separate action streams to transformer
        x_TSC = self.decoder(x_TSC + self.pos_embed_TSC, 
                            history_actions=history_actions, 
                            future_actions=future_actions)
        x_next_TSC = self.out_x_proj(x_TSC)

        logits_CTHW = rearrange(x_next_TSC, "B T (H W) C -> B C T H W", H=self.h, W=self.w)
        return logits_CTHW

    def forward(self, input_ids, labels, actions=None, history_actions=None, future_actions=None, 
                contact_labels=None, **kwargs):  # Changed from future_contact to contact_labels
        T, H, W = self.config.T, self.h, self.w
        x_THW = rearrange(input_ids, "B (T H W) -> B T H W", T=T, H=H, W=W)

        # Use the separated action inputs - get hidden states
        x_TS = rearrange(x_THW, "B T H W -> B T (H W)")
        x_TSC = self.token_embed(x_TS)
        x_TSC = self.decoder(x_TSC + self.pos_embed_TSC, 
                            history_actions=history_actions, 
                            future_actions=future_actions)
        
        # Video prediction logits
        video_logits_TSC = self.out_x_proj(x_TSC)
        logits_CTHW = rearrange(video_logits_TSC, "B T (H W) C -> B C T H W", H=H, W=W)

        labels = rearrange(labels, "B (T H W) -> B T H W", T=T, H=H, W=W)

        # Record the loss over masked tokens only
        relevant_mask = x_THW[:, 1:] == self.mask_token_id
        video_loss, video_acc = self.compute_loss_and_acc(logits_CTHW, labels, relevant_mask)

        # Contact prediction loss (only computed on masked positions via relevant_mask)
        contact_loss = torch.tensor(0.0, device=input_ids.device)
        contact_acc = torch.tensor(0.0, device=input_ids.device)
        if contact_labels is not None:
            # Contact logits for all frames
            contact_logits_TSC = self.out_contact_proj(x_TSC)
            contact_logits_CTHW = rearrange(contact_logits_TSC, "B T (H W) C -> B C T H W", H=H, W=W)
            
            # Extract frames 1: onwards (same as video loss) - shape: (B, C, T-1, H, W)
            contact_logits_future = contact_logits_CTHW[:, :, 1:]
            
            # Reshape full contact labels: (B, T*H*W) -> (B, T, H, W) -> (B, T-1, H, W)
            contact_labels_THW = rearrange(contact_labels, "B (T H W) -> B T H W", T=T, H=H, W=W)
            contact_labels_future = contact_labels_THW[:, 1:]  # frames 1 to T-1
            
            # Compute contact loss only on masked positions (relevant_mask handles this)
            contact_loss, contact_acc = self.compute_contact_loss_and_acc(
                contact_logits_future, contact_labels_future, relevant_mask
            )
        
        # Combine losses
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

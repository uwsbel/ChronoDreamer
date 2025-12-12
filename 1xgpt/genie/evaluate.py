"""
Evaluation script for the GENIE pipeline.

Evaluates:
- Video frame prediction: token accuracy, loss, LPIPS
- Contact frame prediction: token accuracy, LPIPS (if contact data available)
- Joint angle prediction: MSE per joint (if joint angle data available)

Pipeline:
- Input: history_video_frames + history_actions + future_actions + history_joint_angles
- Output: predicted future_video_frames + predicted future_contact_frames + predicted future_joint_angles

Example usage:
    python genie/evaluate.py --checkpoint_dir data/genie_model/step_700000 --val_data_dir data/val_v3.0
    python genie/evaluate.py --checkpoint_dir data/genie_model/step_700000 --val_data_dir data/val_v3.0 --evaluate_contact
    python genie/evaluate.py --checkpoint_dir data/genie_model/step_700000 --val_data_dir data/val_v3.0 --evaluate_joints
"""

import argparse
import json
import time
import os
import sys
from collections import defaultdict
from pathlib import Path

import lpips
import numpy as np
import torch
import transformers
from einops import rearrange
from torch.utils.data import DataLoader
from tqdm import tqdm


# 1xgpt imports
sys.path.append(os.getcwd())
from data import RawTokenDataset, get_maskgit_collator
from visualize import decode_latents_wrapper
from eval_utils import decode_tokens, compute_lpips, AvgMetric
from genie.st_mask_git import STMaskGIT
from genie.config import GenieConfig
from genie.factorization_utils import factorize_labels


# Default values (can be overridden by args)
DEFAULT_WINDOW_SIZE = 16
DEFAULT_STRIDE = 15  # Data is ~30 Hz, so with stride 15, effective video is ~2 Hz
DEFAULT_NUM_PROMPT_FRAMES = 8  # Use first half as context


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate GENIE-style models on video and contact prediction.")
    parser.add_argument(
        "--val_data_dir", type=str, default="data/val_v3.0",
        help="A directory with video data, should have `metadata.json`, `video.bin`, and optionally `contact_splat.bin`."
    )
    parser.add_argument(
        "--checkpoint_dir", type=str, required=True,
        help="Path to a HuggingFace-style checkpoint."
    )
    parser.add_argument(
        "--batch_size", type=int, default=8,
        help="Batch size, current script only supports a single GPU."
    )
    parser.add_argument(
        "--window_size", type=int, default=DEFAULT_WINDOW_SIZE,
        help="Number of frames in a sequence."
    )
    parser.add_argument(
        "--stride", type=int, default=DEFAULT_STRIDE,
        help="Frame stride for loading data (must match training stride)."
    )
    parser.add_argument(
        "--num_prompt_frames", type=int, default=DEFAULT_NUM_PROMPT_FRAMES,
        help="Number of history/prompt frames to condition on."
    )
    parser.add_argument(
        "--maskgit_steps", type=int, default=2, 
        help="Number of MaskGIT sampling steps per frame."
    )
    parser.add_argument(
        "--temperature", type=float, default=0,
        help="Sampling temperature. If `temperature` <= 1e-8, will do greedy sampling."
    )
    parser.add_argument(
        "--evaluate_contact", action="store_true",
        help="If specified, will also evaluate contact prediction (requires contact_splat.bin in val_data_dir)."
    )
    parser.add_argument(
        "--save_outputs_dir", type=str,
        help="Debug option. If specified, will save model predictions and ground truths to this directory."
    )
    parser.add_argument(
        "--max_examples", type=int,
        help="If specified, will stop evaluation early after `max_examples` examples."
    )
    parser.add_argument(
        "--teacher_force_time", action="store_true",
        help="If True, teacher-forces generation in time dimension (uses ground truth for earlier frames)."
    )
    parser.add_argument(
        "--evaluate_joints", action="store_true",
        help="If specified, will also evaluate joint angle prediction (requires joint_angles.bin in val_data_dir)."
    )

    return parser.parse_args()


class GenieEvaluator:
    """
    Evaluator for the GENIE video prediction pipeline.
    
    Supports:
    - Video frame prediction with actions conditioning
    - Contact frame prediction
    """
    
    def __init__(self, args, decode_latents, device="cuda"):
        super().__init__()

        self.model = STMaskGIT.from_pretrained(args.checkpoint_dir)
        self.model = self.model.to(device=device)
        self.model.eval()

        self.decode_latents = decode_latents
        self.device = device
        self.args = args
        self.window_size = args.window_size
        self.num_prompt_frames = args.num_prompt_frames
        self.latent_h = args.latent_h
        self.latent_w = args.latent_w

    @torch.no_grad()
    def predict_video_frames(
        self, 
        input_ids: torch.LongTensor,
        actions: torch.FloatTensor = None,
        joint_angles: torch.FloatTensor = None,
        ground_truth_THW: torch.LongTensor = None,  # For teacher forcing
    ) -> tuple[torch.LongTensor, torch.FloatTensor]:
        """
        Predict future video frames given history frames and actions.
        
        Args:
            input_ids: LongTensor of size (B, T*H*W) - flattened tokenized video
            actions: FloatTensor of size (B, T, 3) - actions for all frames (history + future)
            joint_angles: FloatTensor of size (B, T, 4) - joint angles for all frames
            ground_truth_THW: LongTensor of size (B, T, H, W) - for teacher forcing mode
            
        Returns: (samples_THW, factored_logits)
            samples_THW: (B, num_future_frames, H, W) - predicted token ids
            factored_logits: (B, 512, 2, num_future_frames, H, W) - predicted logits
        """
        inputs_THW = rearrange(input_ids, "b (t h w) -> b t h w", 
                               t=self.window_size, h=self.latent_h, w=self.latent_w).to(self.device)
        
        if actions is not None:
            actions = actions.to(self.device)
        if joint_angles is not None:
            joint_angles = joint_angles.to(self.device)
        
        # Initialize prompt with history frames visible, future masked
        prompt_THW = inputs_THW.clone()
        prompt_THW[:, self.num_prompt_frames:] = self.model.mask_token_id
        
        all_samples = []
        all_logits = []
        
        for timestep in range(self.num_prompt_frames, self.window_size):
            # Teacher forcing: use ground truth for frames before current timestep
            if self.args.teacher_force_time and ground_truth_THW is not None:
                prompt_THW = ground_truth_THW.clone().to(self.device)
                prompt_THW[:, timestep:] = self.model.mask_token_id
            
            # MaskGIT sampling with actions and joint angles
            samples_HW, factored_logits = self.model.maskgit_generate(
                prompt_THW, 
                out_t=timestep, 
                actions=actions,
                joint_angles=joint_angles,
                maskgit_steps=self.args.maskgit_steps,
                temperature=self.args.temperature,
            )

            all_samples.append(samples_HW)
            all_logits.append(factored_logits)
            
            # Autoregressive: use predicted frame for next prediction
            if not self.args.teacher_force_time:
                prompt_THW[:, timestep] = samples_HW

        samples_THW = torch.stack(all_samples, dim=1)  # (B, num_future_frames, H, W)
        factored_logits = torch.stack(all_logits, dim=3)  # (B, 512, 2, num_future_frames, H, W)
        
        return samples_THW, factored_logits

    @torch.no_grad()
    def predict_contact_frames(
        self,
        video_THW: torch.LongTensor,
        actions: torch.FloatTensor = None,
        joint_angles: torch.FloatTensor = None,
    ) -> torch.LongTensor:
        """
        Predict future contact frames given video frames and actions.
        
        Args:
            video_THW: LongTensor of size (B, T, H, W) - full video (history + predicted future)
            actions: FloatTensor of size (B, T, 3) - actions for all frames
            joint_angles: FloatTensor of size (B, T, 4) - joint angles for all frames
            
        Returns:
            contact_tokens: (B, num_future_frames, H, W) - predicted contact token ids
            factored_logits: (B, factored_vocab_size, num_factored_vocabs, num_future_frames, H, W)
        """
        if actions is not None:
            actions = actions.to(self.device)
        if joint_angles is not None:
            joint_angles = joint_angles.to(self.device)
        
        video_THW = video_THW.to(self.device)
        
        contact_tokens, factored_logits = self.model.generate_contact(
            video_THW,
            actions=actions,
            joint_angles=joint_angles,
            num_prompt_frames=self.num_prompt_frames,
            temperature=self.args.temperature,
            return_logits=True,
        )
        
        return contact_tokens, factored_logits

    @torch.no_grad()
    def predict_joint_angles(
        self,
        video_THW: torch.LongTensor,
        actions: torch.FloatTensor = None,
        joint_angles: torch.FloatTensor = None,
    ) -> torch.FloatTensor:
        """
        Predict future joint angles given video frames and actions.
        
        Args:
            video_THW: LongTensor of size (B, T, H, W) - full video (history + predicted future)
            actions: FloatTensor of size (B, T, 3) - actions for all frames
            joint_angles: FloatTensor of size (B, T, 4) - joint angles for all frames (history used as input)
            
        Returns:
            pred_joints: (B, num_future_frames, 4) - predicted joint angles
        """
        if actions is not None:
            actions = actions.to(self.device)
        if joint_angles is not None:
            joint_angles = joint_angles.to(self.device)
        
        video_THW = video_THW.to(self.device)
        
        pred_joints = self.model.generate_joints(
            video_THW,
            actions=actions,
            joint_angles=joint_angles,
            num_prompt_frames=self.num_prompt_frames,
        )
        
        return pred_joints

    def decode_frames(self, tokens_THW: torch.LongTensor) -> torch.ByteTensor:
        """
        Decode tokenized frames to RGB images.
        
        Args:
            tokens_THW: (B, T, H, W) token ids
            
        Returns:
            (B, T, 3, 256, 256) RGB images
        """
        return decode_tokens(tokens_THW.cpu(), self.decode_latents)


def compute_contact_accuracy(
    contact_labels: torch.LongTensor,
    pred_contact: torch.LongTensor,
) -> float:
    """
    Compute token-level accuracy for contact prediction.
    
    Args:
        contact_labels: (B, num_future_frames, H, W) ground truth contact tokens
        pred_contact: (B, num_future_frames, H, W) predicted contact tokens
        
    Returns:
        Token accuracy as float
    """
    return (contact_labels == pred_contact).float().mean().item()


def compute_future_frame_loss(
    gt_future_tokens: torch.LongTensor,
    factored_logits: torch.FloatTensor,
    num_factored_vocabs: int,
    factored_vocab_size: int,
) -> float:
    """
    Compute cross entropy loss for future frame predictions.
    
    Matches training loss computation: sum CE over factored vocabs, mean over batch/spatial.
    
    Args:
        gt_future_tokens: (B, num_future_frames, H, W) ground truth tokens for future frames
        factored_logits: (B, factored_vocab_size, num_factored_vocabs, num_future_frames, H, W)
        num_factored_vocabs: Number of factored vocabularies (from model config)
        factored_vocab_size: Size of each factored vocabulary (from model config)
        
    Returns:
        Cross entropy loss (sum over factored vocabs, mean over batch/spatial)
    """
    # factored_logits: (B, factored_vocab_size, num_factored_vocabs, num_future_frames, H, W)
    # gt_future_tokens: (B, num_future_frames, H, W)
    
    # Clamp any out-of-range tokens (e.g., mask tokens that slipped through)
    image_vocab_size = factored_vocab_size ** num_factored_vocabs
    gt_future_tokens = gt_future_tokens.clamp(max=image_vocab_size - 1)
    
    # Factorize labels: (B, num_factored_vocabs, num_future_frames, H, W)
    factored_labels = factorize_labels(
        gt_future_tokens.to(factored_logits.device), 
        num_factored_vocabs, 
        factored_vocab_size
    )
    
    # Cross entropy: treats dim=1 (factored_vocab_size) as class dimension
    # Output shape: (B, num_factored_vocabs, num_future_frames, H, W)
    # Then sum over num_factored_vocabs (dim=1), mean over rest
    loss = torch.nn.functional.cross_entropy(
        factored_logits, factored_labels, reduction="none"
    ).sum(dim=1).mean().item()
    
    return loss


@torch.no_grad()
def main():
    transformers.set_seed(42)
    args = parse_args()

    print(f"=" * 60)
    print(f"GENIE Evaluation")
    print(f"=" * 60)
    print(f"Checkpoint: {args.checkpoint_dir}")
    print(f"Val data: {args.val_data_dir}")
    print(f"Window size: {args.window_size}, Stride: {args.stride}")
    print(f"Prompt frames: {args.num_prompt_frames}, Future frames: {args.window_size - args.num_prompt_frames}")
    print(f"MaskGIT steps: {args.maskgit_steps}, Temperature: {args.temperature}")
    print(f"Teacher forcing: {args.teacher_force_time}")
    print(f"Evaluate contact: {args.evaluate_contact}")
    print(f"Evaluate joints: {args.evaluate_joints}")
    print(f"=" * 60)

    # Load dataset
    val_dataset = RawTokenDataset(
        args.val_data_dir, 
        window_size=args.window_size, 
        stride=args.stride, 
        filter_overlaps=True
    )
    args.latent_h = args.latent_w = val_dataset.metadata["s"]
    
    # Check if contact data is available
    has_contact_data = val_dataset.contact is not None
    if args.evaluate_contact and not has_contact_data:
        print("WARNING: --evaluate_contact specified but no contact data found. Skipping contact evaluation.")
        args.evaluate_contact = False
    
    # Check if joint angles data is available
    has_joint_data = val_dataset.joint_angles is not None
    if args.evaluate_joints and not has_joint_data:
        print("WARNING: --evaluate_joints specified but no joint angles data found. Skipping joint evaluation.")
        args.evaluate_joints = False
    
    if args.max_examples is not None:
        val_dataset.valid_start_inds = val_dataset.valid_start_inds[:args.max_examples]
        print(f"Limiting evaluation to {args.max_examples} examples")

    # Load model and create dataloader with proper collator
    model = STMaskGIT.from_pretrained(args.checkpoint_dir)
    config = model.config
    collate_fn = get_maskgit_collator(config)
    dataloader = DataLoader(val_dataset, collate_fn=collate_fn, batch_size=args.batch_size, shuffle=False)

    # Initialize evaluator and metrics
    decode_latents = decode_latents_wrapper()
    lpips_alex = lpips.LPIPS(net="alex")
    
    evaluator = GenieEvaluator(args, decode_latents)
    
    # Metrics
    metrics = defaultdict(AvgMetric)
    
    if args.save_outputs_dir is not None:
        outputs_to_save = defaultdict(list)

    num_future_frames = args.window_size - args.num_prompt_frames
    
    print(f"\nStarting evaluation on {len(val_dataset)} examples...")
    
    for batch_idx, batch in enumerate(tqdm(dataloader, desc="Evaluating")):
        batch_size = batch["input_ids"].size(0)
        
        # Reshape inputs
        reshaped_input_ids = rearrange(
            batch["input_ids"], "b (t h w) -> b t h w", 
            t=args.window_size, h=args.latent_h, w=args.latent_w
        )
        
        # Get actions and joint angles
        actions = batch.get("actions", None)
        joint_angles = batch.get("joint_angles", None)
        
        # ==================== VIDEO PREDICTION ====================
        start_time = time.time()
        video_samples, video_logits = evaluator.predict_video_frames(
            batch["input_ids"],
            actions=actions,
            joint_angles=joint_angles,
            ground_truth_THW=reshaped_input_ids if args.teacher_force_time else None,
        )
        gen_time = time.time() - start_time
        frames_generated = num_future_frames * batch_size
        metrics["video_gen_time_per_frame"].update(gen_time / frames_generated, batch_size)
        
        # Video token accuracy
        gt_future_tokens = reshaped_input_ids[:, args.num_prompt_frames:].to(evaluator.device)
        video_token_acc = (gt_future_tokens == video_samples).float().mean().item()
        metrics["video_token_acc"].update(video_token_acc, batch_size)
        
        # Video loss (using factorized logits) - use model config for vocab sizes
        video_loss = compute_future_frame_loss(
            gt_future_tokens, video_logits,
            num_factored_vocabs=config.num_factored_vocabs,
            factored_vocab_size=config.factored_vocab_size
        )
        metrics["video_loss"].update(video_loss, batch_size)
        
        # Decode and compute LPIPS
        start_time = time.time()
        pred_video_frames = evaluator.decode_frames(video_samples)
        gt_video_frames = evaluator.decode_frames(gt_future_tokens.cpu())
        dec_time = time.time() - start_time
        metrics["video_dec_time_per_frame"].update(dec_time / frames_generated, batch_size)
        
        video_lpips = compute_lpips(gt_video_frames, pred_video_frames, lpips_alex)
        metrics["video_lpips"].update_list(video_lpips)
        
        # ==================== CONTACT PREDICTION ====================
        if args.evaluate_contact:
            # Get ground truth contact
            contact_labels = batch.get("contact_labels", None)
            if contact_labels is not None:
                contact_labels_THW = rearrange(
                    contact_labels, "b (t h w) -> b t h w",
                    t=args.window_size, h=args.latent_h, w=args.latent_w
                )
                gt_contact_future = contact_labels_THW[:, args.num_prompt_frames:].to(evaluator.device)
                
                # Build full video for contact prediction: [history_gt, predicted_future]
                full_video = torch.cat([
                    reshaped_input_ids[:, :args.num_prompt_frames].to(evaluator.device),
                    video_samples,
                ], dim=1)
                
                # Predict contact (now also returns logits)
                start_time = time.time()
                contact_samples, contact_logits = evaluator.predict_contact_frames(full_video, actions=actions, joint_angles=joint_angles)
                contact_gen_time = time.time() - start_time
                metrics["contact_gen_time_per_frame"].update(contact_gen_time / frames_generated, batch_size)
                
                # Contact token accuracy
                contact_token_acc = compute_contact_accuracy(gt_contact_future, contact_samples)
                metrics["contact_token_acc"].update(contact_token_acc, batch_size)
                
                # Contact loss (using factorized logits, same as video)
                contact_loss = compute_future_frame_loss(
                    gt_contact_future, contact_logits,
                    num_factored_vocabs=config.num_factored_vocabs,
                    factored_vocab_size=config.factored_vocab_size
                )
                metrics["contact_loss"].update(contact_loss, batch_size)
                
                # Decode and compute contact LPIPS
                start_time = time.time()
                pred_contact_frames = evaluator.decode_frames(contact_samples)
                gt_contact_frames = evaluator.decode_frames(gt_contact_future.cpu())
                contact_dec_time = time.time() - start_time
                metrics["contact_dec_time_per_frame"].update(contact_dec_time / frames_generated, batch_size)
                
                contact_lpips = compute_lpips(gt_contact_frames, pred_contact_frames, lpips_alex)
                metrics["contact_lpips"].update_list(contact_lpips)
                
                if args.save_outputs_dir is not None:
                    outputs_to_save["pred_contact_tokens"].append(contact_samples.cpu())
                    outputs_to_save["gt_contact_tokens"].append(gt_contact_future.cpu())
                    outputs_to_save["pred_contact_frames"].append(pred_contact_frames)
                    outputs_to_save["gt_contact_frames"].append(gt_contact_frames)
                    outputs_to_save["contact_logits"].append(contact_logits.cpu())
        
        # ==================== JOINT ANGLE PREDICTION ====================
        if args.evaluate_joints and joint_angles is not None:
            gt_joints_future = joint_angles[:, args.num_prompt_frames:].to(evaluator.device)  # (B, num_future, 4)
            
            # Build full video for joint prediction: [history_gt, predicted_future]
            full_video = torch.cat([
                reshaped_input_ids[:, :args.num_prompt_frames].to(evaluator.device),
                video_samples,
            ], dim=1)
            
            # Predict joint angles
            start_time = time.time()
            pred_joints = evaluator.predict_joint_angles(full_video, actions=actions, joint_angles=joint_angles)
            joint_gen_time = time.time() - start_time
            metrics["joint_gen_time_per_frame"].update(joint_gen_time / num_future_frames, batch_size)
            
            # Joint angle MSE
            joint_mse = ((pred_joints - gt_joints_future) ** 2).mean().item()
            metrics["joint_mse"].update(joint_mse, batch_size)
            
            # Per-joint MSE
            for j in range(4):
                per_joint_mse = ((pred_joints[:, :, j] - gt_joints_future[:, :, j]) ** 2).mean().item()
                metrics[f"joint_{j}_mse"].update(per_joint_mse, batch_size)
            
            if args.save_outputs_dir is not None:
                outputs_to_save["pred_joints"].append(pred_joints.cpu())
                outputs_to_save["gt_joints"].append(gt_joints_future.cpu())
        
        # Save outputs if requested
        if args.save_outputs_dir is not None:
            outputs_to_save["pred_video_tokens"].append(video_samples.cpu())
            outputs_to_save["gt_video_tokens"].append(gt_future_tokens.cpu())
            outputs_to_save["pred_video_frames"].append(pred_video_frames)
            outputs_to_save["gt_video_frames"].append(gt_video_frames)
            outputs_to_save["video_logits"].append(video_logits.cpu())
        
        # Print running metrics every 10 batches
        if (batch_idx + 1) % 10 == 0:
            print(f"\n[Batch {batch_idx + 1}] Running metrics:")
            for key, val in sorted(metrics.items()):
                print(f"  {key}: {val.mean():.4f}")

    # ==================== FINAL RESULTS ====================
    print(f"\n" + "=" * 60)
    print("FINAL EVALUATION RESULTS")
    print("=" * 60)
    
    results = {}
    print("\n📹 VIDEO PREDICTION METRICS:")
    for key in ["video_token_acc", "video_loss", "video_lpips", "video_gen_time_per_frame", "video_dec_time_per_frame"]:
        if key in metrics:
            val = metrics[key].mean()
            results[key] = val
            print(f"  {key}: {val:.4f}")
    
    if args.evaluate_contact:
        print("\n🤚 CONTACT PREDICTION METRICS:")
        for key in ["contact_token_acc", "contact_loss", "contact_lpips", "contact_gen_time_per_frame", "contact_dec_time_per_frame"]:
            if key in metrics:
                val = metrics[key].mean()
                results[key] = val
                print(f"  {key}: {val:.4f}")
    
    if args.evaluate_joints:
        print("\n🦾 JOINT ANGLE PREDICTION METRICS:")
        for key in ["joint_mse", "joint_0_mse", "joint_1_mse", "joint_2_mse", "joint_3_mse", "joint_gen_time_per_frame"]:
            if key in metrics:
                val = metrics[key].mean()
                results[key] = val
                print(f"  {key}: {val:.6f}")
    
    print("=" * 60)
    
    # Save outputs
    if args.save_outputs_dir is not None:
        os.makedirs(args.save_outputs_dir, exist_ok=True)
        save_dir = Path(args.save_outputs_dir)
        
        for key, tensors in outputs_to_save.items():
            torch.save(torch.cat(tensors, dim=0), save_dir / f"{key}.pt")
            print(f"Saved {key} to {save_dir / f'{key}.pt'}")
        
        # Save metrics as JSON
        with open(save_dir / "metrics.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"Saved metrics to {save_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()

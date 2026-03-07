"""
Example usage: See https://github.com/1x-technologies/1xgpt?tab=readme-ov-file#1x-genie-baseline

Pipeline summary:
- Input: history_video_frames (0..num_prompt_frames-1) + history_actions + future_actions
- Output: future_video_frames (num_prompt_frames..window_size-1) + optionally future_contact_frames
- Actions are strided the same way as video frames in RawTokenDataset
"""

import argparse
import json
import os
import sys
from pathlib import Path

import torch
import numpy as np

sys.path.append(os.getcwd())
from data import RawTokenDataset
from genie.st_mask_git import STMaskGIT

STRIDE = 15


def parse_args():
    parser = argparse.ArgumentParser(description="Generates samples (as tokens) from GENIE model. "
                                                 "Optionally visualizes these tokens as GIFs or comics.")
    parser.add_argument(
        "--val_data_dir", type=str, default="data/val_v3.0",
        help="A directory with video data, should have a `metadata.json` and `video.bin`. "
             "We generate using the first frames of this dataset."
    )
    parser.add_argument(
        "--checkpoint_dir", type=str,
        help="Path to a HuggingFace-style checkpoint."
    )
    parser.add_argument(
        "--output_dir", type=str, default="data/genie_generated",
        help="Directory to save generated outputs."
    )
    parser.add_argument(
        "--num_prompt_frames", type=int, default=8, 
        help="The number of context (history) frames to condition on."
    )
    parser.add_argument(
        "--window_size", type=int, default=16,
        help="Total frames in a sequence. Will generate `window_size - num_prompt_frames` future frames."
    )
    parser.add_argument(
        "--stride", type=int, default=STRIDE,
        help="Frame stride for loading data (must match training stride)."
    )
    parser.add_argument(
        "--example_ind", type=int, default=0,
        help="The index in the dataset of the example to generate on."
    )
    parser.add_argument(
        "--start_frame", type=int, default=None,
        help="Optional: explicit start frame index in the original video to use as window start. Overrides example_ind.",
    )
    parser.add_argument(
        "--teacher_force_time", action="store_true",
        help="If True, teacher-forces generation in time dimension (uses ground truth for earlier frames)."
    )
    parser.add_argument(
        "--maskgit_steps", type=int, default=2, help="Number of MaskGIT sampling steps per frame."
    )
    parser.add_argument(
        "--temperature", type=float, default=0,
        help="Sampling temperature. If `temperature` <= 1e-8, will do greedy sampling."
    )
    parser.add_argument(
        "--generate_contact", action="store_true",
        help="If True, also generate and save contact predictions for future frames."
    )
    parser.add_argument(
        "--generate_joints", action="store_true",
        help="If True, also generate and save joint angle predictions for future frames."
    )
    parser.add_argument(
        "--skip_ground_truth", action="store_true",
        help="If True, do NOT include ground truth frames in output. Use for simulation mode where we don't have ground truth."
    )

    return parser.parse_args()


@torch.no_grad()
def main():
    args = parse_args()
    assert args.num_prompt_frames <= args.window_size, \
        f"num_prompt_frames ({args.num_prompt_frames}) must be <= window_size ({args.window_size})"
    
    # Load dataset with same stride as training
    val_dataset = RawTokenDataset(args.val_data_dir, window_size=args.window_size, stride=args.stride)
    latent_side_len = val_dataset.metadata["s"]

    # Handle --start_frame override
    if args.start_frame is not None:
        if args.start_frame in val_dataset.valid_start_inds:
            args.example_ind = val_dataset.valid_start_inds.index(args.start_frame)
        else:
            print(f"Warning: start_frame {args.start_frame} not in valid_start_inds, using example_ind instead")

    # Get single example: video tokens, actions (strided), and optionally contact
    example_data = val_dataset[args.example_ind]
    
    # Reshape video tokens: (1, T, H, W)
    example_THW = example_data["input_ids"].reshape(1, args.window_size, latent_side_len, latent_side_len).to("cuda")
    
    # Actions: (1, T, 3) - includes both history and future actions (strided same as video)
    example_actions = example_data["actions"].unsqueeze(0).to("cuda")
    
    # Verify alignment: actions should have same temporal length as video
    assert example_actions.shape[1] == args.window_size, \
        f"Actions length {example_actions.shape[1]} != window_size {args.window_size}"
    
    # Joint angles: (1, T, 4) - includes both history and future joint angles
    if "joint_angles" in example_data:
        example_joint_angles = example_data["joint_angles"].unsqueeze(0).to("cuda")
    else:
        example_joint_angles = None
    
    # Load the model checkpoint
    model = STMaskGIT.from_pretrained(args.checkpoint_dir).to("cuda")
    model.eval()
    
    print(f"Generating with:")
    print(f"  - History frames: 0..{args.num_prompt_frames - 1} (history_actions from same frames)")
    print(f"  - Future frames to predict: {args.num_prompt_frames}..{args.window_size - 1}")
    print(f"  - Future actions (conditioning): frames {args.num_prompt_frames}..{args.window_size - 1}")
    print(f"  - Stride: {args.stride} (effective Hz: {val_dataset.metadata.get('hz', 30) / args.stride:.1f})")

    # Initialize prompt: history frames visible, future frames masked
    prompt_THW = example_THW.clone()
    prompt_THW[:, args.num_prompt_frames:] = model.mask_token_id

    # Generate future frames one at a time
    samples = []
    for timestep in range(args.num_prompt_frames, args.window_size):
        # Teacher-forced: reset to ground truth for frames before current timestep
        if args.teacher_force_time:
            prompt_THW = example_THW.clone()
            prompt_THW[:, timestep:] = model.mask_token_id

        # Generate frame at timestep using:
        #   - prompt_THW: history video + previously generated frames (or GT if teacher forcing)
        #   - example_actions: full action sequence (history + future)
        #   - example_joint_angles: full joint angle sequence (history + future)
        samples_HW, _ = model.maskgit_generate(
            prompt_THW,
            out_t=timestep,
            actions=example_actions,  # Full actions: (B, T, 3)
            joint_angles=example_joint_angles,  # Full joint angles: (B, T, 4)
            maskgit_steps=args.maskgit_steps,
            temperature=args.temperature,
        )

        samples.append(samples_HW)
        
        # Autoregressive: use predicted frame as context for next prediction
        if not args.teacher_force_time:
            prompt_THW[:, timestep] = samples_HW

    # Stack predicted frames: (B, num_future_frames, H, W)
    predicted_future = torch.stack(samples, dim=1)
    
    # Build output: [prompt_frames, predicted_frames, (optional) ground_truth_future_frames]
    # This layout allows comic-strip visualization with GT comparison
    if args.skip_ground_truth:
        # Simulation mode: no ground truth available, just output prompt + predictions
        outputs = torch.cat([
            example_THW[:, :args.num_prompt_frames],  # History (prompt)
            predicted_future,                          # Predicted future
        ], dim=1)
    else:
        # Normal mode: include ground truth for comparison
        outputs = torch.cat([
            example_THW[:, :args.num_prompt_frames],  # History (prompt)
            predicted_future,                          # Predicted future
            example_THW[:, args.num_prompt_frames:],  # Ground truth future (for comparison)
        ], dim=1)

    # Write video tokens to output
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs.cpu().numpy().astype(np.dtype(val_dataset.metadata["dtype"])).tofile(output_dir / "video.bin")
    print(f"Saved video tokens to {output_dir / 'video.bin'}")

    # Generate and save contact if requested
    if args.generate_contact:
        # Build the full predicted video sequence for contact generation:
        # [history_frames, predicted_future_frames]
        predicted_video = torch.cat([
            example_THW[:, :args.num_prompt_frames],  # History frames (ground truth)
            predicted_future,                          # Predicted future frames
        ], dim=1)
        
        # Generate contact tokens for future frames
        # Input: predicted_video (B, T, H, W) + full actions (B, T, 3) + joint angles (B, T, 4)
        # Output: contact tokens for frames num_prompt_frames..window_size-1
        contact_tokens = model.generate_contact(
            predicted_video,
            actions=example_actions,
            joint_angles=example_joint_angles,
            num_prompt_frames=args.num_prompt_frames,
            temperature=args.temperature,
        )
        
        # Build contact output: [predicted_contact, ground_truth_contact (if available)]
        if "contact" in example_data:
            gt_contact = example_data["contact"].reshape(
                1, args.window_size, latent_side_len, latent_side_len
            ).to("cuda")
            gt_contact_future = gt_contact[:, args.num_prompt_frames:]
            
            # Stack: [predicted_contact, ground_truth_contact] for comparison
            contact_outputs = torch.cat([contact_tokens, gt_contact_future], dim=1)
        else:
            contact_outputs = contact_tokens
        
        contact_outputs.cpu().numpy().astype(
            np.dtype(val_dataset.metadata["dtype"])
        ).tofile(output_dir / "contact_splat.bin")
        print(f"Saved contact tokens to {output_dir / 'contact_splat.bin'}")

    # Generate and save joint angles if requested
    if args.generate_joints:
        # Build the full predicted video sequence for joint generation
        predicted_video = torch.cat([
            example_THW[:, :args.num_prompt_frames],  # History frames (ground truth)
            predicted_future,                          # Predicted future frames
        ], dim=1)
        
        # Generate joint angle predictions for future frames
        pred_joints = model.generate_joints(
            predicted_video,
            actions=example_actions,
            joint_angles=example_joint_angles,
            num_prompt_frames=args.num_prompt_frames,
        )
        
        # Build output: [predicted_joints, ground_truth_joints (if available)]
        if example_joint_angles is not None:
            gt_joints_future = example_joint_angles[:, args.num_prompt_frames:]
            
            # Stack: [predicted_joints, ground_truth_joints] for comparison
            joint_outputs = torch.cat([pred_joints, gt_joints_future], dim=1)
        else:
            joint_outputs = pred_joints
        
        joint_outputs.cpu().numpy().astype(np.float16).tofile(output_dir / "joint_angles.bin")
        print(f"Saved joint angles to {output_dir / 'joint_angles.bin'}")

    # Save metadata
    num_future_frames = args.window_size - args.num_prompt_frames
    if args.skip_ground_truth:
        layout = "[prompt_frames, predicted_frames]"
    else:
        layout = "[prompt_frames, predicted_frames, ground_truth_future_frames]"
    
    with open(output_dir / "metadata.json", "w") as f:
        json.dump(vars(args) | val_dataset.metadata | {
            "num_images": outputs.shape[1],
            "h": latent_side_len,
            "w": latent_side_len,
            "t": args.window_size,
            "num_prompt_frames": args.num_prompt_frames,
            "num_future_frames": num_future_frames,
            "stride": args.stride,
            "layout": layout,
            "has_ground_truth": not args.skip_ground_truth,
        }, f, indent=2)
    print(f"Saved metadata to {output_dir / 'metadata.json'}")


if __name__ == "__main__":
    main()

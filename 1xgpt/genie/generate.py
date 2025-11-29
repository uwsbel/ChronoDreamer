"""
Example usage: See https://github.com/1x-technologies/1xgpt?tab=readme-ov-file#1x-genie-baseline
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
        help="A directory with video data, should have a `metadata.json` and `video.bin` We generate using the first frames of this dataset."
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
        "--num_prompt_frames", type=int, default=8, help="The number of context frames."
    )
    parser.add_argument(
        "--window_size", type=int, default=16,
        help="Will generate `window_size - num_prompt_frames` frames."
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
        help="If True, teacher-forces generation in time dimension."
    )
    parser.add_argument(
        "--maskgit_steps", type=int, default=2, help="Number of MaskGIT sampling steps."
    )
    parser.add_argument(
        "--temperature", type=float, default=0,
        help="Sampling temperature. If `temperature` <= 1e-8, will do greedy sampling."
    )
    parser.add_argument(
        "--generate_contact", action="store_true",
        help="If True, also generate and save contact predictions."
    )

    return parser.parse_args()


@torch.no_grad()
def main():
    args = parse_args()
    assert args.num_prompt_frames <= args.window_size
    val_dataset = RawTokenDataset(args.val_data_dir, window_size=args.window_size, stride=STRIDE)
    latent_side_len = val_dataset.metadata["s"]

    # Handle --start_frame override
    if args.start_frame is not None:
        # Find which example_ind corresponds to this start_frame
        # Or directly index into the dataset's valid_start_inds
        if args.start_frame in val_dataset.valid_start_inds:
            args.example_ind = val_dataset.valid_start_inds.index(args.start_frame)
        else:
            # Find nearest valid start
            print(f"Warning: start_frame {args.start_frame} not in valid_start_inds, using example_ind instead")

    # Get single example INCLUDING ACTIONS
    example_data = val_dataset[args.example_ind]
    example_THW = example_data["input_ids"].reshape(1, args.window_size, latent_side_len, latent_side_len).to("cuda")

    # ✅ Extract actions from the example
    example_actions = example_data["actions"].unsqueeze(0).to("cuda")  # (1, window_size, 3)
    
    # Load the model checkpoint
    model = STMaskGIT.from_pretrained(args.checkpoint_dir).to("cuda")
    model.eval()

    samples = []
    prompt_THW = example_THW.clone()
    prompt_THW[:, args.num_prompt_frames:] = model.mask_token_id

    for timestep in range(args.num_prompt_frames, args.window_size):
        # Teacher-forced, maskgit generation
        if args.teacher_force_time:
            prompt_THW = example_THW.clone()
            prompt_THW[:, timestep:] = model.mask_token_id

        samples_HW, _ = model.maskgit_generate(
            prompt_THW,
            out_t=timestep,
            actions=example_actions,  # Full actions sequence
            maskgit_steps=args.maskgit_steps,
            temperature=args.temperature,
        )

        samples.append(samples_HW)
        if not args.teacher_force_time:
            prompt_THW[:, timestep] = samples_HW

    outputs = torch.stack(samples, dim=1)
    # prepend prompt sequence
    outputs = torch.cat([example_THW[:, :args.num_prompt_frames], outputs], dim=1)

    # append ground-truth targets next to generated outputs for comic strip generation
    # [<prompt frames><predicted frames><ground truth frames>]
    outputs = torch.cat([outputs, example_THW[:, args.num_prompt_frames:]], dim=1)

    # write to output
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs.cpu().numpy().astype(np.dtype(val_dataset.metadata["token_dtype"])).tofile(output_dir / "video.bin")

    # Generate and save contact if requested
    if args.generate_contact:
        # Use the final predicted video (not ground truth) for contact generation
        predicted_video = torch.cat([
            example_THW[:, :args.num_prompt_frames],  # prompt frames
            torch.stack(samples, dim=1)  # predicted frames
        ], dim=1)
        
        contact_tokens = model.generate_contact(
            predicted_video,
            actions=example_actions,
            num_prompt_frames=args.num_prompt_frames,
            temperature=args.temperature,
        )
        
        # Also get ground truth contact if available
        if "contact" in example_data:
            gt_contact = example_data["contact"].reshape(1, args.window_size, latent_side_len, latent_side_len).to("cuda")
            gt_contact_future = gt_contact[:, args.num_prompt_frames:]
            
            # Stack: [predicted_contact, ground_truth_contact]
            contact_outputs = torch.cat([contact_tokens, gt_contact_future], dim=1)
        else:
            contact_outputs = contact_tokens
        
        contact_outputs.cpu().numpy().astype(np.dtype(val_dataset.metadata["token_dtype"])).tofile(
            output_dir / "contact_splat.bin"
        )
        print(f"Saved contact tokens to {output_dir / 'contact_splat.bin'}")

    with open(output_dir / "metadata.json", "w") as f:
        json.dump(vars(args) | val_dataset.metadata | {
            "num_images": outputs.shape[1],
            "h": latent_side_len,
            "w": latent_side_len,
            "t": args.window_size,
        }, f)


if __name__ == "__main__":
    main()

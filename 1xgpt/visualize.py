#!/usr/bin/env python3

"""
Script to decode tokenized video into images/video.
Example usage: See https://github.com/1x-technologies/1xgpt?tab=readme-ov-file#1x-genie-baseline
"""

import argparse
import json
import math
import os
from PIL import Image, ImageDraw

import numpy as np
import torch
import torch.distributed.optim
import torch.utils.checkpoint
import torch.utils.data
import torchvision.transforms.v2.functional as transforms_f
from einops import rearrange
from matplotlib import pyplot as plt

from data import RawTokenDataset
from magvit2.config import VQConfig
from magvit2.models.lfqgan import VQModel


def parse_args():
    parser = argparse.ArgumentParser(description="Visualize tokenized video as GIF or comic.")
    parser.add_argument(
        "--stride",
        type=int,
        default=1,
        help="Frame skip",
    )
    parser.add_argument(
        "--token_dir",
        type=str,
        default="data/genie_generated",
        help="Directory of tokens, in the format of `video.bin` and `metadata.json`. "
             "Visualized gif and comic will be written here.",
    )
    parser.add_argument(
        "--offset", type=int, default=0, help="Offset to start generating images from"
    )
    parser.add_argument(
        "--fps", type=int, default=2, help="Frames per second"
    )
    parser.add_argument(
        "--max_images", type=int, default=None, help="Maximum number of images to generate. None for all."
    )
    parser.add_argument(
        "--disable_comic", action="store_true",
        help="Comic generation assumes `token_dir` follows the same format as generate: e.g., "
             "`prompt | predictions | gtruth` in `video.bin`, `window_size` in `metadata.json`."
             "Therefore, comic should be disabled when visualizing videos without this format, such as the dataset."
    )
    parser.add_argument(
        "--visualize_contact", action="store_true",
        help="If specified, will also visualize contact_splat.bin if it exists."
    )
    args = parser.parse_args()

    return args


def export_to_gif(frames: list, output_gif_path: str, fps: int):
    """
    Export a list of frames to a GIF.

    Args:
    - frames (list): List of frames (as numpy arrays or PIL Image objects).
    - output_gif_path (str): Path to save the output GIF.
    - fps (int): Desired frames per second.
    """
    # Convert numpy arrays to PIL Images if needed
    pil_frames = [Image.fromarray(frame) if isinstance(
        frame, np.ndarray) else frame for frame in frames]

    duration_ms = 1000 / fps
    pil_frames[0].save(output_gif_path.replace(".mp4", ".gif"),
                       format="GIF",
                       append_images=pil_frames[1:],
                       save_all=True,
                       duration=duration_ms,
                       loop=0)


def rescale_magvit_output(magvit_output):
    """
    [-1, 1] -> [0, 255]

    Important: clip to [0, 255]
    """
    rescaled_output = ((magvit_output.detach().cpu() + 1) * 127.5)
    clipped_output = torch.clamp(rescaled_output, 0, 255).to(dtype=torch.uint8)
    return clipped_output


def decode_latents_wrapper(batch_size=16, tokenizer_ckpt="cosmos/Cosmos-Tokenizer/pretrained_ckpts/Cosmos-0.1-Tokenizer-DI8x8", max_images=None):
    import sys
    sys.path.append("cosmos/Cosmos-Tokenizer")
    from cosmos_tokenizer.image_lib import ImageTokenizer
    
    device = "cuda"
    dtype = torch.bfloat16
    
    enc_ckpt = os.path.join(tokenizer_ckpt, "encoder.jit")
    dec_ckpt = os.path.join(tokenizer_ckpt, "decoder.jit")
    
    decoder = ImageTokenizer(
        checkpoint_dec=dec_ckpt,
        device=device,
        dtype="bfloat16",
    )

    @torch.no_grad()
    def decode_latents(video_data):
        """
        video_data: (b, h, w), where h=32, w=32 for Cosmos DI8x8
        """
        decoded_imgs = []

        for shard_ind in range(math.ceil(len(video_data) / batch_size)):
            batch = torch.from_numpy(video_data[shard_ind * batch_size: (shard_ind + 1) * batch_size].astype(np.int64))
            
            # Cosmos decoder expects (B, H, W) indices
            recon = decoder.decode(batch.to(device=device))  # Returns (B, 3, 256, 256) in [-1, 1]
            recon_scaled_batch = rescale_magvit_output(recon)  # (B, 3, 256, 256) uint8

            decoded_imgs.append(recon_scaled_batch)

            if max_images and len(decoded_imgs) * batch_size >= max_images:
                break

        return [transforms_f.to_pil_image(img) for img in torch.cat(decoded_imgs)]

    return decode_latents


def caption_image(pil_image: Image, caption: str):
    """
    Add a bit of empty space at the top, and add the caption there
    """
    border_size = 36
    font_size = 24

    width, height = pil_image.size
    new_width = width
    new_height = height + border_size

    new_image = Image.new("RGB", (new_width, new_height), "white")
    new_image.paste(pil_image, (0, border_size))

    # Draw the caption
    draw = ImageDraw.Draw(new_image)

    # Center text (`align` keyword doesn't work)
    _, _, text_w, text_h = draw.textbbox((0, 0), caption, font_size=font_size)
    draw.text(((width - text_w) / 2, (border_size - text_h) / 2), caption, fill="black", font_size=font_size)

    return new_image


def create_side_by_side_frame(left_image: Image, right_image: Image, gap: int = 10) -> Image:
    """
    Create a side-by-side image from two PIL images with a gap between them.
    """
    left_w, left_h = left_image.size
    right_w, right_h = right_image.size
    
    # Use max height, total width + gap
    combined_w = left_w + gap + right_w
    combined_h = max(left_h, right_h)
    
    combined = Image.new("RGB", (combined_w, combined_h), "white")
    combined.paste(left_image, (0, 0))
    combined.paste(right_image, (left_w + gap, 0))
    
    return combined


@torch.no_grad()
def main():
    args = parse_args()

    # Load metadata first to determine if this is generated data
    metadata_path = os.path.join(args.token_dir, "metadata.json")
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    
    is_generated_data = all(key in metadata for key in ("num_prompt_frames", "window_size"))
    has_ground_truth = metadata.get("has_ground_truth", True)  # Default to True for backwards compatibility
    
    # Load video tokens directly (bypassing RawTokenDataset to avoid contact shape mismatch)
    video_path = os.path.join(args.token_dir, "video.bin")
    token_dtype = np.dtype(metadata.get("dtype", metadata.get("token_dtype", "uint32")))
    s = metadata["s"]
    
    if is_generated_data:
        if has_ground_truth:
            # Generated data with GT: [prompt | predicted | ground_truth]
            num_video_frames = metadata["window_size"] * 2 - metadata["num_prompt_frames"]
        else:
            # Generated data without GT: [prompt | predicted]
            num_video_frames = metadata["window_size"]
    else:
        num_video_frames = metadata["num_images"]
    
    video_shape = (num_video_frames, s, s)
    video_tokens = np.memmap(video_path, dtype=token_dtype, mode="r", shape=video_shape)

    video_frames = decode_latents_wrapper(max_images=args.max_images)(video_tokens[args.offset::args.stride])
    output_gif_path = os.path.join(args.token_dir, f"generated_offset{args.offset}.gif")

    if is_generated_data:
        if has_ground_truth:
            expected_frames = metadata["window_size"] * 2 - metadata["num_prompt_frames"]
        else:
            expected_frames = metadata["window_size"]
        
        if video_tokens.shape[0] != expected_frames:
            raise ValueError(f"Unexpected {video_tokens.shape=} given {metadata['window_size']=}, {metadata['num_prompt_frames']=}, {has_ground_truth=}")

        captioned_frames = []
        for i, frame in enumerate(video_frames):
            if i < metadata["num_prompt_frames"]:
                caption = "Prompt"
            elif i < metadata["window_size"]:
                caption = "Generated"
            else:
                caption = "Ground truth"

            captioned_frames.append(caption_image(frame, caption))
    else:
        # Leave ground truth frames uncaptioned
        captioned_frames = video_frames

    export_to_gif(captioned_frames, output_gif_path, args.fps)
    print(f"Saved to {output_gif_path}")

    # Visualize contact if requested and available
    contact_frames = None
    captioned_contact = None
    if args.visualize_contact:
        contact_path = os.path.join(args.token_dir, "contact_splat.bin")
        if os.path.exists(contact_path):
            # For generated data, contact has different frame count than video
            # Load it directly with the correct shape instead of using RawTokenDataset
            if is_generated_data:
                num_future_frames = metadata["window_size"] - metadata["num_prompt_frames"]
                if has_ground_truth:
                    num_contact_frames = num_future_frames * 2
                else:
                    num_contact_frames = num_future_frames
                contact_shape = (num_contact_frames, metadata["s"], metadata["s"])
            else:
                # For training/raw data, contact has same shape as video
                contact_shape = (metadata["num_images"], metadata["s"], metadata["s"])
            
            # Use "dtype" key (matching generate.py)
            token_dtype = np.dtype(metadata.get("dtype", metadata.get("token_dtype", "uint32")))
            contact_tokens = np.memmap(contact_path, dtype=token_dtype, mode="r", shape=contact_shape)
            contact_frames = decode_latents_wrapper(max_images=args.max_images)(contact_tokens[args.offset::args.stride])
            
            # Create separate contact GIF
            contact_gif_path = os.path.join(args.token_dir, f"contact_offset{args.offset}.gif")
            
            if is_generated_data:
                # Contact has [predicted] or [predicted | ground_truth] (no prompt frames)
                captioned_contact = []
                for i, frame in enumerate(contact_frames):
                    if not has_ground_truth:
                        caption = "Contact: Generated"
                    else:
                        if i < num_future_frames:
                            caption = "Contact: Generated"
                        else:
                            caption = "Contact: GT"
                    captioned_contact.append(caption_image(frame, caption))
            else:
                captioned_contact = [caption_image(f, "Contact") for f in contact_frames]
                
            export_to_gif(captioned_contact, contact_gif_path, args.fps)
            print(f"Saved contact to {contact_gif_path}")
            
            # Create COMBINED side-by-side GIF (video | contact)
            if is_generated_data:
                num_future_frames = metadata["window_size"] - metadata["num_prompt_frames"]
                combined_frames = []
                
                # For each future frame, show: [video_pred | contact_pred] then [video_gt | contact_gt]
                # Video layout: [prompt (0..num_prompt-1) | pred (num_prompt..window-1) | gt (window..end)]
                # Contact layout: [pred (0..num_future-1) | gt (num_future..end)]
                
                # Part 1: Prompt frames (video only, no contact for prompt)
                for i in range(metadata["num_prompt_frames"]):
                    video_frame = captioned_frames[i]
                    # Create placeholder for contact (gray or blank)
                    placeholder = Image.new("RGB", video_frame.size, (200, 200, 200))
                    placeholder = caption_image(placeholder.crop((0, 36, placeholder.width, placeholder.height)), "Contact: N/A")
                    combined = create_side_by_side_frame(video_frame, placeholder)
                    combined_frames.append(combined)
                
                # Part 2: Predicted frames (video pred | contact pred)
                for i in range(num_future_frames):
                    video_idx = metadata["num_prompt_frames"] + i
                    contact_idx = i  # Contact pred starts at 0
                    video_frame = captioned_frames[video_idx]
                    contact_frame = captioned_contact[contact_idx]
                    combined = create_side_by_side_frame(video_frame, contact_frame)
                    combined_frames.append(combined)

                if has_ground_truth:
                    # Part 3: Ground truth frames (video gt | contact gt)
                    for i in range(num_future_frames):
                        video_idx = metadata["window_size"] + i
                        contact_idx = num_future_frames + i  # Contact GT starts at num_future_frames
                        video_frame = captioned_frames[video_idx]
                        contact_frame = captioned_contact[contact_idx]
                        combined = create_side_by_side_frame(video_frame, contact_frame)
                        combined_frames.append(combined)
                
                combined_gif_path = os.path.join(args.token_dir, f"combined_offset{args.offset}.gif")
                export_to_gif(combined_frames, combined_gif_path, args.fps)
                print(f"Saved combined (video | contact) to {combined_gif_path}")
            
        else:
            print("Warning: --visualize_contact specified but no contact_splat.bin found")

    if not args.disable_comic:
        # Comic generation only works for generated data format
        if not is_generated_data:
            print("Warning: Comic generation skipped - metadata missing 'window_size' or 'num_prompt_frames'. "
                  "Use --disable_comic for raw dataset visualization.")
        else:
            # Determine number of rows based on whether we have contact and ground truth
            has_contact = args.visualize_contact and contact_frames is not None
            
            if has_ground_truth:
                # With GT: 2 rows for video (prediction + GT), optionally 2 more for contact
                nrows = 4 if has_contact else 2
            else:
                # Without GT: 1 row for video, optionally 1 more for contact
                nrows = 2 if has_contact else 1
            
            fig, axs = plt.subplots(nrows=nrows, ncols=metadata["window_size"], 
                                    figsize=(3 * metadata["window_size"], 3 * nrows))
            
            # Ensure axs is always 2D for consistency
            if nrows == 1:
                axs = axs.reshape(1, -1)
            
            for i, image in enumerate(video_frames):
                if i < metadata["num_prompt_frames"]:
                    if has_ground_truth:
                        curr_axs = [axs[0, i], axs[1, i]]
                    else:
                        curr_axs = [axs[0, i]]
                    title = "Prompt"

                elif i < metadata["window_size"]:
                    curr_axs = [axs[0, i]]
                    title = "Prediction"
                else:
                    # Ground truth (only when has_ground_truth is True)
                    curr_axs = [axs[1, i - metadata["window_size"] + metadata["num_prompt_frames"]]]
                    title = "Ground truth"

                for ax in curr_axs:
                    ax.set_title(title)
                    ax.imshow(image)
                    ax.axis("off")
            
            # Add contact rows if available
            # Note: Contact has [predicted] or [predicted | ground_truth] format (no prompt frames)
            if has_contact:
                num_future_frames = metadata["window_size"] - metadata["num_prompt_frames"]
                
                # Row indices for contact depend on whether we have ground truth
                contact_pred_row = 2 if has_ground_truth else 1
                contact_gt_row = 3 if has_ground_truth else None
                
                # Leave prompt columns empty for contact rows
                for i in range(metadata["num_prompt_frames"]):
                    axs[contact_pred_row, i].axis("off")
                    if contact_gt_row is not None:
                        axs[contact_gt_row, i].axis("off")
                
                # Plot contact frames starting at num_prompt_frames column
                for i, frame in enumerate(contact_frames):
                    if i < num_future_frames:
                        # Predicted contact
                        col_idx = metadata["num_prompt_frames"] + i
                        axs[contact_pred_row, col_idx].set_title("Contact: Pred")
                        axs[contact_pred_row, col_idx].imshow(frame)
                        axs[contact_pred_row, col_idx].axis("off")
                    elif contact_gt_row is not None:
                        # Ground truth contact (only if we have video GT)
                        col_idx = metadata["num_prompt_frames"] + (i - num_future_frames)
                        axs[contact_gt_row, col_idx].set_title("Contact: GT")
                        axs[contact_gt_row, col_idx].imshow(frame)
                        axs[contact_gt_row, col_idx].axis("off")

            output_comic_path = os.path.join(args.token_dir, f"generated_comic_offset{args.offset}.png")
            plt.savefig(output_comic_path, bbox_inches="tight")
            plt.close()
            print(f"Saved to {output_comic_path}")


if __name__ == "__main__":
    main()

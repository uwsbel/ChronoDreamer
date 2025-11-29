#!/usr/bin/env python3
"""
Encode a 256x256 MP4 into Cosmos DI16x16 tokens.

Input:
  - MP4 video (e.g., test.mp4)

Output:
  - NPZ file with:
      indices: [T, 16, 16]   (discrete tokens per frame)
      codes:   [T, 6, 16, 16] (continuous FSQ latents)
      fps:     float
      model_name: str
"""

import argparse
import os

import numpy as np
import torch
from torchvision.io import read_video
import torchvision.transforms as T

from cosmos_tokenizer.image_lib import ImageTokenizer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--video",
        type=str,
        required=True,
        help="Path to input MP4 (e.g. test.mp4)",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="Cosmos-0.1-Tokenizer-DI8x8",   # <- was DI16x16
        help="Cosmos tokenizer model name",
    )
    parser.add_argument(
        "--ckpt_dir",
        type=str,
        default="pretrained_ckpts",
        help="Directory containing downloaded checkpoints",
    )
    parser.add_argument(
        "--out_tokens",
        type=str,
        required=True,
        help="Output .npz file to save indices & codes",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=32,
        help="Batch size over frames for encoding",
    )
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # ----------------------------------------------------------
    # 1) Load video with torchvision
    # ----------------------------------------------------------
    # video: [T, H, W, C], uint8
    # info["video_fps"]: float
    video, audio, info = read_video(args.video, pts_unit="sec")
    fps = info.get("video_fps", None)

    T_frames, H, W, C = video.shape
    print(
        f"Loaded {args.video}: frames={T_frames}, size={H}x{W}, channels={C}, fps={fps}"
    )

    if C != 3:
        raise RuntimeError(
            f"Expected 3-channel RGB video, but got {C} channels. "
            "Convert the video to RGB first."
        )

    # ----------------------------------------------------------
    # 2) Convert to [T, 3, H, W] and resize to 256x256 if needed
    # ----------------------------------------------------------
    frames = video.permute(0, 3, 1, 2)  # [T, 3, H, W], uint8

    if (frames.shape[-2], frames.shape[-1]) != (256, 256):
        print(
            f"Resizing frames from {frames.shape[-2]}x{frames.shape[-1]} to 256x256..."
        )
        resize = T.Resize((256, 256), antialias=True)
        frames = resize(frames)

    # uint8 in [0, 255] -> float32 in [-1, 1]
    frames = frames.to(torch.float32) / 255.0   # [0, 1]
    frames = frames * 2.0 - 1.0                 # [-1, 1]
    frames = frames.to(device).to(torch.bfloat16)

    print(f"Frames tensor: {frames.shape} {frames.dtype} on {frames.device}")

    # ----------------------------------------------------------
    # 3) Initialize DI16x16 encoder
    # ----------------------------------------------------------
    enc_ckpt = os.path.join(args.ckpt_dir, args.model_name, "encoder.jit")
    if not os.path.exists(enc_ckpt):
        raise FileNotFoundError(f"Encoder checkpoint not found at: {enc_ckpt}")

    print(f"Loading encoder from {enc_ckpt}")
    encoder = ImageTokenizer(
        checkpoint_enc=enc_ckpt,
        device=device,
        dtype="bfloat16",
    )

    # ----------------------------------------------------------
    # 4) Encode all frames in batches
    # ----------------------------------------------------------
    batch_size = args.batch_size
    all_indices = []
    all_codes = []

    encoder.eval()
    with torch.no_grad():
        for start in range(0, T_frames, batch_size):
            end = min(start + batch_size, T_frames)
            batch = frames[start:end]  # [B, 3, 256, 256]

            # ImageTokenizer.encode expects Bx3xHxW in [-1, 1]
            indices, codes = encoder.encode(batch)

            # indices: [B, h, w], codes: [B, 6, h, w] for DI models
            all_indices.append(indices.cpu())
            all_codes.append(codes.cpu())

            print(
                f"Encoded frames {start}..{end - 1} -> "
                f"indices {tuple(indices.shape)}, codes {tuple(codes.shape)}"
            )

    # ----------------------------------------------------------
    # 5) Stack and convert to NumPy (cast codes off bfloat16)
    # ----------------------------------------------------------
    indices_full = torch.cat(all_indices, dim=0).to(torch.int32).numpy()    # [T, h, w]
    codes_full   = (
        torch.cat(all_codes, dim=0)
        .to(torch.float32)   # or float16 if you want smaller files
        .numpy()
    )  # [T, 6, h, w]

    print("Final token shapes:")
    print("  indices:", indices_full.shape)
    print("  codes  :", codes_full.shape)

    # ----------------------------------------------------------
    # 6) Save to NPZ
    # ----------------------------------------------------------
    np.savez_compressed(
        args.out_tokens,
        indices=indices_full,
        codes=codes_full,
        fps=fps,
        model_name=args.model_name,
    )
    print(f"Saved tokens to {args.out_tokens}")


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Decode Cosmos DI8x8 indices back into a 256x256 MP4.

Input:
  - NPZ file produced by encode_di8x8_from_mp4.py, containing:
      indices: [T, 32, 32]           (discrete tokens per frame)
      codes:   [T, 6, 32, 32]        (unused here)
      fps:     scalar
      model_name: str

Output:
  - MP4 video reconstructed from the tokens.
"""

import argparse
import os

import numpy as np
import torch
import imageio.v2 as imageio  # <-- use imageio, not torchvision

from cosmos_tokenizer.image_lib import ImageTokenizer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tokens",
        type=str,
        required=True,
        help="Path to NPZ with DI8x8 tokens (e.g. test_di8x8_tokens.npz)",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="Cosmos-0.1-Tokenizer-DI8x8",
        help="Cosmos tokenizer model name",
    )
    parser.add_argument(
        "--ckpt_dir",
        type=str,
        default="pretrained_ckpts",
        help="Directory containing downloaded checkpoints",
    )
    parser.add_argument(
        "--out_video",
        type=str,
        required=True,
        help="Output MP4 path (e.g. recon_test_di8x8.mp4)",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=32,
        help="Batch size over frames for decoding",
    )
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # ----------------------------------------------------------
    # 1) Load tokens NPZ
    # ----------------------------------------------------------
    data = np.load(args.tokens)
    indices_np = data["indices"]          # [T, 32, 32]
    fps = float(data["fps"])              # ensure plain Python float

    print(f"Loaded tokens from {args.tokens}")
    print(f"  indices shape: {indices_np.shape}")
    print(f"  fps: {fps} (type={type(fps)})")

    T_frames, h, w = indices_np.shape
    print(f"Decoding {T_frames} frames of {h}x{w} tokens")

    # ----------------------------------------------------------
    # 2) Initialize DI8x8 decoder
    # ----------------------------------------------------------
    dec_ckpt = os.path.join(args.ckpt_dir, args.model_name, "decoder.jit")
    if not os.path.exists(dec_ckpt):
        raise FileNotFoundError(f"Decoder checkpoint not found at: {dec_ckpt}")

    print(f"Loading decoder from {dec_ckpt}")
    decoder = ImageTokenizer(
        checkpoint_dec=dec_ckpt,
        device=device,
        dtype="bfloat16",
    )

    # ----------------------------------------------------------
    # 3) Decode all frames in batches
    # ----------------------------------------------------------
    indices_torch = torch.from_numpy(indices_np).to(torch.int64)  # [T, h, w]
    batch_size = args.batch_size

    decoded_frames = []  # will hold uint8 [H, W, C] arrays on CPU

    decoder.eval()
    with torch.no_grad():
        for start in range(0, T_frames, batch_size):
            end = min(start + batch_size, T_frames)
            batch_idx = indices_torch[start:end].to(device)  # [B, h, w]

            # decoder.decode expects [B, h, w] integer indices
            recon = decoder.decode(batch_idx)  # [B, 3, 256, 256], in [-1, 1], bf16

            # Map from [-1, 1] -> [0, 255] uint8, move to CPU
            recon = recon.to(torch.float32)
            recon = (recon + 1.0) / 2.0               # [0,1]
            recon = torch.clamp(recon, 0.0, 1.0)
            recon = (recon * 255.0).round().to(torch.uint8)  # [B, 3, 256, 256]

            # Convert to [B, H, W, C] numpy
            recon = recon.permute(0, 2, 3, 1).cpu().numpy()  # [B, 256, 256, 3]
            decoded_frames.append(recon)

            print(
                f"Decoded frames {start}..{end - 1} -> "
                f"{recon.shape} uint8"
            )

    # Stack into [T, H, W, C] numpy array
    video_np = np.concatenate(decoded_frames, axis=0)  # [T, 256, 256, 3]
    assert video_np.shape[0] == T_frames

    print("Final reconstructed video array:", video_np.shape, video_np.dtype)

    # ----------------------------------------------------------
    # 4) Write MP4 using imageio
    # ----------------------------------------------------------
    out_path = args.out_video
    # imageio expects (num_frames, H, W, C), uint8
    imageio.mimwrite(out_path, video_np, fps=fps)
    print(f"Wrote reconstructed video to {out_path}")


if __name__ == "__main__":
    main()



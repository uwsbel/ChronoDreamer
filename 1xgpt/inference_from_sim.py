#!/usr/bin/env python3
"""
Inference script for world model prediction from simulation data.
Creates a proper RawTokenDataset-compatible data directory and calls generate.py/visualize.py.

Usage:
    python inference_from_sim.py --frames_path /path/to/frames.npy \
                                 --actions_path /path/to/actions.npy \
                                 --joint_angles_path /path/to/joint_angles.npy \
                                 --future_actions_path /path/to/future_actions.npy \
                                 --output_dir /path/to/output \
                                 --checkpoint_dir data/genie_model/8_24_ckpt

Input format (at stride 15, so 8 frames cover 8*15=120 raw frames = 4.8 seconds):
    - frames.npy: (16, 256, 256, 3) uint8 RGB images (8 history + 8 dummy future)
    - actions.npy: (16, 3) float32 joystick actions (8 history + 8 future)
    - joint_angles.npy: (16, 4) float32 joint angles (8 history + 8 zeros for future)
      NOTE: Model only uses history joint angles, future joint angles should be zeros

Output:
    - output_dir/generated.gif: visualization with prompt, predicted, ground truth
"""

import argparse
import json
import os
import sys
import subprocess
import shutil
from pathlib import Path

# Disable tqdm progress bars before any imports that might use it
os.environ['TQDM_DISABLE'] = '1'

import numpy as np
import torch

# Add paths for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, os.path.join(SCRIPT_DIR, "cosmos/Cosmos-Tokenizer"))

from cosmos_tokenizer.image_lib import ImageTokenizer


# Constants matching training configuration
TOKENIZER_CKPT = "cosmos/Cosmos-Tokenizer/pretrained_ckpts/Cosmos-0.1-Tokenizer-DI8x8"
STRIDE = 15
NUM_PROMPT_FRAMES = 8
WINDOW_SIZE = 16
LATENT_SIZE = 32  # 32x32 tokens per frame


def parse_args():
    parser = argparse.ArgumentParser(description="Run world model inference from simulation data")
    parser.add_argument("--frames_path", type=str, required=True,
                        help="Path to frames numpy file (16, 256, 256, 3) uint8")
    parser.add_argument("--actions_path", type=str, required=True,
                        help="Path to actions numpy file (16, 3) float32")
    parser.add_argument("--joint_angles_path", type=str, required=True,
                        help="Path to joint angles numpy file (16, 4) float32")
    parser.add_argument("--output_dir", type=str, required=True,
                        help="Directory to save outputs")
    parser.add_argument("--checkpoint_dir", type=str, default="data/genie_model/8_24_ckpt",
                        help="Path to model checkpoint (relative to 1xgpt dir)")
    parser.add_argument("--temperature", type=float, default=0,
                        help="Sampling temperature (0 for greedy)")
    parser.add_argument("--maskgit_steps", type=int, default=2,
                        help="Number of MaskGIT steps per frame")
    return parser.parse_args()


def load_cosmos_encoder():
    """Load Cosmos tokenizer encoder"""
    tokenizer_path = os.path.join(SCRIPT_DIR, TOKENIZER_CKPT)
    enc_ckpt = os.path.join(tokenizer_path, "encoder.jit")
    
    print(f"Loading Cosmos encoder from: {enc_ckpt}")
    encoder = ImageTokenizer(
        checkpoint_enc=enc_ckpt,
        device="cuda",
        dtype="bfloat16",
    )
    return encoder


def encode_frames_to_tokens(encoder, frames_np):
    """
    Encode RGB frames to Cosmos DI8x8 tokens.
    
    Args:
        encoder: Cosmos ImageTokenizer with encoder
        frames_np: (N, 256, 256, 3) uint8 RGB frames
        
    Returns:
        tokens: (N, 32, 32) uint32 token indices
    """
    print(f"Encoding {frames_np.shape[0]} frames to tokens...")
    
    # Convert to tensor: (N, 3, H, W) float in [-1, 1]
    frames_tensor = torch.from_numpy(frames_np).permute(0, 3, 1, 2).float()
    frames_tensor = (frames_tensor / 255.0) * 2.0 - 1.0
    frames_tensor = frames_tensor.to(device="cuda", dtype=torch.bfloat16)
    
    with torch.no_grad():
        indices, _ = encoder.encode(frames_tensor)  # (N, 32, 32)
    
    tokens = indices.cpu().numpy().astype(np.uint32)
    print(f"  Encoded to tokens shape: {tokens.shape}")
    return tokens


def create_data_directory(temp_dir, video_tokens, actions, joint_angles):
    """
    Create a RawTokenDataset-compatible data directory.
    
    Args:
        temp_dir: Path to temp directory
        video_tokens: (num_frames, 32, 32) uint32
        actions: (num_frames, 3) float32
        joint_angles: (num_frames, 4) float32
    """
    temp_dir = Path(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    num_frames = video_tokens.shape[0]
    
    # Save video.bin - uint32 tokens
    video_path = temp_dir / "video.bin"
    video_tokens.astype(np.uint32).tofile(video_path)
    print(f"  Saved video.bin: {video_tokens.shape}")
    
    # Save actions.bin - float16
    actions_path = temp_dir / "actions.bin"
    actions.astype(np.float16).tofile(actions_path)
    print(f"  Saved actions.bin: {actions.shape}")
    
    # Save joint_angles.bin - float16
    joints_path = temp_dir / "joint_angles.bin"
    joint_angles.astype(np.float16).tofile(joints_path)
    print(f"  Saved joint_angles.bin: {joint_angles.shape}")
    
    # Save segment_ids.bin - all zeros (single segment)
    # NOTE: data.py expects int32, not uint32!
    segment_path = temp_dir / "segment_ids.bin"
    np.zeros(num_frames, dtype=np.int32).tofile(segment_path)
    print(f"  Saved segment_ids.bin: ({num_frames},)")
    
    # Create metadata.json
    metadata = {
        "clips": [{
            "name": "sim_data",
            "start": 0,
            "frames": num_frames,
            "segment_id": 0
        }],
        "latent_shape": [LATENT_SIZE, LATENT_SIZE],
        "dtype": "uint32",
        "token_dim": 6,
        "tokenizer": "Cosmos-0.1-Tokenizer-DI8x8",
        "total_frames": num_frames,
        "num_images": num_frames,
        "s": LATENT_SIZE,
        "vocab_size": 65536,
        "hz": 25
    }
    
    meta_path = temp_dir / "metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Saved metadata.json")
    
    # Debug: print file sizes
    print(f"\n  File sizes:")
    for fname in ["video.bin", "actions.bin", "joint_angles.bin", "segment_ids.bin", "metadata.json"]:
        fpath = temp_dir / fname
        if fpath.exists():
            print(f"    {fname}: {fpath.stat().st_size} bytes")
        else:
            print(f"    {fname}: NOT FOUND!")
    
    return temp_dir


def run_generate(temp_data_dir, output_dir, checkpoint_dir, temperature, maskgit_steps):
    """Run genie/generate.py"""
    generate_script = os.path.join(SCRIPT_DIR, "genie/generate.py")
    
    # NOTE: We use stride=1 because our input data is ALREADY strided
    # (we selected frames at stride 15 from the simulation buffer)
    # So the 16 frames we provide are exactly the frames we want to use
    cmd = [
        sys.executable,
        generate_script,
        "--val_data_dir", str(temp_data_dir),
        "--checkpoint_dir", checkpoint_dir,
        "--output_dir", str(output_dir),
        "--num_prompt_frames", str(NUM_PROMPT_FRAMES),
        "--window_size", str(WINDOW_SIZE),
        "--stride", "1",  # Stride=1 since our data is already strided
        "--example_ind", "0",
        "--temperature", str(temperature),
        "--maskgit_steps", str(maskgit_steps),
        "--generate_contact",
        "--skip_ground_truth",  # We don't have real ground truth in simulation
    ]
    
    print(f"\nRunning generate.py...")
    print(f"  Command: {' '.join(cmd)}")
    sys.stdout.flush()
    
    result = subprocess.run(
        cmd,
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    
    # Always print output
    print("\n=== generate.py OUTPUT ===")
    print("STDOUT:")
    print(result.stdout if result.stdout else "(empty)")
    print("\nSTDERR:")
    print(result.stderr if result.stderr else "(empty)")
    print("=== END generate.py OUTPUT ===\n")
    sys.stdout.flush()
    
    if result.returncode != 0:
        raise RuntimeError(f"generate.py failed with return code {result.returncode}")
    
    print("  generate.py completed successfully!")


def run_visualize(output_dir):
    """Run visualize.py"""
    visualize_script = os.path.join(SCRIPT_DIR, "visualize.py")
    
    cmd = [
        sys.executable,
        visualize_script,
        "--token_dir", str(output_dir),
        "--fps", "2",
        "--visualize_contact",
    ]
    
    print(f"\nRunning visualize.py...")
    print(f"  Command: {' '.join(cmd)}")
    sys.stdout.flush()
    
    result = subprocess.run(
        cmd,
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    
    print("\n=== visualize.py OUTPUT ===")
    print("STDOUT:")
    print(result.stdout if result.stdout else "(empty)")
    print("\nSTDERR:")
    print(result.stderr if result.stderr else "(empty)")
    print("=== END visualize.py OUTPUT ===\n")
    sys.stdout.flush()
    
    if result.returncode != 0:
        raise RuntimeError(f"visualize.py failed with return code {result.returncode}")
    
    print("  visualize.py completed successfully!")


def main():
    args = parse_args()
    
    print("=" * 60)
    print("WORLD MODEL INFERENCE")
    print("=" * 60)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load input data
    print(f"\nLoading input data...")
    print(f"  Frames: {args.frames_path}")
    frames = np.load(args.frames_path)  # (16, 256, 256, 3) uint8
    print(f"    Shape: {frames.shape}, dtype: {frames.dtype}")
    
    print(f"  Actions: {args.actions_path}")
    actions = np.load(args.actions_path)  # (16, 3) float32
    print(f"    Shape: {actions.shape}, dtype: {actions.dtype}")
    
    print(f"  Joint angles: {args.joint_angles_path}")
    joint_angles = np.load(args.joint_angles_path)  # (16, 4) float32
    print(f"    Shape: {joint_angles.shape}, dtype: {joint_angles.dtype}")
    
    # Validate shapes
    assert frames.shape[0] == WINDOW_SIZE, f"Expected {WINDOW_SIZE} frames, got {frames.shape[0]}"
    assert actions.shape == (WINDOW_SIZE, 3), f"Expected actions shape ({WINDOW_SIZE}, 3), got {actions.shape}"
    assert joint_angles.shape == (WINDOW_SIZE, 4), f"Expected joint_angles shape ({WINDOW_SIZE}, 4), got {joint_angles.shape}"
    
    # Load Cosmos encoder
    encoder = load_cosmos_encoder()
    
    # Encode frames to tokens
    video_tokens = encode_frames_to_tokens(encoder, frames)
    
    # Create temp data directory in the expected format
    temp_data_dir = output_dir / "temp_data"
    print(f"\nCreating data directory: {temp_data_dir}")
    create_data_directory(temp_data_dir, video_tokens, actions, joint_angles)
    
    # Run generate.py
    run_generate(
        temp_data_dir=temp_data_dir,
        output_dir=output_dir,
        checkpoint_dir=args.checkpoint_dir,
        temperature=args.temperature,
        maskgit_steps=args.maskgit_steps
    )
    
    # Run visualize.py
    run_visualize(output_dir)
    
    # Clean up temp data dir (optional - keep for debugging)
    # shutil.rmtree(temp_data_dir)
    
    print("\n" + "=" * 60)
    print("INFERENCE COMPLETE!")
    print(f"Output directory: {output_dir}")
    print("=" * 60)
    
    # Write success marker
    with open(output_dir / "done.txt", "w") as f:
        f.write("success\n")


if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception as e:
        print("=" * 60)
        print(f"ERROR: {e}")
        print("=" * 60)
        traceback.print_exc()
        sys.exit(1)

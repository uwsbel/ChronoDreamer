import numpy as np
import torch
import cv2
import json
from pathlib import Path
from magvit2.models.lfqgan import VQModel
from magvit2.config import VQConfig
from tqdm import tqdm

# -------------------------------
# Settings
# -------------------------------
bin_path = "external_data/video_0.bin"
meta_path = "external_data/metadata.json"
ckpt_path = "checkpoints/finetuned_epoch40.ckpt"
out_dir = Path("decoded_frames")
out_dir.mkdir(parents=True, exist_ok=True)
out_video = "decoded.mp4"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
batch_size = 8

# -------------------------------
# Load metadata
# -------------------------------
try:
    with open(meta_path, "r") as f:
        meta = json.load(f)
except Exception as e:
    raise RuntimeError(f"Failed to load metadata {meta_path}: {e}")
num_frames = meta.get("num_images")
if not isinstance(num_frames, int) or num_frames <= 0:
    raise ValueError("Invalid or missing num_images in metadata")
fps = float(meta.get("frame_rate", 30.0))
if fps <= 0.0:
    print("Warning: Invalid frame rate. Setting to 30.0")
    fps = 30.0
token_shape = tuple(meta.get("token_shape", [16, 16]))
print(f"Restoring {num_frames} frames at {fps} Hz, token shape {token_shape}")

# -------------------------------
# Load tokenizer
# -------------------------------
tokenizer = VQModel(VQConfig()).to(device).eval()
try:
    state = torch.load(ckpt_path, map_location=device)
    if "state_dict" in state:
        tokenizer.load_state_dict(state["state_dict"], strict=False)
    else:
        tokenizer.load_state_dict(state, strict=False)
except Exception as e:
    raise RuntimeError(f"Failed to load checkpoint {ckpt_path}: {e}")

# -------------------------------
# Validate token shape
# -------------------------------
try:
    test_tokens = torch.zeros(1, *token_shape, dtype=torch.long).to(device)
    with torch.no_grad():
        quant = tokenizer.quantize.indices_to_bits(test_tokens).permute(0, 3, 1, 2).float()
        recon = tokenizer.decode(quant)
    if recon.shape[-2:] != (256, 256):
        raise ValueError(f"Decoded frame size {recon.shape[-2:]} does not match expected (256, 256)")
except Exception as e:
    raise RuntimeError(f"Token shape {token_shape} is incompatible with model: {e}")

# -------------------------------
# Load tokens
# -------------------------------
try:
    video_data = np.memmap(bin_path, dtype=np.uint32, mode="r", shape=(num_frames, *token_shape))
except Exception as e:
    raise RuntimeError(f"Failed to load tokens from {bin_path}: {e}")

# -------------------------------
# Decode frames
# -------------------------------
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
video_writer = cv2.VideoWriter(out_video, fourcc, fps, (256, 256))
if not video_writer.isOpened():
    raise RuntimeError(f"Failed to initialize VideoWriter for {out_video}")

for start_idx in tqdm(range(0, num_frames, batch_size), desc="Decoding frames"):
    try:
        end_idx = min(start_idx + batch_size, num_frames)
        batch_tokens = torch.from_numpy(video_data[start_idx:end_idx].copy()).long().to(device)
        with torch.no_grad():
            quant = tokenizer.quantize.indices_to_bits(batch_tokens).permute(0, 3, 1, 2).float()
            recon = tokenizer.decode(quant)  # (batch_size, 3, 256, 256)
        for i, frame in enumerate(recon):
            frame = (frame.permute(1, 2, 0).cpu().numpy() + 1) / 2.0
            frame = np.clip(frame * 255, 0, 255).astype(np.uint8)
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(out_dir / f"frame_{(start_idx + i):05d}.jpg"), frame_bgr)
            video_writer.write(frame_bgr)
    except Exception as e:
        print(f"Error decoding frames {start_idx}-{end_idx}: {e}")
        continue

video_writer.release()
print(f"Decoded video saved to {out_video}")



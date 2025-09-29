import cv2
import torch
import numpy as np
import json
from pathlib import Path
from tqdm import tqdm

from magvit2.models.lfqgan import VQModel
from magvit2.config import VQConfig

# -------------------------------
# Settings
# -------------------------------
video_path = "test-vid.mp4"
ckpt_path = "checkpoints/finetuned_epoch90.ckpt"
out_dir = Path("external_data")
out_dir.mkdir(parents=True, exist_ok=True)
out_bin = out_dir / "video_0.bin"
out_meta = out_dir / "metadata.json"
batch_size = 8
resize_hw = (256, 256)

# -------------------------------
# Load tokenizer
# -------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = VQModel(VQConfig()).to(device).eval()
codebook_dim = tokenizer.quantize.codebook_dim
state = torch.load(ckpt_path, map_location=device)
if "state_dict" in state:
    tokenizer.load_state_dict(state["state_dict"], strict=False)
else:
    tokenizer.load_state_dict(state, strict=False)

# -------------------------------
# Count frames
# -------------------------------
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise FileNotFoundError(f"Could not open {video_path}")

num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_rate = float(cap.get(cv2.CAP_PROP_FPS))
if frame_rate <= 0:
    print("Warning: Invalid frame rate. Setting to default (30.0)")
    frame_rate = 30.0

# Test encode one dummy frame to infer latent H,W
test_frame = torch.zeros(1, 3, *resize_hw).to(device)
with torch.no_grad():
    quant, _, _, _ = tokenizer.encode(test_frame)
latent_h, latent_w = quant.shape[2], quant.shape[3]

# Create memmap for token IDs (uint32)
video_data = np.memmap(out_bin, dtype=np.uint32, mode="w+",
                       shape=(num_frames, latent_h, latent_w))

# -------------------------------
# Encode frames
# -------------------------------
frame_idx, frames = 0, []
for _ in tqdm(range(num_frames), desc="Encoding frames"):
    ret, frame = cap.read()
    if not ret or frame is None or frame.size == 0:
        print(f"Warning: Skipping invalid frame at index {frame_idx}")
        continue

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, resize_hw)
    frame = frame.astype(np.float32) / 255.0
    tensor = torch.from_numpy(frame).permute(2, 0, 1)
    frames.append(tensor)

    if len(frames) == batch_size:
        batch = torch.stack(frames).to(device)
        with torch.no_grad():
            # Normalize to [-1,1]
            quant, _, _, _ = tokenizer.encode(batch * 2 - 1)
            # Convert to token IDs (B,H,W), each entry in [0, 2^bits)
            token_ids = tokenizer.quantize.bits_to_indices(
                quant.permute(0, 2, 3, 1) > 0
            ).cpu().numpy().astype(np.uint32)

        video_data[frame_idx:frame_idx + token_ids.shape[0]] = token_ids
        frame_idx += token_ids.shape[0]
        frames = []

# Handle leftover frames
if frames:
    batch = torch.stack(frames).to(device)
    with torch.no_grad():
        quant, _, _, _ = tokenizer.encode(batch * 2 - 1)
        token_ids = tokenizer.quantize.bits_to_indices(
            quant.permute(0, 2, 3, 1) > 0
        ).cpu().numpy().astype(np.uint32)
        print(token_ids.shape)

    video_data[frame_idx:frame_idx + token_ids.shape[0]] = token_ids
    frame_idx += token_ids.shape[0]

cap.release()
video_data.flush()
print(f"Encoding complete. Saved {frame_idx} frames to {out_bin}")

# -------------------------------
# Metadata
# -------------------------------
metadata = {
    "num_images": int(frame_idx),
    "frame_rate": frame_rate,
    "resolution": list(resize_hw),
    "latent_shape": [latent_h, latent_w],  # no channel dim
    "dtype": "uint32"
}
with open(out_meta, "w") as f:
    json.dump(metadata, f, indent=2)
print(f"Metadata written to {out_meta}")



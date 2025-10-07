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
video_path = "test-vid-2.mp4"
ckpt_path = "checkpoints/finetuned_epoch90.ckpt"
out_dir = Path("external_data")
out_dir.mkdir(parents=True, exist_ok=True)
out_bin = out_dir / "video_0.bin"
out_meta = out_dir / "metadata.json"
batch_size = 8

# -------------------------------
# Load tokenizer
# -------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = VQModel(VQConfig()).to(device).eval()
state = torch.load(ckpt_path, map_location=device)
if "state_dict" in state:
    tokenizer.load_state_dict(state["state_dict"], strict=False)
else:
    tokenizer.load_state_dict(state, strict=False)

# -------------------------------
# Determine latent shape
# -------------------------------
test_frame = torch.zeros(1, 3, 256, 256).to(device)
with torch.no_grad():
    z_e = tokenizer.encoder(test_frame)
    quant, _, *_ = tokenizer.quantize(z_e)

print("Quant shape from quantize:", quant.shape)  # expect (B,18,16,16)
B, C, H, W = quant.shape
latent_shape = (C, H, W)

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

video_data = np.memmap(out_bin, dtype=np.float16, mode="w+",
                       shape=(num_frames, *latent_shape))

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
    frame = cv2.resize(frame, (256, 256))
    frame = frame.astype(np.float32) / 255.0
    tensor = torch.from_numpy(frame).permute(2, 0, 1)
    frames.append(tensor)

    if len(frames) == batch_size:
        batch = torch.stack(frames).to(device) * 2 - 1
        with torch.no_grad():
            z_e = tokenizer.encoder(batch)
            quant, _, *_ = tokenizer.quantize(z_e)  # already (B,C,H,W)
        video_data[frame_idx:frame_idx + quant.shape[0]] = quant.cpu().numpy().astype(np.float16)
        print(quant)
        frame_idx += quant.shape[0]
        frames = []

if frames:
    batch = torch.stack(frames).to(device) * 2 - 1
    with torch.no_grad():
        z_e = tokenizer.encoder(batch)
        print(f"[Debug] Encoded ze latent shape: {z_e.shape}")  # <<< ADD THIS
        quant, _, *_ = tokenizer.quantize(z_e)
    print(f"[Debug] Encoded batch latent shape: {quant.shape}")  # <<< ADD THIS
    video_data[frame_idx:frame_idx + quant.shape[0]] = quant.cpu().numpy().astype(np.float16)
    frame_idx += quant.shape[0]

cap.release()
video_data.flush()
print(f"Encoding complete. Saved {frame_idx} frames to {out_bin}")

# -------------------------------
# Metadata
# -------------------------------
metadata = {
    "num_images": int(frame_idx),
    "frame_rate": frame_rate,
    "resolution": [256, 256],
    "latent_shape": list(latent_shape),  # (C,H,W)
    "dtype": "float16"
}
with open(out_meta, "w") as f:
    json.dump(metadata, f, indent=2)
print(f"Metadata written to {out_meta}")




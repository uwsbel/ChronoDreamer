import cv2
import torch
import numpy as np
import json
from magvit2.models.lfqgan import VQModel
from magvit2.config import VQConfig
from pathlib import Path
from tqdm import tqdm

# -------------------------------
# Settings
# -------------------------------
video_path = "test-vid.mp4"
ckpt_path = "checkpoints/finetuned_epoch40.ckpt"
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
try:
    state = torch.load(ckpt_path, map_location=device)
    if "state_dict" in state:
        tokenizer.load_state_dict(state["state_dict"], strict=False)
    else:
        tokenizer.load_state_dict(state, strict=False)
except Exception as e:
    raise RuntimeError(f"Failed to load checkpoint {ckpt_path}: {e}")

# -------------------------------
# Determine token shape
# -------------------------------
test_frame = torch.zeros(1, 3, 256, 256).to(device)
with torch.no_grad():
    quant, _, _, _ = tokenizer.encode(test_frame)
    token_ids = tokenizer.quantize.bits_to_indices((quant.permute(0, 2, 3, 1) > 0)).cpu().numpy()
    token_shape = token_ids.shape[1:3]  # e.g., (16, 16)

# -------------------------------
# Pass 1: count frames
# -------------------------------
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise FileNotFoundError(f"Could not open {video_path}")
num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_rate = float(cap.get(cv2.CAP_PROP_FPS))
if frame_rate <= 0:
    print("Warning: Invalid frame rate. Setting to default (30.0)")
    frame_rate = 30.0
video_data = np.memmap(out_bin, dtype=np.uint32, mode="w+", shape=(num_frames, *token_shape))

# -------------------------------
# Pass 2: encode frames
# -------------------------------
frame_idx = 0
frames = []
for _ in tqdm(range(num_frames), desc="Encoding frames"):
    try:
        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            print(f"Warning: Skipping invalid frame at index {frame_idx}")
            continue
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (256, 256))  # Ensure 256x256
        frame = frame.astype(np.float32) / 255.0
        tensor = torch.from_numpy(frame).permute(2, 0, 1)
        frames.append(tensor)
        if len(frames) == batch_size:
            batch = torch.stack(frames).to(device) * 2 - 1
            with torch.no_grad():
                quant, _, _, _ = tokenizer.encode(batch)
                token_ids = tokenizer.quantize.bits_to_indices(
                    (quant.permute(0, 2, 3, 1) > 0)
                ).cpu().numpy()
            video_data[frame_idx:frame_idx + batch_size] = token_ids
            frame_idx += batch_size
            frames = []
    except Exception as e:
        print(f"Error processing frame {frame_idx}: {e}")
        continue

# Process remaining frames
if frames:
    batch = torch.stack(frames).to(device) * 2 - 1
    with torch.no_grad():
        quant, _, _, _ = tokenizer.encode(batch)
        token_ids = tokenizer.quantize.bits_to_indices(
            (quant.permute(0, 2, 3, 1) > 0)
        ).cpu().numpy()
    video_data[frame_idx:frame_idx + len(frames)] = token_ids
    frame_idx += len(frames)

cap.release()
video_data.flush()
print(f"Encoding complete. Saved {frame_idx} frames to {out_bin}")
if frame_idx != num_frames:
    print(f"Warning: Processed {frame_idx} frames, expected {num_frames}")
    num_frames = frame_idx

# -------------------------------
# Metadata
# -------------------------------
metadata = {
    "num_images": int(num_frames),
    "frame_rate": frame_rate,
    "resolution": [256, 256],
    "token_shape": list(token_shape),
    "dtype": "uint32"
}
with open(out_meta, "w") as f:
    json.dump(metadata, f, indent=2)
print(f"Metadata written to {out_meta}")


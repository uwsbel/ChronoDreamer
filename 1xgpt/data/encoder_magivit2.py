import cv2
import torch
import numpy as np
import json
from magvit2.models.lfqgan import VQModel
from magvit2.config import VQConfig
from pathlib import Path

# -------------------------------
# Settings
# -------------------------------
video_path = "test-vid.mp4"
ckpt_path = "magvit2.ckpt"
out_dir = Path("external_data")
out_dir.mkdir(parents=True, exist_ok=True)
out_bin = out_dir / "video_0.bin"
out_meta = out_dir / "metadata.json"

# -------------------------------
# Load tokenizer (MagViT2 image encoder/decoder)
# -------------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = VQModel(VQConfig(), ckpt_path=ckpt_path).to(device).eval()

# -------------------------------
# Pass 1: count frames
# -------------------------------
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise FileNotFoundError(f"Could not open {video_path}")

num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"Total frames: {num_frames}")

# Shape of tokens per frame: (16,16), dtype=uint32
video_data = np.memmap(out_bin, dtype=np.uint32, mode="w+", shape=(num_frames, 16, 16))

# -------------------------------
# Pass 2: encode frames
# -------------------------------
frame_idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert BGR (OpenCV) -> RGB, normalize to [0,1]
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = frame.astype(np.float32) / 255.0

    # To tensor: (3,256,256)
    tensor = torch.from_numpy(frame).permute(2, 0, 1).unsqueeze(0).to(device)

    # Scale to [-1,1] as expected
    tensor = tensor * 2 - 1

    # Encode
    with torch.no_grad():
        quant, _, _, _ = tokenizer.encode(tensor)
        token_ids = tokenizer.quantize.bits_to_indices(
            (quant.permute(0, 2, 3, 1) > 0)
        ).cpu().numpy()  # shape (1,16,16)

    video_data[frame_idx] = token_ids[0]
    frame_idx += 1

cap.release()
video_data.flush()
print(f"Encoding complete. Saved {frame_idx} frames to {out_bin}")

# -------------------------------
# Metadata
# -------------------------------
metadata = {
    "num_images": int(num_frames),
    "frame_rate": float(cap.get(cv2.CAP_PROP_FPS)),  # 30.0 for your file
    "resolution": [256, 256],
    "token_shape": [16, 16],
    "dtype": "uint32"
}
with open(out_meta, "w") as f:
    json.dump(metadata, f, indent=2)
print(f"Metadata written to {out_meta}")


import numpy as np
import torch
import cv2
import json
from pathlib import Path
from magvit2.models.lfqgan import VQModel
from magvit2.config import VQConfig

# -------------------------------
# Settings
# -------------------------------
bin_path = "external_data/video_0.bin"
meta_path = "external_data/metadata.json"
ckpt_path = "magvit2.ckpt"
out_dir = Path("decoded_frames")
out_dir.mkdir(parents=True, exist_ok=True)
out_video = "decoded.mp4"

device = "cuda" if torch.cuda.is_available() else "cpu"

# -------------------------------
# Load metadata
# -------------------------------
with open(meta_path, "r") as f:
    meta = json.load(f)

num_frames = meta.get("num_images")
fps = float(meta.get("frame_rate", 30.0))
if fps <= 0.0:
    fps = 30.0
token_shape = tuple(meta.get("token_shape", [16, 16]))

print(f"Restoring {num_frames} frames at {fps} Hz")

# -------------------------------
# Load tokenizer
# -------------------------------
tokenizer = VQModel(VQConfig(), ckpt_path=ckpt_path).to(device).eval()

# -------------------------------
# Load tokens
# -------------------------------
video_data = np.memmap(
    bin_path, dtype=np.uint32, mode="r", shape=(num_frames, *token_shape)
)

# -------------------------------
# Decode frames
# -------------------------------
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
video_writer = cv2.VideoWriter(out_video, fourcc, fps, (256, 256))

for idx in range(num_frames):
    # Convert token IDs to torch.LongTensor
    token_ids = torch.from_numpy(video_data[idx].copy()).long().unsqueeze(0).to(device)

    with torch.no_grad():
        quant = tokenizer.quantize.indices_to_bits(token_ids).permute(0, 3, 1, 2)
        quant = quant.float()  # decoder expects float, not bool
        recon = tokenizer.decode(quant)  # (1, 3, 256, 256)

    # Convert back to uint8 image
    frame = (recon.squeeze(0).permute(1, 2, 0).cpu().numpy() + 1) / 2.0
    frame = np.clip(frame * 255, 0, 255).astype(np.uint8)

    # Save frame as .jpg
    cv2.imwrite(
        str(out_dir / f"frame_{idx:05d}.jpg"), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    )

    # Write to video
    video_writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    if idx % 100 == 0:
        print(f"Decoded {idx}/{num_frames} frames...")

video_writer.release()
print(f"Decoded video saved to {out_video}")



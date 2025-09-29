import numpy as np
import torch
import cv2
import json
from pathlib import Path
from tqdm import tqdm
from magvit2.models.lfqgan import VQModel
from magvit2.config import VQConfig

# -------------------------------
# Settings
# -------------------------------
bin_path = "external_data/video_0.bin"
meta_path = "external_data/metadata.json"
ckpt_path = "checkpoints/finetuned_epoch90.ckpt"
out_dir = Path("decoded_frames")
out_dir.mkdir(parents=True, exist_ok=True)
out_video = "decoded.mp4"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
batch_size = 8

# -------------------------------
# Load metadata
# -------------------------------
with open(meta_path, "r") as f:
    meta = json.load(f)

num_frames = meta["num_images"]
fps = float(meta.get("frame_rate", 30.0))
latent_shape = tuple(meta.get("latent_shape", []))  # (C,H,W)
if len(latent_shape) != 3:
    raise RuntimeError("Invalid metadata. Expected latent_shape [C,H,W].")

print(f"Restoring {num_frames} frames at {fps} Hz, latent_shape {latent_shape}")

# -------------------------------
# Load tokenizer
# -------------------------------
tokenizer = VQModel(VQConfig()).to(device).eval()
state = torch.load(ckpt_path, map_location=device)
if "state_dict" in state:
    tokenizer.load_state_dict(state["state_dict"], strict=False)
else:
    tokenizer.load_state_dict(state, strict=False)

# -------------------------------
# Load latents
# -------------------------------
video_data = np.memmap(bin_path, dtype=np.float16, mode="r", shape=(num_frames, *latent_shape))

# -------------------------------
# Decode frames
# -------------------------------
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
video_writer = cv2.VideoWriter(out_video, fourcc, fps, (256, 256))
if not video_writer.isOpened():
    raise RuntimeError(f"Failed to initialize VideoWriter for {out_video}")

for start_idx in tqdm(range(0, num_frames, batch_size), desc="Decoding frames"):
    end_idx = min(start_idx + batch_size, num_frames)
    quant = torch.from_numpy(video_data[start_idx:end_idx].copy()).float().to(device)  # (B,C,H,W)

    with torch.no_grad():
        recon = tokenizer.decode(quant)  # (B,3,256,256)

    for i, frame in enumerate(recon):
        frame = (frame.permute(1, 2, 0).cpu().numpy() + 1) / 2.0
        frame = np.clip(frame * 255, 0, 255).astype(np.uint8)
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(out_dir / f"frame_{(start_idx + i):05d}.jpg"), frame_bgr)
        video_writer.write(frame_bgr)

video_writer.release()
print(f"Decoded video saved to {out_video}")




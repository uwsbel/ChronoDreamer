import numpy as np
import torch
import cv2
import json
from pathlib import Path
from tqdm import tqdm
from einops import rearrange

from magvit2.models.lfqgan import VQModel
from magvit2.config import VQConfig

def rescale_magvit_output(magvit_output):
    """
    [-1, 1] -> [0, 255]

    Important: clip to [0, 255]
    """
    rescaled_output = ((magvit_output.detach().cpu() + 1) * 127.5)
    clipped_output = torch.clamp(rescaled_output, 0, 255).to(dtype=torch.uint8)
    return clipped_output

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
dtype = torch.float32   # safer; use torch.bfloat16 if your GPU supports it

# -------------------------------
# Load metadata
# -------------------------------
with open(meta_path, "r") as f:
    meta = json.load(f)

num_frames = meta["num_images"]
fps = float(meta.get("frame_rate", 30.0))
latent_shape = tuple(meta["latent_shape"])  # (H, W)

print(f"Decoding {num_frames} frames @ {fps} fps, latent grid {latent_shape}")

# -------------------------------
# Load tokenizer
# -------------------------------
tokenizer = VQModel(VQConfig(), ckpt_path=ckpt_path).to(device=device, dtype=dtype).eval()
codebook_dim = tokenizer.quantize.codebook_dim
state = torch.load(ckpt_path, map_location=device)
if "state_dict" in state:
    tokenizer.load_state_dict(state["state_dict"], strict=False)
else:
    tokenizer.load_state_dict(state, strict=False)

# -------------------------------
# Load tokens (uint32)
# -------------------------------
video_data = np.memmap(
    bin_path, dtype=np.uint32, mode="r", shape=(num_frames, *latent_shape)
)

# -------------------------------
# Video writer
# -------------------------------
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(str(out_video), fourcc, fps, (256, 256))
if not writer.isOpened():
    raise RuntimeError(f"Failed to initialize writer for {out_video}")

recon_scaled = []

# -------------------------------
# Decode
# -------------------------------
for start_idx in tqdm(range(0, num_frames, batch_size), desc="Decoding"):
    end_idx = min(start_idx + batch_size, num_frames)
    
    with torch.no_grad():
        # Load indices as (B, H, W)
        indices = torch.from_numpy(video_data[start_idx:end_idx].copy()).long().to(device)
        batch_size_actual = indices.shape[0]
        h, w = indices.shape[1], indices.shape[2]

        # Convert token IDs back to quantized latents
        # Step 1: Convert indices to bits using corrected indices_to_bits
        bits = tokenizer.quantize.indices_to_bits(indices.flatten())
        # Step 2: Reshape to match original quantized shape
        bits = bits.view(indices.shape[0], indices.shape[1], indices.shape[2], tokenizer.quantize.codebook_dim)
        # Step 3: Convert bits to quantized values (-1 or 1)
        quant = bits.float() * 2.0 - 1.0
        # Step 4: Reshape to (B, C, H, W) format
        quant = quant.permute(0, 3, 1, 2)
        
        # Decode to image frames
        recon = tokenizer.decode(quant.to(device=device, dtype=dtype))
        recon_scaled_batch = rescale_magvit_output(recon)  # (B, 3, 256, 256)

    # Save frames - iterate over the batch dimension
    for i, img in enumerate(recon_scaled_batch):
        # img is now (3, 256, 256) - single image
        rgb = img.permute(1, 2, 0).numpy()  # (256, 256, 3)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(out_dir / f"frame_{(start_idx + i):05d}.jpg"), bgr)
        writer.write(bgr)

writer.release()
print(f"Decoded video saved to {out_video}")





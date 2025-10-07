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
root_dir = Path("exp_data")        # top-level folder containing experiments
ckpt_path = Path("checkpoints/finetuned_epoch90.ckpt")
resize_hw = (256, 256)
batch_size = 8

# Output folder
out_dir = Path("external_data")
out_dir.mkdir(parents=True, exist_ok=True)
out_bin = out_dir / "video.bin"
out_meta = out_dir / "metadata.json"
out_seg = out_dir / "segment_ids.bin"

# Remove old outputs if re-running
for f in [out_bin, out_meta, out_seg]:
    if f.exists():
        f.unlink()

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

# Test encode one dummy frame to infer latent shape
test_frame = torch.zeros(1, 3, *resize_hw).to(device)
with torch.no_grad():
    quant, _, _, _ = tokenizer.encode(test_frame)
latent_h, latent_w = quant.shape[2], quant.shape[3]
codebook_dim = tokenizer.quantize.codebook_dim

# -------------------------------
# Helper to encode one video
# -------------------------------
def encode_video(video_path, file_handle):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"⚠️  Could not open {video_path}")
        return 0

    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    if frame_rate <= 0:
        frame_rate = 30.0

    frame_idx = 0
    frames = []

    for _ in tqdm(range(num_frames), desc=f"Encoding {video_path.name}", leave=False):
        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            continue
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, resize_hw)
        frame = frame.astype(np.float32) / 255.0
        tensor = torch.from_numpy(frame).permute(2, 0, 1)
        frames.append(tensor)

        if len(frames) == batch_size:
            batch = torch.stack(frames).to(device)
            with torch.no_grad():
                quant, _, _, _ = tokenizer.encode(batch * 2 - 1)
                token_ids = tokenizer.quantize.bits_to_indices(
                    quant.permute(0, 2, 3, 1) > 0
                ).cpu().numpy().astype(np.uint32)
            token_ids.tofile(file_handle)
            frame_idx += token_ids.shape[0]
            frames = []

    # Handle leftovers
    if frames:
        batch = torch.stack(frames).to(device)
        with torch.no_grad():
            quant, _, _, _ = tokenizer.encode(batch * 2 - 1)
            token_ids = tokenizer.quantize.bits_to_indices(
                quant.permute(0, 2, 3, 1) > 0
            ).cpu().numpy().astype(np.uint32)
        token_ids.tofile(file_handle)
        frame_idx += token_ids.shape[0]

    cap.release()
    return frame_idx

# -------------------------------
# Process all experiments
# -------------------------------
metadata = {
    "clips": [],
    "latent_shape": [latent_h, latent_w],
    "dtype": "uint32",
    "token_dim": codebook_dim,
}

total_frames = 0

with open(out_bin, "ab") as fbin, open(out_seg, "ab") as fseg:
    exp_dirs = sorted([d for d in root_dir.iterdir() if d.is_dir()])

    for exp_idx, exp_dir in enumerate(exp_dirs):
        sensor_dir = exp_dir / "sensor_img"
        video_path = sensor_dir / "video.mp4"

        if not video_path.exists():
            print(f"Skipping {exp_dir.name}: no sensor_img/video.mp4")
            continue

        print(f"🎥 Processing {video_path}")
        start_frame = total_frames
        nframes = encode_video(video_path, fbin)
        print(f"  ✅ Encoded {nframes} frames from {exp_dir.name}")

        # Write segment IDs for this video
        if nframes > 0:
            np.full(nframes, exp_idx, dtype=np.uint32).tofile(fseg)

        metadata["clips"].append({
            "name": exp_dir.name,
            "start": start_frame,
            "frames": nframes,
            "segment_id": exp_idx,
        })
        total_frames += nframes

metadata["total_frames"] = total_frames

# -------------------------------
# Save metadata
# -------------------------------
with open(out_meta, "w") as f:
    json.dump(metadata, f, indent=2)

print(f"\n✅ All done! Saved {total_frames} total frames to {out_bin}")
print(f"🧩 Segment IDs written to {out_seg}")
print(f"📄 Metadata written to {out_meta}")




#!/usr/bin/env python3
import json
import sys
import csv
from pathlib import Path

import cv2
import numpy as np
import torch
from tqdm import tqdm

from magvit2.models.lfqgan import VQModel
from magvit2.config import VQConfig

# ---------------------------------------
# Settings
# ---------------------------------------
root_dir = Path("exp_data")        # experiments live here: exp_data/*/{sensor_img, joystick_commands.csv}
ckpt_path = Path("checkpoints/action_data_finetune.ckpt")
resize_hw = (256, 256)
batch_size = 8

out_dir = Path("external_data")
out_dir.mkdir(parents=True, exist_ok=True)
out_bin = out_dir / "video.bin"          # uint32 tokens: (total_frames, latent_h, latent_w)
out_actions = out_dir / "actions.bin"    # float16 actions: (total_frames, 3) in [axis_x, axis_y, axis_right_y]
out_meta = out_dir / "metadata.json"
out_seg = out_dir / "segment_ids.bin"    # uint32: (total_frames,)

# Clean old outputs
for f in [out_bin, out_actions, out_meta, out_seg]:
    if f.exists():
        f.unlink()

# ---------------------------------------
# Model setup
# ---------------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = VQModel(VQConfig()).to(device).eval()
state = torch.load(ckpt_path, map_location=device)
tokenizer.load_state_dict(state.get("state_dict", state), strict=False)

# Infer latent grid by encoding one dummy frame
with torch.no_grad():
    test_frame = torch.zeros(1, 3, *resize_hw, device=device)
    quant, _, _, _ = tokenizer.encode(test_frame)  # quant: (1, Cbits, Hq, Wq) with {-1, +1}
latent_h, latent_w = quant.shape[2], quant.shape[3]
codebook_dim = int(getattr(tokenizer.quantize, "codebook_dim", getattr(tokenizer.quantize, "code_dim", 0)))
if codebook_dim <= 0:
    raise RuntimeError("Could not infer codebook_dim from tokenizer.quantize")

# ---------------------------------------
# Helpers
# ---------------------------------------
CHANNELS = ["axis_x", "axis_y", "axis_right_y"]

def read_joystick_csv(csv_path: Path):
    """Read joystick CSV into (t, X) where t is float64 sim_time, X is (N,3) float64."""
    times = []
    cols = {k: [] for k in CHANNELS}
    with csv_path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        if "sim_time" not in reader.fieldnames:
            raise ValueError(f"{csv_path}: missing 'sim_time'")
        for ch in CHANNELS:
            if ch not in reader.fieldnames:
                raise ValueError(f"{csv_path}: missing '{ch}'")
        for row in reader:
            try:
                t = float(row["sim_time"])
                vals = [float(row[ch]) for ch in CHANNELS]
            except Exception:
                continue
            times.append(t)
            for ch, v in zip(CHANNELS, vals):
                cols[ch].append(v)
    if not times:
        raise ValueError(f"{csv_path}: no valid rows")
    t = np.asarray(times, dtype=np.float64)  # guaranteed monotonic increasing by your data contract
    X = np.stack([np.asarray(cols[ch], dtype=np.float64) for ch in CHANNELS], axis=1)
    return t, X  # t: (N,), X: (N,3)

def resample_actions_to_nframes(t_in, X_in, nframes):
    """
    Resample joystick channels to exactly nframes over sim_time [0, 60].
    Uses linear interpolation; clamps at edges.
    Returns float16 array of shape (nframes, 3).
    """
    if nframes <= 0:
        return np.empty((0, 3), dtype=np.float16)
    t_out = np.linspace(0.0, 60.0, nframes, dtype=np.float64)
    out = np.empty((nframes, X_in.shape[1]), dtype=np.float64)
    for j in range(X_in.shape[1]):
        out[:, j] = np.interp(t_out, t_in, X_in[:, j])
    return out.astype(np.float16, copy=False)

def encode_video_to_tokens(video_path: Path, f_tokens) -> int:
    """
    Read frames from video, encode to token indices, append to f_tokens.
    Returns the number of frames written.
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"⚠️  Could not open {video_path}")
        return 0

    n_written = 0
    frames = []

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        total = None  # tqdm without fixed length

    pbar = tqdm(total=total, desc=f"Encoding {video_path.name}", leave=False)
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame is None or frame.size == 0:
                pbar.update(1)
                continue

            # BGR -> RGB, resize, [0..1], CHW tensor
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, resize_hw, interpolation=cv2.INTER_AREA)
            frame = frame.astype(np.float32) / 255.0
            frames.append(torch.from_numpy(frame).permute(2, 0, 1))  # (3,H,W)

            if len(frames) == batch_size:
                batch = torch.stack(frames).to(device)
                with torch.no_grad():
                    quant, _, _, _ = tokenizer.encode(batch * 2 - 1)  # [-1,1]
                    # Convert {-1,+1} bits -> boolean -> indices (uint32)
                    bits = (quant.permute(0, 2, 3, 1) > 0)  # (B,Hq,Wq,Cbits) bool
                    token_ids = tokenizer.quantize.bits_to_indices(bits).cpu().numpy().astype(np.uint32)
                token_ids.tofile(f_tokens)
                n_written += token_ids.shape[0]
                frames = []
            pbar.update(1)
    finally:
        cap.release()
        pbar.close()

    # leftover batch
    if frames:
        batch = torch.stack(frames).to(device)
        with torch.no_grad():
            quant, _, _, _ = tokenizer.encode(batch * 2 - 1)
            bits = (quant.permute(0, 2, 3, 1) > 0)
            token_ids = tokenizer.quantize.bits_to_indices(bits).cpu().numpy().astype(np.uint32)
        token_ids.tofile(f_tokens)
        n_written += token_ids.shape[0]

    return n_written

# ---------------------------------------
# Main processing across experiments
# ---------------------------------------
metadata = {
    "clips": [],
    "latent_shape": [latent_h, latent_w],
    "dtype": "uint32",
    "token_dim": codebook_dim,
}
total_frames = 0

exp_dirs = sorted([d for d in root_dir.iterdir() if d.is_dir()])

with open(out_bin, "ab") as f_tokens, open(out_seg, "ab") as f_seg, open(out_actions, "ab") as f_actions:
    for exp_idx, exp_dir in enumerate(exp_dirs):
        video_path = exp_dir / "sensor_img" / "video.mp4"
        action_csv = exp_dir / "joystick_commands.csv"

        # Require BOTH files per experiment; don't mix or partially write
        if (not video_path.exists()) or (not action_csv.exists()):
            missing = []
            if not video_path.exists(): missing.append("sensor_img/video.mp4")
            if not action_csv.exists(): missing.append("joystick_commands.csv")
            print(f"Skipping {exp_dir.name}: missing {', '.join(missing)}")
            continue

        print(f"🎥 Processing {exp_dir.name}")

        # 1) Encode video -> tokens
        start = total_frames
        nframes = encode_video_to_tokens(video_path, f_tokens)
        if nframes <= 0:
            print(f"  ⚠️ No frames written for {exp_dir.name}, skipping actions/segments.")
            continue

        # 2) Append segment IDs (uint32)
        np.full(nframes, exp_idx, dtype=np.uint32).tofile(f_seg)

        # 3) Read & resample joystick actions to nframes, then append (float16)
        try:
            t_js, X_js = read_joystick_csv(action_csv)
        except Exception as e:
            print(f"  ❌ Failed to read actions for {exp_dir.name}: {e}")
            # Rollback is non-trivial for streamed bin; instead, we skip this EXP entirely by not counting frames
            # But to maintain one-to-one alignment, we *must* also skip the video we just wrote — which we cannot delete now.
            # Safer approach: since joystick CSV is guaranteed per your spec, we treat this as fatal.
            raise

        Y = resample_actions_to_nframes(t_js, X_js, nframes)  # (nframes,3) float16
        Y.tofile(f_actions)

        # 4) Record metadata entry
        metadata["clips"].append({
            "name": exp_dir.name,
            "start": start,
            "frames": nframes,
            "segment_id": exp_idx,
        })
        total_frames += nframes
        print(f"  ✅ Frames: {nframes} | start={start} | latent=({latent_h},{latent_w}) | actions appended")

metadata["total_frames"] = total_frames

# Save metadata
with open(out_meta, "w") as f:
    json.dump(metadata, f, indent=2)

# ---------------------------------------
# Final status + memmap tips
# ---------------------------------------
print(f"\n✅ Done. Total frames: {total_frames}")
print(f"📦 Tokens    : {out_bin}")
print(f"🎮 Actions   : {out_actions}")
print(f"🧩 Segments  : {out_seg}")
print(f"📄 Metadata  : {out_meta}")

print("\nMemmap hints:")
print(f"  tokens  = np.memmap('{out_bin}', dtype=np.uint32, mode='r', shape=({total_frames}, {latent_h}, {latent_w}))")
print(f"  actions = np.memmap('{out_actions}', dtype=np.float16, mode='r', shape=({total_frames}, 3))")
print(f"  seg_ids = np.memmap('{out_seg}', dtype=np.uint32, mode='r', shape=({total_frames},))")


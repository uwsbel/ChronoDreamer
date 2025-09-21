import math
import json
from pathlib import Path

import av
import numpy as np
import torch
import torchvision.transforms as T

from cosmos_tokenizer.video_lib import CausalVideoTokenizer

# ========= CONFIG =========
input_video = Path("test-vid.mp4")
output_dir = Path("/1xgpt-test")
output_dir.mkdir(parents=True, exist_ok=True)

model_name = "Cosmos-Tokenizer-DV8x8x8"
encoder_path = Path("pretrained_ckpts") / model_name / "encoder.jit"

rank = 0   # shard index, matching decoder convention
fps = 30   # expected frame rate
resolution = 256
frames_per_chunk = 17
# ==========================

# --- load encoder ---
encoder = CausalVideoTokenizer(checkpoint_enc=str(encoder_path))
if encoder._enc_model is None:
    raise RuntimeError(f"Failed to load encoder model from {encoder_path}")
print("Encoder initialized successfully.")

# --- video reader ---
container = av.open(str(input_video))
stream = container.streams.video[0]
stream.thread_type = "AUTO"

transform = T.Compose([
    T.Resize((resolution, resolution)),
    T.ToTensor()  # (C,H,W) in [0,1]
])

# --- read frames ---
frames = []
for frame in container.decode(video=0):
    img = frame.to_ndarray(format="rgb24")
    tensor = transform(img).unsqueeze(0)  # (1,3,H,W)
    frames.append(tensor)

video_tensor = torch.cat(frames, dim=0)  # (T,3,H,W)
print(f"Loaded video tensor: {video_tensor.shape}")  # (frames,3,256,256)

# --- chunk into 17-frame segments ---
num_chunks = math.ceil(video_tensor.shape[0] / frames_per_chunk)
encoded_tokens = []

with torch.no_grad():
    for i in range(num_chunks):
        start = i * frames_per_chunk
        end = min((i + 1) * frames_per_chunk, video_tensor.shape[0])

        clip = video_tensor[start:end]  # (t,3,256,256)
        if clip.shape[0] < frames_per_chunk:
            # pad with last frame if not enough
            pad_frames = frames_per_chunk - clip.shape[0]
            pad = clip[-1:].repeat(pad_frames, 1, 1, 1)
            clip = torch.cat([clip, pad], dim=0)

        clip = clip.unsqueeze(0).cuda()  # (1,17,3,256,256) expected
        tokens = encoder.encode(clip).cpu().numpy()  # (1,3,32,32)
        encoded_tokens.append(tokens[0])

        if i % 10 == 0:
            print(f"Processed chunk {i+1}/{num_chunks}")

encoded_tokens = np.stack(encoded_tokens, axis=0)  # (num_chunks,3,32,32)

# --- save binary shard ---
bin_path = output_dir / f"video_{rank}.bin"
encoded_video_dataset = np.memmap(
    bin_path, dtype=np.int32, mode="w+",
    shape=encoded_tokens.shape
)
encoded_video_dataset[:] = encoded_tokens[:]
encoded_video_dataset.flush()

# --- save metadata ---
metadata = {
    "shard_num_frames": video_tensor.shape[0],
    "fps": fps,
    "resolution": resolution,
    "frames_per_chunk": frames_per_chunk
}
metadata_path = output_dir / f"metadata_{rank}.json"
with open(metadata_path, "w") as f:
    json.dump(metadata, f, indent=2)

print(f"Saved encoded tokens to {bin_path}")
print(f"Saved metadata to {metadata_path}")


"""
NOTE: Download the Cosmos-Tokenizer repository and pre-trained model weights before running this script.
For full installation and setup instructions, please refer to:
https://github.com/NVIDIA/Cosmos-Tokenizer#readme
"""

import math
from pathlib import Path

import av
import numpy as np
import torch

from cosmos_tokenizer.utils import tensor2numpy
from cosmos_tokenizer.video_lib import CausalVideoTokenizer

input_dir = Path("../worldmodel/val_v2.0")
output_dir = Path("/tmp/reconst_1xgpt/")
model_name = "Cosmos-Tokenizer-DV8x8x8"
decoder_path = Path("pretrained_ckpts") / model_name / "decoder.jit"

print(f"Output directory exists: {input_dir.exists()}")
print(f"Decoder path exists: {decoder_path.exists()}")

rank = 0
metadata_path = input_dir / f"metadata_{rank}.json"
if not metadata_path.exists():
    raise FileNotFoundError(f"Metadata file not found at {metadata_path}")

with open(metadata_path, "r") as f:
    metadata_shard = json.load(f)

total_frames = metadata_shard["shard_num_frames"]
print(f"Total frames: {total_frames}")

encoded_video_dataset = np.memmap(input_dir / f"video_{rank}.bin", dtype=np.int32, mode="r", shape=(math.ceil(total_frames / 17), 3, 32, 32))

print(f"Encoded video dataset shape: {encoded_video_dataset.shape}")

indices = torch.tensor(encoded_video_dataset, device="cuda") if not isinstance(encoded_video_dataset, torch.Tensor) else encoded_video_dataset

try:
    decoder = CausalVideoTokenizer(checkpoint_dec=str(decoder_path))
    if decoder._dec_model is None:
        raise RuntimeError(f"Failed to load decoder model from {decoder_path}")
    print("Decoder initialized successfully.")
except Exception as e:
    raise RuntimeError(f"Error loading decoder: {str(e)}") from e

batch_size = 1
fps = 30
output_file = output_dir / "reconstructed_video.mp4"

first_batch = torch.from_numpy(encoded_video_dataset[0:1]).cuda()
with torch.no_grad():
    first_output = decoder.decode(first_batch).float()
    _, _, height, width = first_output.shape[-4:]

print(f"Output video dimensions: {width}x{height}")


ec = av.open(str(output_file), mode="w")
es = ec.add_stream("hevc_nvenc", rate=30)
es.width = 256
es.height = 256


num_batches = math.ceil(len(encoded_video_dataset) / batch_size)
for i in range(num_batches):
    start_idx = i * batch_size
    end_idx = min((i + 1) * batch_size, len(encoded_video_dataset))

    batch = torch.from_numpy(encoded_video_dataset[start_idx:end_idx]).cuda()
    with torch.no_grad():
        # [B, 3, 17, 256, 256]
        reconstructed_batch = decoder.decode(batch)

    # (B, 17, 256, 256, 3)
    reconstructed_batch = tensor2numpy(reconstructed_batch)

    # frame: 17, 256, 256, 3
    for this_batch in reconstructed_batch:
        for single_frame in this_batch:  # Temporal dimension
            # 256, 256, 3
            for ep in es.encode(av.VideoFrame.from_ndarray(single_frame, format="rgb24")):
                ec.mux(ep)

    print(f"Processed batch {i + 1}/{num_batches}", flush=True)
    if i == 100:
        break

ec.close()
print(f"Video saved to: {output_file}")
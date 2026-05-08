"""Example script to unpack one shard of the 1xGPT v2.0 video dataset."""

import json
import pathlib
import subprocess

import numpy as np

dir_path = pathlib.Path("val_v2.0")
rank = 0

# load metadata.json
metadata = json.load(open(dir_path / "metadata.json"))
metadata_shard = json.load(open(dir_path / f"metadata_{rank}.json"))

total_frames = metadata_shard["shard_num_frames"]


maps = [
    ("segment_idx", np.int32, []),
    ("states", np.float32, [25]),
]

for m, dtype, shape in maps:
    filename = dir_path / f"{m}_{rank}.bin"
    print("Reading", filename, [total_frames] + shape)
    m_out = np.memmap(filename, dtype=dtype, mode="r", shape=tuple([total_frames] + shape))
    assert m_out.shape[0] == total_frames
    print(m, m_out[:100])


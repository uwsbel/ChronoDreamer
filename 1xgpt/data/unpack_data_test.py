"""Example script to unpack one shard of the 1xGPT Compression Challenge Test dataset."""

import pathlib
import numpy as np

dir_path = pathlib.Path("test_v2.0")
rank = 0

maps = [
    ("videos",        "video",  np.int32,  [3, 32, 32]),
    ("robot_states",  "states", np.float32,[64, 25]),
]

for sub_dir, name, dtype, shape_tail in maps:
    fn = dir_path / sub_dir / f"{name}_{rank}.bin"
    print(f"Reading {fn} shape={shape_tail} dtype={dtype.__name__}")
    arr_size = np.prod(shape_tail)
    arr_bytes = arr_size * np.dtype(dtype).itemsize
    on_disk = fn.stat().st_size if fn.exists() else -1
    if on_disk != arr_bytes:
        print(f"  mismatch => on_disk={on_disk}, need={arr_bytes}")
        if on_disk < 0:
            continue
    arr = np.memmap(fn, dtype=dtype, mode="r", shape=tuple(shape_tail))
    print(f"  shape={arr.shape}, first row:", arr[0])
    print()

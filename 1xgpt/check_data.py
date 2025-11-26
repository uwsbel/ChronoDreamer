import numpy as np
from pathlib import Path

# Check train data
data_dir = Path("data/train_v3.0")
video_path = data_dir / "video.bin"

# Load a sample of the data
data = np.memmap(video_path, dtype=np.uint32, mode="r", shape=(1501, 32, 32))

print("Checking token values...")
print(f"Min value: {data.min()}")
print(f"Max value: {data.max()}")
print(f"Unique values: {len(np.unique(data))}")

# Check for out-of-range values
invalid_mask = data >= 65536
num_invalid = invalid_mask.sum()
print(f"\nTokens >= 65536: {num_invalid} / {data.size} ({100*num_invalid/data.size:.2f}%)")

if num_invalid > 0:
    invalid_values = np.unique(data[invalid_mask])
    print(f"Invalid token values (first 20): {invalid_values[:20]}")

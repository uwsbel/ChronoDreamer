import os
from data import RawTokenDataset

def test_raw_token_dataset():
    data_dir = "/home/jason/Desktop/ChronoDreamer/1xgpt/data/train_v3.0"  # <-- change as needed
    window_size = 16
    stride = 1

    dataset = RawTokenDataset(data_dir, window_size, stride)
    print(f"Dataset length: {len(dataset)}")
    print(f"Shape of memmap data: {dataset.data.shape}")

    print("\nFirst 10 samples:")
    for i in range(min(10, len(dataset))):
        item = dataset[i]
        print(f"Sample {i}:")
        print(f"  input_ids shape: {item['input_ids'].shape}")
        print(f"  First 10 tokens: {item['input_ids'][:10].tolist()}")
        print(f"  attention_mask shape: {item['attention_mask'].shape}")
        print(f"  labels shape: {item['labels'].shape}")

if __name__ == "__main__":
    test_raw_token_dataset()
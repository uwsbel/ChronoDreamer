#!/usr/bin/env python3
"""
Test script for efficient attention implementations
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from genie.config import GenieConfig
from data import RawTokenDataset, get_maskgit_collator

def test_data_loader():
    # --- Setup config ---
    config = GenieConfig(
        num_layers=32, num_heads=8, d_model=256, T=16, S=256,
        image_vocab_size=262144, use_mup=True, num_factored_vocabs=2,
        qkv_bias=False, proj_bias=True, attn_drop=0.0, qk_norm=False,
        mlp_ratio=4.0, mlp_drop=0.0, mlp_bias=True
    )
    # --- Path to your data directory ---
    data_dir = "/home/jason/Desktop/ChronoDreamer/1xgpt/data/train_v3.0"  # <-- change as needed
    window_size = config.T
    stride = 1

    # --- Instantiate dataset ---
    dataset = RawTokenDataset(data_dir, window_size, stride)
    print(f"Dataset length: {len(dataset)}")
    print(f"Shape of memmap data: {dataset.data.shape}")

    # --- Print first 10 lines of video.bin ---
    print("First 10 frames (flattened):")
    for i in range(10):
        item = dataset[i]
        print(f"Sample {i}: input_ids shape={item['input_ids'].shape}, first 10 tokens={item['input_ids'][:10].tolist()}")

    # --- Setup DataLoader and collator ---
    collator = get_maskgit_collator(config)
    dataloader = DataLoader(dataset, batch_size=2, collate_fn=collator)

    # --- Print first batch ---
    print("\nFirst batch from DataLoader:")
    batch = next(iter(dataloader))
    for k, v in batch.items():
        print(f"{k}: shape={v.shape}, dtype={v.dtype}")
        print(f"First 10 values of {k}: {v[0][:10].tolist()}")

if __name__ == "__main__":
    print("Running RawTokenDataset and DataLoader test...\n")
    try:
        test_data_loader()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
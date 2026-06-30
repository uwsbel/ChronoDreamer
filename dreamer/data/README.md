---
license: apache-2.0
pretty_name: 1X World Model Challenge Dataset
size_categories:
- 10M<n<100M
viewer: false
---

# 1X World Model Compression Challenge Dataset

> **Note for ChronoDreamer.** ChronoDreamer trains on the [DreamerBench dataset](https://huggingface.co/datasets/zzhou292/DreamerBench), not the 1X data described below. The loaders in this folder (`cosmos_video_decoder.py`, `unpack_data_*.py`) and the Cosmos-tokenized `.bin` layout are reused from 1X's original challenge, so the format notes still apply, but the robot and joint definitions here are 1X's EVE robot rather than our Robotiq pushing setup.

This repository hosts the dataset for the [1X World Model Compression Challenge](https://huggingface.co/spaces/1x-technologies/1X_World_Model_Challenge_Compression).

```bash
huggingface-cli download 1x-technologies/worldmodel --repo-type dataset --local-dir data
```

## Updates Since v1.1

- **Train/Val v2.0 (~100 hours)**, replacing v1.1
- **Test v2.0 dataset for the Compression Challenge**
- **Faces blurred** for privacy
- **New raw video dataset** (CC-BY-NC-SA 4.0) at [worldmodel_raw_data](https://huggingface.co/datasets/1x-technologies/worldmodel_raw_data)
- **Example scripts** now split into:
  - `cosmos_video_decoder.py` — for decoding Cosmos Tokenized bins
  - `unpack_data_test.py` — for reading the new test set
  - `unpack_data_train_val.py` — for reading the train/val sets

---

## Train & Val v2.0

### Format

Each split is sharded:  
- `video_{shard}.bin` — [NVIDIA Cosmos Tokenizer](https://github.com/NVIDIA/Cosmos-Tokenizer) discrete DV8×8×8 tokens at 30 Hz  
- `segment_idx_{shard}.bin` — segment boundaries  
- `states_{shard}.bin` — `np.float32` states (see below)  
- `metadata.json` / `metadata_{shard}.json` — overall vs. per‐shard metadata


---

## Test v2.0

We provide a 450 sample **test_v2.0** dataset for the [World Model Compression Challenge](https://huggingface.co/spaces/1x-technologies/1X_World_Model_Challenge_Compression) with a similar structure (`video_{shard}.bin`, `states_{shard}.bin`). Use:
- `unpack_data_test.py` to read the test set
- `unpack_data_train_val.py` to read train/val
---

### State Index Definition (New)
```
 0: HIP_YAW
 1: HIP_ROLL
 2: HIP_PITCH
 3: KNEE_PITCH
 4: ANKLE_ROLL
 5: ANKLE_PITCH
 6: LEFT_SHOULDER_PITCH
 7: LEFT_SHOULDER_ROLL
 8: LEFT_SHOULDER_YAW
 9: LEFT_ELBOW_PITCH
10: LEFT_ELBOW_YAW
11: LEFT_WRIST_PITCH
12: LEFT_WRIST_ROLL
13: RIGHT_SHOULDER_PITCH
14: RIGHT_SHOULDER_ROLL
15: RIGHT_SHOULDER_YAW
16: RIGHT_ELBOW_PITCH
17: RIGHT_ELBOW_YAW
18: RIGHT_WRIST_PITCH
19: RIGHT_WRIST_ROLL
20: NECK_PITCH
21: Left hand closure (0= open, 1= closed)
22: Right hand closure (0= open, 1= closed)
23: Linear Velocity
24: Angular Velocity
```

## Previous v1.1

- `video.bin` — 16×16 patches at 30Hz, quantized
- `segment_ids.bin` — segment boundaries
- `actions/` folder storing multiple `.bin`s for states, closures, etc.

### v1.1 Joint Index
  ```
   {
        0: HIP_YAW
        1: HIP_ROLL
        2: HIP_PITCH
        3: KNEE_PITCH
        4: ANKLE_ROLL
        5: ANKLE_PITCH
        6: LEFT_SHOULDER_PITCH
        7: LEFT_SHOULDER_ROLL
        8: LEFT_SHOULDER_YAW
        9: LEFT_ELBOW_PITCH
        10: LEFT_ELBOW_YAW
        11: LEFT_WRIST_PITCH
        12: LEFT_WRIST_ROLL
        13: RIGHT_SHOULDER_PITCH
        14: RIGHT_SHOULDER_ROLL
        15: RIGHT_SHOULDER_YAW
        16: RIGHT_ELBOW_PITCH
        17: RIGHT_ELBOW_YAW
        18: RIGHT_WRIST_PITCH
        19: RIGHT_WRIST_ROLL
        20: NECK_PITCH
    }
  
A separate `val_v1.1` set is available.

---

## Provided Checkpoints

- `magvit2.ckpt` from [MAGVIT2](https://github.com/TencentARC/Open-MAGVIT2) used in v1.1
- For v2.0, see [NVIDIA Cosmos Tokenizer](https://github.com/NVIDIA/Cosmos-Tokenizer); we supply `cosmos_video_decoder.py`.

---

## Directory Structure Example

```
train_v1.1/
val_v1.1/
train_v2.0/
val_v2.0/
test_v2.0/
  ├── video_{shard}.bin
  ├── states_{shard}.bin
  ├── ...
  ├── metadata_{shard}.json
cosmos_video_decoder.py
unpack_data_test.py
unpack_data_train_val.py
```

**License**: [Apache-2.0](./LICENSE)  
**Author**: 1X Technologies  
```
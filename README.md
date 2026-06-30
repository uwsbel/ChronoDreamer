# ChronoDreamer

ChronoDreamer is the code for our work on action-conditioned world models for contact-rich robotic manipulation. The model watches a short clip from the robot's cameras, and given the actions the arm is about to take, it predicts what comes next: the future video frames, a contact map, and the arm's joint angles. Everything is trained on pushing and striking trajectories simulated in [Project Chrono](https://projectchrono.org/) and released as the [DreamerBench dataset](https://huggingface.co/datasets/zzhou292/DreamerBench).

<img width="4800" height="2400" alt="ChronoDreamer training visualization" src="https://github.com/user-attachments/assets/16793f01-b350-4074-967b-7b4845f6de27" />

![A predicted rollout](https://github.com/user-attachments/assets/395be1c5-6c9f-4f3a-b93c-3a5548606722)

## What's in here

The repo follows the three stages of the project, so each top-level folder is one stage:

- **`PyChronobotics-main/`** — the Chrono simulation that generates the data. A Robotiq gripper is driven around a tabletop with Ornstein–Uhlenbeck joystick noise so that it keeps running into things, and we log RGB from a few cameras, joint angles, the action commands, and the per-contact forces. The relevant scripts are in `experiment/`, mainly `jz_robotiq_push_contact*.py` (and `jz_robotiq_push_ou.py` for the OU excitation).
- **`dreamer/`** — the world model itself. A spatial-temporal transformer trained with a MaskGIT-style masked-token objective on Cosmos image tokens. Training, sampling, visualization, and running the model on a simulated episode all live here.
- **`human-label/`** — the VLM-AUC evaluation. `label_collisions.py` is the small UI we used to mark whether a clip actually contains a collision, and `vlm_evaluate.py` runs vision-language judges and scores them against those labels.

`dreamer/cosmos/` and `dreamer/magvit2/` are vendored tokenizers (NVIDIA Cosmos and Open-MAGVIT2). You don't normally need to touch them.

## Setup

You need Python 3.10 (tested on 3.10.12) and a CUDA GPU. From `dreamer/`:

```sh
cd dreamer
./build.sh
source venv/bin/activate
```

`build.sh` makes a virtualenv, installs `requirements.txt`, and builds flash-attn. On newer (sm_120) cards use `build-sm120.sh` with `requirements-sm120.txt` instead. Image tokenization runs through the Cosmos tokenizer in `dreamer/cosmos/`, whose weights download on first use.

## How to run it

The stages run in order, but if you just want to train, grab DreamerBench and skip straight to step 2.

**1. Generate data (optional).** From `PyChronobotics-main/experiment/`:

```sh
python3 jz_robotiq_push_contact.py --output-dir test_run
```

`run_sample.sh` just loops that and compresses the rendered frames to JPEG.

**2. Train the world model.** From `dreamer/`:

```sh
python train.py --genie_config genie/configs/magvit_n32_h8_d256.json \
    --output_dir data/genie_model
```

Configs are in `genie/configs/`; `python train.py --help` lists the rest of the knobs.

**3. Predict and visualize a rollout** (camera plus contact):

```sh
python genie/generate.py --checkpoint_dir data/genie_model/<ckpt> \
    --val_data_dir data/generate_test --example_ind 100 --generate_contact
python visualize.py --token_dir data/genie_generated --visualize_contact
```

`sample.sh` batches those two over a range of clips. To run the model on one specific simulated episode (frames, actions, and joint angles already on disk), use `inference_from_sim.py`.

**4. Evaluate with VLM-AUC.** From `human-label/`, label a few clips and then score a judge against them:

```sh
python label_collisions.py
python vlm_evaluate.py --backend nvidia --api_key $NVIDIA_API_KEY --data_dir output_pilot
```

The judges are open-weight VLMs (we used Llama 3.2 90B, Gemma 3 27B, and Qwen3.5 122B). The `prompts*.py` files hold the prompt variants we average over.

## Data

DreamerBench is on the Hub: <https://huggingface.co/datasets/zzhou292/DreamerBench>. It contains the raw RGB, contact-splat, proprioception, action, and physics arrays for each scenario, plus precomputed Cosmos DI8×8 tokens so you can train in token space without re-encoding. It's large, so pull the scenario you need rather than the whole thing.

## Acknowledgements

The transformer and MaskGIT sampler in `dreamer/` started from 1X Technologies' GENIE baseline ([1xgpt](https://github.com/1x-technologies/1xgpt)) — thanks to them for releasing it. Tokenization uses NVIDIA's [Cosmos Tokenizer](https://github.com/NVIDIA/Cosmos-Tokenizer), and the older MAGVIT2 path comes from [Open-MAGVIT2](https://github.com/TencentARC/Open-MAGVIT2).

## Citing

If this code or DreamerBench is useful in your research, please cite the ChronoDreamer paper (Zhou and Negrut) and the DreamerBench dataset.

## License

The code is Apache-2.0 (see `dreamer/LICENSE`). The Cosmos tokenizer weights are covered by the [NVIDIA Open Model License](https://developer.download.nvidia.com/licenses/nvidia-open-model-license-agreement-june-2024.pdf).

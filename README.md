A world model training framework upon Chrono
# ChronoDreamer World Model & Robotics Framework

This repository provides a comprehensive framework for world model training, video tokenization, and robotics simulation, integrating state-of-the-art generative models and physical simulation environments.
<img width="4800" height="2400" alt="media_images_vis_train_0_217000_206c6109eb0c8f29c237" src="https://github.com/user-attachments/assets/16793f01-b350-4074-967b-7b4845f6de27" />

![generated_offset0(1)](https://github.com/user-attachments/assets/395be1c5-6c9f-4f3a-b93c-3a5548606722)


## Repository Structure

- **1xgpt/**  
  Implementation of GENIE (spatio-temporal transformer and MaskGIT sampler), world model compression challenge scripts, and utilities.
  - `train.py`, `visualize.py`, `test_attention.py`: Model training, visualization, and testing.
  - `data/`: Dataset scripts and documentation.
  - `genie/`: GENIE model code.
  - `magvit2/`: MAGVIT2 encoder/decoder utilities.

- **test-scripts/vid-model/**  
  Video model scripts, Cosmos-Tokenizer integration, and pre-trained checkpoints.
  - `Cosmos-Tokenizer/`: NVIDIA Cosmos Tokenizer code and documentation.
  - `pretrained_ckpts/`: Pre-trained Cosmos Tokenizer models.
  - `1xgpt_cosmos_vid_endecoder.ipynb`: Example notebook for video encoding/decoding.

- **PyChronobotics-main/**  
  Robotics simulation and control using PyChrono.
  - `experiment/`: Example scripts for robot control and simulation.
  - `models/`: Robot models (e.g., Jackal, robot arm).
  - `data/`: 3D assets and robot assembly files.
  - `util/`: Utilities for kinematics and asset import.

## Getting Started

### Requirements

- Python 3.10+
- [PyTorch](https://pytorch.org/)
- [PyChrono](https://projectchrono.org/)
- [ffmpeg](https://ffmpeg.org/) (for video processing)
- Additional dependencies listed in `requirements.txt` files.

### Installation

1. **Install dependencies and download data:**
    ```sh
    cd 1xgpt
    ./build.sh
    source venv/bin/activate
    ```

2. **Install Cosmos-Tokenizer (Linux recommended):**
    ```sh
    git clone https://github.com/NVIDIA/Cosmos-Tokenizer.git
    cd Cosmos-Tokenizer
    pip3 install -r requirements.txt
    apt-get install -y ffmpeg
    ```

3. **(Optional) Build Docker image for Cosmos-Tokenizer:**
    ```sh
    docker build -t cosmos-tokenizer -f Dockerfile .
    docker run --gpus all -it --rm -v /home/${USER}:/home/${USER} \
        --workdir ${PWD} cosmos-tokenizer /bin/bash
    ```

## Usage

### Train GENIE Model

```sh
python train.py --genie_config genie/configs/magvit_n32_h8_d256.json --output_dir data/genie_model --max_eval_steps 10
```

### Generate and Visualize

```sh
python genie/generate.py --checkpoint_dir data/genie_model/final_checkpt
python visualize.py --token_dir data/genie_generated
```

### Evaluate

```sh
python genie/evaluate.py --checkpoint_dir data/genie_model/final_checkpt
```

### Video Tokenization (Cosmos-Tokenizer)

See [test-scripts/vid-model/Cosmos-Tokenizer/README.md](test-scripts/vid-model/Cosmos-Tokenizer/README.md) for details and API usage.

## Dataset

- **1X World Model Compression Challenge Dataset**  
  See [1xgpt/data/README.md](1xgpt/data/README.md) for dataset details, structure, and usage scripts.

## Citation

If you use this repository, please cite the relevant papers and repositories as described in [1xgpt/README.md](1xgpt/README.md) and [test-scripts/vid-model/Cosmos-Tokenizer/README.md](test-scripts/vid-model/Cosmos-Tokenizer/README.md).

## License

- Code: [Apache 2.0](1xgpt/LICENSE)
- Cosmos-Tokenizer Models: [NVIDIA Open Model License](https://developer.download.nvidia.com/licenses/nvidia-open-model-license-agreement-june-2024.pdf)

---

For more details, see individual module READMEs and documentation.

---
license: other
license_name: nvidia-open-model-license
license_link: >-
  https://developer.download.nvidia.com/licenses/nvidia-open-model-license-agreement-june-2024.pdf
library_name: nemo
---
# **Cosmos Tokenizer**: A suite of image and video tokenizers

[**Website**](https://research.nvidia.com/labs/dir/cosmos-tokenizer) | [**Code**](https://github.com/NVIDIA/Cosmos-Tokenizer) | [**Video**](https://youtu.be/Soy_myOfWIU)


# Model Overview

## Description:
**Cosmos Tokenizer** is a suite of visual tokenizers for images and videos that delivers various compression rates while maintaining high reconstruction quality. Cosmos Tokenizer can serve as an effective and efficient building block in both diffusion-based and autoregressive models for image and video generation.


Our tokenizers come in two types: **Continuous** (C) and **Discrete** (D), each with **Image** (I) and **Video** (V) variants:
* Continuous tokenizers encode visual data into continuous latent embeddings, as shown in latent diffusion models like [Stable Diffusion](https://github.com/CompVis/stable-diffusion). These embeddings are suitable for models that generate data by sampling from continuous distributions. 
* Discrete tokenizers encode visual data into discrete latent codes, mapping them into quantized indices, as seen in autoregressive transformers such as [VideoPoet](https://sites.research.google/videopoet/). This discretization is required for models that generate data by optimizing the cross-entropy loss, such as the GPT models.


|                   | Continuous ( C )    | Discrete ( D )      |
| ------------------|---------------------|---------------------|
| **Images ( I )**        | Cosmos-Tokenizer-CI            | Cosmos-Tokenizer-DI            |
| **Videos ( V )**        | Cosmos-Tokenizer-CV            | Cosmos-Tokenizer-DV            |


Given an image or a video, Cosmos Tokenizer outputs either continuous latents or discrete tokens. Cosmos Tokenizer achieves spatial compression rates of 8x8 or 16x16 and temporal compression factors of 4x or 8x, resulting in a total compression factor of up to 2048x (=8x16x16). Cosmos Tokenizer delivers 8x more total compression than state-of-the-art (SOTA) methods while simultaneously maintaining higher image quality and running up to 12x faster than the best available SOTA tokenizers.

**Model Developer**: NVIDIA

## Model Versions

The initial release (v1.0) of Cosmos Tokenizer includes the following tokenizers:
* **Continuous Tokenizers**
    * Continuous Image (CI) Tokenizer
        * [Cosmos-Tokenizer-CI8x8](https://huggingface.co/nvidia/Cosmos-Tokenizer-CI8x8) (8x8 spatial compression)
        * [Cosmos-Tokenizer-CI16x16](https://huggingface.co/nvidia/Cosmos-Tokenizer-CI16x16) (16x16 spatial compression)
    * Continuous Video (CV) Tokenizer
        * [Cosmos-Tokenizer-CV4x8x8](https://huggingface.co/nvidia/Cosmos-Tokenizer-CV4x8x8) (4x temporal compression, 8x8 spatial compression)
        * [Cosmos-Tokenizer-CV8x8x8](https://huggingface.co/nvidia/Cosmos-Tokenizer-CV8x8x8) (8x temporal compression, 8x8 spatial compression)
        * [Cosmos-Tokenizer-CV8x16x16](https://huggingface.co/nvidia/Cosmos-Tokenizer-CV8x16x16) (8x temporal compression, 16x16 spatial compression)
* **Discrete Tokenizers**
    * Discrete Image (DI) Tokenizer
        * [Cosmos-Tokenizer-DI8x8](https://huggingface.co/nvidia/Cosmos-Tokenizer-DI8x8) (8x8 spatial compression)
        * [Cosmos-Tokenizer-DI16x16](https://huggingface.co/nvidia/Cosmos-Tokenizer-DI16x16) (16x16 spatial compression)
    * Discrete Video (DV) Tokenizer
        * [Cosmos-Tokenizer-DV4x8x8](https://huggingface.co/nvidia/Cosmos-Tokenizer-DV4x8x8) (4x temporal compression, 8x8 spatial compression)
        * [Cosmos-Tokenizer-DV8x8x8](https://huggingface.co/nvidia/Cosmos-Tokenizer-DV8x8x8) (8x temporal compression, 8x8 spatial compression)
        * [Cosmos-Tokenizer-DV8x16x16](https://huggingface.co/nvidia/Cosmos-Tokenizer-DV8x16x16) (8x temporal compression, 16x16 spatial compression)


### License/Terms of Use: 
[NVIDIA Open Model License](https://developer.download.nvidia.com/licenses/nvidia-open-model-license-agreement-june-2024.pdf)

Under the NVIDIA Open Model License, NVIDIA confirms:

* Models are commercially usable.
* You are free to create and distribute Derivative Models.
* NVIDIA does not claim ownership to any outputs generated using the Models or Derivative Models.

## Model Architecture: 

We designed Cosmos Tokenizer using a lightweight and computationally efficient architecture, featuring a temporally causal design. Specifically, we employ causal temporal convolution and causal temporal attention layers to preserve the natural temporal order of video frames, ensuring seamless tokenization of images and videos using a single unified network architecture. The encoder and decoder form a symmetrical pair, which are mirrors of each other. The encoder starts with a 2-level [Haar wavelet](https://link.springer.com/book/10.1007/978-3-319-04295-4) transform layer, which down-samples inputs by a factor of 4 in both spatial and temporal dimensions. Likewise, the decoder ends with an inverse wavelet transform. We employ the vanilla autoencoder (AE) formulation to model the latent space for continuous tokenizers. For discrete tokenizers, we adopt the [Finite-Scalar-Quantization](https://openreview.net/forum?id=8ishA3LxN8) (FSQ) as the latent space quantizer.

![image/jpeg](https://cdn-uploads.huggingface.co/production/uploads/638fb8cf2380ffd99caf8c2a/gQH5n9iCEtqZc7uutUwdL.jpeg)



## Input/Output Specifications

### Encoder
* **Input**
    * **Types:** Images or Videos
    * **Format:** RGB (Red, Green, Blue)
    * **Resolution:** 
        * Minimum: 256px (shorter side)
        * Maximum: Up to 4K
    * **Video Length:** Up to 8 seconds for 1080p videos (bounded by A100 80G GPU memory; higher resolutions will have shorter supported durations)

* **Output**
    * **Types:** Tokens
        * Continuous Image/Video Tokenizers: Continuous value feature vectors
        * Discrete Image/Video Tokenizers: Integer indices

### Decoder
* **Input**
    * **Types:** Tokens from encoder

* **Output**
    * **Types:** Images or Videos (matching input type)
    * **Format:** RGB (Red, Green, Blue)
    * **Resolution:** Same as input resolution
    * **Video Length:** Same as input video length

## Software Integration (Required For NVIDIA Models Only):
**Runtime Engine(s):** 
* [Cosmos-Tokenizer](https://github.com/NVIDIA/Cosmos-Tokenizer)
* [NeMo](https://github.com/NVIDIA/NeMo) (please install the latest version from the GitHub main branch)

**Supported Hardware Microarchitecture Compatibility:**
* NVIDIA Ampere (e.g., A100)
* NVIDIA Hopper (e.g., H100)

Note: We have only tested Cosmos Tokenizer with BF16 precision on Ampere and Hopper GPUs. If you are using older versions of NVIDIA GPUs (e.g., NVIDIA Volta GPUs), you may need to switch to FP32 precision.


**Operating System(s):**
* Linux (We have not tested on other operating systems.)

# Usage
Inference Engines: 
* [Cosmos-Tokenizer](https://github.com/NVIDIA/Cosmos-Tokenizer) (PyTorch)
* [NeMo](https://github.com/NVIDIA/NeMo)

## Inference with `Cosmos-Tokenizer` (PyTorch)
### Step-1: Installation of `Cosmos-Tokenizer` 
Note: Currently, the `Cosmos-Tokenizer` code is only supported on Linux.

- Please clone the `Cosmos-Tokenizer` from GitHub repo [github.com/NVIDIA/Cosmos-Tokenizer](https://github.com/NVIDIA/Cosmos-Tokenizer).

    ```bash
    git clone https://github.com/NVIDIA/Cosmos-Tokenizer.git
    cd Cosmos-Tokenizer
    ```
- Install dependencies

    ```bash
    pip3 install -r requirements.txt
    apt-get install -y ffmpeg
    ```

- Preferably, you could build a docker image using our provided Dockerfile.
    ```bash
    docker build -t cosmos-docker -f Dockerfile.    
    # You can run the container as:
    docker run --gpus all -it --rm -v /home/${USER}:/home/${USER} \
        --workdir ${PWD} cosmos-docker /bin/bash
    ```

### Step-2: Download Pre-trained Checkpoints
- Create a local directory for the pre-trained checkpoints and download the 
pre-trained checkpoints from HuggingFace.

    ```python
    from huggingface_hub import login, snapshot_download
    import os
    # You could get your Hugging Face token from https://huggingface.co/settings/tokens
    login(token=<YOUT-HF-TOKEN>, add_to_git_credential=True)
    # You could specify the tokenizers you want to download.
    model_names = [
            "Cosmos-Tokenizer-CI8x8",
            "Cosmos-Tokenizer-CI16x16",
            "Cosmos-Tokenizer-CV4x8x8",
            "Cosmos-Tokenizer-CV8x8x8",
            "Cosmos-Tokenizer-CV8x16x16",
            "Cosmos-Tokenizer-DI8x8",
            "Cosmos-Tokenizer-DI16x16",
            "Cosmos-Tokenizer-DV4x8x8",
            "Cosmos-Tokenizer-DV8x8x8",
            "Cosmos-Tokenizer-DV8x16x16",
    ]
    for model_name in model_names:
        hf_repo = "nvidia/" + model_name
        local_dir = "pretrained_ckpts/" + model_name
        os.makedirs(local_dir, exist_ok=True)
        print(f"downloading {model_name} to {local_dir}...")
        snapshot_download(repo_id=hf_repo, local_dir=local_dir)
    ```

- Under the ech checkpoint directory `pretrained_ckpts/<model-name>`, we provide the encoder, 
decoder and the full autoencoder JIT models.

    ```bash 
    ├── pretrained_ckpts/   
    │   ├── Cosmos-Tokenizer-DV8x8x8/
    │   │   ├── encoder.jit
    │   │   ├── decoder.jit
    │   │   ├── autoencoder.jit
    │   ...
    ```

### Step-3: Run Inference
You can use the following example commands to encode and decode images or videos. For each, the same command works for both continuous and discrete tokenization. Simply provide the proper JIT-compiled ckpt to `checkpoint_enc`, `checkpoint_dec`, or the full autoencoder ckpt to `checkpoint`.

```python
import torch
from cosmos_tokenizer.video_lib import CausalVideoTokenizer

model_name = "Cosmos-Tokenizer-CV4x8x8"
input_tensor = torch.randn(1, 3, 9, 512, 512).to('cuda').to(torch.bfloat16)  # [B, C, T, H, W]
encoder = CausalVideoTokenizer(checkpoint_enc=f'pretrained_ckpts/{model_name}/encoder.jit')
(latent,) = encoder.encode(input_tensor)
torch.testing.assert_close(latent.shape, (1, 16, 3, 64, 64))

# The input tensor can be reconstructed by the decoder as:
decoder = CausalVideoTokenizer(checkpoint_dec=f'pretrained_ckpts/{model_name}/decoder.jit')
reconstructed_tensor = decoder.decode(latent)
torch.testing.assert_close(reconstructed_tensor.shape, input_tensor.shape)
```

The latent will have the shape `(1, 16, 3, 64, 64)`, where the first of the three latents represents the first frame, and `C=16` is the number of channels of the latent.

**Note**: More inference usage commands, including both TorchScript (JIT) and PyTorch Inference APIs on real images and videos, can be found on our GitHub repository [github.com/NVIDIA/Cosmos-Tokenizer](https://github.com/NVIDIA/Cosmos-Tokenizer).


## Inference with NeMo

### Step-1: Install NeMo
Please install NeMo from the GitHub `main` branch following the instructions [here](https://github.com/NVIDIA/NeMo?tab=readme-ov-file#pip-from-a-source-branch).

### Step-2: Run Inference
Run the following code to tokenize the video:

```python
import torch
from nemo.collections.common.video_tokenizers.cosmos_vision_tokenizer import CausalVideoTokenizer
model_name = "Cosmos-Tokenizer-CV4x8x8"
model = CausalVideoTokenizer.from_pretrained(model_name)
input_tensor = torch.randn(1, 3, 9, 512, 512).to('cuda').to(torch.bfloat16)
(latent, ) = model.encode(input_tensor)
```
Please see the [Cosmos Tokenizer README within the NeMo repository](https://github.com/NVIDIA/NeMo/tree/main/nemo/collections/common/video_tokenizers) for additional examples to create training datasets with the Cosmos Tokenizer.


# Evaluation

## TokenizationPerformance Comparison
We have extensively evaluated the **Cosmos Tokenizer** suite on various image and video benchmark datasets. In addition to commonly used datasets such as [MS-COCO](https://cocodataset.org/#home) and [DAVIS](https://davischallenge.org/), in order to cover a wide variety of visual data and standardize the evaluation, we created a benchmark called [TokenBench](https://github.com/NVlabs/Token-Bench), which is a mixed sampling of video data from diverse domains.

| Tokenizer      | Compression Ratio | Formulation | PSNR (DAVIS) | SSIM (DAVIS) | rFVD (DAVIS) | PSNR (TokenBench) | SSIM (TokenBench) | rFVD (TokenBench) |
|----------------|-------------------|-------------|--------------|--------------|--------------|--------------------|--------------------|--------------------|
| CogVideoX      | 4×8×8             | VAE         | 31.74        | 0.860        | 19.58        | 33.14             | 0.908             | 6.97              |
| Omnitokenizer  | 4×8×8             | VAE         | 29.04        | 0.710        | 117.66       | 29.70             | 0.830             | 35.86             |
| Cosmos-Tokenizer-CV      | 4×8×8             | AE          | **35.28**    | **0.890**    | **15.93**    | **37.27**         | **0.928**         | **6.849**         |
| Cosmos-Tokenizer-CV      | 8×8×8             | AE          | 34.10        | 0.850        | 30.16        | 36.85             | 0.917             | 11.62             |
| Cosmos-Tokenizer-CV      | 8×16×16           | AE          | 32.55        | 0.770        | 93.82        | 35.15             | 0.875             | 43.08             |


* We compare with the state-of-the-art continuous video tokenizers, [CogVideoX](https://github.com/THUDM/CogVideo) and [OmniTokenizer](https://github.com/FoundationVision/OmniTokenizer).
* Evaluation metrics:
    * Peak Signal-to-Noise Ratio (PSNR)
    * Structural Similarity (SSIM)
    * Reconstruction Fréchet Video Distance (rFVD)

## Runtime Comparison

The following table shows the number of parameters and the averaged encoding and decoding times per image or video frame, measured on a single A100 80GB GPU. For comparison, we also list the parameters and average speeds of prior state-of-the-art tokenizer(s) with the same compression ratio.

| Tokenizer      | Resolution | Compression Ratio | Parameters | Time (ms) |
|----------------|------------|-------------------|------------|-----------|
| CogVideoX      | 720x1280   | 4×8×8            | 216M       | 414       |
| OmniTokenizer  | 720x1280   | 4×8×8            | 54M        | 82.9      |
| Cosmos-Tokenizer-CV      | 720x1280   | 4×8×8            | 105M       | **34.8**  |


Note: We benchmarked the runtime for images under the 8x8 compression and videos under the 4×8×8 compression. Tokenizers with different compression ratios are not included in this comparison.

## Ethical Considerations
NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications.  When downloaded or used in accordance with our terms of service, developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse.  

For more detailed information on ethical considerations for this model, please see the subcards of Explainability, Bias, Safety & Security, and Privacy below. Please report security vulnerabilities or NVIDIA AI Concerns [here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/).

### Bias

Field                                                                                               |  Response
:---------------------------------------------------------------------------------------------------|:---------------
Participation considerations from adversely impacted groups [protected classes](https://www.senate.ca.gov/content/protected-classes) in model design and testing:  |  None
Measures taken to mitigate against unwanted bias:                                                   |  None
 

### Explainability

Field                                                                                                  |  Response
:------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------
Intended Application & Domain:                                                                   |  Tokenization of images and videos
Model Type:                                                                                            |  Auto-Encoder
Intended Users:                                                                                        |  Generative AI developers for image and video generation models
Output:                                                                                                |  Images/Videos and Latent Tokens 
Describe how the model works:                                                                          |  Compresses and decompresses visual input (image/video).
Technical Limitations:                                                                                 |  Due to tokenizer compression limitations, some visual information (such as small text and other structured fine details) may not be reconstructed accurately.
Verified to have met prescribed NVIDIA quality standards:  |  Yes
Performance Metrics:                                                                                   |  Peak Signal-to-Noise Ratio (PSNR), Structural Similarity (SSIM), Reconstruction Fréchet Video Distance (rFVD), Reconstruction Fréchet Inception Distance (rFID), Latency
Potential Known Risks:                                                                                 |  Tokenizer's output can parse all forms of input, including what may be considered toxic, offensive, or indecent. 
Licensing:                                                                                             |  [NVIDIA Open Model License](https://developer.download.nvidia.com/licenses/nvidia-open-model-license-agreement-june-2024.pdf)


### Privacy
Field                                                                                                                              |  Response
:----------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------
Generatable or reverse engineerable personal information?                                                     |  No
Protected class data used to create this model?                                                                                       |  None Known
Was consent obtained for any personal data used?                                                                                             |  None Known
How often is dataset reviewed?                                                                                                     |  Before Release
Is a mechanism in place to honor data subject right of access or deletion of personal data?                                        |  Not Applicable
If personal collected for the development of the model, was it collected directly by NVIDIA?                                            |  Not Applicable
If personal collected for the development of the model by NVIDIA, do you maintain or have access to disclosures made to data subjects?  |  Not Applicable
If personal collected for the development of this AI model, was it minimized to only what was required?                                 |  Not Applicable
Is there provenance for all datasets used in training?                                                                                |  Yes
Does data labeling (annotation, metadata) comply with privacy laws?                                                                |  Yes
Is data compliant with data subject requests for data correction or removal, if such a request was made?                           |  Not Applicable

### Safety

Field                                               |  Response
:---------------------------------------------------|:----------------------------------
Model Application(s):                               |  Tokenization of images and videos 
Describe the life critical impact (if present).   |  None Known
Use Case Restrictions:                              |  See [NVIDIA Open Model License](https://developer.download.nvidia.com/licenses/nvidia-open-model-license-agreement-june-2024.pdf)
Model and dataset restrictions:            |  The Principle of least privilege (PoLP) is applied limiting access for dataset generation and model development.  Restrictions enforce dataset access during training, and dataset license constraints adhered to. Model checkpoints are made available on Hugging Face, and may become available on cloud providers' model catalog.


### Plus Plus (++) Promise

We value you, the datasets, the diversity they represent, and what we have been entrusted with. This model and its associated data have been:
* Verified to comply with current applicable disclosure laws, regulations, and industry standards.
* Verified to comply with applicable privacy labeling requirements.
* Annotated to describe the collector/source (NVIDIA or a third-party).
* Characterized for technical limitations.
* Reviewed to ensure proper disclosure is accessible to, maintained for, and in compliance with NVIDIA data subjects and their requests.
* Reviewed before release.
* Tagged for known restrictions and potential safety implications.


# Core Contributors
Fitsum Reda, Jinwei Gu, Xian Liu, Songwei Ge, Ting-Chun Wang, Haoxiang Wang, Ming-Yu Liu
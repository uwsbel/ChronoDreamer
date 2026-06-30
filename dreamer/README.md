# dreamer

This is the world-model training code for ChronoDreamer. It's a spatial-temporal transformer trained with a MaskGIT-style masked-token objective on discrete image tokens from the Cosmos tokenizer. Given a few context frames together with the actions and joint angles, it predicts the next frames, a contact map, and the future joint angles.

The transformer and MaskGIT sampler come from 1X's GENIE implementation ([Genie paper](https://arxiv.org/abs/2402.15391), [1xgpt](https://github.com/1x-technologies/1xgpt)). On top of that base we added the contact-splat output channel, the action and joint-angle conditioning, a joint-angle regression head, and the path that runs the model directly on simulated episodes.

## Setup

Python 3.10+ (tested on 3.10.12):

```sh
./build.sh
source venv/bin/activate
```

On sm_120 GPUs use `build-sm120.sh` and `requirements-sm120.txt`.

## Train

```sh
python train.py --genie_config genie/configs/magvit_n32_h8_d256.json \
    --output_dir data/genie_model
```

Model configs live in `genie/configs/`. `python train.py --help` lists the full set of flags (sequence length, batch size, learning-rate schedule, and so on).

## Generate, visualize, evaluate

```sh
# Predict a rollout (RGB + contact) from a validation clip
python genie/generate.py --checkpoint_dir data/genie_model/<ckpt> \
    --val_data_dir data/generate_test --example_ind 100 --generate_contact

# Render the predicted tokens to GIFs
python visualize.py --token_dir data/genie_generated --visualize_contact

# Score a checkpoint
python genie/evaluate.py --checkpoint_dir data/genie_model/<ckpt>
```

`sample.sh` loops generate + visualize over a range of clips. To run on one specific simulated episode (frames, actions, and joint angles already on disk), use `inference_from_sim.py`.

## A note on the token loss

Image tokens have a large vocabulary, so rather than one softmax over the entire codebook, each token is split into two sub-tokens and the cross-entropy is summed over the two. This keeps the logit tensor small enough to be practical, and it's the same factorization GENIE uses. Contact tokens are predicted the same way; joint angles are handled by a separate MSE regression head.

## Credit

The transformer/MaskGIT core is from 1X's GENIE baseline ([1xgpt](https://github.com/1x-technologies/1xgpt)). The tokenizers in `cosmos/` and `magvit2/` are NVIDIA Cosmos and Open-MAGVIT2.

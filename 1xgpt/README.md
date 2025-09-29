Progress in video generation may soon make it possible to evaluate robot policies in a completely learned world model. An end-to-end learned simulator of millions of robot environments would greatly accelerate progress in general-purpose robotics and provide a useful signal for scaling data and compute.


## Getting Started
We require `Python 3.10` or later. This code was tested with `Python 3.10.12`.

```
# Install dependencies and download data
./build.sh 

# Source the Python environment
source venv/bin/activate
```

## GENIE

This repo provides an implementation of the spatio-temporal transformer and MaskGIT sampler as described in [Genie: Generative Interactive Environments](https://arxiv.org/abs/2402.15391). Note that this implementation only trains on video sequences, not actions (though it is trivial to add this via an additive embedding).

```
# Train the GENIE model
python train.py --genie_config genie/configs/magvit_n32_h8_d256.json --output_dir data/genie_model --max_eval_steps 10

# Generate frames from trained model
python genie/generate.py --checkpoint_dir data/genie_model/final_checkpt

# Visualize generated frames
python visualize.py --token_dir data/genie_generated

# Evaluate the trained model
python genie/evaluate.py --checkpoint_dir data/genie_model/final_checkpt
```

### 1X GENIE Baseline
We provide two pre-trained GENIE models, linked in the [leaderboard](#leaderboard).
```
# Generate and visualize
output_dir='data/genie_baseline_generated'
for i in {0..240..10}; do
    python genie/generate.py --checkpoint_dir 1x-technologies/GENIE_138M \
        --output_dir $output_dir --example_ind $i --maskgit_steps 2 --temperature 0
    python visualize.py --token_dir $output_dir
    mv $output_dir/generated_offset0.gif $output_dir/example_$i.gif
    mv $output_dir/generated_comic_offset0.png $output_dir/example_$i.png
done

# Evaluate
python genie/evaluate.py --checkpoint_dir 1x-technologies/GENIE_138M --maskgit_steps 2
```
 

## Additional Challenge Details

1. We've provided `magvit2.ckpt` in the dataset download, which are the weights for a [MAGVIT2](https://github.com/TencentARC/Open-MAGVIT2) encoder/decoder. The encoder allows you to tokenize external data to try to improve the metric.
2. The loss metric is nonstandard compared to LLMs due to the vocabulary size of the image tokens, which was changed as of v1.0 release (Jul 8, 2024). Instead of computing cross entropy loss on logits with 2^18 classes, we compute cross entropy losses on 2x 2^9 class predictions and sum them up. The rationale for this is that the large vocabulary size (2^18) makes it very memory-intensive to store a logit tensor of size `(B, 2^18, T, 16, 16)`. Therefore, the compression challenge considers families of models with a factorized pmfs of the form p(x1, x2) = p(x1)p(x2). For sampling and evaluation challenge, a factorized pmf is a necessary criteria.
3. For the compression challenge, we are making the deliberate choice to evaluate held-out data on the same factorized distribution p(x1, x2) = p(x1)p(x2) that we train on. Although unfactorized models of the form p(x1, x2) = f(x1, x2) ought to achieve lower cross entropy on test data by exploiting the off-block-diagonal terms of Cov(x1, x2), we want to encourage solutions that achieve lower losses while holding the factorization fixed.
5. Naive nearest-neighbor retrieval + seeking ahead to next frames from the training set will achieve reasonably good losses and sampling results on the dev-validation set, because there are similar sequences in the training set. However, we explicitly forbid these kinds of solutions (and the private test set penalizes these kinds of solutions).


### Metric Details
There are different scenarios for evaluation, which vary in the degree of ground truth context the model receives.
In decreasing order of context, these scenarios are:
- **Fully Autoregressive**: the model receives a predetermined number of ground truth frames and autoregressively predicts all remaining frames.
- **Temporally Teacher-forced**: the model receives all ground truth frames before the current frame and autoregressively predicts all tokens in the current frame.
- **Fully Teacher-forced**: the model receives all ground truth tokens before the current token, 
including tokens in the current frame. Only applicable for causal LMs.

As an example, consider predicting the final token of a video, corresponding to the lower right patch of frame 15. 
The context the model receives in each scenario is:
- Fully Autoregressive: the first $t$x16x16 tokens are ground truth tokens corresponding to the first $t$ prompt frames, 
and all remaining tokens are autoregressively generated, where $0 < t < 15$ is the predetermined number of prompt frames.
- Temporally Teacher-forced: the first 15x16x16 tokens are ground truth tokens corresponding to the first 15 frames, 
and all remaining tokens are autoregressively generated.
- Fully Teacher-forced: all previous (16x16x16 - 1) tokens are ground truth tokens.

## Citation
If you use this software or dataset in your work, please cite it using the "Cite this repository" button on Github.

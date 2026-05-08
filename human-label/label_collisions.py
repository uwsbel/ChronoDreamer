"""
Human labeling interface for collision detection in validation data.

For each validation sample, the human sees:
  - GT comic strip (video + contact frames at stride=15)
  - Stride-1 decoded video GIF (full-rate playback)

The human labels whether a collision occurred (binary).
Mode_0 and mode_1 predictions are generated and saved to disk silently
(never shown to the human).

All outputs for one sample share the same unique sample_uid:
  output/samples/{sample_uid}/gt.png, mode_0.png, mode_1.png, stride1_video.gif

Labels are saved atomically to output/collision_labels.json.

Example usage:
    cd human-label
    source ../1xgpt/venv/bin/activate
    python label_collisions.py \
        --val_data_dirs ../1xgpt/data/final_eval/flashlight_coca_eval_tokenized \
        --checkpoint_dirs ../1xgpt/data/final_ckpt/mode_0_epoch_9 \
                          ../1xgpt/data/final_ckpt/mode_1_epoch_9
"""

import argparse
import json
import math
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = str(Path(__file__).resolve().parent)
ONEXGPT_DIR = str(Path(__file__).resolve().parent.parent / "1xgpt")
sys.path.insert(0, ONEXGPT_DIR)
os.chdir(ONEXGPT_DIR)

from data import RawTokenDataset
from visualize import decode_latents_wrapper
from eval_utils import decode_tokens
from genie.st_mask_git import STMaskGIT
from generate_samples import (
    generate_video_predictions,
    generate_contact_predictions,
    decode_tokens_to_pil,
    save_comic_strip,
)

import gradio as gr

FORCE_DARK_JS = """
function refresh() {
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
}
"""

DEFAULT_STRIDE = 15
DEFAULT_WINDOW_SIZE = 16
DEFAULT_NUM_PROMPT_FRAMES = 8


def parse_args():
    parser = argparse.ArgumentParser(
        description="Human labeling interface for collision detection."
    )
    parser.add_argument(
        "--val_data_dirs", type=str, nargs="+", required=True,
        help="One or more tokenized eval dataset directories.",
    )
    parser.add_argument(
        "--checkpoint_dirs", type=str, nargs="+", required=True,
        help="One or more checkpoint directories. Mode auto-detected.",
    )
    parser.add_argument(
        "--output_dir", type=str, default="output",
        help="Root output directory for labels and sample artifacts.",
    )
    parser.add_argument(
        "--output_json", type=str, default=None,
        help="Path to labels JSON (default: {output_dir}/collision_labels.json).",
    )
    parser.add_argument("--stride", type=int, default=DEFAULT_STRIDE)
    parser.add_argument("--window_size", type=int, default=DEFAULT_WINDOW_SIZE)
    parser.add_argument("--num_prompt_frames", type=int, default=DEFAULT_NUM_PROMPT_FRAMES)
    parser.add_argument("--maskgit_steps", type=int, default=2)
    parser.add_argument("--temperature", type=float, default=0)
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--jump", type=int, default=50,
                        help="Minimum gap in raw frames between consecutive sample start positions. "
                             "Default: 50 (2 seconds at 25fps).")
    parser.add_argument("--skip_labeled", action="store_true",
                        help="Skip samples that already have a label.")
    parser.add_argument("--inference_only", action="store_true",
                        help="Run inference on all samples and save artifacts, "
                             "but do not launch the labeling UI or produce collision_labels.json.")
    parser.add_argument("--inference_future_only", action="store_true",
                        help="Like --inference_only but only produce future frames "
                             "(no context frames) and only future GIFs (no full GIFs).")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Sample registry
# ---------------------------------------------------------------------------

class SampleRegistry:
    """Flat list of all samples across datasets with unique IDs."""

    def __init__(self, val_data_dirs, window_size, stride, jump=None):
        self.entries = []
        self.datasets = {}
        if jump is None:
            jump = 50

        for data_dir in val_data_dirs:
            data_dir = str(Path(data_dir).resolve())
            ds_name = Path(data_dir).name
            ds = RawTokenDataset(
                data_dir,
                window_size=window_size,
                stride=stride,
                filter_overlaps=False,
            )
            self.datasets[ds_name] = ds

            total_valid = len(ds.valid_start_inds)
            last_start = -jump
            for idx in range(total_valid):
                sf = ds.valid_start_inds[idx]
                if sf - last_start >= jump:
                    uid = f"{ds_name}__start{sf}"
                    self.entries.append({
                        "uid": uid,
                        "dataset_name": ds_name,
                        "dataset_idx": idx,
                        "start_frame": sf,
                    })
                    last_start = sf

            print(f"  {ds_name}: {total_valid} valid windows -> "
                  f"{len([e for e in self.entries if e['dataset_name'] == ds_name])} "
                  f"samples (jump={jump})")

        print(f"Sample registry: {len(self.entries)} total samples "
              f"across {len(self.datasets)} dataset(s), jump={jump}")

    def __len__(self):
        return len(self.entries)

    def get_entry(self, flat_idx):
        return self.entries[flat_idx]

    def get_dataset(self, ds_name):
        return self.datasets[ds_name]


# ---------------------------------------------------------------------------
# Labels I/O
# ---------------------------------------------------------------------------

def load_labels(json_path):
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            return json.load(f)
    return {"metadata": {}, "labels": {}}


def save_labels_atomic(data, json_path):
    """Write JSON atomically via tmp + rename."""
    os.makedirs(os.path.dirname(json_path) or ".", exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=os.path.dirname(json_path) or ".", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, json_path)
    except Exception:
        os.unlink(tmp_path)
        raise


# ---------------------------------------------------------------------------
# GIF generation utilities
# ---------------------------------------------------------------------------

def make_raw_gif(data_array, start, end, decode_latents, output_path, fps=25):
    """Decode raw token data at stride=1 from a memmap array and save as GIF.

    Works for both video (dataset.data) and contact (dataset.contact) arrays.
    """
    if os.path.exists(output_path):
        return output_path

    tokens = data_array[start: end + 1]  # (N, H, W)
    pil_frames = decode_latents(tokens.astype(np.int64))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    duration_ms = 1000 / fps
    pil_frames[0].save(
        output_path, format="GIF", append_images=pil_frames[1:],
        save_all=True, duration=duration_ms, loop=0,
    )
    return output_path


def make_pil_gif(pil_frames, output_path, fps=25 / 15):
    """Save a list of already-decoded PIL images as a GIF.

    Used for stride-15 GIFs where frames are already decoded.
    Default fps=25/15 (~1.667) matches real-time playback at stride=15, 25fps source.
    """
    if os.path.exists(output_path):
        return output_path
    if not pil_frames:
        return None

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    duration_ms = 1000 / fps
    pil_frames[0].save(
        output_path, format="GIF", append_images=pil_frames[1:],
        save_all=True, duration=duration_ms, loop=0,
    )
    return output_path


def make_sidebyside_frame(video_pil, contact_pil, gap=16, label_h=32):
    """Composite video (left) and contact (right) into one image with labels."""
    w, h = video_pil.size
    total_w = 2 * w + gap
    total_h = h + label_h
    canvas = Image.new("RGB", (total_w, total_h), (0, 0, 0))

    canvas.paste(video_pil, (0, label_h))
    canvas.paste(contact_pil, (w + gap, label_h))

    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except OSError:
        font = ImageFont.load_default()

    vid_bbox = draw.textbbox((0, 0), "Video", font=font)
    vid_tw = vid_bbox[2] - vid_bbox[0]
    draw.text(((w - vid_tw) // 2, 4), "Video", fill="white", font=font)

    con_bbox = draw.textbbox((0, 0), "Contact", font=font)
    con_tw = con_bbox[2] - con_bbox[0]
    draw.text((w + gap + (w - con_tw) // 2, 4), "Contact", fill="white", font=font)

    return canvas


def label_frame(pil_img, text, label_h=32):
    """Add a text banner at the top of a PIL image."""
    w, h = pil_img.size
    canvas = Image.new("RGB", (w, h + label_h), (0, 0, 0))
    canvas.paste(pil_img, (0, label_h))

    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, 4), text, fill="white", font=font)
    return canvas


def make_sidebyside_raw_gif(video_array, contact_array, start, end,
                            decode_latents, output_path, fps=25):
    """Decode video and contact at stride-1, composite side-by-side, save GIF."""
    if os.path.exists(output_path):
        return output_path

    vid_tokens = video_array[start: end + 1]
    con_tokens = contact_array[start: end + 1]
    vid_frames = decode_latents(vid_tokens.astype(np.int64))
    con_frames = decode_latents(con_tokens.astype(np.int64))

    composites = [make_sidebyside_frame(v, c) for v, c in zip(vid_frames, con_frames)]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    duration_ms = 1000 / fps
    composites[0].save(
        output_path, format="GIF", append_images=composites[1:],
        save_all=True, duration=duration_ms, loop=0,
    )
    return output_path


# ---------------------------------------------------------------------------
# Per-sample artifact generation
# ---------------------------------------------------------------------------

@torch.no_grad()
def generate_sample_artifacts(
    entry, registry, models, decode_latents, args, output_dir,
    future_only=False,
):
    """
    Generate and save all artifacts for one sample:
      - gt.png (video-only comic strip)
      - gt_contact.png (video + contact comic strip, if contact data exists)
      - mode_X.png for each checkpoint (predictions, saved silently)
      - gif/ folder with all GIF variants

    Returns paths: (gt_path, gt_contact_path_or_None, gif_path)
    """
    uid = entry["uid"]
    ds_name = entry["dataset_name"]
    ds_idx = entry["dataset_idx"]
    start_frame = entry["start_frame"]
    ds = registry.get_dataset(ds_name)

    sample_dir = Path(output_dir) / "samples" / uid
    sample_dir.mkdir(parents=True, exist_ok=True)
    gif_dir = sample_dir / "gif"
    gif_dir.mkdir(parents=True, exist_ok=True)

    suffix = "_future_only" if future_only else ""
    gt_path = sample_dir / f"gt{suffix}.png"
    gt_contact_path = sample_dir / f"gt_contact{suffix}.png"
    gif_path = gif_dir / "gt_future_stride1.gif"

    has_contact = ds.contact is not None
    gt_contact_result = str(gt_contact_path) if has_contact else None

    # Fast path: if all artifacts already exist, skip all decoding/inference
    expected = [gt_path, gif_path]
    if has_contact:
        expected.append(gt_contact_path)
    for ml in models:
        expected.append(sample_dir / f"{ml}{suffix}.png")
    if all(p.exists() for p in expected):
        return str(gt_path), gt_contact_result, str(gif_path)

    device = "cuda"
    latent_s = ds.metadata["s"]
    video_len = (args.window_size - 1) * args.stride
    npf = args.num_prompt_frames
    s = args.stride
    future_start = start_frame + npf * s
    future_end = start_frame + video_len

    sample = ds[ds_idx]
    video_THW = sample["input_ids"].reshape(
        1, args.window_size, latent_s, latent_s
    ).to(device)
    actions = sample["actions"].unsqueeze(0).to(device)
    joint_angles = sample["joint_angles"].unsqueeze(0).to(device)

    if has_contact:
        contact_THW = sample["contact"].reshape(
            1, args.window_size, latent_s, latent_s
        ).to(device)

    # Decode GT frames once (needed for comic strips and stride-15 GIFs)
    gt_video_pil = decode_tokens_to_pil(video_THW, decode_latents)
    gt_contact_pil = None
    if has_contact:
        gt_contact_pil = decode_tokens_to_pil(contact_THW, decode_latents)

    # --- GT video-only comic strip ---
    if not gt_path.exists():
        if future_only:
            save_comic_strip([gt_video_pil[npf:]], [("Future", "Future")],
                             args.window_size - npf, str(gt_path))
        else:
            save_comic_strip([gt_video_pil], [("Context", "Future")],
                             args.window_size, str(gt_path))

    # --- GT video + contact comic strip ---
    if has_contact and not gt_contact_path.exists():
        if future_only:
            save_comic_strip(
                [gt_video_pil[npf:], gt_contact_pil[npf:]],
                [("Future", "Future"), ("Contact Future", "Contact Future")],
                args.window_size - npf, str(gt_contact_path),
            )
        else:
            save_comic_strip(
                [gt_video_pil, gt_contact_pil],
                [("Context", "Future"), ("Contact Context", "Contact Future")],
                args.window_size, str(gt_contact_path),
            )

    # --- Model predictions (saved silently, not shown) ---
    pred_pil_cache = {}
    for model_label, model in models.items():
        pred_path = sample_dir / f"{model_label}{suffix}.png"

        mode = model.config.mode
        pred_future = generate_video_predictions(
            model, video_THW, actions, joint_angles, args
        )
        full_pred_video = torch.cat([
            video_THW[:, :npf], pred_future
        ], dim=1)
        pred_video_pil = decode_tokens_to_pil(full_pred_video, decode_latents)
        pred_rows = [pred_video_pil]
        pred_labels = [("Context", "Future")]

        pred_contact_pil = None
        if mode == 0 and has_contact:
            pred_contact = generate_contact_predictions(
                model, video_THW, pred_future, actions, joint_angles, args
            )
            full_pred_contact = torch.cat([
                contact_THW[:, :npf], pred_contact
            ], dim=1)
            pred_contact_pil = decode_tokens_to_pil(full_pred_contact, decode_latents)
            if future_only:
                pred_rows.append(pred_contact_pil[npf:])
                pred_labels.append(("Contact Future", "Contact Future"))
            else:
                pred_rows.append(pred_contact_pil)
                pred_labels.append(("Contact Context", "Contact Future"))

        if not pred_path.exists():
            if future_only:
                # Only future frames for video row too
                save_comic_strip(
                    [pred_video_pil[npf:]] + pred_rows[1:],
                    [("Future", "Future")] + pred_labels[1:],
                    args.window_size - npf, str(pred_path),
                )
            else:
                save_comic_strip(pred_rows, pred_labels, args.window_size, str(pred_path))

        pred_pil_cache[model_label] = {
            "video": pred_video_pil,
            "contact": pred_contact_pil,
        }

    # --- GIF generation ---
    # GT video: stride-1
    make_raw_gif(ds.data, future_start, future_end, decode_latents,
                 str(gif_dir / "gt_future_stride1.gif"))
    # GT video: stride-15
    make_pil_gif(gt_video_pil[npf:], str(gif_dir / "gt_future_stride15.gif"))

    if not future_only:
        make_raw_gif(ds.data, start_frame, future_end, decode_latents,
                     str(gif_dir / "gt_full_stride1.gif"))
        make_pil_gif(gt_video_pil, str(gif_dir / "gt_full_stride15.gif"))

    if has_contact:
        # GT contact (side-by-side video+contact): stride-1
        make_sidebyside_raw_gif(ds.data, ds.contact, future_start, future_end,
                                decode_latents, str(gif_dir / "gt_contact_future_stride1.gif"))
        # GT contact (side-by-side video+contact): stride-15
        sbs_future = [make_sidebyside_frame(v, c)
                      for v, c in zip(gt_video_pil[npf:], gt_contact_pil[npf:])]
        make_pil_gif(sbs_future, str(gif_dir / "gt_contact_future_stride15.gif"))

        if not future_only:
            make_sidebyside_raw_gif(ds.data, ds.contact, start_frame, future_end,
                                    decode_latents, str(gif_dir / "gt_contact_full_stride1.gif"))
            sbs_full = [make_sidebyside_frame(v, c)
                        for v, c in zip(gt_video_pil, gt_contact_pil)]
            make_pil_gif(sbs_full, str(gif_dir / "gt_contact_full_stride15.gif"))

    # Prediction GIFs (stride-15 only)
    for model_label, cached in pred_pil_cache.items():
        pv = cached["video"]
        pc = cached["contact"]

        if pc is not None:
            # Mode 0: side-by-side video + contact
            sbs_fut = [make_sidebyside_frame(v, c)
                       for v, c in zip(pv[npf:], pc[npf:])]
            make_pil_gif(sbs_fut, str(gif_dir / f"{model_label}_future.gif"))

            if not future_only:
                sbs_all = [make_sidebyside_frame(v, c)
                           for v, c in zip(pv, pc)]
                labeled = ([label_frame(f, "Context") for f in sbs_all[:npf]]
                           + [label_frame(f, "Future") for f in sbs_all[npf:]])
                make_pil_gif(labeled, str(gif_dir / f"{model_label}_full.gif"))
        else:
            # Mode 1: video only
            make_pil_gif(pv[npf:], str(gif_dir / f"{model_label}_future.gif"))

            if not future_only:
                labeled = ([label_frame(f, "Context") for f in pv[:npf]]
                           + [label_frame(f, "Future") for f in pv[npf:]])
                make_pil_gif(labeled, str(gif_dir / f"{model_label}_full.gif"))

    return str(gt_path), gt_contact_result, str(gif_path)


# ---------------------------------------------------------------------------
# Gradio app
# ---------------------------------------------------------------------------

def build_app(registry, models, decode_latents, args, labels_data, labels_path):
    current_idx = gr.State(0)

    def count_labeled():
        return len(labels_data["labels"])

    def get_nav_indices(skip_labeled):
        """Return list of flat indices, optionally filtering already-labeled."""
        all_idxs = list(range(len(registry)))
        if not skip_labeled:
            return all_idxs
        return [i for i in all_idxs
                if registry.get_entry(i)["uid"] not in labels_data["labels"]]

    def find_first_unlabeled():
        for i in range(len(registry)):
            if registry.get_entry(i)["uid"] not in labels_data["labels"]:
                return i
        return 0

    def load_sample(flat_idx):
        """Generate artifacts and return display data for the given sample index."""
        flat_idx = max(0, min(flat_idx, len(registry) - 1))
        entry = registry.get_entry(flat_idx)
        uid = entry["uid"]

        gt_path, gt_contact_path, gif_path = generate_sample_artifacts(
            entry, registry, models, decode_latents, args, args.output_dir
        )

        existing_label = labels_data["labels"].get(uid)
        if existing_label is not None:
            label_text = "COLLISION" if existing_label["collision"] else "NO COLLISION"
            status = f"Current label: {label_text}"
        else:
            status = "Not yet labeled"

        total = len(registry)
        labeled = count_labeled()
        progress = f"Sample {flat_idx + 1} / {total}  ({labeled} labeled)"
        info = f"**{uid}**\n\n{progress}\n\n{status}"

        return flat_idx, gt_path, gt_contact_path, gif_path, info

    def on_label(flat_idx, collision_value):
        entry = registry.get_entry(flat_idx)
        uid = entry["uid"]
        labels_data["labels"][uid] = {
            "collision": collision_value,
            "timestamp": datetime.now().isoformat(),
            "dataset": entry["dataset_name"],
            "dataset_idx": entry["dataset_idx"],
            "start_frame": entry["start_frame"],
        }
        save_labels_atomic(labels_data, labels_path)
        next_idx = min(flat_idx + 1, len(registry) - 1)
        return load_sample(next_idx)

    def on_collision(flat_idx):
        return on_label(flat_idx, True)

    def on_no_collision(flat_idx):
        return on_label(flat_idx, False)

    def on_skip(flat_idx):
        next_idx = min(flat_idx + 1, len(registry) - 1)
        return load_sample(next_idx)

    def on_prev(flat_idx):
        prev_idx = max(flat_idx - 1, 0)
        return load_sample(prev_idx)

    def on_goto(idx_text):
        try:
            idx = int(idx_text)
        except ValueError:
            idx = 0
        return load_sample(idx)

    # Build Gradio UI
    with gr.Blocks(title="Collision Labeler") as app:
        gr.Markdown("# Collision Labeling Interface")
        gr.Markdown("Label whether a **collision** occurred in the ground truth validation window. "
                    "Scroll to zoom, drag to pan on the comic strip image.")

        with gr.Row():
            info_md = gr.Markdown("Loading...")

        with gr.Row():
            gt_image = gr.Image(
                label="Video (scroll to zoom, drag to pan)",
                type="filepath",
                height=500,
            )

        with gr.Row():
            gt_contact_image = gr.Image(
                label="Video + Contact (scroll to zoom, drag to pan)",
                type="filepath",
                height=500,
            )

        with gr.Row():
            gif_image = gr.Image(
                label="Future Video (full-rate playback)",
                type="filepath",
                height=400,
            )

        with gr.Row():
            collision_btn = gr.Button("Collision", variant="stop", size="lg")
            no_collision_btn = gr.Button("No Collision", variant="primary", size="lg")
            skip_btn = gr.Button("Skip", variant="secondary", size="lg")
            prev_btn = gr.Button("Prev", variant="secondary", size="lg")

        with gr.Row():
            goto_input = gr.Textbox(
                label="Go to sample index",
                placeholder="Enter index (0-based)",
                scale=1,
            )
            goto_btn = gr.Button("Go", variant="secondary", scale=0)

        idx_state = gr.State(find_first_unlabeled())

        outputs = [idx_state, gt_image, gt_contact_image, gif_image, info_md]

        collision_btn.click(on_collision, inputs=[idx_state], outputs=outputs)
        no_collision_btn.click(on_no_collision, inputs=[idx_state], outputs=outputs)
        skip_btn.click(on_skip, inputs=[idx_state], outputs=outputs)
        prev_btn.click(on_prev, inputs=[idx_state], outputs=outputs)
        goto_btn.click(on_goto, inputs=[goto_input], outputs=outputs)

        app.load(lambda: load_sample(find_first_unlabeled()), outputs=outputs)

    return app


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

@torch.no_grad()
def main():
    args = parse_args()

    # Resolve output paths relative to human-label/ dir (before os.chdir changed cwd)
    if not os.path.isabs(args.output_dir):
        args.output_dir = os.path.join(SCRIPT_DIR, args.output_dir)
    if args.output_json is None:
        args.output_json = os.path.join(args.output_dir, "collision_labels.json")
    if not os.path.isabs(args.output_json):
        args.output_json = os.path.join(SCRIPT_DIR, args.output_json)

    labels_path = str(Path(args.output_json).resolve())
    os.makedirs(args.output_dir, exist_ok=True)

    # Build sample registry
    print("Building sample registry ...")
    registry = SampleRegistry(args.val_data_dirs, args.window_size, args.stride, jump=args.jump)

    # Load models
    print(f"\nLoading {len(args.checkpoint_dirs)} checkpoint(s) ...")
    models = {}
    device = "cuda"
    for ckpt_dir in args.checkpoint_dirs:
        model = STMaskGIT.from_pretrained(ckpt_dir).to(device)
        model.eval()
        mode = model.config.mode
        label = f"mode_{mode}"
        if label in models:
            label = f"mode_{mode}_{Path(ckpt_dir).name}"
        models[label] = model
        print(f"  Loaded {ckpt_dir} -> {label} (mode={mode})")

    # Init decoder
    print("\nInitializing Cosmos decoder ...")
    decode_latents = decode_latents_wrapper()

    # Inference-only mode: generate all artifacts then exit
    if args.inference_only or args.inference_future_only:
        future_only = args.inference_future_only
        mode_label = "inference-future-only" if future_only else "inference-only"
        total = len(registry)
        print(f"\n{mode_label} mode: generating artifacts for {total} samples ...")
        for i in range(total):
            entry = registry.get_entry(i)
            print(f"  [{i + 1}/{total}] {entry['uid']}")
            generate_sample_artifacts(
                entry, registry, models, decode_latents, args, args.output_dir,
                future_only=future_only,
            )
        print(f"\nDone. Artifacts saved under {args.output_dir}/samples/")
        return

    # Load existing labels
    labels_data = load_labels(labels_path)
    if not labels_data["metadata"]:
        labels_data["metadata"] = {
            "checkpoint_dirs": args.checkpoint_dirs,
            "stride": args.stride,
            "window_size": args.window_size,
            "num_prompt_frames": args.num_prompt_frames,
            "created": datetime.now().isoformat(),
        }
        save_labels_atomic(labels_data, labels_path)

    labeled_count = len(labels_data["labels"])
    print(f"\nLoaded {labeled_count} existing labels from {labels_path}")
    print(f"Total samples: {len(registry)}")

    # Build and launch Gradio app
    app = build_app(registry, models, decode_latents, args, labels_data, labels_path)
    allowed = [os.path.abspath(args.output_dir)]
    print(f"\nLaunching labeling interface (preferred port {args.port}) ...")
    try:
        app.launch(server_name="0.0.0.0", server_port=args.port, allowed_paths=allowed,
                   js=FORCE_DARK_JS)
    except OSError:
        print(f"Port {args.port} is busy, finding a free port ...")
        app.launch(server_name="0.0.0.0", allowed_paths=allowed,
                   js=FORCE_DARK_JS)


if __name__ == "__main__":
    main()

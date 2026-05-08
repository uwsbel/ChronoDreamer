"""
VLM-as-judge evaluation pipeline for collision detection.

Sends comic-strip images to a Vision-Language Model (NVIDIA NIM or Google Gemini)
with 5 prompt variants across 4 evaluation conditions. Collects 1-5 Likert-scale
collision scores and computes three aggregate metrics:

  Score 1 (VLM Ceiling)   -- How well the VLM judges GT data vs oracle labels
  Score 2 (Fidelity Gap)  -- Divergence between GT and predicted ensemble scores
  Score 3 (Accuracy Drop) -- Binary accuracy loss from GT to predicted conditions

Usage:
    python vlm_evaluate.py --backend gemini --data_dir output_pilot
    python vlm_evaluate.py --backend nvidia --api_key $NVIDIA_API_KEY --data_dir output_pilot
    python vlm_evaluate.py --analyze_only --data_dir output_pilot
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import importlib
import inspect

import numpy as np

# ============================================================================
# Constants
# ============================================================================

SCRIPT_DIR = Path(__file__).resolve().parent

DEFAULT_NVIDIA_MODEL = "meta/llama-3.2-90b-vision-instruct"
DEFAULT_NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"

PROMPT_VARIANT_IDS = ["P1", "P2", "P3", "P4", "P5"]

BINARIZATION_THRESHOLDS = [2.5, 3.0, 3.5, 4.0]
DEFAULT_THRESHOLD = 3.0

MAX_RETRIES = 3
INITIAL_BACKOFF_SEC = 2.0

# Maps each evaluation condition to its image file and whether the prompt
# should include the contact-channel addendum.
CONDITION_MAP: dict[str, dict[str, Any]] = {
    "gt_video": {
        "image_file": "gt.png",
        "has_contact": False,
        "description": "Ground truth RGB only",
    },
    "gt_video_contact": {
        "image_file": "gt_contact.png",
        "has_contact": True,
        "description": "Ground truth RGB + contact splat",
    },
    "mode_0": {
        "image_file": "mode_0.png",
        "has_contact": True,
        "description": "Mode 0 prediction (video + contact)",
    },
    "mode_1": {
        "image_file": "mode_1.png",
        "has_contact": False,
        "description": "Mode 1 prediction (video only)",
    },
}


# ============================================================================
# JSON extraction from VLM response
# ============================================================================

def extract_json(text: str) -> dict:
    """Parse JSON from VLM response, stripping markdown fences if present.

    Args:
        text: Raw response text from the VLM.

    Returns:
        Parsed dict from the JSON content.

    Raises:
        ValueError: If no valid JSON can be extracted.
    """
    cleaned = text.strip()

    # Strip ```json ... ``` or ``` ... ```
    fence_pattern = re.compile(r"```(?:json)?\s*\n?(.*?)\n?\s*```", re.DOTALL)
    match = fence_pattern.search(cleaned)
    if match:
        cleaned = match.group(1).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Fallback: find first { ... } block
    brace_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract JSON from response: {text[:200]}")


def sanitize_model_for_filename(model: str) -> str:
    """Turn a model id into a safe single path component (no slashes, etc.)."""
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "_", model.strip())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "model"


def extract_score(parsed: dict) -> int:
    """Extract and clamp the integer score from a parsed VLM response.

    Args:
        parsed: Dict parsed from VLM JSON response.

    Returns:
        Integer score clamped to [1, 5].

    Raises:
        ValueError: If no 'score' key is found.
    """
    raw = parsed.get("score")
    if raw is None:
        raise ValueError(f"No 'score' field in response: {parsed}")
    score = int(raw)
    return max(1, min(5, score))


# ============================================================================
# VLM backend: NVIDIA NIM
# ============================================================================

class NvidiaBackend:
    """Calls a VLM via NVIDIA NIM's OpenAI-compatible endpoint.

    Requires the ``openai`` package.
    """

    def __init__(self, api_key: str, model: str, base_url: str):
        try:
            from openai import OpenAI
        except ImportError:
            sys.exit("ERROR: 'openai' package required for nvidia backend. "
                     "Install with: pip install openai")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def call(self, image_path: str, prompt_text: str) -> tuple[str, dict]:
        """Send an image + prompt to the NVIDIA NIM VLM.

        Args:
            image_path: Path to the comic-strip PNG.
            prompt_text: Full prompt string.

        Returns:
            Tuple of (raw_text, parsed_dict) from the VLM response.
        """
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            max_tokens=16384,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_b64}"},
                    },
                    {"type": "text", "text": prompt_text},
                ],
            }],
            extra_body={"include_reasoning": False},
        )
        choice = response.choices[0]
        raw_text = choice.message.content
        if raw_text is None:
            finish = getattr(choice, "finish_reason", "unknown")
            raise ValueError(f"Model returned empty content (finish_reason={finish})")
        raw_text = raw_text.strip()
        return raw_text, extract_json(raw_text)


# ============================================================================
# VLM backend: Google Gemini
# ============================================================================

class GeminiBackend:
    """Calls a VLM via Google's Gemini API using the google-genai SDK.

    Requires the ``google-genai`` package.
    """

    def __init__(self, api_key: str, model: str):
        try:
            from google import genai
            from google.genai import types  # noqa: F401
        except ImportError:
            sys.exit("ERROR: 'google-genai' package required for gemini backend. "
                     "Install with: pip install google-genai")
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def call(self, image_path: str, prompt_text: str) -> tuple[str, dict]:
        """Send an image + prompt to Gemini.

        Args:
            image_path: Path to the comic-strip PNG.
            prompt_text: Full prompt string.

        Returns:
            Tuple of (raw_text, parsed_dict) from the VLM response.
        """
        from google.genai import types

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                prompt_text,
            ],
            config=types.GenerateContentConfig(temperature=0.2),
        )
        raw_text = response.text.strip()
        return raw_text, extract_json(raw_text)


# ============================================================================
# Unified VLM caller with retry
# ============================================================================

def call_vlm_with_retry(
    backend: NvidiaBackend | GeminiBackend,
    image_path: str,
    prompt_text: str,
) -> tuple[str, dict]:
    """Call the VLM backend with exponential-backoff retry on failure.

    Args:
        backend: An NvidiaBackend or GeminiBackend instance.
        image_path: Path to the comic-strip image.
        prompt_text: Full prompt string.

    Returns:
        Tuple of (raw_text, parsed_dict) from VLM response.

    Raises:
        RuntimeError: If all retries are exhausted.
    """
    last_error: Optional[Exception] = None
    for attempt in range(MAX_RETRIES):
        try:
            return backend.call(image_path, prompt_text)
        except Exception as e:
            last_error = e
            wait = INITIAL_BACKOFF_SEC * (2 ** attempt)
            print(f"  [retry {attempt + 1}/{MAX_RETRIES}] {type(e).__name__}: {e}")
            print(f"  Waiting {wait:.1f}s before next attempt...")
            time.sleep(wait)

    raise RuntimeError(
        f"VLM call failed after {MAX_RETRIES} retries. Last error: {last_error}"
    )


# ============================================================================
# Result I/O (atomic saves)
# ============================================================================

def load_results(json_path: str) -> dict:
    """Load existing VLM results from disk, or return empty structure.

    Args:
        json_path: Path to the results JSON file.

    Returns:
        Dict with 'metadata' and 'results' keys.
    """
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            return json.load(f)
    return {"metadata": {}, "results": []}


def save_results_atomic(data: dict, json_path: str) -> None:
    """Write results JSON atomically via tmp file + rename.

    Args:
        data: The full results dict to serialize.
        json_path: Destination path.
    """
    os.makedirs(os.path.dirname(json_path) or ".", exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=os.path.dirname(json_path) or ".", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, json_path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def build_result_key(sample_uid: str, condition: str, prompt_id: str) -> str:
    """Build a unique key for a sample/condition/prompt combination.

    Args:
        sample_uid: The sample's unique identifier.
        condition: Evaluation condition name.
        prompt_id: Prompt variant ID (P1-P5).

    Returns:
        A string key like "flashlight__start0|gt_video|P1".
    """
    return f"{sample_uid}|{condition}|{prompt_id}"


def get_existing_keys(results_data: dict, backend_name: str) -> set[str]:
    """Extract the set of already-completed result keys for a specific model.

    Only entries matching the given backend_name are considered, so switching
    models won't incorrectly skip calls.

    Args:
        results_data: The loaded results dict.
        backend_name: The backend/model identifier to filter by.

    Returns:
        Set of result key strings for the specified model.
    """
    keys = set()
    for entry in results_data.get("results", []):
        if entry.get("model") != backend_name:
            continue
        key = build_result_key(
            entry["sample"], entry["condition"], entry["prompt_id"]
        )
        keys.add(key)
    return keys


# ============================================================================
# Main evaluation loop
# ============================================================================

def run_evaluation(
    backend: NvidiaBackend | GeminiBackend,
    backend_name: str,
    build_prompt,
    data_dir: str,
    output_json: str,
    conditions: list[str],
    prompt_ids: list[str],
    rate_limit: float,
    resume: bool,
) -> dict:
    """Run the full VLM evaluation loop across all samples, conditions, and prompts.

    Args:
        backend: The VLM backend instance.
        backend_name: Human-readable backend name for metadata.
        build_prompt: Function(variant_id, has_contact) -> prompt string.
        data_dir: Root directory containing collision_labels.json and samples/.
        output_json: Path to write/append results.
        conditions: List of condition names to evaluate.
        prompt_ids: List of prompt variant IDs to run.
        rate_limit: Minimum seconds between API calls.
        resume: If True, skip combinations already in the output file.

    Returns:
        The complete results dict.
    """
    # Detect whether build_prompt accepts has_contact (2 params) or just variant_id (1 param)
    sig = inspect.signature(build_prompt)
    _build_prompt_takes_contact = len(sig.parameters) >= 2

    labels_path = os.path.join(data_dir, "collision_labels.json")
    if not os.path.exists(labels_path):
        sys.exit(f"ERROR: Labels file not found: {labels_path}")

    with open(labels_path, "r") as f:
        labels_data = json.load(f)

    labels = labels_data.get("labels", {})
    if not labels:
        sys.exit("ERROR: No labeled samples found in collision_labels.json")

    samples_dir = os.path.join(data_dir, "samples")
    if not os.path.isdir(samples_dir):
        sys.exit(f"ERROR: Samples directory not found: {samples_dir}")

    results_data = load_results(output_json) if resume else {"metadata": {}, "results": []}

    if resume and results_data["metadata"]:
        existing_backend = results_data["metadata"].get("backend", "")
        if existing_backend and existing_backend != backend_name:
            print(f"WARNING: Results file was created with '{existing_backend}' "
                  f"but you are now using '{backend_name}'.")
            print(f"  Resume will only skip entries from the current model.")

    existing_keys = get_existing_keys(results_data, backend_name) if resume else set()

    if not results_data["metadata"]:
        results_data["metadata"] = {
            "backend": backend_name,
            "conditions": conditions,
            "prompt_ids": prompt_ids,
            "data_dir": data_dir,
            "started": datetime.now().isoformat(),
        }

    total_combos = len(labels) * len(conditions) * len(prompt_ids)
    skipped = 0
    completed = 0
    errors = 0

    print(f"\n{'=' * 60}")
    print(f"VLM Evaluation: {len(labels)} samples x {len(conditions)} conditions "
          f"x {len(prompt_ids)} prompts = {total_combos} calls")
    print(f"Model: {backend_name}")
    if resume:
        print(f"Resume mode: {len(existing_keys)} existing results will be skipped")
    print(f"{'=' * 60}\n")

    for sample_i, (sample_uid, label_info) in enumerate(labels.items()):
        oracle_collision = label_info["collision"]
        sample_path = os.path.join(samples_dir, sample_uid)

        if not os.path.isdir(sample_path):
            print(f"[{sample_i + 1}/{len(labels)}] SKIP {sample_uid}: "
                  f"sample directory not found")
            continue

        print(f"[{sample_i + 1}/{len(labels)}] {sample_uid} "
              f"(oracle={'collision' if oracle_collision else 'no collision'})")

        for condition in conditions:
            cond_info = CONDITION_MAP[condition]
            image_file = os.path.join(sample_path, cond_info["image_file"])

            if not os.path.exists(image_file):
                print(f"  {condition}: image not found ({cond_info['image_file']}), skipping")
                continue

            for prompt_id in prompt_ids:
                result_key = build_result_key(sample_uid, condition, prompt_id)

                if result_key in existing_keys:
                    skipped += 1
                    continue

                prompt_text = build_prompt(prompt_id, cond_info["has_contact"]) \
                    if _build_prompt_takes_contact else build_prompt(prompt_id)

                print(f"  {condition}/{prompt_id}: calling VLM...", end="", flush=True)
                t0 = time.time()
                try:
                    raw_text, parsed = call_vlm_with_retry(backend, image_file, prompt_text)
                    score = extract_score(parsed)
                    elapsed = time.time() - t0
                    print(f" score={score} ({elapsed:.1f}s)")
                    entry = {
                        "sample": sample_uid,
                        "dataset": label_info.get("dataset", ""),
                        "condition": condition,
                        "prompt_id": prompt_id,
                        "model": backend_name,
                        "oracle": oracle_collision,
                        "score": score,
                        "raw_text": raw_text,
                        "raw_response": parsed,
                        "timestamp": datetime.now().isoformat(),
                    }
                    completed += 1
                except Exception as e:
                    elapsed = time.time() - t0
                    print(f" FAILED ({elapsed:.1f}s): {e}")
                    entry = {
                        "sample": sample_uid,
                        "dataset": label_info.get("dataset", ""),
                        "condition": condition,
                        "prompt_id": prompt_id,
                        "model": backend_name,
                        "oracle": oracle_collision,
                        "score": None,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                    errors += 1

                results_data["results"].append(entry)
                time.sleep(rate_limit)

        # Atomic save after each sample
        save_results_atomic(results_data, output_json)

    results_data["metadata"]["finished"] = datetime.now().isoformat()
    results_data["metadata"]["total_calls"] = completed
    results_data["metadata"]["errors"] = errors
    results_data["metadata"]["skipped_resume"] = skipped
    save_results_atomic(results_data, output_json)

    print(f"\nEvaluation complete: {completed} calls, {errors} errors, "
          f"{skipped} skipped (resume)")
    print(f"Results saved to: {output_json}")

    return results_data


# ============================================================================
# Analysis: ensemble aggregation
# ============================================================================

def aggregate_ensembles(results_data: dict) -> dict[str, dict[str, dict]]:
    """Aggregate per-prompt scores into ensemble statistics per sample+condition.

    Args:
        results_data: The complete results dict.

    Returns:
        Nested dict: {sample_uid: {condition: {scores, mean, std, median, oracle}}}.
    """
    ensembles: dict[str, dict[str, dict]] = {}

    for entry in results_data.get("results", []):
        uid = entry["sample"]
        cond = entry["condition"]
        score = entry.get("score")
        oracle = entry.get("oracle")

        if uid not in ensembles:
            ensembles[uid] = {}
        if cond not in ensembles[uid]:
            ensembles[uid][cond] = {"scores": [], "oracle": oracle}

        if score is not None:
            ensembles[uid][cond]["scores"].append(score)

    for uid in ensembles:
        for cond in ensembles[uid]:
            scores = ensembles[uid][cond]["scores"]
            if scores:
                ensembles[uid][cond]["mean"] = float(np.mean(scores))
                ensembles[uid][cond]["std"] = float(np.std(scores))
                ensembles[uid][cond]["median"] = float(np.median(scores))
            else:
                ensembles[uid][cond]["mean"] = None
                ensembles[uid][cond]["std"] = None
                ensembles[uid][cond]["median"] = None

    return ensembles


# ============================================================================
# Analysis: three-score framework
# ============================================================================

def _try_import_sklearn():
    """Attempt to import sklearn metrics, return (roc_auc_score, accuracy_score) or None."""
    try:
        from sklearn.metrics import accuracy_score, roc_auc_score
        return roc_auc_score, accuracy_score
    except ImportError:
        print("WARNING: scikit-learn not installed. AUC will not be computed.")
        print("  Install with: pip install scikit-learn")
        return None, None


def compute_accuracy(oracle_labels: list[bool], predictions: list[bool]) -> float:
    """Compute binary accuracy.

    Args:
        oracle_labels: Ground truth boolean labels.
        predictions: Predicted boolean labels.

    Returns:
        Accuracy as a float in [0, 1].
    """
    if not oracle_labels:
        return float("nan")
    correct = sum(1 for o, p in zip(oracle_labels, predictions) if o == p)
    return correct / len(oracle_labels)


def compute_analysis(results_data: dict) -> None:
    """Run the full three-score analysis and print results.

    Args:
        results_data: The complete results dict with raw VLM scores.
    """
    roc_auc_score_fn, _ = _try_import_sklearn()
    ensembles = aggregate_ensembles(results_data)

    if not ensembles:
        print("No ensemble data available for analysis.")
        return

    # Collect per-condition data: lists of (oracle, ensemble_mean) for accuracy etc.
    cond_data: dict[str, list[tuple[bool, float]]] = {}
    for uid, conds in ensembles.items():
        for cond, stats in conds.items():
            if stats["mean"] is not None:
                cond_data.setdefault(cond, []).append((stats["oracle"], stats["mean"]))

    # ---- Score 1: VLM Ceiling ----
    print(f"\n{'=' * 60}")
    print("SCORE 1: VLM CEILING (VLM on GT vs oracle labels)")
    print(f"{'=' * 60}")

    for cond in CONDITION_MAP:
        if cond not in cond_data:
            print(f"  {cond}: no data")
            continue

        pairs = cond_data[cond]
        oracles = [p[0] for p in pairs]
        means = [p[1] for p in pairs]

        print(f"\n  {cond} ({len(pairs)} samples):")

        # AUC computed on ensemble-averaged scores
        if roc_auc_score_fn and len(set(oracles)) > 1:
            auc = roc_auc_score_fn([int(o) for o in oracles], means)
            print(f"    AUC: {auc:.3f}")
        else:
            print(f"    AUC: N/A (need both classes or sklearn)")

        for thresh in BINARIZATION_THRESHOLDS:
            preds = [m >= thresh for m in means]
            acc = compute_accuracy(oracles, preds)
            marker = " <-- default" if thresh == DEFAULT_THRESHOLD else ""
            print(f"    Acc@{thresh}: {acc:.3f}{marker}")

        collision_scores = [m for o, m in pairs if o]
        no_collision_scores = [m for o, m in pairs if not o]
        if collision_scores:
            print(f"    Mean score (collision subset): {np.mean(collision_scores):.2f}")
        if no_collision_scores:
            print(f"    Mean score (no-collision subset): {np.mean(no_collision_scores):.2f}")

    # ---- Score 2: Fidelity Gap ----
    print(f"\n{'=' * 60}")
    print("SCORE 2: FIDELITY GAP (|GT_mean - Pred_mean| per sample)")
    print(f"{'=' * 60}")

    gt_pred_pairs = [
        ("gt_video", "mode_1", "RGB only"),
        ("gt_video_contact", "mode_0", "RGB + contact"),
    ]
    for gt_cond, pred_cond, desc in gt_pred_pairs:
        gt_map = {uid: stats["mean"]
                  for uid, conds in ensembles.items()
                  if gt_cond in conds and conds[gt_cond]["mean"] is not None
                  for stats in [conds[gt_cond]]}
        pred_map = {uid: stats["mean"]
                    for uid, conds in ensembles.items()
                    if pred_cond in conds and conds[pred_cond]["mean"] is not None
                    for stats in [conds[pred_cond]]}

        common_uids = set(gt_map) & set(pred_map)
        if not common_uids:
            print(f"\n  {desc}: no paired samples")
            continue

        gaps = [abs(gt_map[uid] - pred_map[uid]) for uid in common_uids]
        print(f"\n  {desc} ({len(gaps)} paired samples):")
        print(f"    Mean gap: {np.mean(gaps):.3f}")
        print(f"    Std gap:  {np.std(gaps):.3f}")
        print(f"    Max gap:  {np.max(gaps):.3f}")
        print(f"    Min gap:  {np.min(gaps):.3f}")

        # Breakdown by collision/no-collision
        for subset_label, subset_oracle in [("collision", True), ("no-collision", False)]:
            subset_gaps = []
            for uid in common_uids:
                cond_stats = ensembles[uid].get(gt_cond, {})
                if cond_stats.get("oracle") == subset_oracle:
                    subset_gaps.append(abs(gt_map[uid] - pred_map[uid]))
            if subset_gaps:
                print(f"    Mean gap ({subset_label}): {np.mean(subset_gaps):.3f} "
                      f"(n={len(subset_gaps)})")

    # ---- Score 3: Accuracy Drop ----
    print(f"\n{'=' * 60}")
    print("SCORE 3: ACCURACY DROP (GT accuracy - Pred accuracy)")
    print(f"{'=' * 60}")

    condition_acc: dict[str, float] = {}
    for cond in CONDITION_MAP:
        if cond not in cond_data:
            continue
        pairs = cond_data[cond]
        oracles = [p[0] for p in pairs]
        means = [p[1] for p in pairs]
        preds = [m >= DEFAULT_THRESHOLD for m in means]
        acc = compute_accuracy(oracles, preds)
        condition_acc[cond] = acc

        auc_str = "N/A"
        if roc_auc_score_fn and len(set(oracles)) > 1:
            auc_str = f"{roc_auc_score_fn([int(o) for o in oracles], means):.3f}"

        print(f"  {cond}: AUC={auc_str}  Acc@{DEFAULT_THRESHOLD}={acc:.3f} "
              f"(n={len(pairs)})")

    for gt_cond, pred_cond, desc in gt_pred_pairs:
        if gt_cond in condition_acc and pred_cond in condition_acc:
            drop = condition_acc[gt_cond] - condition_acc[pred_cond]
            print(f"\n  Accuracy drop ({desc}): "
                  f"{condition_acc[gt_cond]:.3f} - {condition_acc[pred_cond]:.3f} "
                  f"= {drop:+.3f}")


# ============================================================================
# Analysis: prompt sensitivity
# ============================================================================

def compute_prompt_sensitivity(results_data: dict) -> None:
    """Analyze per-prompt accuracy on GT conditions to check robustness.

    Args:
        results_data: The complete results dict.
    """
    print(f"\n{'=' * 60}")
    print("PROMPT SENSITIVITY (per-prompt accuracy on gt_video)")
    print(f"{'=' * 60}")

    gt_results = [r for r in results_data.get("results", [])
                  if r["condition"] == "gt_video" and r.get("score") is not None]

    if not gt_results:
        print("  No gt_video results available.")
        return

    prompt_ids = sorted(set(r["prompt_id"] for r in gt_results))
    for pid in prompt_ids:
        pid_results = [r for r in gt_results if r["prompt_id"] == pid]
        correct = sum(
            1 for r in pid_results
            if (r["score"] >= DEFAULT_THRESHOLD) == r["oracle"]
        )
        total = len(pid_results)
        acc = correct / total if total > 0 else 0
        scores = [r["score"] for r in pid_results]
        print(f"  {pid}: Acc={acc:.3f} ({correct}/{total})  "
              f"mean_score={np.mean(scores):.2f}  std={np.std(scores):.2f}")

    # Per-prompt accuracy on gt_video_contact
    gt_contact_results = [r for r in results_data.get("results", [])
                          if r["condition"] == "gt_video_contact"
                          and r.get("score") is not None]
    if gt_contact_results:
        print(f"\n  -- On gt_video_contact --")
        prompt_ids_c = sorted(set(r["prompt_id"] for r in gt_contact_results))
        for pid in prompt_ids_c:
            pid_results = [r for r in gt_contact_results if r["prompt_id"] == pid]
            correct = sum(
                1 for r in pid_results
                if (r["score"] >= DEFAULT_THRESHOLD) == r["oracle"]
            )
            total = len(pid_results)
            acc = correct / total if total > 0 else 0
            scores = [r["score"] for r in pid_results]
            print(f"  {pid}: Acc={acc:.3f} ({correct}/{total})  "
                  f"mean_score={np.mean(scores):.2f}  std={np.std(scores):.2f}")


# ============================================================================
# Analysis: per-sample breakdown
# ============================================================================

def print_per_sample_breakdown(results_data: dict) -> None:
    """Print a compact table of ensemble scores per sample across conditions.

    Args:
        results_data: The complete results dict.
    """
    ensembles = aggregate_ensembles(results_data)

    if not ensembles:
        return

    print(f"\n{'=' * 60}")
    print("PER-SAMPLE ENSEMBLE BREAKDOWN")
    print(f"{'=' * 60}")

    conds = list(CONDITION_MAP.keys())
    header = f"{'Sample':<45} {'Oracle':<8}" + "".join(f" {c:<18}" for c in conds)
    print(header)
    print("-" * len(header))

    for uid in sorted(ensembles.keys()):
        oracle_str = "?"
        parts = [f"{uid:<45}"]
        for cond in conds:
            stats = ensembles[uid].get(cond)
            if stats:
                oracle_str = "coll" if stats["oracle"] else "none"
                if stats["mean"] is not None:
                    parts.append(f" {stats['mean']:5.2f}+/-{stats['std']:4.2f}  ")
                else:
                    parts.append(f" {'N/A':^18}")
            else:
                parts.append(f" {'--':^18}")

        print(f"{uid:<45} {oracle_str:<8}" +
              "".join(parts[1:]))


# ============================================================================
# CLI argument parsing
# ============================================================================

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed argument namespace.
    """
    parser = argparse.ArgumentParser(
        description="VLM-as-judge evaluation pipeline for collision detection.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # Run with Gemini backend
  python vlm_evaluate.py --backend gemini --data_dir output_pilot

  # Run with NVIDIA NIM backend
  python vlm_evaluate.py --backend nvidia --api_key $NVIDIA_API_KEY

  # Resume an interrupted run
  python vlm_evaluate.py --backend gemini --resume

  # Only run analysis on existing results
  python vlm_evaluate.py --analyze_only --data_dir output_pilot

  # Run specific conditions and prompts
  python vlm_evaluate.py --backend gemini --conditions gt_video mode_1 --prompts P1 P3
        """,
    )

    parser.add_argument(
        "--data_dir", type=str, default="output_pilot",
        help="Root directory containing collision_labels.json and samples/. "
             "Default: output_pilot",
    )
    parser.add_argument(
        "--output_json", type=str, default=None,
        help="Path to write VLM results JSON. Default (evaluation): "
             "{data_dir}/vlm_results_<model>.json from --model. "
             "Default (--analyze_only): {data_dir}/vlm_results.json",
    )
    parser.add_argument(
        "--backend", type=str, choices=["nvidia", "gemini"], default=None,
        help="VLM backend to use. Required unless --analyze_only.",
    )
    parser.add_argument(
        "--api_key", type=str, default=None,
        help="API key. Falls back to NVIDIA_API_KEY or GEMINI_API_KEY env var.",
    )
    parser.add_argument(
        "--model", type=str, default=None,
        help="Model name. Defaults per backend: "
             f"nvidia={DEFAULT_NVIDIA_MODEL}, gemini={DEFAULT_GEMINI_MODEL}",
    )
    parser.add_argument(
        "--base_url", type=str, default=DEFAULT_NVIDIA_BASE_URL,
        help=f"NVIDIA NIM endpoint URL. Default: {DEFAULT_NVIDIA_BASE_URL}",
    )
    parser.add_argument(
        "--prompts", type=str, nargs="+", default=PROMPT_VARIANT_IDS,
        choices=PROMPT_VARIANT_IDS,
        help="Prompt variants to run. Default: all (P1-P5).",
    )
    parser.add_argument(
        "--conditions", type=str, nargs="+", default=list(CONDITION_MAP.keys()),
        choices=list(CONDITION_MAP.keys()),
        help="Evaluation conditions to run. Default: all four.",
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Skip sample/condition/prompt combos already in the output JSON.",
    )
    parser.add_argument(
        "--rate_limit", type=float, default=2.0,
        help="Minimum seconds between API calls. Default: 2.0",
    )
    parser.add_argument(
        "--analyze_only", action="store_true",
        help="Skip API calls; only run analysis. Default results path: "
             "{data_dir}/vlm_results.json unless --output_json is set.",
    )
    parser.add_argument(
        "--prompts_file", type=str, default="prompts",
        help="Python module name for prompt definitions (without .py). "
             "Default: prompts. Use 'prompts_2' for updated v2 prompts.",
    )

    args = parser.parse_args()

    # Resolve paths relative to script directory
    if not os.path.isabs(args.data_dir):
        args.data_dir = str(SCRIPT_DIR / args.data_dir)

    if args.output_json is not None and not os.path.isabs(args.output_json):
        args.output_json = str(SCRIPT_DIR / args.output_json)

    return args


# ============================================================================
# Entry point
# ============================================================================

def main() -> None:
    """Main entry point: parse args, run evaluation or analysis."""
    args = parse_args()

    # -- Load prompt module --
    prompt_mod = importlib.import_module(args.prompts_file)
    build_prompt = prompt_mod.build_prompt
    print(f"Prompts: loaded from {args.prompts_file}.py")

    # -- Analyze-only mode --
    if args.analyze_only:
        if args.output_json is None:
            args.output_json = os.path.join(args.data_dir, "vlm_results.json")
        if not os.path.exists(args.output_json):
            sys.exit(f"ERROR: Results file not found: {args.output_json}")
        print(f"Loading results from: {args.output_json}")
        results_data = load_results(args.output_json)
        n = len(results_data.get("results", []))
        print(f"Loaded {n} result entries.")
        compute_analysis(results_data)
        compute_prompt_sensitivity(results_data)
        print_per_sample_breakdown(results_data)
        return

    # -- Validate backend --
    if args.backend is None:
        sys.exit("ERROR: --backend is required (nvidia or gemini) unless --analyze_only.")

    # -- Resolve API key --
    api_key = args.api_key
    if api_key is None:
        env_var = "NVIDIA_API_KEY" if args.backend == "nvidia" else "GEMINI_API_KEY"
        api_key = os.environ.get(env_var)
        if not api_key:
            sys.exit(f"ERROR: No API key provided. Use --api_key or set {env_var}.")

    # -- Resolve model --
    model = args.model
    if model is None:
        model = DEFAULT_NVIDIA_MODEL if args.backend == "nvidia" else DEFAULT_GEMINI_MODEL

    if args.output_json is None:
        slug = sanitize_model_for_filename(model)
        args.output_json = os.path.join(args.data_dir, f"vlm_results_{slug}.json")

    # -- Create backend --
    if args.backend == "nvidia":
        backend = NvidiaBackend(api_key=api_key, model=model, base_url=args.base_url)
        backend_name = f"nvidia/{model}"
    else:
        backend = GeminiBackend(api_key=api_key, model=model)
        backend_name = f"gemini/{model}"

    print(f"Backend: {backend_name}")
    print(f"Data dir: {args.data_dir}")
    print(f"Output: {args.output_json}")
    print(f"Conditions: {args.conditions}")
    print(f"Prompts: {args.prompts}")
    print(f"Rate limit: {args.rate_limit}s")
    print(f"Resume: {args.resume}")

    # -- Run evaluation --
    results_data = run_evaluation(
        backend=backend,
        backend_name=backend_name,
        build_prompt=build_prompt,
        data_dir=args.data_dir,
        output_json=args.output_json,
        conditions=args.conditions,
        prompt_ids=args.prompts,
        rate_limit=args.rate_limit,
        resume=args.resume,
    )

    # -- Run analysis --
    compute_analysis(results_data)
    compute_prompt_sensitivity(results_data)
    print_per_sample_breakdown(results_data)


if __name__ == "__main__":
    main()

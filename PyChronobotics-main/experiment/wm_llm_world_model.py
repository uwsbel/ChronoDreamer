import os
import subprocess
import json
import time
import base64
import io
import urllib.request
import urllib.error
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import re

import numpy as np

try:
    from PIL import Image
except Exception:
    Image = None

try:
    import imageio.v2 as imageio
except Exception:
    imageio = None


LLM_PROMPT_TEMPLATE = """Do you think there is a collision happening between the manipulator and any of the objects on the table?
The camera is mounted on the arm of the manipulator.
You are a strict collision verifier.

You will be shown:
(1) History RGB frames (prompt)
(2) Predicted future RGB frames (generated)
(3) Predicted contact map (generated) — WARNING: this is noisy and often has false positives.

TASK
Decide if a collision happens between the manipulator/gripper and ANY table object.

DEFINITION
Output collision_likely=true ONLY if BOTH are true:
(A) In the predicted future RGB frames, the gripper/manipulator makes physically plausible contact with an object (not just overlaps in 2D).
(B) At least one of the following is visible in RGB:
(B1) The object moves/rotates/shifts relative to the table (displacement) compared to its pose in the last prompt frame.
(B2) The object deforms/deflects/compresses at the contact point (common for chains/FEA/deformables), even if its base pose does not translate.
(B3) There is sustained pushing/pressing contact across multiple future frames with no visible gap, even if the object is constrained/heavy and does not translate.

IMPORTANT RULES (to reduce false positives)
- Do NOT claim collision based only on the contact map. The contact map can be wrong.
- If the gripper crosses over an object in the image in 2D but there is a visible gap/clearance (no sustained contact), this is NOT a collision.
- If you cannot clearly see contact evidence in the predicted RGB frames (displacement, deformation/deflection, or sustained pressing contact), set collision_likely=false.
- Lack of object translation does NOT imply "no collision" when the object is constrained/heavy or deformable. In those cases, look for deformation/deflection or sustained pressing contact.
- If the yellow table seems becoming smaller, this likely means the arm/camera is lifting upward; lifting makes collision less likely. Prefer collision_likely=false unless there is clear contact evidence (displacement, deformation/deflection, or sustained pressing contact).
- Only give high confidence (>= 0.85) when contact evidence (displacement or deformation/deflection) is obvious and sustained across multiple future frames.
- If evidence is ambiguous or blurred, set collision_likely=false and confidence <= 0.5.

FEW-SHOT EXAMPLES (read carefully)
Example 1 (NO collision: high clearance pass-over)
- Predicted frames show the gripper moving "over" a block in 2D, but the block's pose does not change relative to the table.
- Even if the contact map lights up near the block, answer:
  {"collision_likely": false, "confidence": 0.3, "first_collision_frame": 0, "explanation": "Gripper passes above/near object; no visible displacement in RGB."}

Example 2 (NO collision: apparent motion from camera ego-motion)
- Camera moves with the arm; objects may appear to shift slightly due to viewpoint changes.
- If the object remains fixed relative to table edges/markers and there is no clear push/impact, answer:
  {"collision_likely": false, "confidence": 0.4, "first_collision_frame": 0, "explanation": "No clear object displacement; apparent changes likely from camera motion."}

Example 3 (YES collision: clear push)
- Gripper contacts a block and the block translates/rotates in a sustained way across multiple future frames.
- Answer:
  {"collision_likely": true, "confidence": 0.9, "first_collision_frame": 1, "explanation": "Contact with sustained object displacement visible in RGB."}

Example 4 (YES collision: constrained/heavy/deformable object)
- The gripper presses into a chain/beam/deformable object and you can see bending/compression/deflection at the contact point, even if the object does not translate.
- Answer:
  {"collision_likely": true, "confidence": 0.85, "first_collision_frame": 1, "explanation": "Sustained pressing contact with visible deformation/deflection in RGB."}

Inputs:
- Image 1: history RGB frames (prompt)
- Image 2: predicted future RGB frames (generated)
- Image 3: predicted future contact map (generated)

Return JSON only with the following schema:
{
  \"collision_likely\": true/false,
  \"confidence\": 0.0-1.0,
  \"first_collision_frame\": 0-7,
  \"explanation\": \"...\"
}
"""


@dataclass(frozen=True)
class GeminiConfig:
    model: str = "gemini-2.5-flash"
    api_key_env: str = "GEMINI_API_KEY"
    timeout_s: float = 20.0
    temperature: float = 0.0
    max_output_tokens: int = 1024


@dataclass(frozen=True)
class CollisionDecision:
    collision_likely: bool
    confidence: float
    first_collision_frame: int
    explanation: str
    raw_text: str


def _gemini_list_models(api_key: str, timeout_s: float = 10.0) -> dict:
    url = "https://generativelanguage.googleapis.com/v1beta/models"
    req = urllib.request.Request(
        url,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=float(timeout_s)) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def _extract_first_json_object(text: str) -> Optional[str]:
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return text[start : end + 1]


def _extract_first_json_object_balanced(text: str) -> Optional[str]:
    if not text:
        return None
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _normalize_model_name(model: str) -> str:
    m = (model or "").strip()
    if m.startswith("models/"):
        m = m[len("models/") :]
    return m


def _tile_frames(frames: List[np.ndarray], cols: int) -> np.ndarray:
    if not frames:
        raise ValueError("No frames")
    cols = max(1, int(cols))
    h, w = frames[0].shape[:2]
    rows = int(np.ceil(len(frames) / float(cols)))
    canvas = np.zeros((rows * h, cols * w, 3), dtype=np.uint8)
    for i, fr in enumerate(frames):
        r = i // cols
        c = i % cols
        fr3 = fr[..., :3]
        canvas[r * h : (r + 1) * h, c * w : (c + 1) * w] = fr3
    return canvas


def _encode_png_base64(rgb: np.ndarray) -> str:
    if Image is None:
        raise RuntimeError("PIL is required to encode images for LLM")
    buf = io.BytesIO()
    Image.fromarray(rgb).save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


class GeminiCollisionJudge:
    def __init__(self, config: GeminiConfig, prompt_template: str):
        self.config = config
        self.prompt_template = prompt_template

    def judge(
        self,
        history_frames: List[np.ndarray],
        pred_frames: List[np.ndarray],
        contact_frames: List[np.ndarray],
        debug_response_path: Optional[Path] = None,
    ) -> CollisionDecision:
        api_key = os.environ.get(self.config.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key env var {self.config.api_key_env}")

        model_name = _normalize_model_name(self.config.model)
        supports_json_mode = not model_name.startswith("gemma-")

        history_img = _tile_frames(history_frames, cols=4)
        pred_img = _tile_frames(pred_frames, cols=4)
        contact_img = _tile_frames(contact_frames, cols=4)

        text_prompt = self.prompt_template
        if not supports_json_mode:
            text_prompt = (
                text_prompt
                + "\n\nReturn ONLY a valid JSON object (no markdown fences, no preamble, no trailing text) with keys: "
                + "collision_likely (boolean), confidence (number 0..1), first_collision_frame (integer 0..7), explanation (string)."
            )

        parts = [
            {"text": text_prompt},
            {"inline_data": {"mime_type": "image/png", "data": _encode_png_base64(history_img)}},
            {"inline_data": {"mime_type": "image/png", "data": _encode_png_base64(pred_img)}},
            {"inline_data": {"mime_type": "image/png", "data": _encode_png_base64(contact_img)}},
        ]

        generation_config = {
            "temperature": float(self.config.temperature),
            "maxOutputTokens": int(self.config.max_output_tokens),
        }

        if supports_json_mode:
            response_schema = {
                "type": "object",
                "properties": {
                    "collision_likely": {"type": "boolean"},
                    "confidence": {"type": "number"},
                    "first_collision_frame": {"type": "integer"},
                    "explanation": {"type": "string"},
                },
                "required": ["collision_likely", "confidence", "first_collision_frame", "explanation"],
            }
            generation_config["responseMimeType"] = "application/json"
            generation_config["responseJsonSchema"] = response_schema

        payload = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": generation_config,
        }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=float(self.config.timeout_s)) as resp:
                resp_text = resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            if debug_response_path is not None:
                try:
                    Path(debug_response_path).write_text(body)
                except Exception:
                    pass
            raise RuntimeError(f"Gemini HTTPError {e.code}: {body}")
        except Exception as e:
            raise RuntimeError(f"Gemini request failed: {e}")

        if debug_response_path is not None:
            try:
                Path(debug_response_path).write_text(resp_text)
            except Exception:
                pass

        try:
            data = json.loads(resp_text)
        except Exception:
            raise RuntimeError(f"Gemini response was not JSON: {resp_text[:500]}")

        finish_reason = None
        try:
            finish_reason = data.get("candidates", [{}])[0].get("finishReason")
        except Exception:
            pass

        raw_text = ""
        try:
            parts_out = data["candidates"][0]["content"]["parts"]
            for p in parts_out:
                if "text" in p:
                    raw_text += p["text"]
        except Exception:
            raw_text = ""

        obj = None
        parse_err = None
        if raw_text:
            try:
                obj = json.loads(raw_text)
            except Exception as e:
                parse_err = e

        if obj is None:
            cleaned = raw_text.replace("```json", "```").replace("```", "")
            jtxt = _extract_first_json_object_balanced(cleaned)
            if jtxt is None:
                raise RuntimeError(
                    f"Gemini did not return a JSON object. finishReason={finish_reason}. Raw: {raw_text}"
                )
            try:
                obj = json.loads(jtxt)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to parse Gemini JSON. finishReason={finish_reason}. "
                    f"first_err={parse_err}. err={e}. Raw: {raw_text}"
                )

        collision_likely = bool(obj.get("collision_likely"))
        confidence = float(obj.get("confidence", 0.0))
        first_collision_frame = int(obj.get("first_collision_frame", 0))
        explanation = str(obj.get("explanation", ""))
        return CollisionDecision(
            collision_likely=collision_likely,
            confidence=confidence,
            first_collision_frame=first_collision_frame,
            explanation=explanation,
            raw_text=raw_text,
        )


class WorldModelRunner:
    def __init__(
        self,
        output_root: str,
        camera_dir: str,
        checkpoint_dir: str,
        start_time: float = 10.0,
        period: float = 5.0,
        stride: int = 15,
        venv_python: Optional[str] = None,
        llm_enabled: bool = False,
        llm_model: str = "gemini-2.5-flash",
        llm_timeout_s: float = 20.0,
        llm_temperature: float = 0.0,
        llm_max_output_tokens: int = 1024,
        llm_max_attempts: int = 3,
        llm_use_contact_map: bool = True,
        llm_reject_confidence: float = 0.9,
        llm_prompt_file: Optional[str] = None,
        llm_prompt_template: Optional[str] = None,
        context_globals: Optional[dict] = None,
    ):
        self.output_root = Path(output_root).resolve()
        self.camera_dir = Path(camera_dir).resolve()
        self.checkpoint_dir = checkpoint_dir
        self.start_time = float(start_time)
        self.period = float(period)
        self.stride = int(stride)
        self.next_time = float(start_time)
        self.proc = None
        self._planned_actions = None
        self._planned_action_idx = 0
        self._pending_runs = []
        self._walltime_start = time.time()
        self._camera_mtime_floor = self._walltime_start - 5.0
        self.llm_enabled = bool(llm_enabled)
        self.llm_max_attempts = int(llm_max_attempts)
        self.llm_use_contact_map = bool(llm_use_contact_map)
        self.llm_reject_confidence = float(llm_reject_confidence)
        self._in_planning = False
        self._context_globals = context_globals if context_globals is not None else {}

        prompt_template = LLM_PROMPT_TEMPLATE
        if llm_prompt_template is not None:
            prompt_template = str(llm_prompt_template)
        if llm_prompt_file:
            try:
                prompt_template = Path(llm_prompt_file).read_text()
            except Exception:
                pass
        self._collision_judge = None
        if self.llm_enabled:
            self._collision_judge = GeminiCollisionJudge(
                GeminiConfig(
                    model=str(llm_model),
                    timeout_s=float(llm_timeout_s),
                    temperature=float(llm_temperature),
                    max_output_tokens=int(llm_max_output_tokens),
                ),
                prompt_template=prompt_template,
            )

        self.chronodreamer_root = Path(__file__).resolve().parents[2]
        self.one_xgpt_dir = self.chronodreamer_root / "1xgpt"
        self.inference_script = self.one_xgpt_dir / "inference_from_sim.py"

        if venv_python is None:
            venv_python = str(self.one_xgpt_dir / "venv" / "bin" / "python")
        self.venv_python = venv_python

        self.output_root.mkdir(parents=True, exist_ok=True)

    def pop_next_planned_action(self):
        if self._planned_actions is None:
            return None
        if self._planned_action_idx >= len(self._planned_actions):
            self._planned_actions = None
            self._planned_action_idx = 0
            return None
        a = self._planned_actions[self._planned_action_idx]
        self._planned_action_idx += 1
        return a

    def _read_gif_frames(self, gif_path: Path):
        if not gif_path.exists():
            return None
        if imageio is None:
            return None
        try:
            frames = imageio.mimread(str(gif_path))
            return frames
        except Exception:
            return None

    def _write_gif(self, frames, out_path: Path, fps: int = 2):
        if not frames:
            return
        duration_ms = int(round(1000.0 / float(fps)))
        if Image is not None:
            pil_frames = []
            for fr in frames:
                if isinstance(fr, np.ndarray):
                    pil_frames.append(Image.fromarray(fr))
                else:
                    pil_frames.append(fr)
            pil_frames[0].save(
                str(out_path),
                format="GIF",
                append_images=pil_frames[1:],
                save_all=True,
                duration=duration_ms,
                loop=0,
            )
            return
        if imageio is not None:
            imageio.mimsave(str(out_path), frames, duration=duration_ms / 1000.0)

    def _maybe_finalize_pending(self):
        if not self._pending_runs:
            return
        image_files = self._list_image_files()
        if not image_files:
            return
        remaining = []
        for item in self._pending_runs:
            run_dir = item.get("run_dir")
            window_inds = item.get("window_inds")
            if run_dir is None or window_inds is None:
                continue
            max_ind = int(max(window_inds))
            if max_ind >= len(image_files):
                remaining.append(item)
                continue
            pred_gif = Path(run_dir) / "generated_offset0.gif"
            pred_frames = self._read_gif_frames(pred_gif)
            if pred_frames is None:
                remaining.append(item)
                continue
            gt_gif = Path(run_dir) / "ground_truth_offset0.gif"
            combo_gif = Path(run_dir) / "gt_vs_pred_offset0.gif"
            if combo_gif.exists() and gt_gif.exists():
                continue
            gt_frames = []
            try:
                for idx in window_inds:
                    gt_frames.append(self._load_rgb(image_files[int(idx)]))
            except Exception:
                remaining.append(item)
                continue
            self._write_gif(gt_frames, gt_gif, fps=2)
            if Image is None:
                remaining.append(item)
                continue
            combo_frames = []
            for i in range(min(len(gt_frames), len(pred_frames))):
                left = Image.fromarray(gt_frames[i])
                right = Image.fromarray(pred_frames[i])
                h = max(left.size[1], right.size[1])
                if left.size[1] != h:
                    padded = Image.new("RGB", (left.size[0], h), "white")
                    padded.paste(left, (0, h - left.size[1]))
                    left = padded
                if right.size[1] != h:
                    padded = Image.new("RGB", (right.size[0], h), "white")
                    padded.paste(right, (0, h - right.size[1]))
                    right = padded
                combined = Image.new("RGB", (left.size[0] + right.size[0], h), "white")
                combined.paste(left, (0, 0))
                combined.paste(right, (left.size[0], 0))
                combo_frames.append(combined)
            self._write_gif(combo_frames, combo_gif, fps=2)
        self._pending_runs = remaining

    def _list_image_files(self) -> List[str]:
        if not self.camera_dir.exists():
            return []
        exts = (".png", ".jpg", ".jpeg", ".bmp")
        files = []
        for f in os.listdir(self.camera_dir):
            p = self.camera_dir / f
            if not (os.path.isfile(p) and f.lower().endswith(exts)):
                continue
            try:
                if p.stat().st_mtime < self._camera_mtime_floor:
                    continue
            except Exception:
                continue
            files.append(f)

        def _key(name: str):
            m = re.search(r"frame_(\d+)", name)
            if m is not None:
                try:
                    return int(m.group(1))
                except Exception:
                    pass
            base = os.path.basename(name)
            nums = re.findall(r"\d+", base)
            if nums:
                try:
                    return int(nums[-1])
                except Exception:
                    return base
            return base

        files.sort(key=_key)
        return [str(self.camera_dir / f) for f in files]

    def _load_rgb(self, path: str) -> np.ndarray:
        if Image is not None:
            img = Image.open(path).convert("RGB")
            if img.size != (256, 256):
                img = img.resize((256, 256))
            return np.asarray(img, dtype=np.uint8)
        if imageio is not None:
            arr = imageio.imread(path)
            if arr.ndim == 2:
                arr = np.stack([arr, arr, arr], axis=-1)
            if arr.shape[-1] == 4:
                arr = arr[..., :3]
            if arr.shape[0] != 256 or arr.shape[1] != 256:
                raise RuntimeError(f"Unexpected image shape {arr.shape} for {path}")
            return arr.astype(np.uint8, copy=False)
        raise RuntimeError("Neither PIL nor imageio is available to load camera frames")

    def maybe_launch(self, sim_time: float, actions_hist: List[np.ndarray], joints_hist: List[np.ndarray]):
        self._maybe_finalize_pending()
        if sim_time < self.next_time:
            return

        if self.llm_enabled:
            if self._in_planning:
                return
            self._in_planning = True
            try:
                self._plan_with_llm_gate(sim_time, actions_hist, joints_hist)
            finally:
                self._in_planning = False
            return

        if not os.path.isfile(self.venv_python):
            print(f"World model disabled: venv python not found at {self.venv_python}")
            self.next_time = sim_time + self.period
            return

        if not self.inference_script.exists():
            print(f"World model disabled: inference script not found at {self.inference_script}")
            self.next_time = sim_time + self.period
            return

        if self.proc is not None and self.proc.poll() is None:
            print(f"World model inference still running at t={sim_time:.2f}, skipping t={self.next_time:.2f}")
            self.next_time += self.period
            return

        num_prompt = 8
        window_size = 16
        num_future = window_size - num_prompt
        needed = (num_prompt - 1) * self.stride + 1

        image_files = self._list_image_files()
        n = min(len(image_files), len(actions_hist), len(joints_hist))
        if n < needed:
            print(f"Not enough history for world model at t={sim_time:.2f}: have {n}, need {needed}")
            self.next_time += self.period
            return

        prompt_end_idx = n - 1
        prompt_start_idx = prompt_end_idx - (num_prompt - 1) * self.stride
        prompt_inds = [prompt_start_idx + i * self.stride for i in range(num_prompt)]

        try:
            prompt_frames = [self._load_rgb(image_files[i]) for i in prompt_inds]
        except Exception as e:
            print(f"Failed to load history frames for world model: {e}")
            self.next_time += self.period
            return

        last_frame = prompt_frames[-1]
        frames_np = np.stack(prompt_frames + [last_frame] * num_future, axis=0).astype(np.uint8)

        prompt_actions = [actions_hist[i] for i in prompt_inds]
        prompt_joints = [joints_hist[i] for i in prompt_inds]

        plan_hz = 25
        plan_steps = int(round(self.period * plan_hz))
        ou = self._context_globals.get("ou_process", None)
        if ou is None:
            self._planned_actions = None
            self._planned_action_idx = 0
            last_action = np.array(prompt_actions[-1], dtype=np.float32)
            planned_actions = [last_action.copy() for _ in range(plan_steps)]
        else:
            planned_actions = []
            for _ in range(plan_steps):
                a = ou.sample()
                axis_x_f = float(a[0])
                axis_y_f = float(a[1])
                axis_right_y_f = float(a[2])
                deadzone = 0.1
                if abs(axis_x_f) < deadzone:
                    axis_x_f = 0.0
                if abs(axis_y_f) < deadzone:
                    axis_y_f = 0.0
                if abs(axis_right_y_f) < deadzone:
                    axis_right_y_f = 0.0
                planned_actions.append(np.array([axis_x_f, axis_y_f, axis_right_y_f], dtype=np.float32))
            self._planned_actions = planned_actions
            self._planned_action_idx = 0

        max_needed = self.stride * num_future
        if len(planned_actions) < max_needed:
            planned_actions = planned_actions + [planned_actions[-1].copy()] * (max_needed - len(planned_actions))
        future_actions = [planned_actions[i * self.stride - 1].copy() for i in range(1, num_future + 1)]

        ik = self._context_globals.get("IK_solver", None)
        move_speed = self._context_globals.get("movement_speed", None)
        desired_pos_global = self._context_globals.get("desired_position", None)
        last_j = np.array(prompt_joints[-1], dtype=np.float32)
        if ik is None or move_speed is None or desired_pos_global is None:
            future_joints = [last_j.copy() for _ in range(num_future)]
        else:
            desired_pos = np.array(desired_pos_global, dtype=np.float64).copy()
            joint_guess = last_j.astype(np.float64, copy=True)
            joints_25hz = []
            printed_ik_error = False
            for a in planned_actions[:max_needed]:
                axis_x_f, axis_y_f, axis_right_y_f = [float(x) for x in a]
                if sim_time > 5:
                    desired_pos[0] += axis_x_f * float(move_speed)
                    desired_pos[1] += -axis_y_f * float(move_speed)
                    desired_pos[2] += -axis_right_y_f * float(move_speed)
                    desired_pos[0] = float(np.clip(desired_pos[0], -0.4, 0.4))
                    desired_pos[1] = float(np.clip(desired_pos[1], 0.45, 0.95))
                    desired_pos[2] = float(np.clip(desired_pos[2], -0.15, 0.3))
                try:
                    joint_guess = np.array(
                        ik.inverse_kinematics_solver(desired_pos, joint_guess),
                        dtype=np.float64,
                    )
                except Exception:
                    if not printed_ik_error:
                        print(f"[world_model] IK rollout failed during future joint forecast at t={sim_time:.2f}")
                        printed_ik_error = True
                joints_25hz.append(joint_guess.astype(np.float32, copy=True))
            future_joints = [joints_25hz[i * self.stride - 1].copy() for i in range(1, num_future + 1)]

        actions_np = np.stack(prompt_actions + future_actions, axis=0).astype(np.float32)
        actions_np = np.clip(actions_np, -1.0, 1.0)
        joints_np = np.stack(prompt_joints + future_joints, axis=0).astype(np.float32)

        run_dir = (self.output_root / f"t_{int(round(self.next_time))}s").resolve()
        run_dir.mkdir(parents=True, exist_ok=True)

        try:
            window_inds = [prompt_start_idx + i * self.stride for i in range(window_size)]
            prompt_meta = []
            for i in prompt_inds:
                p = image_files[int(i)]
                entry = {"idx": int(i), "path": str(p)}
                try:
                    entry["mtime"] = float(Path(p).stat().st_mtime)
                except Exception:
                    pass
                cam_csv = self.camera_dir.parent / "camera" / f"camera_{int(i):04d}.csv"
                if cam_csv.exists():
                    try:
                        lines = cam_csv.read_text().splitlines()
                        if len(lines) >= 2:
                            vals = lines[1].split(",")
                            if vals:
                                entry["camera_sim_time"] = float(vals[0])
                    except Exception:
                        pass
                prompt_meta.append(entry)

            debug = {
                "sim_time": float(sim_time),
                "stride": int(self.stride),
                "num_prompt_frames": int(num_prompt),
                "window_size": int(window_size),
                "n_used": int(n),
                "num_images": int(len(image_files)),
                "num_actions": int(len(actions_hist)),
                "num_joints": int(len(joints_hist)),
                "prompt_start_idx": int(prompt_start_idx),
                "prompt_end_idx": int(prompt_end_idx),
                "prompt_inds": [int(x) for x in prompt_inds],
                "window_inds": [int(x) for x in window_inds],
                "prompt": prompt_meta,
            }
            (run_dir / "sampling_debug.json").write_text(json.dumps(debug, indent=2))
        except Exception:
            pass

        frames_path = (run_dir / "frames.npy").resolve()
        actions_path = (run_dir / "actions.npy").resolve()
        joints_path = (run_dir / "joint_angles.npy").resolve()

        np.save(frames_path, frames_np)
        np.save(actions_path, actions_np)
        np.save(joints_path, joints_np)

        window_inds = [prompt_start_idx + i * self.stride for i in range(window_size)]
        self._pending_runs.append({"run_dir": str(run_dir), "window_inds": window_inds})

        cmd = [
            self.venv_python,
            str(self.inference_script),
            "--frames_path",
            str(frames_path),
            "--actions_path",
            str(actions_path),
            "--joint_angles_path",
            str(joints_path),
            "--output_dir",
            str(run_dir),
            "--checkpoint_dir",
            self.checkpoint_dir,
        ]

        stdout_path = run_dir / "inference_stdout.txt"
        stderr_path = run_dir / "inference_stderr.txt"
        with open(stdout_path, "w") as out_f, open(stderr_path, "w") as err_f:
            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            self.proc = subprocess.Popen(cmd, cwd=str(self.one_xgpt_dir), stdout=out_f, stderr=err_f, env=env)

        print(f"Launched world model inference for t={self.next_time:.2f} -> {run_dir}")
        self.next_time += self.period

    def _run_inference_blocking(self, run_dir: Path, frames_np: np.ndarray, actions_np: np.ndarray, joints_np: np.ndarray) -> bool:
        frames_path = (run_dir / "frames.npy").resolve()
        actions_path = (run_dir / "actions.npy").resolve()
        joints_path = (run_dir / "joint_angles.npy").resolve()
        np.save(frames_path, frames_np)
        np.save(actions_path, actions_np)
        np.save(joints_path, joints_np)

        cmd = [
            self.venv_python,
            str(self.inference_script),
            "--frames_path",
            str(frames_path),
            "--actions_path",
            str(actions_path),
            "--joint_angles_path",
            str(joints_path),
            "--output_dir",
            str(run_dir),
            "--checkpoint_dir",
            self.checkpoint_dir,
        ]

        stdout_path = run_dir / "inference_stdout.txt"
        stderr_path = run_dir / "inference_stderr.txt"
        with open(stdout_path, "w") as out_f, open(stderr_path, "w") as err_f:
            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            res = subprocess.run(cmd, cwd=str(self.one_xgpt_dir), stdout=out_f, stderr=err_f, env=env)
        return res.returncode == 0

    def _load_predicted_media(self, run_dir: Path):
        pred_gif = run_dir / "generated_offset0.gif"
        contact_gif = run_dir / "contact_offset0.gif"
        pred_frames = self._read_gif_frames(pred_gif)
        contact_frames = self._read_gif_frames(contact_gif)
        if pred_frames is None or contact_frames is None:
            raise RuntimeError("Missing generated/contact GIFs")
        if len(pred_frames) < 16:
            raise RuntimeError(f"Expected >=16 frames in {pred_gif}, got {len(pred_frames)}")
        if len(contact_frames) < 8:
            raise RuntimeError(f"Expected >=8 frames in {contact_gif}, got {len(contact_frames)}")
        history = [np.asarray(fr)[..., :3].astype(np.uint8) for fr in pred_frames[:8]]
        future = [np.asarray(fr)[..., :3].astype(np.uint8) for fr in pred_frames[8:16]]
        contact = [np.asarray(fr)[..., :3].astype(np.uint8) for fr in contact_frames[:8]]
        return history, future, contact

    def _fallback_retract_up(self, plan_steps: int) -> List[np.ndarray]:
        a = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        return [a.copy() for _ in range(int(plan_steps))]

    def _plan_with_llm_gate(self, sim_time: float, actions_hist: List[np.ndarray], joints_hist: List[np.ndarray]):
        if self._collision_judge is None:
            self.next_time += self.period
            return

        num_prompt = 8
        window_size = 16
        num_future = window_size - num_prompt
        needed = (num_prompt - 1) * self.stride + 1
        image_files = self._list_image_files()
        n = min(len(image_files), len(actions_hist), len(joints_hist))
        if n < needed:
            print(f"Not enough history for LLM-gated planning at t={sim_time:.2f}: have {n}, need {needed}")
            self.next_time += self.period
            return

        prompt_end_idx = n - 1
        prompt_start_idx = prompt_end_idx - (num_prompt - 1) * self.stride
        prompt_inds = [prompt_start_idx + i * self.stride for i in range(num_prompt)]

        prompt_frames = [self._load_rgb(image_files[i]) for i in prompt_inds]
        last_frame = prompt_frames[-1]
        frames_np = np.stack(prompt_frames + [last_frame] * num_future, axis=0).astype(np.uint8)
        prompt_actions = [actions_hist[i] for i in prompt_inds]
        prompt_joints = [joints_hist[i] for i in prompt_inds]

        plan_hz = 25
        plan_steps = int(round(self.period * plan_hz))
        max_needed = self.stride * num_future
        ou = self._context_globals.get("ou_process", None)
        ik = self._context_globals.get("IK_solver", None)
        move_speed = self._context_globals.get("movement_speed", None)
        action_scale = self._context_globals.get("control_action_scale", 1.0)
        deadzone = self._context_globals.get("control_deadzone", 0.1)
        control_start_time = self._context_globals.get("control_start_time", 0.0)
        desired_pos_global = self._context_globals.get("desired_position", None)
        last_j = np.array(prompt_joints[-1], dtype=np.float32)

        base_dir = (self.output_root / f"t_{int(round(self.next_time))}s").resolve()
        base_dir.mkdir(parents=True, exist_ok=True)
        attempts_log = []

        accepted_plan = None
        accepted_attempt = None
        for attempt in range(max(1, self.llm_max_attempts)):
            run_dir = (base_dir / f"attempt_{attempt}").resolve()
            run_dir.mkdir(parents=True, exist_ok=True)

            planned_actions = []
            if ou is None:
                last_action = np.array(prompt_actions[-1], dtype=np.float32)
                planned_actions = [last_action.copy() for _ in range(plan_steps)]
            else:
                for _ in range(plan_steps):
                    a = ou.sample()
                    axis_x_f = float(a[0])
                    axis_y_f = float(a[1])
                    axis_right_y_f = float(a[2])
                    if abs(axis_x_f) < deadzone:
                        axis_x_f = 0.0
                    if abs(axis_y_f) < deadzone:
                        axis_y_f = 0.0
                    if abs(axis_right_y_f) < deadzone:
                        axis_right_y_f = 0.0

                    axis_x_f *= float(action_scale)
                    axis_y_f *= float(action_scale)
                    axis_right_y_f *= float(action_scale)
                    planned_actions.append(np.array([axis_x_f, axis_y_f, axis_right_y_f], dtype=np.float32))

            if len(planned_actions) < max_needed:
                planned_actions = planned_actions + [planned_actions[-1].copy()] * (max_needed - len(planned_actions))
            future_actions = [planned_actions[i * self.stride - 1].copy() for i in range(1, num_future + 1)]
            if ik is None or move_speed is None or desired_pos_global is None:
                future_joints = [last_j.copy() for _ in range(num_future)]
            else:
                desired_pos = np.array(desired_pos_global, dtype=np.float64).copy()
                joint_guess = last_j.astype(np.float64, copy=True)
                joints_25hz = []
                for a in planned_actions[:max_needed]:
                    axis_x_f, axis_y_f, axis_right_y_f = [float(x) for x in a]
                    if sim_time > float(control_start_time):
                        desired_pos[0] += axis_x_f * float(move_speed)
                        desired_pos[1] += -axis_y_f * float(move_speed)
                        desired_pos[2] += -axis_right_y_f * float(move_speed)
                        desired_pos[0] = float(np.clip(desired_pos[0], -0.4, 0.4))
                        desired_pos[1] = float(np.clip(desired_pos[1], 0.45, 0.95))
                        desired_pos[2] = float(np.clip(desired_pos[2], -0.15, 0.3))
                    try:
                        joint_guess = np.array(
                            ik.inverse_kinematics_solver(desired_pos, joint_guess),
                            dtype=np.float64,
                        )
                    except Exception:
                        pass
                    joints_25hz.append(joint_guess.astype(np.float32, copy=True))
                future_joints = [joints_25hz[i * self.stride - 1].copy() for i in range(1, num_future + 1)]

            actions_np = np.stack(prompt_actions + future_actions, axis=0).astype(np.float32)
            actions_np = np.clip(actions_np, -1.0, 1.0)
            joints_np = np.stack(prompt_joints + future_joints, axis=0).astype(np.float32)

            ok = self._run_inference_blocking(run_dir, frames_np, actions_np, joints_np)
            if not ok:
                attempts_log.append({"attempt": attempt, "status": "inference_failed"})
                continue

            try:
                hist_rgb, fut_rgb, fut_contact = self._load_predicted_media(run_dir)
            except Exception as e:
                attempts_log.append({"attempt": attempt, "status": f"media_failed: {e}"})
                continue

            if not self.llm_use_contact_map:
                fut_contact = [np.zeros_like(fr) for fr in fut_contact]

            try:
                decision = self._collision_judge.judge(
                    hist_rgb,
                    fut_rgb,
                    fut_contact,
                    debug_response_path=(run_dir / "gemini_response.json"),
                )
            except Exception as e:
                attempts_log.append({"attempt": attempt, "status": f"llm_failed: {e}"})
                continue

            (run_dir / "llm_decision.json").write_text(
                json.dumps(
                    {
                        "collision_likely": decision.collision_likely,
                        "confidence": decision.confidence,
                        "first_collision_frame": decision.first_collision_frame,
                        "explanation": decision.explanation,
                        "raw_text": decision.raw_text,
                    },
                    indent=2,
                )
            )

            attempts_log.append(
                {
                    "attempt": attempt,
                    "status": "collision" if decision.collision_likely else "safe",
                    "confidence": decision.confidence,
                    "first_collision_frame": decision.first_collision_frame,
                }
            )

            reject = bool(decision.collision_likely) and float(decision.confidence) >= float(self.llm_reject_confidence)
            if not reject:
                accepted_plan = planned_actions[:plan_steps]
                accepted_attempt = attempt
                break

        if accepted_plan is None:
            accepted_plan = self._fallback_retract_up(plan_steps)
            accepted_attempt = None

        self._planned_actions = accepted_plan
        self._planned_action_idx = 0

        (base_dir / "planning_log.json").write_text(
            json.dumps(
                {
                    "sim_time": float(sim_time),
                    "accepted_attempt": accepted_attempt,
                    "max_attempts": int(self.llm_max_attempts),
                    "reject_confidence": float(self.llm_reject_confidence),
                    "fallback": accepted_attempt is None,
                    "attempts": attempts_log,
                },
                indent=2,
            )
        )
        self.next_time += self.period

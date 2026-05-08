"""
Prompt definitions for VLM-as-judge collision evaluation (v8).
 
Changes from prompts_7.py (v7):
  - REMOVED all contact visualization support (CONTACT_ADDENDUM, has_contact
    parameter). Evaluation is now RGB-only.
  - RECENTERED RUBRIC: 1-5 scale now symmetric around 3 (uncertain).
    1 = confidently no collision, 3 = genuinely uncertain, 5 = confident
    collision. This eliminates the positive skew that inflated false
    positives on imbalanced (mostly no-collision) datasets.
  - PHYSICAL CONSISTENCY: Added requirement that collision evidence must
    be temporally coherent across frames. Flickering, snapping, or
    randomly appearing/disappearing items are prediction artifacts, not
    collision evidence.
  - DEGRADED FRAME SKEPTICISM: When FUTURE frames are noticeably blurrier
    or noisier than CONTEXT frames, the VLM must apply extra skepticism
    and require stronger evidence before scoring above 3.
  - FEW-SHOT EXAMPLES: Added Example 6 (prediction artifact) to
    reinforce the physical consistency rule.
 
Edit the string constants below to modify prompt wording. The evaluation script
(vlm_evaluate.py) imports only build_prompt() from this module.
"""
 
 
# ============================================================================
# Common header -- shared by all prompt variants
# ============================================================================
 
COMMON_HEADER = """\
You are evaluating a robotic manipulation sequence for \
physical contact between the manipulator and items on a \
table.
 
SCENE: A robot arm with a manipulator and various items \
(colored bars, cylinders, containers) on a tabletop. You \
are shown 16 frames arranged left to right in time order: \
the first 8 are CONTEXT (recent history), the last 8 are \
FUTURE (predicted continuation). The CONTEXT frames are \
ground-truth simulation output and can be used as a \
reliable reference for the scene layout — use them to \
identify what items are present and their approximate \
arrangement. Visual clarity may vary in the FUTURE frames \
— focus on physical evidence (item displacement, relative \
motion, local deformation) rather than image sharpness when \
evaluating collision.
Evaluate ONLY the FUTURE frames (9–16) for collision.
 
CAMERA: The camera is mounted on the robot arm (ego view, \
looking downward). Because the camera moves with the arm, \
ALL items will appear to shift between frames due to camera \
motion alone — this is NOT collision. To detect real \
collision, check whether items move RELATIVE TO EACH OTHER:
  • If all items shift together and maintain their relative \
arrangement → camera motion only, no collision.
  • If some items move while others stay put, or items \
spread apart / scatter relative to each other → real \
displacement, likely collision.
 
WHAT COUNTS AS COLLISION:
  • ONLY manipulator-to-item contact counts. Item-to-item \
or item-to-table contact does NOT count.
  • Movement, deformation, or shape change must occur CLOSE \
TO the manipulator to count as evidence. Items shifting on \
the far side of the table, away from the manipulator, are \
not evidence of manipulator collision.
  • Items may already be scattered from earlier interactions. \
A messy scene does NOT indicate collision — look for NEW \
relative movement or new local deformation within frames \
9–16 only.
  • Contact may occur between shown frames. If items near \
the manipulator appear suddenly displaced or deformed \
without a visible contact moment, collision likely occurred \
between frames.
  • If the table appears to shrink or recede, the arm is \
lifting — collision is less likely.
  • A high-clearance pass-through is NOT a collision. If the \
manipulator passes above, around, or past an item with \
visible separation and the item shows no new displacement, \
rotation, bending, compression, or deformation, score it \
as no collision even if the motion looks close in the 2D \
image.
 
PHYSICAL CONSISTENCY:
  • Collision evidence must be PHYSICALLY CONSISTENT across \
frames. Real displacement follows a smooth trajectory — an \
item pushed in frame 10 should continue moving in frames \
11–12, not snap back or vanish.
  • If items flicker between positions, change shape \
randomly, or appear / disappear between frames, this is a \
prediction artifact, NOT collision evidence.
  • Random blur, noise, or frame-to-frame inconsistency in \
the FUTURE frames is NOT evidence of collision. Only \
spatially coherent, temporally sustained displacement or \
deformation counts.
 
DEGRADED FUTURE FRAMES: If the FUTURE frames appear \
noticeably blurrier, noisier, or less visually coherent \
than the CONTEXT frames, apply EXTRA skepticism — require \
even clearer physical evidence before scoring above 3, \
since visual artifacts can mimic the appearance of motion \
or deformation."""
 
 
# ============================================================================
# Few-shot examples -- appended for all prompt variants
# ============================================================================
 
FEW_SHOT_EXAMPLES = """\
 
EXAMPLES:
 
Example 1 — no object response (score 1):
The manipulator moves over or very near an item, but the \
item's pose does not change relative to the table or other \
nearby references. No displacement, rotation, or deformation \
is visible. Score: 1.
 
Example 2 — camera-motion-only appearance (score 1–2):
All objects shift together in the frame due to the ego-mounted \
camera moving with the arm. No item moves relative to other \
items. The scene layout is preserved. Score: 1 if clearly \
uniform motion, 2 if slight ambiguity.
 
Example 3 — rigid-object displacement (score 4–5):
The manipulator contacts a block, and the block shows new \
translation or rotation across multiple future frames relative \
to the table and nearby items. The displacement is sustained \
and physically smooth. Score: 4 if clear, 5 if strong impact.
 
Example 4 — deformable-object deflection (score 4–5):
The manipulator presses into a beam or deformable object, and \
you can see local bending, compression, or deflection at or \
near the contact point, even if the object does not translate \
across the table. Sustained deformation is collision evidence. \
Score: 4 if visible, 5 if pronounced.
 
Example 5 — apparent overlap in 2D (score 1–2):
The manipulator passes near an item's silhouette in the image, \
but there is visible clearance and the item shows no new \
displacement, rotation, or deformation. 2D overlap alone is \
NOT collision. Score: 1 if clear separation, 2 if ambiguous.
 
Example 6 — prediction artifact (score 2–3):
The FUTURE frames are blurry or noisy. Items appear to flicker \
between positions or change shape inconsistently between \
consecutive frames. This is NOT evidence of collision — it is \
a prediction artifact. Real collision produces smooth, \
sustained displacement, not random frame-to-frame jitter. \
Score: 2 if mostly artifact, 3 if genuinely uncertain whether \
real motion is also present.
"""
 
 
# ============================================================================
# Recentered rubric text -- used by P1, P3, P4
# ============================================================================
 
RUBRIC_CENTERED = """\
Rate on a 1–5 scale:
5 = Confidently collision — clear, sustained item \
displacement or deformation caused by manipulator across \
multiple frames.
4 = Probably collision — visible item displacement or \
deformation near manipulator, but some ambiguity remains.
3 = Uncertain — cannot confidently determine whether \
collision occurred. Evidence is ambiguous, noisy, or \
contradictory, scenario is inconsistent.
2 = Probably no collision — minor ambiguous motion near \
manipulator but no clear item response.
1 = Confidently no collision — items maintain stable \
relative positions, only camera motion visible."""
 
 
# ============================================================================
# Output instruction -- appended to P1, P3, P4
# ============================================================================
 
OUTPUT_INSTRUCTION_STANDARD = """
Respond with ONLY this JSON, no other text:
{
  "score": <integer 1-5>,
  "reasoning": "<2-3 sentences of visual evidence>"
}"""
 
 
# ============================================================================
# P1: Baseline (standard rubric-based direct assessment)
# ============================================================================
 
P1_BODY = f"""\
 
{RUBRIC_CENTERED}"""
 
 
# ============================================================================
# P2: Evidence-first (explicit evidence extraction before scoring)
# ============================================================================
 
P2_BODY = f"""\
 
Before scoring, analyze the future frames (frames 9–16):
 
Step 1: Describe the manipulator's trajectory — is it moving \
toward, away from, or parallel to any item?
 
Step 2: List any signs of physical contact — item \
displacement, orientation change, manipulator-item overlap, \
local bending / compression / deformation, or sudden motion \
changes. For each sign, assess whether it is physically \
consistent across frames or could be a prediction artifact.
 
Step 3: Assess how clear and sustained the evidence is.
 
Then assign a score:
{RUBRIC_CENTERED}
 
Respond with ONLY this JSON:
{{
  "trajectory": "<1 sentence on manipulator movement>",
  "contact_signs": "<1-2 sentences on evidence>",
  "clarity": "<1 sentence on certainty>",
  "score": <integer 1-5>,
  "reasoning": "<1 sentence summary>"
}}"""
 
 
# ============================================================================
# P3: Conservative (instructed to avoid high scores without clear evidence)
# ============================================================================
 
P3_BODY = f"""\
 
{RUBRIC_CENTERED}
 
IMPORTANT: Assign a score of 4 or 5 ONLY if the collision \
evidence is visually unambiguous AND physically consistent \
across multiple frames — you can clearly see the manipulator \
causing a sustained local physical effect on the item \
(displacement, rotation, bending, compression, indentation, \
or deformation). If there is any doubt or the evidence could \
be a prediction artifact, score 3 or below."""
 
 
# ============================================================================
# P4: Strict future-only (emphasizes temporal boundary)
# ============================================================================
 
P4_BODY = f"""\
 
CRITICAL: The context frames (1–8) are provided ONLY for \
understanding the scene setup and the robot's approach \
trajectory. Do NOT consider any contact or collision that \
may appear in the context frames.
 
Focus exclusively on the future frames (9–16). Ask yourself: \
within these 8 frames specifically, does the robot's manipulator \
make new physical contact with any item, causing new displacement \
or deformation that is sustained and physically consistent \
across frames?
 
{RUBRIC_CENTERED}"""
 
 
# ============================================================================
# P5: Counterfactual verification (boundary stability check)
# ============================================================================
 
P5_BODY = f"""\
 
{RUBRIC_CENTERED}
 
After choosing your score, briefly state what visual evidence \
would need to be ABSENT for your score to drop by one level. \
This helps verify your score is at the right level.
 
Respond with ONLY this JSON:
{{
  "score": <integer 1-5>,
  "reasoning": "<2 sentences of visual evidence>",
  "if_absent": "<1 sentence: what evidence removal would lower score>"
}}"""
 
 
# ============================================================================
# Prompt assembler
# ============================================================================
 
def build_prompt(variant_id: str) -> str:
    """Assemble a complete prompt for the given variant.
 
    Args:
        variant_id: One of "P1"-"P5".
 
    Returns:
        The full prompt string to send to the VLM.
    """
    header = COMMON_HEADER + FEW_SHOT_EXAMPLES
 
    variant_map = {
        "P1": P1_BODY + OUTPUT_INSTRUCTION_STANDARD,
        "P2": P2_BODY,
        "P3": P3_BODY + OUTPUT_INSTRUCTION_STANDARD,
        "P4": P4_BODY + OUTPUT_INSTRUCTION_STANDARD,
        "P5": P5_BODY,
    }
    body = variant_map.get(variant_id)
    if body is None:
        raise ValueError(f"Unknown prompt variant: {variant_id}")
 
    return header + body
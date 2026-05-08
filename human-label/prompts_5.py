"""
Prompt definitions for VLM-as-judge collision evaluation (v5).

Changes from prompts_4.py (v4):
  - COMMON_HEADER (WHAT COUNTS AS COLLISION): Added spatial proximity
    requirement (movement must be close to manipulator; far-side motion
    is not evidence). Tightened between-frame bullet to "items near the
    manipulator". Removed weak "when in doubt" line.
  - COMMON_HEADER: New DEFAULT ASSUMPTION block (null hypothesis framing,
    escalating evidence requirements for scores 1 vs 3+ vs 4/5).
  - CONTACT_ADDENDUM, OUTPUT_INSTRUCTION_STANDARD, P1-P5: unchanged from v4.

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
are shown 16 frames: the first 8 are CONTEXT (recent \
history), the last 8 are FUTURE (predicted continuation). \
The CONTEXT frames establish the scene layout \u2014 use them \
to identify what items are present and their approximate \
arrangement on the table.
Evaluate ONLY the FUTURE frames (9\u201316) for collision.

CAMERA: The camera is mounted on the robot arm (ego view, \
looking downward). Because the camera moves with the arm, \
ALL items will appear to shift between frames due to camera \
motion alone \u2014 this is NOT collision. To detect real \
collision, check whether items move RELATIVE TO EACH OTHER:
  \u2022 If all items shift together and maintain their relative \
arrangement \u2192 camera motion only, no collision.
  \u2022 If some items move while others stay put, or items \
spread apart / scatter relative to each other \u2192 real \
displacement, likely collision.

WHAT COUNTS AS COLLISION:
  \u2022 ONLY manipulator-to-item contact counts. Item-to-item \
or item-to-table contact does NOT count.
  \u2022 Movement or deformation must occur CLOSE TO the \
manipulator to count as evidence. Items shifting on the \
far side of the table, away from the manipulator, are \
not evidence of manipulator collision.
  \u2022 Items may already be scattered from earlier interactions. \
A messy scene does NOT indicate collision \u2014 look for NEW \
relative movement within frames 9\u201316 only.
  \u2022 Contact may occur between shown frames. If items near \
the manipulator appear suddenly displaced without a \
visible contact moment, collision likely occurred between \
frames.
  \u2022 If the table appears to shrink or recede, the arm is \
lifting \u2014 collision is less likely.

DEFAULT ASSUMPTION: Start from the assumption that NO \
collision occurred, and only increase your score if you \
see clear, specific evidence that contradicts this. A \
score of 1 requires no justification. A score of 3 or \
above requires you to identify WHICH item moved and HOW \
it moved relative to nearby items. A score of 4 or 5 \
requires clear, sustained evidence across multiple future \
frames of item displacement in proximity to the \
manipulator."""


# ============================================================================
# Contact addendum -- appended when image has contact visualization row
# ============================================================================

CONTACT_ADDENDUM = """\

You are shown two rows of images:
- Top row: RGB camera frames of the scene.
- Bottom row: Contact visualization frames. These show \
predicted contact locations projected from the 3D scene \
onto the camera view:
    \u2022 Colored spots indicate where physical contact is \
occurring between surfaces.
    \u2022 Brighter and larger spots indicate stronger contact \
forces.
    \u2022 The color (hue) of each spot encodes the direction \
of the contact force as seen from the camera \u2014 \
different colors mean forces pushing in different \
directions.
    \u2022 A mostly black image means little or no contact at \
that timestep.

  IMPORTANT: The contact visualization shows ALL physical \
contact in the scene, not just manipulator-to-item \
contact. Items resting on the table or leaning against \
each other produce baseline colored spots from gravity \
and resting forces. These baseline spots are ALWAYS \
present and do NOT indicate manipulator collision.
  To use the contact frames effectively:
    \u2022 Compare future contact frames to context contact \
frames \u2014 look for NEW spots or sudden changes in \
intensity that were not present in the context.
    \u2022 Focus on spots appearing near where the manipulator \
meets an item, not spots scattered across the scene \
from resting contacts.
    \u2022 If the contact frames look roughly the same in \
context and future, that suggests no new collision \
occurred."""


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

P1_BODY = """\

Rate the likelihood and severity of collision in the future \
frames on a 1\u20135 scale:

5 = Very clear collision with strong visible impact and \
substantial item displacement.
4 = Clear collision with noticeable interaction or item \
displacement.
3 = Likely collision with visible contact or slight \
post-contact effect, but not fully conclusive.
2 = Possible contact, but weak or ambiguous visual evidence.
1 = No visible collision evidence. Clear separation between \
manipulator and all items."""


# ============================================================================
# P2: Evidence-first (explicit evidence extraction before scoring)
# ============================================================================

P2_BODY = """\

Before scoring, analyze the future frames (frames 9\u201316):

Step 1: Describe the manipulator's trajectory \u2014 is it moving \
toward, away from, or parallel to any item?

Step 2: List any signs of physical contact \u2014 item \
displacement, orientation change, manipulator-item overlap, \
or sudden motion changes.

Step 3: Assess how clear the evidence is.

Then assign a score using this rubric:
5 = Very clear collision with strong visible impact.
4 = Clear collision with noticeable interaction.
3 = Likely collision, some evidence but not conclusive.
2 = Possible contact, weak or ambiguous.
1 = No collision evidence.

Respond with ONLY this JSON:
{
  "trajectory": "<1 sentence on manipulator movement>",
  "contact_signs": "<1-2 sentences on evidence>",
  "clarity": "<1 sentence on certainty>",
  "score": <integer 1-5>,
  "reasoning": "<1 sentence summary>"
}"""


# ============================================================================
# P3: Conservative (instructed to avoid high scores without clear evidence)
# ============================================================================

P3_BODY = """\

Rate collision in the future frames on a 1\u20135 scale.

IMPORTANT: Assign a score of 4 or 5 ONLY if the collision \
evidence is visually unambiguous \u2014 you can clearly see the \
manipulator making contact AND the item reacting (displacement, \
rotation, deformation). If there is any doubt, score 3 or \
below.

5 = Unambiguous collision with strong visible impact.
4 = Unambiguous collision with clear interaction.
3 = Probable collision but some visual ambiguity.
2 = Possible contact, weak evidence.
1 = No collision evidence."""


# ============================================================================
# P4: Strict future-only (emphasizes temporal boundary)
# ============================================================================

P4_BODY = """\

CRITICAL: The context frames (1\u20138) are provided ONLY for \
understanding the scene setup and the robot's approach \
trajectory. Do NOT consider any contact or collision that \
may appear in the context frames.

Focus exclusively on the future frames (9\u201316). Ask yourself: \
within these 8 frames specifically, does the robot's manipulator \
make new physical contact with any item?

Rate on a 1\u20135 scale:
5 = Very clear collision in future frames with strong impact.
4 = Clear collision in future frames with noticeable effect.
3 = Likely collision in future frames, evidence not conclusive.
2 = Possible contact in future frames, weak evidence.
1 = No collision evidence in future frames."""


# ============================================================================
# P5: Counterfactual verification (boundary stability check)
# ============================================================================

P5_BODY = """\

Rate collision in the future frames on a 1\u20135 scale using \
this rubric:
5 = Very clear collision with strong visible impact.
4 = Clear collision with noticeable interaction.
3 = Likely collision, not fully conclusive.
2 = Possible contact, weak evidence.
1 = No collision evidence.

After choosing your score, briefly state what visual evidence \
would need to be ABSENT for your score to drop by one level. \
This helps verify your score is at the right level.

Respond with ONLY this JSON:
{
  "score": <integer 1-5>,
  "reasoning": "<2 sentences of visual evidence>",
  "if_absent": "<1 sentence: what evidence removal would lower score>"
}"""


# ============================================================================
# Prompt assembler
# ============================================================================

def build_prompt(variant_id: str, has_contact: bool) -> str:
    """Assemble a complete prompt for the given variant and contact mode.

    Args:
        variant_id: One of "P1"-"P5".
        has_contact: Whether the image includes the contact visualization row.

    Returns:
        The full prompt string to send to the VLM.
    """
    header = COMMON_HEADER
    if has_contact:
        header += CONTACT_ADDENDUM

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

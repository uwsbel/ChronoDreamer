#!/usr/bin/env bash
set -euo pipefail

# Choose Python
if command -v python >/dev/null 2>&1; then PY=python
elif command -v python3 >/dev/null 2>&1; then PY=python3
else echo "No Python found. Install Python 3 or activate your env."; exit 1; fi

GENIE_SCRIPT="genie/generate.py"
VIS_SCRIPT="visualize.py"
CKPT_DIR="data/genie_model/8_24_256_720data_1040000"
VAL_DATA_DIR="data/generate_test"
TOKEN_DIR="data/genie_generated"

START=100   # first example_ind
STEP=50    # increment per run
COUNT=100     # total runs

mkdir -p "$TOKEN_DIR"

for ((i=0; i<COUNT; i++)); do
  EX=$((START + i * STEP))
  echo "[*] Generating example_ind=$EX"
  "$PY" "$GENIE_SCRIPT" --checkpoint_dir "$CKPT_DIR" --val_data_dir "$VAL_DATA_DIR" --example_ind "$EX" --generate_contact
 
  echo "    Visualizing tokens -> GIF (camera + contact)"
  "$PY" "$VIS_SCRIPT" --token_dir "$TOKEN_DIR" --visualize_contact

  SRC="$TOKEN_DIR/generated_offset0.gif"
  if [[ ! -f "$SRC" ]]; then
    echo "Error: $SRC not found for example_ind=$EX" >&2
    exit 1
  fi

  # Name by index (zero-pad to 6 digits; change %06d to %d for no padding)
  printf -v DST "%s/generated_%06d.gif" "$TOKEN_DIR" "$EX"
  mv -f "$SRC" "$DST"
  echo "    Saved: $DST"

  # Also rename contact and combined GIFs if they exist
  CONTACT_SRC="$TOKEN_DIR/contact_offset0.gif"
  COMBINED_SRC="$TOKEN_DIR/combined_offset0.gif"
  COMIC_SRC="$TOKEN_DIR/generated_comic_offset0.png"

  if [[ -f "$CONTACT_SRC" ]]; then
    printf -v CONTACT_DST "%s/contact_%06d.gif" "$TOKEN_DIR" "$EX"
    mv -f "$CONTACT_SRC" "$CONTACT_DST"
    echo "    Saved: $CONTACT_DST"
  fi

  if [[ -f "$COMBINED_SRC" ]]; then
    printf -v COMBINED_DST "%s/combined_%06d.gif" "$TOKEN_DIR" "$EX"
    mv -f "$COMBINED_SRC" "$COMBINED_DST"
    echo "    Saved: $COMBINED_DST"
  fi

  if [[ -f "$COMIC_SRC" ]]; then
    printf -v COMIC_DST "%s/comic_%06d.png" "$TOKEN_DIR" "$EX"
    mv -f "$COMIC_SRC" "$COMIC_DST"
    echo "    Saved: $COMIC_DST"
  fi
done

echo "All done. GIFs are in $TOKEN_DIR"


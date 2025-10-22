#!/usr/bin/env bash
set -euo pipefail

# Choose Python
if command -v python >/dev/null 2>&1; then PY=python
elif command -v python3 >/dev/null 2>&1; then PY=python3
else echo "No Python found. Install Python 3 or activate your env."; exit 1; fi

GENIE_SCRIPT="genie/generate.py"
VIS_SCRIPT="visualize.py"
CKPT_DIR="data/genie_model/step_300000/"
TOKEN_DIR="data/genie_generated"

START=30000   # first example_ind
STEP=2000    # increment per run
COUNT=20     # total runs

mkdir -p "$TOKEN_DIR"

for ((i=0; i<COUNT; i++)); do
  EX=$((START + i * STEP))
  echo "[*] Generating example_ind=$EX"
  "$PY" "$GENIE_SCRIPT" --checkpoint_dir "$CKPT_DIR" --example_ind "$EX"

  echo "    Visualizing tokens -> GIF"
  "$PY" "$VIS_SCRIPT" --token_dir "$TOKEN_DIR"

  SRC="$TOKEN_DIR/generated_offset0.gif"
  if [[ ! -f "$SRC" ]]; then
    echo "Error: $SRC not found for example_ind=$EX" >&2
    exit 1
  fi

  # Name by index (zero-pad to 6 digits; change %06d to %d for no padding)
  printf -v DST "%s/generated_%06d.gif" "$TOKEN_DIR" "$EX"
  mv -f "$SRC" "$DST"
  echo "    Saved: $DST"
done

echo "All done. GIFs are in $TOKEN_DIR"


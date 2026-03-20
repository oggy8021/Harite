#!/usr/bin/env bash
set -euo pipefail

# Run #6 follow-up checks on XFCE:
# 1) Rollback verification with a known-good image.
# 2) Optional short smoke run using xfce_smoke_runner.py.

usage() {
  cat <<'EOF'
Usage:
  scripts/run_xfce_followup.sh --known-good /abs/path/to/good.jpg [options]

Options:
  --known-good PATH      Absolute path to known-good wallpaper image (required)
  --smoke-input PATH     Directory or file for smoke runner input (optional)
  --smoke-iterations N   Smoke iterations (default: 5)
  --outdir DIR           Output directory (default: xfce-followup-YYYYmmdd-HHMMSS)
  --python CMD           Python executable (default: python3)
  --skip-smoke           Skip smoke runner execution
  -h, --help             Show this help

Example:
  scripts/run_xfce_followup.sh \
    --known-good /home/user/Pictures/known-good.jpg \
    --smoke-input /home/user/Pictures/wallpapers \
    --smoke-iterations 5
EOF
}

KNOWN_GOOD=""
SMOKE_INPUT=""
SMOKE_ITERATIONS=5
OUTDIR="xfce-followup-$(date +%Y%m%d-%H%M%S)"
PYTHON_CMD="python3"
SKIP_SMOKE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --known-good)
      KNOWN_GOOD="${2:-}"
      shift 2
      ;;
    --smoke-input)
      SMOKE_INPUT="${2:-}"
      shift 2
      ;;
    --smoke-iterations)
      SMOKE_ITERATIONS="${2:-}"
      shift 2
      ;;
    --outdir)
      OUTDIR="${2:-}"
      shift 2
      ;;
    --python)
      PYTHON_CMD="${2:-}"
      shift 2
      ;;
    --skip-smoke)
      SKIP_SMOKE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ -z "$KNOWN_GOOD" ]]; then
  echo "--known-good is required" >&2
  usage
  exit 2
fi

if [[ ! "$KNOWN_GOOD" = /* ]]; then
  echo "--known-good must be an absolute path" >&2
  exit 2
fi

if [[ ! -f "$KNOWN_GOOD" ]]; then
  echo "known-good image not found: $KNOWN_GOOD" >&2
  exit 2
fi

mkdir -p "$OUTDIR"

echo "[1/6] Collecting XFCE properties (before)"
xfconf-query -c xfce4-desktop -l > "$OUTDIR/xfconf-props-before.txt"
xfconf-query -c xfce4-desktop -l -v > "$OUTDIR/xfconf-values-before.txt"

echo "[2/6] Running dry-run apply"
"$PYTHON_CMD" -m harite.cli apply --plugin linux --file "$KNOWN_GOOD" \
  > "$OUTDIR/apply-dry-run.log" 2>&1

echo "[3/6] Running do-it apply"
"$PYTHON_CMD" -m harite.cli apply --plugin linux --file "$KNOWN_GOOD" --do-it \
  > "$OUTDIR/apply-do-it.log" 2>&1

echo "[4/6] Collecting XFCE properties (after)"
xfconf-query -c xfce4-desktop -l -v > "$OUTDIR/xfconf-values-after.txt"

echo "[5/6] Extracting last-image lines"
grep -i "last-image" "$OUTDIR/xfconf-values-before.txt" > "$OUTDIR/last-image-before.txt" || true
grep -i "last-image" "$OUTDIR/xfconf-values-after.txt" > "$OUTDIR/last-image-after.txt" || true

if [[ "$SKIP_SMOKE" -eq 0 && -n "$SMOKE_INPUT" ]]; then
  echo "[6/6] Running short smoke"
  "$PYTHON_CMD" scripts/xfce_smoke_runner.py \
    --input "$SMOKE_INPUT" \
    --iterations "$SMOKE_ITERATIONS" \
    --interval-min 5 \
    --interval-max 15 \
    --do-it \
    --log-file "$OUTDIR/smoke.log" \
    > "$OUTDIR/smoke-stdout.log" 2>&1 || true
else
  echo "[6/6] Smoke skipped"
fi

cat > "$OUTDIR/summary.md" <<EOF
# XFCE Follow-up Summary

- Date: $(date +%Y-%m-%d)
- Known-good image: $KNOWN_GOOD
- Dry-run log: $OUTDIR/apply-dry-run.log
- Do-it log: $OUTDIR/apply-do-it.log
- Before values: $OUTDIR/xfconf-values-before.txt
- After values: $OUTDIR/xfconf-values-after.txt
- Last-image(before): $OUTDIR/last-image-before.txt
- Last-image(after): $OUTDIR/last-image-after.txt
- Smoke output: $OUTDIR/smoke.log

Result notes:
- [ ] Wallpaper recovered on-screen
- [ ] last-image values are absolute paths
- [ ] No black background observed
EOF

echo "Done. Output directory: $OUTDIR"
echo "Please review: $OUTDIR/summary.md"

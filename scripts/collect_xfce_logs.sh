#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/collect_xfce_logs.sh [outdir]
OUTDIR="${1:-xfce-logs-$(date +%Y%m%d-%H%M%S)}"
mkdir -p "$OUTDIR"

echo "Collecting environment variables..." > "$OUTDIR/env.txt"
env >> "$OUTDIR/env.txt"
echo >> "$OUTDIR/env.txt"
echo "XDG_SESSION_TYPE=$XDG_SESSION_TYPE" >> "$OUTDIR/env.txt" 2>/dev/null || true

echo "Collecting xrandr output..." > "$OUTDIR/xrandr.txt"
if command -v xrandr >/dev/null 2>&1; then
  xrandr --verbose >> "$OUTDIR/xrandr.txt" 2>&1 || true
else
  echo "xrandr: not available" >> "$OUTDIR/xrandr.txt"
fi

echo "Collecting display-related logs..." > "$OUTDIR/display_info.txt"
if command -v xfce4-display-settings >/dev/null 2>&1; then
  xfce4-display-settings --version >> "$OUTDIR/display_info.txt" 2>&1 || true
fi

echo "Attempting to run harite with --verbose (if installed)..." > "$OUTDIR/harite.log"
if command -v python3 >/dev/null 2>&1; then
  if python3 -m pip show harite >/dev/null 2>&1; then
    python3 -m harite --verbose >> "$OUTDIR/harite.log" 2>&1 || true
  else
    echo "harite not installed in current Python environment" >> "$OUTDIR/harite.log"
  fi
else
  echo "python3 not available" >> "$OUTDIR/harite.log"
fi

# Attempt to collect system logs for display/Xorg if available
journalctl -b _COMM=Xorg --no-pager > "$OUTDIR/xorg.log" 2>/dev/null || true
journalctl -b -u display-manager --no-pager > "$OUTDIR/display-manager.log" 2>/dev/null || true

tar -czf "$OUTDIR.tar.gz" -C "$(dirname "$OUTDIR")" "$(basename "$OUTDIR")" >/dev/null 2>&1 || true

echo "Collected logs: $OUTDIR (archive: $OUTDIR.tar.gz)"

#!/usr/bin/env python3
"""Run repeated Harite CLI apply calls for local XFCE smoke testing.

This helper keeps interval-based wallpaper checks outside the core CLI.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"


def default_python_executable() -> str:
    """Prefer project virtualenv Python when available."""
    win = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    unix = PROJECT_ROOT / ".venv" / "bin" / "python"
    if win.exists():
        return str(win)
    if unix.exists():
        return str(unix)
    return sys.executable


def collect_images(inputs: Iterable[str]) -> List[Path]:
    images: List[Path] = []
    for raw in inputs:
        p = Path(raw)
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            images.append(p.resolve())
            continue
        if p.is_dir():
            for child in sorted(p.rglob("*")):
                if child.is_file() and child.suffix.lower() in IMAGE_EXTS:
                    images.append(child.resolve())
    # Preserve order while removing duplicates.
    seen = set()
    uniq: List[Path] = []
    for p in images:
        key = str(p)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(p)
    return uniq


def build_apply_command(
    image: Path,
    settings_file: Path | None,
    do_it: bool,
    extra_args: List[str],
    python_executable: str,
) -> List[str]:
    cmd = [
        python_executable,
        "-m",
        "harite.cli",
        "apply",
        "--file",
        str(image),
    ]
    if settings_file is not None:
        cmd.extend(["-c", str(settings_file)])
    if do_it:
        cmd.append("--do-it")
    cmd.extend(extra_args)
    return cmd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="XFCE smoke runner for Harite CLI apply")
    parser.add_argument(
        "--input",
        "-i",
        action="append",
        required=True,
        help="Input image file or directory (repeatable)",
    )
    parser.add_argument("--iterations", type=int, default=30, help="Number of apply attempts")
    parser.add_argument("--interval-min", type=int, default=15, help="Minimum wait seconds")
    parser.add_argument("--interval-max", type=int, default=120, help="Maximum wait seconds")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument(
        "--plugin",
        default="linux",
        help="Plugin name written to a temporary settings file for apply (default: linux)",
    )
    parser.add_argument("--python", default=default_python_executable(), help="Python executable for child apply command")
    parser.add_argument("--do-it", action="store_true", help="Actually apply wallpaper (default: dry-run)")
    parser.add_argument("--stop-on-error", action="store_true", help="Stop loop on first non-zero exit")
    parser.add_argument("--log-file", default="xfce-smoke.log", help="Log file path")
    parser.add_argument(
        "--extra-apply-arg",
        action="append",
        default=[],
        help="Extra arg forwarded to `harite apply` (repeatable)",
    )
    return parser.parse_args()


def log_line(path: Path, message: str) -> None:
    stamp = datetime.now().isoformat(timespec="seconds")
    line = f"[{stamp}] {message}"
    print(line)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def main() -> int:
    args = parse_args()

    if args.iterations <= 0:
        print("--iterations must be > 0", file=sys.stderr)
        return 2
    if args.interval_min < 0 or args.interval_max < 0 or args.interval_min > args.interval_max:
        print("invalid interval range", file=sys.stderr)
        return 2

    if args.seed is not None:
        random.seed(args.seed)

    images = collect_images(args.input)
    if not images:
        print("No input images found. Check --input paths.", file=sys.stderr)
        return 2

    log_file = Path(args.log_file)
    log_line(log_file, f"start iterations={args.iterations} images={len(images)} do_it={args.do_it}")

    settings_file = log_file.parent / "xfce-smoke-settings.json"
    settings_file.write_text(
        json.dumps({"plugin": args.plugin, "apply_mode": "single-file"}, indent=2) + "\n",
        encoding="utf-8",
    )

    failures = 0
    for idx in range(1, args.iterations + 1):
        image = random.choice(images)
        cmd = build_apply_command(
            image=image,
            settings_file=settings_file,
            do_it=args.do_it,
            extra_args=args.extra_apply_arg,
            python_executable=args.python,
        )

        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC_DIR) + os.pathsep + env.get("PYTHONPATH", "")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
        ok = result.returncode == 0
        status = "ok" if ok else "fail"
        log_line(log_file, f"iter={idx} status={status} file={image} rc={result.returncode}")

        out = (result.stdout or "").strip()
        err = (result.stderr or "").strip()
        if out:
            log_line(log_file, f"stdout: {out}")
        if err:
            log_line(log_file, f"stderr: {err}")

        if not ok:
            failures += 1
            if args.stop_on_error:
                log_line(log_file, "stopped by --stop-on-error")
                break

        if idx < args.iterations:
            wait_sec = random.randint(args.interval_min, args.interval_max)
            log_line(log_file, f"sleep={wait_sec}s")
            time.sleep(wait_sec)

    log_line(log_file, f"finish failures={failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
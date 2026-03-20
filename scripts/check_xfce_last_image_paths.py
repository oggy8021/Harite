#!/usr/bin/env python3
"""Validate that XFCE last-image values are absolute paths."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check whether xfconf last-image values are absolute paths"
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to xfconf-values-after.txt (or equivalent)",
    )
    return parser.parse_args()


def is_absolute_path(value: str) -> bool:
    # Linux absolute path
    if value.startswith("/"):
        return True
    # URI style (file:///...)
    if value.startswith("file://"):
        return True
    return False


def main() -> int:
    args = parse_args()
    path = Path(args.file)
    if not path.exists():
        print(f"ERROR: file not found: {path}")
        return 2

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    target_lines = [ln for ln in lines if "last-image" in ln.lower()]
    if not target_lines:
        print("WARN: no last-image lines found")
        return 1

    bad: list[str] = []
    for ln in target_lines:
        # Accept common xfconf format: "key  value"
        m = re.split(r"\s{2,}|\t+", ln.strip(), maxsplit=1)
        if len(m) < 2:
            bad.append(ln)
            continue
        value = m[1].strip().strip('"')
        if not is_absolute_path(value):
            bad.append(ln)

    print(f"checked lines: {len(target_lines)}")
    if bad:
        print("result: FAIL")
        for ln in bad:
            print(f"  non-absolute: {ln}")
        return 1

    print("result: OK (all last-image values are absolute)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

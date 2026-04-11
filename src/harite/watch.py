"""Watch command helpers (minimum skeleton stage)."""
from __future__ import annotations

from pathlib import Path
from typing import List


_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}


def collect_watch_input_images(input_dir: Path) -> List[Path]:
    """Collect image files from an input directory.

    This function performs minimum validation for the first watch phase.
    """
    if not input_dir.exists() or not input_dir.is_dir():
        raise ValueError("--input must be an existing directory")

    images = sorted(
        p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in _IMAGE_EXTS
    )
    if not images:
        raise ValueError("no image files found in --input directory")
    return images

"""Watch command helpers (minimum skeleton stage)."""
from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Callable, List


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


def select_next_image(
    images: List[Path],
    mode: str,
    index: int,
    rng: random.Random | None = None,
) -> tuple[Path, int]:
    """Select the next image for a watch cycle.

    Returns a tuple of (selected_image, next_index).
    """
    if not images:
        raise ValueError("images must not be empty")

    normalized_mode = mode.lower().strip()
    if normalized_mode == "sequential":
        selected_index = index % len(images)
        return images[selected_index], index + 1

    if normalized_mode == "random":
        chooser = rng if rng is not None else random
        return chooser.choice(images), index

    raise ValueError("mode must be one of: sequential, random")


def run_watch_cycles(
    images: List[Path],
    mode: str,
    interval_sec: int,
    iterations: int | None,
    on_cycle: Callable[[Path, int], None],
    sleep_fn: Callable[[float], None] = time.sleep,
) -> int:
    """Run watch cycles and return completed cycle count."""
    if interval_sec < 1:
        raise ValueError("interval_sec must be >= 1")
    if iterations is not None and iterations < 1:
        raise ValueError("iterations must be >= 1")

    index = 0
    completed = 0

    while iterations is None or completed < iterations:
        selected, index = select_next_image(images, mode, index)
        on_cycle(selected, completed)
        completed += 1

        # Sleep only if another cycle may follow.
        if iterations is None or completed < iterations:
            sleep_fn(interval_sec)

    return completed

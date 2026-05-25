"""Slideshow command helpers."""
from __future__ import annotations

from dataclasses import dataclass
import random
import time
from pathlib import Path
from typing import Callable, List, Sequence


_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}


@dataclass(frozen=True)
class SlideshowCycleState:
    index: int = 0
    previous_selected: Path | None = None
    completed: int = 0


def collect_slideshow_input_images(input_dirs: Sequence[Path]) -> List[Path]:
    """Collect image files from one or more input directories.

    This function performs input validation for slideshow execution.
    """
    if not input_dirs:
        raise ValueError("--input must be an existing directory")

    images: List[Path] = []
    for input_dir in input_dirs:
        if not input_dir.exists() or not input_dir.is_dir():
            raise ValueError("--input must be an existing directory")
        images.extend(
            sorted(
                p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in _IMAGE_EXTS
            )
        )
    if not images:
        raise ValueError("no image files found in --input directory")
    return images


def select_next_image(
    images: List[Path],
    mode: str,
    index: int,
    previous_selected: Path | None = None,
    rng: random.Random | None = None,
) -> tuple[Path, int]:
    """Select the next image for a slideshow cycle.

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
        if len(images) > 1 and previous_selected in images:
            candidates = [img for img in images if img != previous_selected]
            return chooser.choice(candidates), index
        return chooser.choice(images), index

    raise ValueError("mode must be one of: sequential, random")


def run_slideshow_cycle(
    images: List[Path],
    mode: str,
    state: SlideshowCycleState,
    rng: random.Random | None = None,
) -> tuple[Path, SlideshowCycleState]:
    """Run a single slideshow cycle and return the updated state."""
    selected, next_index = select_next_image(
        images,
        mode,
        state.index,
        previous_selected=state.previous_selected,
        rng=rng,
    )
    next_state = SlideshowCycleState(
        index=next_index,
        previous_selected=selected,
        completed=state.completed + 1,
    )
    return selected, next_state


def run_slideshow_cycles(
    images: List[Path],
    mode: str,
    interval_sec: int,
    on_cycle: Callable[[Path, int], None],
    sleep_fn: Callable[[float], None] = time.sleep,
) -> int:
    """Run slideshow cycles and return completed cycle count."""
    if interval_sec < 1:
        raise ValueError("interval_sec must be >= 1")

    state = SlideshowCycleState()

    while True:
        selected, state = run_slideshow_cycle(images, mode, state)
        on_cycle(selected, state.completed - 1)

        sleep_fn(interval_sec)

    return state.completed
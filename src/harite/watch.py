"""Watch command helpers (minimum skeleton stage)."""
from __future__ import annotations

from dataclasses import dataclass
import random
import time
from pathlib import Path
from typing import Callable, List


_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}


@dataclass(frozen=True)
class WatchCycleState:
    index: int = 0
    previous_selected: Path | None = None
    completed: int = 0


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
    previous_selected: Path | None = None,
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
        if len(images) > 1 and previous_selected in images:
            candidates = [img for img in images if img != previous_selected]
            return chooser.choice(candidates), index
        return chooser.choice(images), index

    raise ValueError("mode must be one of: sequential, random")


def run_watch_cycle(
    images: List[Path],
    mode: str,
    state: WatchCycleState,
    rng: random.Random | None = None,
) -> tuple[Path, WatchCycleState]:
    """Run a single watch cycle and return the updated state."""
    selected, next_index = select_next_image(
        images,
        mode,
        state.index,
        previous_selected=state.previous_selected,
        rng=rng,
    )
    next_state = WatchCycleState(
        index=next_index,
        previous_selected=selected,
        completed=state.completed + 1,
    )
    return selected, next_state


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

    state = WatchCycleState()

    while iterations is None or state.completed < iterations:
        selected, state = run_watch_cycle(images, mode, state)
        on_cycle(selected, state.completed - 1)

        # Sleep only if another cycle may follow.
        if iterations is None or state.completed < iterations:
            sleep_fn(interval_sec)

    return state.completed

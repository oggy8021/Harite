from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .core import split_composite_for_displays
from .workspace import Display, detect_displays


@dataclass(frozen=True)
class TwoScreenOptimizeContext:
    displays: tuple[Display, Display]
    resolution: tuple[int, int]
    l_display: tuple[int, int]
    r_display: tuple[int, int]


def order_displays(displays: Sequence[Display], *, limit: int | None = None) -> tuple[Display, ...]:
    ordered = tuple(
        sorted(
            displays,
            key=lambda display: (int(display.x_offset), int(display.y_offset), display.name),
        )
    )
    if limit is None:
        return ordered
    return ordered[:limit]


def derive_virtual_resolution(displays: Sequence[Display]) -> tuple[int, int] | None:
    if not displays:
        return None

    min_x = min(int(display.x_offset) for display in displays)
    max_x = max(int(display.x_offset) + int(display.width) for display in displays)
    min_y = min(int(display.y_offset) for display in displays)
    max_y = max(int(display.y_offset) + int(display.height) for display in displays)
    return (max_x - min_x, max_y - min_y)


def build_two_screen_optimize_context(displays: Sequence[Display] | None = None) -> TwoScreenOptimizeContext | None:
    detected = order_displays(detect_displays() if displays is None else displays, limit=2)
    if len(detected) < 2:
        return None

    resolution = derive_virtual_resolution(detected)
    if resolution is None:
        return None

    left_display, right_display = detected[0], detected[1]
    return TwoScreenOptimizeContext(
        displays=(left_display, right_display),
        resolution=resolution,
        l_display=(int(left_display.width), int(left_display.height)),
        r_display=(int(right_display.width), int(right_display.height)),
    )


def build_auto_split_display_map(
    composite_path: Path,
    displays: Sequence[Display] | None = None,
    output_dir: Path | None = None,
) -> dict:
    detected = order_displays(detect_displays() if displays is None else displays)
    if not detected:
        return {}
    return split_composite_for_displays(
        composite_path,
        list(detected),
        composite_path.parent if output_dir is None else output_dir,
    )
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .display_context import build_two_screen_optimize_context


AUTO = "auto"


def is_auto_value(value: object) -> bool:
    return isinstance(value, str) and value.strip().lower() == AUTO


@dataclass(frozen=True)
class EffectiveOptimizeDisplaySettings:
    resolution: str
    two_screen: bool
    l_display: str | None
    r_display: str | None


def _stringify_resolution(value: tuple[int, int]) -> str:
    return f"{int(value[0])}x{int(value[1])}"


def resolve_optimize_display_settings(
    *,
    input_values: Sequence[str],
    resolution: str | None,
    two_screen: bool | None,
    l_display: str | None,
    r_display: str | None,
) -> EffectiveOptimizeDisplaySettings:
    cleaned_inputs = [str(value).strip() for value in input_values if str(value).strip()]
    context = build_two_screen_optimize_context() if len(cleaned_inputs) >= 2 else None

    auto_two_screen = two_screen is None
    effective_two_screen = bool(two_screen) if two_screen is not None else context is not None

    effective_resolution = None if resolution is None or is_auto_value(resolution) else str(resolution).strip()
    if not effective_resolution:
        effective_resolution = None
    effective_l_display = None if l_display is None or is_auto_value(l_display) else str(l_display).strip()
    effective_r_display = None if r_display is None or is_auto_value(r_display) else str(r_display).strip()

    if context is not None and effective_two_screen:
        if effective_resolution is None:
            effective_resolution = _stringify_resolution(context.resolution)
        if effective_l_display is None:
            effective_l_display = _stringify_resolution(context.l_display)
        if effective_r_display is None:
            effective_r_display = _stringify_resolution(context.r_display)

    if auto_two_screen and context is None:
        effective_two_screen = False

    if effective_resolution is None and cleaned_inputs:
        from .display_context import order_displays
        from .workspace import detect_displays

        detected = order_displays(detect_displays(), limit=1)
        if detected:
            primary = detected[0]
            effective_resolution = _stringify_resolution((int(primary.width), int(primary.height)))

    if effective_resolution is None:
        raise ValueError("resolution is required")

    return EffectiveOptimizeDisplaySettings(
        resolution=effective_resolution,
        two_screen=effective_two_screen,
        l_display=effective_l_display,
        r_display=effective_r_display,
    )
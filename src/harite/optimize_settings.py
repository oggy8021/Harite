from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .display_context import build_two_screen_optimize_context


AUTO = "auto"

DUAL_INPUT_REQUIRES_TWO_DISPLAYS = (
    "Two input images require two detected displays. "
    "Use one input, or set --two-screen with explicit --resolution and --l-display/--r-display."
)

DUAL_INPUT_REQUIRES_TWO_SCREEN = (
    "Two input images require two-screen mode. "
    "Do not use --no-two-screen or two_screen off in settings."
)


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
    dual_input = len(cleaned_inputs) >= 2
    context = build_two_screen_optimize_context() if dual_input else None

    explicit_resolution = resolution is not None and not is_auto_value(resolution)
    manual_dual_override = dual_input and two_screen is True and explicit_resolution

    if dual_input:
        if two_screen is False:
            raise ValueError(DUAL_INPUT_REQUIRES_TWO_SCREEN)
        if context is None and not manual_dual_override:
            raise ValueError(DUAL_INPUT_REQUIRES_TWO_DISPLAYS)
        effective_two_screen = True
    elif two_screen is not None:
        effective_two_screen = bool(two_screen)
    else:
        effective_two_screen = False

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

    if effective_resolution is None and cleaned_inputs and not dual_input:
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
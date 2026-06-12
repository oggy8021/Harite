from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .display_context import build_two_screen_optimize_context


DUAL_INPUT_REQUIRES_TWO_DISPLAYS = (
    "Two input images require two detected displays. Use one input only."
)


def normalize_canvas_scale_percent(value: object, *, default: int = 100) -> int:
    if value is None:
        return default
    try:
        percent = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("canvas_scale_percent must be an integer between 1 and 100") from exc
    if percent < 1 or percent > 100:
        raise ValueError("canvas_scale_percent must be between 1 and 100")
    return percent


@dataclass(frozen=True)
class EffectiveOptimizeDisplaySettings:
    resolution: str
    two_screen: bool
    l_display: str | None
    r_display: str | None
    canvas_scale_percent: int


def _stringify_resolution(value: tuple[int, int]) -> str:
    return f"{int(value[0])}x{int(value[1])}"


def _apply_canvas_scale(size: tuple[int, int], percent: int) -> tuple[int, int]:
    w, h = size
    p = normalize_canvas_scale_percent(percent)
    return (max(1, round(w * p / 100)), max(1, round(h * p / 100)))


def resolve_optimize_display_settings(
    *,
    input_values: Sequence[str],
    canvas_scale_percent: int = 100,
) -> EffectiveOptimizeDisplaySettings:
    cleaned_inputs = [str(value).strip() for value in input_values if str(value).strip()]
    dual_input = len(cleaned_inputs) >= 2
    scale = normalize_canvas_scale_percent(canvas_scale_percent)
    context = build_two_screen_optimize_context() if dual_input else None

    if dual_input:
        if context is None:
            raise ValueError(DUAL_INPUT_REQUIRES_TWO_DISPLAYS)
        effective_two_screen = True
        base_w, base_h = context.resolution
        scaled_w, scaled_h = _apply_canvas_scale((base_w, base_h), scale)
        effective_resolution = _stringify_resolution((scaled_w, scaled_h))
        effective_l_display = _stringify_resolution(context.l_display)
        effective_r_display = _stringify_resolution(context.r_display)
    else:
        effective_two_screen = False
        effective_r_display = None
        base_size: tuple[int, int] | None = None
        if context is not None:
            base_size = context.resolution
        elif cleaned_inputs:
            from .display_context import order_displays
            from .workspace import detect_displays

            detected = order_displays(detect_displays(), limit=1)
            if detected:
                primary = detected[0]
                base_size = (int(primary.width), int(primary.height))
        if base_size is None:
            raise ValueError("No display detected for optimize")
        effective_l_display = _stringify_resolution(base_size)
        scaled_w, scaled_h = _apply_canvas_scale(base_size, scale)
        effective_resolution = _stringify_resolution((scaled_w, scaled_h))

    return EffectiveOptimizeDisplaySettings(
        resolution=effective_resolution,
        two_screen=effective_two_screen,
        l_display=effective_l_display,
        r_display=effective_r_display,
        canvas_scale_percent=scale,
    )

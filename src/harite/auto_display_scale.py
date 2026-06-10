"""MAT-14b: threshold-based automatic source-image upscale."""

from __future__ import annotations

from harite.display_scale import normalize_display_scale


def usable_display_rect(
    screen_w: int,
    screen_h: int,
    margins: tuple[int, int, int, int],
) -> tuple[int, int]:
    ml, mr, mt, mb = margins
    return (
        max(1, int(screen_w) - ml - mr),
        max(1, int(screen_h) - mt - mb),
    )


def compute_auto_display_scale_factor(
    image_width: int,
    image_height: int,
    *,
    screen_w: int,
    screen_h: int,
    margins: tuple[int, int, int, int],
) -> float:
    """Return 1.0, 1.5, or 2.0 from short-edge thresholds vs the display slot."""
    usable_w, usable_h = usable_display_rect(screen_w, screen_h, margins)
    image_short = min(int(image_width), int(image_height))
    display_short = min(usable_w, usable_h)
    if image_short <= display_short // 4:
        return 2.0
    if image_short <= display_short // 2:
        return 1.5
    return 1.0


def resolve_effective_display_scale(
    image_width: int,
    image_height: int,
    *,
    screen_w: int,
    screen_h: int,
    margins: tuple[int, int, int, int],
    manual_scale: float | object,
    auto_enabled: bool,
) -> float:
    """Manual MAT-14 preset overrides auto when not 100%."""
    manual = normalize_display_scale(manual_scale)
    if manual != 1.0:
        return manual
    if not auto_enabled:
        return 1.0
    return compute_auto_display_scale_factor(
        image_width,
        image_height,
        screen_w=screen_w,
        screen_h=screen_h,
        margins=margins,
    )

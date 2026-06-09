"""Per-display intentional source-image scale presets (MAT-14)."""

from __future__ import annotations

DISPLAY_SCALE_PRESETS: tuple[float, ...] = (1.0, 1.25, 1.5, 2.0)
MAX_OPTIMIZE_EDGE = 16384


def normalize_display_scale(value: object) -> float:
    if value is None:
        return 1.0

    raw_text = str(value).strip() if isinstance(value, str) else None
    if raw_text == "":
        return 1.0

    parsed: float | None = None
    if raw_text is not None:
        percent_mode = raw_text.endswith("%")
        number_text = raw_text[:-1].strip() if percent_mode else raw_text
        try:
            parsed = float(number_text)
        except ValueError:
            return 1.0
        if percent_mode:
            parsed /= 100.0
        elif parsed > 4.0:
            parsed /= 100.0
    else:
        try:
            parsed = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 1.0

    if parsed is None:
        return 1.0

    # Legacy MAT-14 draft stored 4x; map to the current maximum preset.
    if abs(parsed - 4.0) < 1e-6:
        parsed = 2.0

    for preset in DISPLAY_SCALE_PRESETS:
        if abs(parsed - preset) < 1e-6:
            return preset
    return 1.0


def is_unity_display_scale(value: object) -> bool:
    return normalize_display_scale(value) == 1.0


def format_display_scale_label(scale: float | object) -> str:
    normalized = normalize_display_scale(scale)
    return f"{int(round(normalized * 100))}%"


def scale_image_dimensions(width: int, height: int, factor: float | object) -> tuple[int, int]:
    normalized = normalize_display_scale(factor)
    if normalized == 1.0:
        return (int(width), int(height))
    return (
        max(1, int(round(int(width) * normalized))),
        max(1, int(round(int(height) * normalized))),
    )


def validate_scaled_image_edge(width: int, height: int, *, label: str = "source image") -> None:
    if int(width) <= 0 or int(height) <= 0:
        raise ValueError(f"{label} must be positive")
    if int(width) > MAX_OPTIMIZE_EDGE or int(height) > MAX_OPTIMIZE_EDGE:
        raise ValueError(
            f"scaled {label} exceeds limit (max {MAX_OPTIMIZE_EDGE}px per edge): {int(width)}x{int(height)}"
        )


def image_scale_for_index(index: int, *, l_display_scale: float, r_display_scale: float) -> float:
    if index == 0:
        return normalize_display_scale(l_display_scale)
    if index == 1:
        return normalize_display_scale(r_display_scale)
    return 1.0

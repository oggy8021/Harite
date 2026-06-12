"""WCAG relative luminance helpers for contrasting foreground choices."""

from __future__ import annotations


def _linearize_channel(channel: int) -> float:
    c = max(0, min(255, int(channel))) / 255.0
    if c <= 0.03928:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    """Return WCAG 2.x relative luminance for an sRGB triple."""
    r, g, b = rgb
    return (
        0.2126 * _linearize_channel(r)
        + 0.7152 * _linearize_channel(g)
        + 0.0722 * _linearize_channel(b)
    )


def choose_contrasting_embed_text_rgb(background_rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    """Pick light or dark embed text for readability on ``background_rgb``."""
    if relative_luminance(background_rgb) < 0.5:
        return (235, 235, 235)
    return (35, 35, 35)

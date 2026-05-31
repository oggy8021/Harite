"""User-facing apply-mode strings and Windows Span surface rules."""

from __future__ import annotations

import platform

from harite.workspace import detect_displays


def is_windows_host() -> bool:
    return platform.system() == "Windows"


def count_detected_displays() -> int:
    try:
        return len(detect_displays())
    except Exception:
        return 0


def windows_multi_monitor() -> bool:
    return is_windows_host() and count_detected_displays() >= 2


def per_monitor_mode_radio_label() -> str:
    return "Span" if is_windows_host() else "Auto-Split"


def single_file_mode_radio_label() -> str:
    return "No Split"


def apply_mode_help_text(mode: str, *, windows_apply_span: bool = False) -> str:
    normalized = str(mode or "single-file").strip().lower()
    if is_windows_host():
        if normalized == "per-monitor-auto-split":
            if windows_apply_span:
                return (
                    "Apply one wide image across all displays. "
                    "Harite will switch Windows background to Span when applying."
                )
            return (
                "Apply one wide image across all displays. "
                "Choose Span here, or set Windows background to Span manually."
            )
        return "Apply one image file to the desktop wallpaper."
    if normalized == "per-monitor-auto-split":
        return "Split the optimized image and apply per display."
    return "Apply the optimized image as a single file."


def preview_result_notes(apply_mode: str) -> tuple[str, str]:
    normalized = str(apply_mode or "single-file").strip().lower()
    if normalized == "per-monitor-auto-split" and is_windows_host():
        return (
            "Result: left monitor region",
            "Result: right monitor region",
        )
    if normalized == "per-monitor-auto-split":
        return (
            "Result: auto-split left crop",
            "Result: auto-split right crop",
        )
    return (
        "Result: full optimized image",
        "Result: full optimized image",
    )


def preview_assist_summary(
    apply_mode: str,
    l_display: tuple[int, int] | None,
    r_display: tuple[int, int] | None,
) -> str:
    normalized = str(apply_mode or "single-file").strip().lower()
    if normalized != "per-monitor-auto-split":
        return "Assist: same optimized image will be applied to both displays"

    left = _format_display(l_display)
    right = _format_display(r_display)
    if is_windows_host():
        if left and right:
            return f"Assist: Span preview L {left} | R {right}"
        return "Assist: wide image shown per monitor region (Span)"
    if left and right:
        return f"Assist: auto-split as L {left} | R {right}"
    return "Assist: auto-split by current left/right display widths"


def preview_state_label(apply_mode: str) -> str:
    normalized = str(apply_mode or "single-file").strip().lower()
    if normalized == "per-monitor-auto-split" and is_windows_host():
        return "Preview: wide image by monitor region (Span)"
    if normalized == "per-monitor-auto-split":
        return "Preview: pseudo auto-split by display widths"
    return "Preview: same image on both displays"


def margin_settings_split_label(two_screen: bool) -> str:
    if not two_screen:
        return "No Split"
    return "Span" if is_windows_host() else "Auto-Split"


def _format_display(display: tuple[int, int] | None) -> str | None:
    if display is None:
        return None
    return f"{display[0]}x{display[1]}"

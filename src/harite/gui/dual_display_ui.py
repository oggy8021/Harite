"""P-03: disable UI second slot (R) when a single display is detected."""

from __future__ import annotations

from typing import Any, Sequence

# Registry names (camelCase GTK aliases and snake_case Qt build keys).
SECOND_SLOT_WIDGET_NAMES: tuple[str, ...] = (
    # Main — direction cross + path + preview (R)
    "tglUpperR",
    "tglLowerR",
    "tglPushLeftR",
    "tglPushRightR",
    "btnGetImgR",
    "btnClrPathR",
    "cmbDisplayScaleR",
    "combo_display_scale_r",
    "entPathR",
    "imgPreviewR",
    "btnSwapInputPaths",
    "btn_swap_input_paths",
    # Slideshow — R source block (profile combo intentionally omitted)
    "btnOpenSrcdirR",
    "btnClrSrcdirR",
    "btn_clr_srcdir_r",
    "comboSlideshowSourceR",
    "combo_slideshow_source_r",
    "lblSlideshowSourceR",
    "btnSwapSlideshowSrcdirs",
    "btn_swap_slideshow_srcdirs",
)


def sync_second_slot_widget_enabled(
    backend: Any,
    *,
    second_slot_enabled: bool,
    widget_names: Sequence[str] = SECOND_SLOT_WIDGET_NAMES,
) -> None:
    """Enable or disable P-03 second-slot widgets on GTK/Qt backends."""
    for name in widget_names:
        if hasattr(backend, "_set_widget_slot_blocked"):
            backend._set_widget_slot_blocked(name, blocked=not second_slot_enabled)
        elif hasattr(backend, "_set_widget_enabled"):
            backend._set_widget_enabled(name, second_slot_enabled)
        elif hasattr(backend, "_set_button_enabled"):
            backend._set_button_enabled(name, second_slot_enabled)


def sync_dual_display_slot_availability_from_owner(backend: Any, owner: Any) -> None:
    dual = bool(getattr(owner, "dual_display_available", True))
    sync_second_slot_widget_enabled(backend, second_slot_enabled=dual)

"""Qt widget helper functions for Harite GUI (Phase 8).

Free functions that operate on the widget registry
(``backend._objects``) using Qt-specific APIs.

These mirror the GTK equivalents in ``gtk_runtime_state_labels.py`` and
scattered ``set_*`` / ``read_*`` helpers in ``gtk_backend.py``, but use
Qt widget API instead of GTK.

All functions accept ``backend`` (any object with ``._objects: dict``)
and delegate silently if the named widget is not found.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any

from harite.gui.adapters.gtk_runtime_file_dialog_flow import format_slideshow_path_display
from harite.gui.views.main_window import REGISTRY_NONE_LABEL


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get(backend: Any, name: str) -> Any:
    return backend._objects.get(name)


@contextmanager
def _with_blocked_signals(widget: Any):
    """Block Qt signals while mutating widget state programmatically."""
    if widget is None or not hasattr(widget, "blockSignals"):
        yield
        return
    previous = widget.blockSignals(True)
    try:
        yield
    finally:
        widget.blockSignals(previous)


# ---------------------------------------------------------------------------
# Label / text
# ---------------------------------------------------------------------------


def set_label_text(backend: Any, name: str, value: object | None) -> None:
    w = _get(backend, name)
    if w is None:
        return
    text = str(value or "")
    if hasattr(w, "setText"):
        w.setText(text)


def set_status(backend: Any, message: str) -> None:
    set_label_text(backend, "lblStatus", message)


def set_error(backend: Any, message: str | None) -> None:
    set_label_text(backend, "lblError", message or "")


def set_feedback(backend: Any, *, phase: str, state: str, error: str | None = None) -> None:
    set_status(backend, f"{phase}: {state}")
    set_error(backend, error)


# ---------------------------------------------------------------------------
# Entry / text-edit
# ---------------------------------------------------------------------------


def set_entry_text(backend: Any, name: str, value: object | None) -> None:
    w = _get(backend, name)
    if w is None:
        return
    text = str(value or "")
    with _with_blocked_signals(w):
        if hasattr(w, "setPlainText"):
            w.setPlainText(text)
        elif hasattr(w, "setText"):
            w.setText(text)


def read_entry_text(backend: Any, name: str) -> str:
    w = _get(backend, name)
    if w is None:
        return ""
    if hasattr(w, "toPlainText"):
        return w.toPlainText()
    if hasattr(w, "text"):
        return w.text()
    return ""


# ---------------------------------------------------------------------------
# Spin box
# ---------------------------------------------------------------------------


def set_spin_value(backend: Any, name: str, value: int) -> None:
    w = _get(backend, name)
    if w is None:
        return
    if hasattr(w, "setValue"):
        with _with_blocked_signals(w):
            try:
                w.setValue(int(value))
            except Exception:
                pass


def read_spin_int(backend: Any, name: str) -> int:
    w = _get(backend, name)
    if w is None:
        return 0
    if hasattr(w, "value"):
        try:
            return int(w.value())
        except Exception:
            pass
    return 0


# ---------------------------------------------------------------------------
# Buttons / toggle
# ---------------------------------------------------------------------------


def set_button_enabled(backend: Any, name: str, enabled: bool) -> None:
    w = _get(backend, name)
    if w is None:
        return
    if hasattr(w, "setEnabled"):
        w.setEnabled(bool(enabled))


def set_widget_enabled(backend: Any, name: str, enabled: bool) -> None:
    set_button_enabled(backend, name, enabled)


def set_toggle_active(backend: Any, name: str, active: bool) -> None:
    """Set checked state of QPushButton (checkable) or QRadioButton."""
    w = _get(backend, name)
    if w is None:
        return
    if hasattr(w, "setChecked"):
        with _with_blocked_signals(w):
            w.setChecked(bool(active))


def is_toggle_active(backend: Any, name: str) -> bool:
    w = _get(backend, name)
    if w is None:
        return False
    if hasattr(w, "isChecked"):
        return bool(w.isChecked())
    return False


# ---------------------------------------------------------------------------
# Tab widget
# ---------------------------------------------------------------------------


def set_notebook_page(backend: Any, name: str, page_index: int) -> None:
    w = _get(backend, name)
    if w is None:
        return
    if hasattr(w, "setCurrentIndex"):
        try:
            w.setCurrentIndex(int(page_index))
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Preview image (QLabel + QPixmap)
# ---------------------------------------------------------------------------


def set_preview_pixmap(
    backend: Any,
    name: str,
    source_path: Any,
    *,
    target_size: tuple[int, int] = (160, 90),
    crop_box: tuple[int, int, int, int] | None = None,
) -> None:
    """Load an image file and display it in a QLabel.

    Falls back silently if PyQt6 or the image file is not available.
    """
    w = _get(backend, name)
    if w is None:
        return
    try:
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QPixmap

        if source_path is None:
            w.clear()
            return
        pm = QPixmap(str(source_path))
        if pm.isNull():
            return
        if crop_box is not None:
            x, y, width, height = (int(value) for value in crop_box)
            pm = pm.copy(x, y, width, height)
        scaled = pm.scaled(
            target_size[0],
            target_size[1],
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        w.setPixmap(scaled)
    except Exception:
        pass


def clear_preview(backend: Any, name: str, message: str = "") -> None:
    w = _get(backend, name)
    if w is None:
        return
    if hasattr(w, "clear"):
        w.clear()
    if message and hasattr(w, "setText"):
        w.setText(message)


# ---------------------------------------------------------------------------
# Save-path state label
# ---------------------------------------------------------------------------

SAVE_PATH_STATE_ALIASES: tuple[str, ...] = ("lblSavePathState",)


def set_save_path_state_text(backend: Any, message: str) -> None:
    for alias in SAVE_PATH_STATE_ALIASES:
        set_label_text(backend, alias, message)
    set_label_text(backend, "save_path_state_label", message)


# ---------------------------------------------------------------------------
# Misc refresh helpers (called by gtk_runtime_sync.py through backend._*)
# ---------------------------------------------------------------------------


def format_input_display(path: str) -> str:
    """Truncate long paths for display in the path QLineEdit."""
    if not path:
        return ""
    if len(path) <= 60:
        return path
    return "…" + path[-57:]


def refresh_save_target_label(backend: Any, filename: str | None = None) -> None:
    if filename:
        set_label_text(backend, "lblSaveTarget", f"Export target: {filename}")
    else:
        set_label_text(backend, "lblSaveTarget", "Export target: not-selected")


def format_slideshow_srcdir_side_label(
    side: str,
    path: str,
    *,
    source_name: str | None = None,
) -> str:
    side_key = side.strip().upper()
    if not path.strip():
        return f"{side_key}: -"
    if source_name and source_name.strip():
        return f"{side_key}: {source_name.strip()}"
    return f"{side_key}: {format_input_display(path)}"


def refresh_slideshow_source_labels(backend: Any, owner: Any | None = None) -> None:
    catalog = None
    if owner is not None and hasattr(owner, "load_source_catalog"):
        try:
            catalog = owner.load_source_catalog()
        except Exception:
            catalog = None

    def _side_label(side_key: str, path: str, source_id: str) -> str:
        source_name = None
        if catalog is not None and source_id.strip():
            from harite.sources import get_source

            entry = get_source(catalog, source_id.strip())
            if entry is not None:
                source_name = entry.name
        return format_slideshow_srcdir_side_label(side_key, path, source_name=source_name)

    l_src = getattr(backend, "_slideshow_srcdir_l", "")
    r_src = getattr(backend, "_slideshow_srcdir_r", "")
    l_id = getattr(owner, "slideshow_source_id_l", "") if owner is not None else ""
    r_id = getattr(owner, "slideshow_source_id_r", "") if owner is not None else ""
    set_label_text(backend, "lblSlideshowSourceL", _side_label("L", l_src, l_id))
    set_label_text(backend, "lblSlideshowSourceR", _side_label("R", r_src, r_id))


def refresh_slideshow_mode_controls(backend: Any, owner: Any) -> None:
    enabled = bool(getattr(owner, "slideshow_mode_controls_enabled", True))
    for widget_key in ("rad_slideshow_mode_sequential", "rad_slideshow_mode_random"):
        widget = backend._objects.get(widget_key)
        if widget is not None:
            widget.setEnabled(enabled)
    if enabled:
        mode = str(getattr(owner, "slideshow_mode", "random") or "random")
        help_text = (
            "Sequential rotates images."
            if mode == "sequential"
            else "Random rotates images."
        )
        set_label_text(backend, "lblSlideshowModeHelp", help_text)
    else:
        set_label_text(
            backend,
            "lblSlideshowModeHelp",
            "Mode is fixed while a weather-map preset is selected (single image per side).",
        )


def refresh_slideshow_summary_label(backend: Any) -> None:
    running = bool(getattr(backend, "_slideshow_running", False))
    l_src = getattr(backend, "_slideshow_srcdir_l", "")
    r_src = getattr(backend, "_slideshow_srcdir_r", "")
    has_src = bool(l_src or r_src)
    if running:
        text = "Slideshow: running"
    elif has_src:
        text = "Slideshow: ready"
    else:
        text = "Slideshow: no source"
    set_label_text(backend, "lblSlideshowSummary", text)


def refresh_slideshow_current_label(
    backend: Any,
    left: str | None = None,
    right: str | None = None,
) -> None:
    state_l = left or str(getattr(backend, "_slideshow_previous_l", None) or "-")
    state_r = right or str(getattr(backend, "_slideshow_previous_r", None) or "-")
    if not getattr(backend, "_slideshow_running", False) and state_l == "-" and state_r == "-":
        set_label_text(backend, "lblSlideshowCurrent", "Slideshow current: idle")
        return
    text = (
        f"Slideshow current: L={format_slideshow_path_display(state_l)}"
        f" | R={format_slideshow_path_display(state_r)}"
    )
    set_label_text(backend, "lblSlideshowCurrent", text)


def format_slideshow_output_label_text(output_dir: str | None) -> tuple[str, str]:
    """Return (on-screen label, full path for tooltip)."""
    full = str(output_dir or ".").strip() or "."
    if full == ".":
        return "Slideshow output: .", ""
    return f"Slideshow output: {format_input_display(full)}", full


def refresh_slideshow_output_label(backend: Any, output_dir: str | None = None) -> None:
    text, tooltip = format_slideshow_output_label_text(output_dir)
    set_label_text(backend, "lblSlideshowOutput", text)
    widget = _get(backend, "lblSlideshowOutput")
    if widget is not None and hasattr(widget, "setToolTip"):
        widget.setToolTip(tooltip if tooltip else "")


def _normalize_combo_data(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _set_combo_current_data(combo: Any, value: str) -> None:
    if combo is None:
        return
    target = _normalize_combo_data(value)
    for index in range(combo.count()):
        if _normalize_combo_data(combo.itemData(index)) == target:
            combo.setCurrentIndex(index)
            return
    combo.setCurrentIndex(0)


def refresh_slideshow_registry_combos(backend: Any, owner: Any) -> None:
    from harite.gui.adapters_qt.qt_source_catalog import (
        prepare_owner_source_catalog,
        slideshow_profile_combo_label,
        slideshow_source_combo_label,
    )
    from harite.sources import list_profiles, list_sources

    setattr(backend, "_slideshow_registry_combo_refresh", True)
    try:
        catalog = prepare_owner_source_catalog(owner)

        profile_combo = backend._objects.get("combo_slideshow_profile")
        if profile_combo is not None:
            profile_combo.blockSignals(True)
            profile_combo.clear()
            profile_combo.addItem(REGISTRY_NONE_LABEL, "")
            for entry in list_profiles(catalog):
                profile_combo.addItem(slideshow_profile_combo_label(catalog, entry), entry.id)
            profile_id = _normalize_combo_data(getattr(owner, "slideshow_profile_id", ""))
            _set_combo_current_data(profile_combo, profile_id)
            profile_combo.blockSignals(False)

        for widget_key, id_attr in (
            ("combo_slideshow_source_l", "slideshow_source_id_l"),
            ("combo_slideshow_source_r", "slideshow_source_id_r"),
        ):
            combo = backend._objects.get(widget_key)
            if combo is None:
                continue
            combo.blockSignals(True)
            combo.clear()
            combo.addItem(REGISTRY_NONE_LABEL, "")
            for entry in list_sources(catalog):
                combo.addItem(slideshow_source_combo_label(entry), entry.id)
            source_id = _normalize_combo_data(getattr(owner, id_attr, ""))
            _set_combo_current_data(combo, source_id)
            combo.blockSignals(False)
    finally:
        setattr(backend, "_slideshow_registry_combo_refresh", False)


def refresh_current_state_labels(backend: Any) -> None:
    """Refresh the Margins tab 'current state' summary."""
    lm = read_spin_int(backend, "spnLeftMargin")
    rm = read_spin_int(backend, "spnRightMargin")
    tm = read_spin_int(backend, "spnTopMargin")
    bm = read_spin_int(backend, "spnBottomMargin")
    summary = f"align=center,center/center,center  margins={lm},{rm},{tm},{bm}"
    set_label_text(backend, "current_state_summary_display", summary)
    set_label_text(backend, "lblCurrentMargins", f"margins={lm},{rm},{tm},{bm}")

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


def set_preview_pixmap(backend: Any, name: str, source_path: Any, *, target_size: tuple[int, int] = (160, 90)) -> None:
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


def refresh_slideshow_source_labels(backend: Any) -> None:
    l_src = getattr(backend, "_slideshow_srcdir_l", "")
    r_src = getattr(backend, "_slideshow_srcdir_r", "")
    set_label_text(backend, "lblSlideshowSourceL", f"L: {l_src or '-'}")
    set_label_text(backend, "lblSlideshowSourceR", f"R: {r_src or '-'}")


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
    state_l = left or str(getattr(backend, "_slideshow_state_l", None) or "idle")
    state_r = right or str(getattr(backend, "_slideshow_state_r", None) or "idle")
    text = f"Slideshow current: L={state_l}  R={state_r}"
    set_label_text(backend, "lblSlideshowCurrent", text)


def refresh_slideshow_output_label(backend: Any, output_dir: str | None = None) -> None:
    text = f"Slideshow output: {output_dir or '.'}"
    set_label_text(backend, "lblSlideshowOutput", text)


def refresh_current_state_labels(backend: Any) -> None:
    """Refresh the Margins tab 'current state' summary."""
    lm = read_spin_int(backend, "spnLeftMargin")
    rm = read_spin_int(backend, "spnRightMargin")
    tm = read_spin_int(backend, "spnTopMargin")
    bm = read_spin_int(backend, "spnBottomMargin")
    summary = f"align=center,center/center,center  margins={lm},{rm},{tm},{bm}"
    set_label_text(backend, "current_state_summary_display", summary)
    set_label_text(backend, "lblCurrentMargins", f"margins={lm},{rm},{tm},{bm}")

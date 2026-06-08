from __future__ import annotations

from pathlib import Path
from typing import Any

from harite.gui.adapters.gtk_runtime_file_dialog_flow import (
    format_input_display,
    format_slideshow_path_display,
)


def commit_slideshow_interval_from_spin(backend: Any) -> int:
    """Apply the Interval spin value to owner state (may not have fired value-changed yet)."""
    interval_seconds = 0
    reader = getattr(backend, "_read_spin_int", None)
    if callable(reader):
        try:
            interval_seconds = int(reader("spnInterval"))
        except (TypeError, ValueError):
            interval_seconds = 0
    else:
        interval_widget = backend._objects.get("spnInterval")
        if interval_widget is not None and hasattr(interval_widget, "get_value_as_int"):
            interval_seconds = int(interval_widget.get_value_as_int())

    if interval_seconds > 0:
        callback = backend._signal_handlers.get("on_slideshow_interval_change")
        if callback is not None:
            try:
                callback(interval_seconds)
            except (TypeError, ValueError):
                pass
    return interval_seconds


def format_slideshow_srcdir_side_label(
    side: str,
    path: str,
    *,
    source_name: str | None = None,
) -> str:
    side_key = side.strip().upper()
    if not str(path or "").strip():
        return f"{side_key}: -"
    if source_name and source_name.strip():
        return f"{side_key}: {source_name.strip()}"
    return f"{side_key}: {format_input_display(path)}"


def _set_slideshow_srcdir_label(
    backend: Any,
    *,
    object_name: str,
    snake_key: str,
    text: str,
    full_path: str,
) -> None:
    backend._set_label_text(object_name, text)
    widget = backend._objects.get(object_name) or backend._objects.get(snake_key)
    if widget is None:
        return
    tooltip = str(full_path).strip() if str(full_path).strip() else ""
    if hasattr(widget, "set_tooltip_text"):
        widget.set_tooltip_text(tooltip)
    elif hasattr(widget, "setToolTip"):
        widget.setToolTip(tooltip)


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

    left_path = str(getattr(backend, "_slideshow_srcdir_l", "") or "")
    right_path = str(getattr(backend, "_slideshow_srcdir_r", "") or "")
    left_id = str(getattr(owner, "slideshow_source_id_l", "") or "") if owner is not None else ""
    right_id = str(getattr(owner, "slideshow_source_id_r", "") or "") if owner is not None else ""
    _set_slideshow_srcdir_label(
        backend,
        object_name="lblSlideshowSourceL",
        snake_key="slideshow_source_label_l",
        text=_side_label("L", left_path, left_id),
        full_path=left_path,
    )
    _set_slideshow_srcdir_label(
        backend,
        object_name="lblSlideshowSourceR",
        snake_key="slideshow_source_label_r",
        text=_side_label("R", right_path, right_id),
        full_path=right_path,
    )


def refresh_slideshow_summary_label(backend: Any) -> None:
    state = "paused" if getattr(backend, "_slideshow_paused", False) and backend._slideshow_running else ("running" if backend._slideshow_running else "stopped")
    backend._set_label_text("lblSlideshowSummary", f"Slideshow: {state}")
    backend._set_label_text("lblSlideshowTabTitle", f"Slideshow ({state})")


def refresh_slideshow_current_label(backend: Any, left: str | None = None, right: str | None = None) -> None:
    current_left = left if left is not None else (str(backend._slideshow_previous_l) if backend._slideshow_previous_l else "-")
    current_right = right if right is not None else (str(backend._slideshow_previous_r) if backend._slideshow_previous_r else "-")
    if not backend._slideshow_running and current_left == "-" and current_right == "-":
        backend._set_label_text("lblSlideshowCurrent", "Slideshow current: idle")
        return
    backend._set_label_text(
        "lblSlideshowCurrent",
        f"Slideshow current: L={format_slideshow_path_display(current_left)} | R={format_slideshow_path_display(current_right)}",
    )


def refresh_slideshow_output_label(backend: Any, output_dir: str | None = None) -> None:
    from harite.gui.adapters_qt.qt_widget_helpers import format_slideshow_output_label_text

    text, tooltip = format_slideshow_output_label_text(output_dir)
    backend._set_label_text("lblSlideshowOutput", text)
    widget = backend._objects.get("lblSlideshowOutput") or backend._objects.get("slideshow_output_label")
    if widget is not None and hasattr(widget, "setToolTip"):
        widget.setToolTip(tooltip if tooltip else "")


def on_slideshow_interval_changed(backend: Any, widget: Any) -> None:
    callback = backend._signal_handlers.get("on_slideshow_interval_change")
    if callback is None:
        backend._set_feedback(phase="Slideshow", state="handler-missing", error="handler not connected")
        return
    try:
        interval = 0
        if hasattr(widget, "get_value_as_int"):
            interval = int(widget.get_value_as_int())
        elif hasattr(widget, "get_value"):
            interval = int(widget.get_value())

        ok = callback(interval)

        if ok:
            backend._set_feedback(phase="Slideshow", state=f"interval-updated({interval}s)")
        else:
            backend._set_feedback(phase="Slideshow", state="interval-failed", error="interval returned false")
    except (TypeError, ValueError) as exc:
        backend._set_feedback(phase="Slideshow", state="error", error=str(exc))


def on_slideshow_start_clicked(backend: Any, *_args: Any) -> None:
    callback = backend._signal_handlers.get("on_slideshow_start")
    if callback is None:
        backend._set_feedback(phase="Slideshow", state="handler-missing", error="handler not connected")
        return
    try:
        commit_slideshow_interval_from_spin(backend)
        owner = backend._get_handler_owner("on_slideshow_start")
        ok = callback()
        if not ok:
            if owner is not None:
                backend._sync_slideshow_state_with_feedback_from_owner(owner)
            else:
                backend._set_feedback(phase="Slideshow", state="start-failed", error="slideshow start returned false")
            return

        if owner is not None:
            backend._sync_slideshow_state_only_from_owner(owner)
            interval_seconds = int(getattr(owner, "slideshow_interval_seconds", 0) or 0)
            backend._start_slideshow_timer(interval_seconds)
            backend._set_feedback(phase="Slideshow", state="started")
            return

        backend._slideshow_active_mode = str(getattr(backend, "slideshow_mode", "random") or "random")
        selected_left = "-"
        selected_right = "-"
        if backend._slideshow_srcdir_l:
            selected_left = backend._run_slideshow_cycle_for_side("L", Path(backend._slideshow_srcdir_l))
        if backend._slideshow_srcdir_r:
            selected_right = backend._run_slideshow_cycle_for_side("R", Path(backend._slideshow_srcdir_r))

        backend._slideshow_running = True
        refresh_slideshow_summary_label(backend)
        refresh_slideshow_source_labels(backend)
        refresh_slideshow_current_label(backend, selected_left, selected_right)
        interval_widget = backend._objects.get("spnInterval")
        interval_seconds = 0
        if interval_widget is not None and hasattr(interval_widget, "get_value_as_int"):
            interval_seconds = int(interval_widget.get_value_as_int())
        backend._start_slideshow_timer(interval_seconds)
        backend._set_feedback(phase="Slideshow", state="started")
    except TypeError as exc:
        backend._set_feedback(phase="Slideshow", state="error", error=str(exc))


def on_slideshow_stop_clicked(backend: Any, *_args: Any) -> None:
    callback = backend._signal_handlers.get("on_slideshow_stop")
    if callback is None:
        backend._set_feedback(phase="Slideshow", state="handler-missing", error="handler not connected")
        return
    try:
        ok = callback()
        if not ok:
            backend._set_feedback(phase="Slideshow", state="stop-ignored")
            return

        owner = backend._get_handler_owner("on_slideshow_stop")
        if owner is not None:
            backend._stop_slideshow_timer()
            backend._sync_slideshow_state_only_from_owner(owner)
            backend._set_feedback(phase="Slideshow", state="stopped")
            return

        backend._slideshow_running = False
        backend._slideshow_active_mode = str(getattr(backend, "slideshow_mode", "random") or "random")
        backend._stop_slideshow_timer()
        refresh_slideshow_summary_label(backend)
        refresh_slideshow_current_label(backend)
        backend._set_feedback(phase="Slideshow", state="stopped")
    except TypeError as exc:
        backend._set_feedback(phase="Slideshow", state="error", error=str(exc))
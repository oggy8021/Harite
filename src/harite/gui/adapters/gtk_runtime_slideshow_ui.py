from __future__ import annotations

from pathlib import Path
from typing import Any


def refresh_slideshow_source_labels(backend: Any) -> None:
    left = backend._slideshow_srcdir_l or "-"
    right = backend._slideshow_srcdir_r or "-"
    backend._set_label_text("lblSlideshowSourceL", f"L: {left}")
    backend._set_label_text("lblSlideshowSourceR", f"R: {right}")


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
    backend._set_label_text("lblSlideshowCurrent", f"Slideshow current: L={current_left} | R={current_right}")


def refresh_slideshow_output_label(backend: Any, output_dir: str | None = None) -> None:
    value = str(output_dir or "").strip() or "."
    backend._set_label_text("lblSlideshowOutput", f"Slideshow output: {value}")


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
from __future__ import annotations

from pathlib import Path
from typing import Any


def refresh_watch_source_labels(backend: Any) -> None:
    left = backend._watch_srcdir_l or "-"
    right = backend._watch_srcdir_r or "-"
    backend._set_label_text("lblWatchSourceL", f"L: {left}")
    backend._set_label_text("lblWatchSourceR", f"R: {right}")


def refresh_watch_summary_label(backend: Any) -> None:
    state = "paused" if getattr(backend, "_watch_paused", False) and backend._watch_running else ("running" if backend._watch_running else "stopped")
    backend._set_label_text("lblWatchSummary", f"Watch: {state}")
    backend._set_label_text("lblWatchTabTitle", f"Watch ({state})")


def refresh_watch_current_label(backend: Any, left: str | None = None, right: str | None = None) -> None:
    current_left = left if left is not None else (str(backend._watch_previous_l) if backend._watch_previous_l else "-")
    current_right = right if right is not None else (str(backend._watch_previous_r) if backend._watch_previous_r else "-")
    if not backend._watch_running and current_left == "-" and current_right == "-":
        backend._set_label_text("lblWatchCurrent", "Watch current: idle")
        return
    backend._set_label_text("lblWatchCurrent", f"Watch current: L={current_left} | R={current_right}")


def refresh_watch_output_label(backend: Any, output_dir: str | None = None) -> None:
    value = str(output_dir or "").strip() or "."
    backend._set_label_text("lblWatchOutput", f"Watch output: {value}")


def on_watch_interval_changed(backend: Any, widget: Any) -> None:
    callback = backend._signal_handlers.get("on_watch_interval_change")
    if callback is None:
        backend._set_feedback(phase="Watch", state="handler-missing", error="handler not connected")
        return
    try:
        interval = 0
        if hasattr(widget, "get_value_as_int"):
            interval = int(widget.get_value_as_int())
        elif hasattr(widget, "get_value"):
            interval = int(widget.get_value())

        ok = callback(interval)

        if ok:
            backend._set_feedback(phase="Watch", state=f"interval-updated({interval}s)")
        else:
            backend._set_feedback(phase="Watch", state="interval-failed", error="interval returned false")
    except (TypeError, ValueError) as exc:
        backend._set_feedback(phase="Watch", state="error", error=str(exc))


def on_watch_start_clicked(backend: Any, *_args: Any) -> None:
    callback = backend._signal_handlers.get("on_watch_start")
    if callback is None:
        backend._set_feedback(phase="Watch", state="handler-missing", error="handler not connected")
        return
    try:
        owner = backend._get_handler_owner("on_watch_start")
        ok = callback()
        if not ok:
            if owner is not None:
                backend._sync_watch_state_with_feedback_from_owner(owner)
            else:
                backend._set_feedback(phase="Watch", state="start-failed", error="watch start returned false")
            return

        if owner is not None:
            backend._sync_watch_state_only_from_owner(owner)
            interval_seconds = int(getattr(owner, "watch_interval_seconds", 0) or 0)
            backend._start_watch_timer(interval_seconds)
            backend._set_feedback(phase="Watch", state="started")
            return

        selected_left = "-"
        selected_right = "-"
        if backend._watch_srcdir_l:
            selected_left = backend._run_watch_cycle_for_side("L", Path(backend._watch_srcdir_l))
        if backend._watch_srcdir_r:
            selected_right = backend._run_watch_cycle_for_side("R", Path(backend._watch_srcdir_r))

        backend._watch_running = True
        refresh_watch_summary_label(backend)
        refresh_watch_source_labels(backend)
        refresh_watch_current_label(backend, selected_left, selected_right)
        interval_widget = backend._objects.get("spnInterval")
        interval_seconds = 0
        if interval_widget is not None and hasattr(interval_widget, "get_value_as_int"):
            interval_seconds = int(interval_widget.get_value_as_int())
        backend._start_watch_timer(interval_seconds)
        backend._set_feedback(phase="Watch", state="started")
    except TypeError as exc:
        backend._set_feedback(phase="Watch", state="error", error=str(exc))


def on_watch_stop_clicked(backend: Any, *_args: Any) -> None:
    callback = backend._signal_handlers.get("on_watch_stop")
    if callback is None:
        backend._set_feedback(phase="Watch", state="handler-missing", error="handler not connected")
        return
    try:
        ok = callback()
        if not ok:
            backend._set_feedback(phase="Watch", state="stop-ignored")
            return

        owner = backend._get_handler_owner("on_watch_stop")
        if owner is not None:
            backend._stop_watch_timer()
            backend._sync_watch_state_only_from_owner(owner)
            backend._set_feedback(phase="Watch", state="stopped")
            return

        backend._watch_running = False
        backend._stop_watch_timer()
        refresh_watch_summary_label(backend)
        refresh_watch_current_label(backend)
        backend._set_feedback(phase="Watch", state="stopped")
    except TypeError as exc:
        backend._set_feedback(phase="Watch", state="error", error=str(exc))
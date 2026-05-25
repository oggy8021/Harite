from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

from harite.slideshow import collect_slideshow_input_images, run_slideshow_cycle


def get_glib_module(backend: Any) -> Any | None:
    glib = getattr(backend._gtk, "GLib", None)
    if glib is not None:
        return glib
    try:
        gi = importlib.import_module("gi")
        gi.require_version("Gtk", "3.0")
        return importlib.import_module("gi.repository.GLib")
    except (ImportError, ValueError):
        return None


def stop_slideshow_timer(backend: Any) -> None:
    if backend._slideshow_timer_source_id is None:
        return

    glib = get_glib_module(backend)
    if glib is not None and hasattr(glib, "source_remove"):
        glib.source_remove(backend._slideshow_timer_source_id)
    backend._slideshow_timer_source_id = None


def on_slideshow_timer_event(backend: Any) -> bool:
    if not backend._slideshow_running:
        backend._slideshow_timer_source_id = None
        return False

    ok = backend.run_slideshow_cycle_once()
    if not ok or not backend._slideshow_running:
        backend._slideshow_timer_source_id = None
        return False
    return True


def start_slideshow_timer(backend: Any, interval_seconds: int) -> bool:
    stop_slideshow_timer(backend)

    glib = get_glib_module(backend)
    if glib is None or not hasattr(glib, "timeout_add"):
        return False

    interval_ms = max(1, int(interval_seconds)) * 1000
    backend._slideshow_timer_source_id = int(glib.timeout_add(interval_ms, backend._on_slideshow_timer_event))
    return True


def run_slideshow_cycle_for_side(backend: Any, side: str, source_dir: Path) -> str:
    images = collect_slideshow_input_images([source_dir])
    mode = str(getattr(backend, "_slideshow_active_mode", getattr(backend, "slideshow_mode", "random")) or "random")
    if side == "L":
        selected, state = run_slideshow_cycle(images, mode, backend._slideshow_state_l)
        backend._slideshow_state_l = state
        backend._slideshow_previous_l = selected
        return str(selected)

    selected, state = run_slideshow_cycle(images, mode, backend._slideshow_state_r)
    backend._slideshow_state_r = state
    backend._slideshow_previous_r = selected
    return str(selected)


def run_slideshow_cycle_once(backend: Any) -> bool:
    if not backend._slideshow_running:
        return False

    callback = backend._signal_handlers.get("on_slideshow_tick")
    if callback is not None:
        owner = backend._get_handler_owner("on_slideshow_tick")
        try:
            ok = bool(callback())
        except TypeError as exc:
            backend._set_feedback(phase="Slideshow", state="error", error=str(exc))
            return False
        if not ok:
            if owner is not None:
                backend._sync_slideshow_state_with_feedback_from_owner(owner)
            return False

        if owner is not None:
            if bool(getattr(owner, "_slideshow_feedback_dirty", False)):
                backend._sync_slideshow_state_with_feedback_from_owner(owner)
                owner._slideshow_feedback_dirty = False
            else:
                backend._sync_slideshow_state_only_from_owner(owner)
            return True

    selected_left = "-"
    selected_right = "-"
    if backend._slideshow_srcdir_l:
        try:
            selected_left = run_slideshow_cycle_for_side(backend, "L", Path(backend._slideshow_srcdir_l))
        except ValueError as exc:
            backend._set_feedback(phase="Slideshow", state="error", error=str(exc))
            return False
    if backend._slideshow_srcdir_r:
        try:
            selected_right = run_slideshow_cycle_for_side(backend, "R", Path(backend._slideshow_srcdir_r))
        except ValueError as exc:
            backend._set_feedback(phase="Slideshow", state="error", error=str(exc))
            return False

    backend._refresh_slideshow_current_label(selected_left, selected_right)
    return True
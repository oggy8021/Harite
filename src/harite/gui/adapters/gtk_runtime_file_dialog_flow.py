from __future__ import annotations

from pathlib import Path
from typing import Any


def set_save_path_dialog_open_state(backend: Any, opened: bool, *, state_text: str | None = None) -> None:
    dialog = backend._get_save_path_dialog()
    if dialog is not None:
        if opened and hasattr(dialog, "show"):
            dialog.show()
        if not opened and hasattr(dialog, "hide"):
            dialog.hide()

    if state_text is not None:
        backend._set_save_path_state_text(state_text)


def on_save_path_filename_changed(backend: Any, filename: str) -> None:
    backend._refresh_save_target_label(filename)
    if not is_save_path_dialog_open(backend):
        return
    if str(filename or "").strip():
        backend._set_save_path_state_text("Save path: ready")
    else:
        backend._set_save_path_state_text("Save path: required")


def is_save_path_dialog_open(backend: Any) -> bool:
    dialog = backend._get_save_path_dialog()
    if dialog is None or not hasattr(dialog, "is_visible"):
        return False
    return bool(dialog.is_visible())


def on_input_changed(backend: Any, entry: Any) -> None:
    callback = backend._signal_handlers.get("on_change_input_text")
    text_l = backend._input_path_l.strip()
    text_r = backend._input_path_r.strip()

    entry_l = backend._objects.get("entPathL")
    if not text_l and entry_l is not None and hasattr(entry_l, "get_text"):
        text_l = str(entry_l.get_text() or "").strip()

    entry_r = backend._objects.get("entPathR")
    if not text_r and entry_r is not None and hasattr(entry_r, "get_text"):
        text_r = str(entry_r.get_text() or "").strip()

    input_values = [value for value in (text_l, text_r) if value]
    text = ",".join(input_values)
    has_input = bool(input_values)
    backend._set_button_enabled("btnSave", has_input)
    backend._set_button_enabled("btnOptimize", has_input)
    backend._set_button_enabled("btnSetWall", False)
    if not has_input:
        set_save_path_dialog_open_state(backend, False, state_text="Save path: reset")
    backend._set_label_text("lblOptimizeResult", "Optimize result: not-run")
    backend._set_label_text("lblApplyTarget", "Apply target: not-ready")

    if callback is None:
        return

    try:
        callback(text)
        owner = backend._get_handler_owner("on_change_input_text")
        if owner is not None:
            backend._sync_preview_state_from_owner(owner)
        backend._set_feedback(phase="Input", state="updated")
    except Exception as exc:
        backend._set_feedback(phase="Input", state="failed", error=str(exc))


def on_pick_input_clicked(backend: Any, side: str) -> None:
    value = backend._input_path_l if side == "L" else backend._input_path_r

    dialog = backend._objects.get("ImgOpenDialog")
    if dialog is None or not hasattr(dialog, "open_for_side"):
        backend._set_label_text("lblPickState", f"Open-{side}: handler-missing")
        backend._set_feedback(
            phase=f"Open-{side}",
            state="handler-missing",
            error="open dialog not available",
        )
        return

    dialog.open_for_side(side, value)
    backend._set_label_text("lblPickState", f"Open-{side}: dialog-open")
    backend._set_feedback(phase=f"Open-{side}", state="dialog-open")


def notify_open_dialog_destroy(backend: Any) -> None:
    callback = backend._signal_handlers.get("on_close_open_image_dialog")
    if callback is None:
        return
    try:
        callback()
    except Exception:
        pass


def on_open_dialog_confirmed(backend: Any) -> None:
    dialog = backend._objects.get("ImgOpenDialog")
    if dialog is None:
        backend._set_feedback(phase="Open", state="error", error="open dialog not available")
        return

    side = "L"
    if hasattr(dialog, "get_side"):
        side = str(dialog.get_side() or "L").upper()

    filename = ""
    if hasattr(dialog, "get_filename"):
        filename = str(dialog.get_filename() or "").strip()

    if not filename:
        backend._set_label_text("lblPickState", f"Open-{side}: awaiting-selection")
        backend._set_feedback(
            phase=f"Open-{side}",
            state="awaiting-selection",
            error="image selection required",
        )
        return

    callback = backend._signal_handlers.get("on_pick_input")
    if callback is None:
        backend._set_label_text("lblPickState", f"Open-{side}: handler-missing")
        backend._set_feedback(
            phase=f"Open-{side}",
            state="handler-missing",
            error="handler not connected",
        )
        return

    try:
        callback(filename, side)
        owner = backend._get_handler_owner("on_pick_input")
        if owner is not None:
            backend._sync_input_preview_state_from_owner(owner)
        else:
            entry_name = "entPathL" if side == "L" else "entPathR"
            if side == "L":
                backend._input_path_l = filename
            else:
                backend._input_path_r = filename
            entry = backend._objects.get(entry_name)
            if entry is not None and hasattr(entry, "set_text"):
                entry.set_text(format_input_display(filename))
        if hasattr(dialog, "hide"):
            dialog.hide()
        backend._set_label_text("lblPickState", f"Open-{side}: selected")
        backend._set_feedback(phase=f"Open-{side}", state="selected")
        notify_open_dialog_destroy(backend)
    except Exception as exc:
        backend._set_label_text("lblPickState", f"Open-{side}: error")
        backend._set_feedback(phase=f"Open-{side}", state="error", error=str(exc))


def on_open_dialog_canceled(backend: Any, destroyed: bool = False) -> None:
    dialog = backend._objects.get("ImgOpenDialog")
    side = "L"
    if dialog is not None:
        if hasattr(dialog, "get_side"):
            side = str(dialog.get_side() or "L").upper()
        if hasattr(dialog, "hide"):
            dialog.hide()

    state = "closed" if destroyed else "canceled"
    backend._set_label_text("lblPickState", f"Open-{side}: {state}")
    backend._set_feedback(phase=f"Open-{side}", state=state)
    notify_open_dialog_destroy(backend)


def format_input_display(path: str) -> str:
    value = str(path or "").strip()
    if not value:
        return ""
    try:
        name = Path(value).name or value
    except Exception:
        return value

    max_length = 36
    if len(name) <= max_length:
        return name

    tail_length = 12
    head_length = max_length - tail_length - 3
    if head_length < 8:
        head_length = 8
        tail_length = max(4, max_length - head_length - 3)
    return f"{name[:head_length]}...{name[-tail_length:]}"


def on_clear_input_clicked(backend: Any, side: str) -> None:
    callback = backend._signal_handlers.get("on_clear_input")
    if callback is None:
        backend._set_feedback(phase=f"Clear-{side}", state="handler-missing", error="handler not connected")
        return

    try:
        callback(side)
        owner = backend._get_handler_owner("on_clear_input")
        if owner is not None:
            backend._sync_input_preview_state_from_owner(owner, include_feedback=True)
        else:
            backend._set_feedback(phase=f"Clear-{side}", state="ok")
    except TypeError:
        try:
            callback()
            owner = backend._get_handler_owner("on_clear_input")
            if owner is not None:
                backend._sync_input_preview_state_from_owner(owner, include_feedback=True)
            else:
                backend._set_feedback(phase=f"Clear-{side}", state="ok")
        except Exception as exc:
            backend._set_feedback(phase=f"Clear-{side}", state="failed", error=str(exc))
    except Exception as exc:
        backend._set_feedback(phase=f"Clear-{side}", state="failed", error=str(exc))


def current_srcdir_for_side(backend: Any, side: str) -> str:
    return backend._watch_srcdir_l if side == "L" else backend._watch_srcdir_r


def on_pick_srcdir_clicked(backend: Any, side: str) -> None:
    dialog = backend._objects.get("SrcdirDialog")
    if dialog is None or not hasattr(dialog, "open_for_side"):
        backend._set_feedback(
            phase=f"Srcdir-{side}",
            state="handler-missing",
            error="srcdir dialog not available",
        )
        return

    dialog.open_for_side(side, current_srcdir_for_side(backend, side))
    backend._set_feedback(phase=f"Srcdir-{side}", state="dialog-open")


def on_srcdir_dialog_confirmed(backend: Any) -> None:
    dialog = backend._objects.get("SrcdirDialog")
    if dialog is None:
        backend._set_feedback(phase="Srcdir", state="error", error="srcdir dialog not available")
        return

    side = "L"
    if hasattr(dialog, "get_side"):
        side = str(dialog.get_side() or "L").upper()

    folder = ""
    if hasattr(dialog, "get_current_folder"):
        folder = str(dialog.get_current_folder() or "").strip()

    if not folder:
        backend._set_feedback(
            phase=f"Srcdir-{side}",
            state="awaiting-selection",
            error="source directory is required",
        )
        return

    callback = backend._signal_handlers.get("on_pick_watch_srcdir")
    if callback is None:
        backend._set_feedback(
            phase=f"Srcdir-{side}",
            state="handler-missing",
            error="handler not connected",
        )
        return

    try:
        ok = callback(folder, side)
        if not ok:
            backend._set_feedback(
                phase=f"Srcdir-{side}",
                state="select-failed",
                error="srcdir selection returned false",
            )
            return

        if side == "L":
            backend._watch_srcdir_l = folder
        else:
            backend._watch_srcdir_r = folder
        backend._refresh_watch_source_labels()
        if hasattr(dialog, "hide"):
            dialog.hide()
        backend._set_feedback(phase=f"Srcdir-{side}", state="selected")
        backend._notify_srcdir_dialog_destroy()
    except Exception as exc:
        backend._set_feedback(phase=f"Srcdir-{side}", state="error", error=str(exc))


def on_srcdir_dialog_canceled(backend: Any, destroyed: bool = False) -> None:
    dialog = backend._objects.get("SrcdirDialog")
    side = "L"
    if dialog is not None:
        if hasattr(dialog, "get_side"):
            side = str(dialog.get_side() or "L").upper()
        if hasattr(dialog, "hide"):
            dialog.hide()
    state = "closed" if destroyed else "canceled"
    backend._set_feedback(phase=f"Srcdir-{side}", state=state)
    backend._notify_srcdir_dialog_destroy()


def handle_save_path_confirm(backend: Any, filename: str) -> None:
    callback = backend._signal_handlers.get("on_save_path_selected")
    if callback is None:
        backend._set_feedback(phase="SavePath", state="handler-missing", error="handler not connected")
        return
    try:
        if not filename:
            backend._set_save_path_state_text("Save path: required")
            backend._set_feedback(phase="SavePath", state="path-required", error="save path is required")
            return
        backend._refresh_save_target_label(filename)
        ok = callback(filename)
        if ok:
            set_save_path_dialog_open_state(backend, False, state_text="Save path: saved")
            backend._set_feedback(phase="SavePath", state="saved")
            backend._notify_save_path_dialog_destroy()
        else:
            backend._set_feedback(phase="SavePath", state="failed", error="save path acceptance returned false")
    except Exception as exc:
        backend._set_feedback(phase="SavePath", state="error", error=str(exc))


def handle_save_path_cancel(backend: Any) -> None:
    callback = backend._signal_handlers.get("on_save_path_selection_canceled")
    if callback is not None:
        try:
            callback()
        except Exception as exc:
            backend._set_feedback(phase="SavePath", state="error", error=str(exc))
            return
    set_save_path_dialog_open_state(backend, False, state_text="Save path: canceled")
    backend._set_feedback(phase="SavePath", state="canceled")
    backend._notify_save_path_dialog_destroy()


def on_native_save_path_confirmed(backend: Any) -> None:
    handle_save_path_confirm(backend, backend._current_save_path_filename())


def on_native_save_path_canceled(backend: Any) -> None:
    handle_save_path_cancel(backend)
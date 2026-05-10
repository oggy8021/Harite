from __future__ import annotations

from typing import Any, Callable

from harite.gui.adapters.gtk_runtime_object_registry import SAVE_PATH_DIALOG_OBJECT_ALIASES
from harite.gui.adapters.gtk_runtime_object_registry import SAVE_PATH_STATE_LABEL_ALIASES


SAVE_PATH_DESTROY_HANDLER_NAMES: tuple[str, ...] = (
    "on_close_save_path_dialog",
)


def get_save_path_dialog(backend: Any) -> Any | None:
    for object_name in SAVE_PATH_DIALOG_OBJECT_ALIASES:
        dialog = backend._objects.get(object_name)
        if dialog is not None:
            return dialog
    return None


def get_save_path_destroy_callback(backend: Any) -> Callable[..., Any] | None:
    for handler_name in SAVE_PATH_DESTROY_HANDLER_NAMES:
        callback = backend._signal_handlers.get(handler_name)
        if callback is not None:
            return callback
    return None


def set_save_path_state_text(backend: Any, message: str) -> None:
    for object_name in SAVE_PATH_STATE_LABEL_ALIASES:
        if backend._objects.get(object_name) is not None:
            backend._set_label_text(object_name, message)
            return


def current_save_path_filename(backend: Any) -> str:
    dialog = get_save_path_dialog(backend)
    if dialog is None or not hasattr(dialog, "get_filename"):
        return ""
    return str(dialog.get_filename() or "").strip()


def refresh_save_target_label(backend: Any, filename: str | None = None) -> None:
    value = str(filename or "").strip()
    if not value:
        value = current_save_path_filename(backend)
    if value:
        backend._set_label_text("lblSaveTarget", f"Save target: {value}")
        return
    backend._set_label_text("lblSaveTarget", "Save target: not-selected")
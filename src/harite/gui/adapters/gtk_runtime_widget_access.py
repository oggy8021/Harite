from __future__ import annotations

from typing import Any


def set_status(backend: Any, message: str) -> None:
    status = backend._objects.get("lblStatus")
    if status is not None and hasattr(status, "set_text"):
        status.set_text(message)


def set_error(backend: Any, message: str | None) -> None:
    if not message:
        set_label_text(backend, "lblError", "Error: none")
        return
    set_label_text(backend, "lblError", f"Error: {message}")


def set_feedback(backend: Any, *, phase: str, state: str, error: str | None = None) -> None:
    set_status(backend, f"{phase}: {state}")
    set_error(backend, error)


def set_label_text(backend: Any, object_name: str, message: str) -> None:
    label = backend._objects.get(object_name)
    if label is not None and hasattr(label, "set_text"):
        label.set_text(message)


def set_entry_text(backend: Any, object_name: str, value: object | None) -> None:
    entry = backend._objects.get(object_name)
    normalized = "" if value is None else str(value)
    if entry is not None and hasattr(entry, "get_text") and str(entry.get_text() or "") == normalized:
        return
    if entry is not None and hasattr(entry, "set_text"):
        entry.set_text(normalized)
        return
    if entry is not None and hasattr(entry, "get_buffer"):
        buffer = entry.get_buffer()
        if buffer is not None and hasattr(buffer, "get_text"):
            if hasattr(buffer, "get_bounds"):
                start, end = buffer.get_bounds()
            else:
                start = buffer.get_start_iter() if hasattr(buffer, "get_start_iter") else None
                end = buffer.get_end_iter() if hasattr(buffer, "get_end_iter") else None
            if str(buffer.get_text(start, end, True) or "") == normalized:
                return
        if buffer is not None and hasattr(buffer, "set_text"):
            buffer.set_text(normalized)


def read_entry_text(backend: Any, object_name: str) -> str:
    entry = backend._objects.get(object_name)
    if entry is None:
        return ""
    if hasattr(entry, "get_text"):
        return str(entry.get_text() or "").strip()
    if hasattr(entry, "get_buffer"):
        buffer = entry.get_buffer()
        if buffer is not None and hasattr(buffer, "get_text"):
            if hasattr(buffer, "get_bounds"):
                start, end = buffer.get_bounds()
            else:
                start = buffer.get_start_iter() if hasattr(buffer, "get_start_iter") else None
                end = buffer.get_end_iter() if hasattr(buffer, "get_end_iter") else None
            return str(buffer.get_text(start, end, True) or "").strip()
    return str(getattr(entry, "text", "") or "").strip()


def set_spin_value(backend: Any, object_name: str, value: int) -> None:
    spin = backend._objects.get(object_name)
    if spin is not None and hasattr(spin, "set_value"):
        spin.set_value(int(value))


def read_spin_int(backend: Any, object_name: str) -> int:
    spin = backend._objects.get(object_name)
    if spin is None:
        return 0
    if hasattr(spin, "get_value_as_int"):
        return int(spin.get_value_as_int())
    if hasattr(spin, "get_value"):
        return int(spin.get_value())
    return 0


def set_button_enabled(backend: Any, object_name: str, enabled: bool) -> None:
    button = backend._objects.get(object_name)
    if button is not None and hasattr(button, "set_sensitive"):
        button.set_sensitive(bool(enabled))


def set_widget_enabled(backend: Any, object_name: str, enabled: bool) -> None:
    widget = backend._objects.get(object_name)
    if widget is not None and hasattr(widget, "set_sensitive"):
        widget.set_sensitive(bool(enabled))


def set_notebook_page(backend: Any, object_name: str, page_index: int) -> None:
    notebook = backend._objects.get(object_name)
    if notebook is not None and hasattr(notebook, "set_current_page"):
        notebook.set_current_page(int(page_index))


def set_toggle_active(backend: Any, object_name: str, active: bool) -> None:
    toggle = backend._objects.get(object_name)
    if toggle is None:
        return
    if hasattr(toggle, "set_active"):
        toggle.set_active(bool(active))
        return
    setattr(toggle, "active", bool(active))


def is_toggle_active(backend: Any, object_name: str) -> bool:
    toggle = backend._objects.get(object_name)
    if toggle is None:
        return False
    if hasattr(toggle, "get_active"):
        return bool(toggle.get_active())
    return bool(getattr(toggle, "active", False))
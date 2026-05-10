from __future__ import annotations

import importlib
from typing import Any

from harite.gui.adapters.gtk_runtime_margin_text import read_margin_text_widget_text
from harite.gui.adapters.gtk_runtime_margin_text import should_block_margin_text_return


def apply_margin_text_widget_style(gtk_module: Any, shell: Any, entry: Any) -> None:
    try:
        gi = importlib.import_module("gi")
        gi.require_version("Gdk", "3.0")
        gdk_module = importlib.import_module("gi.repository.Gdk")

        rgba = gdk_module.RGBA()
        rgba.parse("#ffffff")
        state_flags = getattr(gtk_module, "StateFlags", None)
        normal_state = getattr(state_flags, "NORMAL", None) if state_flags is not None else None
        for widget in (shell, entry):
            if widget is not None and hasattr(widget, "override_background_color") and normal_state is not None:
                widget.override_background_color(normal_state, rgba)
    except Exception:
        return


def on_margin_text_key_press(widget: Any, event: Any, *, max_lines: int = 5) -> bool:
    keyval = getattr(event, "keyval", None)
    try:
        gi = importlib.import_module("gi")
        gi.require_version("Gdk", "3.0")
        gdk_module = importlib.import_module("gi.repository.Gdk")
        return_keys = {
            getattr(gdk_module, "KEY_Return", None),
            getattr(gdk_module, "KEY_KP_Enter", None),
        }
    except Exception:
        return False

    current = read_margin_text_widget_text(widget)
    return should_block_margin_text_return(
        keyval=keyval,
        return_keys=return_keys,
        current_text=current,
        max_lines=max_lines,
    )
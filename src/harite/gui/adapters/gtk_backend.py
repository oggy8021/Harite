"""GTK backend loader for optional UI signal binding.

This adapter is intentionally optional. It should only be used in environments
where PyGObject/GTK is available.
"""

from __future__ import annotations

from pathlib import Path


def load_gtk_builder_signal_backend(ui_file: Path):
    """Return a GTK Builder object that supports `connect_signals(mapping)`.

    Raises RuntimeError when GTK bindings are unavailable or the UI file cannot
    be loaded.
    """
    try:
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
    except Exception as exc:  # pragma: no cover - depends on host GTK runtime.
        raise RuntimeError(f"GTK backend unavailable: {exc}") from exc

    builder = Gtk.Builder()
    try:
        builder.add_from_file(str(ui_file))
    except Exception as exc:  # pragma: no cover - requires GTK runtime.
        raise RuntimeError(f"failed to load GTK builder from {ui_file}: {exc}") from exc

    return builder

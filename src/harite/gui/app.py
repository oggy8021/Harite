"""Standalone GUI app entrypoint (skeleton)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .views.main_window import MainWindow


def _should_load_ui_prototype(load_ui_prototype: bool | None) -> bool:
    if load_ui_prototype is not None:
        return load_ui_prototype
    raw = os.getenv("HARITE_GUI_LOAD_UI", "0").strip().lower()
    return raw in ("1", "true", "yes", "on")


def _should_bind_ui_backend(bind_ui_backend: bool | None) -> bool:
    if bind_ui_backend is not None:
        return bind_ui_backend
    raw = os.getenv("HARITE_GUI_BIND_SIGNALS", "0").strip().lower()
    return raw in ("1", "true", "yes", "on")


def _load_ui_signal_backend(ui_file: Path) -> Any:
    from .adapters.gtk_backend import load_gtk_builder_signal_backend

    return load_gtk_builder_signal_backend(ui_file)


def run(*, load_ui_prototype: bool | None = None, bind_ui_backend: bool | None = None) -> None:
    """Run standalone GUI skeleton.

    For now this is a placeholder entrypoint to keep CI green while
    GUI framework integration is being prepared.
    """
    loaded_result = None
    if _should_load_ui_prototype(load_ui_prototype):
        try:
            from .adapters.ui_loader import load_glade_prototype

            loaded_result = load_glade_prototype()
            print(
                f"UI prototype loaded: widgets={loaded_result.widget_count}, "
                f"signals={loaded_result.signal_count}"
            )
        except Exception as exc:
            # Keep entrypoint safe in headless or partial environments.
            print(f"UI prototype load skipped: {exc}")

    window = MainWindow()

    if loaded_result is not None:
        signal_backend = None
        if _should_bind_ui_backend(bind_ui_backend):
            try:
                signal_backend = _load_ui_signal_backend(loaded_result.file_path)
                print("UI signal backend ready")
            except Exception as exc:
                # Keep entrypoint safe when GTK/PyGObject is unavailable.
                print(f"UI signal backend skipped: {exc}")

        try:
            from .adapters.ui_adapter import bind_mainwindow

            bind_mainwindow(window, loaded_result, signal_backend=signal_backend)
        except Exception as exc:
            # Non-fatal: adapter binding is optional for prototype flow.
            print(f"UI adapter binding skipped: {exc}")

    window.show()


if __name__ == "__main__":
    run()

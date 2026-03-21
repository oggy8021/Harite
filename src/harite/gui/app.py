"""Standalone GUI app entrypoint (skeleton)."""

from __future__ import annotations

import os

from .views.main_window import MainWindow


def _should_load_ui_prototype(load_ui_prototype: bool | None) -> bool:
    if load_ui_prototype is not None:
        return load_ui_prototype
    raw = os.getenv("HARITE_GUI_LOAD_UI", "0").strip().lower()
    return raw in ("1", "true", "yes", "on")


def run(*, load_ui_prototype: bool | None = None) -> None:
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
        try:
            from .adapters.ui_adapter import bind_mainwindow

            bind_mainwindow(window, loaded_result)
        except Exception as exc:
            # Non-fatal: adapter binding is optional for prototype flow.
            print(f"UI adapter binding skipped: {exc}")

    window.show()


if __name__ == "__main__":
    run()

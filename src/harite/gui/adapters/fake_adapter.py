"""Fake adapter for Phase 3 integration tests.

This provides a tiny in-memory mapping of widget ids to callables that invoke
the `MainWindow` methods. It avoids any GUI toolkit dependency and enables
testing the "signal -> MainWindow" mapping end-to-end in unit tests.
"""

from __future__ import annotations

from typing import Any, Callable, Dict

from .ui_loader import UiLoadResult


def create_fake_widget_map(mainwindow: Any, ui_result: UiLoadResult) -> Dict[str, Callable[..., None]]:
    """Return a mapping of fake widget identifiers to callables.

    The names follow the legacy signal mapping conventions used in the
    codebase (e.g. `btnSave_clicked`, `entPath_insert_text`). Tests can call
    these callables to simulate user actions.
    """
    # Record metadata for inspection
    setattr(mainwindow, "_adapter_bindings", {
        "file": ui_result.file_path,
        "root_tag": ui_result.root_tag,
        "widget_count": ui_result.widget_count,
        "signal_count": ui_result.signal_count,
    })

    def plugin_change(name: str) -> None:
        mainwindow.on_change_plugin(name)

    def margins_change(left: int, right: int, top: int, bottom: int) -> None:
        mainwindow.on_change_margins(left, right, top, bottom)

    def toggle_fixed(enabled: bool) -> None:
        mainwindow.on_toggle_fixed(enabled)

    def input_text(text: str) -> None:
        mainwindow.on_change_input_text(text)

    return {
        "plugin_change": plugin_change,
        "margins_change": margins_change,
        "toggle_fixed": toggle_fixed,
        "input_text": input_text,
    }

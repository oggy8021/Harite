"""Minimal UI adapter bindings for Phase 3.

This module provides a tiny, framework-neutral binding entrypoint that maps a
loaded UI prototype (parsed metadata) onto a `MainWindow`-like object. The
implementation is intentionally minimal: it records binding metadata on the
target object so higher-level integration can be developed and tested without
pulling in GUI toolkit dependencies.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .ui_loader import UiLoadResult


def bind_mainwindow(mainwindow: Any, ui_result: UiLoadResult) -> None:
    """Bind a `MainWindow`-like object to the parsed UI prototype.

    For the prototype this simply stores binding metadata on the target object
    so tests and later adapter implementations can inspect the result.
    """
    metadata = {
        "file": Path(ui_result.file_path),
        "root_tag": ui_result.root_tag,
        "widget_count": ui_result.widget_count,
        "signal_count": ui_result.signal_count,
    }

    # Store on the target object using a private attribute to avoid changing
    # public APIs of `MainWindow` for now.
    setattr(mainwindow, "_adapter_bindings", metadata)

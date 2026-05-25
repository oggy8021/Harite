"""Standalone GUI app entrypoint."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from .views.main_window import MainWindow


_TRUTHY_ENV_VALUES = ("1", "true", "yes", "on")


def _exit_missing_gui_runtime(exc: RuntimeError) -> None:
    message = (
        "Harite GUI runtime is unavailable. "
        "Install GTK 3 / PyGObject on the host environment, or run with "
        "--no-bind-ui-backend --no-present-ui-window for fallback-only troubleshooting. "
        f"Details: {exc}"
    )
    raise SystemExit(message)


def _should_bind_ui_backend(bind_ui_backend: bool | None) -> bool:
    if bind_ui_backend is not None:
        return bind_ui_backend
    raw = os.getenv("HARITE_GUI_BIND_SIGNALS", "").strip().lower()
    if raw:
        return raw in _TRUTHY_ENV_VALUES
    return True


def _should_present_ui_window(present_ui_window: bool | None) -> bool:
    if present_ui_window is not None:
        return present_ui_window
    raw = os.getenv("HARITE_GUI_PRESENT_WINDOW", "").strip().lower()
    if raw:
        return raw in _TRUTHY_ENV_VALUES
    return True


def _get_ui_window_id() -> str:
    raw = os.getenv("HARITE_GUI_WINDOW_ID", "main_window").strip()
    return raw or "main_window"


def _load_ui_signal_backend() -> Any:
    from .adapters.gtk_backend import load_gtk_runtime_signal_backend

    return load_gtk_runtime_signal_backend()


def _initialize_tasktray(signal_backend: Any) -> Any | None:
    from .adapters.tasktray_adapter import initialize_tasktray

    return initialize_tasktray(signal_backend)


def _present_ui_window(signal_backend: Any) -> bool:
    from .adapters.gtk_backend import present_gtk_window

    window_id = _get_ui_window_id()
    return bool(present_gtk_window(signal_backend, window_id=window_id))


def run(
    *,
    bind_ui_backend: bool | None = None,
    present_ui_window: bool | None = None,
) -> None:
    """Run the standalone GUI entrypoint."""
    window = MainWindow()
    should_bind_ui_backend = _should_bind_ui_backend(bind_ui_backend)
    should_present_ui_window = _should_present_ui_window(present_ui_window)

    signal_backend = None
    presented = False

    if should_bind_ui_backend:
        try:
            signal_backend = _load_ui_signal_backend()
        except RuntimeError as exc:
            if should_present_ui_window:
                _exit_missing_gui_runtime(exc)
            pass

    if signal_backend is not None:
        try:
            from .adapters.ui_adapter import (
                RUNTIME_HANDLER_MAP,
                connect_signal_dispatch,
                create_mainwindow_signal_dispatch,
            )

            handlers = tuple(RUNTIME_HANDLER_MAP.keys())
            dispatch = create_mainwindow_signal_dispatch(
                window,
                handlers,
                handler_map=RUNTIME_HANDLER_MAP,
                signal_backend=signal_backend,
            )
            if dispatch:
                connect_signal_dispatch(signal_backend, dispatch)
                setattr(window, "_adapter_signal_dispatch", dispatch)
        except (ImportError, TypeError):
            # Non-fatal: runtime fallback should remain usable in partial environments.
            pass

        try:
            tasktray_adapter = _initialize_tasktray(signal_backend)
            if tasktray_adapter is not None:
                setattr(signal_backend, "_tasktray_adapter", tasktray_adapter)
                setattr(window, "_tasktray_adapter", tasktray_adapter)
        except RuntimeError:
            pass

    if signal_backend is not None and should_present_ui_window:
        try:
            presented = _present_ui_window(signal_backend)
            if presented:
                return
        except RuntimeError as exc:
            _exit_missing_gui_runtime(exc)

    window.show()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Harite standalone GUI app")
    parser.add_argument(
        "--bind-ui-backend",
        dest="bind_ui_backend",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="override backend signal binding for development or troubleshooting",
    )
    parser.add_argument(
        "--present-ui-window",
        dest="present_ui_window",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="override real GTK window presentation for development or troubleshooting",
    )
    args = parser.parse_args(argv)

    run(
        bind_ui_backend=args.bind_ui_backend,
        present_ui_window=args.present_ui_window,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Qt backend GUI entrypoint (harite-qt)."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from .views.main_window import MainWindow

_TRUTHY_ENV_VALUES = ("1", "true", "yes", "on")


def _exit_missing_qt_runtime(exc: RuntimeError) -> None:
    message = (
        "Harite Qt backend is unavailable. "
        "Install PyQt6 with: pip install 'harite[gui-qt]'  "
        "or: pip install PyQt6. "
        f"Details: {exc}"
    )
    raise SystemExit(message)


def _should_present_ui_window(present_ui_window: bool | None) -> bool:
    if present_ui_window is not None:
        return present_ui_window
    raw = os.getenv("HARITE_GUI_PRESENT_WINDOW", "").strip().lower()
    if raw:
        return raw in _TRUTHY_ENV_VALUES
    return True


def _load_qt_signal_backend() -> Any:
    from .adapters_qt.qt_backend import load_qt_runtime_signal_backend

    return load_qt_runtime_signal_backend()


def _initialize_tasktray(signal_backend: Any) -> Any | None:
    """Install QSystemTrayIcon when available; non-fatal if unavailable."""
    install = getattr(signal_backend, "install_tray", None)
    if install is None:
        return None
    try:
        if not install():
            return None
    except RuntimeError:
        return None
    return getattr(signal_backend, "tray_adapter", None)


def run(
    *,
    present_ui_window: bool | None = None,
) -> None:
    """Run the Qt backend GUI entrypoint."""
    window = MainWindow()
    should_present = _should_present_ui_window(present_ui_window)

    try:
        signal_backend = _load_qt_signal_backend()
    except RuntimeError as exc:
        if should_present:
            _exit_missing_qt_runtime(exc)
        window.show()
        return

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
        pass

    try:
        tasktray_adapter = _initialize_tasktray(signal_backend)
        if tasktray_adapter is not None:
            setattr(signal_backend, "_tasktray_adapter", tasktray_adapter)
            setattr(window, "_tasktray_adapter", tasktray_adapter)
        elif sys.platform.startswith("linux"):
            from harite.gui.adapters_qt.qt_tray_adapter import system_tray_unavailable_message

            print(system_tray_unavailable_message(), file=sys.stderr)
    except RuntimeError:
        pass

    if should_present:
        signal_backend.present()
    else:
        window.show()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Harite Qt backend GUI")
    parser.add_argument(
        "--present-ui-window",
        dest="present_ui_window",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="override Qt window presentation for development or troubleshooting",
    )
    args = parser.parse_args(argv)

    run(present_ui_window=args.present_ui_window)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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


def _register_application_quit_persistence(window: MainWindow, signal_backend: Any) -> None:
    qapp = getattr(signal_backend, "qapp", None)
    if qapp is None:
        return

    def _on_about_to_quit() -> None:
        window.on_prepare_application_quit()

    try:
        qapp.aboutToQuit.connect(_on_about_to_quit)
    except Exception:
        pass


def _schedule_startup_slideshow_if_needed(
    window: MainWindow,
    signal_backend: Any,
    *,
    startup_launch: bool,
) -> None:
    from harite.gui.startup_slideshow import should_auto_start_from_owner

    def _log_skip(reason: str) -> None:
        log = getattr(window, "_log", None)
        if callable(log):
            log(f"Startup slideshow auto-start skipped: {reason}")

    if not startup_launch:
        _log_skip("not a --startup-launch session")
        return
    if not should_auto_start_from_owner(window, is_startup_launch=startup_launch):
        _log_skip(
            "startup_slideshow, was_running_at_exit, or slideshow_running "
            "does not satisfy auto-start conditions"
        )
        return

    try:
        from PyQt6.QtCore import QTimer
    except ImportError:
        _log_skip("PyQt6 QTimer unavailable")
        return

    def _attempt() -> None:
        if not should_auto_start_from_owner(window, is_startup_launch=startup_launch):
            _log_skip("conditions changed before deferred auto-start")
            return
        start = getattr(signal_backend, "_on_slideshow_start_clicked", None)
        if start is None:
            _log_skip("Qt backend slideshow start handler unavailable")
            return
        log = getattr(window, "_log", None)
        if callable(log):
            log("Startup slideshow auto-start: invoking slideshow start")
        start()

    QTimer.singleShot(0, _attempt)


def run(
    *,
    present_ui_window: bool | None = None,
    startup_launch: bool | None = None,
) -> None:
    """Run the Qt backend GUI entrypoint."""
    from harite.gui.startup_slideshow import resolve_startup_launch

    window = MainWindow()
    should_present = _should_present_ui_window(present_ui_window)
    is_startup_launch = resolve_startup_launch(cli_flag=startup_launch)

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

    _register_application_quit_persistence(window, signal_backend)
    _schedule_startup_slideshow_if_needed(
        window,
        signal_backend,
        startup_launch=is_startup_launch,
    )

    if should_present:
        signal_backend.show_main_window()
    signal_backend.run_event_loop()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Harite Qt backend GUI")
    parser.add_argument(
        "--present-ui-window",
        dest="present_ui_window",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="override Qt window presentation for development or troubleshooting",
    )
    parser.add_argument(
        "--startup-launch",
        dest="startup_launch",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="mark this process as a session autostart launch (#518)",
    )
    args = parser.parse_args(argv)

    run(
        present_ui_window=args.present_ui_window,
        startup_launch=args.startup_launch,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

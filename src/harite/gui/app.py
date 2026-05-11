"""Standalone GUI app entrypoint (skeleton)."""

from __future__ import annotations

import argparse
import os
from typing import Any

from .views.main_window import MainWindow


_TRUTHY_ENV_VALUES = ("1", "true", "yes", "on")


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
    raw = os.getenv("HARITE_GUI_WINDOW_ID", "WallPosit_MainWindow").strip()
    return raw or "WallPosit_MainWindow"


def _load_ui_signal_backend() -> Any:
    from .adapters.gtk_backend import load_gtk_builder_signal_backend

    return load_gtk_builder_signal_backend()


def _present_ui_window(signal_backend: Any) -> bool:
    from .adapters.gtk_backend import present_gtk_window

    window_id = _get_ui_window_id()
    return bool(present_gtk_window(signal_backend, window_id=window_id))


def run(
    *,
    bind_ui_backend: bool | None = None,
    present_ui_window: bool | None = None,
) -> None:
    """Run standalone GUI skeleton.

    For now this is a placeholder entrypoint to keep CI green while
    GUI framework integration is being prepared.
    """
    window = MainWindow()

    signal_backend = None
    presented = False

    if _should_bind_ui_backend(bind_ui_backend):
        try:
            signal_backend = _load_ui_signal_backend()
            print("UI signal backend ready")
        except Exception as exc:
            # Keep entrypoint safe when GTK/PyGObject is unavailable.
            print(f"UI signal backend skipped: {exc}")

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
                print(f"UI runtime fallback dispatch ready: handlers={len(dispatch)}")
        except Exception as exc:
            # Non-fatal: runtime fallback should remain usable in partial environments.
            print(f"UI runtime fallback dispatch skipped: {exc}")

    if signal_backend is not None and _should_present_ui_window(present_ui_window):
        try:
            window_id = _get_ui_window_id()
            presented = _present_ui_window(signal_backend)
            if presented:
                return
            print(f"UI window presentation skipped: target window not found (id={window_id})")
        except Exception as exc:
            # Non-fatal in headless CI or partial GTK environments.
            print(f"UI window presentation skipped: {exc}")

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

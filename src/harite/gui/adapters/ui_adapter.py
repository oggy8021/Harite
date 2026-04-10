"""Minimal UI adapter bindings for Phase 3.

This module provides a tiny, framework-neutral binding entrypoint that maps a
loaded UI prototype (parsed metadata) onto a `MainWindow`-like object. The
implementation is intentionally minimal: it records binding metadata on the
target object so higher-level integration can be developed and tested without
pulling in GUI toolkit dependencies.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping

from .ui_loader import UiLoadResult


LEGACY_HANDLER_MAP: dict[str, str] = {
    "on_WallPosit_MainWindow_delete_event": "on_close",
    "on_spnMergin_value_changed": "on_change_margins",
    "on_radFixed_toggled": "on_toggle_fixed",
    "on_entPath_insert_text": "on_change_input_text",
    "on_btnSave_clicked": "on_optimize",
    "on_btnSetWall_clicked": "on_apply_dry_run",
    "on_btnGetImg_clicked": "on_pick_input",
    "on_ErrorDialog_destroy": "on_close_error_dialog",
    "on_ImgOpenDialog_destroy": "on_close_open_image_dialog",
    "on_SaveWallpaperDialog_destroy": "on_close_save_dialog",
    "on_SettingDialog_destroy": "on_close_settings_dialog",
    "on_ColorSelectionDialog_destroy": "on_close_color_dialog",
    "on_SrcdirDialog_destroy": "on_close_srcdir_dialog",
}


def _build_dispatch_callback(
    legacy_name: str,
    target: Callable[..., Any],
) -> Callable[..., Any]:
    """Build a GTK-tolerant callback for selected legacy handlers.

    Why:
        GtkBuilder から来るシグナル引数は handler ごとに形が異なるため、
        `MainWindow` の簡潔なメソッド署名へ最小限の変換が必要。
    """

    if legacy_name == "on_entPath_insert_text":

        def _on_insert_text(*args: Any) -> Any:
            # GTK insert-text commonly passes (editable, new_text, new_text_length, position)
            if len(args) >= 2 and isinstance(args[1], str):
                return target(args[1])
            if args and isinstance(args[0], str):
                return target(args[0])
            return target("")

        return _on_insert_text

    if legacy_name in ("on_btnSave_clicked", "on_btnSetWall_clicked"):

        def _on_clicked(*_args: Any) -> Any:
            return target()

        return _on_clicked

    return target


def create_mainwindow_signal_dispatch(
    mainwindow: Any,
    glade_handlers: tuple[str, ...],
    handler_map: Mapping[str, str] | None = None,
) -> dict[str, Callable[..., Any]]:
    """Create a legacy-handler to bound-method dispatch table.

    This table is the bridge for real widget binding in later steps:
    adapters can connect legacy signal handlers directly to callables from
    this mapping without importing toolkit-specific code here.
    """
    mapping = dict(handler_map or LEGACY_HANDLER_MAP)
    dispatch: dict[str, Callable[..., Any]] = {}

    for legacy_name, method_name in mapping.items():
        if legacy_name not in glade_handlers:
            continue
        target = getattr(mainwindow, method_name, None)
        if callable(target):
            dispatch[legacy_name] = _build_dispatch_callback(legacy_name, target)

    return dispatch


def connect_signal_dispatch(
    signal_backend: Any,
    dispatch: Mapping[str, Callable[..., Any]],
) -> dict[str, Any]:
    """Connect dispatch handlers to a backend-provided signal API.

    Supported backend styles:
    - `connect_signals(mapping)`
    - `connect(handler_name, callback)`
    """
    if hasattr(signal_backend, "connect_signals") and callable(signal_backend.connect_signals):
        signal_backend.connect_signals(dict(dispatch))
        return {
            "strategy": "connect_signals",
            "connected_handlers": tuple(sorted(dispatch.keys())),
            "connected_count": len(dispatch),
        }

    if hasattr(signal_backend, "connect") and callable(signal_backend.connect):
        for handler_name, callback in dispatch.items():
            signal_backend.connect(handler_name, callback)
        return {
            "strategy": "connect",
            "connected_handlers": tuple(sorted(dispatch.keys())),
            "connected_count": len(dispatch),
        }

    raise TypeError("signal backend must provide connect_signals(mapping) or connect(name, callback)")


def validate_mainwindow_signal_mapping(
    mainwindow: Any,
    glade_handlers: tuple[str, ...],
    handler_map: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Validate mapped legacy handlers against `MainWindow` methods."""
    mapping = dict(handler_map or LEGACY_HANDLER_MAP)

    missing_handlers_in_glade = [name for name in mapping if name not in glade_handlers]

    missing_methods: list[str] = []
    for legacy_name, method_name in mapping.items():
        if legacy_name in glade_handlers and not hasattr(mainwindow, method_name):
            missing_methods.append(method_name)

    return {
        "required_handlers": sorted(mapping.keys()),
        "present_handlers": sorted([name for name in mapping if name in glade_handlers]),
        "missing_handlers_in_glade": sorted(missing_handlers_in_glade),
        "missing_methods": sorted(set(missing_methods)),
        "ok": (not missing_handlers_in_glade and not missing_methods),
    }


def bind_mainwindow(
    mainwindow: Any,
    ui_result: UiLoadResult,
    signal_backend: Any | None = None,
) -> None:
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

    if ui_result.signal_handlers:
        metadata["mapping_validation"] = validate_mainwindow_signal_mapping(
            mainwindow,
            ui_result.signal_handlers,
        )
        dispatch = create_mainwindow_signal_dispatch(mainwindow, ui_result.signal_handlers)
        setattr(mainwindow, "_adapter_signal_dispatch", dispatch)
        metadata["dispatch_handlers"] = tuple(sorted(dispatch.keys()))
        if signal_backend is not None:
            metadata["signal_connection"] = connect_signal_dispatch(signal_backend, dispatch)

    # Store on the target object using a private attribute to avoid changing
    # public APIs of `MainWindow` for now.
    setattr(mainwindow, "_adapter_bindings", metadata)

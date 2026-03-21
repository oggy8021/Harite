"""Minimal UI adapter bindings for Phase 3.

This module provides a tiny, framework-neutral binding entrypoint that maps a
loaded UI prototype (parsed metadata) onto a `MainWindow`-like object. The
implementation is intentionally minimal: it records binding metadata on the
target object so higher-level integration can be developed and tested without
pulling in GUI toolkit dependencies.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

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

    if ui_result.signal_handlers:
        metadata["mapping_validation"] = validate_mainwindow_signal_mapping(
            mainwindow,
            ui_result.signal_handlers,
        )

    # Store on the target object using a private attribute to avoid changing
    # public APIs of `MainWindow` for now.
    setattr(mainwindow, "_adapter_bindings", metadata)

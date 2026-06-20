"""Minimal runtime UI adapter bindings."""

from __future__ import annotations

from typing import Any, Callable, Mapping

RUNTIME_HANDLER_MAP: dict[str, str] = {
    "on_open_settings_dialog": "on_open_settings_dialog",
    "on_get_settings": "on_get_settings",
    "on_apply_settings": "on_apply_settings",
    "on_load_settings_file": "on_load_settings_file",
    "on_save_settings_file": "on_save_settings_file",
    "on_change_input_text": "on_change_input_text",
    "on_save_as": "on_save_as",
    "on_optimize": "on_optimize",
    "on_apply": "on_apply",
    "on_change_apply_mode": "on_change_apply_mode",
    "on_change_slideshow_mode": "on_change_slideshow_mode",
    "on_change_margin_text_mode": "on_change_margin_text_mode",
    "on_change_margin_text": "on_change_margin_text",
    "on_change_margin_text_position": "on_change_margin_text_position",
    "on_change_margin_text_max_lines": "on_change_margin_text_max_lines",
    "on_slideshow_start": "on_slideshow_start",
    "on_slideshow_tick": "on_slideshow_tick",
    "on_slideshow_stop": "on_slideshow_stop",
    "on_slideshow_interval_change": "on_slideshow_interval_change",
    "on_pick_slideshow_srcdir": "on_pick_slideshow_srcdir",
    "on_pick_input": "on_pick_input",
    "on_clear_input": "on_clear_input",
    "on_swap_input_paths": "on_swap_input_paths",
    "on_swap_slideshow_srcdirs": "on_swap_slideshow_srcdirs",
    "on_clear_slideshow_srcdir": "on_clear_slideshow_srcdir",
    "on_select_slideshow_source": "on_select_slideshow_source",
    "on_select_slideshow_profile": "on_select_slideshow_profile",
    "on_manage_source_registry": "on_manage_source_registry",
    "on_source_catalog_saved": "on_source_catalog_saved",
    "on_about": "on_about",
    "on_set_color": "on_set_color",
    "on_toggle_position_pressed": "on_toggle_position_pressed",
    "on_toggle_position": "on_toggle_position",
    "on_toggle_position_reset": "on_toggle_position_reset",
    "on_change_margins": "on_change_margins",
    "on_change_display_scale": "on_change_display_scale",
    "on_change_auto_display_scale": "on_change_auto_display_scale",
    "on_change_slideshow_auto_display_scale": "on_change_slideshow_auto_display_scale",
    "on_change_startup_slideshow": "on_change_startup_slideshow",
    "on_save_path_selection_canceled": "on_save_path_selection_canceled",
    "on_save_path_selected": "on_save_path_selected",
    "on_close_save_path_dialog": "on_close_save_path_dialog",
    "on_close_open_image_dialog": "on_close_open_image_dialog",
    "on_close_srcdir_dialog": "on_close_srcdir_dialog",
    "on_close_error_dialog": "on_close_error_dialog",
    "on_close_settings_dialog": "on_close_settings_dialog",
    "on_close_color_dialog": "on_close_color_dialog",
    "on_get_about_dialog_info": "on_get_about_dialog_info",
    "on_close_about_dialog": "on_close_about_dialog",
}


def create_mainwindow_signal_dispatch(
    mainwindow: Any,
    handler_names: tuple[str, ...],
    handler_map: Mapping[str, str] | None = None,
    *,
    signal_backend: Any | None = None,
) -> dict[str, Callable[..., Any]]:
    """Create a runtime handler-name to bound-method dispatch table."""
    mapping = dict(handler_map or RUNTIME_HANDLER_MAP)
    dispatch: dict[str, Callable[..., Any]] = {}

    for handler_name, method_name in mapping.items():
        if handler_name not in handler_names:
            continue
        target = getattr(mainwindow, method_name, None)
        if callable(target):
            dispatch[handler_name] = target

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



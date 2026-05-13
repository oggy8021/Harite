from __future__ import annotations

from typing import Any

from harite.config import resolve_default_settings_path
from harite.core import DEFAULT_BACKGROUND_COLOR_HEX, is_background_color_literal, normalize_background_color
from harite.optimize_settings import AUTO
from harite.positioning import format_position_pair, parse_position_pair


def set_preferences_two_screen_mode(backend: Any, value: object) -> None:
    raw = str(value).strip().lower() if value is not None else "off"
    is_auto = raw == "auto"
    is_on = raw in {"on", "true", "1"} or value is True
    backend._set_toggle_active("radSettingsTwoScreenAuto", is_auto)
    backend._set_toggle_active("radSettingsTwoScreenOn", is_on and not is_auto)
    backend._set_toggle_active("radSettingsTwoScreenOff", not is_auto and not is_on)


def read_preferences_two_screen_mode(backend: Any) -> str | bool:
    if backend._is_toggle_active("radSettingsTwoScreenAuto"):
        return "auto"
    if backend._is_toggle_active("radSettingsTwoScreenOn"):
        return True
    return False


def set_preferences_apply_mode(backend: Any, value: object | None) -> None:
    mode = str(value or "single-file").strip().lower()
    backend._prefs_apply_mode_syncing = True
    try:
        if mode == "per-monitor-auto-split":
            backend._prefs_apply_mode_preserved = None
            backend._set_toggle_active("radSettingsApplySingle", False)
            backend._set_toggle_active("radSettingsApplyPerMonitor", True)
            return
        if mode == "single-file":
            backend._prefs_apply_mode_preserved = None
            backend._set_toggle_active("radSettingsApplySingle", True)
            backend._set_toggle_active("radSettingsApplyPerMonitor", False)
            return

        backend._prefs_apply_mode_preserved = mode
        backend._set_toggle_active("radSettingsApplySingle", False)
        backend._set_toggle_active("radSettingsApplyPerMonitor", False)
    finally:
        backend._prefs_apply_mode_syncing = False


def read_preferences_apply_mode(backend: Any) -> str:
    if backend._is_toggle_active("radSettingsApplyPerMonitor"):
        return "per-monitor-auto-split"
    if backend._is_toggle_active("radSettingsApplySingle"):
        return "single-file"
    if backend._prefs_apply_mode_preserved:
        return backend._prefs_apply_mode_preserved
    return "single-file"


def on_preferences_apply_mode_toggled(backend: Any, widget: Any, mode: str) -> None:
    if backend._prefs_apply_mode_syncing:
        return
    is_active = True
    if hasattr(widget, "get_active"):
        is_active = bool(widget.get_active())
    if not is_active:
        return
    backend._prefs_apply_mode_preserved = None


def build_settings_open_notice(backend: Any) -> str:
    export_path = resolve_default_settings_path()
    try:
        if export_path.exists():
            return ""
    except Exception:
        pass
    return "現在は未保存です"


def sync_preferences_widgets_from_dialog(backend: Any) -> dict[str, object]:
    dialog = backend._objects.get("SettingsDialog")
    if dialog is None or not hasattr(dialog, "get_preferences_config"):
        return {}
    config = dict(dialog.get_preferences_config())
    resolution = config.get("resolution")
    backend._set_entry_text("entSettingsResolution", "" if resolution in {None, AUTO} else resolution)
    backend._set_entry_text("entSettingsScaling", config.get("scaling", "fit"))
    set_preferences_two_screen_mode(backend, config.get("two_screen", False))
    l_display = config.get("l_display")
    r_display = config.get("r_display")
    backend._set_entry_text("entSettingsLDisplay", "" if l_display in {None, AUTO} else l_display)
    backend._set_entry_text("entSettingsRDisplay", "" if r_display in {None, AUTO} else r_display)
    backend._set_entry_text("entSettingsMargins", config.get("margins"))
    backend._set_entry_text("entSettingsAlign", format_position_pair(config.get("align", "center"), axis="align"))
    backend._set_entry_text("entSettingsValign", format_position_pair(config.get("valign", "center"), axis="valign"))
    backend._set_spin_value("spnSettingsQuality", int(config.get("quality", 90)))
    backend._set_entry_text("entSettingsMarginTextMode", config.get("embed_info", "none"))
    backend._set_entry_text("entSettingsMarginText", config.get("embed_text"))
    backend._set_entry_text("entSettingsMarginTextPosition", config.get("embed_position", "auto"))
    backend._set_spin_value("spnSettingsMarginTextMaxLines", int(config.get("embed_max_lines", 3)))
    backend._set_entry_text("entSettingsPlugin", config.get("plugin", "windows"))
    set_preferences_apply_mode(backend, config.get("apply_mode", "single-file"))
    return config


def sync_preferences_dialog_from_widgets(backend: Any) -> dict[str, object]:
    dialog = backend._objects.get("SettingsDialog")
    config: dict[str, object] = {}
    if dialog is not None and hasattr(dialog, "get_preferences_config"):
        config = dict(dialog.get_preferences_config())

    def _empty_to_none(value: str) -> str | None:
        return value if value else None

    config.update(
        {
            "scaling": backend._read_entry_text("entSettingsScaling") or "fit",
            "two_screen": read_preferences_two_screen_mode(backend),
            "margins": _empty_to_none(backend._read_entry_text("entSettingsMargins")),
            "align": list(parse_position_pair(backend._read_entry_text("entSettingsAlign") or "center", axis="align")),
            "valign": list(parse_position_pair(backend._read_entry_text("entSettingsValign") or "center", axis="valign")),
            "quality": backend._read_spin_int("spnSettingsQuality"),
            "embed_info": backend._read_entry_text("entSettingsMarginTextMode") or "none",
            "embed_text": _empty_to_none(backend._read_entry_text("entSettingsMarginText")),
            "embed_position": backend._read_entry_text("entSettingsMarginTextPosition") or "auto",
            "embed_max_lines": backend._read_spin_int("spnSettingsMarginTextMaxLines"),
            "plugin": backend._read_entry_text("entSettingsPlugin") or "windows",
            "apply_mode": read_preferences_apply_mode(backend),
        }
    )

    resolution = _empty_to_none(backend._read_entry_text("entSettingsResolution"))
    l_display = _empty_to_none(backend._read_entry_text("entSettingsLDisplay"))
    r_display = _empty_to_none(backend._read_entry_text("entSettingsRDisplay"))
    if resolution is None:
        config.pop("resolution", None)
    else:
        config["resolution"] = resolution
    if l_display is None:
        config.pop("l_display", None)
    else:
        config["l_display"] = l_display
    if r_display is None:
        config.pop("r_display", None)
    else:
        config["r_display"] = r_display
    if dialog is not None:
        if hasattr(dialog, "set_preferences_config"):
            dialog.set_preferences_config(config)
    return config


def refresh_preferences_dialog_config_from_getter(backend: Any) -> None:
    dialog = backend._objects.get("SettingsDialog")
    getter = backend._signal_handlers.get("on_get_settings_config")
    if getter is None or dialog is None or not hasattr(dialog, "set_preferences_config"):
        return

    current_config: dict[str, object] = {}
    if hasattr(dialog, "get_preferences_config"):
        current_config = dict(dialog.get_preferences_config())

    refreshed = dict(current_config)
    refreshed.update(dict(getter()))
    dialog.set_preferences_config(refreshed)


def refresh_color_dialog_from_getter(backend: Any) -> str:
    getter = backend._signal_handlers.get("on_get_settings_config")
    dialog = backend._objects.get("ColorDialog")
    background_color = dialog.get_color() if dialog is not None and hasattr(dialog, "get_color") else DEFAULT_BACKGROUND_COLOR_HEX
    if getter is not None:
        try:
            config = dict(getter())
            if "background_color" in config:
                background_color = normalize_background_color(config.get("background_color"))
        except Exception:
            pass
    if dialog is not None and hasattr(dialog, "set_color"):
        dialog.set_color(background_color)
    return background_color


def refresh_about_dialog_from_getter(backend: Any) -> dict[str, object]:
    getter = backend._signal_handlers.get("on_get_about_dialog_info")
    dialog = backend._objects.get("AboutDialog")
    content: dict[str, object] = {
        "app_name": "Harite",
        "version": "-",
        "description": "壁紙最適化ツール",
        "credits": "-",
        "license_name": "LICENSE",
    }
    if getter is not None:
        try:
            content.update(dict(getter()))
        except Exception:
            pass
    if dialog is not None and hasattr(dialog, "set_content"):
        dialog.set_content(content)
    return content


def store_background_color_in_settings_dialog(backend: Any, color: str) -> None:
    dialog = backend._objects.get("SettingsDialog")
    if dialog is None or not hasattr(dialog, "get_preferences_config") or not hasattr(dialog, "set_preferences_config"):
        return
    config = dict(dialog.get_preferences_config())
    config["background_color"] = normalize_background_color(color)
    dialog.set_preferences_config(config)


def on_settings_clicked(backend: Any, *_args: Any) -> None:
    callback = backend._signal_handlers.get("on_open_settings_dialog")
    dialog = backend._objects.get("SettingsDialog")
    if callback is None:
        backend._set_feedback(phase="Settings", state="planned")
        return
    try:
        ok = callback()
        if ok:
            refresh_preferences_dialog_config_from_getter(backend)
            sync_preferences_widgets_from_dialog(backend)
            owner = backend._get_handler_owner("on_open_settings_dialog")
            if owner is not None:
                backend._sync_watch_state_only_from_owner(owner)
            backend._set_label_text("lblSettingsState", "Settings: current values")
            backend._set_label_text("lblSettingsNotice", build_settings_open_notice(backend))
            if dialog is not None and hasattr(dialog, "show"):
                dialog.show()
            backend._set_feedback(phase="Settings", state="opened")
        else:
            backend._set_feedback(phase="Settings", state="deferred")
    except Exception as exc:
        backend._set_feedback(phase="Settings", state="error", error=str(exc))


def on_preferences_apply_clicked(backend: Any, *_args: Any) -> None:
    handler_name = "on_apply_settings"
    callback = backend._signal_handlers.get(handler_name)
    dialog = backend._objects.get("SettingsDialog")
    if callback is None or dialog is None or not hasattr(dialog, "get_preferences_config"):
        backend._set_feedback(phase="SettingsApply", state="handler-missing", error="handler not connected")
        return
    try:
        backend._set_label_text("lblSettingsNotice", "")
        ok = callback(sync_preferences_dialog_from_widgets(backend))
        if ok:
            owner = backend._get_handler_owner(handler_name)
            if owner is not None:
                backend._sync_non_preview_state_from_owner(owner)
            if hasattr(dialog, "hide"):
                dialog.hide()
            backend._set_feedback(phase="SettingsApply", state="applied")
        else:
            backend._set_label_text("lblSettingsNotice", "Settings: apply returned false")
            backend._set_feedback(phase="SettingsApply", state="failed", error="settings apply returned false")
    except Exception as exc:
        backend._set_label_text("lblSettingsNotice", f"Settings: {exc}")
        backend._set_feedback(phase="SettingsApply", state="error", error=str(exc))


def on_preferences_load_clicked(backend: Any, *_args: Any) -> None:
    backend._set_feedback(phase="SettingsLoad", state="unavailable")


def on_preferences_save_clicked(backend: Any, *_args: Any) -> None:
    callback = backend._signal_handlers.get("on_save_settings_file")
    dialog = backend._objects.get("SettingsDialog")
    if callback is None or dialog is None or not hasattr(dialog, "get_export_path"):
        backend._set_feedback(phase="SettingsSave", state="handler-missing", error="handler not connected")
        return
    try:
        backend._set_label_text("lblSettingsNotice", "")
        config = sync_preferences_dialog_from_widgets(backend)
        try:
            ok = callback(dialog.get_export_path(), config)
        except TypeError:
            ok = callback(dialog.get_export_path())
        if ok:
            backend._set_label_text("lblSettingsNotice", "Settings: saved")
            backend._set_feedback(phase="SettingsSave", state="saved")
        else:
            backend._set_label_text("lblSettingsNotice", "Settings: save returned false")
            backend._set_feedback(phase="SettingsSave", state="failed", error="settings save returned false")
    except Exception as exc:
        backend._set_label_text("lblSettingsNotice", f"Settings: {exc}")
        backend._set_feedback(phase="SettingsSave", state="error", error=str(exc))


def on_preferences_close_clicked(backend: Any, *_args: Any) -> None:
    dialog = backend._objects.get("SettingsDialog")
    backend._set_label_text("lblSettingsNotice", "")
    if dialog is not None and hasattr(dialog, "hide"):
        dialog.hide()
    callback = backend._signal_handlers.get("on_close_settings_dialog")
    if callback is not None:
        try:
            callback()
        except Exception:
            pass
    backend._set_feedback(phase="Settings", state="closed")


def on_preferences_window_delete_event(backend: Any) -> bool:
    on_preferences_close_clicked(backend)
    return True


def on_color_clicked(backend: Any, *_args: Any) -> None:
    dialog = backend._objects.get("ColorDialog")
    callback = backend._signal_handlers.get("on_set_color")
    if dialog is None or not hasattr(dialog, "open_dialog"):
        backend._set_feedback(phase="Color", state="handler-missing", error="color dialog not available")
        return
    try:
        refresh_color_dialog_from_getter(backend)
        if callback is not None:
            callback()
        backend._set_feedback(phase="Color", state="opened")
        dialog.open_dialog()
    except Exception as exc:
        backend._set_feedback(phase="Color", state="error", error=str(exc))


def on_about_clicked(backend: Any, *_args: Any) -> None:
    dialog = backend._objects.get("AboutDialog")
    callback = backend._signal_handlers.get("on_about")
    if dialog is None or not hasattr(dialog, "show"):
        backend._set_feedback(phase="About", state="handler-missing", error="about dialog not available")
        return
    try:
        refresh_about_dialog_from_getter(backend)
        ok = True if callback is None else bool(callback())
        if not ok:
            backend._set_feedback(phase="About", state="failed", error="about dialog open rejected")
            return
        dialog.show()
        backend._set_feedback(phase="About", state="opened")
    except Exception as exc:
        backend._set_feedback(phase="About", state="error", error=str(exc))


def on_about_dialog_close_clicked(backend: Any, *_args: Any) -> None:
    close_about_dialog(backend, False)


def on_about_window_delete_event(backend: Any) -> bool:
    close_about_dialog(backend, True)
    return True


def close_about_dialog(backend: Any, destroyed: bool) -> None:
    dialog = backend._objects.get("AboutDialog")
    if dialog is not None and hasattr(dialog, "hide"):
        dialog.hide()
    callback = backend._signal_handlers.get("on_close_about_dialog")
    if callback is not None:
        try:
            callback()
        except Exception:
            pass
    backend._set_feedback(phase="About", state="closed" if destroyed else "closed")


def on_color_dialog_apply_clicked(backend: Any, *_args: Any) -> None:
    dialog = backend._objects.get("ColorDialog")
    callback = backend._signal_handlers.get("on_set_color")
    if dialog is None or not hasattr(dialog, "get_color"):
        backend._set_feedback(phase="Color", state="handler-missing", error="color dialog not available")
        return
    if callback is None:
        backend._set_feedback(phase="Color", state="handler-missing", error="handler not connected")
        return
    try:
        if hasattr(dialog, "clear_notice"):
            dialog.clear_notice()
        else:
            backend._set_label_text("lblColorNotice", "")
        if hasattr(dialog, "get_pending_color"):
            color = dialog.get_pending_color()
        else:
            color = dialog.get_color()
        if not is_background_color_literal(color):
            if hasattr(dialog, "set_notice"):
                dialog.set_notice("Color: invalid background color")
            else:
                backend._set_label_text("lblColorNotice", "Color: invalid background color")
            return
        ok = callback(color)
        owner = backend._get_handler_owner("on_set_color")
        if ok:
            store_background_color_in_settings_dialog(backend, color)
            if hasattr(dialog, "hide"):
                dialog.hide()
            backend._set_label_text("lblColorState", f"Color: {normalize_background_color(color)}")
            backend._set_label_text("lblColorNotice", "")
            backend._set_feedback(phase="Color", state="updated")
        else:
            if owner is not None and str(getattr(owner, "status_phase", "") or "") == "color":
                message = str(getattr(owner, "status_message", "color update returned false") or "color update returned false")
                error = str(getattr(owner, "last_error", "") or "") or None
                backend._set_label_text("lblColorNotice", f"Color: {message}")
                backend._set_feedback(phase="Color", state=message, error=error)
            else:
                backend._set_feedback(phase="Color", state="failed", error="color update returned false")
    except Exception as exc:
        backend._set_feedback(phase="Color", state="error", error=str(exc))


def on_color_dialog_cancel_clicked(backend: Any, *_args: Any) -> None:
    on_color_dialog_canceled(backend, False)


def on_color_window_delete_event(backend: Any) -> bool:
    on_color_dialog_canceled(backend, True)
    return True


def on_color_dialog_confirmed(backend: Any, color: str) -> None:
    callback = backend._signal_handlers.get("on_set_color")
    if callback is None:
        backend._set_feedback(phase="Color", state="handler-missing", error="handler not connected")
        return
    try:
        ok = callback(color)
        owner = backend._get_handler_owner("on_set_color")
        if ok:
            store_background_color_in_settings_dialog(backend, color)
            dialog = backend._objects.get("ColorDialog")
            if dialog is not None and hasattr(dialog, "hide"):
                dialog.hide()
            backend._set_label_text("lblColorState", f"Color: {normalize_background_color(color)}")
            backend._set_label_text("lblColorNotice", "")
            backend._set_feedback(phase="Color", state="updated")
        else:
            if owner is not None and str(getattr(owner, "status_phase", "") or "") == "color":
                message = str(getattr(owner, "status_message", "color update returned false") or "color update returned false")
                error = str(getattr(owner, "last_error", "") or "") or None
                backend._set_label_text("lblColorNotice", f"Color: {message}")
                backend._set_feedback(phase="Color", state=message, error=error)
            else:
                backend._set_feedback(phase="Color", state="failed", error="color update returned false")
    except Exception as exc:
        backend._set_feedback(phase="Color", state="error", error=str(exc))


def on_color_dialog_canceled(backend: Any, destroyed: bool) -> None:
    dialog = backend._objects.get("ColorDialog")
    if dialog is not None and hasattr(dialog, "hide"):
        dialog.hide()
    callback = backend._signal_handlers.get("on_close_color_dialog")
    if callback is not None:
        try:
            callback()
        except Exception:
            pass
    backend._set_label_text("lblColorNotice", "Color: canceled")
    backend._set_feedback(phase="Color", state="closed" if destroyed else "canceled")
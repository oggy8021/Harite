from __future__ import annotations

from typing import Any

from harite.core import DEFAULT_BACKGROUND_COLOR_HEX, is_background_color_literal, normalize_background_color
from harite.optimize_settings import AUTO
from harite.positioning import format_position_pair, parse_position_pair
from harite.settings_file import resolve_default_settings_path


def set_settings_two_screen_mode(backend: Any, value: object) -> None:
    raw = str(value).strip().lower() if value is not None else "off"
    is_auto = raw == "auto"
    is_on = raw in {"on", "true", "1"} or value is True
    backend._set_toggle_active("radSettingsTwoScreenAuto", is_auto)
    backend._set_toggle_active("radSettingsTwoScreenOn", is_on and not is_auto)
    backend._set_toggle_active("radSettingsTwoScreenOff", not is_auto and not is_on)


def read_settings_two_screen_mode(backend: Any) -> str | bool:
    if backend._is_toggle_active("radSettingsTwoScreenAuto"):
        return "auto"
    if backend._is_toggle_active("radSettingsTwoScreenOn"):
        return True
    return False


def set_settings_apply_mode(backend: Any, value: object | None) -> None:
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


def read_settings_apply_mode(backend: Any) -> str:
    if backend._is_toggle_active("radSettingsApplyPerMonitor"):
        return "per-monitor-auto-split"
    if backend._is_toggle_active("radSettingsApplySingle"):
        return "single-file"
    if backend._prefs_apply_mode_preserved:
        return backend._prefs_apply_mode_preserved
    return "single-file"


def on_settings_apply_mode_toggled(backend: Any, widget: Any, mode: str) -> None:
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
    if export_path.exists():
        return ""
    return "現在は未保存です"


def _dialog_get_settings(dialog: Any) -> dict[str, object]:
    if dialog is None:
        return {}
    getter = getattr(dialog, "get_settings", None)
    if callable(getter):
        return dict(getter())
    return {}


def _dialog_set_settings(dialog: Any, settings: dict[str, object]) -> bool:
    if dialog is None:
        return False
    setter = getattr(dialog, "set_settings", None)
    if callable(setter):
        setter(settings)
        return True
    return False


def _settings_getter(backend: Any) -> Any:
    return backend._signal_handlers.get("on_get_settings")


def sync_settings_widgets_from_dialog(backend: Any) -> dict[str, object]:
    dialog = backend._objects.get("SettingsDialog")
    if dialog is None:
        return {}
    settings = _dialog_get_settings(dialog)
    resolution = settings.get("resolution")
    backend._set_entry_text("entSettingsResolution", "" if resolution in {None, AUTO} else resolution)
    backend._set_entry_text("entSettingsScaling", settings.get("scaling", "fit"))
    set_settings_two_screen_mode(backend, settings.get("two_screen", False))
    l_display = settings.get("l_display")
    r_display = settings.get("r_display")
    backend._set_entry_text("entSettingsLDisplay", "" if l_display in {None, AUTO} else l_display)
    backend._set_entry_text("entSettingsRDisplay", "" if r_display in {None, AUTO} else r_display)
    backend._set_entry_text("entSettingsMargins", settings.get("margins"))
    backend._set_entry_text("entSettingsAlign", format_position_pair(settings.get("align", "center"), axis="align"))
    backend._set_entry_text("entSettingsValign", format_position_pair(settings.get("valign", "center"), axis="valign"))
    backend._set_spin_value("spnSettingsQuality", int(settings.get("quality", 90)))
    backend._set_entry_text("entSettingsMarginTextMode", settings.get("embed_info", "none"))
    backend._set_entry_text("entSettingsMarginText", settings.get("embed_text"))
    backend._set_entry_text("entSettingsMarginTextPosition", settings.get("embed_position", "right-bottom"))
    backend._set_spin_value("spnSettingsMarginTextMaxLines", int(settings.get("embed_max_lines", 3)))
    backend._set_entry_text("entSettingsPlugin", settings.get("plugin", "windows"))
    set_settings_apply_mode(backend, settings.get("apply_mode", "single-file"))
    return settings


def sync_settings_dialog_from_widgets(backend: Any) -> dict[str, object]:
    dialog = backend._objects.get("SettingsDialog")
    settings: dict[str, object] = {}
    if dialog is not None:
        settings = _dialog_get_settings(dialog)

    def _empty_to_none(value: str) -> str | None:
        return value if value else None

    settings.update(
        {
            "scaling": backend._read_entry_text("entSettingsScaling") or "fit",
            "two_screen": read_settings_two_screen_mode(backend),
            "margins": _empty_to_none(backend._read_entry_text("entSettingsMargins")),
            "align": list(parse_position_pair(backend._read_entry_text("entSettingsAlign") or "center", axis="align")),
            "valign": list(parse_position_pair(backend._read_entry_text("entSettingsValign") or "center", axis="valign")),
            "quality": backend._read_spin_int("spnSettingsQuality"),
            "embed_info": backend._read_entry_text("entSettingsMarginTextMode") or "none",
            "embed_text": _empty_to_none(backend._read_entry_text("entSettingsMarginText")),
            "embed_position": backend._read_entry_text("entSettingsMarginTextPosition") or "right-bottom",
            "embed_max_lines": backend._read_spin_int("spnSettingsMarginTextMaxLines"),
            "plugin": backend._read_entry_text("entSettingsPlugin") or "windows",
            "apply_mode": read_settings_apply_mode(backend),
        }
    )

    resolution = _empty_to_none(backend._read_entry_text("entSettingsResolution"))
    l_display = _empty_to_none(backend._read_entry_text("entSettingsLDisplay"))
    r_display = _empty_to_none(backend._read_entry_text("entSettingsRDisplay"))
    if resolution is None:
        settings.pop("resolution", None)
    else:
        settings["resolution"] = resolution
    if l_display is None:
        settings.pop("l_display", None)
    else:
        settings["l_display"] = l_display
    if r_display is None:
        settings.pop("r_display", None)
    else:
        settings["r_display"] = r_display
    if dialog is not None:
        _dialog_set_settings(dialog, settings)
    return settings


def refresh_settings_dialog_from_getter(backend: Any) -> None:
    dialog = backend._objects.get("SettingsDialog")
    getter = _settings_getter(backend)
    if getter is None or dialog is None:
        return

    current_settings = _dialog_get_settings(dialog)

    refreshed = dict(current_settings)
    refreshed.update(dict(getter()))
    _dialog_set_settings(dialog, refreshed)


def refresh_color_dialog_from_getter(backend: Any) -> str:
    getter = _settings_getter(backend)
    dialog = backend._objects.get("ColorDialog")
    background_color = dialog.get_color() if dialog is not None and hasattr(dialog, "get_color") else DEFAULT_BACKGROUND_COLOR_HEX
    if getter is not None:
        settings = dict(getter())
        if "background_color" in settings:
            background_color = normalize_background_color(settings.get("background_color"))
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
        content.update(dict(getter()))
    if dialog is not None and hasattr(dialog, "set_content"):
        dialog.set_content(content)
    return content


def store_background_color_in_settings_dialog(backend: Any, color: str) -> None:
    dialog = backend._objects.get("SettingsDialog")
    if dialog is None:
        return
    settings = _dialog_get_settings(dialog)
    settings["background_color"] = normalize_background_color(color)
    _dialog_set_settings(dialog, settings)


def on_settings_clicked(backend: Any, *_args: Any) -> None:
    callback = backend._signal_handlers.get("on_open_settings_dialog")
    dialog = backend._objects.get("SettingsDialog")
    if callback is None:
        backend._set_feedback(phase="Settings", state="planned")
        return
    try:
        ok = callback()
    except TypeError as exc:
        backend._set_feedback(phase="Settings", state="error", error=str(exc))
        return

    if ok:
        try:
            refresh_settings_dialog_from_getter(backend)
            sync_settings_widgets_from_dialog(backend)
            owner = backend._get_handler_owner("on_open_settings_dialog")
            if owner is not None:
                backend._sync_slideshow_state_only_from_owner(owner)
            backend._set_label_text("lblSettingsState", "Settings: current values")
            backend._set_label_text("lblSettingsNotice", build_settings_open_notice(backend))
            if dialog is not None and hasattr(dialog, "show"):
                dialog.show()
            backend._set_feedback(phase="Settings", state="opened")
        except (RuntimeError, TypeError, ValueError) as exc:
            backend._set_feedback(phase="Settings", state="error", error=str(exc))
    else:
        backend._set_feedback(phase="Settings", state="deferred")


def on_settings_apply_clicked(backend: Any, *_args: Any) -> None:
    handler_name = "on_apply_settings"
    callback = backend._signal_handlers.get(handler_name)
    dialog = backend._objects.get("SettingsDialog")
    if callback is None or dialog is None:
        backend._set_feedback(phase="SettingsApply", state="handler-missing", error="handler not connected")
        return
    try:
        backend._set_label_text("lblSettingsNotice", "")
        ok = callback(sync_settings_dialog_from_widgets(backend))
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
    except (TypeError, ValueError) as exc:
        backend._set_label_text("lblSettingsNotice", f"Settings: {exc}")
        backend._set_feedback(phase="SettingsApply", state="error", error=str(exc))


def on_settings_load_clicked(backend: Any, *_args: Any) -> None:
    backend._set_feedback(phase="SettingsLoad", state="unavailable")


def on_settings_save_clicked(backend: Any, *_args: Any) -> None:
    callback = backend._signal_handlers.get("on_save_settings_file")
    dialog = backend._objects.get("SettingsDialog")
    if callback is None or dialog is None or not hasattr(dialog, "get_export_path"):
        backend._set_feedback(phase="SettingsSave", state="handler-missing", error="handler not connected")
        return
    try:
        backend._set_label_text("lblSettingsNotice", "")
        settings = sync_settings_dialog_from_widgets(backend)
        ok = callback(dialog.get_export_path(), settings)
        if ok:
            backend._set_label_text("lblSettingsNotice", "Settings: saved")
            backend._set_feedback(phase="SettingsSave", state="saved")
        else:
            backend._set_label_text("lblSettingsNotice", "Settings: save returned false")
            backend._set_feedback(phase="SettingsSave", state="failed", error="settings save returned false")
    except (TypeError, ValueError) as exc:
        backend._set_label_text("lblSettingsNotice", f"Settings: {exc}")
        backend._set_feedback(phase="SettingsSave", state="error", error=str(exc))


def on_settings_close_clicked(backend: Any, *_args: Any) -> None:
    dialog = backend._objects.get("SettingsDialog")
    backend._set_label_text("lblSettingsNotice", "")
    if dialog is not None and hasattr(dialog, "hide"):
        dialog.hide()
    callback = backend._signal_handlers.get("on_close_settings_dialog")
    if callback is not None:
        callback()
    backend._set_feedback(phase="Settings", state="closed")


def on_settings_window_delete_event(backend: Any) -> bool:
    on_settings_close_clicked(backend)
    return True


def on_color_clicked(backend: Any, *_args: Any) -> None:
    dialog = backend._objects.get("ColorDialog")
    callback = backend._signal_handlers.get("on_set_color")
    if dialog is None or not hasattr(dialog, "open_dialog"):
        backend._set_feedback(phase="Color", state="handler-missing", error="color dialog not available")
        return
    try:
        refresh_color_dialog_from_getter(backend)
    except (RuntimeError, TypeError, ValueError) as exc:
        backend._set_feedback(phase="Color", state="error", error=str(exc))
        return
    try:
        if callback is not None:
            callback()
        backend._set_feedback(phase="Color", state="opened")
        dialog.open_dialog()
    except TypeError as exc:
        backend._set_feedback(phase="Color", state="error", error=str(exc))


def on_about_clicked(backend: Any, *_args: Any) -> None:
    dialog = backend._objects.get("AboutDialog")
    callback = backend._signal_handlers.get("on_about")
    if dialog is None or not hasattr(dialog, "show"):
        backend._set_feedback(phase="About", state="handler-missing", error="about dialog not available")
        return
    try:
        refresh_about_dialog_from_getter(backend)
    except (RuntimeError, TypeError, ValueError) as exc:
        backend._set_feedback(phase="About", state="error", error=str(exc))
        return
    try:
        ok = True if callback is None else bool(callback())
        if not ok:
            backend._set_feedback(phase="About", state="failed", error="about dialog open rejected")
            return
        dialog.show()
        backend._set_feedback(phase="About", state="opened")
    except TypeError as exc:
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
        callback()
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
    except (TypeError, ValueError) as exc:
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
    except (TypeError, ValueError) as exc:
        backend._set_feedback(phase="Color", state="error", error=str(exc))


def on_color_dialog_canceled(backend: Any, destroyed: bool) -> None:
    dialog = backend._objects.get("ColorDialog")
    if dialog is not None and hasattr(dialog, "hide"):
        dialog.hide()
    callback = backend._signal_handlers.get("on_close_color_dialog")
    if callback is not None:
        callback()
    backend._set_label_text("lblColorNotice", "Color: canceled")
    backend._set_feedback(phase="Color", state="closed" if destroyed else "canceled")
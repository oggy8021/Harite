from __future__ import annotations

from typing import Any


def connect_runtime_widgets(backend: Any, widgets: dict[str, Any]) -> None:
    _connect_input_widgets(backend, widgets)
    _connect_direction_widgets(backend, widgets)
    _connect_action_widgets(backend, widgets)
    _connect_watch_widgets(backend, widgets)
    _connect_margin_text_widgets(backend, widgets)


def _connect_input_widgets(backend: Any, widgets: dict[str, Any]) -> None:
    # The current runtime shows selected input paths as labels. If editable text
    # widgets return in the future, keep the old input-changed wiring scoped to
    # those widgets only.
    for widget_name in ("input_display_l", "input_display_r"):
        widget = widgets[widget_name]
        if hasattr(widget, "set_editable") or hasattr(widget, "set_placeholder_text"):
            widget.connect("changed", backend._on_input_changed)

    widgets["btn_get_img_l"].connect("clicked", lambda *_args: backend._on_pick_input_clicked("L"))
    widgets["btn_get_img_r"].connect("clicked", lambda *_args: backend._on_pick_input_clicked("R"))
    widgets["btn_clr_path_l"].connect("clicked", lambda *_args: backend._on_clear_input_clicked("L"))
    widgets["btn_clr_path_r"].connect("clicked", lambda *_args: backend._on_clear_input_clicked("R"))


def _connect_direction_widgets(backend: Any, widgets: dict[str, Any]) -> None:
    for widget_name, handler_key in (
        ("tgl_upper_l", "tglUpperL"),
        ("tgl_lower_l", "tglLowerL"),
        ("tgl_upper_r", "tglUpperR"),
        ("tgl_lower_r", "tglLowerR"),
        ("tgl_push_left_l", "tglPushLeftL"),
        ("tgl_push_right_l", "tglPushRightL"),
        ("tgl_push_left_r", "tglPushLeftR"),
        ("tgl_push_right_r", "tglPushRightR"),
    ):
        widget = widgets[widget_name]
        widget.connect("pressed", lambda *_args, key=handler_key: backend._on_direction_pressed(key))
        widget.connect("toggled", lambda *_args, key=handler_key: backend._on_direction_toggled(key))
        widget.connect("released", lambda *_args, key=handler_key: backend._on_direction_released(key))

    for widget_name in ("top_margin_spin", "left_margin_spin", "right_margin_spin", "bottom_margin_spin"):
        widgets[widget_name].connect("value-changed", backend._on_margin_changed)


def _connect_action_widgets(backend: Any, widgets: dict[str, Any]) -> None:
    widgets["optimize_btn"].connect("clicked", backend._on_save_clicked)
    widgets["optimize_modern_btn"].connect("clicked", backend._on_optimize_clicked)
    widgets["apply_btn"].connect("clicked", backend._on_apply_clicked)
    widgets["btn_setting"].connect("clicked", backend._on_settings_clicked)
    widgets["prefs_apply_btn"].connect("clicked", backend._on_preferences_apply_clicked)
    widgets["prefs_save_btn"].connect("clicked", backend._on_preferences_save_clicked)
    widgets["prefs_close_btn"].connect("clicked", backend._on_preferences_close_clicked)
    widgets["rad_apply_single"].connect(
        "toggled",
        lambda widget, *_args: backend._on_apply_mode_toggled(widget, "single-file"),
    )
    widgets["rad_apply_per_monitor"].connect(
        "toggled",
        lambda widget, *_args: backend._on_apply_mode_toggled(widget, "per-monitor-auto-split"),
    )
    widgets["btn_set_color"].connect("clicked", backend._on_color_clicked)
    widgets["btn_about"].connect("clicked", backend._on_about_clicked)
    widgets["color_apply_btn"].connect("clicked", backend._on_color_dialog_apply_clicked)
    widgets["color_cancel_btn"].connect("clicked", backend._on_color_dialog_cancel_clicked)
    widgets["about_close_btn"].connect("clicked", backend._on_about_dialog_close_clicked)


def _connect_watch_widgets(backend: Any, widgets: dict[str, Any]) -> None:
    widgets["btn_open_srcdir_l"].connect("clicked", lambda *_args: backend._on_pick_srcdir_clicked("L"))
    widgets["btn_open_srcdir_r"].connect("clicked", lambda *_args: backend._on_pick_srcdir_clicked("R"))
    widgets["interval_spin"].connect("value-changed", backend._on_watch_interval_changed)
    widgets["btn_daemonize"].connect("clicked", backend._on_watch_start_clicked)
    widgets["btn_cancel_daemonize"].connect("clicked", backend._on_watch_stop_clicked)


def _connect_margin_text_widgets(backend: Any, widgets: dict[str, Any]) -> None:
    widgets["margin_text_mode_off"].connect(
        "toggled",
        lambda widget, *_args: backend._on_margin_text_mode_toggled(widget, "none"),
    )
    widgets["margin_text_mode_settings"].connect(
        "toggled",
        lambda widget, *_args: backend._on_margin_text_mode_toggled(widget, "params"),
    )
    widgets["margin_text_mode_text"].connect(
        "toggled",
        lambda widget, *_args: backend._on_margin_text_mode_toggled(widget, "free"),
    )
    widgets["margin_text_mode_both"].connect(
        "toggled",
        lambda widget, *_args: backend._on_margin_text_mode_toggled(widget, "combo"),
    )

    margin_text_entry = widgets["margin_text_entry"]
    if hasattr(margin_text_entry, "get_buffer") and hasattr(margin_text_entry.get_buffer(), "connect"):
        margin_text_entry.get_buffer().connect(
            "changed",
            lambda *_args: backend._on_margin_text_changed(margin_text_entry),
        )
    else:
        margin_text_entry.connect("changed", backend._on_margin_text_changed)
    margin_text_entry.connect("key-press-event", backend._on_margin_text_key_press)

    widgets["margin_position_left_top"].connect(
        "toggled",
        lambda widget, *_args: backend._on_margin_position_toggled(widget, "top"),
    )
    widgets["margin_position_right_bottom"].connect(
        "toggled",
        lambda widget, *_args: backend._on_margin_position_toggled(widget, "bottom"),
    )
    widgets["margin_position_left_bottom"].connect(
        "toggled",
        lambda widget, *_args: backend._on_margin_position_toggled(widget, "left"),
    )
    widgets["margin_position_right_top"].connect(
        "toggled",
        lambda widget, *_args: backend._on_margin_position_toggled(widget, "right"),
    )
    widgets["margin_text_max_lines_spin"].connect(
        "value-changed",
        backend._on_margin_text_max_lines_changed,
    )
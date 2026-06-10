"""Qt signal-to-handler wiring for Harite GUI (Phase 8).

Mirrors ``gui_runtime_signal_wiring.connect_runtime_widgets``.

GTK pattern:  ``widget.connect("clicked", backend._on_*_clicked)``
Qt  pattern:  ``widget.clicked.connect(backend._on_*_clicked)``

For toggle signals the Qt ``toggled(bool)`` carries the new state,
so handlers receive an ``is_checked`` bool instead of the GTK widget ref.

``connect_qt_widgets(backend, widgets)`` is the public entry point.
"""

from __future__ import annotations

from typing import Any


def connect_qt_widgets(backend: Any, widgets: dict[str, Any]) -> None:
    """Connect all Qt widget signals to backend handler methods."""
    _connect_input_widgets(backend, widgets)
    _connect_direction_widgets(backend, widgets)
    _connect_action_widgets(backend, widgets)
    _connect_slideshow_widgets(backend, widgets)
    _connect_margin_text_widgets(backend, widgets)


# ---------------------------------------------------------------------------
# Input (image file) widgets
# ---------------------------------------------------------------------------


def _connect_input_widgets(backend: Any, widgets: dict[str, Any]) -> None:
    _safe_connect(
        widgets.get("btn_get_img_l"),
        "clicked",
        lambda: backend._on_pick_input_clicked("L"),
    )
    _safe_connect(
        widgets.get("btn_get_img_r"),
        "clicked",
        lambda: backend._on_pick_input_clicked("R"),
    )
    _safe_connect(
        widgets.get("btn_clr_path_l"),
        "clicked",
        lambda: backend._on_clear_input_clicked("L"),
    )
    _safe_connect(
        widgets.get("btn_clr_path_r"),
        "clicked",
        lambda: backend._on_clear_input_clicked("R"),
    )
    _safe_connect(
        widgets.get("chk_auto_display_scale_l"),
        "toggled",
        lambda checked: backend._on_auto_display_scale_toggled("L", checked),
    )
    _safe_connect(
        widgets.get("chk_auto_display_scale_r"),
        "toggled",
        lambda checked: backend._on_auto_display_scale_toggled("R", checked),
    )
    _safe_connect(
        widgets.get("combo_display_scale_l"),
        "currentIndexChanged",
        lambda _index: backend._on_display_scale_combo_changed("L"),
    )
    _safe_connect(
        widgets.get("combo_display_scale_r"),
        "currentIndexChanged",
        lambda _index: backend._on_display_scale_combo_changed("R"),
    )
    _safe_connect(
        widgets.get("btn_swap_input_paths"),
        "clicked",
        backend._on_swap_input_paths_clicked,
    )


# ---------------------------------------------------------------------------
# Direction toggle widgets
# ---------------------------------------------------------------------------


def _connect_direction_widgets(backend: Any, widgets: dict[str, Any]) -> None:
    direction_pairs = [
        ("tgl_upper_l", "tglUpperL"),
        ("tgl_lower_l", "tglLowerL"),
        ("tgl_upper_r", "tglUpperR"),
        ("tgl_lower_r", "tglLowerR"),
        ("tgl_push_left_l", "tglPushLeftL"),
        ("tgl_push_right_l", "tglPushRightL"),
        ("tgl_push_left_r", "tglPushLeftR"),
        ("tgl_push_right_r", "tglPushRightR"),
    ]

    for widget_name, handler_key in direction_pairs:
        w = widgets.get(widget_name)
        if w is None:
            continue
        key = handler_key
        # pressed / released are not direct signals on QPushButton for checkable
        # buttons - use clicked (which fires on release) and toggled for state.
        _safe_connect(
            w, "pressed",
            lambda _key=key: backend._on_direction_pressed(_key),
        )
        _safe_connect(
            w, "toggled",
            lambda checked, _key=key: backend._on_direction_toggled(_key),
        )
        _safe_connect(
            w, "released",
            lambda _key=key: backend._on_direction_released(_key),
        )

    spin_aliases = (
        ("top_margin_spin", "spnTopMargin"),
        ("left_margin_spin", "spnLeftMargin"),
        ("right_margin_spin", "spnRightMargin"),
        ("bottom_margin_spin", "spnBottomMargin"),
        ("all_margins_spin", "spnAllMargins"),
    )
    for spin_key, alias in spin_aliases:
        spin = widgets.get(spin_key)
        if spin is None:
            continue
        _safe_connect(
            spin,
            "valueChanged",
            lambda value, _alias=alias: backend._on_margin_changed(_alias, value),
        )


# ---------------------------------------------------------------------------
# Main action widgets
# ---------------------------------------------------------------------------


def _connect_action_widgets(backend: Any, widgets: dict[str, Any]) -> None:
    _safe_connect(widgets.get("optimize_btn"), "clicked", backend._on_save_clicked)
    _safe_connect(widgets.get("optimize_modern_btn"), "clicked", backend._on_optimize_clicked)
    _safe_connect(widgets.get("apply_btn"), "clicked", backend._on_apply_clicked)
    _safe_connect(widgets.get("btn_setting"), "clicked", backend._on_settings_clicked)
    _safe_connect(widgets.get("prefs_apply_btn"), "clicked", backend._on_settings_apply_clicked)
    _safe_connect(widgets.get("prefs_save_btn"), "clicked", backend._on_settings_save_clicked)
    _safe_connect(widgets.get("prefs_close_btn"), "clicked", backend._on_settings_close_clicked)

    rad_single = widgets.get("rad_apply_single")
    rad_per_monitor = widgets.get("rad_apply_per_monitor")
    if rad_single is not None:
        _safe_connect(
            rad_single, "toggled",
            lambda checked: backend._on_apply_mode_toggled(rad_single, "single-file") if checked else None,
        )
    if rad_per_monitor is not None:
        _safe_connect(
            rad_per_monitor, "toggled",
            lambda checked: backend._on_apply_mode_toggled(rad_per_monitor, "per-monitor-auto-split") if checked else None,
        )

    _safe_connect(widgets.get("btn_set_color"), "clicked", backend._on_color_clicked)
    _safe_connect(widgets.get("btn_about"), "clicked", backend._on_about_clicked)
    _safe_connect(widgets.get("color_apply_btn"), "clicked", backend._on_color_dialog_apply_clicked)
    _safe_connect(widgets.get("color_cancel_btn"), "clicked", backend._on_color_dialog_cancel_clicked)
    _safe_connect(widgets.get("about_close_btn"), "clicked", backend._on_about_dialog_close_clicked)
    _safe_connect(widgets.get("color_pick_btn"), "clicked", backend._on_color_pick_clicked)

    # Export image button
    _safe_connect(widgets.get("btn_export"), "clicked", backend._on_save_clicked)


# ---------------------------------------------------------------------------
# Slideshow widgets
# ---------------------------------------------------------------------------


def _connect_slideshow_widgets(backend: Any, widgets: dict[str, Any]) -> None:
    _safe_connect(
        widgets.get("btn_open_srcdir_l"),
        "clicked",
        lambda: backend._on_pick_srcdir_clicked("L"),
    )
    _safe_connect(
        widgets.get("btn_open_srcdir_r"),
        "clicked",
        lambda: backend._on_pick_srcdir_clicked("R"),
    )
    _safe_connect(
        widgets.get("btn_swap_slideshow_srcdirs"),
        "clicked",
        backend._on_swap_slideshow_srcdirs_clicked,
    )
    _safe_connect(
        widgets.get("btn_clr_srcdir_l"),
        "clicked",
        lambda: backend._on_clear_slideshow_srcdir_clicked("L"),
    )
    _safe_connect(
        widgets.get("btn_clr_srcdir_r"),
        "clicked",
        lambda: backend._on_clear_slideshow_srcdir_clicked("R"),
    )
    _safe_connect(
        widgets.get("chk_slideshow_auto_display_scale_l"),
        "toggled",
        lambda checked: backend._on_slideshow_auto_display_scale_toggled("L", checked),
    )
    _safe_connect(
        widgets.get("chk_slideshow_auto_display_scale_r"),
        "toggled",
        lambda checked: backend._on_slideshow_auto_display_scale_toggled("R", checked),
    )
    _safe_connect(
        widgets.get("combo_slideshow_source_l"),
        "currentIndexChanged",
        lambda _index: backend._on_slideshow_source_combo_changed("L"),
    )
    _safe_connect(
        widgets.get("combo_slideshow_source_r"),
        "currentIndexChanged",
        lambda _index: backend._on_slideshow_source_combo_changed("R"),
    )
    _safe_connect(
        widgets.get("combo_slideshow_profile"),
        "currentIndexChanged",
        lambda _index: backend._on_slideshow_profile_combo_changed(),
    )
    _safe_connect(
        widgets.get("btn_manage_source_registry"),
        "clicked",
        backend._on_manage_source_registry_clicked,
    )
    _safe_connect(
        widgets.get("interval_spin"),
        "valueChanged",
        lambda val: backend._on_slideshow_interval_changed(None),
    )

    rad_seq = widgets.get("rad_slideshow_mode_sequential")
    rad_rnd = widgets.get("rad_slideshow_mode_random")
    if rad_seq is not None:
        _safe_connect(
            rad_seq, "toggled",
            lambda checked: backend._on_slideshow_mode_toggled(rad_seq, "sequential") if checked else None,
        )
    if rad_rnd is not None:
        _safe_connect(
            rad_rnd, "toggled",
            lambda checked: backend._on_slideshow_mode_toggled(rad_rnd, "random") if checked else None,
        )
    _safe_connect(widgets.get("btn_daemonize"), "clicked", backend._on_slideshow_start_clicked)
    _safe_connect(widgets.get("btn_cancel_daemonize"), "clicked", backend._on_slideshow_stop_clicked)
    from harite.gui.views.slideshow_options_drawer import toggle_slideshow_options_drawer

    _safe_connect(
        widgets.get("btn_slideshow_options_more"),
        "clicked",
        lambda *_args: toggle_slideshow_options_drawer(backend),
    )
    from harite.gui.views.margins_options_drawer import toggle_margins_options_drawer

    _safe_connect(
        widgets.get("btn_margins_options_more"),
        "clicked",
        lambda *_args: toggle_margins_options_drawer(backend),
    )


# ---------------------------------------------------------------------------
# Margin text widgets
# ---------------------------------------------------------------------------


def _connect_margin_text_widgets(backend: Any, widgets: dict[str, Any]) -> None:
    mode_pairs = [
        ("margin_text_mode_off", "none"),
        ("margin_text_mode_settings", "params"),
        ("margin_text_mode_text", "free"),
        ("margin_text_mode_both", "combo"),
    ]
    for widget_name, mode_value in mode_pairs:
        w = widgets.get(widget_name)
        if w is None:
            continue
        val = mode_value
        _safe_connect(
            w, "toggled",
            lambda checked, _w=w, _v=val: backend._on_margin_text_mode_toggled(_w, _v) if checked else None,
        )

    margin_text_entry = widgets.get("margin_text_entry")
    if margin_text_entry is not None:
        from harite.gui.adapters_qt.qt_margin_text import install_margin_text_key_handler

        install_margin_text_key_handler(margin_text_entry)
        if hasattr(margin_text_entry, "textChanged"):
            _safe_connect(
                margin_text_entry, "textChanged",
                lambda: backend._on_margin_text_changed(margin_text_entry),
            )

    position_pairs = [
        ("margin_position_left_top", "left-top"),
        ("margin_position_right_bottom", "right-bottom"),
        ("margin_position_left_bottom", "left-bottom"),
        ("margin_position_right_top", "right-top"),
    ]
    for widget_name, pos_value in position_pairs:
        w = widgets.get(widget_name)
        if w is None:
            continue
        val = pos_value
        _safe_connect(
            w, "toggled",
            lambda checked, _w=w, _v=val: backend._on_margin_position_toggled(_w, _v) if checked else None,
        )

    _safe_connect(
        widgets.get("margin_text_max_lines_spin"),
        "valueChanged",
        lambda val: backend._on_margin_text_max_lines_changed(None),
    )


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


def _safe_connect(widget: Any, signal_name: str, slot: Any) -> None:
    """Connect ``widget.{signal_name}.connect(slot)`` silently on failure."""
    if widget is None:
        return
    try:
        signal = getattr(widget, signal_name, None)
        if signal is not None and hasattr(signal, "connect"):
            signal.connect(slot)
    except Exception:
        pass

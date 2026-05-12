from __future__ import annotations

from typing import Any

from harite.gui.adapters.gtk_layout_builders import build_horizontal_separator, set_xalign_if_supported


def build_settings_section(gtk_module: Any, *, configure_spin_button: Any) -> dict[str, Any]:
    prefs_window = gtk_module.Window(title="Settings")
    if hasattr(prefs_window, "set_default_size"):
        prefs_window.set_default_size(520, 420)
    if hasattr(prefs_window, "set_resizable"):
        prefs_window.set_resizable(True)

    prefs_apply_btn = gtk_module.Button(label="Settings Apply")
    prefs_load_btn = gtk_module.Button(label="Settings Load")
    prefs_save_btn = gtk_module.Button(label="Settings Save")
    prefs_close_btn = gtk_module.Button(label="Settings Close")
    prefs_state_label = gtk_module.Label(label="Settings: idle")
    set_xalign_if_supported(prefs_state_label)
    prefs_editor_box = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
    prefs_editor_title = gtk_module.Label(label="Settings")
    set_xalign_if_supported(prefs_editor_title)
    prefs_editor_box.pack_start(prefs_editor_title, False, False, 0)

    def _prefs_row(label_text: str, *widgets: Any) -> Any:
        row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
        row_label = gtk_module.Label(label=label_text)
        set_xalign_if_supported(row_label)
        row.pack_start(row_label, False, False, 0)
        for widget in widgets:
            row.pack_start(widget, True, True, 0)
        prefs_editor_box.pack_start(row, False, False, 0)
        return row

    prefs_resolution_entry = gtk_module.Entry()
    prefs_scaling_entry = gtk_module.Entry()
    prefs_two_screen_auto = gtk_module.RadioButton.new_with_label(None, "TwoScreen Auto")
    prefs_two_screen_on = gtk_module.RadioButton.new_with_label_from_widget(prefs_two_screen_auto, "TwoScreen On")
    prefs_two_screen_off = gtk_module.RadioButton.new_with_label_from_widget(prefs_two_screen_auto, "TwoScreen Off")
    if hasattr(prefs_two_screen_off, "set_active"):
        prefs_two_screen_off.set_active(True)
    prefs_l_display_entry = gtk_module.Entry()
    prefs_r_display_entry = gtk_module.Entry()
    prefs_margins_entry = gtk_module.Entry()
    prefs_align_entry = gtk_module.Entry()
    prefs_valign_entry = gtk_module.Entry()
    prefs_quality_spin = gtk_module.SpinButton()
    configure_spin_button(prefs_quality_spin, minimum=1, maximum=100, step=1, page=10, initial=90)
    prefs_margin_text_mode_entry = gtk_module.Entry()
    prefs_margin_text_entry = gtk_module.Entry()
    prefs_margin_text_position_entry = gtk_module.Entry()
    prefs_margin_text_max_lines_spin = gtk_module.SpinButton()
    configure_spin_button(
        prefs_margin_text_max_lines_spin,
        minimum=1,
        maximum=20,
        step=1,
        page=5,
        initial=3,
    )
    prefs_plugin_entry = gtk_module.Entry()
    prefs_apply_single = gtk_module.RadioButton.new_with_label(None, "Apply Default")
    prefs_apply_per_monitor = gtk_module.RadioButton.new_with_label_from_widget(prefs_apply_single, "Apply Auto-split")
    if hasattr(prefs_apply_single, "set_active"):
        prefs_apply_single.set_active(True)
    prefs_import_path_entry = gtk_module.Entry()
    prefs_export_path_entry = gtk_module.Entry()

    prefs_apply_mode_shell = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
    prefs_apply_mode_shell.pack_start(prefs_apply_single, False, False, 0)
    prefs_apply_mode_shell.pack_start(prefs_apply_per_monitor, False, False, 0)

    _prefs_row("Resolution", prefs_resolution_entry)
    _prefs_row("Scaling", prefs_scaling_entry)
    _prefs_row("Plugin", prefs_plugin_entry)
    _prefs_row("Apply", prefs_apply_mode_shell)
    _prefs_row("Import path", prefs_import_path_entry)
    _prefs_row("Export path", prefs_export_path_entry)

    prefs_actions = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
    prefs_actions.pack_start(prefs_apply_btn, False, False, 0)
    prefs_actions.pack_start(prefs_load_btn, False, False, 0)
    prefs_actions.pack_start(prefs_save_btn, False, False, 0)
    prefs_actions.pack_start(prefs_close_btn, False, False, 0)
    prefs_editor_box.pack_start(prefs_actions, False, False, 0)
    prefs_notice_separator = build_horizontal_separator(gtk_module)
    prefs_editor_box.pack_start(prefs_notice_separator, False, False, 0)
    prefs_editor_box.pack_start(prefs_state_label, False, False, 0)

    if hasattr(prefs_window, "add"):
        prefs_window.add(prefs_editor_box)

    return {
        "prefs_window": prefs_window,
        "prefs_apply_btn": prefs_apply_btn,
        "prefs_load_btn": prefs_load_btn,
        "prefs_save_btn": prefs_save_btn,
        "prefs_close_btn": prefs_close_btn,
        "prefs_state_label": prefs_state_label,
        "prefs_notice_separator": prefs_notice_separator,
        "prefs_editor_box": prefs_editor_box,
        "prefs_editor_title": prefs_editor_title,
        "prefs_resolution_entry": prefs_resolution_entry,
        "prefs_scaling_entry": prefs_scaling_entry,
        "prefs_two_screen_auto": prefs_two_screen_auto,
        "prefs_two_screen_on": prefs_two_screen_on,
        "prefs_two_screen_off": prefs_two_screen_off,
        "prefs_l_display_entry": prefs_l_display_entry,
        "prefs_r_display_entry": prefs_r_display_entry,
        "prefs_margins_entry": prefs_margins_entry,
        "prefs_align_entry": prefs_align_entry,
        "prefs_valign_entry": prefs_valign_entry,
        "prefs_quality_spin": prefs_quality_spin,
        "prefs_margin_text_mode_entry": prefs_margin_text_mode_entry,
        "prefs_margin_text_entry": prefs_margin_text_entry,
        "prefs_margin_text_position_entry": prefs_margin_text_position_entry,
        "prefs_margin_text_max_lines_spin": prefs_margin_text_max_lines_spin,
        "prefs_plugin_entry": prefs_plugin_entry,
        "prefs_apply_single": prefs_apply_single,
        "prefs_apply_per_monitor": prefs_apply_per_monitor,
        "prefs_import_path_entry": prefs_import_path_entry,
        "prefs_export_path_entry": prefs_export_path_entry,
    }


def build_color_dialog_section(gtk_module: Any, *, default_color_hex: str) -> dict[str, Any]:
    color_window = gtk_module.Window(title="Background Color")
    if hasattr(color_window, "set_default_size"):
        color_window.set_default_size(420, 360)
    if hasattr(color_window, "set_resizable"):
        color_window.set_resizable(False)

    color_value_entry = gtk_module.Entry()
    color_state_label = gtk_module.Label(label=f"Color: {default_color_hex}")
    set_xalign_if_supported(color_state_label)
    color_notice_label = gtk_module.Label(label="")
    set_xalign_if_supported(color_notice_label)
    color_pick_btn = gtk_module.Button(label="Pick Color")
    color_apply_btn = gtk_module.Button(label="Color Apply")
    color_cancel_btn = gtk_module.Button(label="Color Cancel")
    color_editor_box = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
    color_editor_title = gtk_module.Label(label="Background color (#RRGGBB)")
    set_xalign_if_supported(color_editor_title)
    color_editor_box.pack_start(color_editor_title, False, False, 0)
    color_picker_host = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=0)
    color_editor_box.pack_start(color_picker_host, True, True, 0)
    color_editor_box.pack_start(color_value_entry, False, False, 0)
    color_actions = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
    color_actions.pack_start(color_pick_btn, False, False, 0)
    color_actions.pack_start(color_apply_btn, False, False, 0)
    color_actions.pack_start(color_cancel_btn, False, False, 0)
    color_editor_box.pack_start(color_actions, False, False, 0)
    color_notice_separator = build_horizontal_separator(gtk_module)
    color_editor_box.pack_start(color_notice_separator, False, False, 0)
    color_editor_box.pack_start(color_state_label, False, False, 0)
    color_editor_box.pack_start(color_notice_label, False, False, 0)
    if hasattr(color_window, "add"):
        color_window.add(color_editor_box)

    return {
        "color_window": color_window,
        "color_value_entry": color_value_entry,
        "color_state_label": color_state_label,
        "color_notice_label": color_notice_label,
        "color_notice_separator": color_notice_separator,
        "color_picker_host": color_picker_host,
        "color_pick_btn": color_pick_btn,
        "color_apply_btn": color_apply_btn,
        "color_cancel_btn": color_cancel_btn,
    }


def build_about_dialog_section(gtk_module: Any) -> dict[str, Any]:
    about_window = gtk_module.Window(title="About Harite")
    if hasattr(about_window, "set_default_size"):
        about_window.set_default_size(420, 220)
    if hasattr(about_window, "set_resizable"):
        about_window.set_resizable(False)

    about_shell = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=0)
    about_top_spacer = gtk_module.Label(label="")
    about_bottom_spacer = gtk_module.Label(label="")
    about_box = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
    about_title_label = gtk_module.Label(label="Harite")
    about_version_label = gtk_module.Label(label="Version: -")
    about_description_label = gtk_module.Label(label="")
    about_credits_label = gtk_module.Label(label="Credits: -")
    about_license_label = gtk_module.Label(label="License: -")
    for label in (
        about_title_label,
        about_version_label,
        about_description_label,
        about_credits_label,
        about_license_label,
    ):
        set_xalign_if_supported(label, 0.5)

    about_close_btn = gtk_module.Button(label="About Close")
    about_box.pack_start(about_title_label, False, False, 0)
    about_box.pack_start(about_version_label, False, False, 0)
    about_box.pack_start(about_description_label, False, False, 0)
    about_box.pack_start(about_credits_label, False, False, 0)
    about_box.pack_start(about_license_label, False, False, 0)
    about_close_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=0)
    about_close_left = gtk_module.Label(label="")
    about_close_right = gtk_module.Label(label="")
    about_close_row.pack_start(about_close_left, True, True, 0)
    about_close_row.pack_start(about_close_btn, False, False, 0)
    about_close_row.pack_start(about_close_right, True, True, 0)
    about_box.pack_start(about_close_row, False, False, 0)
    about_shell.pack_start(about_top_spacer, True, True, 0)
    about_shell.pack_start(about_box, False, False, 0)
    about_shell.pack_start(about_bottom_spacer, True, True, 0)
    if hasattr(about_window, "add"):
        about_window.add(about_shell)

    return {
        "about_window": about_window,
        "about_title_label": about_title_label,
        "about_version_label": about_version_label,
        "about_description_label": about_description_label,
        "about_credits_label": about_credits_label,
        "about_license_label": about_license_label,
        "about_close_btn": about_close_btn,
    }
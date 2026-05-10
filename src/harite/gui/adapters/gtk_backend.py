"""GTK backend loader for optional UI signal binding.

This adapter is intentionally optional. It should only be used in environments
where PyGObject/GTK is available.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable

from harite.core import DEFAULT_BACKGROUND_COLOR_HEX, is_background_color_literal, normalize_background_color
from harite.gui.adapters.gtk_runtime_builders import build_action_cluster_section
from harite.gui.adapters.gtk_runtime_builders import build_header_section
from harite.gui.adapters.gtk_runtime_builders import build_margins_tab_section
from harite.gui.adapters.gtk_runtime_builders import build_watch_tab_section
from harite.gui.adapters.gtk_runtime_dialogs import AboutDialogProxy as _AboutDialogProxy
from harite.gui.adapters.gtk_runtime_dialogs import ColorDialogProxy as _ColorDialogProxy
from harite.gui.adapters.gtk_runtime_dialogs import OpenDialogProxy as _OpenDialogProxy
from harite.gui.adapters.gtk_runtime_dialogs import SavePathDialogProxy as _SavePathDialogProxy
from harite.gui.adapters.gtk_runtime_dialogs import SettingsDialogProxy as _SettingsDialogProxy
from harite.gui.adapters.gtk_runtime_dialogs import SrcdirDialogProxy as _SrcdirDialogProxy
from harite.gui.adapters.gtk_runtime_preview import build_preview_crop_boxes
from harite.gui.adapters.gtk_runtime_preview import clear_preview_widget
from harite.gui.adapters.gtk_runtime_preview import get_gdkpixbuf_module
from harite.gui.adapters.gtk_runtime_preview import preview_target_size
from harite.gui.adapters.gtk_runtime_preview import set_preview_widget
from harite.gui.adapters.gtk_runtime_preview import sync_result_preview_from_owner
from harite.gui.adapters.gtk_runtime_sync import build_margin_settings_preview
from harite.gui.adapters.gtk_runtime_sync import parse_margin_values
from harite.gui.adapters.gtk_runtime_sync import refresh_margins_controls
from harite.gui.adapters.gtk_runtime_sync import sync_feedback_from_owner
from harite.gui.adapters.gtk_runtime_sync import sync_input_state_from_owner
from harite.gui.adapters.gtk_runtime_sync import sync_main_state_from_owner
from harite.gui.adapters.gtk_runtime_sync import sync_margins_state_from_owner
from harite.gui.adapters.gtk_runtime_sync import sync_watch_state_from_owner
from harite.gui.adapters.gtk_runtime_watch import get_glib_module
from harite.gui.adapters.gtk_runtime_watch import on_watch_timer_event
from harite.gui.adapters.gtk_runtime_watch import run_watch_cycle_for_side
from harite.gui.adapters.gtk_runtime_watch import run_watch_cycle_once as run_runtime_watch_cycle_once
from harite.gui.adapters.gtk_runtime_watch import start_watch_timer
from harite.gui.adapters.gtk_runtime_watch import stop_watch_timer
from harite.positioning import format_position_pair, parse_position_pair
from harite.watch import WatchCycleState


SAVE_PATH_DIALOG_OBJECT_ALIASES: tuple[str, ...] = (
    "SavePathDialog",
)

SAVE_PATH_STATE_LABEL_ALIASES: tuple[str, ...] = (
    "lblSavePathState",
)

SAVE_PATH_SELECTED_HANDLER_NAMES: tuple[str, ...] = (
    "on_save_path_selected",
)

SAVE_PATH_CANCELED_HANDLER_NAMES: tuple[str, ...] = (
    "on_save_path_selection_canceled",
)

SAVE_PATH_DESTROY_HANDLER_NAMES: tuple[str, ...] = (
    "on_close_save_path_dialog",
)

SETTINGS_DIALOG_OBJECT_ALIASES: tuple[str, ...] = (
    "SettingsDialog",
)

MARGIN_TEXT_MODE_VISIBLE_LABELS: dict[str, str] = {
    "none": "Off",
    "params": "Params",
    "free": "Text",
    "combo": "Both",
}


def _default_apply_mode() -> str:
    session_markers = (
        os.environ.get("XDG_CURRENT_DESKTOP", ""),
        os.environ.get("XDG_SESSION_DESKTOP", ""),
        os.environ.get("DESKTOP_SESSION", ""),
        os.environ.get("GDMSESSION", ""),
    )
    is_xfce_session = any("xfce" in marker.strip().lower() for marker in session_markers if marker)
    return "per-monitor-auto-split" if is_xfce_session else "single-file"


class GtkRuntimeSignalBackend:
    """Minimal GTK runtime backend that does not require Glade parsing.

    This fallback keeps present/bind flows usable even when a legacy Glade
    resource cannot be consumed by Gtk.Builder at runtime.
    """

    def __init__(self, gtk_module: Any) -> None:
        self._gtk = gtk_module
        self._signal_handlers: dict[str, Callable[..., Any]] = {}
        self._input_path_l = ""
        self._input_path_r = ""
        self._prefs_apply_mode_preserved: str | None = None
        self._prefs_apply_mode_syncing = False
        self._watch_srcdir_l = ""
        self._watch_srcdir_r = ""
        self._watch_running = False
        self._watch_state_l = WatchCycleState()
        self._watch_state_r = WatchCycleState()
        self._watch_previous_l: Path | None = None
        self._watch_previous_r: Path | None = None
        self._watch_timer_source_id: int | None = None

        window = gtk_module.Window(title="Harite")
        if hasattr(window, "set_resizable"):
            # P5-2 policy: modern desktop UX expects a resizable main window.
            window.set_resizable(True)
        if hasattr(window, "set_default_size"):
            window.set_default_size(1040, 720)

        if hasattr(gtk_module, "Box") and hasattr(gtk_module, "Label"):
            root = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=10)
            root.set_border_width(10)
            header_widgets = build_header_section(gtk_module, root)
            header_col = header_widgets["header_col"]
            title = header_widgets["title"]
            subtitle = header_widgets["subtitle"]
            command_bar = header_widgets["command_bar"]
            command_section_label = header_widgets["command_section_label"]
            btn_setting = header_widgets["btn_setting"]
            btn_help = header_widgets["btn_help"]
            btn_about = header_widgets["btn_about"]
            btn_set_color = header_widgets["btn_set_color"]
            flow_row = header_widgets["flow_row"]
            flow_legend_label = header_widgets["flow_legend_label"]
            optimize_btn = header_widgets["optimize_btn"]

            top_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=8)
            top_margin_label = gtk_module.Label(label="Top margin (px)")
            if hasattr(top_margin_label, "set_xalign"):
                top_margin_label.set_xalign(0.0)
            top_margin_spin = gtk_module.SpinButton()
            self._configure_spin_button(top_margin_spin, minimum=0, maximum=250, step=1, page=10)

            # Row 1: center body
            center_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=10)
            root.pack_start(center_row, True, True, 0)

            left_margin_shell = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=0)
            left_margin_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
            left_margin_label = gtk_module.Label(label="Left margin (px)")
            if hasattr(left_margin_label, "set_xalign"):
                left_margin_label.set_xalign(0.0)
            left_margin_spin = gtk_module.SpinButton()
            self._configure_spin_button(left_margin_spin, minimum=0, maximum=500, step=1, page=10)

            command_tabs = gtk_module.Notebook()
            center_row.pack_start(command_tabs, True, True, 0)

            def _build_centered_page(content: Any) -> Any:
                page_shell = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=0)
                top_spacer = gtk_module.Label(label="")
                page_shell.pack_start(top_spacer, True, True, 0)
                center_shell = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=0)
                page_shell.pack_start(center_shell, False, False, 0)
                left_spacer = gtk_module.Label(label="")
                right_spacer = gtk_module.Label(label="")
                center_shell.pack_start(left_spacer, True, True, 0)
                center_shell.pack_start(content, False, False, 0)
                center_shell.pack_start(right_spacer, True, True, 0)
                bottom_spacer = gtk_module.Label(label="")
                page_shell.pack_start(bottom_spacer, True, True, 0)
                return page_shell

            main_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=12)
            main_section_label = gtk_module.Label(label="Main")
            main_page_shell = _build_centered_page(main_col)

            compose_grid = gtk_module.Grid()
            if hasattr(compose_grid, "set_column_spacing"):
                compose_grid.set_column_spacing(32)
            if hasattr(compose_grid, "set_row_spacing"):
                compose_grid.set_row_spacing(12)
            main_col.pack_start(compose_grid, True, True, 0)

            left_display_grid = gtk_module.Grid()
            right_display_grid = gtk_module.Grid()
            if hasattr(left_display_grid, "set_column_spacing"):
                left_display_grid.set_column_spacing(6)
            if hasattr(left_display_grid, "set_row_spacing"):
                left_display_grid.set_row_spacing(8)
            if hasattr(right_display_grid, "set_column_spacing"):
                right_display_grid.set_column_spacing(6)
            if hasattr(right_display_grid, "set_row_spacing"):
                right_display_grid.set_row_spacing(8)
            tgl_upper_l = gtk_module.ToggleButton(label="Top-L")
            tgl_upper_r = gtk_module.ToggleButton(label="Top-R")
            tgl_lower_l = gtk_module.ToggleButton(label="Bottom-L")
            tgl_lower_r = gtk_module.ToggleButton(label="Bottom-R")
            tgl_push_left_l = gtk_module.ToggleButton(label="Left-L")
            tgl_push_right_l = gtk_module.ToggleButton(label="Right-L")
            btn_get_img_l = gtk_module.Button(label="Open-L")
            tgl_push_left_r = gtk_module.ToggleButton(label="Left-R")
            tgl_push_right_r = gtk_module.ToggleButton(label="Right-R")
            btn_get_img_r = gtk_module.Button(label="Open-R")

            if hasattr(left_display_grid, "attach"):
                left_display_grid.attach(tgl_upper_l, 1, 0, 1, 1)
                left_display_grid.attach(tgl_push_left_l, 0, 1, 1, 1)
                left_display_grid.attach(btn_get_img_l, 1, 1, 1, 1)
                left_display_grid.attach(tgl_push_right_l, 2, 1, 1, 1)
                left_display_grid.attach(tgl_lower_l, 1, 2, 1, 1)

            if hasattr(compose_grid, "attach"):
                compose_grid.attach(left_display_grid, 0, 0, 1, 1)

            input_row_l = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            input_entry_l = gtk_module.Label(label="")
            if hasattr(input_entry_l, "set_xalign"):
                input_entry_l.set_xalign(0.0)
            btn_clr_path_l = gtk_module.Button(label="Clear-L")
            input_row_l.pack_start(input_entry_l, True, True, 0)
            input_row_l.pack_start(btn_clr_path_l, False, False, 0)
            if hasattr(compose_grid, "attach"):
                compose_grid.attach(input_row_l, 0, 1, 1, 1)

            if hasattr(right_display_grid, "attach"):
                right_display_grid.attach(tgl_upper_r, 1, 0, 1, 1)
                right_display_grid.attach(tgl_push_left_r, 0, 1, 1, 1)
                right_display_grid.attach(btn_get_img_r, 1, 1, 1, 1)
                right_display_grid.attach(tgl_push_right_r, 2, 1, 1, 1)
                right_display_grid.attach(tgl_lower_r, 1, 2, 1, 1)

            if hasattr(compose_grid, "attach"):
                compose_grid.attach(right_display_grid, 1, 0, 1, 1)

            input_row_r = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            input_entry_r = gtk_module.Label(label="")
            if hasattr(input_entry_r, "set_xalign"):
                input_entry_r.set_xalign(0.0)
            btn_clr_path_r = gtk_module.Button(label="Clear-R")
            input_row_r.pack_start(input_entry_r, True, True, 0)
            input_row_r.pack_start(btn_clr_path_r, False, False, 0)
            if hasattr(compose_grid, "attach"):
                compose_grid.attach(input_row_r, 1, 1, 1, 1)

            pick_state_label = gtk_module.Label(label="")
            if hasattr(pick_state_label, "set_xalign"):
                pick_state_label.set_xalign(0.0)

            default_apply_mode = _default_apply_mode()
            action_widgets = build_action_cluster_section(gtk_module, compose_grid, default_apply_mode=default_apply_mode)
            action_cluster_row = action_widgets["action_cluster_row"]
            optimize_group = action_widgets["optimize_group"]
            apply_group = action_widgets["apply_group"]
            optimize_section_label = action_widgets["optimize_section_label"]
            optimize_row = action_widgets["optimize_row"]
            optimize_modern_btn = action_widgets["optimize_modern_btn"]
            optimize_result = action_widgets["optimize_result"]
            apply_section_label = action_widgets["apply_section_label"]
            apply_row = action_widgets["apply_row"]
            apply_btn = action_widgets["apply_btn"]
            apply_target = action_widgets["apply_target"]
            rad_apply_single = action_widgets["rad_apply_single"]
            rad_apply_per_monitor = action_widgets["rad_apply_per_monitor"]
            apply_mode_label = action_widgets["apply_mode_label"]
            preview_group = action_widgets["preview_group"]
            preview_images_row = action_widgets["preview_images_row"]
            preview_left = action_widgets["preview_left"]
            preview_right = action_widgets["preview_right"]
            preview_left_assignment = action_widgets["preview_left_assignment"]
            preview_right_assignment = action_widgets["preview_right_assignment"]
            preview_left_result = action_widgets["preview_left_result"]
            preview_right_result = action_widgets["preview_right_result"]
            preview_state_label = action_widgets["preview_state_label"]
            preview_source_label = action_widgets["preview_source_label"]
            preview_assist_label = action_widgets["preview_assist_label"]
            preview_section_label = action_widgets["preview_section_label"]

            do_it_plan_label = gtk_module.Label(label="Debug: apply is immediate")
            if hasattr(do_it_plan_label, "set_xalign"):
                do_it_plan_label.set_xalign(0.0)

            save_path_state_label = gtk_module.Label(label="Save path: idle")
            if hasattr(save_path_state_label, "set_xalign"):
                save_path_state_label.set_xalign(0.0)

            save_target_label = gtk_module.Label(label="Save target: not-selected")
            if hasattr(save_target_label, "set_xalign"):
                save_target_label.set_xalign(0.0)

            priority_note_label = gtk_module.Label(
                label="Rule: margins define area; align/valign act inside it"
            )
            if hasattr(priority_note_label, "set_xalign"):
                priority_note_label.set_xalign(0.0)

            style_legend_label = gtk_module.Label(label="Current behavior: margins are global to the composite canvas")
            if hasattr(style_legend_label, "set_xalign"):
                style_legend_label.set_xalign(0.0)

            current_state_section_label = gtk_module.Label(label="Main Window Current alignment:")
            if hasattr(current_state_section_label, "set_xalign"):
                current_state_section_label.set_xalign(0.0)

            current_margins_label = gtk_module.Label(label="margins=0,0,0,0")
            if hasattr(current_margins_label, "set_xalign"):
                current_margins_label.set_xalign(0.0)

            current_left_label = gtk_module.Label(label="L: align=center valign=center")
            if hasattr(current_left_label, "set_xalign"):
                current_left_label.set_xalign(0.0)

            current_right_label = gtk_module.Label(label="R: align=center valign=center")
            if hasattr(current_right_label, "set_xalign"):
                current_right_label.set_xalign(0.0)

            command_tabs.append_page(main_page_shell, main_section_label)

            right_margin_shell = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=0)
            right_margin_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
            right_margin_label = gtk_module.Label(label="Right margin (px)")
            if hasattr(right_margin_label, "set_xalign"):
                right_margin_label.set_xalign(0.0)
            right_margin_spin = gtk_module.SpinButton()
            self._configure_spin_button(right_margin_spin, minimum=0, maximum=500, step=1, page=10)

            bottom_margin_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=8)
            bottom_margin_label = gtk_module.Label(label="Bottom margin (px)")
            if hasattr(bottom_margin_label, "set_xalign"):
                bottom_margin_label.set_xalign(0.0)
            bottom_margin_spin = gtk_module.SpinButton()
            self._configure_spin_button(bottom_margin_spin, minimum=0, maximum=250, step=1, page=10)

            open_dialog_proxy = _OpenDialogProxy(
                gtk_module,
                window,
                self._on_open_dialog_confirmed,
                self._on_open_dialog_canceled,
            )
            save_path_dialog_proxy = _SavePathDialogProxy(
                gtk_module,
                window,
                self._on_save_path_filename_changed,
                self._on_native_save_path_confirmed,
                self._on_native_save_path_canceled,
            )
            prefs_window = gtk_module.Window(title="Settings")
            if hasattr(prefs_window, "set_default_size"):
                prefs_window.set_default_size(520, 420)
            if hasattr(prefs_window, "set_resizable"):
                prefs_window.set_resizable(True)
            settings_dialog_proxy = _SettingsDialogProxy(prefs_window)
            if hasattr(prefs_window, "connect"):
                prefs_window.connect(
                    "delete-event",
                    lambda *_args: self._on_preferences_window_delete_event(),
                )
            color_window = gtk_module.Window(title="Background Color")
            if hasattr(color_window, "set_default_size"):
                color_window.set_default_size(360, 140)
            if hasattr(color_window, "set_resizable"):
                color_window.set_resizable(False)
            color_value_entry = gtk_module.Entry()
            color_state_label = gtk_module.Label(label=f"Color: {DEFAULT_BACKGROUND_COLOR_HEX}")
            if hasattr(color_state_label, "set_xalign"):
                color_state_label.set_xalign(0.0)
            color_apply_btn = gtk_module.Button(label="Color Apply")
            color_cancel_btn = gtk_module.Button(label="Color Cancel")
            color_editor_box = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
            color_editor_title = gtk_module.Label(label="Background color (#RRGGBB)")
            if hasattr(color_editor_title, "set_xalign"):
                color_editor_title.set_xalign(0.0)
            color_editor_box.pack_start(color_editor_title, False, False, 0)
            color_editor_box.pack_start(color_value_entry, False, False, 0)
            color_actions = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            color_actions.pack_start(color_apply_btn, False, False, 0)
            color_actions.pack_start(color_cancel_btn, False, False, 0)
            color_editor_box.pack_start(color_actions, False, False, 0)
            if hasattr(color_window, "add"):
                color_window.add(color_editor_box)
            color_dialog_proxy = _ColorDialogProxy(
                gtk_module,
                window,
                color_window,
                color_value_entry,
                color_state_label,
                self._on_color_dialog_confirmed,
                self._on_color_dialog_canceled,
            )
            if hasattr(color_window, "connect"):
                color_window.connect(
                    "delete-event",
                    lambda *_args: self._on_color_window_delete_event(),
                )
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
                if hasattr(label, "set_xalign"):
                    label.set_xalign(0.5)
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
            about_dialog_proxy = _AboutDialogProxy(
                about_window,
                about_title_label,
                about_version_label,
                about_description_label,
                about_credits_label,
                about_license_label,
            )
            if hasattr(about_window, "connect"):
                about_window.connect(
                    "delete-event",
                    lambda *_args: self._on_about_window_delete_event(),
                )
            srcdir_dialog_proxy = _SrcdirDialogProxy(
                gtk_module,
                window,
                self._on_srcdir_dialog_confirmed,
                self._on_srcdir_dialog_canceled,
            )

            prefs_apply_btn = gtk_module.Button(label="Settings Apply")
            prefs_load_btn = gtk_module.Button(label="Settings Load")
            prefs_save_btn = gtk_module.Button(label="Settings Save")
            prefs_close_btn = gtk_module.Button(label="Settings Close")
            prefs_state_label = gtk_module.Label(label="Settings: idle")
            if hasattr(prefs_state_label, "set_xalign"):
                prefs_state_label.set_xalign(0.0)
            prefs_editor_box = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
            prefs_editor_title = gtk_module.Label(label="Settings")
            if hasattr(prefs_editor_title, "set_xalign"):
                prefs_editor_title.set_xalign(0.0)
            prefs_editor_box.pack_start(prefs_editor_title, False, False, 0)

            def _prefs_row(label_text: str, *widgets: Any) -> Any:
                row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
                row_label = gtk_module.Label(label=label_text)
                if hasattr(row_label, "set_xalign"):
                    row_label.set_xalign(0.0)
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
            self._configure_spin_button(prefs_quality_spin, minimum=1, maximum=100, step=1, page=10, initial=90)
            prefs_margin_text_mode_entry = gtk_module.Entry()
            prefs_margin_text_entry = gtk_module.Entry()
            prefs_margin_text_position_entry = gtk_module.Entry()
            prefs_margin_text_max_lines_spin = gtk_module.SpinButton()
            self._configure_spin_button(
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
            prefs_apply_single.connect(
                "toggled",
                lambda widget, *_args: self._on_preferences_apply_mode_toggled(widget, "single-file"),
            )
            prefs_apply_per_monitor.connect(
                "toggled",
                lambda widget, *_args: self._on_preferences_apply_mode_toggled(widget, "per-monitor-auto-split"),
            )
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
            prefs_editor_box.pack_start(prefs_state_label, False, False, 0)

            if hasattr(prefs_window, "add"):
                prefs_window.add(prefs_editor_box)

            watch_widgets = build_watch_tab_section(gtk_module, configure_spin_button=self._configure_spin_button)
            watch_tab_box = watch_widgets["watch_tab_box"]
            watch_label = watch_widgets["watch_label"]
            watch_tab_title = watch_widgets["watch_tab_title"]
            watch_controls_row = watch_widgets["watch_controls_row"]
            watch_detail_row = watch_widgets["watch_detail_row"]
            btn_open_srcdir_l = watch_widgets["btn_open_srcdir_l"]
            btn_open_srcdir_r = watch_widgets["btn_open_srcdir_r"]
            interval_spin = watch_widgets["interval_spin"]
            interval_label = watch_widgets["interval_label"]
            btn_daemonize = watch_widgets["btn_daemonize"]
            btn_cancel_daemonize = watch_widgets["btn_cancel_daemonize"]
            watch_sources_label = watch_widgets["watch_sources_label"]
            watch_current_label = watch_widgets["watch_current_label"]
            watch_output_label = watch_widgets["watch_output_label"]

            margins_widgets = build_margins_tab_section(
                gtk_module,
                top_margin_label=top_margin_label,
                top_margin_spin=top_margin_spin,
                left_margin_label=left_margin_label,
                left_margin_spin=left_margin_spin,
                priority_note_label=priority_note_label,
                style_legend_label=style_legend_label,
                current_state_section_label=current_state_section_label,
                current_margins_label=current_margins_label,
                current_left_label=current_left_label,
                current_right_label=current_right_label,
                configure_spin_button=self._configure_spin_button,
                apply_margin_text_widget_style=self._apply_margin_text_widget_style,
            )
            margins_tab_box = margins_widgets["margins_tab_box"]
            margins_section_label = margins_widgets["margins_section_label"]
            right_margin_col = margins_widgets["right_margin_col"]
            right_margin_label = margins_widgets["right_margin_label"]
            right_margin_spin = margins_widgets["right_margin_spin"]
            bottom_margin_row = margins_widgets["bottom_margin_row"]
            bottom_margin_label = margins_widgets["bottom_margin_label"]
            bottom_margin_spin = margins_widgets["bottom_margin_spin"]
            margins_tab_title = margins_widgets["margins_tab_title"]
            margin_text_tabs = margins_widgets["margin_text_tabs"]
            margin_settings_page = margins_widgets["margin_settings_page"]
            margin_text_page = margins_widgets["margin_text_page"]
            margin_settings_preview_label = margins_widgets["margin_settings_preview_label"]
            margin_text_section_label = margins_widgets["margin_text_section_label"]
            margin_text_mode_label = margins_widgets["margin_text_mode_label"]
            margin_text_mode_off = margins_widgets["margin_text_mode_off"]
            margin_text_mode_settings = margins_widgets["margin_text_mode_settings"]
            margin_text_mode_text = margins_widgets["margin_text_mode_text"]
            margin_text_mode_both = margins_widgets["margin_text_mode_both"]
            margin_text_entry = margins_widgets["margin_text_entry"]
            margin_position_left_top = margins_widgets["margin_position_left_top"]
            margin_position_right_bottom = margins_widgets["margin_position_right_bottom"]
            margin_position_left_bottom = margins_widgets["margin_position_left_bottom"]
            margin_position_right_top = margins_widgets["margin_position_right_top"]
            margin_text_max_lines_spin = margins_widgets["margin_text_max_lines_spin"]
            self._current_state_summary_display = margins_widgets["current_state_summary_display"]
            margins_page_shell = _build_centered_page(margins_tab_box)
            command_tabs.append_page(margins_page_shell, margins_tab_title)

            watch_page_shell = _build_centered_page(watch_tab_box)
            command_tabs.append_page(watch_page_shell, watch_tab_title)

            # Row 4: status row (Glade statusbar equivalent)
            footer_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=4)
            root.pack_start(footer_col, False, False, 0)

            status_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=8)
            footer_col.pack_start(status_row, False, False, 0)
            status_label = gtk_module.Label(label="Status: ready")
            if hasattr(status_label, "set_xalign"):
                status_label.set_xalign(0.0)
            status_row.pack_start(status_label, False, False, 0)
            status_spacer = gtk_module.Label(label="")
            status_row.pack_start(status_spacer, True, True, 0)
            watch_summary_label = gtk_module.Label(label="Watch: stopped")
            if hasattr(watch_summary_label, "set_xalign"):
                watch_summary_label.set_xalign(0.0)

            error_label = gtk_module.Label(label="Error: none")
            if hasattr(error_label, "set_xalign"):
                error_label.set_xalign(0.0)

            if hasattr(window, "add"):
                window.add(root)

            self._objects = {
                "WallPosit_MainWindow": window,
                "main_window": window,
                "boxRoot": root,
                "lblTopMargin": top_margin_label,
                "spnTopMargin": top_margin_spin,
                "lblLeftMargin": left_margin_label,
                "spnLeftMargin": left_margin_spin,
                "lblTitle": title,
                "lblSubtitle": subtitle,
                "lblMainSection": main_section_label,
                "boxMainSection": main_col,
                "composeGrid": compose_grid,
                "leftDisplayCol": left_display_grid,
                "rightDisplayCol": right_display_grid,
                "inputRowL": input_row_l,
                "inputRowR": input_row_r,
                "actionClusterRow": action_cluster_row,
                "actionClusterCol": optimize_group,
                "tglUpperL": tgl_upper_l,
                "tglUpperR": tgl_upper_r,
                "tglPushLeftL": tgl_push_left_l,
                "tglPushRightL": tgl_push_right_l,
                "tglLowerL": tgl_lower_l,
                "tglPushLeftR": tgl_push_left_r,
                "tglPushRightR": tgl_push_right_r,
                "tglLowerR": tgl_lower_r,
                "btnGetImgL": btn_get_img_l,
                "btnGetImgR": btn_get_img_r,
                "lblPickState": pick_state_label,
                "entPathL": input_entry_l,
                "btnClrPathL": btn_clr_path_l,
                "entPathR": input_entry_r,
                "btnClrPathR": btn_clr_path_r,
                "vbox5": right_margin_col,
                "lblRightMargin": right_margin_label,
                "spnRightMargin": right_margin_spin,
                "hbox12": bottom_margin_row,
                "lblBottomMargin": bottom_margin_label,
                "spnBottomMargin": bottom_margin_spin,
                "lblOptimizeSection": optimize_section_label,
                "boxOptimizeSection": optimize_row,
                "btnSave": optimize_btn,
                "btnOptimize": optimize_modern_btn,
                "lblOptimizeResult": optimize_result,
                "lblApplySection": apply_section_label,
                "boxApplySection": apply_row,
                "btnSetWall": apply_btn,
                "lblApplyTarget": apply_target,
                "lblPreviewSection": preview_section_label,
                "boxPreviewSection": preview_group,
                "boxPreviewImagesRow": preview_images_row,
                "imgPreviewL": preview_left,
                "imgPreviewR": preview_right,
                "lblPreviewAssignL": preview_left_assignment,
                "lblPreviewAssignR": preview_right_assignment,
                "lblPreviewResultL": preview_left_result,
                "lblPreviewResultR": preview_right_result,
                "lblPreviewState": preview_state_label,
                "lblPreviewSource": preview_source_label,
                "lblPreviewAssist": preview_assist_label,
                "radApplySingle": rad_apply_single,
                "radApplyPerMonitor": rad_apply_per_monitor,
                "lblApplyMode": apply_mode_label,
                "lblDoItPlanned": do_it_plan_label,
                "lblSaveTarget": save_target_label,
                "lblPriorityRule": priority_note_label,
                "lblStyleLegend": style_legend_label,
                "lblCurrentStateSection": current_state_section_label,
                "lblCurrentMargins": current_margins_label,
                "lblCurrentStateL": current_left_label,
                "lblCurrentStateR": current_right_label,
                "lblCommandSection": command_section_label,
                "commandTabs": command_tabs,
                "hbox14": command_bar,
                "btnSetting": btn_setting,
                "btnSettings": btn_setting,
                "btnSettingsApply": prefs_apply_btn,
                "btnSettingsLoad": prefs_load_btn,
                "btnSettingsSave": prefs_save_btn,
                "btnSettingsClose": prefs_close_btn,
                "lblSettingsState": prefs_state_label,
                "boxSettingsEditor": prefs_editor_box,
                "settingsWindow": prefs_window,
                "lblSettingsEditorTitle": prefs_editor_title,
                "entSettingsResolution": prefs_resolution_entry,
                "entSettingsScaling": prefs_scaling_entry,
                "radSettingsTwoScreenAuto": prefs_two_screen_auto,
                "radSettingsTwoScreenOn": prefs_two_screen_on,
                "radSettingsTwoScreenOff": prefs_two_screen_off,
                "entSettingsLDisplay": prefs_l_display_entry,
                "entSettingsRDisplay": prefs_r_display_entry,
                "entSettingsMargins": prefs_margins_entry,
                "entSettingsAlign": prefs_align_entry,
                "entSettingsValign": prefs_valign_entry,
                "spnSettingsQuality": prefs_quality_spin,
                "entSettingsMarginTextMode": prefs_margin_text_mode_entry,
                "entSettingsMarginText": prefs_margin_text_entry,
                "entSettingsMarginTextPosition": prefs_margin_text_position_entry,
                "spnSettingsMarginTextMaxLines": prefs_margin_text_max_lines_spin,
                "entSettingsPlugin": prefs_plugin_entry,
                "radSettingsApplySingle": prefs_apply_single,
                "radSettingsApplyPerMonitor": prefs_apply_per_monitor,
                "entSettingsImportPath": prefs_import_path_entry,
                "entSettingsExportPath": prefs_export_path_entry,
                "btnSetColor": btn_set_color,
                "ColorDialog": color_dialog_proxy,
                "colorWindow": color_window,
                "entColorValue": color_value_entry,
                "lblColorState": color_state_label,
                "btnColorApply": color_apply_btn,
                "btnColorCancel": color_cancel_btn,
                "AboutDialog": about_dialog_proxy,
                "aboutWindow": about_window,
                "lblAboutTitle": about_title_label,
                "lblAboutVersion": about_version_label,
                "lblAboutDescription": about_description_label,
                "lblAboutCredits": about_credits_label,
                "lblAboutLicense": about_license_label,
                "btnAboutClose": about_close_btn,
                "ImgOpenDialog": open_dialog_proxy,
                "SrcdirDialog": srcdir_dialog_proxy,
                **{object_name: settings_dialog_proxy for object_name in SETTINGS_DIALOG_OBJECT_ALIASES},
                "watchTab": watch_tab_box,
                "marginsTab": margins_tab_box,
                "watchControlsRow": watch_controls_row,
                "watchDetailRow": watch_detail_row,
                "lblMarginsTabTitle": margins_tab_title,
                "lblMarginsSection": margins_section_label,
                "marginTextTabs": margin_text_tabs,
                "marginSettingsPage": margin_settings_page,
                "marginTextPage": margin_text_page,
                "lblMarginSettingsPreview": margin_settings_preview_label,
                "lblMarginTextSection": margin_text_section_label,
                "lblMarginTextMode": margin_text_mode_label,
                "radMarginTextModeOff": margin_text_mode_off,
                "radMarginTextModeSettings": margin_text_mode_settings,
                "radMarginTextModeText": margin_text_mode_text,
                "radMarginTextModeBoth": margin_text_mode_both,
                "txtMarginText": margin_text_entry,
                "radMarginTextPositionLeftTop": margin_position_left_top,
                "radMarginTextPositionRightBottom": margin_position_right_bottom,
                "radMarginTextPositionLeftBottom": margin_position_left_bottom,
                "radMarginTextPositionRightTop": margin_position_right_top,
                "spnMarginTextMaxLines": margin_text_max_lines_spin,
                "btnOpenSrcdirL": btn_open_srcdir_l,
                "btnOpenSrcdirR": btn_open_srcdir_r,
                "lblWatchSection": watch_label,
                "lblWatchTabTitle": watch_tab_title,
                "spnInterval": interval_spin,
                "lblInterval": interval_label,
                "btnDaemonize": btn_daemonize,
                "btnCancelDaemonize": btn_cancel_daemonize,
                "btnAbout": btn_about,
                "btnHelp": btn_help,
                "statusbar": footer_col,
                "flowRow": flow_row,
                "lblFlowLegend": flow_legend_label,
                "lblStatus": status_label,
                "lblError": error_label,
                "lblWatchSummary": watch_summary_label,
                "lblWatchSources": watch_sources_label,
                "lblWatchCurrent": watch_current_label,
                "lblWatchOutput": watch_output_label,
                **{object_name: save_path_state_label for object_name in SAVE_PATH_STATE_LABEL_ALIASES},
                **{object_name: save_path_dialog_proxy for object_name in SAVE_PATH_DIALOG_OBJECT_ALIASES},
            }

            for object_name, widget in self._objects.items():
                if hasattr(widget, "set_name"):
                    widget.set_name(object_name)
                elif not hasattr(widget, "get_name"):
                    setattr(widget, "name", object_name)

            # Why: fallback window must still exercise MainWindow handlers even when
            # legacy glade cannot be parsed at runtime.
            try:
                input_entry_l.connect("changed", self._on_input_changed)
            except Exception:
                pass
            try:
                input_entry_r.connect("changed", self._on_input_changed)
            except Exception:
                pass
            tgl_upper_l.connect("pressed", lambda *_args: self._on_direction_pressed("tglUpperL"))
            tgl_upper_l.connect("toggled", lambda *_args: self._on_direction_toggled("tglUpperL"))
            tgl_upper_l.connect("released", lambda *_args: self._on_direction_released("tglUpperL"))
            tgl_lower_l.connect("pressed", lambda *_args: self._on_direction_pressed("tglLowerL"))
            tgl_lower_l.connect("toggled", lambda *_args: self._on_direction_toggled("tglLowerL"))
            tgl_lower_l.connect("released", lambda *_args: self._on_direction_released("tglLowerL"))
            tgl_upper_r.connect("pressed", lambda *_args: self._on_direction_pressed("tglUpperR"))
            tgl_upper_r.connect("toggled", lambda *_args: self._on_direction_toggled("tglUpperR"))
            tgl_upper_r.connect("released", lambda *_args: self._on_direction_released("tglUpperR"))
            tgl_lower_r.connect("pressed", lambda *_args: self._on_direction_pressed("tglLowerR"))
            tgl_lower_r.connect("toggled", lambda *_args: self._on_direction_toggled("tglLowerR"))
            tgl_lower_r.connect("released", lambda *_args: self._on_direction_released("tglLowerR"))
            tgl_push_left_l.connect("pressed", lambda *_args: self._on_direction_pressed("tglPushLeftL"))
            tgl_push_left_l.connect("toggled", lambda *_args: self._on_direction_toggled("tglPushLeftL"))
            tgl_push_left_l.connect("released", lambda *_args: self._on_direction_released("tglPushLeftL"))
            tgl_push_right_l.connect("pressed", lambda *_args: self._on_direction_pressed("tglPushRightL"))
            tgl_push_right_l.connect("toggled", lambda *_args: self._on_direction_toggled("tglPushRightL"))
            tgl_push_right_l.connect("released", lambda *_args: self._on_direction_released("tglPushRightL"))
            tgl_push_left_r.connect("pressed", lambda *_args: self._on_direction_pressed("tglPushLeftR"))
            tgl_push_left_r.connect("toggled", lambda *_args: self._on_direction_toggled("tglPushLeftR"))
            tgl_push_left_r.connect("released", lambda *_args: self._on_direction_released("tglPushLeftR"))
            tgl_push_right_r.connect("pressed", lambda *_args: self._on_direction_pressed("tglPushRightR"))
            tgl_push_right_r.connect("toggled", lambda *_args: self._on_direction_toggled("tglPushRightR"))
            tgl_push_right_r.connect("released", lambda *_args: self._on_direction_released("tglPushRightR"))
            btn_get_img_l.connect("clicked", lambda *_args: self._on_pick_input_clicked("L"))
            btn_get_img_r.connect("clicked", lambda *_args: self._on_pick_input_clicked("R"))
            btn_clr_path_l.connect("clicked", lambda *_args: self._on_clear_input_clicked("L"))
            btn_clr_path_r.connect("clicked", lambda *_args: self._on_clear_input_clicked("R"))
            top_margin_spin.connect("value-changed", self._on_margin_changed)
            left_margin_spin.connect("value-changed", self._on_margin_changed)
            right_margin_spin.connect("value-changed", self._on_margin_changed)
            bottom_margin_spin.connect("value-changed", self._on_margin_changed)
            optimize_btn.connect("clicked", self._on_save_clicked)
            optimize_modern_btn.connect("clicked", self._on_optimize_clicked)
            apply_btn.connect("clicked", self._on_apply_clicked)
            btn_setting.connect("clicked", self._on_settings_clicked)
            prefs_apply_btn.connect("clicked", self._on_preferences_apply_clicked)
            prefs_load_btn.connect("clicked", self._on_preferences_load_clicked)
            prefs_save_btn.connect("clicked", self._on_preferences_save_clicked)
            prefs_close_btn.connect("clicked", self._on_preferences_close_clicked)
            rad_apply_single.connect(
                "toggled",
                lambda widget, *_args: self._on_apply_mode_toggled(widget, "single-file"),
            )
            rad_apply_per_monitor.connect(
                "toggled",
                lambda widget, *_args: self._on_apply_mode_toggled(widget, "per-monitor-auto-split"),
            )
            btn_set_color.connect("clicked", self._on_color_clicked)
            btn_about.connect("clicked", self._on_about_clicked)
            color_apply_btn.connect("clicked", self._on_color_dialog_apply_clicked)
            color_cancel_btn.connect("clicked", self._on_color_dialog_cancel_clicked)
            about_close_btn.connect("clicked", self._on_about_dialog_close_clicked)
            btn_open_srcdir_l.connect("clicked", lambda *_args: self._on_pick_srcdir_clicked("L"))
            btn_open_srcdir_r.connect("clicked", lambda *_args: self._on_pick_srcdir_clicked("R"))
            interval_spin.connect("value-changed", self._on_watch_interval_changed)
            btn_daemonize.connect("clicked", self._on_watch_start_clicked)
            btn_cancel_daemonize.connect("clicked", self._on_watch_stop_clicked)
            margin_text_mode_off.connect("toggled", lambda widget, *_args: self._on_margin_text_mode_toggled(widget, "none"))
            margin_text_mode_settings.connect("toggled", lambda widget, *_args: self._on_margin_text_mode_toggled(widget, "params"))
            margin_text_mode_text.connect("toggled", lambda widget, *_args: self._on_margin_text_mode_toggled(widget, "free"))
            margin_text_mode_both.connect("toggled", lambda widget, *_args: self._on_margin_text_mode_toggled(widget, "combo"))
            if hasattr(margin_text_entry, "get_buffer") and hasattr(margin_text_entry.get_buffer(), "connect"):
                margin_text_entry.get_buffer().connect("changed", lambda *_args: self._on_margin_text_changed(margin_text_entry))
            else:
                margin_text_entry.connect("changed", self._on_margin_text_changed)
            try:
                margin_text_entry.connect("key-press-event", self._on_margin_text_key_press)
            except Exception:
                pass
            margin_position_left_top.connect("toggled", lambda widget, *_args: self._on_margin_position_toggled(widget, "top"))
            margin_position_right_bottom.connect("toggled", lambda widget, *_args: self._on_margin_position_toggled(widget, "bottom"))
            margin_position_left_bottom.connect("toggled", lambda widget, *_args: self._on_margin_position_toggled(widget, "left"))
            margin_position_right_top.connect("toggled", lambda widget, *_args: self._on_margin_position_toggled(widget, "right"))
            margin_text_max_lines_spin.connect("value-changed", self._on_margin_text_max_lines_changed)
            self._refresh_current_state_labels()
            self._refresh_margins_controls()
        else:
            self._objects = {
                "WallPosit_MainWindow": window,
                "main_window": window,
            }

    def connect_signals(self, mapping: dict[str, Callable[..., Any]]) -> None:
        self._signal_handlers.update(mapping)
        owner = self._get_connected_owner()
        if owner is not None:
            self._sync_non_preview_state_from_owner(owner)

    def connect(self, handler_name: str, callback: Callable[..., Any]) -> None:
        self._signal_handlers[handler_name] = callback
        owner = self._get_connected_owner()
        if owner is not None:
            self._sync_non_preview_state_from_owner(owner)

    def _configure_spin_button(
        self,
        spin: Any,
        *,
        minimum: int,
        maximum: int,
        step: int,
        page: int,
        initial: int | None = None,
    ) -> None:
        if hasattr(spin, "set_numeric"):
            spin.set_numeric(True)
        if hasattr(spin, "set_range"):
            spin.set_range(minimum, maximum)
        if hasattr(spin, "set_increments"):
            spin.set_increments(step, page)
        if hasattr(spin, "set_value"):
            spin.set_value(minimum if initial is None else initial)

    def get_object(self, name: str) -> Any:
        return self._objects.get(name)

    def get_objects(self) -> list[Any]:
        return list(self._objects.values())

    def _set_status(self, message: str) -> None:
        status = self._objects.get("lblStatus")
        if status is not None and hasattr(status, "set_text"):
            status.set_text(message)

    def _set_error(self, message: str | None) -> None:
        if not message:
            self._set_label_text("lblError", "Error: none")
            return
        self._set_label_text("lblError", f"Error: {message}")

    def _set_feedback(self, *, phase: str, state: str, error: str | None = None) -> None:
        self._set_status(f"{phase}: {state}")
        self._set_error(error)

    def _set_label_text(self, object_name: str, message: str) -> None:
        label = self._objects.get(object_name)
        if label is not None and hasattr(label, "set_text"):
            label.set_text(message)

    def _set_entry_text(self, object_name: str, value: object | None) -> None:
        entry = self._objects.get(object_name)
        normalized = "" if value is None else str(value)
        if entry is not None and hasattr(entry, "get_text") and str(entry.get_text() or "") == normalized:
            return
        if entry is not None and hasattr(entry, "set_text"):
            entry.set_text(normalized)
            return
        if entry is not None and hasattr(entry, "get_buffer"):
            buffer = entry.get_buffer()
            if buffer is not None and hasattr(buffer, "get_text"):
                if hasattr(buffer, "get_bounds"):
                    start, end = buffer.get_bounds()
                else:
                    start = buffer.get_start_iter() if hasattr(buffer, "get_start_iter") else None
                    end = buffer.get_end_iter() if hasattr(buffer, "get_end_iter") else None
                if str(buffer.get_text(start, end, True) or "") == normalized:
                    return
            if buffer is not None and hasattr(buffer, "set_text"):
                buffer.set_text(normalized)

    def _sanitize_margin_text(self, value: str) -> str:
        return "\n".join(str(value or "").split("\n")[:5])

    def _apply_margin_text_widget_style(self, gtk_module: Any, shell: Any, entry: Any) -> None:
        try:
            import importlib

            gi = importlib.import_module("gi")
            gi.require_version("Gdk", "3.0")
            Gdk = importlib.import_module("gi.repository.Gdk")

            rgba = Gdk.RGBA()
            rgba.parse("#ffffff")
            state_flags = getattr(gtk_module, "StateFlags", None)
            normal_state = getattr(state_flags, "NORMAL", None) if state_flags is not None else None
            for widget in (shell, entry):
                if widget is not None and hasattr(widget, "override_background_color") and normal_state is not None:
                    widget.override_background_color(normal_state, rgba)
        except Exception:
            return

    def _on_margin_text_key_press(self, widget: Any, event: Any) -> bool:
        keyval = getattr(event, "keyval", None)
        if keyval is None:
            return False
        try:
            import importlib

            gi = importlib.import_module("gi")
            gi.require_version("Gdk", "3.0")
            Gdk = importlib.import_module("gi.repository.Gdk")

            return_keys = {
                getattr(Gdk, "KEY_Return", None),
                getattr(Gdk, "KEY_KP_Enter", None),
            }
        except Exception:
            return False

        if keyval not in return_keys:
            return False

        if hasattr(widget, "get_text"):
            current = str(widget.get_text() or "")
        elif hasattr(widget, "get_buffer"):
            buffer = widget.get_buffer()
            if buffer is not None and hasattr(buffer, "get_bounds") and hasattr(buffer, "get_text"):
                start, end = buffer.get_bounds()
                current = str(buffer.get_text(start, end, True) or "")
            else:
                current = ""
        else:
            current = ""

        return len(current.split("\n")) >= 5

    def _read_entry_text(self, object_name: str) -> str:
        entry = self._objects.get(object_name)
        if entry is None:
            return ""
        if hasattr(entry, "get_text"):
            return str(entry.get_text() or "").strip()
        if hasattr(entry, "get_buffer"):
            buffer = entry.get_buffer()
            if buffer is not None and hasattr(buffer, "get_text"):
                if hasattr(buffer, "get_bounds"):
                    start, end = buffer.get_bounds()
                else:
                    start = buffer.get_start_iter() if hasattr(buffer, "get_start_iter") else None
                    end = buffer.get_end_iter() if hasattr(buffer, "get_end_iter") else None
                return str(buffer.get_text(start, end, True) or "").strip()
        return str(getattr(entry, "text", "") or "").strip()

    def _set_spin_value(self, object_name: str, value: int) -> None:
        spin = self._objects.get(object_name)
        if spin is not None and hasattr(spin, "set_value"):
            spin.set_value(int(value))

    def _set_button_enabled(self, object_name: str, enabled: bool) -> None:
        button = self._objects.get(object_name)
        if button is not None and hasattr(button, "set_sensitive"):
            button.set_sensitive(bool(enabled))

    def _set_widget_enabled(self, object_name: str, enabled: bool) -> None:
        widget = self._objects.get(object_name)
        if widget is not None and hasattr(widget, "set_sensitive"):
            widget.set_sensitive(bool(enabled))

    def _set_notebook_page(self, object_name: str, page_index: int) -> None:
        notebook = self._objects.get(object_name)
        if notebook is not None and hasattr(notebook, "set_current_page"):
            notebook.set_current_page(int(page_index))

    def _get_save_path_dialog(self) -> Any | None:
        for object_name in SAVE_PATH_DIALOG_OBJECT_ALIASES:
            dialog = self._objects.get(object_name)
            if dialog is not None:
                return dialog
        return None

    def _get_save_path_destroy_callback(self) -> Callable[..., Any] | None:
        for handler_name in SAVE_PATH_DESTROY_HANDLER_NAMES:
            callback = self._signal_handlers.get(handler_name)
            if callback is not None:
                return callback
        return None

    def _set_save_path_state_text(self, message: str) -> None:
        for object_name in SAVE_PATH_STATE_LABEL_ALIASES:
            if self._objects.get(object_name) is not None:
                self._set_label_text(object_name, message)
                return

    def _current_save_path_filename(self) -> str:
        dialog = self._get_save_path_dialog()
        if dialog is None or not hasattr(dialog, "get_filename"):
            return ""
        return str(dialog.get_filename() or "").strip()

    def _refresh_save_target_label(self, filename: str | None = None) -> None:
        value = str(filename or "").strip()
        if not value:
            value = self._current_save_path_filename()
        if value:
            self._set_label_text("lblSaveTarget", f"Save target: {value}")
            return
        self._set_label_text("lblSaveTarget", "Save target: not-selected")

    def _refresh_watch_source_labels(self) -> None:
        left = self._watch_srcdir_l or "-"
        right = self._watch_srcdir_r or "-"
        self._set_label_text("lblWatchSources", f"Watch srcdirs: L={left} | R={right}")

    def _refresh_watch_summary_label(self) -> None:
        state = "running" if self._watch_running else "stopped"
        self._set_label_text("lblWatchSummary", f"Watch: {state}")
        self._set_label_text("lblWatchTabTitle", f"Watch ({state})")

    def _refresh_watch_current_label(self, left: str | None = None, right: str | None = None) -> None:
        current_left = left if left is not None else (str(self._watch_previous_l) if self._watch_previous_l else "-")
        current_right = right if right is not None else (str(self._watch_previous_r) if self._watch_previous_r else "-")
        if not self._watch_running and current_left == "-" and current_right == "-":
            self._set_label_text("lblWatchCurrent", "Watch current: idle")
            return
        self._set_label_text("lblWatchCurrent", f"Watch current: L={current_left} | R={current_right}")

    def _refresh_watch_output_label(self, output_dir: str | None = None) -> None:
        value = str(output_dir or "").strip() or "."
        self._set_label_text("lblWatchOutput", f"Watch output: {value}")

    def _get_handler_owner(self, handler_name: str) -> Any | None:
        callback = self._signal_handlers.get(handler_name)
        if callback is None:
            return None
        return getattr(callback, "__self__", None)

    def _get_connected_owner(self) -> Any | None:
        for callback in self._signal_handlers.values():
            owner = getattr(callback, "__self__", None)
            if owner is not None:
                return owner
        return None

    def _sync_watch_state_from_owner(self, owner: Any) -> None:
        sync_watch_state_from_owner(self, owner)

    def _parse_margin_values(self, value: object | None) -> tuple[int, int, int, int]:
        return parse_margin_values(value)

    def _sync_main_state_from_owner(self, owner: Any) -> None:
        sync_main_state_from_owner(self, owner)

    def _sync_input_state_from_owner(self, owner: Any) -> None:
        sync_input_state_from_owner(self, owner)

    def _sync_margins_state_from_owner(self, owner: Any) -> None:
        sync_margins_state_from_owner(self, owner)

    def _build_margin_settings_preview(self, owner: Any | None = None) -> str:
        return build_margin_settings_preview(self, owner)

    def _refresh_margins_controls(self, owner: Any | None = None) -> None:
        refresh_margins_controls(self, owner)

    def _sync_feedback_from_owner(self, owner: Any) -> None:
        sync_feedback_from_owner(self, owner)

    def _sync_non_preview_state_from_owner(self, owner: Any) -> None:
        self._sync_input_state_from_owner(owner)
        self._sync_main_state_from_owner(owner)
        self._sync_margins_state_from_owner(owner)
        self._sync_watch_state_from_owner(owner)
        self._sync_feedback_from_owner(owner)

    def _sync_preview_state_from_owner(self, owner: Any, *, include_input: bool = False, include_feedback: bool = False) -> None:
        if include_input:
            self._sync_input_state_from_owner(owner)
        self._sync_result_preview_from_owner(owner)
        if include_feedback:
            self._sync_feedback_from_owner(owner)

    def _sync_input_preview_state_from_owner(self, owner: Any, *, include_feedback: bool = False) -> None:
        self._sync_preview_state_from_owner(owner, include_input=True, include_feedback=include_feedback)

    def _sync_margins_state_with_feedback_from_owner(self, owner: Any) -> None:
        self._sync_margins_state_from_owner(owner)
        self._sync_feedback_from_owner(owner)

    def _sync_watch_state_with_feedback_from_owner(self, owner: Any) -> None:
        self._sync_watch_state_from_owner(owner)
        self._sync_feedback_from_owner(owner)

    def _sync_watch_state_only_from_owner(self, owner: Any) -> None:
        self._sync_watch_state_from_owner(owner)

    def _get_gdkpixbuf_module(self) -> Any | None:
        return get_gdkpixbuf_module(self)

    def _clear_preview_widget(self, object_name: str, message: str) -> None:
        clear_preview_widget(self, object_name, message)

    def _preview_target_size(self) -> tuple[int, int]:
        return preview_target_size(self)

    def _set_preview_widget(self, object_name: str, source_path: Path | None, *, crop_box: tuple[int, int, int, int] | None = None) -> None:
        set_preview_widget(self, object_name, source_path, crop_box=crop_box)

    def _build_preview_crop_boxes(
        self,
        source_path: Path,
        *,
        l_display: tuple[int, int] | None,
        r_display: tuple[int, int] | None,
    ) -> tuple[tuple[int, int, int, int], tuple[int, int, int, int]] | None:
        return build_preview_crop_boxes(source_path, l_display=l_display, r_display=r_display)

    def _sync_result_preview_from_owner(self, owner: Any) -> None:
        sync_result_preview_from_owner(self, owner)

    def _get_glib_module(self) -> Any | None:
        return get_glib_module(self)

    def _stop_watch_timer(self) -> None:
        stop_watch_timer(self)

    def _on_watch_timer_event(self) -> bool:
        return on_watch_timer_event(self)

    def _start_watch_timer(self, interval_seconds: int) -> bool:
        return start_watch_timer(self, interval_seconds)

    def _run_watch_cycle_for_side(self, side: str, source_dir: Path) -> str:
        return run_watch_cycle_for_side(self, side, source_dir)

    def _notify_srcdir_dialog_destroy(self) -> None:
        callback = self._signal_handlers.get("on_close_srcdir_dialog")
        if callback is None:
            return
        try:
            callback()
        except Exception:
            pass

    def _notify_save_path_dialog_destroy(self) -> None:
        callback = self._get_save_path_destroy_callback()
        if callback is None:
            return
        try:
            callback()
        except Exception:
            pass

    def _set_save_path_dialog_open_state(self, opened: bool, *, state_text: str | None = None) -> None:
        dialog = self._get_save_path_dialog()
        if dialog is not None:
            if opened and hasattr(dialog, "show"):
                dialog.show()
            if not opened and hasattr(dialog, "hide"):
                dialog.hide()

        if state_text is not None:
            self._set_save_path_state_text(state_text)

    def _on_save_path_filename_changed(self, filename: str) -> None:
        self._refresh_save_target_label(filename)
        if not self._is_save_path_dialog_open():
            return
        if str(filename or "").strip():
            self._set_save_path_state_text("Save path: ready")
        else:
            self._set_save_path_state_text("Save path: required")

    def _is_save_path_dialog_open(self) -> bool:
        dialog = self._get_save_path_dialog()
        if dialog is None or not hasattr(dialog, "is_visible"):
            return False
        return bool(dialog.is_visible())

    def _on_input_changed(self, entry: Any) -> None:
        callback = self._signal_handlers.get("on_change_input_text")
        text_l = self._input_path_l.strip()
        text_r = self._input_path_r.strip()

        entry_l = self._objects.get("entPathL")
        if not text_l and entry_l is not None and hasattr(entry_l, "get_text"):
            text_l = str(entry_l.get_text() or "").strip()

        entry_r = self._objects.get("entPathR")
        if not text_r and entry_r is not None and hasattr(entry_r, "get_text"):
            text_r = str(entry_r.get_text() or "").strip()

        input_values = [value for value in (text_l, text_r) if value]
        text = ",".join(input_values)
        has_input = bool(input_values)
        # Why: avoid invalid optimize/apply calls when the input field is empty.
        self._set_button_enabled("btnSave", has_input)
        self._set_button_enabled("btnOptimize", has_input)
        self._set_button_enabled("btnSetWall", False)
        if not has_input:
            self._set_save_path_dialog_open_state(False, state_text="Save path: reset")
        self._set_label_text("lblOptimizeResult", "Optimize result: not-run")
        self._set_label_text("lblApplyTarget", "Apply target: not-ready")

        if callback is None:
            return

        try:
            callback(text)
            owner = self._get_handler_owner("on_change_input_text")
            if owner is not None:
                self._sync_preview_state_from_owner(owner)
            self._set_feedback(phase="Input", state="updated")
        except Exception as exc:
            self._set_feedback(phase="Input", state="failed", error=str(exc))

    def _on_pick_input_clicked(self, side: str) -> None:
        value = self._input_path_l if side == "L" else self._input_path_r

        dialog = self._objects.get("ImgOpenDialog")
        if dialog is None or not hasattr(dialog, "open_for_side"):
            self._set_label_text("lblPickState", f"Open-{side}: handler-missing")
            self._set_feedback(
                phase=f"Open-{side}",
                state="handler-missing",
                error="open dialog not available",
            )
            return

        dialog.open_for_side(side, value)
        self._set_label_text("lblPickState", f"Open-{side}: dialog-open")
        self._set_feedback(phase=f"Open-{side}", state="dialog-open")

    def _notify_open_dialog_destroy(self) -> None:
        callback = self._signal_handlers.get("on_close_open_image_dialog")
        if callback is None:
            return
        try:
            callback()
        except Exception:
            pass

    def _on_open_dialog_confirmed(self) -> None:
        dialog = self._objects.get("ImgOpenDialog")
        if dialog is None:
            self._set_feedback(phase="Open", state="error", error="open dialog not available")
            return

        side = "L"
        if hasattr(dialog, "get_side"):
            side = str(dialog.get_side() or "L").upper()

        filename = ""
        if hasattr(dialog, "get_filename"):
            filename = str(dialog.get_filename() or "").strip()

        if not filename:
            self._set_label_text("lblPickState", f"Open-{side}: awaiting-selection")
            self._set_feedback(
                phase=f"Open-{side}",
                state="awaiting-selection",
                error="image selection required",
            )
            return

        callback = self._signal_handlers.get("on_pick_input")
        if callback is None:
            self._set_label_text("lblPickState", f"Open-{side}: handler-missing")
            self._set_feedback(
                phase=f"Open-{side}",
                state="handler-missing",
                error="handler not connected",
            )
            return

        try:
            callback(filename, side)
            owner = self._get_handler_owner("on_pick_input")
            if owner is not None:
                self._sync_input_preview_state_from_owner(owner)
            else:
                entry_name = "entPathL" if side == "L" else "entPathR"
                if side == "L":
                    self._input_path_l = filename
                else:
                    self._input_path_r = filename
                entry = self._objects.get(entry_name)
                if entry is not None and hasattr(entry, "set_text"):
                    entry.set_text(self._format_input_display(filename))
            if hasattr(dialog, "hide"):
                dialog.hide()
            self._set_label_text("lblPickState", f"Open-{side}: selected")
            self._set_feedback(phase=f"Open-{side}", state="selected")
            self._notify_open_dialog_destroy()
        except Exception as exc:
            self._set_label_text("lblPickState", f"Open-{side}: error")
            self._set_feedback(phase=f"Open-{side}", state="error", error=str(exc))

    def _on_open_dialog_canceled(self, destroyed: bool = False) -> None:
        dialog = self._objects.get("ImgOpenDialog")
        side = "L"
        if dialog is not None:
            if hasattr(dialog, "get_side"):
                side = str(dialog.get_side() or "L").upper()
            if hasattr(dialog, "hide"):
                dialog.hide()

        state = "closed" if destroyed else "canceled"
        self._set_label_text("lblPickState", f"Open-{side}: {state}")
        self._set_feedback(phase=f"Open-{side}", state=state)
        self._notify_open_dialog_destroy()

    def _format_input_display(self, path: str) -> str:
        value = str(path or "").strip()
        if not value:
            return ""
        try:
            name = Path(value).name or value
        except Exception:
            return value

        max_length = 36
        if len(name) <= max_length:
            return name

        tail_length = 12
        head_length = max_length - tail_length - 3
        if head_length < 8:
            head_length = 8
            tail_length = max(4, max_length - head_length - 3)
        return f"{name[:head_length]}...{name[-tail_length:]}"

    def _on_clear_input_clicked(self, side: str) -> None:
        callback = self._signal_handlers.get("on_clear_input")
        if callback is None:
            self._set_feedback(phase=f"Clear-{side}", state="handler-missing", error="handler not connected")
            return

        try:
            callback(side)
            owner = self._get_handler_owner("on_clear_input")
            if owner is not None:
                self._sync_input_preview_state_from_owner(owner, include_feedback=True)
            else:
                self._set_feedback(phase=f"Clear-{side}", state="ok")
        except TypeError:
            try:
                callback()
                owner = self._get_handler_owner("on_clear_input")
                if owner is not None:
                    self._sync_input_preview_state_from_owner(owner, include_feedback=True)
                else:
                    self._set_feedback(phase=f"Clear-{side}", state="ok")
            except Exception as exc:
                self._set_feedback(phase=f"Clear-{side}", state="failed", error=str(exc))
        except Exception as exc:
            self._set_feedback(phase=f"Clear-{side}", state="failed", error=str(exc))

    def _current_srcdir_for_side(self, side: str) -> str:
        return self._watch_srcdir_l if side == "L" else self._watch_srcdir_r

    def _on_pick_srcdir_clicked(self, side: str) -> None:
        dialog = self._objects.get("SrcdirDialog")
        if dialog is None or not hasattr(dialog, "open_for_side"):
            self._set_feedback(
                phase=f"Srcdir-{side}",
                state="handler-missing",
                error="srcdir dialog not available",
            )
            return

        dialog.open_for_side(side, self._current_srcdir_for_side(side))
        self._set_feedback(phase=f"Srcdir-{side}", state="dialog-open")

    def _on_srcdir_dialog_confirmed(self) -> None:
        dialog = self._objects.get("SrcdirDialog")
        if dialog is None:
            self._set_feedback(phase="Srcdir", state="error", error="srcdir dialog not available")
            return

        side = "L"
        if hasattr(dialog, "get_side"):
            side = str(dialog.get_side() or "L").upper()

        folder = ""
        if hasattr(dialog, "get_current_folder"):
            folder = str(dialog.get_current_folder() or "").strip()

        if not folder:
            self._set_feedback(
                phase=f"Srcdir-{side}",
                state="awaiting-selection",
                error="source directory is required",
            )
            return

        callback = self._signal_handlers.get("on_pick_watch_srcdir")
        if callback is None:
            self._set_feedback(
                phase=f"Srcdir-{side}",
                state="handler-missing",
                error="handler not connected",
            )
            return

        try:
            ok = callback(folder, side)
            if not ok:
                self._set_feedback(
                    phase=f"Srcdir-{side}",
                    state="select-failed",
                    error="srcdir selection returned false",
                )
                return

            if side == "L":
                self._watch_srcdir_l = folder
            else:
                self._watch_srcdir_r = folder
            self._refresh_watch_source_labels()
            if hasattr(dialog, "hide"):
                dialog.hide()
            self._set_feedback(phase=f"Srcdir-{side}", state="selected")
            self._notify_srcdir_dialog_destroy()
        except Exception as exc:
            self._set_feedback(phase=f"Srcdir-{side}", state="error", error=str(exc))

    def _on_srcdir_dialog_canceled(self, destroyed: bool = False) -> None:
        dialog = self._objects.get("SrcdirDialog")
        side = "L"
        if dialog is not None:
            if hasattr(dialog, "get_side"):
                side = str(dialog.get_side() or "L").upper()
            if hasattr(dialog, "hide"):
                dialog.hide()
        state = "closed" if destroyed else "canceled"
        self._set_feedback(phase=f"Srcdir-{side}", state=state)
        self._notify_srcdir_dialog_destroy()

    def _on_watch_interval_changed(self, widget: Any) -> None:
        callback = self._signal_handlers.get("on_watch_interval_change")
        if callback is None:
            self._set_feedback(phase="Watch", state="handler-missing", error="handler not connected")
            return
        try:
            interval = 0
            if hasattr(widget, "get_value_as_int"):
                interval = int(widget.get_value_as_int())
            elif hasattr(widget, "get_value"):
                interval = int(widget.get_value())

            owner = self._get_handler_owner("on_watch_interval_change")
            if owner is not None:
                ok = callback(interval)
            else:
                ok = callback(widget)

            if ok:
                self._set_feedback(phase="Watch", state=f"interval-updated({interval}s)")
            else:
                self._set_feedback(phase="Watch", state="interval-failed", error="interval returned false")
        except Exception as exc:
            self._set_feedback(phase="Watch", state="error", error=str(exc))

    def _on_watch_start_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_watch_start")
        if callback is None:
            self._set_feedback(phase="Watch", state="handler-missing", error="handler not connected")
            return
        try:
            owner = self._get_handler_owner("on_watch_start")
            ok = callback()
            if not ok:
                if owner is not None:
                    self._sync_watch_state_with_feedback_from_owner(owner)
                else:
                    self._set_feedback(phase="Watch", state="start-failed", error="watch start returned false")
                return

            if owner is not None:
                self._sync_watch_state_only_from_owner(owner)
                interval_seconds = int(getattr(owner, "watch_interval_seconds", 0) or 0)
                self._start_watch_timer(interval_seconds)
                self._set_feedback(phase="Watch", state="started")
                return

            selected_left = "-"
            selected_right = "-"
            if self._watch_srcdir_l:
                selected_left = self._run_watch_cycle_for_side("L", Path(self._watch_srcdir_l))
            if self._watch_srcdir_r:
                selected_right = self._run_watch_cycle_for_side("R", Path(self._watch_srcdir_r))

            self._watch_running = True
            self._refresh_watch_summary_label()
            self._refresh_watch_source_labels()
            self._refresh_watch_current_label(selected_left, selected_right)
            interval_widget = self._objects.get("spnInterval")
            interval_seconds = 0
            if interval_widget is not None and hasattr(interval_widget, "get_value_as_int"):
                interval_seconds = int(interval_widget.get_value_as_int())
            self._start_watch_timer(interval_seconds)
            self._set_feedback(phase="Watch", state="started")
        except Exception as exc:
            self._set_feedback(phase="Watch", state="error", error=str(exc))

    def _on_watch_stop_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_watch_stop")
        if callback is None:
            self._set_feedback(phase="Watch", state="handler-missing", error="handler not connected")
            return
        try:
            ok = callback()
            if not ok:
                self._set_feedback(phase="Watch", state="stop-ignored")
                return

            owner = self._get_handler_owner("on_watch_stop")
            if owner is not None:
                self._stop_watch_timer()
                self._sync_watch_state_only_from_owner(owner)
                self._set_feedback(phase="Watch", state="stopped")
                return

            self._watch_running = False
            self._stop_watch_timer()
            self._refresh_watch_summary_label()
            self._refresh_watch_current_label()
            self._set_feedback(phase="Watch", state="stopped")
        except Exception as exc:
            self._set_feedback(phase="Watch", state="error", error=str(exc))

    def _on_margin_text_mode_toggled(self, widget: Any, value: str) -> None:
        if hasattr(widget, "get_active") and not widget.get_active():
            return
        callback = self._signal_handlers.get("on_change_margin_text_mode")
        if callback is None:
            self._set_feedback(phase="Margins", state="planned")
            return
        try:
            ok = callback(value)
            if ok is False:
                self._set_feedback(phase="Margins", state="info-rejected", error="margin text mode update rejected")
                return
            owner = self._get_handler_owner("on_change_margin_text_mode")
            if owner is not None:
                self._sync_margins_state_with_feedback_from_owner(owner)
                return
            self._set_feedback(phase="Margins", state="info-updated")
        except Exception as exc:
            self._set_feedback(phase="Margins", state="info-error", error=str(exc))

    def _on_margin_text_changed(self, entry: Any) -> None:
        callback = self._signal_handlers.get("on_change_margin_text")
        if callback is None:
            return
        try:
            if hasattr(entry, "get_text"):
                value = str(entry.get_text() or "")
            elif hasattr(entry, "get_buffer"):
                buffer = entry.get_buffer()
                if hasattr(buffer, "get_bounds"):
                    start, end = buffer.get_bounds()
                else:
                    start = buffer.get_start_iter() if hasattr(buffer, "get_start_iter") else None
                    end = buffer.get_end_iter() if hasattr(buffer, "get_end_iter") else None
                value = str(buffer.get_text(start, end, True) or "")
            else:
                value = ""
            value = self._sanitize_margin_text(value)
            ok = callback(value)
            if ok is False:
                self._set_feedback(phase="Margins", state="text-rejected", error="margin text update rejected")
                return
            owner = self._get_handler_owner("on_change_margin_text")
            if owner is not None:
                self._sync_margins_state_with_feedback_from_owner(owner)
                return
            self._set_feedback(phase="Margins", state="text-updated")
        except Exception as exc:
            self._set_feedback(phase="Margins", state="text-error", error=str(exc))

    def _on_margin_position_toggled(self, widget: Any, value: str) -> None:
        if hasattr(widget, "get_active") and not widget.get_active():
            return
        callback = self._signal_handlers.get("on_change_margin_text_position")
        if callback is None:
            return
        try:
            ok = callback(value)
            if ok is False:
                self._set_feedback(phase="Margins", state="position-rejected", error="margin area update rejected")
                return
            owner = self._get_handler_owner("on_change_margin_text_position")
            if owner is not None:
                self._sync_margins_state_with_feedback_from_owner(owner)
                return
            self._set_feedback(phase="Margins", state="position-updated")
        except Exception as exc:
            self._set_feedback(phase="Margins", state="position-error", error=str(exc))

    def _on_margin_text_max_lines_changed(self, spin: Any) -> None:
        callback = self._signal_handlers.get("on_change_margin_text_max_lines")
        if callback is None:
            return
        try:
            value = int(spin.get_value_as_int()) if hasattr(spin, "get_value_as_int") else int(spin.get_value())
            ok = callback(value)
            if ok is False:
                self._set_feedback(phase="Margins", state="max-lines-rejected", error="margin text line limit update rejected")
                return
            owner = self._get_handler_owner("on_change_margin_text_max_lines")
            if owner is not None:
                self._sync_margins_state_with_feedback_from_owner(owner)
                return
            self._set_feedback(phase="Margins", state="max-lines-updated")
        except Exception as exc:
            self._set_feedback(phase="Margins", state="max-lines-error", error=str(exc))

    def run_watch_cycle_once(self) -> bool:
        return run_runtime_watch_cycle_once(self)

    def _set_toggle_active(self, object_name: str, active: bool) -> None:
        toggle = self._objects.get(object_name)
        if toggle is None:
            return
        if hasattr(toggle, "set_active"):
            toggle.set_active(bool(active))
            return
        setattr(toggle, "active", bool(active))

    def _set_preferences_two_screen_mode(self, value: object) -> None:
        raw = str(value).strip().lower() if value is not None else "off"
        is_auto = raw == "auto"
        is_on = raw in {"on", "true", "1"} or value is True
        self._set_toggle_active("radSettingsTwoScreenAuto", is_auto)
        self._set_toggle_active("radSettingsTwoScreenOn", is_on and not is_auto)
        self._set_toggle_active("radSettingsTwoScreenOff", not is_auto and not is_on)

    def _read_preferences_two_screen_mode(self) -> str | bool:
        if self._is_toggle_active("radSettingsTwoScreenAuto"):
            return "auto"
        if self._is_toggle_active("radSettingsTwoScreenOn"):
            return True
        return False

    def _set_preferences_apply_mode(self, value: object | None) -> None:
        mode = str(value or "single-file").strip().lower()
        self._prefs_apply_mode_syncing = True
        try:
            if mode == "per-monitor-auto-split":
                self._prefs_apply_mode_preserved = None
                self._set_toggle_active("radSettingsApplySingle", False)
                self._set_toggle_active("radSettingsApplyPerMonitor", True)
                return
            if mode == "single-file":
                self._prefs_apply_mode_preserved = None
                self._set_toggle_active("radSettingsApplySingle", True)
                self._set_toggle_active("radSettingsApplyPerMonitor", False)
                return

            # Preserve unsupported modes such as per-monitor-explicit without
            # surfacing them as editable GUI choices.
            self._prefs_apply_mode_preserved = mode
            self._set_toggle_active("radSettingsApplySingle", False)
            self._set_toggle_active("radSettingsApplyPerMonitor", False)
        finally:
            self._prefs_apply_mode_syncing = False

    def _read_preferences_apply_mode(self) -> str:
        if self._is_toggle_active("radSettingsApplyPerMonitor"):
            return "per-monitor-auto-split"
        if self._is_toggle_active("radSettingsApplySingle"):
            return "single-file"
        if self._prefs_apply_mode_preserved:
            return self._prefs_apply_mode_preserved
        return "single-file"

    def _on_preferences_apply_mode_toggled(self, widget: Any, mode: str) -> None:
        if self._prefs_apply_mode_syncing:
            return
        is_active = True
        if hasattr(widget, "get_active"):
            is_active = bool(widget.get_active())
        if not is_active:
            return
        self._prefs_apply_mode_preserved = None

    def _sync_preferences_widgets_from_dialog(self) -> dict[str, object]:
        dialog = self._objects.get("SettingsDialog")
        if dialog is None or not hasattr(dialog, "get_preferences_config"):
            return {}
        config = dict(dialog.get_preferences_config())
        self._set_entry_text("entSettingsResolution", config.get("resolution", "1920x1080"))
        self._set_entry_text("entSettingsScaling", config.get("scaling", "fit"))
        self._set_preferences_two_screen_mode(config.get("two_screen", False))
        self._set_entry_text("entSettingsLDisplay", config.get("l_display"))
        self._set_entry_text("entSettingsRDisplay", config.get("r_display"))
        self._set_entry_text("entSettingsMargins", config.get("margins"))
        self._set_entry_text("entSettingsAlign", format_position_pair(config.get("align", "center"), axis="align"))
        self._set_entry_text("entSettingsValign", format_position_pair(config.get("valign", "center"), axis="valign"))
        self._set_spin_value("spnSettingsQuality", int(config.get("quality", 90)))
        self._set_entry_text("entSettingsMarginTextMode", config.get("embed_info", "none"))
        self._set_entry_text("entSettingsMarginText", config.get("embed_text"))
        self._set_entry_text("entSettingsMarginTextPosition", config.get("embed_position", "auto"))
        self._set_spin_value("spnSettingsMarginTextMaxLines", int(config.get("embed_max_lines", 3)))
        self._set_entry_text("entSettingsPlugin", config.get("plugin", "windows"))
        self._set_preferences_apply_mode(config.get("apply_mode", "single-file"))
        if hasattr(dialog, "get_import_path"):
            self._set_entry_text("entSettingsImportPath", dialog.get_import_path())
        if hasattr(dialog, "get_export_path"):
            self._set_entry_text("entSettingsExportPath", dialog.get_export_path())
        return config

    def _sync_preferences_dialog_from_widgets(self) -> dict[str, object]:
        dialog = self._objects.get("SettingsDialog")
        config: dict[str, object] = {}
        if dialog is not None and hasattr(dialog, "get_preferences_config"):
            config = dict(dialog.get_preferences_config())

        def _empty_to_none(value: str) -> str | None:
            return value if value else None

        config.update(
            {
                "resolution": self._read_entry_text("entSettingsResolution") or "1920x1080",
                "scaling": self._read_entry_text("entSettingsScaling") or "fit",
                "two_screen": self._read_preferences_two_screen_mode(),
                "l_display": _empty_to_none(self._read_entry_text("entSettingsLDisplay")),
                "r_display": _empty_to_none(self._read_entry_text("entSettingsRDisplay")),
                "margins": _empty_to_none(self._read_entry_text("entSettingsMargins")),
                "align": list(parse_position_pair(self._read_entry_text("entSettingsAlign") or "center", axis="align")),
                "valign": list(parse_position_pair(self._read_entry_text("entSettingsValign") or "center", axis="valign")),
                "quality": self._read_spin_int("spnSettingsQuality"),
                "embed_info": self._read_entry_text("entSettingsMarginTextMode") or "none",
                "embed_text": _empty_to_none(self._read_entry_text("entSettingsMarginText")),
                "embed_position": self._read_entry_text("entSettingsMarginTextPosition") or "auto",
                "embed_max_lines": self._read_spin_int("spnSettingsMarginTextMaxLines"),
                "plugin": self._read_entry_text("entSettingsPlugin") or "windows",
                "apply_mode": self._read_preferences_apply_mode(),
            }
        )

        import_path = self._read_entry_text("entSettingsImportPath")
        export_path = self._read_entry_text("entSettingsExportPath")
        if dialog is not None:
            if hasattr(dialog, "set_preferences_config"):
                dialog.set_preferences_config(config)
            if hasattr(dialog, "set_import_path"):
                dialog.set_import_path(import_path)
            if hasattr(dialog, "set_export_path"):
                dialog.set_export_path(export_path)
        return config

    def _refresh_preferences_dialog_config_from_getter(self) -> None:
        dialog = self._objects.get("SettingsDialog")
        getter = self._signal_handlers.get("on_get_settings_config")
        if getter is None or dialog is None or not hasattr(dialog, "set_preferences_config"):
            return

        current_config: dict[str, object] = {}
        if hasattr(dialog, "get_preferences_config"):
            current_config = dict(dialog.get_preferences_config())

        refreshed = dict(current_config)
        refreshed.update(dict(getter()))
        dialog.set_preferences_config(refreshed)

    def _refresh_color_dialog_from_getter(self) -> str:
        getter = self._signal_handlers.get("on_get_settings_config")
        dialog = self._objects.get("ColorDialog")
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

    def _refresh_about_dialog_from_getter(self) -> dict[str, object]:
        getter = self._signal_handlers.get("on_get_about_dialog_info")
        dialog = self._objects.get("AboutDialog")
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

    def _store_background_color_in_settings_dialog(self, color: str) -> None:
        dialog = self._objects.get("SettingsDialog")
        if dialog is None or not hasattr(dialog, "get_preferences_config") or not hasattr(dialog, "set_preferences_config"):
            return
        config = dict(dialog.get_preferences_config())
        config["background_color"] = normalize_background_color(color)
        dialog.set_preferences_config(config)

    def _is_toggle_active(self, object_name: str) -> bool:
        toggle = self._objects.get(object_name)
        if toggle is None:
            return False
        if hasattr(toggle, "get_active"):
            return bool(toggle.get_active())
        return bool(getattr(toggle, "active", False))

    def _current_side_state(self, side: str) -> tuple[str, str]:
        align = "center"
        valign = "center"

        if self._is_toggle_active(f"tglPushLeft{side}"):
            align = "left"
        elif self._is_toggle_active(f"tglPushRight{side}"):
            align = "right"

        if self._is_toggle_active(f"tglUpper{side}"):
            valign = "top"
        elif self._is_toggle_active(f"tglLower{side}"):
            valign = "bottom"

        return align, valign

    def _refresh_current_state_labels(self) -> None:
        left = self._read_spin_int("spnLeftMargin")
        right = self._read_spin_int("spnRightMargin")
        top = self._read_spin_int("spnTopMargin")
        bottom = self._read_spin_int("spnBottomMargin")
        align_l, valign_l = self._current_side_state("L")
        align_r, valign_r = self._current_side_state("R")

        self._set_label_text("lblCurrentMargins", f"margins={left},{right},{top},{bottom}")
        self._set_label_text("lblCurrentStateL", f"L: align={align_l} valign={valign_l}")
        self._set_label_text("lblCurrentStateR", f"R: align={align_r} valign={valign_r}")
        current_state_summary_display = getattr(self, "_current_state_summary_display", None)
        if current_state_summary_display is not None and hasattr(current_state_summary_display, "set_text"):
            current_state_summary_display.set_text(f"align={align_l},{align_r}/{valign_l},{valign_r}")
        self._set_label_text("lblMarginSettingsPreview", self._build_margin_settings_preview())

    def _opposite_toggle_name(self, object_name: str) -> str | None:
        opposites = {
            "tglPushLeftL": "tglPushRightL",
            "tglPushRightL": "tglPushLeftL",
            "tglUpperL": "tglLowerL",
            "tglLowerL": "tglUpperL",
            "tglPushLeftR": "tglPushRightR",
            "tglPushRightR": "tglPushLeftR",
            "tglUpperR": "tglLowerR",
            "tglLowerR": "tglUpperR",
        }
        return opposites.get(object_name)

    def _on_direction_pressed(self, object_name: str) -> None:
        opposite_name = self._opposite_toggle_name(object_name)
        if opposite_name is not None:
            opposite_toggle = self._objects.get(opposite_name)
            if opposite_toggle is not None and hasattr(opposite_toggle, "get_active"):
                if bool(opposite_toggle.get_active()):
                    self._set_toggle_active(opposite_name, False)
                    reset_callback = self._signal_handlers.get("on_toggle_position_reset")
                    if reset_callback is not None:
                        try:
                            reset_callback(opposite_name)
                        except Exception:
                            pass
        self._refresh_current_state_labels()

        callback = self._signal_handlers.get("on_toggle_position_pressed")
        if callback is not None:
            try:
                callback(object_name)
            except Exception:
                pass

    def _on_direction_toggled(self, object_name: str) -> None:
        self._refresh_current_state_labels()
        callback = self._signal_handlers.get("on_toggle_position")
        active = self._is_toggle_active(object_name)
        if callback is not None:
            try:
                callback(object_name, active)
            except Exception:
                pass

        if not active:
            reset_callback = self._signal_handlers.get("on_toggle_position_reset")
            if reset_callback is not None:
                try:
                    reset_callback(object_name)
                except Exception:
                    pass

    def _on_direction_released(self, object_name: str) -> None:
        self._refresh_current_state_labels()
        return

    def _read_spin_int(self, object_name: str) -> int:
        spin = self._objects.get(object_name)
        if spin is None:
            return 0
        if hasattr(spin, "get_value_as_int"):
            return int(spin.get_value_as_int())
        if hasattr(spin, "get_value"):
            return int(spin.get_value())
        return 0

    def _on_margin_changed(self, widget: Any) -> None:
        self._refresh_current_state_labels()
        callback = self._signal_handlers.get("on_change_margins")

        if callback is None:
            self._set_feedback(phase="Margins", state="planned")
            return

        try:
            widget_name = widget.get_name() if hasattr(widget, "get_name") else ""
            value = 0
            if hasattr(widget, "get_value_as_int"):
                value = int(widget.get_value_as_int())
            elif hasattr(widget, "get_value"):
                value = int(widget.get_value())
            callback(widget_name, value)
            self._set_feedback(phase="Margins", state="updated")
        except Exception as exc:
            self._set_feedback(phase="Margins", state="error", error=str(exc))

    def _run_optimize_path(self, callback: Callable[..., Any] | None) -> None:
        if callback is None:
            self._set_feedback(
                phase="Optimize",
                state="handler-missing",
                error="handler not connected",
            )
            self._set_button_enabled("btnSetWall", False)
            self._set_label_text("lblOptimizeResult", "Optimize result: handler-missing")
            self._set_label_text("lblApplyTarget", "Apply target: not-ready")
            return
        try:
            self._set_feedback(phase="Optimize", state="running")
            ok = callback()
            self._set_button_enabled("btnSetWall", bool(ok))
            owner = self._get_handler_owner("on_optimize")
            if ok:
                if owner is not None:
                    self._sync_preview_state_from_owner(owner)
                self._set_feedback(phase="Optimize", state="ok")
                self._set_label_text("lblOptimizeResult", "Optimize result: success")
                self._set_label_text("lblApplyTarget", "Apply target: ready")
            else:
                if owner is not None:
                    self._sync_preview_state_from_owner(owner)
                self._set_feedback(
                    phase="Optimize",
                    state="failed",
                    error="optimize returned false",
                )
                self._set_label_text("lblOptimizeResult", "Optimize result: failed")
                self._set_label_text("lblApplyTarget", "Apply target: not-ready")
        except Exception as exc:
            self._set_button_enabled("btnSetWall", False)
            self._set_feedback(phase="Optimize", state="error", error=str(exc))
            self._set_label_text("lblOptimizeResult", "Optimize result: error")
            self._set_label_text("lblApplyTarget", "Apply target: not-ready")

    def _on_apply_mode_toggled(self, widget: Any, mode: str) -> None:
        is_active = True
        if hasattr(widget, "get_active"):
            is_active = bool(widget.get_active())
        label = "Apply the optimized image as a single file."
        if mode == "per-monitor-auto-split" and is_active:
            label = "Split the optimized image and apply per display."
        self._set_label_text("lblApplyMode", label)

        if not is_active:
            return

        callback = self._signal_handlers.get("on_change_apply_mode")
        if callback is None:
            return
        try:
            callback(mode)
            owner = self._get_handler_owner("on_change_apply_mode")
            if owner is not None:
                self._sync_preview_state_from_owner(owner)
            self._set_feedback(phase="ApplyMode", state="updated")
        except Exception as exc:
            self._set_feedback(phase="ApplyMode", state="error", error=str(exc))

    def _on_save_clicked(self, *_args: Any) -> None:
        # P6 direction: Save As keeps chooser semantics, but fallback should not
        # depend on separate confirm/cancel controls.
        callback = self._signal_handlers.get("on_save_as")
        if callback is not None:
            try:
                callback()
            except Exception:
                pass

        self._refresh_save_target_label()

        dialog = self._get_save_path_dialog()
        if dialog is not None and hasattr(dialog, "supports_native_dialog") and dialog.supports_native_dialog():
            if hasattr(dialog, "open_dialog"):
                dialog.open_dialog()
            return

        fallback_filename = self._current_save_path_filename()
        if not fallback_filename:
            fallback_filename = str(Path.home() / "harite-output.jpg")
        if dialog is not None and hasattr(dialog, "set_filename"):
            dialog.set_filename(fallback_filename)
        self._handle_save_path_confirm(fallback_filename)

    def _on_optimize_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_optimize")
        self._run_optimize_path(callback)

    def _on_apply_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_apply")
        if callback is None:
            self._set_feedback(
                phase="Apply",
                state="handler-missing",
                error="handler not connected",
            )
            self._set_label_text("lblApplyTarget", "Apply target: handler-missing")
            return
        try:
            self._set_feedback(phase="Apply", state="running")
            ok = callback()
            if ok:
                self._set_feedback(phase="Apply", state="ok")
                self._set_label_text("lblApplyTarget", "Apply target: last applied")
            else:
                self._set_feedback(
                    phase="Apply",
                    state="failed",
                    error="apply returned false",
                )
        except Exception as exc:
            self._set_feedback(phase="Apply", state="error", error=str(exc))

    def _on_settings_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_open_settings_dialog")
        dialog = self._objects.get("SettingsDialog")
        if callback is None:
            self._set_feedback(phase="Settings", state="planned")
            return
        try:
            ok = callback()
            if ok:
                self._refresh_preferences_dialog_config_from_getter()
                self._sync_preferences_widgets_from_dialog()
                owner = self._get_handler_owner("on_open_settings_dialog")
                if owner is not None:
                    self._sync_watch_state_only_from_owner(owner)
                if dialog is not None and hasattr(dialog, "show"):
                    dialog.show()
                self._set_label_text("lblSettingsState", "Settings: opened")
                self._set_feedback(phase="Settings", state="opened")
            else:
                self._set_feedback(phase="Settings", state="deferred")
        except Exception as exc:
            self._set_feedback(phase="Settings", state="error", error=str(exc))

    def _on_preferences_apply_clicked(self, *_args: Any) -> None:
        handler_name = "on_apply_settings"
        callback = self._signal_handlers.get(handler_name)
        dialog = self._objects.get("SettingsDialog")
        if callback is None or dialog is None or not hasattr(dialog, "get_preferences_config"):
            self._set_feedback(phase="SettingsApply", state="handler-missing", error="handler not connected")
            return
        try:
            ok = callback(self._sync_preferences_dialog_from_widgets())
            if ok:
                owner = self._get_handler_owner(handler_name)
                if owner is not None:
                    self._sync_non_preview_state_from_owner(owner)
                if hasattr(dialog, "hide"):
                    dialog.hide()
                self._set_label_text("lblSettingsState", "Settings: applied")
                self._set_feedback(phase="SettingsApply", state="applied")
            else:
                self._set_feedback(phase="SettingsApply", state="failed", error="settings apply returned false")
        except Exception as exc:
            self._set_feedback(phase="SettingsApply", state="error", error=str(exc))

    def _on_preferences_load_clicked(self, *_args: Any) -> None:
        handler_name = "on_load_settings_file"
        callback = self._signal_handlers.get(handler_name)
        dialog = self._objects.get("SettingsDialog")
        if callback is None or dialog is None or not hasattr(dialog, "get_import_path"):
            self._set_feedback(phase="SettingsLoad", state="handler-missing", error="handler not connected")
            return
        try:
            self._sync_preferences_dialog_from_widgets()
            ok = callback(dialog.get_import_path())
            if ok:
                self._refresh_preferences_dialog_config_from_getter()
                self._sync_preferences_widgets_from_dialog()
                owner = self._get_handler_owner(handler_name)
                if owner is not None:
                    self._sync_non_preview_state_from_owner(owner)
                self._set_label_text("lblSettingsState", "Settings: loaded")
                self._set_feedback(phase="SettingsLoad", state="loaded")
            else:
                self._set_feedback(phase="SettingsLoad", state="failed", error="settings load returned false")
        except Exception as exc:
            self._set_feedback(phase="SettingsLoad", state="error", error=str(exc))

    def _on_preferences_save_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_save_settings_file")
        dialog = self._objects.get("SettingsDialog")
        if callback is None or dialog is None or not hasattr(dialog, "get_export_path"):
            self._set_feedback(phase="SettingsSave", state="handler-missing", error="handler not connected")
            return
        try:
            config = self._sync_preferences_dialog_from_widgets()
            try:
                ok = callback(dialog.get_export_path(), config)
            except TypeError:
                ok = callback(dialog.get_export_path())
            if ok:
                self._set_label_text("lblSettingsState", "Settings: saved")
                self._set_feedback(phase="SettingsSave", state="saved")
            else:
                self._set_feedback(phase="SettingsSave", state="failed", error="settings save returned false")
        except Exception as exc:
            self._set_feedback(phase="SettingsSave", state="error", error=str(exc))

    def _on_preferences_close_clicked(self, *_args: Any) -> None:
        dialog = self._objects.get("SettingsDialog")
        if dialog is not None and hasattr(dialog, "hide"):
            dialog.hide()
        callback = self._signal_handlers.get("on_close_settings_dialog")
        if callback is not None:
            try:
                callback()
            except Exception:
                pass
        self._set_label_text("lblSettingsState", "Settings: closed")
        self._set_feedback(phase="Settings", state="closed")

    def _on_preferences_window_delete_event(self) -> bool:
        self._on_preferences_close_clicked()
        return True

    def _on_color_clicked(self, *_args: Any) -> None:
        dialog = self._objects.get("ColorDialog")
        callback = self._signal_handlers.get("on_set_color")
        if dialog is None or not hasattr(dialog, "open_dialog"):
            self._set_feedback(phase="Color", state="handler-missing", error="color dialog not available")
            return
        try:
            self._refresh_color_dialog_from_getter()
            if callback is not None:
                callback()
            dialog.open_dialog()
            self._set_feedback(phase="Color", state="opened")
        except Exception as exc:
            self._set_feedback(phase="Color", state="error", error=str(exc))

    def _on_about_clicked(self, *_args: Any) -> None:
        dialog = self._objects.get("AboutDialog")
        callback = self._signal_handlers.get("on_about")
        if dialog is None or not hasattr(dialog, "show"):
            self._set_feedback(phase="About", state="handler-missing", error="about dialog not available")
            return
        try:
            self._refresh_about_dialog_from_getter()
            ok = True if callback is None else bool(callback())
            if not ok:
                self._set_feedback(phase="About", state="failed", error="about dialog open rejected")
                return
            dialog.show()
            self._set_feedback(phase="About", state="opened")
        except Exception as exc:
            self._set_feedback(phase="About", state="error", error=str(exc))

    def _on_about_dialog_close_clicked(self, *_args: Any) -> None:
        self._close_about_dialog(False)

    def _on_about_window_delete_event(self) -> bool:
        self._close_about_dialog(True)
        return True

    def _close_about_dialog(self, destroyed: bool) -> None:
        dialog = self._objects.get("AboutDialog")
        if dialog is not None and hasattr(dialog, "hide"):
            dialog.hide()
        callback = self._signal_handlers.get("on_close_about_dialog")
        if callback is not None:
            try:
                callback()
            except Exception:
                pass
        self._set_feedback(phase="About", state="closed" if destroyed else "closed")

    def _on_color_dialog_apply_clicked(self, *_args: Any) -> None:
        dialog = self._objects.get("ColorDialog")
        callback = self._signal_handlers.get("on_set_color")
        if dialog is None or not hasattr(dialog, "get_color"):
            self._set_feedback(phase="Color", state="handler-missing", error="color dialog not available")
            return
        if callback is None:
            self._set_feedback(phase="Color", state="handler-missing", error="handler not connected")
            return
        try:
            color = dialog.get_color()
            ok = callback(color)
            if ok:
                self._store_background_color_in_settings_dialog(color)
                if hasattr(dialog, "hide"):
                    dialog.hide()
                self._set_label_text("lblColorState", f"Color: {color}")
                self._set_feedback(phase="Color", state="updated")
            else:
                self._set_feedback(phase="Color", state="failed", error="color update returned false")
        except Exception as exc:
            self._set_feedback(phase="Color", state="error", error=str(exc))

    def _on_color_dialog_cancel_clicked(self, *_args: Any) -> None:
        self._on_color_dialog_canceled(False)

    def _on_color_window_delete_event(self) -> bool:
        self._on_color_dialog_canceled(True)
        return True

    def _on_color_dialog_confirmed(self, color: str) -> None:
        callback = self._signal_handlers.get("on_set_color")
        if callback is None:
            self._set_feedback(phase="Color", state="handler-missing", error="handler not connected")
            return
        try:
            ok = callback(color)
            if ok:
                self._store_background_color_in_settings_dialog(color)
                dialog = self._objects.get("ColorDialog")
                if dialog is not None and hasattr(dialog, "hide"):
                    dialog.hide()
                self._set_label_text("lblColorState", f"Color: {color}")
                self._set_feedback(phase="Color", state="updated")
            else:
                self._set_feedback(phase="Color", state="failed", error="color update returned false")
        except Exception as exc:
            self._set_feedback(phase="Color", state="error", error=str(exc))

    def _on_color_dialog_canceled(self, destroyed: bool) -> None:
        dialog = self._objects.get("ColorDialog")
        if dialog is not None and hasattr(dialog, "hide"):
            dialog.hide()
        callback = self._signal_handlers.get("on_close_color_dialog")
        if callback is not None:
            try:
                callback()
            except Exception:
                pass
        self._set_label_text("lblColorState", "Color: canceled")
        self._set_feedback(phase="Color", state="closed" if destroyed else "canceled")

    def _handle_save_path_confirm(self, filename: str) -> None:
        callback = self._signal_handlers.get("on_save_path_selected")
        if callback is None:
            self._set_feedback(phase="SavePath", state="handler-missing", error="handler not connected")
            return
        try:
            if not filename:
                self._set_save_path_state_text("Save path: required")
                self._set_feedback(phase="SavePath", state="path-required", error="save path is required")
                return
            self._refresh_save_target_label(filename)
            ok = callback(filename)
            if ok:
                self._set_save_path_dialog_open_state(False, state_text="Save path: saved")
                self._set_feedback(phase="SavePath", state="saved")
                self._notify_save_path_dialog_destroy()
            else:
                self._set_feedback(phase="SavePath", state="failed", error="save path acceptance returned false")
        except Exception as exc:
            self._set_feedback(phase="SavePath", state="error", error=str(exc))

    def _handle_save_path_cancel(self) -> None:
        callback = self._signal_handlers.get("on_save_path_selection_canceled")
        if callback is not None:
            try:
                callback()
            except Exception as exc:
                self._set_feedback(phase="SavePath", state="error", error=str(exc))
                return
        self._set_save_path_dialog_open_state(False, state_text="Save path: canceled")
        self._set_feedback(phase="SavePath", state="canceled")
        self._notify_save_path_dialog_destroy()

    def _on_native_save_path_confirmed(self) -> None:
        self._handle_save_path_confirm(self._current_save_path_filename())

    def _on_native_save_path_canceled(self) -> None:
        self._handle_save_path_cancel()


def load_gtk_builder_signal_backend(ui_file: Path | None = None):
    """Return a GTK Builder object that supports `connect_signals(mapping)`.

    When the UI file is incompatible with Gtk.Builder, a minimal runtime
    backend is returned so present/bind flows can continue without runtime
    Glade dependency.
    """
    try:
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
    except Exception as exc:  # pragma: no cover - depends on host GTK runtime.
        raise RuntimeError(f"GTK backend unavailable: {exc}") from exc

    if ui_file is None:
        return GtkRuntimeSignalBackend(Gtk)

    builder = Gtk.Builder()
    try:
        builder.add_from_file(str(ui_file))
    except Exception as exc:  # pragma: no cover - requires GTK runtime.
        # Why: legacy resources may use old Glade schema (<glade-interface>).
        # Keep runtime path alive by falling back to a minimal GTK window backend.
        return GtkRuntimeSignalBackend(Gtk)

    return builder


def _resolve_window(signal_backend, requested_id: str):
    window = signal_backend.get_object(requested_id)
    if window is not None:
        return window

    # Fallback IDs that may appear in legacy GTK/Glade exports.
    for candidate in ("main_window",):
        window = signal_backend.get_object(candidate)
        if window is not None:
            return window

    # Last fallback: first top-level GTK Window-like object.
    if hasattr(signal_backend, "get_objects"):
        for obj in signal_backend.get_objects():
            if obj.__class__.__name__.endswith("Window"):
                return obj
    return None


def present_gtk_window(signal_backend, *, window_id: str = "WallPosit_MainWindow") -> bool:
    """Present the real GTK window and enter the main loop.

    Returns True when the target window object is found and shown.
    """
    try:
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
    except Exception as exc:  # pragma: no cover - depends on host GTK runtime.
        raise RuntimeError(f"GTK runtime unavailable: {exc}") from exc

    if not hasattr(signal_backend, "get_object"):
        raise TypeError("signal backend must provide get_object(name)")

    window = _resolve_window(signal_backend, window_id)
    if window is None:
        return False

    # Ensure the minimal prototype flow can exit Gtk.main() by window close.
    if hasattr(window, "connect") and not getattr(window, "_harite_quit_hooked", False):

        def _on_delete_event(*_args):
            Gtk.main_quit()
            return False

        window.connect("delete-event", _on_delete_event)
        setattr(window, "_harite_quit_hooked", True)

    if hasattr(window, "show_all"):
        window.show_all()
    if hasattr(window, "present"):
        window.present()

    Gtk.main()
    return True

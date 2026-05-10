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
from harite.gui.adapters.gtk_runtime_builders import build_about_dialog_section
from harite.gui.adapters.gtk_runtime_builders import build_center_body_section
from harite.gui.adapters.gtk_runtime_builders import build_centered_page_shell
from harite.gui.adapters.gtk_runtime_builders import build_color_dialog_section
from harite.gui.adapters.gtk_runtime_builders import build_footer_section
from harite.gui.adapters.gtk_runtime_builders import build_header_section
from harite.gui.adapters.gtk_runtime_builders import build_main_tab_section
from harite.gui.adapters.gtk_runtime_builders import build_margins_tab_section
from harite.gui.adapters.gtk_runtime_builders import build_primary_margin_controls
from harite.gui.adapters.gtk_runtime_builders import build_runtime_state_labels
from harite.gui.adapters.gtk_runtime_builders import build_settings_section
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

            primary_margin_controls = build_primary_margin_controls(
                gtk_module,
                configure_spin_button=self._configure_spin_button,
            )
            top_margin_label = primary_margin_controls["top_margin_label"]
            top_margin_spin = primary_margin_controls["top_margin_spin"]
            left_margin_label = primary_margin_controls["left_margin_label"]
            left_margin_spin = primary_margin_controls["left_margin_spin"]

            center_body_widgets = build_center_body_section(gtk_module, root)
            center_row = center_body_widgets["center_row"]
            command_tabs = center_body_widgets["command_tabs"]

            main_widgets = build_main_tab_section(gtk_module)
            main_col = main_widgets["main_col"]
            main_section_label = main_widgets["main_section_label"]
            main_page_shell = build_centered_page_shell(gtk_module, main_col)
            compose_grid = main_widgets["compose_grid"]
            left_display_grid = main_widgets["left_display_grid"]
            right_display_grid = main_widgets["right_display_grid"]
            tgl_upper_l = main_widgets["tgl_upper_l"]
            tgl_upper_r = main_widgets["tgl_upper_r"]
            tgl_lower_l = main_widgets["tgl_lower_l"]
            tgl_lower_r = main_widgets["tgl_lower_r"]
            tgl_push_left_l = main_widgets["tgl_push_left_l"]
            tgl_push_right_l = main_widgets["tgl_push_right_l"]
            btn_get_img_l = main_widgets["btn_get_img_l"]
            tgl_push_left_r = main_widgets["tgl_push_left_r"]
            tgl_push_right_r = main_widgets["tgl_push_right_r"]
            btn_get_img_r = main_widgets["btn_get_img_r"]
            input_row_l = main_widgets["input_row_l"]
            input_entry_l = main_widgets["input_entry_l"]
            btn_clr_path_l = main_widgets["btn_clr_path_l"]
            input_row_r = main_widgets["input_row_r"]
            input_entry_r = main_widgets["input_entry_r"]
            btn_clr_path_r = main_widgets["btn_clr_path_r"]
            pick_state_label = main_widgets["pick_state_label"]

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

            state_labels = build_runtime_state_labels(gtk_module)
            do_it_plan_label = state_labels["do_it_plan_label"]
            save_path_state_label = state_labels["save_path_state_label"]
            save_target_label = state_labels["save_target_label"]
            priority_note_label = state_labels["priority_note_label"]
            style_legend_label = state_labels["style_legend_label"]
            current_state_section_label = state_labels["current_state_section_label"]
            current_margins_label = state_labels["current_margins_label"]
            current_left_label = state_labels["current_left_label"]
            current_right_label = state_labels["current_right_label"]

            command_tabs.append_page(main_page_shell, main_section_label)

            dialog_runtime = self._build_dialog_runtime_widgets(gtk_module=gtk_module, window=window)
            open_dialog_proxy = dialog_runtime["open_dialog_proxy"]
            save_path_dialog_proxy = dialog_runtime["save_path_dialog_proxy"]
            prefs_window = dialog_runtime["prefs_window"]
            prefs_apply_btn = dialog_runtime["prefs_apply_btn"]
            prefs_load_btn = dialog_runtime["prefs_load_btn"]
            prefs_save_btn = dialog_runtime["prefs_save_btn"]
            prefs_close_btn = dialog_runtime["prefs_close_btn"]
            prefs_state_label = dialog_runtime["prefs_state_label"]
            prefs_editor_box = dialog_runtime["prefs_editor_box"]
            prefs_editor_title = dialog_runtime["prefs_editor_title"]
            prefs_resolution_entry = dialog_runtime["prefs_resolution_entry"]
            prefs_scaling_entry = dialog_runtime["prefs_scaling_entry"]
            prefs_two_screen_auto = dialog_runtime["prefs_two_screen_auto"]
            prefs_two_screen_on = dialog_runtime["prefs_two_screen_on"]
            prefs_two_screen_off = dialog_runtime["prefs_two_screen_off"]
            prefs_l_display_entry = dialog_runtime["prefs_l_display_entry"]
            prefs_r_display_entry = dialog_runtime["prefs_r_display_entry"]
            prefs_margins_entry = dialog_runtime["prefs_margins_entry"]
            prefs_align_entry = dialog_runtime["prefs_align_entry"]
            prefs_valign_entry = dialog_runtime["prefs_valign_entry"]
            prefs_quality_spin = dialog_runtime["prefs_quality_spin"]
            prefs_margin_text_mode_entry = dialog_runtime["prefs_margin_text_mode_entry"]
            prefs_margin_text_entry = dialog_runtime["prefs_margin_text_entry"]
            prefs_margin_text_position_entry = dialog_runtime["prefs_margin_text_position_entry"]
            prefs_margin_text_max_lines_spin = dialog_runtime["prefs_margin_text_max_lines_spin"]
            prefs_plugin_entry = dialog_runtime["prefs_plugin_entry"]
            prefs_apply_single = dialog_runtime["prefs_apply_single"]
            prefs_apply_per_monitor = dialog_runtime["prefs_apply_per_monitor"]
            prefs_import_path_entry = dialog_runtime["prefs_import_path_entry"]
            prefs_export_path_entry = dialog_runtime["prefs_export_path_entry"]
            settings_dialog_proxy = dialog_runtime["settings_dialog_proxy"]
            color_window = dialog_runtime["color_window"]
            color_value_entry = dialog_runtime["color_value_entry"]
            color_state_label = dialog_runtime["color_state_label"]
            color_apply_btn = dialog_runtime["color_apply_btn"]
            color_cancel_btn = dialog_runtime["color_cancel_btn"]
            color_dialog_proxy = dialog_runtime["color_dialog_proxy"]
            about_window = dialog_runtime["about_window"]
            about_title_label = dialog_runtime["about_title_label"]
            about_version_label = dialog_runtime["about_version_label"]
            about_description_label = dialog_runtime["about_description_label"]
            about_credits_label = dialog_runtime["about_credits_label"]
            about_license_label = dialog_runtime["about_license_label"]
            about_close_btn = dialog_runtime["about_close_btn"]
            about_dialog_proxy = dialog_runtime["about_dialog_proxy"]
            srcdir_dialog_proxy = dialog_runtime["srcdir_dialog_proxy"]

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
            margins_page_shell = build_centered_page_shell(gtk_module, margins_tab_box)
            command_tabs.append_page(margins_page_shell, margins_tab_title)

            watch_page_shell = build_centered_page_shell(gtk_module, watch_tab_box)
            command_tabs.append_page(watch_page_shell, watch_tab_title)

            footer_widgets = build_footer_section(gtk_module, root)
            footer_col = footer_widgets["footer_col"]
            status_row = footer_widgets["status_row"]
            status_label = footer_widgets["status_label"]
            status_spacer = footer_widgets["status_spacer"]
            watch_summary_label = footer_widgets["watch_summary_label"]
            error_label = footer_widgets["error_label"]

            if hasattr(window, "add"):
                window.add(root)

            self._objects = self._build_runtime_object_map(
                window=window,
                root=root,
                top_margin_label=top_margin_label,
                top_margin_spin=top_margin_spin,
                left_margin_label=left_margin_label,
                left_margin_spin=left_margin_spin,
                title=title,
                subtitle=subtitle,
                main_section_label=main_section_label,
                main_col=main_col,
                compose_grid=compose_grid,
                left_display_grid=left_display_grid,
                right_display_grid=right_display_grid,
                input_row_l=input_row_l,
                input_row_r=input_row_r,
                action_cluster_row=action_cluster_row,
                optimize_group=optimize_group,
                tgl_upper_l=tgl_upper_l,
                tgl_upper_r=tgl_upper_r,
                tgl_push_left_l=tgl_push_left_l,
                tgl_push_right_l=tgl_push_right_l,
                tgl_lower_l=tgl_lower_l,
                tgl_push_left_r=tgl_push_left_r,
                tgl_push_right_r=tgl_push_right_r,
                tgl_lower_r=tgl_lower_r,
                btn_get_img_l=btn_get_img_l,
                btn_get_img_r=btn_get_img_r,
                pick_state_label=pick_state_label,
                input_entry_l=input_entry_l,
                btn_clr_path_l=btn_clr_path_l,
                input_entry_r=input_entry_r,
                btn_clr_path_r=btn_clr_path_r,
                right_margin_col=right_margin_col,
                right_margin_label=right_margin_label,
                right_margin_spin=right_margin_spin,
                bottom_margin_row=bottom_margin_row,
                bottom_margin_label=bottom_margin_label,
                bottom_margin_spin=bottom_margin_spin,
                optimize_section_label=optimize_section_label,
                optimize_row=optimize_row,
                optimize_btn=optimize_btn,
                optimize_modern_btn=optimize_modern_btn,
                optimize_result=optimize_result,
                apply_section_label=apply_section_label,
                apply_row=apply_row,
                apply_btn=apply_btn,
                apply_target=apply_target,
                preview_section_label=preview_section_label,
                preview_group=preview_group,
                preview_images_row=preview_images_row,
                preview_left=preview_left,
                preview_right=preview_right,
                preview_left_assignment=preview_left_assignment,
                preview_right_assignment=preview_right_assignment,
                preview_left_result=preview_left_result,
                preview_right_result=preview_right_result,
                preview_state_label=preview_state_label,
                preview_source_label=preview_source_label,
                preview_assist_label=preview_assist_label,
                rad_apply_single=rad_apply_single,
                rad_apply_per_monitor=rad_apply_per_monitor,
                apply_mode_label=apply_mode_label,
                do_it_plan_label=do_it_plan_label,
                save_target_label=save_target_label,
                priority_note_label=priority_note_label,
                style_legend_label=style_legend_label,
                current_state_section_label=current_state_section_label,
                current_margins_label=current_margins_label,
                current_left_label=current_left_label,
                current_right_label=current_right_label,
                command_section_label=command_section_label,
                command_tabs=command_tabs,
                command_bar=command_bar,
                btn_setting=btn_setting,
                prefs_apply_btn=prefs_apply_btn,
                prefs_load_btn=prefs_load_btn,
                prefs_save_btn=prefs_save_btn,
                prefs_close_btn=prefs_close_btn,
                prefs_state_label=prefs_state_label,
                prefs_editor_box=prefs_editor_box,
                prefs_window=prefs_window,
                prefs_editor_title=prefs_editor_title,
                prefs_resolution_entry=prefs_resolution_entry,
                prefs_scaling_entry=prefs_scaling_entry,
                prefs_two_screen_auto=prefs_two_screen_auto,
                prefs_two_screen_on=prefs_two_screen_on,
                prefs_two_screen_off=prefs_two_screen_off,
                prefs_l_display_entry=prefs_l_display_entry,
                prefs_r_display_entry=prefs_r_display_entry,
                prefs_margins_entry=prefs_margins_entry,
                prefs_align_entry=prefs_align_entry,
                prefs_valign_entry=prefs_valign_entry,
                prefs_quality_spin=prefs_quality_spin,
                prefs_margin_text_mode_entry=prefs_margin_text_mode_entry,
                prefs_margin_text_entry=prefs_margin_text_entry,
                prefs_margin_text_position_entry=prefs_margin_text_position_entry,
                prefs_margin_text_max_lines_spin=prefs_margin_text_max_lines_spin,
                prefs_plugin_entry=prefs_plugin_entry,
                prefs_apply_single=prefs_apply_single,
                prefs_apply_per_monitor=prefs_apply_per_monitor,
                prefs_import_path_entry=prefs_import_path_entry,
                prefs_export_path_entry=prefs_export_path_entry,
                btn_set_color=btn_set_color,
                color_dialog_proxy=color_dialog_proxy,
                color_window=color_window,
                color_value_entry=color_value_entry,
                color_state_label=color_state_label,
                color_apply_btn=color_apply_btn,
                color_cancel_btn=color_cancel_btn,
                about_dialog_proxy=about_dialog_proxy,
                about_window=about_window,
                about_title_label=about_title_label,
                about_version_label=about_version_label,
                about_description_label=about_description_label,
                about_credits_label=about_credits_label,
                about_license_label=about_license_label,
                about_close_btn=about_close_btn,
                open_dialog_proxy=open_dialog_proxy,
                srcdir_dialog_proxy=srcdir_dialog_proxy,
                settings_dialog_proxy=settings_dialog_proxy,
                watch_tab_box=watch_tab_box,
                margins_tab_box=margins_tab_box,
                watch_controls_row=watch_controls_row,
                watch_detail_row=watch_detail_row,
                margins_tab_title=margins_tab_title,
                margins_section_label=margins_section_label,
                margin_text_tabs=margin_text_tabs,
                margin_settings_page=margin_settings_page,
                margin_text_page=margin_text_page,
                margin_settings_preview_label=margin_settings_preview_label,
                margin_text_section_label=margin_text_section_label,
                margin_text_mode_label=margin_text_mode_label,
                margin_text_mode_off=margin_text_mode_off,
                margin_text_mode_settings=margin_text_mode_settings,
                margin_text_mode_text=margin_text_mode_text,
                margin_text_mode_both=margin_text_mode_both,
                margin_text_entry=margin_text_entry,
                margin_position_left_top=margin_position_left_top,
                margin_position_right_bottom=margin_position_right_bottom,
                margin_position_left_bottom=margin_position_left_bottom,
                margin_position_right_top=margin_position_right_top,
                margin_text_max_lines_spin=margin_text_max_lines_spin,
                btn_open_srcdir_l=btn_open_srcdir_l,
                btn_open_srcdir_r=btn_open_srcdir_r,
                watch_label=watch_label,
                watch_tab_title=watch_tab_title,
                interval_spin=interval_spin,
                interval_label=interval_label,
                btn_daemonize=btn_daemonize,
                btn_cancel_daemonize=btn_cancel_daemonize,
                btn_about=btn_about,
                btn_help=btn_help,
                footer_col=footer_col,
                flow_row=flow_row,
                flow_legend_label=flow_legend_label,
                status_label=status_label,
                error_label=error_label,
                watch_summary_label=watch_summary_label,
                watch_sources_label=watch_sources_label,
                watch_current_label=watch_current_label,
                watch_output_label=watch_output_label,
                save_path_state_label=save_path_state_label,
                save_path_dialog_proxy=save_path_dialog_proxy,
            )

            self._assign_object_names()
            self._connect_runtime_widgets(
                input_entry_l=input_entry_l,
                input_entry_r=input_entry_r,
                tgl_upper_l=tgl_upper_l,
                tgl_lower_l=tgl_lower_l,
                tgl_upper_r=tgl_upper_r,
                tgl_lower_r=tgl_lower_r,
                tgl_push_left_l=tgl_push_left_l,
                tgl_push_right_l=tgl_push_right_l,
                tgl_push_left_r=tgl_push_left_r,
                tgl_push_right_r=tgl_push_right_r,
                btn_get_img_l=btn_get_img_l,
                btn_get_img_r=btn_get_img_r,
                btn_clr_path_l=btn_clr_path_l,
                btn_clr_path_r=btn_clr_path_r,
                top_margin_spin=top_margin_spin,
                left_margin_spin=left_margin_spin,
                right_margin_spin=right_margin_spin,
                bottom_margin_spin=bottom_margin_spin,
                optimize_btn=optimize_btn,
                optimize_modern_btn=optimize_modern_btn,
                apply_btn=apply_btn,
                btn_setting=btn_setting,
                prefs_apply_btn=prefs_apply_btn,
                prefs_load_btn=prefs_load_btn,
                prefs_save_btn=prefs_save_btn,
                prefs_close_btn=prefs_close_btn,
                rad_apply_single=rad_apply_single,
                rad_apply_per_monitor=rad_apply_per_monitor,
                btn_set_color=btn_set_color,
                btn_about=btn_about,
                color_apply_btn=color_apply_btn,
                color_cancel_btn=color_cancel_btn,
                about_close_btn=about_close_btn,
                btn_open_srcdir_l=btn_open_srcdir_l,
                btn_open_srcdir_r=btn_open_srcdir_r,
                interval_spin=interval_spin,
                btn_daemonize=btn_daemonize,
                btn_cancel_daemonize=btn_cancel_daemonize,
                margin_text_mode_off=margin_text_mode_off,
                margin_text_mode_settings=margin_text_mode_settings,
                margin_text_mode_text=margin_text_mode_text,
                margin_text_mode_both=margin_text_mode_both,
                margin_text_entry=margin_text_entry,
                margin_position_left_top=margin_position_left_top,
                margin_position_right_bottom=margin_position_right_bottom,
                margin_position_left_bottom=margin_position_left_bottom,
                margin_position_right_top=margin_position_right_top,
                margin_text_max_lines_spin=margin_text_max_lines_spin,
            )
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

    def _assign_object_names(self) -> None:
        for object_name, widget in self._objects.items():
            if hasattr(widget, "set_name"):
                widget.set_name(object_name)
            elif not hasattr(widget, "get_name"):
                setattr(widget, "name", object_name)

    def _build_runtime_object_map(self, **widgets: Any) -> dict[str, Any]:
        return {
            "WallPosit_MainWindow": widgets["window"],
            "main_window": widgets["window"],
            "boxRoot": widgets["root"],
            "lblTopMargin": widgets["top_margin_label"],
            "spnTopMargin": widgets["top_margin_spin"],
            "lblLeftMargin": widgets["left_margin_label"],
            "spnLeftMargin": widgets["left_margin_spin"],
            "lblTitle": widgets["title"],
            "lblSubtitle": widgets["subtitle"],
            "lblMainSection": widgets["main_section_label"],
            "boxMainSection": widgets["main_col"],
            "composeGrid": widgets["compose_grid"],
            "leftDisplayCol": widgets["left_display_grid"],
            "rightDisplayCol": widgets["right_display_grid"],
            "inputRowL": widgets["input_row_l"],
            "inputRowR": widgets["input_row_r"],
            "actionClusterRow": widgets["action_cluster_row"],
            "actionClusterCol": widgets["optimize_group"],
            "tglUpperL": widgets["tgl_upper_l"],
            "tglUpperR": widgets["tgl_upper_r"],
            "tglPushLeftL": widgets["tgl_push_left_l"],
            "tglPushRightL": widgets["tgl_push_right_l"],
            "tglLowerL": widgets["tgl_lower_l"],
            "tglPushLeftR": widgets["tgl_push_left_r"],
            "tglPushRightR": widgets["tgl_push_right_r"],
            "tglLowerR": widgets["tgl_lower_r"],
            "btnGetImgL": widgets["btn_get_img_l"],
            "btnGetImgR": widgets["btn_get_img_r"],
            "lblPickState": widgets["pick_state_label"],
            "entPathL": widgets["input_entry_l"],
            "btnClrPathL": widgets["btn_clr_path_l"],
            "entPathR": widgets["input_entry_r"],
            "btnClrPathR": widgets["btn_clr_path_r"],
            "vbox5": widgets["right_margin_col"],
            "lblRightMargin": widgets["right_margin_label"],
            "spnRightMargin": widgets["right_margin_spin"],
            "hbox12": widgets["bottom_margin_row"],
            "lblBottomMargin": widgets["bottom_margin_label"],
            "spnBottomMargin": widgets["bottom_margin_spin"],
            "lblOptimizeSection": widgets["optimize_section_label"],
            "boxOptimizeSection": widgets["optimize_row"],
            "btnSave": widgets["optimize_btn"],
            "btnOptimize": widgets["optimize_modern_btn"],
            "lblOptimizeResult": widgets["optimize_result"],
            "lblApplySection": widgets["apply_section_label"],
            "boxApplySection": widgets["apply_row"],
            "btnSetWall": widgets["apply_btn"],
            "lblApplyTarget": widgets["apply_target"],
            "lblPreviewSection": widgets["preview_section_label"],
            "boxPreviewSection": widgets["preview_group"],
            "boxPreviewImagesRow": widgets["preview_images_row"],
            "imgPreviewL": widgets["preview_left"],
            "imgPreviewR": widgets["preview_right"],
            "lblPreviewAssignL": widgets["preview_left_assignment"],
            "lblPreviewAssignR": widgets["preview_right_assignment"],
            "lblPreviewResultL": widgets["preview_left_result"],
            "lblPreviewResultR": widgets["preview_right_result"],
            "lblPreviewState": widgets["preview_state_label"],
            "lblPreviewSource": widgets["preview_source_label"],
            "lblPreviewAssist": widgets["preview_assist_label"],
            "radApplySingle": widgets["rad_apply_single"],
            "radApplyPerMonitor": widgets["rad_apply_per_monitor"],
            "lblApplyMode": widgets["apply_mode_label"],
            "lblDoItPlanned": widgets["do_it_plan_label"],
            "lblSaveTarget": widgets["save_target_label"],
            "lblPriorityRule": widgets["priority_note_label"],
            "lblStyleLegend": widgets["style_legend_label"],
            "lblCurrentStateSection": widgets["current_state_section_label"],
            "lblCurrentMargins": widgets["current_margins_label"],
            "lblCurrentStateL": widgets["current_left_label"],
            "lblCurrentStateR": widgets["current_right_label"],
            "lblCommandSection": widgets["command_section_label"],
            "commandTabs": widgets["command_tabs"],
            "hbox14": widgets["command_bar"],
            "btnSetting": widgets["btn_setting"],
            "btnSettings": widgets["btn_setting"],
            "btnSettingsApply": widgets["prefs_apply_btn"],
            "btnSettingsLoad": widgets["prefs_load_btn"],
            "btnSettingsSave": widgets["prefs_save_btn"],
            "btnSettingsClose": widgets["prefs_close_btn"],
            "lblSettingsState": widgets["prefs_state_label"],
            "boxSettingsEditor": widgets["prefs_editor_box"],
            "settingsWindow": widgets["prefs_window"],
            "lblSettingsEditorTitle": widgets["prefs_editor_title"],
            "entSettingsResolution": widgets["prefs_resolution_entry"],
            "entSettingsScaling": widgets["prefs_scaling_entry"],
            "radSettingsTwoScreenAuto": widgets["prefs_two_screen_auto"],
            "radSettingsTwoScreenOn": widgets["prefs_two_screen_on"],
            "radSettingsTwoScreenOff": widgets["prefs_two_screen_off"],
            "entSettingsLDisplay": widgets["prefs_l_display_entry"],
            "entSettingsRDisplay": widgets["prefs_r_display_entry"],
            "entSettingsMargins": widgets["prefs_margins_entry"],
            "entSettingsAlign": widgets["prefs_align_entry"],
            "entSettingsValign": widgets["prefs_valign_entry"],
            "spnSettingsQuality": widgets["prefs_quality_spin"],
            "entSettingsMarginTextMode": widgets["prefs_margin_text_mode_entry"],
            "entSettingsMarginText": widgets["prefs_margin_text_entry"],
            "entSettingsMarginTextPosition": widgets["prefs_margin_text_position_entry"],
            "spnSettingsMarginTextMaxLines": widgets["prefs_margin_text_max_lines_spin"],
            "entSettingsPlugin": widgets["prefs_plugin_entry"],
            "radSettingsApplySingle": widgets["prefs_apply_single"],
            "radSettingsApplyPerMonitor": widgets["prefs_apply_per_monitor"],
            "entSettingsImportPath": widgets["prefs_import_path_entry"],
            "entSettingsExportPath": widgets["prefs_export_path_entry"],
            "btnSetColor": widgets["btn_set_color"],
            "ColorDialog": widgets["color_dialog_proxy"],
            "colorWindow": widgets["color_window"],
            "entColorValue": widgets["color_value_entry"],
            "lblColorState": widgets["color_state_label"],
            "btnColorApply": widgets["color_apply_btn"],
            "btnColorCancel": widgets["color_cancel_btn"],
            "AboutDialog": widgets["about_dialog_proxy"],
            "aboutWindow": widgets["about_window"],
            "lblAboutTitle": widgets["about_title_label"],
            "lblAboutVersion": widgets["about_version_label"],
            "lblAboutDescription": widgets["about_description_label"],
            "lblAboutCredits": widgets["about_credits_label"],
            "lblAboutLicense": widgets["about_license_label"],
            "btnAboutClose": widgets["about_close_btn"],
            "ImgOpenDialog": widgets["open_dialog_proxy"],
            "SrcdirDialog": widgets["srcdir_dialog_proxy"],
            **{object_name: widgets["settings_dialog_proxy"] for object_name in SETTINGS_DIALOG_OBJECT_ALIASES},
            "watchTab": widgets["watch_tab_box"],
            "marginsTab": widgets["margins_tab_box"],
            "watchControlsRow": widgets["watch_controls_row"],
            "watchDetailRow": widgets["watch_detail_row"],
            "lblMarginsTabTitle": widgets["margins_tab_title"],
            "lblMarginsSection": widgets["margins_section_label"],
            "marginTextTabs": widgets["margin_text_tabs"],
            "marginSettingsPage": widgets["margin_settings_page"],
            "marginTextPage": widgets["margin_text_page"],
            "lblMarginSettingsPreview": widgets["margin_settings_preview_label"],
            "lblMarginTextSection": widgets["margin_text_section_label"],
            "lblMarginTextMode": widgets["margin_text_mode_label"],
            "radMarginTextModeOff": widgets["margin_text_mode_off"],
            "radMarginTextModeSettings": widgets["margin_text_mode_settings"],
            "radMarginTextModeText": widgets["margin_text_mode_text"],
            "radMarginTextModeBoth": widgets["margin_text_mode_both"],
            "txtMarginText": widgets["margin_text_entry"],
            "radMarginTextPositionLeftTop": widgets["margin_position_left_top"],
            "radMarginTextPositionRightBottom": widgets["margin_position_right_bottom"],
            "radMarginTextPositionLeftBottom": widgets["margin_position_left_bottom"],
            "radMarginTextPositionRightTop": widgets["margin_position_right_top"],
            "spnMarginTextMaxLines": widgets["margin_text_max_lines_spin"],
            "btnOpenSrcdirL": widgets["btn_open_srcdir_l"],
            "btnOpenSrcdirR": widgets["btn_open_srcdir_r"],
            "lblWatchSection": widgets["watch_label"],
            "lblWatchTabTitle": widgets["watch_tab_title"],
            "spnInterval": widgets["interval_spin"],
            "lblInterval": widgets["interval_label"],
            "btnDaemonize": widgets["btn_daemonize"],
            "btnCancelDaemonize": widgets["btn_cancel_daemonize"],
            "btnAbout": widgets["btn_about"],
            "btnHelp": widgets["btn_help"],
            "statusbar": widgets["footer_col"],
            "flowRow": widgets["flow_row"],
            "lblFlowLegend": widgets["flow_legend_label"],
            "lblStatus": widgets["status_label"],
            "lblError": widgets["error_label"],
            "lblWatchSummary": widgets["watch_summary_label"],
            "lblWatchSources": widgets["watch_sources_label"],
            "lblWatchCurrent": widgets["watch_current_label"],
            "lblWatchOutput": widgets["watch_output_label"],
            **{object_name: widgets["save_path_state_label"] for object_name in SAVE_PATH_STATE_LABEL_ALIASES},
            **{object_name: widgets["save_path_dialog_proxy"] for object_name in SAVE_PATH_DIALOG_OBJECT_ALIASES},
        }

    def _build_dialog_runtime_widgets(self, *, gtk_module: Any, window: Any) -> dict[str, Any]:
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

        settings_widgets = build_settings_section(gtk_module, configure_spin_button=self._configure_spin_button)
        prefs_window = settings_widgets["prefs_window"]
        settings_dialog_proxy = _SettingsDialogProxy(prefs_window)
        if hasattr(prefs_window, "connect"):
            prefs_window.connect(
                "delete-event",
                lambda *_args: self._on_preferences_window_delete_event(),
            )

        prefs_apply_single = settings_widgets["prefs_apply_single"]
        prefs_apply_per_monitor = settings_widgets["prefs_apply_per_monitor"]
        prefs_apply_single.connect(
            "toggled",
            lambda widget, *_args: self._on_preferences_apply_mode_toggled(widget, "single-file"),
        )
        prefs_apply_per_monitor.connect(
            "toggled",
            lambda widget, *_args: self._on_preferences_apply_mode_toggled(widget, "per-monitor-auto-split"),
        )

        color_widgets = build_color_dialog_section(gtk_module, default_color_hex=DEFAULT_BACKGROUND_COLOR_HEX)
        color_window = color_widgets["color_window"]
        color_value_entry = color_widgets["color_value_entry"]
        color_state_label = color_widgets["color_state_label"]
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

        about_widgets = build_about_dialog_section(gtk_module)
        about_window = about_widgets["about_window"]
        about_dialog_proxy = _AboutDialogProxy(
            about_window,
            about_widgets["about_title_label"],
            about_widgets["about_version_label"],
            about_widgets["about_description_label"],
            about_widgets["about_credits_label"],
            about_widgets["about_license_label"],
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

        return {
            "open_dialog_proxy": open_dialog_proxy,
            "save_path_dialog_proxy": save_path_dialog_proxy,
            **settings_widgets,
            "settings_dialog_proxy": settings_dialog_proxy,
            **color_widgets,
            "color_dialog_proxy": color_dialog_proxy,
            **about_widgets,
            "about_dialog_proxy": about_dialog_proxy,
            "srcdir_dialog_proxy": srcdir_dialog_proxy,
        }

    def _connect_runtime_widgets(self, **widgets: Any) -> None:
        # Why: fallback window must still exercise MainWindow handlers even when
        # legacy glade cannot be parsed at runtime.
        try:
            widgets["input_entry_l"].connect("changed", self._on_input_changed)
        except Exception:
            pass
        try:
            widgets["input_entry_r"].connect("changed", self._on_input_changed)
        except Exception:
            pass

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
            widget.connect("pressed", lambda *_args, key=handler_key: self._on_direction_pressed(key))
            widget.connect("toggled", lambda *_args, key=handler_key: self._on_direction_toggled(key))
            widget.connect("released", lambda *_args, key=handler_key: self._on_direction_released(key))

        widgets["btn_get_img_l"].connect("clicked", lambda *_args: self._on_pick_input_clicked("L"))
        widgets["btn_get_img_r"].connect("clicked", lambda *_args: self._on_pick_input_clicked("R"))
        widgets["btn_clr_path_l"].connect("clicked", lambda *_args: self._on_clear_input_clicked("L"))
        widgets["btn_clr_path_r"].connect("clicked", lambda *_args: self._on_clear_input_clicked("R"))

        for widget_name in ("top_margin_spin", "left_margin_spin", "right_margin_spin", "bottom_margin_spin"):
            widgets[widget_name].connect("value-changed", self._on_margin_changed)

        widgets["optimize_btn"].connect("clicked", self._on_save_clicked)
        widgets["optimize_modern_btn"].connect("clicked", self._on_optimize_clicked)
        widgets["apply_btn"].connect("clicked", self._on_apply_clicked)
        widgets["btn_setting"].connect("clicked", self._on_settings_clicked)
        widgets["prefs_apply_btn"].connect("clicked", self._on_preferences_apply_clicked)
        widgets["prefs_load_btn"].connect("clicked", self._on_preferences_load_clicked)
        widgets["prefs_save_btn"].connect("clicked", self._on_preferences_save_clicked)
        widgets["prefs_close_btn"].connect("clicked", self._on_preferences_close_clicked)
        widgets["rad_apply_single"].connect(
            "toggled",
            lambda widget, *_args: self._on_apply_mode_toggled(widget, "single-file"),
        )
        widgets["rad_apply_per_monitor"].connect(
            "toggled",
            lambda widget, *_args: self._on_apply_mode_toggled(widget, "per-monitor-auto-split"),
        )
        widgets["btn_set_color"].connect("clicked", self._on_color_clicked)
        widgets["btn_about"].connect("clicked", self._on_about_clicked)
        widgets["color_apply_btn"].connect("clicked", self._on_color_dialog_apply_clicked)
        widgets["color_cancel_btn"].connect("clicked", self._on_color_dialog_cancel_clicked)
        widgets["about_close_btn"].connect("clicked", self._on_about_dialog_close_clicked)
        widgets["btn_open_srcdir_l"].connect("clicked", lambda *_args: self._on_pick_srcdir_clicked("L"))
        widgets["btn_open_srcdir_r"].connect("clicked", lambda *_args: self._on_pick_srcdir_clicked("R"))
        widgets["interval_spin"].connect("value-changed", self._on_watch_interval_changed)
        widgets["btn_daemonize"].connect("clicked", self._on_watch_start_clicked)
        widgets["btn_cancel_daemonize"].connect("clicked", self._on_watch_stop_clicked)
        widgets["margin_text_mode_off"].connect(
            "toggled",
            lambda widget, *_args: self._on_margin_text_mode_toggled(widget, "none"),
        )
        widgets["margin_text_mode_settings"].connect(
            "toggled",
            lambda widget, *_args: self._on_margin_text_mode_toggled(widget, "params"),
        )
        widgets["margin_text_mode_text"].connect(
            "toggled",
            lambda widget, *_args: self._on_margin_text_mode_toggled(widget, "free"),
        )
        widgets["margin_text_mode_both"].connect(
            "toggled",
            lambda widget, *_args: self._on_margin_text_mode_toggled(widget, "combo"),
        )

        margin_text_entry = widgets["margin_text_entry"]
        if hasattr(margin_text_entry, "get_buffer") and hasattr(margin_text_entry.get_buffer(), "connect"):
            margin_text_entry.get_buffer().connect(
                "changed",
                lambda *_args: self._on_margin_text_changed(margin_text_entry),
            )
        else:
            margin_text_entry.connect("changed", self._on_margin_text_changed)
        try:
            margin_text_entry.connect("key-press-event", self._on_margin_text_key_press)
        except Exception:
            pass

        widgets["margin_position_left_top"].connect(
            "toggled",
            lambda widget, *_args: self._on_margin_position_toggled(widget, "top"),
        )
        widgets["margin_position_right_bottom"].connect(
            "toggled",
            lambda widget, *_args: self._on_margin_position_toggled(widget, "bottom"),
        )
        widgets["margin_position_left_bottom"].connect(
            "toggled",
            lambda widget, *_args: self._on_margin_position_toggled(widget, "left"),
        )
        widgets["margin_position_right_top"].connect(
            "toggled",
            lambda widget, *_args: self._on_margin_position_toggled(widget, "right"),
        )
        widgets["margin_text_max_lines_spin"].connect(
            "value-changed",
            self._on_margin_text_max_lines_changed,
        )

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

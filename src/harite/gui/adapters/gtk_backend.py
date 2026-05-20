"""GTK backend loader for optional UI signal binding.

This adapter is intentionally optional. It should only be used in environments
where PyGObject/GTK is available.
"""

from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import Any, Callable

from harite.core import DEFAULT_BACKGROUND_COLOR_HEX, normalize_background_color
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
from harite.gui.adapters.gtk_runtime_builders import build_slideshow_tab_section
from harite.gui.adapters.gtk_runtime_dialogs import AboutDialogProxy as _AboutDialogProxy
from harite.gui.adapters.gtk_runtime_dialogs import ColorDialogProxy as _ColorDialogProxy
from harite.gui.adapters.gtk_layout_builders import set_window_icon_if_supported
from harite.gui.adapters.gtk_runtime_dialogs import OpenDialogProxy as _OpenDialogProxy
from harite.gui.adapters.gtk_runtime_dialogs import SavePathDialogProxy as _SavePathDialogProxy
from harite.gui.adapters.gtk_runtime_dialogs import SettingsDialogProxy as _SettingsDialogProxy
from harite.gui.adapters.gtk_runtime_dialogs import SrcdirDialogProxy as _SrcdirDialogProxy
from harite.gui.adapters.gtk_runtime_object_registry import SAVE_PATH_DIALOG_OBJECT_ALIASES
from harite.gui.adapters.gtk_runtime_object_registry import SAVE_PATH_STATE_LABEL_ALIASES
from harite.gui.adapters.gtk_runtime_object_registry import build_runtime_object_aliases
from harite.gui.adapters.gtk_runtime_file_dialog_flow import current_srcdir_for_side
from harite.gui.adapters.gtk_runtime_file_dialog_flow import format_input_display
from harite.gui.adapters.gtk_runtime_file_dialog_flow import handle_save_path_cancel
from harite.gui.adapters.gtk_runtime_file_dialog_flow import handle_save_path_confirm
from harite.gui.adapters.gtk_runtime_file_dialog_flow import is_save_path_dialog_open
from harite.gui.adapters.gtk_runtime_file_dialog_flow import notify_open_dialog_destroy
from harite.gui.adapters.gtk_runtime_file_dialog_flow import on_clear_input_clicked
from harite.gui.adapters.gtk_runtime_file_dialog_flow import on_input_changed
from harite.gui.adapters.gtk_runtime_file_dialog_flow import on_native_save_path_canceled
from harite.gui.adapters.gtk_runtime_file_dialog_flow import on_native_save_path_confirmed
from harite.gui.adapters.gtk_runtime_file_dialog_flow import on_open_dialog_canceled
from harite.gui.adapters.gtk_runtime_file_dialog_flow import on_open_dialog_confirmed
from harite.gui.adapters.gtk_runtime_file_dialog_flow import on_pick_input_clicked
from harite.gui.adapters.gtk_runtime_file_dialog_flow import on_pick_srcdir_clicked
from harite.gui.adapters.gtk_runtime_file_dialog_flow import on_save_path_filename_changed
from harite.gui.adapters.gtk_runtime_file_dialog_flow import on_srcdir_dialog_canceled
from harite.gui.adapters.gtk_runtime_file_dialog_flow import on_srcdir_dialog_confirmed
from harite.gui.adapters.gtk_runtime_file_dialog_flow import set_save_path_dialog_open_state
from harite.gui.adapters.gtk_runtime_margin_text import sanitize_margin_text
from harite.gui.adapters.gtk_runtime_margin_text_gtk import apply_margin_text_widget_style
from harite.gui.adapters.gtk_runtime_margin_text_gtk import on_margin_text_key_press
from harite.gui.adapters.gtk_runtime_owner_sync import sync_input_preview_state_from_owner
from harite.gui.adapters.gtk_runtime_owner_sync import sync_margins_state_with_feedback_from_owner
from harite.gui.adapters.gtk_runtime_owner_sync import sync_non_preview_state_from_owner
from harite.gui.adapters.gtk_runtime_owner_sync import sync_preview_state_from_owner
from harite.gui.adapters.gtk_runtime_owner_sync import sync_slideshow_state_only_from_owner
from harite.gui.adapters.gtk_runtime_owner_sync import sync_slideshow_state_with_feedback_from_owner
from harite.gui.adapters.gtk_runtime_preview import build_preview_crop_boxes
from harite.gui.adapters.gtk_runtime_preview import clear_preview_widget
from harite.gui.adapters.gtk_runtime_preview import get_gdkpixbuf_module
from harite.gui.adapters.gtk_runtime_preview import preview_target_size
from harite.gui.adapters.gtk_runtime_preview import set_preview_widget
from harite.gui.adapters.gtk_runtime_save_path_access import current_save_path_filename
from harite.gui.adapters.gtk_runtime_save_path_access import get_save_path_destroy_callback
from harite.gui.adapters.gtk_runtime_save_path_access import get_save_path_dialog
from harite.gui.adapters.gtk_runtime_save_path_access import refresh_save_target_label
from harite.gui.adapters.gtk_runtime_save_path_access import set_save_path_state_text
from harite.gui.adapters.gtk_runtime_preview import sync_result_preview_from_owner
from harite.gui.adapters.gtk_runtime_settings_dialogs import close_about_dialog
from harite.gui.adapters.gtk_runtime_settings_dialogs import on_about_clicked
from harite.gui.adapters.gtk_runtime_settings_dialogs import on_about_dialog_close_clicked
from harite.gui.adapters.gtk_runtime_settings_dialogs import on_about_window_delete_event
from harite.gui.adapters.gtk_runtime_settings_dialogs import on_color_clicked
from harite.gui.adapters.gtk_runtime_settings_dialogs import on_color_dialog_apply_clicked
from harite.gui.adapters.gtk_runtime_settings_dialogs import on_color_dialog_canceled
from harite.gui.adapters.gtk_runtime_settings_dialogs import on_color_dialog_cancel_clicked
from harite.gui.adapters.gtk_runtime_settings_dialogs import on_color_dialog_confirmed
from harite.gui.adapters.gtk_runtime_settings_dialogs import on_color_window_delete_event
from harite.gui.adapters.gtk_runtime_settings_dialogs import on_settings_apply_clicked
from harite.gui.adapters.gtk_runtime_settings_dialogs import on_settings_apply_mode_toggled
from harite.gui.adapters.gtk_runtime_settings_dialogs import on_settings_close_clicked
from harite.gui.adapters.gtk_runtime_settings_dialogs import on_settings_load_clicked
from harite.gui.adapters.gtk_runtime_settings_dialogs import on_settings_save_clicked
from harite.gui.adapters.gtk_runtime_settings_dialogs import on_settings_window_delete_event
from harite.gui.adapters.gtk_runtime_settings_dialogs import on_settings_clicked
from harite.gui.adapters.gtk_runtime_settings_dialogs import read_settings_apply_mode
from harite.gui.adapters.gtk_runtime_settings_dialogs import read_settings_two_screen_mode
from harite.gui.adapters.gtk_runtime_settings_dialogs import refresh_about_dialog_from_getter
from harite.gui.adapters.gtk_runtime_settings_dialogs import refresh_color_dialog_from_getter
from harite.gui.adapters.gtk_runtime_settings_dialogs import refresh_settings_dialog_from_getter
from harite.gui.adapters.gtk_runtime_settings_dialogs import set_settings_apply_mode
from harite.gui.adapters.gtk_runtime_settings_dialogs import set_settings_two_screen_mode
from harite.gui.adapters.gtk_runtime_settings_dialogs import store_background_color_in_settings_dialog
from harite.gui.adapters.gtk_runtime_settings_dialogs import sync_settings_dialog_from_widgets
from harite.gui.adapters.gtk_runtime_settings_dialogs import sync_settings_widgets_from_dialog
from harite.gui.adapters.gtk_runtime_signal_wiring import connect_runtime_widgets
from harite.gui.adapters.gtk_runtime_state_labels import current_side_state
from harite.gui.adapters.gtk_runtime_state_labels import opposite_toggle_name
from harite.gui.adapters.gtk_runtime_state_labels import refresh_current_state_labels
from harite.gui.adapters.gtk_runtime_sync import build_margin_settings_preview
from harite.gui.adapters.gtk_runtime_sync import parse_margin_values
from harite.gui.adapters.gtk_runtime_sync import refresh_margins_controls
from harite.gui.adapters.gtk_runtime_sync import sync_feedback_from_owner
from harite.gui.adapters.gtk_runtime_sync import sync_input_state_from_owner
from harite.gui.adapters.gtk_runtime_sync import sync_main_state_from_owner
from harite.gui.adapters.gtk_runtime_sync import sync_margins_state_from_owner
from harite.gui.adapters.gtk_runtime_sync import sync_slideshow_state_from_owner
from harite.gui.adapters.gtk_runtime_widget_access import is_toggle_active
from harite.gui.adapters.gtk_runtime_widget_access import read_entry_text
from harite.gui.adapters.gtk_runtime_widget_access import read_spin_int
from harite.gui.adapters.gtk_runtime_widget_access import set_button_enabled
from harite.gui.adapters.gtk_runtime_widget_access import set_entry_text
from harite.gui.adapters.gtk_runtime_widget_access import set_error
from harite.gui.adapters.gtk_runtime_widget_access import set_feedback
from harite.gui.adapters.gtk_runtime_widget_access import set_label_text
from harite.gui.adapters.gtk_runtime_widget_access import set_notebook_page
from harite.gui.adapters.gtk_runtime_widget_access import set_spin_value
from harite.gui.adapters.gtk_runtime_widget_access import set_status
from harite.gui.adapters.gtk_runtime_widget_access import set_toggle_active
from harite.gui.adapters.gtk_runtime_widget_access import set_widget_enabled
from harite.gui.adapters.gtk_runtime_slideshow_ui import on_slideshow_interval_changed
from harite.gui.adapters.gtk_runtime_slideshow_ui import on_slideshow_start_clicked
from harite.gui.adapters.gtk_runtime_slideshow_ui import on_slideshow_stop_clicked
from harite.gui.adapters.gtk_runtime_slideshow_ui import refresh_slideshow_current_label
from harite.gui.adapters.gtk_runtime_slideshow_ui import refresh_slideshow_output_label
from harite.gui.adapters.gtk_runtime_slideshow_ui import refresh_slideshow_source_labels
from harite.gui.adapters.gtk_runtime_slideshow_ui import refresh_slideshow_summary_label
from harite.gui.adapters.gtk_runtime_slideshow import get_glib_module
from harite.gui.adapters.gtk_runtime_slideshow import on_slideshow_timer_event
from harite.gui.adapters.gtk_runtime_slideshow import run_slideshow_cycle_for_side
from harite.gui.adapters.gtk_runtime_slideshow import run_slideshow_cycle_once as run_runtime_slideshow_cycle_once
from harite.gui.adapters.gtk_runtime_slideshow import start_slideshow_timer
from harite.gui.adapters.gtk_runtime_slideshow import stop_slideshow_timer
from harite.positioning import format_position_pair, parse_position_pair
from harite.slideshow import SlideshowCycleState


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
    """Current GTK runtime backend used for present/bind flows."""

    def __init__(self, gtk_module: Any) -> None:
        self._gtk = gtk_module
        self._signal_handlers: dict[str, Callable[..., Any]] = {}
        self._initialize_runtime_state()

        window = self._build_runtime_window(gtk_module)

        if hasattr(gtk_module, "Box") and hasattr(gtk_module, "Label"):
            main_runtime = self._build_main_runtime_widgets(gtk_module)
            root = main_runtime["root"]
            top_margin_label = main_runtime["top_margin_label"]
            top_margin_spin = main_runtime["top_margin_spin"]
            left_margin_label = main_runtime["left_margin_label"]
            left_margin_spin = main_runtime["left_margin_spin"]
            command_tabs = main_runtime["command_tabs"]
            priority_note_label = main_runtime["priority_note_label"]
            style_legend_label = main_runtime["style_legend_label"]
            current_state_section_label = main_runtime["current_state_section_label"]
            current_margins_label = main_runtime["current_margins_label"]
            current_left_label = main_runtime["current_left_label"]
            current_right_label = main_runtime["current_right_label"]

            dialog_runtime = self._build_dialog_runtime_widgets(gtk_module=gtk_module, window=window)
            tab_runtime = self._build_secondary_tab_runtime_widgets(
                gtk_module,
                command_tabs=command_tabs,
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
            )
            self._current_state_summary_display = tab_runtime["current_state_summary_display"]

            footer_runtime = self._build_footer_runtime_widgets(
                gtk_module,
                window=window,
                root=root,
            )

            self._objects = self._build_runtime_object_map(
                window=window,
                main_runtime=main_runtime,
                dialog_runtime=dialog_runtime,
                tab_runtime=tab_runtime,
                footer_runtime=footer_runtime,
            )

            self._assign_object_names()
            self._connect_runtime_widgets(
                main_runtime=main_runtime,
                dialog_runtime=dialog_runtime,
                tab_runtime=tab_runtime,
            )
            self._refresh_current_state_labels()
            self._refresh_margins_controls()
        else:
            self._objects = {
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

    def _initialize_runtime_state(self) -> None:
        self._input_path_l = ""
        self._input_path_r = ""
        self._prefs_apply_mode_preserved: str | None = None
        self._prefs_apply_mode_syncing = False
        self._slideshow_srcdir_l = ""
        self._slideshow_srcdir_r = ""
        self.slideshow_mode = "random"
        self._slideshow_active_mode = "random"
        self._slideshow_running = False
        self._slideshow_paused = False
        self._slideshow_state_l = SlideshowCycleState()
        self._slideshow_state_r = SlideshowCycleState()
        self._slideshow_previous_l: Path | None = None
        self._slideshow_previous_r: Path | None = None
        self._slideshow_timer_source_id: int | None = None

    def _build_runtime_window(self, gtk_module: Any) -> Any:
        window = gtk_module.Window(title="Harite")
        set_window_icon_if_supported(gtk_module, window, "icons", "product", "harite_app.svg")
        if hasattr(window, "set_resizable"):
            # P5-2 policy: modern desktop UX expects a resizable main window.
            window.set_resizable(True)
        if hasattr(window, "set_default_size"):
            window.set_default_size(1040, 720)
        return window

    def _build_main_runtime_widgets(self, gtk_module: Any) -> dict[str, Any]:
        root = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=10)
        root.set_border_width(10)

        header_widgets = build_header_section(gtk_module, root)
        primary_margin_controls = build_primary_margin_controls(
            gtk_module,
            configure_spin_button=self._configure_spin_button,
        )
        center_body_widgets = build_center_body_section(gtk_module, root)
        main_widgets = build_main_tab_section(gtk_module)
        main_page_shell = build_centered_page_shell(gtk_module, main_widgets["main_col"])
        action_widgets = build_action_cluster_section(
            gtk_module,
            main_widgets["main_col"],
            default_apply_mode=_default_apply_mode(),
        )
        state_labels = build_runtime_state_labels(gtk_module)

        center_body_widgets["command_tabs"].append_page(main_page_shell, main_widgets["main_section_label"])

        return {
            "root": root,
            **header_widgets,
            **primary_margin_controls,
            **center_body_widgets,
            **main_widgets,
            **action_widgets,
            **state_labels,
        }

    def _build_secondary_tab_runtime_widgets(
        self,
        gtk_module: Any,
        *,
        command_tabs: Any,
        top_margin_label: Any,
        top_margin_spin: Any,
        left_margin_label: Any,
        left_margin_spin: Any,
        priority_note_label: Any,
        style_legend_label: Any,
        current_state_section_label: Any,
        current_margins_label: Any,
        current_left_label: Any,
        current_right_label: Any,
    ) -> dict[str, Any]:
        slideshow_widgets = build_slideshow_tab_section(gtk_module, configure_spin_button=self._configure_spin_button)
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

        command_tabs.append_page(margins_widgets["margins_tab_box"], margins_widgets["margins_tab_title"])

        command_tabs.append_page(slideshow_widgets["slideshow_tab_box"], slideshow_widgets["slideshow_tab_title"])

        return {
            **slideshow_widgets,
            **margins_widgets,
        }

    def _build_footer_runtime_widgets(self, gtk_module: Any, *, window: Any, root: Any) -> dict[str, Any]:
        footer_widgets = build_footer_section(gtk_module, root)

        if hasattr(window, "add"):
            window.add(root)

        return {
            "footer_col": footer_widgets["footer_col"],
            "status_label": footer_widgets["status_label"],
            "slideshow_summary_label": footer_widgets["slideshow_summary_label"],
            "error_label": footer_widgets["error_label"],
        }

    def _build_runtime_object_map(
        self,
        *,
        window: Any,
        main_runtime: dict[str, Any],
        dialog_runtime: dict[str, Any],
        tab_runtime: dict[str, Any],
        footer_runtime: dict[str, Any],
    ) -> dict[str, Any]:
        widgets = {
            "window": window,
            **main_runtime,
            **dialog_runtime,
            **tab_runtime,
            **footer_runtime,
        }
        return build_runtime_object_aliases(widgets)

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
                lambda *_args: self._on_settings_window_delete_event(),
            )

        prefs_apply_single = settings_widgets["prefs_apply_single"]
        prefs_apply_per_monitor = settings_widgets["prefs_apply_per_monitor"]
        prefs_apply_single.connect(
            "toggled",
            lambda widget, *_args: self._on_settings_apply_mode_toggled(widget, "single-file"),
        )
        prefs_apply_per_monitor.connect(
            "toggled",
            lambda widget, *_args: self._on_settings_apply_mode_toggled(widget, "per-monitor-auto-split"),
        )

        color_widgets = build_color_dialog_section(gtk_module, default_color_hex=DEFAULT_BACKGROUND_COLOR_HEX)
        color_window = color_widgets["color_window"]
        color_value_entry = color_widgets["color_value_entry"]
        color_state_label = color_widgets["color_state_label"]
        color_notice_label = color_widgets["color_notice_label"]
        color_picker_host = color_widgets["color_picker_host"]
        color_pick_btn = color_widgets["color_pick_btn"]
        color_dialog_proxy = _ColorDialogProxy(
            gtk_module,
            window,
            color_window,
            color_value_entry,
            color_state_label,
            color_notice_label,
            color_picker_host,
            color_pick_btn,
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

    def _connect_runtime_widgets(
        self,
        *,
        main_runtime: dict[str, Any],
        dialog_runtime: dict[str, Any],
        tab_runtime: dict[str, Any],
    ) -> None:
        widgets = {
            **main_runtime,
            **dialog_runtime,
            **tab_runtime,
        }
        connect_runtime_widgets(self, widgets)

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
        set_status(self, message)

    def _set_error(self, message: str | None) -> None:
        set_error(self, message)

    def _set_feedback(self, *, phase: str, state: str, error: str | None = None) -> None:
        set_feedback(self, phase=phase, state=state, error=error)

    def _set_label_text(self, object_name: str, message: str) -> None:
        set_label_text(self, object_name, message)

    def _set_entry_text(self, object_name: str, value: object | None) -> None:
        set_entry_text(self, object_name, value)

    def _sanitize_margin_text(self, value: str) -> str:
        return sanitize_margin_text(value)

    def _apply_margin_text_widget_style(self, gtk_module: Any, shell: Any, entry: Any) -> None:
        apply_margin_text_widget_style(gtk_module, shell, entry)

    def _on_margin_text_key_press(self, widget: Any, event: Any) -> bool:
        return on_margin_text_key_press(widget, event)

    def _read_entry_text(self, object_name: str) -> str:
        return read_entry_text(self, object_name)

    def _set_spin_value(self, object_name: str, value: int) -> None:
        set_spin_value(self, object_name, value)

    def _set_button_enabled(self, object_name: str, enabled: bool) -> None:
        set_button_enabled(self, object_name, enabled)

    def _set_widget_enabled(self, object_name: str, enabled: bool) -> None:
        set_widget_enabled(self, object_name, enabled)

    def _set_notebook_page(self, object_name: str, page_index: int) -> None:
        set_notebook_page(self, object_name, page_index)

    def _get_save_path_dialog(self) -> Any | None:
        return get_save_path_dialog(self)

    def _get_save_path_destroy_callback(self) -> Callable[..., Any] | None:
        return get_save_path_destroy_callback(self)

    def _set_save_path_state_text(self, message: str) -> None:
        set_save_path_state_text(self, message)

    def _current_save_path_filename(self) -> str:
        return current_save_path_filename(self)

    def _refresh_save_target_label(self, filename: str | None = None) -> None:
        refresh_save_target_label(self, filename)

    def _refresh_slideshow_source_labels(self) -> None:
        refresh_slideshow_source_labels(self)

    def _refresh_slideshow_summary_label(self) -> None:
        refresh_slideshow_summary_label(self)

    def _refresh_slideshow_current_label(self, left: str | None = None, right: str | None = None) -> None:
        refresh_slideshow_current_label(self, left, right)

    def _refresh_slideshow_output_label(self, output_dir: str | None = None) -> None:
        refresh_slideshow_output_label(self, output_dir)

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

    def _sync_slideshow_state_from_owner(self, owner: Any) -> None:
        sync_slideshow_state_from_owner(self, owner)

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
        sync_non_preview_state_from_owner(self, owner)

    def _sync_preview_state_from_owner(self, owner: Any, *, include_input: bool = False, include_feedback: bool = False) -> None:
        sync_preview_state_from_owner(self, owner, include_input=include_input, include_feedback=include_feedback)

    def _sync_input_preview_state_from_owner(self, owner: Any, *, include_feedback: bool = False) -> None:
        sync_input_preview_state_from_owner(self, owner, include_feedback=include_feedback)

    def _sync_margins_state_with_feedback_from_owner(self, owner: Any) -> None:
        sync_margins_state_with_feedback_from_owner(self, owner)

    def _sync_slideshow_state_with_feedback_from_owner(self, owner: Any) -> None:
        sync_slideshow_state_with_feedback_from_owner(self, owner)

    def _sync_slideshow_state_only_from_owner(self, owner: Any) -> None:
        sync_slideshow_state_only_from_owner(self, owner)

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

    def _stop_slideshow_timer(self) -> None:
        stop_slideshow_timer(self)

    def _on_slideshow_timer_event(self) -> bool:
        return on_slideshow_timer_event(self)

    def _start_slideshow_timer(self, interval_seconds: int) -> bool:
        return start_slideshow_timer(self, interval_seconds)

    def _run_slideshow_cycle_for_side(self, side: str, source_dir: Path) -> str:
        return run_slideshow_cycle_for_side(self, side, source_dir)

    def _notify_srcdir_dialog_destroy(self) -> None:
        callback = self._signal_handlers.get("on_close_srcdir_dialog")
        if callback is None:
            return
        callback()

    def _notify_save_path_dialog_destroy(self) -> None:
        callback = self._get_save_path_destroy_callback()
        if callback is None:
            return
        callback()

    def _set_save_path_dialog_open_state(self, opened: bool, *, state_text: str | None = None) -> None:
        set_save_path_dialog_open_state(self, opened, state_text=state_text)

    def _on_save_path_filename_changed(self, filename: str) -> None:
        on_save_path_filename_changed(self, filename)

    def _is_save_path_dialog_open(self) -> bool:
        return is_save_path_dialog_open(self)

    def _on_input_changed(self, entry: Any) -> None:
        on_input_changed(self, entry)

    def _on_pick_input_clicked(self, side: str) -> None:
        on_pick_input_clicked(self, side)

    def _notify_open_dialog_destroy(self) -> None:
        notify_open_dialog_destroy(self)

    def _on_open_dialog_confirmed(self) -> None:
        on_open_dialog_confirmed(self)

    def _on_open_dialog_canceled(self, destroyed: bool = False) -> None:
        on_open_dialog_canceled(self, destroyed)

    def _format_input_display(self, path: str) -> str:
        return format_input_display(path)

    def _on_clear_input_clicked(self, side: str) -> None:
        on_clear_input_clicked(self, side)

    def _current_srcdir_for_side(self, side: str) -> str:
        return current_srcdir_for_side(self, side)

    def _on_pick_srcdir_clicked(self, side: str) -> None:
        on_pick_srcdir_clicked(self, side)

    def _on_srcdir_dialog_confirmed(self) -> None:
        on_srcdir_dialog_confirmed(self)

    def _on_srcdir_dialog_canceled(self, destroyed: bool = False) -> None:
        on_srcdir_dialog_canceled(self, destroyed)

    def _on_slideshow_interval_changed(self, widget: Any) -> None:
        on_slideshow_interval_changed(self, widget)

    def _on_slideshow_start_clicked(self, *_args: Any) -> None:
        on_slideshow_start_clicked(self, *_args)

    def _on_slideshow_stop_clicked(self, *_args: Any) -> None:
        on_slideshow_stop_clicked(self, *_args)

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
        except TypeError as exc:
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
        except TypeError as exc:
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
        except TypeError as exc:
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
        except TypeError as exc:
            self._set_feedback(phase="Margins", state="max-lines-error", error=str(exc))

    def run_slideshow_cycle_once(self) -> bool:
        return run_runtime_slideshow_cycle_once(self)

    def _set_toggle_active(self, object_name: str, active: bool) -> None:
        set_toggle_active(self, object_name, active)

    def _set_settings_two_screen_mode(self, value: object) -> None:
        set_settings_two_screen_mode(self, value)

    def _read_settings_two_screen_mode(self) -> str | bool:
        return read_settings_two_screen_mode(self)

    def _set_settings_apply_mode(self, value: object | None) -> None:
        set_settings_apply_mode(self, value)

    def _read_settings_apply_mode(self) -> str:
        return read_settings_apply_mode(self)

    def _on_settings_apply_mode_toggled(self, widget: Any, mode: str) -> None:
        on_settings_apply_mode_toggled(self, widget, mode)

    def _sync_settings_widgets_from_dialog(self) -> dict[str, object]:
        return sync_settings_widgets_from_dialog(self)

    def _sync_settings_dialog_from_widgets(self) -> dict[str, object]:
        return sync_settings_dialog_from_widgets(self)

    def _refresh_settings_dialog_from_getter(self) -> None:
        refresh_settings_dialog_from_getter(self)

    def _refresh_color_dialog_from_getter(self) -> str:
        return refresh_color_dialog_from_getter(self)

    def _refresh_about_dialog_from_getter(self) -> dict[str, object]:
        return refresh_about_dialog_from_getter(self)

    def _store_background_color_in_settings_dialog(self, color: str) -> None:
        store_background_color_in_settings_dialog(self, color)

    def _is_toggle_active(self, object_name: str) -> bool:
        return is_toggle_active(self, object_name)

    def _current_side_state(self, side: str) -> tuple[str, str]:
        return current_side_state(self, side)

    def _refresh_current_state_labels(self) -> None:
        refresh_current_state_labels(self)

    def _opposite_toggle_name(self, object_name: str) -> str | None:
        return opposite_toggle_name(object_name)

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
                        except Exception as exc:
                            self._set_feedback(phase="Position", state="error", error=str(exc))
                            return
        self._refresh_current_state_labels()

        callback = self._signal_handlers.get("on_toggle_position_pressed")
        if callback is not None:
            try:
                callback(object_name)
            except Exception as exc:
                self._set_feedback(phase="Position", state="error", error=str(exc))

    def _on_direction_toggled(self, object_name: str) -> None:
        self._refresh_current_state_labels()
        callback = self._signal_handlers.get("on_toggle_position")
        active = self._is_toggle_active(object_name)
        if callback is not None:
            try:
                callback(object_name, active)
            except Exception as exc:
                self._set_feedback(phase="Position", state="error", error=str(exc))
                return

        if not active:
            reset_callback = self._signal_handlers.get("on_toggle_position_reset")
            if reset_callback is not None:
                try:
                    reset_callback(object_name)
                except Exception as exc:
                    self._set_feedback(phase="Position", state="error", error=str(exc))

    def _on_direction_released(self, object_name: str) -> None:
        self._refresh_current_state_labels()
        return

    def _read_spin_int(self, object_name: str) -> int:
        return read_spin_int(self, object_name)

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
        except TypeError as exc:
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
        except TypeError as exc:
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
        except TypeError as exc:
            self._set_feedback(phase="ApplyMode", state="error", error=str(exc))

    def _on_slideshow_mode_toggled(self, widget: Any, mode: str) -> None:
        if hasattr(widget, "get_active") and not widget.get_active():
            return
        help_text = "Sequential rotates images."
        if mode == "random":
            help_text = "Random rotates images."
        self._set_label_text("lblSlideshowModeHelp", help_text)
        callback = self._signal_handlers.get("on_change_slideshow_mode")
        if callback is None:
            self.slideshow_mode = mode
            if not self._slideshow_running:
                self._slideshow_active_mode = mode
            self._set_feedback(phase="SlideshowMode", state="updated")
            return
        try:
            ok = callback(mode)
            if ok is False:
                self._set_feedback(phase="SlideshowMode", state="rejected", error="slideshow mode update rejected")
                return
            owner = self._get_handler_owner("on_change_slideshow_mode")
            if owner is not None:
                self._sync_slideshow_state_from_owner(owner)
                self._set_feedback(phase="SlideshowMode", state="updated")
                return
            self.slideshow_mode = mode
            if not self._slideshow_running:
                self._slideshow_active_mode = mode
            self._set_feedback(phase="SlideshowMode", state="updated")
        except TypeError as exc:
            self._set_feedback(phase="SlideshowMode", state="error", error=str(exc))

    def _on_save_clicked(self, *_args: Any) -> None:
        # P6 direction: Save As keeps chooser semantics, but fallback should not
        # depend on separate confirm/cancel controls.
        callback = self._signal_handlers.get("on_save_as")
        if callback is not None:
            try:
                callback()
            except Exception as exc:
                self._set_feedback(phase="SavePath", state="error", error=str(exc))
                return

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
        except TypeError as exc:
            self._set_feedback(phase="Apply", state="error", error=str(exc))

    def _on_settings_clicked(self, *_args: Any) -> None:
        on_settings_clicked(self, *_args)

    def _on_settings_apply_clicked(self, *_args: Any) -> None:
        on_settings_apply_clicked(self, *_args)

    def _on_settings_load_clicked(self, *_args: Any) -> None:
        on_settings_load_clicked(self, *_args)

    def _on_settings_save_clicked(self, *_args: Any) -> None:
        on_settings_save_clicked(self, *_args)

    def _on_settings_close_clicked(self, *_args: Any) -> None:
        on_settings_close_clicked(self, *_args)

    def _on_settings_window_delete_event(self) -> bool:
        return on_settings_window_delete_event(self)

    def _on_color_clicked(self, *_args: Any) -> None:
        on_color_clicked(self, *_args)

    def _on_about_clicked(self, *_args: Any) -> None:
        on_about_clicked(self, *_args)

    def _on_about_dialog_close_clicked(self, *_args: Any) -> None:
        on_about_dialog_close_clicked(self, *_args)

    def _on_about_window_delete_event(self) -> bool:
        return on_about_window_delete_event(self)

    def _close_about_dialog(self, destroyed: bool) -> None:
        close_about_dialog(self, destroyed)

    def _on_color_dialog_apply_clicked(self, *_args: Any) -> None:
        on_color_dialog_apply_clicked(self, *_args)

    def _on_color_dialog_cancel_clicked(self, *_args: Any) -> None:
        on_color_dialog_cancel_clicked(self, *_args)

    def _on_color_window_delete_event(self) -> bool:
        return on_color_window_delete_event(self)

    def _on_color_dialog_confirmed(self, color: str) -> None:
        on_color_dialog_confirmed(self, color)

    def _on_color_dialog_canceled(self, destroyed: bool) -> None:
        on_color_dialog_canceled(self, destroyed)

    def _handle_save_path_confirm(self, filename: str) -> None:
        handle_save_path_confirm(self, filename)

    def _handle_save_path_cancel(self) -> None:
        handle_save_path_cancel(self)

    def _on_native_save_path_confirmed(self) -> None:
        on_native_save_path_confirmed(self)

    def _on_native_save_path_canceled(self) -> None:
        on_native_save_path_canceled(self)


def load_gtk_runtime_signal_backend():
    """Return the current GTK runtime backend used for signal binding."""
    try:
        gi = importlib.import_module("gi")
        gi.require_version("Gtk", "3.0")
        gtk_module = importlib.import_module("gi.repository.Gtk")
    except (ImportError, ValueError) as exc:  # pragma: no cover - depends on host GTK runtime.
        raise RuntimeError(f"GTK backend unavailable: {exc}") from exc

    return GtkRuntimeSignalBackend(gtk_module)


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


def present_gtk_window(signal_backend, *, window_id: str = "main_window") -> bool:
    """Present the real GTK window and enter the main loop.

    Returns True when the target window object is found and shown.
    """
    try:
        gi = importlib.import_module("gi")
        gi.require_version("Gtk", "3.0")
        gtk_module = importlib.import_module("gi.repository.Gtk")
    except (ImportError, ValueError) as exc:  # pragma: no cover - depends on host GTK runtime.
        raise RuntimeError(f"GTK runtime unavailable: {exc}") from exc

    if not hasattr(signal_backend, "get_object"):
        raise TypeError("signal backend must provide get_object(name)")

    window = _resolve_window(signal_backend, window_id)
    if window is None:
        return False

    # Ensure the current runtime window can exit Gtk.main() by window close.
    if hasattr(window, "connect") and not getattr(window, "_harite_quit_hooked", False):

        def _on_delete_event(*_args):
            gtk_module.main_quit()
            return False

        window.connect("delete-event", _on_delete_event)
        setattr(window, "_harite_quit_hooked", True)

    if hasattr(window, "show_all"):
        window.show_all()
    if hasattr(window, "present"):
        window.present()

    gtk_module.main()
    return True

"""GTK backend loader for optional UI signal binding.

This adapter is intentionally optional. It should only be used in environments
where PyGObject/GTK is available.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


class _SaveDialogProxy:
    """Minimal file chooser-like object used by runtime fallback backend."""

    def __init__(self, on_filename_change: Callable[[str], None] | None = None) -> None:
        self._filename = ""
        self._visible = False
        self._on_filename_change = on_filename_change

    def set_filename(self, filename: str) -> None:
        self._filename = str(filename or "")
        if self._on_filename_change is not None:
            self._on_filename_change(self._filename)

    def get_filename(self) -> str:
        return self._filename

    def show(self) -> None:
        self._visible = True

    def hide(self) -> None:
        self._visible = False

    def is_visible(self) -> bool:
        return self._visible


class GtkRuntimeSignalBackend:
    """Minimal GTK runtime backend that does not require Glade parsing.

    This fallback keeps present/bind flows usable even when a legacy Glade
    resource cannot be consumed by Gtk.Builder at runtime.
    """

    def __init__(self, gtk_module: Any) -> None:
        self._gtk = gtk_module
        self._signal_handlers: dict[str, Callable[..., Any]] = {}
        self._effective_fixed = False
        self._effective_margins = (0, 0, 0, 0)
        self._effective_align = "center"
        self._effective_valign = "center"

        window = gtk_module.Window(title="Harite Studio")
        if hasattr(window, "set_resizable"):
            # P5-2 policy: modern desktop UX expects a resizable main window.
            window.set_resizable(True)
        if hasattr(window, "set_default_size"):
            window.set_default_size(960, 640)

        if hasattr(gtk_module, "Box") and hasattr(gtk_module, "Label"):
            root = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=8)
            root.set_border_width(10)

            # Row 0: top margin row (Glade hbox11 equivalent)
            top_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=8)
            root.pack_start(top_row, False, False, 0)

            top_spacer_l = gtk_module.Label(label="")
            top_row.pack_start(top_spacer_l, True, True, 0)

            top_margin_label = gtk_module.Label(label="上マージン(px)")
            if hasattr(top_margin_label, "set_xalign"):
                top_margin_label.set_xalign(0.0)
            top_row.pack_start(top_margin_label, False, False, 0)

            top_margin_spin = gtk_module.SpinButton()
            self._configure_spin_button(top_margin_spin, minimum=0, maximum=250, step=1, page=10)
            top_row.pack_start(top_margin_spin, False, False, 0)

            top_spacer_r = gtk_module.Label(label="")
            top_row.pack_start(top_spacer_r, True, True, 0)

            # Row 1: center body (Glade hbox2 equivalent)
            center_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=10)
            root.pack_start(center_row, True, True, 0)

            left_margin_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
            center_row.pack_start(left_margin_col, False, False, 0)

            left_margin_label = gtk_module.Label(label="左マージン(px)")
            if hasattr(left_margin_label, "set_xalign"):
                left_margin_label.set_xalign(0.0)
            left_margin_col.pack_start(left_margin_label, False, False, 0)

            left_margin_spin = gtk_module.SpinButton()
            self._configure_spin_button(left_margin_spin, minimum=0, maximum=500, step=1, page=10)
            left_margin_col.pack_start(left_margin_spin, False, False, 0)

            main_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
            center_row.pack_start(main_col, True, True, 0)

            title = gtk_module.Label(label="Wallpaper Optimizer")
            if hasattr(title, "set_xalign"):
                title.set_xalign(0.0)
            main_col.pack_start(title, False, False, 0)

            subtitle = gtk_module.Label(label="Glade-like layout (Phase5 P5-2)")
            if hasattr(subtitle, "set_xalign"):
                subtitle.set_xalign(0.0)
            main_col.pack_start(subtitle, False, False, 0)

            main_section_label = gtk_module.Label(label="Main")
            if hasattr(main_section_label, "set_xalign"):
                main_section_label.set_xalign(0.0)
            main_col.pack_start(main_section_label, False, False, 0)

            upper_toggle_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            main_col.pack_start(upper_toggle_row, False, False, 0)
            tgl_upper_l = gtk_module.ToggleButton(label="Top-L")
            tgl_upper_r = gtk_module.ToggleButton(label="Top-R")
            upper_toggle_row.pack_start(tgl_upper_l, False, False, 0)
            upper_toggle_row.pack_start(tgl_upper_r, False, False, 0)

            cross_center_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=12)
            main_col.pack_start(cross_center_row, False, False, 0)

            push_toggle_row_l = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            cross_center_row.pack_start(push_toggle_row_l, False, False, 0)
            tgl_push_left_l = gtk_module.ToggleButton(label="Left-L")
            tgl_push_right_l = gtk_module.ToggleButton(label="Right-L")
            btn_get_img_l = gtk_module.Button(label="Open-L")
            push_toggle_row_l.pack_start(tgl_push_left_l, False, False, 0)
            push_toggle_row_l.pack_start(btn_get_img_l, False, False, 0)
            push_toggle_row_l.pack_start(tgl_push_right_l, False, False, 0)

            push_toggle_row_r = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            cross_center_row.pack_start(push_toggle_row_r, False, False, 0)
            tgl_push_left_r = gtk_module.ToggleButton(label="Left-R")
            tgl_push_right_r = gtk_module.ToggleButton(label="Right-R")
            btn_get_img_r = gtk_module.Button(label="Open-R")
            push_toggle_row_r.pack_start(tgl_push_left_r, False, False, 0)
            push_toggle_row_r.pack_start(btn_get_img_r, False, False, 0)
            push_toggle_row_r.pack_start(tgl_push_right_r, False, False, 0)

            lower_toggle_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            main_col.pack_start(lower_toggle_row, False, False, 0)
            tgl_lower_l = gtk_module.ToggleButton(label="Bottom-L")
            tgl_lower_r = gtk_module.ToggleButton(label="Bottom-R")
            lower_toggle_row.pack_start(tgl_lower_l, False, False, 0)
            lower_toggle_row.pack_start(tgl_lower_r, False, False, 0)

            pick_state_label = gtk_module.Label(label="Picker: idle")
            if hasattr(pick_state_label, "set_xalign"):
                pick_state_label.set_xalign(0.0)
            main_col.pack_start(pick_state_label, False, False, 0)

            input_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            main_col.pack_start(input_row, False, False, 0)
            input_entry_l = gtk_module.Entry()
            input_entry_l.set_placeholder_text("/path/to/left_image_or_directory")
            btn_clr_path_l = gtk_module.Button(label="Clear-L")
            input_entry_r = gtk_module.Entry()
            input_entry_r.set_placeholder_text("/path/to/right_image_or_directory")
            btn_clr_path_r = gtk_module.Button(label="Clear-R")
            input_row.pack_start(input_entry_l, True, True, 0)
            input_row.pack_start(btn_clr_path_l, False, False, 0)
            input_row.pack_start(input_entry_r, True, True, 0)
            input_row.pack_start(btn_clr_path_r, False, False, 0)

            fixed_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            main_col.pack_start(fixed_row, False, False, 0)
            rad_fixed = gtk_module.RadioButton.new_with_label(None, "入替不可")
            rad_no_fixed = gtk_module.RadioButton.new_with_label_from_widget(rad_fixed, "入替可")
            if hasattr(rad_no_fixed, "set_active"):
                rad_no_fixed.set_active(True)
            fixed_row.pack_start(rad_fixed, False, False, 0)
            fixed_row.pack_start(rad_no_fixed, False, False, 0)

            optimize_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            main_col.pack_start(optimize_row, False, False, 0)
            optimize_section_label = gtk_module.Label(label="Optimize")
            if hasattr(optimize_section_label, "set_xalign"):
                optimize_section_label.set_xalign(0.0)
            optimize_row.pack_start(optimize_section_label, False, False, 0)
            optimize_btn = gtk_module.Button(label="Save")
            if hasattr(optimize_btn, "set_sensitive"):
                optimize_btn.set_sensitive(False)
            optimize_row.pack_start(optimize_btn, False, False, 0)
            optimize_modern_btn = gtk_module.Button(label="Optimize")
            if hasattr(optimize_modern_btn, "set_sensitive"):
                optimize_modern_btn.set_sensitive(False)
            optimize_row.pack_start(optimize_modern_btn, False, False, 0)
            optimize_result = gtk_module.Label(label="Optimize result: not-run")
            if hasattr(optimize_result, "set_xalign"):
                optimize_result.set_xalign(0.0)
            optimize_row.pack_start(optimize_result, True, True, 0)

            apply_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            main_col.pack_start(apply_row, False, False, 0)
            apply_section_label = gtk_module.Label(label="Apply")
            if hasattr(apply_section_label, "set_xalign"):
                apply_section_label.set_xalign(0.0)
            apply_row.pack_start(apply_section_label, False, False, 0)
            apply_btn = gtk_module.Button(label="Apply (dry-run)")
            if hasattr(apply_btn, "set_sensitive"):
                apply_btn.set_sensitive(False)
            apply_row.pack_start(apply_btn, False, False, 0)
            apply_target = gtk_module.Label(label="Apply target: not-ready")
            if hasattr(apply_target, "set_xalign"):
                apply_target.set_xalign(0.0)
            apply_row.pack_start(apply_target, True, True, 0)

            do_it_plan_label = gtk_module.Label(label="do-it: planned")
            if hasattr(do_it_plan_label, "set_xalign"):
                do_it_plan_label.set_xalign(0.0)
            main_col.pack_start(do_it_plan_label, False, False, 0)

            save_dialog_state_label = gtk_module.Label(label="SaveDialog: closed")
            if hasattr(save_dialog_state_label, "set_xalign"):
                save_dialog_state_label.set_xalign(0.0)
            main_col.pack_start(save_dialog_state_label, False, False, 0)

            priority_note_label = gtk_module.Label(
                label="Rule: fixed > margin > toggles"
            )
            if hasattr(priority_note_label, "set_xalign"):
                priority_note_label.set_xalign(0.0)
            main_col.pack_start(priority_note_label, False, False, 0)

            style_legend_label = gtk_module.Label(
                label="Style cues: secondary(about/help) | planned"
            )
            if hasattr(style_legend_label, "set_xalign"):
                style_legend_label.set_xalign(0.0)
            main_col.pack_start(style_legend_label, False, False, 0)

            current_state_section_label = gtk_module.Label(label="Current state")
            if hasattr(current_state_section_label, "set_xalign"):
                current_state_section_label.set_xalign(0.0)
            main_col.pack_start(current_state_section_label, False, False, 0)

            configured_section_label = gtk_module.Label(label="Configured")
            if hasattr(configured_section_label, "set_xalign"):
                configured_section_label.set_xalign(0.0)
            main_col.pack_start(configured_section_label, False, False, 0)

            current_fixed_label = gtk_module.Label(label="Configured fixed: off")
            if hasattr(current_fixed_label, "set_xalign"):
                current_fixed_label.set_xalign(0.0)
            main_col.pack_start(current_fixed_label, False, False, 0)

            current_margins_label = gtk_module.Label(label="Configured margins: 0,0,0,0")
            if hasattr(current_margins_label, "set_xalign"):
                current_margins_label.set_xalign(0.0)
            main_col.pack_start(current_margins_label, False, False, 0)

            current_left_label = gtk_module.Label(label="Configured L: align=center valign=center")
            if hasattr(current_left_label, "set_xalign"):
                current_left_label.set_xalign(0.0)
            main_col.pack_start(current_left_label, False, False, 0)

            current_right_label = gtk_module.Label(label="Configured R: align=center valign=center")
            if hasattr(current_right_label, "set_xalign"):
                current_right_label.set_xalign(0.0)
            main_col.pack_start(current_right_label, False, False, 0)

            effective_section_label = gtk_module.Label(label="Effective")
            if hasattr(effective_section_label, "set_xalign"):
                effective_section_label.set_xalign(0.0)
            main_col.pack_start(effective_section_label, False, False, 0)

            effective_fixed_label = gtk_module.Label(label="Effective fixed: off")
            if hasattr(effective_fixed_label, "set_xalign"):
                effective_fixed_label.set_xalign(0.0)
            main_col.pack_start(effective_fixed_label, False, False, 0)

            effective_margins_label = gtk_module.Label(label="Effective margins: 0,0,0,0")
            if hasattr(effective_margins_label, "set_xalign"):
                effective_margins_label.set_xalign(0.0)
            main_col.pack_start(effective_margins_label, False, False, 0)

            effective_placement_label = gtk_module.Label(label="Effective placement: align=center valign=center")
            if hasattr(effective_placement_label, "set_xalign"):
                effective_placement_label.set_xalign(0.0)
            main_col.pack_start(effective_placement_label, False, False, 0)

            right_margin_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
            center_row.pack_start(right_margin_col, False, False, 0)

            right_margin_label = gtk_module.Label(label="右マージン(px)")
            if hasattr(right_margin_label, "set_xalign"):
                right_margin_label.set_xalign(0.0)
            right_margin_col.pack_start(right_margin_label, False, False, 0)

            right_margin_spin = gtk_module.SpinButton()
            self._configure_spin_button(right_margin_spin, minimum=0, maximum=500, step=1, page=10)
            right_margin_col.pack_start(right_margin_spin, False, False, 0)

            # Row 2: bottom margin row (Glade hbox12 equivalent)
            bottom_margin_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=8)
            root.pack_start(bottom_margin_row, False, False, 0)
            btm_spacer_l = gtk_module.Label(label="")
            bottom_margin_row.pack_start(btm_spacer_l, True, True, 0)
            bottom_margin_label = gtk_module.Label(label="下マージン(px)")
            if hasattr(bottom_margin_label, "set_xalign"):
                bottom_margin_label.set_xalign(0.0)
            bottom_margin_row.pack_start(bottom_margin_label, False, False, 0)
            bottom_margin_spin = gtk_module.SpinButton()
            self._configure_spin_button(bottom_margin_spin, minimum=0, maximum=250, step=1, page=10)
            bottom_margin_row.pack_start(bottom_margin_spin, False, False, 0)
            btm_spacer_r = gtk_module.Label(label="")
            bottom_margin_row.pack_start(btm_spacer_r, True, True, 0)

            # Row 3: command bar (Glade hbox14 equivalent)
            command_section_label = gtk_module.Label(label="Commands")
            if hasattr(command_section_label, "set_xalign"):
                command_section_label.set_xalign(0.0)
            root.pack_start(command_section_label, False, False, 0)

            command_bar = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            root.pack_start(command_bar, False, False, 0)
            btn_setting = gtk_module.Button(label="Prefs")
            btn_set_color = gtk_module.Button(label="Color (planned)")
            save_dialog_proxy = _SaveDialogProxy(self._on_save_dialog_filename_changed)
            btn_open_save = gtk_module.Button(label="Save Confirm")
            if hasattr(btn_open_save, "set_sensitive"):
                btn_open_save.set_sensitive(False)
            btn_cancel_save = gtk_module.Button(label="Save Cancel")
            if hasattr(btn_cancel_save, "set_sensitive"):
                btn_cancel_save.set_sensitive(False)
            watch_label = gtk_module.Label(label="Watch (planned)")
            interval_spin = gtk_module.SpinButton()
            self._configure_spin_button(interval_spin, minimum=1, maximum=86400, step=1, page=10, initial=60)
            interval_label = gtk_module.Label(label="Interval (planned)")
            btn_daemonize = gtk_module.Button(label="Watch Start (planned)")
            btn_cancel_daemonize = gtk_module.Button(label="Watch Stop (planned)")
            btn_about = gtk_module.Button(label="About (secondary)")
            btn_help = gtk_module.Button(label="Help (secondary)")
            command_bar.pack_start(btn_setting, False, False, 0)
            command_bar.pack_start(btn_set_color, False, False, 0)
            command_bar.pack_start(btn_open_save, False, False, 0)
            command_bar.pack_start(btn_cancel_save, False, False, 0)
            command_bar.pack_start(watch_label, False, False, 0)
            command_bar.pack_start(interval_spin, False, False, 0)
            command_bar.pack_start(interval_label, False, False, 0)
            command_bar.pack_start(btn_daemonize, False, False, 0)
            command_bar.pack_start(btn_cancel_daemonize, False, False, 0)
            command_bar.pack_start(btn_about, False, False, 0)
            command_bar.pack_start(btn_help, False, False, 0)

            # Row 4: status row (Glade statusbar equivalent)
            status_row = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=2)
            root.pack_start(status_row, False, False, 0)
            flow_legend_label = gtk_module.Label(label="Flow: Compose -> Optimize -> Apply")
            if hasattr(flow_legend_label, "set_xalign"):
                flow_legend_label.set_xalign(0.0)
            status_row.pack_start(flow_legend_label, False, False, 0)
            status_label = gtk_module.Label(label="Status: ready")
            if hasattr(status_label, "set_xalign"):
                status_label.set_xalign(0.0)
            status_row.pack_start(status_label, False, False, 0)
            error_label = gtk_module.Label(label="Error: none")
            if hasattr(error_label, "set_xalign"):
                error_label.set_xalign(0.0)
            status_row.pack_start(error_label, False, False, 0)

            if hasattr(window, "add"):
                window.add(root)

            self._objects = {
                "WallPosit_MainWindow": window,
                "main_window": window,
                "window1": window,
                "boxRoot": root,
                "hbox11": top_row,
                "lblTopMergin": top_margin_label,
                "spnTopMergin": top_margin_spin,
                "hbox2": center_row,
                "vbox4": left_margin_col,
                "lblLMergin": left_margin_label,
                "spnLMergin": left_margin_spin,
                "lblTitle": title,
                "lblSubtitle": subtitle,
                "lblMainSection": main_section_label,
                "boxMainSection": main_col,
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
                "radFixed": rad_fixed,
                "radNoFixed": rad_no_fixed,
                "vbox5": right_margin_col,
                "lblRMergin": right_margin_label,
                "spnRMergin": right_margin_spin,
                "hbox12": bottom_margin_row,
                "lblBtmMergin": bottom_margin_label,
                "spnBtmMergin": bottom_margin_spin,
                "lblOptimizeSection": optimize_section_label,
                "boxOptimizeSection": optimize_row,
                "btnSave": optimize_btn,
                "btnOptimize": optimize_modern_btn,
                "lblOptimizeResult": optimize_result,
                "lblApplySection": apply_section_label,
                "boxApplySection": apply_row,
                "btnSetWall": apply_btn,
                "lblApplyTarget": apply_target,
                "lblDoItPlanned": do_it_plan_label,
                "lblSaveDialogState": save_dialog_state_label,
                "lblPriorityRule": priority_note_label,
                "lblStyleLegend": style_legend_label,
                "lblCurrentStateSection": current_state_section_label,
                "lblConfiguredSection": configured_section_label,
                "lblCurrentFixed": current_fixed_label,
                "lblCurrentMargins": current_margins_label,
                "lblCurrentStateL": current_left_label,
                "lblCurrentStateR": current_right_label,
                "lblEffectiveSection": effective_section_label,
                "lblEffectiveFixed": effective_fixed_label,
                "lblEffectiveMargins": effective_margins_label,
                "lblEffectivePlacement": effective_placement_label,
                "lblCommandSection": command_section_label,
                "hbox14": command_bar,
                "btnSetting": btn_setting,
                "btnSetColor": btn_set_color,
                "SaveWallpaperDialog": save_dialog_proxy,
                "btnOpenSave": btn_open_save,
                "btnCancelSave": btn_cancel_save,
                "lblWatchSection": watch_label,
                "spnInterval": interval_spin,
                "lblInterval": interval_label,
                "btnDaemonize": btn_daemonize,
                "btnCancelDaemonize": btn_cancel_daemonize,
                "btnAbout": btn_about,
                "btnHelp": btn_help,
                "statusbar": status_row,
                "lblFlowLegend": flow_legend_label,
                "lblStatus": status_label,
                "lblError": error_label,
            }

            for object_name, widget in self._objects.items():
                if hasattr(widget, "set_name"):
                    widget.set_name(object_name)
                elif not hasattr(widget, "get_name"):
                    setattr(widget, "name", object_name)

            # Why: fallback window must still exercise MainWindow handlers even when
            # legacy glade cannot be parsed at runtime.
            input_entry_l.connect("changed", self._on_input_changed)
            input_entry_r.connect("changed", self._on_input_changed)
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
            rad_fixed.connect("clicked", lambda *_args: self._on_fixed_selection(True))
            rad_no_fixed.connect("clicked", lambda *_args: self._on_fixed_selection(False))
            top_margin_spin.connect("value-changed", self._on_margin_changed)
            left_margin_spin.connect("value-changed", self._on_margin_changed)
            right_margin_spin.connect("value-changed", self._on_margin_changed)
            bottom_margin_spin.connect("value-changed", self._on_margin_changed)
            optimize_btn.connect("clicked", self._on_save_clicked)
            optimize_modern_btn.connect("clicked", self._on_optimize_clicked)
            apply_btn.connect("clicked", self._on_apply_clicked)
            btn_set_color.connect("clicked", self._on_color_clicked)
            btn_open_save.connect("clicked", self._on_save_dialog_confirm_clicked)
            btn_cancel_save.connect("clicked", self._on_save_dialog_cancel_clicked)
            self._refresh_current_state_labels()
        else:
            self._objects = {
                "WallPosit_MainWindow": window,
                "main_window": window,
                "window1": window,
            }

    def connect_signals(self, mapping: dict[str, Callable[..., Any]]) -> None:
        self._signal_handlers.update(mapping)

    def connect(self, handler_name: str, callback: Callable[..., Any]) -> None:
        self._signal_handlers[handler_name] = callback

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

    def _set_button_enabled(self, object_name: str, enabled: bool) -> None:
        button = self._objects.get(object_name)
        if button is not None and hasattr(button, "set_sensitive"):
            button.set_sensitive(bool(enabled))

    def _current_save_dialog_filename(self) -> str:
        dialog = self._objects.get("SaveWallpaperDialog")
        if dialog is None or not hasattr(dialog, "get_filename"):
            return ""
        return str(dialog.get_filename() or "").strip()

    def _update_save_dialog_action_buttons(self) -> None:
        opened = self._is_save_dialog_open()
        has_path = bool(self._current_save_dialog_filename())
        self._set_button_enabled("btnCancelSave", opened)
        self._set_button_enabled("btnOpenSave", opened and has_path)

    def _set_save_dialog_open_state(self, opened: bool, *, state_text: str | None = None) -> None:
        dialog = self._objects.get("SaveWallpaperDialog")
        if dialog is not None:
            if opened and hasattr(dialog, "show"):
                dialog.show()
            if not opened and hasattr(dialog, "hide"):
                dialog.hide()
        self._update_save_dialog_action_buttons()

        if state_text is not None:
            self._set_label_text("lblSaveDialogState", state_text)

    def _on_save_dialog_filename_changed(self, filename: str) -> None:
        if not self._is_save_dialog_open():
            return
        self._update_save_dialog_action_buttons()
        if str(filename or "").strip():
            self._set_label_text("lblSaveDialogState", "SaveDialog: open(path-ready)")
        else:
            self._set_label_text("lblSaveDialogState", "SaveDialog: open(path-required)")

    def _is_save_dialog_open(self) -> bool:
        dialog = self._objects.get("SaveWallpaperDialog")
        if dialog is None or not hasattr(dialog, "is_visible"):
            return False
        return bool(dialog.is_visible())

    def _on_input_changed(self, entry: Any) -> None:
        callback = self._signal_handlers.get("on_entPath_insert_text")
        text_l = ""
        text_r = ""

        entry_l = self._objects.get("entPathL")
        if entry_l is not None and hasattr(entry_l, "get_text"):
            text_l = str(entry_l.get_text() or "").strip()

        entry_r = self._objects.get("entPathR")
        if entry_r is not None and hasattr(entry_r, "get_text"):
            text_r = str(entry_r.get_text() or "").strip()

        input_values = [value for value in (text_l, text_r) if value]
        text = ",".join(input_values)
        has_input = bool(input_values)
        # Why: avoid invalid optimize/apply calls when the input field is empty.
        self._set_button_enabled("btnSave", has_input)
        self._set_button_enabled("btnOptimize", has_input)
        self._set_button_enabled("btnSetWall", False)
        if not has_input:
            self._set_save_dialog_open_state(False, state_text="SaveDialog: closed(input-reset)")
        self._set_label_text("lblOptimizeResult", "Optimize result: not-run")
        self._set_label_text("lblApplyTarget", "Apply target: not-ready")

        if callback is None:
            return

        try:
            callback(text)
            self._set_feedback(phase="Input", state="updated")
        except Exception as exc:
            self._set_feedback(phase="Input", state="failed", error=str(exc))

    def _on_pick_input_clicked(self, side: str) -> None:
        callback = self._signal_handlers.get("on_btnGetImg_clicked")
        entry_name = "entPathL" if side == "L" else "entPathR"
        entry = self._objects.get(entry_name)
        value = ""
        if entry is not None and hasattr(entry, "get_text"):
            value = str(entry.get_text() or "").strip()

        if not value:
            self._set_label_text("lblPickState", f"Open-{side}: planned(path-required)")
            self._set_feedback(phase=f"Open-{side}", state="planned", error="path input required")
            return

        if callback is None:
            self._set_label_text("lblPickState", f"Open-{side}: handler-missing")
            self._set_feedback(
                phase=f"Open-{side}",
                state="handler-missing",
                error="handler not connected",
            )
            return

        try:
            callback(value)
            self._set_label_text("lblPickState", f"Open-{side}: selected")
            self._set_feedback(phase=f"Open-{side}", state="selected")
        except Exception as exc:
            self._set_label_text("lblPickState", f"Open-{side}: error")
            self._set_feedback(phase=f"Open-{side}", state="error", error=str(exc))

    def _set_toggle_active(self, object_name: str, active: bool) -> None:
        toggle = self._objects.get(object_name)
        if toggle is None:
            return
        if hasattr(toggle, "set_active"):
            toggle.set_active(bool(active))
            return
        setattr(toggle, "active", bool(active))

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
        fixed_widget = self._objects.get("radFixed")
        fixed_enabled = False
        if fixed_widget is not None and hasattr(fixed_widget, "get_active"):
            fixed_enabled = bool(fixed_widget.get_active())

        left = self._read_spin_int("spnLMergin")
        right = self._read_spin_int("spnRMergin")
        top = self._read_spin_int("spnTopMergin")
        bottom = self._read_spin_int("spnBtmMergin")
        align_l, valign_l = self._current_side_state("L")
        align_r, valign_r = self._current_side_state("R")

        self._set_label_text("lblCurrentFixed", f"Configured fixed: {'on' if fixed_enabled else 'off'}")
        self._set_label_text("lblCurrentMargins", f"Configured margins: {left},{right},{top},{bottom}")
        self._set_label_text("lblCurrentStateL", f"Configured L: align={align_l} valign={valign_l}")
        self._set_label_text("lblCurrentStateR", f"Configured R: align={align_r} valign={valign_r}")
        self._set_label_text("lblEffectiveFixed", f"Effective fixed: {'on' if self._effective_fixed else 'off'}")
        effective_left, effective_right, effective_top, effective_bottom = self._effective_margins
        self._set_label_text(
            "lblEffectiveMargins",
            f"Effective margins: {effective_left},{effective_right},{effective_top},{effective_bottom}",
        )
        self._set_label_text(
            "lblEffectivePlacement",
            f"Effective placement: align={self._effective_align} valign={self._effective_valign}",
        )

    def _on_fixed_selection(self, fixed_enabled: bool) -> None:
        self._set_toggle_active("radFixed", fixed_enabled)
        self._set_toggle_active("radNoFixed", not fixed_enabled)
        self._effective_fixed = bool(fixed_enabled)
        self._refresh_current_state_labels()

        callback = self._signal_handlers.get("on_radFixed_toggled")
        if callback is not None:
            try:
                callback(bool(fixed_enabled))
            except Exception:
                pass

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
        self._refresh_current_state_labels()

        callback = self._signal_handlers.get("on_tglBtn_pressed")
        if callback is not None:
            widget = self._objects.get(object_name)
            try:
                callback(widget)
            except Exception:
                pass

    def _on_direction_toggled(self, object_name: str) -> None:
        if self._is_toggle_active(object_name):
            if "PushLeft" in object_name:
                self._effective_align = "left"
            elif "PushRight" in object_name:
                self._effective_align = "right"
            elif "Upper" in object_name:
                self._effective_valign = "top"
            elif "Lower" in object_name:
                self._effective_valign = "bottom"
        self._refresh_current_state_labels()
        callback = self._signal_handlers.get("on_tglBtn_toggled")
        if callback is None:
            return

        widget = self._objects.get(object_name)
        try:
            callback(widget)
        except Exception:
            pass

    def _on_direction_released(self, object_name: str) -> None:
        opposite_name = self._opposite_toggle_name(object_name)
        if not self._is_toggle_active(object_name) and (opposite_name is None or not self._is_toggle_active(opposite_name)):
            if "Push" in object_name:
                self._effective_align = "center"
            elif "Upper" in object_name or "Lower" in object_name:
                self._effective_valign = "center"
        self._refresh_current_state_labels()
        callback = self._signal_handlers.get("on_tglBtn_released")
        if callback is None:
            return

        widget = self._objects.get(object_name)
        try:
            callback(widget)
        except Exception:
            pass

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
        self._effective_margins = (
            self._read_spin_int("spnLMergin"),
            self._read_spin_int("spnRMergin"),
            self._read_spin_int("spnTopMergin"),
            self._read_spin_int("spnBtmMergin"),
        )
        self._refresh_current_state_labels()
        callback = self._signal_handlers.get("on_spnMergin_value_changed")

        if callback is None:
            self._set_feedback(phase="Margins", state="planned")
            return

        try:
            callback(widget)
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
            if ok:
                self._set_feedback(phase="Optimize", state="ok")
                self._set_label_text("lblOptimizeResult", "Optimize result: success")
                self._set_label_text("lblApplyTarget", "Apply target: ready")
            else:
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

    def _on_save_clicked(self, *_args: Any) -> None:
        # P5-3 split: Save opens save-dialog; generation continues on confirm.
        self._set_save_dialog_open_state(True, state_text="SaveDialog: open")

    def _on_optimize_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_btnOptimize_clicked")
        self._run_optimize_path(callback)

    def _on_apply_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_btnSetWall_clicked")
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
                self._set_feedback(phase="Apply", state="dry-run-ok")
                self._set_label_text("lblApplyTarget", "Apply target: consumed")
            else:
                self._set_feedback(
                    phase="Apply",
                    state="dry-run-failed",
                    error="apply returned false",
                )
        except Exception as exc:
            self._set_feedback(phase="Apply", state="error", error=str(exc))

    def _on_color_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_btnSetColor_clicked")
        if callback is None:
            self._set_feedback(phase="Color", state="planned")
            return
        try:
            callback()
            self._set_feedback(phase="Color", state="planned")
        except Exception as exc:
            self._set_feedback(phase="Color", state="error", error=str(exc))

    def _on_save_dialog_confirm_clicked(self, *_args: Any) -> None:
        if not self._is_save_dialog_open():
            self._set_label_text("lblSaveDialogState", "SaveDialog: closed")
            self._set_feedback(phase="SaveDialog", state="ignored-closed")
            return
        callback = self._signal_handlers.get("on_btnOpenSave_clicked")
        if callback is None:
            self._set_feedback(phase="SaveDialog", state="handler-missing", error="handler not connected")
            return
        try:
            dialog = self._objects.get("SaveWallpaperDialog")
            filename = ""
            if dialog is not None and hasattr(dialog, "get_filename"):
                filename = str(dialog.get_filename() or "").strip()
            if not filename:
                self._set_label_text("lblSaveDialogState", "SaveDialog: open(path-required)")
                self._set_feedback(phase="SaveDialog", state="confirm-pending-path", error="save path is required")
                return
            ok = callback(dialog)
            if ok:
                self._set_save_dialog_open_state(False, state_text="SaveDialog: closed(confirm)")
                self._set_feedback(phase="SaveDialog", state="confirm-ok")
            else:
                self._set_feedback(phase="SaveDialog", state="confirm-failed", error="confirm returned false")
        except Exception as exc:
            self._set_feedback(phase="SaveDialog", state="error", error=str(exc))

    def _on_save_dialog_cancel_clicked(self, *_args: Any) -> None:
        if not self._is_save_dialog_open():
            self._set_label_text("lblSaveDialogState", "SaveDialog: closed")
            self._set_feedback(phase="SaveDialog", state="ignored-closed")
            return
        callback = self._signal_handlers.get("on_btnCancelSave_clicked")
        if callback is None:
            self._set_feedback(phase="SaveDialog", state="handler-missing", error="handler not connected")
            return
        try:
            ok = callback()
            if ok:
                self._set_save_dialog_open_state(False, state_text="SaveDialog: closed(cancel)")
                self._set_feedback(phase="SaveDialog", state="cancel-ok")
            else:
                self._set_feedback(phase="SaveDialog", state="cancel-failed", error="cancel returned false")
        except Exception as exc:
            self._set_feedback(phase="SaveDialog", state="error", error=str(exc))


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
    for candidate in ("main_window", "window1"):
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

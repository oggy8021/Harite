from __future__ import annotations

from typing import Any

from harite.gui.adapters.gtk_layout_builders import set_button_icon_if_supported, set_xalign_if_supported


def build_action_cluster_section(gtk_module: Any, compose_grid: Any, *, default_apply_mode: str) -> dict[str, Any]:
    action_cluster_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=18)
    optimize_group = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
    apply_group = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
    if hasattr(compose_grid, "attach"):
        compose_grid.attach(action_cluster_row, 0, 2, 2, 1)

    optimize_section_label = gtk_module.Label(label="Optimize")
    set_xalign_if_supported(optimize_section_label)
    optimize_group.pack_start(optimize_section_label, False, False, 0)

    optimize_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
    optimize_group.pack_start(optimize_row, False, False, 0)
    optimize_modern_btn = gtk_module.Button(label="Optimize")
    if hasattr(optimize_modern_btn, "set_sensitive"):
        optimize_modern_btn.set_sensitive(False)
    set_button_icon_if_supported(gtk_module, optimize_modern_btn, "icons", "lucide", "image.svg")
    optimize_row.pack_start(optimize_modern_btn, False, False, 0)
    optimize_result = gtk_module.Label(label="Optimize result: not-run")
    set_xalign_if_supported(optimize_result)
    optimize_row.pack_start(optimize_result, True, True, 0)

    apply_section_label = gtk_module.Label(label="Apply")
    set_xalign_if_supported(apply_section_label)
    apply_group.pack_start(apply_section_label, False, False, 0)

    apply_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
    apply_group.pack_start(apply_row, False, False, 0)
    apply_btn = gtk_module.Button(label="Apply")
    if hasattr(apply_btn, "set_sensitive"):
        apply_btn.set_sensitive(False)
    set_button_icon_if_supported(gtk_module, apply_btn, "icons", "lucide", "wallpaper.svg")
    apply_row.pack_start(apply_btn, False, False, 0)
    apply_target = gtk_module.Label(label="Apply target: not-ready")
    set_xalign_if_supported(apply_target)
    apply_row.pack_start(apply_target, True, True, 0)

    apply_mode_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
    apply_group.pack_start(apply_mode_row, False, False, 0)
    apply_mode_help_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
    apply_group.pack_start(apply_mode_help_row, False, False, 0)
    rad_apply_single = gtk_module.RadioButton.new_with_label(None, "No Split")
    rad_apply_per_monitor = gtk_module.RadioButton.new_with_label_from_widget(rad_apply_single, "Auto-Split")
    if default_apply_mode == "per-monitor-auto-split":
        if hasattr(rad_apply_per_monitor, "set_active"):
            rad_apply_per_monitor.set_active(True)
        apply_mode_help_text = "Split the optimized image and apply per display."
    else:
        if hasattr(rad_apply_single, "set_active"):
            rad_apply_single.set_active(True)
        apply_mode_help_text = "Apply the optimized image as a single file."
    apply_mode_label = gtk_module.Label(label=apply_mode_help_text)
    set_xalign_if_supported(apply_mode_label)
    apply_mode_row.pack_start(rad_apply_per_monitor, False, False, 0)
    apply_mode_row.pack_start(rad_apply_single, False, False, 0)
    apply_mode_help_row.pack_start(apply_mode_label, True, True, 0)

    preview_group = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
    action_cluster_row.pack_start(preview_group, False, False, 0)

    action_cluster_spacer = gtk_module.Label(label="")
    action_cluster_row.pack_start(action_cluster_spacer, True, True, 0)
    action_cluster_row.pack_start(optimize_group, False, False, 0)
    action_cluster_row.pack_start(apply_group, False, False, 0)

    preview_section_label = gtk_module.Label(label="Preview")
    set_xalign_if_supported(preview_section_label)
    preview_group.pack_start(preview_section_label, False, False, 0)

    preview_images_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
    preview_group.pack_start(preview_images_row, False, False, 0)

    preview_left_box = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=4)
    preview_right_box = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=4)
    preview_images_row.pack_start(preview_left_box, False, False, 0)
    preview_images_row.pack_start(preview_right_box, False, False, 0)

    preview_left_assignment = gtk_module.Label(label="L display <- -")
    set_xalign_if_supported(preview_left_assignment)
    preview_left_box.pack_start(preview_left_assignment, False, False, 0)

    preview_right_assignment = gtk_module.Label(label="R display <- -")
    set_xalign_if_supported(preview_right_assignment)
    preview_right_box.pack_start(preview_right_assignment, False, False, 0)

    preview_left = gtk_module.Image() if hasattr(gtk_module, "Image") else gtk_module.Label(label="Preview L: not-ready")
    preview_right = gtk_module.Image() if hasattr(gtk_module, "Image") else gtk_module.Label(label="Preview R: not-ready")
    if hasattr(preview_left, "set_size_request"):
        preview_left.set_size_request(160, 90)
    if hasattr(preview_right, "set_size_request"):
        preview_right.set_size_request(160, 90)
    preview_left_box.pack_start(preview_left, False, False, 0)
    preview_right_box.pack_start(preview_right, False, False, 0)

    preview_left_result = gtk_module.Label(label="Result: not-ready")
    set_xalign_if_supported(preview_left_result)
    preview_left_box.pack_start(preview_left_result, False, False, 0)

    preview_right_result = gtk_module.Label(label="Result: not-ready")
    set_xalign_if_supported(preview_right_result)
    preview_right_box.pack_start(preview_right_result, False, False, 0)

    preview_state_label = gtk_module.Label(label="Preview: not-ready")
    set_xalign_if_supported(preview_state_label)
    preview_group.pack_start(preview_state_label, False, False, 0)

    preview_source_label = gtk_module.Label(label="Preview source: -")
    set_xalign_if_supported(preview_source_label)
    preview_group.pack_start(preview_source_label, False, False, 0)

    preview_assist_label = gtk_module.Label(label="Assist: not-ready")
    set_xalign_if_supported(preview_assist_label)
    preview_group.pack_start(preview_assist_label, False, False, 0)

    return {
        "action_cluster_row": action_cluster_row,
        "optimize_group": optimize_group,
        "optimize_section_label": optimize_section_label,
        "optimize_row": optimize_row,
        "optimize_modern_btn": optimize_modern_btn,
        "optimize_result": optimize_result,
        "apply_group": apply_group,
        "apply_section_label": apply_section_label,
        "apply_row": apply_row,
        "apply_btn": apply_btn,
        "apply_target": apply_target,
        "rad_apply_single": rad_apply_single,
        "rad_apply_per_monitor": rad_apply_per_monitor,
        "apply_mode_label": apply_mode_label,
        "preview_group": preview_group,
        "preview_images_row": preview_images_row,
        "preview_left": preview_left,
        "preview_right": preview_right,
        "preview_left_assignment": preview_left_assignment,
        "preview_right_assignment": preview_right_assignment,
        "preview_left_result": preview_left_result,
        "preview_right_result": preview_right_result,
        "preview_state_label": preview_state_label,
        "preview_source_label": preview_source_label,
        "preview_assist_label": preview_assist_label,
        "preview_section_label": preview_section_label,
    }


def build_main_tab_section(gtk_module: Any) -> dict[str, Any]:
    main_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=12)
    main_section_label = gtk_module.Label(label="Main")

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

    set_button_icon_if_supported(gtk_module, tgl_upper_l, "icons", "lucide", "arrow-up.svg")
    set_button_icon_if_supported(gtk_module, tgl_upper_r, "icons", "lucide", "arrow-up.svg")
    set_button_icon_if_supported(gtk_module, tgl_lower_l, "icons", "lucide", "arrow-down.svg")
    set_button_icon_if_supported(gtk_module, tgl_lower_r, "icons", "lucide", "arrow-down.svg")
    set_button_icon_if_supported(gtk_module, tgl_push_left_l, "icons", "lucide", "arrow-left.svg")
    set_button_icon_if_supported(gtk_module, tgl_push_right_l, "icons", "lucide", "arrow-right.svg")
    set_button_icon_if_supported(gtk_module, btn_get_img_l, "icons", "lucide", "folder-open.svg")
    set_button_icon_if_supported(gtk_module, tgl_push_left_r, "icons", "lucide", "arrow-left.svg")
    set_button_icon_if_supported(gtk_module, tgl_push_right_r, "icons", "lucide", "arrow-right.svg")
    set_button_icon_if_supported(gtk_module, btn_get_img_r, "icons", "lucide", "folder-open.svg")

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
    set_xalign_if_supported(input_entry_l)
    btn_clr_path_l = gtk_module.Button(label="Clear-L")
    set_button_icon_if_supported(gtk_module, btn_clr_path_l, "icons", "lucide", "folder-x.svg")
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
    set_xalign_if_supported(input_entry_r)
    btn_clr_path_r = gtk_module.Button(label="Clear-R")
    set_button_icon_if_supported(gtk_module, btn_clr_path_r, "icons", "lucide", "folder-x.svg")
    input_row_r.pack_start(input_entry_r, True, True, 0)
    input_row_r.pack_start(btn_clr_path_r, False, False, 0)
    if hasattr(compose_grid, "attach"):
        compose_grid.attach(input_row_r, 1, 1, 1, 1)

    pick_state_label = gtk_module.Label(label="")
    set_xalign_if_supported(pick_state_label)

    return {
        "main_col": main_col,
        "main_section_label": main_section_label,
        "compose_grid": compose_grid,
        "left_display_grid": left_display_grid,
        "right_display_grid": right_display_grid,
        "tgl_upper_l": tgl_upper_l,
        "tgl_upper_r": tgl_upper_r,
        "tgl_lower_l": tgl_lower_l,
        "tgl_lower_r": tgl_lower_r,
        "tgl_push_left_l": tgl_push_left_l,
        "tgl_push_right_l": tgl_push_right_l,
        "btn_get_img_l": btn_get_img_l,
        "tgl_push_left_r": tgl_push_left_r,
        "tgl_push_right_r": tgl_push_right_r,
        "btn_get_img_r": btn_get_img_r,
        "input_row_l": input_row_l,
        "input_entry_l": input_entry_l,
        "btn_clr_path_l": btn_clr_path_l,
        "input_row_r": input_row_r,
        "input_entry_r": input_entry_r,
        "btn_clr_path_r": btn_clr_path_r,
        "pick_state_label": pick_state_label,
    }


def build_runtime_state_labels(gtk_module: Any) -> dict[str, Any]:
    do_it_plan_label = gtk_module.Label(label="Debug: apply is immediate")
    set_xalign_if_supported(do_it_plan_label)

    save_path_state_label = gtk_module.Label(label="Save path: idle")
    set_xalign_if_supported(save_path_state_label)

    save_target_label = gtk_module.Label(label="Save target: not-selected")
    set_xalign_if_supported(save_target_label)

    priority_note_label = gtk_module.Label(
        label="Rule: margins define area; align/valign act inside it"
    )
    set_xalign_if_supported(priority_note_label)

    style_legend_label = gtk_module.Label(label="Current behavior: margins are global to the composite canvas")
    set_xalign_if_supported(style_legend_label)

    current_state_section_label = gtk_module.Label(label="Main Window Current alignment:")
    set_xalign_if_supported(current_state_section_label)

    current_margins_label = gtk_module.Label(label="margins=0,0,0,0")
    set_xalign_if_supported(current_margins_label)

    current_left_label = gtk_module.Label(label="L: align=center valign=center")
    set_xalign_if_supported(current_left_label)

    current_right_label = gtk_module.Label(label="R: align=center valign=center")
    set_xalign_if_supported(current_right_label)

    return {
        "do_it_plan_label": do_it_plan_label,
        "save_path_state_label": save_path_state_label,
        "save_target_label": save_target_label,
        "priority_note_label": priority_note_label,
        "style_legend_label": style_legend_label,
        "current_state_section_label": current_state_section_label,
        "current_margins_label": current_margins_label,
        "current_left_label": current_left_label,
        "current_right_label": current_right_label,
    }


def build_primary_margin_controls(gtk_module: Any, *, configure_spin_button: Any) -> dict[str, Any]:
    top_margin_label = gtk_module.Label(label="Top margin (px)")
    set_xalign_if_supported(top_margin_label)
    top_margin_spin = gtk_module.SpinButton()
    configure_spin_button(top_margin_spin, minimum=0, maximum=250, step=1, page=10)

    left_margin_label = gtk_module.Label(label="Left margin (px)")
    set_xalign_if_supported(left_margin_label)
    left_margin_spin = gtk_module.SpinButton()
    configure_spin_button(left_margin_spin, minimum=0, maximum=500, step=1, page=10)

    return {
        "top_margin_label": top_margin_label,
        "top_margin_spin": top_margin_spin,
        "left_margin_label": left_margin_label,
        "left_margin_spin": left_margin_spin,
    }


def build_watch_tab_section(gtk_module: Any, *, configure_spin_button: Any) -> dict[str, Any]:
    watch_tab_box = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=16)
    watch_label = gtk_module.Label(label="Watch")
    set_xalign_if_supported(watch_label)
    watch_tab_title = gtk_module.Label(label="Watch (stopped)")
    set_xalign_if_supported(watch_tab_title)
    watch_tab_box.pack_start(watch_label, False, False, 0)

    watch_srcdir_shell = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=0)
    watch_tab_box.pack_start(watch_srcdir_shell, False, False, 0)
    watch_srcdir_left_spacer = gtk_module.Label(label="")
    watch_srcdir_shell.pack_start(watch_srcdir_left_spacer, True, True, 0)
    watch_srcdir_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=48)
    watch_srcdir_shell.pack_start(watch_srcdir_row, False, False, 0)
    watch_srcdir_right_spacer = gtk_module.Label(label="")
    watch_srcdir_shell.pack_start(watch_srcdir_right_spacer, True, True, 0)
    btn_open_srcdir_l = gtk_module.Button(label="Srcdir-L")
    btn_open_srcdir_r = gtk_module.Button(label="Srcdir-R")
    set_button_icon_if_supported(gtk_module, btn_open_srcdir_l, "icons", "lucide", "folder-open.svg")
    set_button_icon_if_supported(gtk_module, btn_open_srcdir_r, "icons", "lucide", "folder-open.svg")
    watch_srcdir_row.pack_start(btn_open_srcdir_l, False, False, 0)
    watch_srcdir_row.pack_start(btn_open_srcdir_r, False, False, 0)

    watch_controls_shell = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
    watch_tab_box.pack_start(watch_controls_shell, False, False, 0)
    watch_controls_left_spacer = gtk_module.Label(label="")
    watch_controls_shell.pack_start(watch_controls_left_spacer, True, True, 0)
    watch_controls_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
    watch_controls_shell.pack_start(watch_controls_row, False, False, 0)
    watch_controls_right_spacer = gtk_module.Label(label="")
    watch_controls_shell.pack_start(watch_controls_right_spacer, True, True, 0)

    interval_spin = gtk_module.SpinButton()
    configure_spin_button(interval_spin, minimum=1, maximum=86400, step=1, page=10, initial=60)
    interval_label = gtk_module.Label(label="Interval")
    btn_daemonize = gtk_module.Button(label="Watch Start")
    btn_cancel_daemonize = gtk_module.Button(label="Watch Stop")
    set_button_icon_if_supported(gtk_module, btn_daemonize, "icons", "lucide", "play.svg")
    set_button_icon_if_supported(gtk_module, btn_cancel_daemonize, "icons", "lucide", "pause.svg")
    watch_controls_row.pack_start(interval_label, False, False, 0)
    watch_controls_row.pack_start(interval_spin, False, False, 0)
    watch_controls_row.pack_start(btn_daemonize, False, False, 0)
    watch_controls_row.pack_start(btn_cancel_daemonize, False, False, 0)

    watch_detail_row = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=2)
    watch_tab_box.pack_start(watch_detail_row, False, False, 0)
    watch_sources_label = gtk_module.Label(label="Watch srcdirs: L=- | R=-")
    set_xalign_if_supported(watch_sources_label)
    watch_detail_row.pack_start(watch_sources_label, False, False, 0)
    watch_current_label = gtk_module.Label(label="Watch current: idle")
    set_xalign_if_supported(watch_current_label)
    watch_detail_row.pack_start(watch_current_label, False, False, 0)
    watch_output_label = gtk_module.Label(label="Watch output: .")
    set_xalign_if_supported(watch_output_label)
    watch_detail_row.pack_start(watch_output_label, False, False, 0)

    return {
        "watch_tab_box": watch_tab_box,
        "watch_label": watch_label,
        "watch_tab_title": watch_tab_title,
        "watch_controls_row": watch_controls_row,
        "watch_detail_row": watch_detail_row,
        "btn_open_srcdir_l": btn_open_srcdir_l,
        "btn_open_srcdir_r": btn_open_srcdir_r,
        "interval_spin": interval_spin,
        "interval_label": interval_label,
        "btn_daemonize": btn_daemonize,
        "btn_cancel_daemonize": btn_cancel_daemonize,
        "watch_sources_label": watch_sources_label,
        "watch_current_label": watch_current_label,
        "watch_output_label": watch_output_label,
    }


def build_margins_tab_section(
    gtk_module: Any,
    *,
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
    configure_spin_button: Any,
    apply_margin_text_widget_style: Any,
) -> dict[str, Any]:
    margins_tab_box = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=12)
    margins_section_label = gtk_module.Label(label="")
    set_xalign_if_supported(margins_section_label)

    margins_layout_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=12)
    margins_tab_box.pack_start(margins_layout_col, False, False, 0)

    current_state_box = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
    current_state_box.pack_start(current_state_section_label, False, False, 0)
    current_state_box.pack_start(current_margins_label, False, False, 0)
    current_state_box.pack_start(current_left_label, False, False, 0)
    current_state_box.pack_start(current_right_label, False, False, 0)

    current_state_title_display = gtk_module.Label(label="Main Window Current alignment:")
    set_xalign_if_supported(current_state_title_display)
    current_state_summary_display = gtk_module.Label(label="align=center,center/center,center")
    set_xalign_if_supported(current_state_summary_display)

    top_margin_box = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
    top_margin_box.pack_start(top_margin_label, False, False, 0)
    top_margin_box.pack_start(top_margin_spin, False, False, 0)
    top_margin_shell = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=0)
    top_margin_shell_left = gtk_module.Label(label="")
    top_margin_shell_right = gtk_module.Label(label="")
    top_margin_shell.pack_start(top_margin_shell_left, True, True, 0)
    top_margin_shell.pack_start(top_margin_box, False, False, 0)
    top_margin_shell.pack_start(top_margin_shell_right, True, True, 0)

    left_margin_box = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
    left_margin_box.pack_start(left_margin_label, False, False, 0)
    left_margin_box.pack_start(left_margin_spin, False, False, 0)

    right_margin_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
    right_margin_label = gtk_module.Label(label="Right margin (px)")
    set_xalign_if_supported(right_margin_label)
    right_margin_spin = gtk_module.SpinButton()
    configure_spin_button(right_margin_spin, minimum=0, maximum=500, step=1, page=10)
    right_margin_box = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
    right_margin_box.pack_start(right_margin_label, False, False, 0)
    right_margin_box.pack_start(right_margin_spin, False, False, 0)

    bottom_margin_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=8)
    bottom_margin_label = gtk_module.Label(label="Bottom margin (px)")
    set_xalign_if_supported(bottom_margin_label)
    bottom_margin_spin = gtk_module.SpinButton()
    configure_spin_button(bottom_margin_spin, minimum=0, maximum=250, step=1, page=10)
    bottom_margin_box = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
    bottom_margin_box.pack_start(bottom_margin_label, False, False, 0)
    bottom_margin_box.pack_start(bottom_margin_spin, False, False, 0)
    bottom_margin_shell = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=0)
    bottom_margin_shell_left = gtk_module.Label(label="")
    bottom_margin_shell_right = gtk_module.Label(label="")
    bottom_margin_shell.pack_start(bottom_margin_shell_left, True, True, 0)
    bottom_margin_shell.pack_start(bottom_margin_box, False, False, 0)
    bottom_margin_shell.pack_start(bottom_margin_shell_right, True, True, 0)

    center_stack = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=8)

    center_state_shell = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=0)
    center_state_left = gtk_module.Label(label="")
    center_state_right = gtk_module.Label(label="")
    center_state_display_box = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=2)
    center_state_display_box.pack_start(current_state_title_display, False, False, 0)
    center_state_display_box.pack_start(current_state_summary_display, False, False, 0)
    center_state_shell.pack_start(center_state_left, True, True, 0)
    center_state_shell.pack_start(center_state_display_box, False, False, 0)
    center_state_shell.pack_start(center_state_right, True, True, 0)
    center_stack.pack_start(center_state_shell, False, False, 0)

    margin_text_mode_block = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
    center_stack.pack_start(margin_text_mode_block, False, False, 0)
    margin_text_mode_label = gtk_module.Label(label="embed pattern:")
    set_xalign_if_supported(margin_text_mode_label)
    margin_text_mode_block.pack_start(margin_text_mode_label, False, False, 0)

    margin_text_mode_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
    margin_text_mode_block.pack_start(margin_text_mode_row, False, False, 0)
    margin_text_mode_off = gtk_module.RadioButton.new_with_label(None, "Off")
    margin_text_mode_settings = gtk_module.RadioButton.new_with_label_from_widget(margin_text_mode_off, "Settings")
    margin_text_mode_text = gtk_module.RadioButton.new_with_label_from_widget(margin_text_mode_off, "Text only")
    margin_text_mode_both = gtk_module.RadioButton.new_with_label_from_widget(margin_text_mode_off, "Both")
    if hasattr(margin_text_mode_off, "set_active"):
        margin_text_mode_off.set_active(True)
    margin_text_mode_row.pack_start(margin_text_mode_off, False, False, 0)
    margin_text_mode_row.pack_start(margin_text_mode_settings, False, False, 0)
    margin_text_mode_row.pack_start(margin_text_mode_text, False, False, 0)
    margin_text_mode_row.pack_start(margin_text_mode_both, False, False, 0)

    margin_text_tabs = gtk_module.Notebook()
    if hasattr(margin_text_tabs, "set_hexpand"):
        margin_text_tabs.set_hexpand(True)
    if hasattr(margin_text_tabs, "set_vexpand"):
        margin_text_tabs.set_vexpand(True)
    center_stack.pack_start(margin_text_tabs, True, True, 0)

    margin_settings_page = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
    margin_settings_preview_label = gtk_module.Label(label="resolution=-")
    set_xalign_if_supported(margin_settings_preview_label)
    if hasattr(margin_settings_preview_label, "set_selectable"):
        margin_settings_preview_label.set_selectable(True)
    if hasattr(margin_settings_preview_label, "set_line_wrap"):
        margin_settings_preview_label.set_line_wrap(True)
    margin_settings_page.pack_start(margin_settings_preview_label, False, False, 0)

    margin_text_page = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
    margin_text_section_label = gtk_module.Label(label="Margin text")
    set_xalign_if_supported(margin_text_section_label)
    margin_text_entry = gtk_module.TextView() if hasattr(gtk_module, "TextView") else gtk_module.Entry()
    if hasattr(margin_text_entry, "set_wrap_mode") and hasattr(gtk_module, "WrapMode"):
        margin_text_entry.set_wrap_mode(gtk_module.WrapMode.WORD_CHAR)
    if hasattr(margin_text_entry, "set_placeholder_text"):
        margin_text_entry.set_placeholder_text("Up to 5 lines of margin text")
    if hasattr(margin_text_entry, "set_size_request"):
        margin_text_entry.set_size_request(460, 140)
    if hasattr(margin_text_entry, "set_editable"):
        margin_text_entry.set_editable(False)
    if hasattr(margin_text_entry, "set_left_margin"):
        margin_text_entry.set_left_margin(8)
    if hasattr(margin_text_entry, "set_right_margin"):
        margin_text_entry.set_right_margin(8)
    if hasattr(margin_text_entry, "set_pixels_above_lines"):
        margin_text_entry.set_pixels_above_lines(2)
    if hasattr(margin_text_entry, "set_pixels_below_lines"):
        margin_text_entry.set_pixels_below_lines(2)
    margin_text_shell = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=0)
    if hasattr(margin_text_shell, "set_border_width"):
        margin_text_shell.set_border_width(2)
    if hasattr(gtk_module, "ScrolledWindow"):
        margin_text_scroller = gtk_module.ScrolledWindow()
        if hasattr(margin_text_scroller, "set_size_request"):
            margin_text_scroller.set_size_request(460, 140)
        if hasattr(margin_text_scroller, "add"):
            margin_text_scroller.add(margin_text_entry)
        margin_text_shell.pack_start(margin_text_scroller, True, True, 0)
    else:
        margin_text_shell.pack_start(margin_text_entry, True, True, 0)
    margin_text_page.pack_start(margin_text_shell, True, True, 0)
    apply_margin_text_widget_style(gtk_module, margin_text_shell, margin_text_entry)

    settings_tab_label = gtk_module.Label(label="Settings")
    text_tab_label = gtk_module.Label(label="Text")
    margin_text_tabs.append_page(margin_settings_page, settings_tab_label)
    margin_text_tabs.append_page(margin_text_page, text_tab_label)

    margin_position_shell = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=4)
    margin_position_label = gtk_module.Label(label="Position:")
    set_xalign_if_supported(margin_position_label)
    margin_position_shell.pack_start(margin_position_label, False, False, 0)
    margin_position_left_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
    margin_position_left_label = gtk_module.Label(label="Left:")
    set_xalign_if_supported(margin_position_left_label)
    margin_position_left_top = gtk_module.RadioButton.new_with_label(None, "Top")
    margin_position_left_bottom = gtk_module.RadioButton.new_with_label_from_widget(margin_position_left_top, "Bottom")
    margin_position_left_shell = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=0)
    margin_position_left_shell_left = gtk_module.Label(label="")
    margin_position_left_shell_right = gtk_module.Label(label="")
    margin_position_right_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
    margin_position_right_label = gtk_module.Label(label="Right:")
    set_xalign_if_supported(margin_position_right_label)
    margin_position_right_top = gtk_module.RadioButton.new_with_label_from_widget(margin_position_left_top, "Top")
    margin_position_right_bottom = gtk_module.RadioButton.new_with_label_from_widget(margin_position_left_top, "Bottom")
    margin_position_right_shell = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=0)
    margin_position_right_shell_left = gtk_module.Label(label="")
    margin_position_right_shell_right = gtk_module.Label(label="")
    if hasattr(margin_position_right_bottom, "set_active"):
        margin_position_right_bottom.set_active(True)
    margin_position_left_row.pack_start(margin_position_left_label, False, False, 0)
    margin_position_left_row.pack_start(margin_position_left_top, False, False, 0)
    margin_position_left_row.pack_start(margin_position_left_bottom, False, False, 0)
    margin_position_left_shell.pack_start(margin_position_left_shell_left, True, True, 0)
    margin_position_left_shell.pack_start(margin_position_left_row, False, False, 0)
    margin_position_left_shell.pack_start(margin_position_left_shell_right, True, True, 0)
    margin_position_right_row.pack_start(margin_position_right_label, False, False, 0)
    margin_position_right_row.pack_start(margin_position_right_top, False, False, 0)
    margin_position_right_row.pack_start(margin_position_right_bottom, False, False, 0)
    margin_position_right_shell.pack_start(margin_position_right_shell_left, True, True, 0)
    margin_position_right_shell.pack_start(margin_position_right_row, False, False, 0)
    margin_position_right_shell.pack_start(margin_position_right_shell_right, True, True, 0)
    margin_position_shell.pack_start(margin_position_left_shell, False, False, 0)
    margin_position_shell.pack_start(margin_position_right_shell, False, False, 0)

    margin_text_max_lines_spin = gtk_module.SpinButton()
    configure_spin_button(margin_text_max_lines_spin, minimum=1, maximum=20, step=1, page=5, initial=3)
    margin_text_hint = gtk_module.Label(label="Line limits are chosen automatically for the selected margin text mode.")
    set_xalign_if_supported(margin_text_hint)
    notes_box = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=4)
    notes_box.pack_start(margin_text_hint, False, False, 0)
    notes_box.pack_start(priority_note_label, False, False, 0)
    notes_box.pack_start(style_legend_label, False, False, 0)

    center_stack.pack_start(bottom_margin_shell, False, False, 0)
    center_stack.pack_start(margin_position_shell, False, False, 0)
    center_stack.pack_start(notes_box, False, False, 0)

    margins_grid_shell = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=28)
    left_margin_shell = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=0)
    center_margin_shell = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=0)
    right_margin_shell = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=0)
    margins_grid_shell.pack_start(left_margin_shell, False, False, 0)
    margins_grid_shell.pack_start(center_margin_shell, True, True, 0)
    margins_grid_shell.pack_start(right_margin_shell, False, False, 0)

    left_margin_spacer_top = gtk_module.Label(label="")
    left_margin_spacer_bottom = gtk_module.Label(label="")
    left_margin_center_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=0)
    left_margin_center_left = gtk_module.Label(label="")
    left_margin_center_right = gtk_module.Label(label="")
    left_margin_center_row.pack_start(left_margin_center_left, True, True, 0)
    left_margin_center_row.pack_start(left_margin_box, False, False, 0)
    left_margin_center_row.pack_start(left_margin_center_right, True, True, 0)
    left_margin_shell.pack_start(left_margin_spacer_top, True, True, 0)
    left_margin_shell.pack_start(left_margin_center_row, False, False, 0)
    left_margin_shell.pack_start(left_margin_spacer_bottom, True, True, 0)

    right_margin_spacer_top = gtk_module.Label(label="")
    right_margin_spacer_bottom = gtk_module.Label(label="")
    right_margin_center_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=0)
    right_margin_center_left = gtk_module.Label(label="")
    right_margin_center_right = gtk_module.Label(label="")
    right_margin_center_row.pack_start(right_margin_center_left, True, True, 0)
    right_margin_center_row.pack_start(right_margin_box, False, False, 0)
    right_margin_center_row.pack_start(right_margin_center_right, True, True, 0)
    right_margin_shell.pack_start(right_margin_spacer_top, True, True, 0)
    right_margin_shell.pack_start(right_margin_center_row, False, False, 0)
    right_margin_shell.pack_start(right_margin_spacer_bottom, True, True, 0)

    center_margin_shell.pack_start(top_margin_shell, False, False, 0)
    center_margin_shell.pack_start(center_stack, True, True, 0)

    margins_layout_col.pack_start(margins_grid_shell, False, False, 0)

    margins_tab_title = gtk_module.Label(label="Margins (for each display)")
    set_xalign_if_supported(margins_tab_title)

    return {
        "margins_tab_box": margins_tab_box,
        "margins_section_label": margins_section_label,
        "right_margin_col": right_margin_col,
        "right_margin_label": right_margin_label,
        "right_margin_spin": right_margin_spin,
        "bottom_margin_row": bottom_margin_row,
        "bottom_margin_label": bottom_margin_label,
        "bottom_margin_spin": bottom_margin_spin,
        "margins_tab_title": margins_tab_title,
        "margin_text_tabs": margin_text_tabs,
        "margin_settings_page": margin_settings_page,
        "margin_text_page": margin_text_page,
        "margin_settings_preview_label": margin_settings_preview_label,
        "margin_text_section_label": margin_text_section_label,
        "margin_text_mode_label": margin_text_mode_label,
        "margin_text_mode_off": margin_text_mode_off,
        "margin_text_mode_settings": margin_text_mode_settings,
        "margin_text_mode_text": margin_text_mode_text,
        "margin_text_mode_both": margin_text_mode_both,
        "margin_text_entry": margin_text_entry,
        "margin_position_left_top": margin_position_left_top,
        "margin_position_right_bottom": margin_position_right_bottom,
        "margin_position_left_bottom": margin_position_left_bottom,
        "margin_position_right_top": margin_position_right_top,
        "margin_text_max_lines_spin": margin_text_max_lines_spin,
        "current_state_summary_display": current_state_summary_display,
    }
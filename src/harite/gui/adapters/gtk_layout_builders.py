from __future__ import annotations

from typing import Any


def set_xalign_if_supported(widget: Any, value: float = 0.0) -> None:
    if hasattr(widget, "set_xalign"):
        widget.set_xalign(value)


def build_header_section(gtk_module: Any, root: Any) -> dict[str, Any]:
    header_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
    root.pack_start(header_col, False, False, 0)

    title_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=8)
    header_col.pack_start(title_row, False, False, 0)

    title = gtk_module.Label(label="")
    set_xalign_if_supported(title)
    title_row.pack_start(title, False, False, 0)

    subtitle = gtk_module.Label(label="")
    set_xalign_if_supported(subtitle)

    command_bar = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=8)
    command_section_label = gtk_module.Label(label="")
    set_xalign_if_supported(command_section_label)

    title_spacer = gtk_module.Label(label="")
    title_row.pack_start(title_spacer, True, True, 0)
    title_row.pack_start(command_bar, False, False, 0)

    btn_setting = gtk_module.Button(label="Settings")
    btn_help = gtk_module.Button(label="Help")
    btn_about = gtk_module.Button(label="About")
    btn_set_color = gtk_module.Button(label="Color")
    command_bar.pack_start(btn_set_color, False, False, 0)
    command_bar.pack_start(btn_setting, False, False, 0)
    command_bar.pack_start(btn_help, False, False, 0)
    command_bar.pack_start(btn_about, False, False, 0)

    flow_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=8)
    header_col.pack_start(flow_row, False, False, 0)

    flow_legend_label = gtk_module.Label(label="Compose -> Optimize -> Apply")
    set_xalign_if_supported(flow_legend_label)
    flow_row.pack_start(flow_legend_label, False, False, 0)

    flow_spacer = gtk_module.Label(label="")
    flow_row.pack_start(flow_spacer, True, True, 0)

    optimize_btn = gtk_module.Button(label="Save As")
    if hasattr(optimize_btn, "set_sensitive"):
        optimize_btn.set_sensitive(False)
    flow_row.pack_start(optimize_btn, False, False, 0)

    return {
        "header_col": header_col,
        "title": title,
        "subtitle": subtitle,
        "command_bar": command_bar,
        "command_section_label": command_section_label,
        "btn_setting": btn_setting,
        "btn_help": btn_help,
        "btn_about": btn_about,
        "btn_set_color": btn_set_color,
        "flow_row": flow_row,
        "flow_legend_label": flow_legend_label,
        "optimize_btn": optimize_btn,
    }


def build_center_body_section(gtk_module: Any, root: Any) -> dict[str, Any]:
    center_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=10)
    root.pack_start(center_row, True, True, 0)

    command_tabs = gtk_module.Notebook()
    center_row.pack_start(command_tabs, True, True, 0)

    return {
        "center_row": center_row,
        "command_tabs": command_tabs,
    }


def build_centered_page_shell(gtk_module: Any, content: Any) -> Any:
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


def build_footer_section(gtk_module: Any, root: Any) -> dict[str, Any]:
    footer_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=4)
    root.pack_start(footer_col, False, False, 0)

    status_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=8)
    footer_col.pack_start(status_row, False, False, 0)
    status_label = gtk_module.Label(label="Status: ready")
    set_xalign_if_supported(status_label)
    status_row.pack_start(status_label, False, False, 0)

    status_spacer = gtk_module.Label(label="")
    status_row.pack_start(status_spacer, True, True, 0)
    watch_summary_label = gtk_module.Label(label="Watch: stopped")
    set_xalign_if_supported(watch_summary_label)
    error_label = gtk_module.Label(label="Error: none")
    set_xalign_if_supported(error_label)

    return {
        "footer_col": footer_col,
        "status_row": status_row,
        "status_label": status_label,
        "status_spacer": status_spacer,
        "watch_summary_label": watch_summary_label,
        "error_label": error_label,
    }
from __future__ import annotations

from harite.gui.adapters.gtk_dialog_builders import build_about_dialog_section
from harite.gui.adapters.gtk_dialog_builders import build_color_dialog_section
from harite.gui.adapters.gtk_dialog_builders import build_settings_section
from harite.gui.adapters.gtk_layout_builders import build_center_body_section
from harite.gui.adapters.gtk_layout_builders import build_centered_page_shell
from harite.gui.adapters.gtk_layout_builders import build_footer_section
from harite.gui.adapters.gtk_layout_builders import build_header_section
from harite.gui.adapters.gtk_tab_builders import build_action_cluster_section
from harite.gui.adapters.gtk_tab_builders import build_main_tab_section
from harite.gui.adapters.gtk_tab_builders import build_margins_tab_section
from harite.gui.adapters.gtk_tab_builders import build_primary_margin_controls
from harite.gui.adapters.gtk_tab_builders import build_runtime_state_labels
from harite.gui.adapters.gtk_tab_builders import build_watch_tab_section


__all__ = [
    "build_about_dialog_section",
    "build_action_cluster_section",
    "build_center_body_section",
    "build_centered_page_shell",
    "build_color_dialog_section",
    "build_footer_section",
    "build_header_section",
    "build_main_tab_section",
    "build_margins_tab_section",
    "build_primary_margin_controls",
    "build_runtime_state_labels",
    "build_settings_section",
    "build_watch_tab_section",
]
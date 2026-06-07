"""Qt layout builders for the Harite GUI skeleton (Phase 2).

Builds the 3-layer window structure (header / center body / footer) and the
QTabWidget with three empty tabs (Main / Margins / Slideshow).

Widget naming follows the GTK adapter convention so that signal wiring in
later phases can reference the same logical names.
"""

from __future__ import annotations

from typing import Any


from harite.gui.resource_access import set_qt_button_icon as _set_button_icon
from harite.gui.views.footer_feedback import configure_footer_error_label_qt


# ---------------------------------------------------------------------------
# Header section
# ---------------------------------------------------------------------------


def build_header_section() -> dict[str, Any]:
    """Build the header: title row (title + command bar) + flow row.

    Returns a dict of named widgets matching the GTK adapter naming convention.
    """
    from PyQt6.QtWidgets import (
        QHBoxLayout,
        QLabel,
        QPushButton,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )

    header = QWidget()
    header_layout = QVBoxLayout(header)
    header_layout.setContentsMargins(0, 0, 0, 4)
    header_layout.setSpacing(4)

    # --- title row: [title label] [spacer] [Color] [Settings] [About] ---
    title_row = QWidget()
    title_row_layout = QHBoxLayout(title_row)
    title_row_layout.setContentsMargins(0, 0, 0, 0)
    title_row_layout.setSpacing(8)

    title = QLabel("")
    title_row_layout.addWidget(title)

    title_spacer = QWidget()
    title_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    title_row_layout.addWidget(title_spacer)

    btn_set_color = QPushButton("Color")
    btn_setting = QPushButton("Settings")
    btn_about = QPushButton("About")
    _set_button_icon(btn_set_color, "icons", "lucide", "palette.svg")
    _set_button_icon(btn_setting, "icons", "lucide", "settings.svg")
    _set_button_icon(btn_about, "icons", "lucide", "info.svg")
    title_row_layout.addWidget(btn_set_color)
    title_row_layout.addWidget(btn_setting)
    title_row_layout.addWidget(btn_about)

    header_layout.addWidget(title_row)

    # --- flow row: [legend] [spacer] [Export Image] ---
    flow_row = QWidget()
    flow_row_layout = QHBoxLayout(flow_row)
    flow_row_layout.setContentsMargins(0, 0, 0, 0)
    flow_row_layout.setSpacing(8)

    flow_legend_label = QLabel("")
    from harite.gui.views.flow_legend_surface import apply_flow_legend_markup

    apply_flow_legend_markup(flow_legend_label, active_step="compose")
    flow_row_layout.addWidget(flow_legend_label)

    flow_spacer = QWidget()
    flow_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    flow_row_layout.addWidget(flow_spacer)

    optimize_btn = QPushButton("Export Image")
    optimize_btn.setEnabled(False)
    _set_button_icon(optimize_btn, "icons", "lucide", "image-down.svg")
    flow_row_layout.addWidget(optimize_btn)

    header_layout.addWidget(flow_row)

    return {
        "header_widget": header,
        "title": title,
        "btn_set_color": btn_set_color,
        "btn_setting": btn_setting,
        "btn_about": btn_about,
        "flow_legend_label": flow_legend_label,
        "optimize_btn": optimize_btn,
    }


# ---------------------------------------------------------------------------
# Center body section (QTabWidget + 3 stub tabs)
# ---------------------------------------------------------------------------

_TAB_MAIN = "Main"
_TAB_MARGINS = "Margins (for each display)"
_TAB_SLIDESHOW = "Slideshow (stopped)"


def build_center_body_section() -> dict[str, Any]:
    """Build the center body: QTabWidget with Main tab + 2 stub tabs.

    Main tab is fully built (Phase 3).
    Margins and Slideshow stubs will be replaced in Phase 4 and Phase 5.

    Returns a dict containing ``command_tabs`` and all tab-level widget dicts.
    """
    from PyQt6.QtWidgets import QTabWidget, QWidget

    from harite.gui.adapters_qt.qt_tab_main import build_main_tab
    from harite.gui.adapters_qt.qt_tab_margins import build_margins_tab
    from harite.gui.adapters_qt.qt_tab_slideshow import build_slideshow_tab

    command_tabs = QTabWidget()

    main_tab_widgets = build_main_tab()

    margins_tab_widgets = build_margins_tab(
        priority_note_label=main_tab_widgets["priority_note_label"],
        style_legend_label=main_tab_widgets["style_legend_label"],
        current_state_section_label=main_tab_widgets["current_state_section_label"],
        current_margins_label=main_tab_widgets["current_margins_label"],
        current_left_label=main_tab_widgets["current_left_label"],
        current_right_label=main_tab_widgets["current_right_label"],
    )

    slideshow_tab_widgets = build_slideshow_tab()

    command_tabs.addTab(main_tab_widgets["main_col"], _TAB_MAIN)
    command_tabs.addTab(margins_tab_widgets["margins_tab_box"], _TAB_MARGINS)
    command_tabs.addTab(slideshow_tab_widgets["slideshow_tab_box"], _TAB_SLIDESHOW)

    return {
        "command_tabs": command_tabs,
        **main_tab_widgets,
        **margins_tab_widgets,
        **slideshow_tab_widgets,
    }


# ---------------------------------------------------------------------------
# Footer section
# ---------------------------------------------------------------------------


def build_footer_section() -> dict[str, Any]:
    """Build the footer: [Status | Slideshow summary] / separator / [Error].

    Returns a dict of named widgets.
    """
    from PyQt6.QtWidgets import (
        QFrame,
        QHBoxLayout,
        QLabel,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )

    footer = QWidget()
    footer_layout = QVBoxLayout(footer)
    footer_layout.setContentsMargins(0, 4, 0, 0)
    footer_layout.setSpacing(4)

    # --- status row: [Status: ready] [spacer] [Slideshow: stopped] ---
    status_row = QWidget()
    status_row_layout = QHBoxLayout(status_row)
    status_row_layout.setContentsMargins(0, 0, 0, 0)
    status_row_layout.setSpacing(8)

    status_label = QLabel("Status: ready")
    status_label.setObjectName("statusLabel")
    status_row_layout.addWidget(status_label)

    status_spacer = QWidget()
    status_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    status_row_layout.addWidget(status_spacer)

    slideshow_summary_label = QLabel("Slideshow: stopped")
    status_row_layout.addWidget(slideshow_summary_label)

    footer_layout.addWidget(status_row)

    # --- separator ---
    message_separator = QFrame()
    message_separator.setFrameShape(QFrame.Shape.HLine)
    message_separator.setFrameShadow(QFrame.Shadow.Sunken)
    footer_layout.addWidget(message_separator)

    # --- error row ---
    message_row = QWidget()
    message_row_layout = QHBoxLayout(message_row)
    message_row_layout.setContentsMargins(0, 0, 0, 0)
    message_row_layout.setSpacing(8)

    error_label = QLabel("Error: none")
    error_label.setObjectName("errorLabel")
    configure_footer_error_label_qt(error_label)
    message_row_layout.addWidget(error_label, 1)

    footer_layout.addWidget(message_row)

    return {
        "footer_widget": footer,
        "status_label": status_label,
        "slideshow_summary_label": slideshow_summary_label,
        "message_separator": message_separator,
        "error_label": error_label,
    }


# ---------------------------------------------------------------------------
# Full window layout assembly
# ---------------------------------------------------------------------------


def build_main_layout(qwindow: Any) -> dict[str, Any]:
    """Populate *qwindow* with the 3-layer layout and return the widget registry.

    Layers (top to bottom):
        header  – title row + flow row
        center  – QTabWidget with 3 tabs
        footer  – status / error rows

    The returned dict uses the same logical names as the GTK adapter so that
    signal wiring can reference widgets by name regardless of backend.
    """
    from PyQt6.QtWidgets import (
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )

    central = QWidget()
    root_layout = QVBoxLayout(central)
    root_layout.setContentsMargins(10, 10, 10, 10)
    root_layout.setSpacing(10)

    header_widgets = build_header_section()
    center_widgets = build_center_body_section()
    footer_widgets = build_footer_section()

    root_layout.addWidget(header_widgets["header_widget"])

    command_tabs = center_widgets["command_tabs"]
    command_tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    root_layout.addWidget(command_tabs, stretch=1)

    root_layout.addWidget(footer_widgets["footer_widget"])

    qwindow.setCentralWidget(central)

    return {
        "main_window": qwindow,
        "root": central,
        **header_widgets,
        **center_widgets,
        **footer_widgets,
    }

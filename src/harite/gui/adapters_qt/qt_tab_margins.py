"""Qt Margins tab builder for Harite GUI (Phase 4).

Builds the Margins tab content:
  - cross-grid editor: Top / Left / center_stack / Right / Bottom
  - center_stack: embed pattern + margin text sub-tabs + position selector
                  (C-04 Wave a: no alignment summary / notes on tab face)

Widget naming follows the GTK adapter convention.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_spin(minimum: int, maximum: int, step: int = 1, initial: int = 0) -> Any:
    from PyQt6.QtWidgets import QSpinBox

    spin = QSpinBox()
    spin.setMinimum(minimum)
    spin.setMaximum(maximum)
    spin.setSingleStep(step)
    spin.setValue(initial)
    return spin


def _vcenter_widget(inner: Any) -> Any:
    """Wrap *inner* in a vertically-centred container."""
    from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

    shell = QWidget()
    shell_layout = QVBoxLayout(shell)
    shell_layout.setContentsMargins(0, 0, 0, 0)
    shell_layout.setSpacing(0)
    shell_layout.addStretch()
    shell_layout.addWidget(inner)
    shell_layout.addStretch()
    shell.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
    return shell


# ---------------------------------------------------------------------------
# Margin spin sections (top / left / right / bottom)
# ---------------------------------------------------------------------------


def _build_margin_spin_block(label_text: str, maximum: int) -> dict[str, Any]:
    """Build a label + spin pair for one margin edge."""
    from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

    block = QWidget()
    layout = QVBoxLayout(block)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)

    label = QLabel(label_text)
    spin = _make_spin(0, maximum)
    layout.addWidget(label)
    layout.addWidget(spin)
    return {"block": block, "label": label, "spin": spin}


# ---------------------------------------------------------------------------
# Center stack subwidgets
# ---------------------------------------------------------------------------


def _build_embed_pattern_block() -> dict[str, Any]:
    """embed pattern: Off / Settings / Text only / Both (radio group, default Off)."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QButtonGroup,
        QHBoxLayout,
        QLabel,
        QRadioButton,
        QVBoxLayout,
        QWidget,
    )

    block = QWidget()
    layout = QVBoxLayout(block)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)

    margin_text_mode_label = QLabel("embed pattern:")
    margin_text_mode_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    layout.addWidget(margin_text_mode_label)

    mode_row = QWidget()
    mode_row_layout = QHBoxLayout(mode_row)
    mode_row_layout.setContentsMargins(0, 0, 0, 0)
    mode_row_layout.setSpacing(6)

    margin_text_mode_off = QRadioButton("Off")
    margin_text_mode_settings = QRadioButton("Settings")
    margin_text_mode_text = QRadioButton("Text only")
    margin_text_mode_both = QRadioButton("Both")
    margin_text_mode_off.setChecked(True)

    embed_mode_group = QButtonGroup(block)
    embed_mode_group.addButton(margin_text_mode_off)
    embed_mode_group.addButton(margin_text_mode_settings)
    embed_mode_group.addButton(margin_text_mode_text)
    embed_mode_group.addButton(margin_text_mode_both)

    for rad in (margin_text_mode_off, margin_text_mode_settings, margin_text_mode_text, margin_text_mode_both):
        mode_row_layout.addWidget(rad)
    mode_row_layout.addStretch()
    layout.addWidget(mode_row)

    return {
        "embed_pattern_block": block,
        "margin_text_mode_label": margin_text_mode_label,
        "margin_text_mode_off": margin_text_mode_off,
        "margin_text_mode_settings": margin_text_mode_settings,
        "margin_text_mode_text": margin_text_mode_text,
        "margin_text_mode_both": margin_text_mode_both,
        "_embed_mode_group": embed_mode_group,
    }


def _build_margin_text_tabs() -> dict[str, Any]:
    """Inner QTabWidget: Settings page (preview label) + Text page (text entry)."""
    from PyQt6.QtWidgets import (
        QLabel,
        QPlainTextEdit,
        QScrollArea,
        QSizePolicy,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )

    margin_text_tabs = QTabWidget()
    margin_text_tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    # --- Settings page ---
    margin_settings_page = QWidget()
    settings_page_layout = QVBoxLayout(margin_settings_page)
    settings_page_layout.setContentsMargins(4, 4, 4, 4)
    settings_page_layout.setSpacing(4)

    margin_settings_preview_label = QLabel("resolution=-")
    margin_settings_preview_label.setAlignment(__import__("PyQt6.QtCore", fromlist=["Qt"]).Qt.AlignmentFlag.AlignLeft)
    margin_settings_preview_label.setWordWrap(True)
    margin_settings_preview_label.setTextInteractionFlags(
        __import__("PyQt6.QtCore", fromlist=["Qt"]).Qt.TextInteractionFlag.TextSelectableByMouse
    )
    settings_page_layout.addWidget(margin_settings_preview_label)
    settings_page_layout.addStretch()

    # --- Text page ---
    margin_text_page = QWidget()
    text_page_layout = QVBoxLayout(margin_text_page)
    text_page_layout.setContentsMargins(4, 4, 4, 4)
    text_page_layout.setSpacing(4)

    margin_text_section_label = QLabel("Margin text")
    text_page_layout.addWidget(margin_text_section_label)

    margin_text_entry = QPlainTextEdit()
    margin_text_entry.setReadOnly(True)
    margin_text_entry.setPlaceholderText("Up to 5 lines of margin text")
    margin_text_entry.setMinimumSize(460, 140)
    text_page_layout.addWidget(margin_text_entry)

    margin_text_tabs.addTab(margin_settings_page, "Settings")
    margin_text_tabs.addTab(margin_text_page, "Text")

    return {
        "margin_text_tabs": margin_text_tabs,
        "margin_settings_page": margin_settings_page,
        "margin_text_page": margin_text_page,
        "margin_settings_preview_label": margin_settings_preview_label,
        "margin_text_section_label": margin_text_section_label,
        "margin_text_entry": margin_text_entry,
    }


def _build_position_selector() -> dict[str, Any]:
    """Position selector: Left (Top/Bottom) and Right (Top/Bottom) radio groups.

    All 4 radios share a single QButtonGroup to replicate GTK behaviour where
    they form one mutually-exclusive selection.  Default: right-bottom.
    """
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QButtonGroup,
        QHBoxLayout,
        QLabel,
        QRadioButton,
        QVBoxLayout,
        QWidget,
    )

    shell = QWidget()
    shell_layout = QVBoxLayout(shell)
    shell_layout.setContentsMargins(0, 0, 0, 0)
    shell_layout.setSpacing(4)

    position_label = QLabel("Position:")
    position_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    shell_layout.addWidget(position_label)

    columns_row = QWidget()
    columns_row_layout = QHBoxLayout(columns_row)
    columns_row_layout.setContentsMargins(0, 0, 0, 0)
    columns_row_layout.setSpacing(48)
    columns_row_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    def _make_col(side_label: str) -> dict[str, Any]:
        col = QWidget()
        col_layout = QVBoxLayout(col)
        col_layout.setContentsMargins(0, 0, 0, 0)
        col_layout.setSpacing(4)
        col_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        lbl = QLabel(f"{side_label}:")
        lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        top_rad = QRadioButton("Top")
        bot_rad = QRadioButton("Bottom")
        col_layout.addWidget(lbl)
        col_layout.addWidget(top_rad)
        col_layout.addWidget(bot_rad)
        return {"col": col, "top": top_rad, "bot": bot_rad}

    left = _make_col("Left")
    right = _make_col("Right")

    position_group = QButtonGroup(shell)
    position_group.addButton(left["top"])
    position_group.addButton(left["bot"])
    position_group.addButton(right["top"])
    position_group.addButton(right["bot"])

    right["bot"].setChecked(True)

    columns_row_layout.addWidget(left["col"])
    columns_row_layout.addWidget(right["col"])
    shell_layout.addWidget(columns_row)

    return {
        "margin_position_shell": shell,
        "margin_position_left_top": left["top"],
        "margin_position_left_bottom": left["bot"],
        "margin_position_right_top": right["top"],
        "margin_position_right_bottom": right["bot"],
        "_position_group": position_group,
    }


def _build_hidden_max_lines_spin() -> dict[str, Any]:
    """Keep max-lines spin for sync/wiring; effective lines still come from mode."""
    spin = _make_spin(1, 20, step=1, initial=3)
    spin.setVisible(False)
    return {"margin_text_max_lines_spin": spin}


def _build_center_stack() -> dict[str, Any]:
    """Center stack: embed pattern + sub-tabs + position (cross-grid primary)."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QLabel,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )

    stack = QWidget()
    stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    stack_layout = QVBoxLayout(stack)
    stack_layout.setContentsMargins(0, 0, 0, 0)
    stack_layout.setSpacing(8)

    # Embed pattern
    embed_widgets = _build_embed_pattern_block()
    stack_layout.addWidget(embed_widgets["embed_pattern_block"])

    # Inner sub-tabs (Settings / Text)
    text_tab_widgets = _build_margin_text_tabs()
    stack_layout.addWidget(text_tab_widgets["margin_text_tabs"], stretch=1)

    # Position selector
    position_widgets = _build_position_selector()
    stack_layout.addWidget(position_widgets["margin_position_shell"])

    hidden_spin = _build_hidden_max_lines_spin()

    from harite.gui.views.margins_surface import (
        MARGIN_CROSS_GRID_TOOLTIP,
        MARGIN_PRIORITY_RULE_TOOLTIP,
        MARGIN_TEXT_LINE_LIMITS_TOOLTIP,
        apply_widget_tooltip,
    )

    apply_widget_tooltip(embed_widgets["margin_text_mode_label"], MARGIN_TEXT_LINE_LIMITS_TOOLTIP)
    apply_widget_tooltip(text_tab_widgets["margin_text_entry"], MARGIN_TEXT_LINE_LIMITS_TOOLTIP)
    apply_widget_tooltip(position_widgets["margin_position_shell"], MARGIN_PRIORITY_RULE_TOOLTIP)
    apply_widget_tooltip(stack, MARGIN_CROSS_GRID_TOOLTIP)

    return {
        "center_stack": stack,
        **embed_widgets,
        **text_tab_widgets,
        **position_widgets,
        **hidden_spin,
    }


# ---------------------------------------------------------------------------
# P-08: Main-tab margin cross-grid + options drawer
# ---------------------------------------------------------------------------


def build_margin_cross_grid(*, compose_center: Any) -> dict[str, Any]:
    """Build the 4-edge margin cross-grid with *compose_center* in the middle cell."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QSizePolicy, QWidget

    top = _build_margin_spin_block("Top margin (px)", maximum=250)
    left = _build_margin_spin_block("Left margin (px)", maximum=500)
    right = _build_margin_spin_block("Right margin (px)", maximum=500)
    bottom = _build_margin_spin_block("Bottom margin (px)", maximum=250)

    def _hcenter(block: Any) -> Any:
        shell = QWidget()
        layout = QHBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(block)
        layout.addStretch()
        return shell

    top_shell = _hcenter(top["block"])
    bottom_shell = _hcenter(bottom["block"])
    left_shell = _vcenter_widget(left["block"])
    right_shell = _vcenter_widget(right["block"])

    margin_cross_grid = QWidget()
    margin_cross_grid.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    cross_grid = QGridLayout(margin_cross_grid)
    cross_grid.setColumnStretch(1, 1)
    cross_grid.setRowStretch(1, 1)
    cross_grid.setSpacing(24)
    cross_grid.setContentsMargins(0, 0, 0, 0)

    cross_grid.addWidget(top_shell, 0, 1, Qt.AlignmentFlag.AlignHCenter)
    cross_grid.addWidget(left_shell, 1, 0)
    cross_grid.addWidget(compose_center, 1, 1)
    cross_grid.addWidget(right_shell, 1, 2)
    cross_grid.addWidget(bottom_shell, 2, 1, Qt.AlignmentFlag.AlignHCenter)

    from harite.gui.views.margins_surface import MARGIN_BEHAVIOR_TOOLTIP, apply_widget_tooltip

    apply_widget_tooltip(margin_cross_grid, MARGIN_BEHAVIOR_TOOLTIP)
    for edge in (top["label"], left["label"], right["label"], bottom["label"]):
        apply_widget_tooltip(edge, MARGIN_BEHAVIOR_TOOLTIP)

    return {
        "margin_cross_grid": margin_cross_grid,
        "top_margin_label": top["label"],
        "top_margin_spin": top["spin"],
        "left_margin_label": left["label"],
        "left_margin_spin": left["spin"],
        "right_margin_label": right["label"],
        "right_margin_spin": right["spin"],
        "bottom_margin_label": bottom["label"],
        "bottom_margin_spin": bottom["spin"],
    }


def _build_margins_options_drawer_trigger() -> dict[str, Any]:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget

    from harite.gui.resource_access import set_qt_button_icon as _set_button_icon
    from harite.gui.views.margins_options_drawer import MORE_LABEL, QT_TRIGGER_OBJECT_NAME

    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    btn_margins_options_more = QPushButton(MORE_LABEL)
    btn_margins_options_more.setObjectName(QT_TRIGGER_OBJECT_NAME)
    _set_button_icon(btn_margins_options_more, "icons", "lucide", "arrow-down.svg")
    layout.addWidget(btn_margins_options_more)

    return {
        "margins_options_trigger_row": row,
        "btn_margins_options_more": btn_margins_options_more,
    }


def build_margins_options_drawer() -> dict[str, Any]:
    """Collapsible panel: embed pattern, margin text notebook, position selector."""
    from PyQt6.QtWidgets import QFrame, QVBoxLayout, QWidget

    from harite.gui.views.margins_options_drawer import QT_DRAWER_OBJECT_NAME

    center_widgets = _build_center_stack()

    from PyQt6.QtWidgets import QSizePolicy

    drawer = QWidget()
    drawer.setObjectName(QT_DRAWER_OBJECT_NAME)
    drawer.setVisible(False)
    drawer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    drawer_layout = QVBoxLayout(drawer)
    drawer_layout.setContentsMargins(0, 8, 0, 0)
    drawer_layout.setSpacing(10)
    drawer_top_border = QFrame()
    drawer_top_border.setVisible(False)
    drawer_top_border.setFixedHeight(1)
    drawer_layout.addWidget(drawer_top_border)
    drawer_layout.addWidget(center_widgets["center_stack"])

    return {
        "margins_options_drawer": drawer,
        "margins_options_drawer_top_border": drawer_top_border,
        **center_widgets,
    }


# ---------------------------------------------------------------------------
# Legacy Margins tab assembly (superseded by P-08 Main + drawer)
# ---------------------------------------------------------------------------


def build_margins_tab(
    *,
    priority_note_label: Any,
    style_legend_label: Any,
    current_state_section_label: Any,
    current_margins_label: Any,
    current_left_label: Any,
    current_right_label: Any,
) -> dict[str, Any]:
    """Build the complete Margins tab widget and return the widget registry.

    Cross-grid structure:
        (1,0) top_margin
        (0,1) left_margin  (1,1) center_stack  (2,1) right_margin
        (1,2) bottom_margin

    Legacy label refs (priority_note_label etc.) are accepted for layout-builder
    compatibility; they are not placed on the Margins tab face (C-04 Wave a).
    """
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )

    margins_tab_box = QWidget()
    outer_layout = QVBoxLayout(margins_tab_box)
    outer_layout.setContentsMargins(8, 8, 8, 8)
    outer_layout.setSpacing(12)

    # -- margin spin blocks --
    top = _build_margin_spin_block("Top margin (px)", maximum=250)
    left = _build_margin_spin_block("Left margin (px)", maximum=500)
    right = _build_margin_spin_block("Right margin (px)", maximum=500)
    bottom = _build_margin_spin_block("Bottom margin (px)", maximum=250)

    # Wrap top/bottom in centered horizontal shells
    def _hcenter(block: Any) -> Any:
        shell = QWidget()
        layout = QHBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(block)
        layout.addStretch()
        return shell

    top_shell = _hcenter(top["block"])
    bottom_shell = _hcenter(bottom["block"])

    # Vertically centre left/right margin blocks
    left_shell = _vcenter_widget(left["block"])
    right_shell = _vcenter_widget(right["block"])

    # -- center stack --
    _ = (priority_note_label, style_legend_label, current_state_section_label, current_margins_label, current_left_label, current_right_label)
    center_widgets = _build_center_stack()

    # -- cross-grid --
    cross_grid_widget = QWidget()
    cross_grid_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    cross_grid = QGridLayout(cross_grid_widget)
    cross_grid.setColumnStretch(1, 1)
    cross_grid.setRowStretch(1, 1)
    cross_grid.setSpacing(24)
    cross_grid.setContentsMargins(0, 0, 0, 0)

    cross_grid.addWidget(top_shell, 0, 1, Qt.AlignmentFlag.AlignHCenter)
    cross_grid.addWidget(left_shell, 1, 0)
    cross_grid.addWidget(center_widgets["center_stack"], 1, 1)
    cross_grid.addWidget(right_shell, 1, 2)
    cross_grid.addWidget(bottom_shell, 2, 1, Qt.AlignmentFlag.AlignHCenter)

    outer_layout.addWidget(cross_grid_widget, stretch=1)

    from harite.gui.views.margins_surface import MARGIN_BEHAVIOR_TOOLTIP, apply_widget_tooltip

    apply_widget_tooltip(cross_grid_widget, MARGIN_BEHAVIOR_TOOLTIP)
    for edge in (top["label"], left["label"], right["label"], bottom["label"]):
        apply_widget_tooltip(edge, MARGIN_BEHAVIOR_TOOLTIP)

    return {
        "margins_tab_box": margins_tab_box,
        "top_margin_label": top["label"],
        "top_margin_spin": top["spin"],
        "left_margin_label": left["label"],
        "left_margin_spin": left["spin"],
        "right_margin_label": right["label"],
        "right_margin_spin": right["spin"],
        "bottom_margin_label": bottom["label"],
        "bottom_margin_spin": bottom["spin"],
        **center_widgets,
    }

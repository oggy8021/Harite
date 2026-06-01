"""Qt Main tab builder for Harite GUI (Phase 3).

Builds the Main tab content:
  - compose grid: left panel / center panel / right panel (3-column)
  - action cluster: Preview group / Optimize group / Apply group (3-column)

Widget naming follows the GTK adapter convention so that signal wiring in
Phase 8 can reference the same logical names.
"""

from __future__ import annotations

from typing import Any


from harite.gui.resource_access import set_qt_button_icon as _set_button_icon


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _default_apply_mode() -> str:
    """Default apply mode for action cluster (plugin-aware)."""
    import sys

    from harite.settings import AppSettings

    platform_map = {
        "win32": "windows",
        "darwin": "macos",
    }
    default_plugin = platform_map.get(sys.platform, "linux")
    return AppSettings._default_apply_mode(default_plugin)


# ---------------------------------------------------------------------------
# Compose grid
# ---------------------------------------------------------------------------


def _build_display_direction_grid(side: str) -> dict[str, Any]:
    """Build the 3×3 direction-toggle grid for one display panel.

    Grid layout (column, row):
      (1,0) = Top toggle
      (0,1) = Left toggle   (1,1) = Open button   (2,1) = Right toggle
      (1,2) = Bottom toggle

    Returns a dict of named widgets; *side* is "l" or "r".
    """
    from PyQt6.QtWidgets import QGridLayout, QPushButton, QSizePolicy, QWidget

    container = QWidget()
    grid = QGridLayout(container)
    grid.setSpacing(6)
    grid.setContentsMargins(0, 0, 0, 0)

    def _tgl(label: str) -> QPushButton:
        btn = QPushButton(label)
        btn.setCheckable(True)
        btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        return btn

    tgl_upper = _tgl(f"Top-{side.upper()}")
    tgl_lower = _tgl(f"Bottom-{side.upper()}")
    tgl_push_left = _tgl(f"Left-{side.upper()}")
    tgl_push_right = _tgl(f"Right-{side.upper()}")
    btn_get_img = QPushButton(f"Open-{side.upper()}")

    _set_button_icon(tgl_upper, "icons", "lucide", "arrow-up.svg")
    _set_button_icon(tgl_lower, "icons", "lucide", "arrow-down.svg")
    _set_button_icon(tgl_push_left, "icons", "lucide", "arrow-left.svg")
    _set_button_icon(tgl_push_right, "icons", "lucide", "arrow-right.svg")
    _set_button_icon(btn_get_img, "icons", "lucide", "folder-open.svg")

    grid.addWidget(tgl_upper, 0, 1)
    grid.addWidget(tgl_push_left, 1, 0)
    grid.addWidget(btn_get_img, 1, 1)
    grid.addWidget(tgl_push_right, 1, 2)
    grid.addWidget(tgl_lower, 2, 1)

    return {
        f"tgl_upper_{side}": tgl_upper,
        f"tgl_lower_{side}": tgl_lower,
        f"tgl_push_left_{side}": tgl_push_left,
        f"tgl_push_right_{side}": tgl_push_right,
        f"btn_get_img_{side}": btn_get_img,
        f"display_grid_{side}": container,
    }


def _build_display_panel(side: str) -> dict[str, Any]:
    """Build one full display panel (direction grid + path display + clear button)."""
    from PyQt6.QtWidgets import (
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )

    panel = QWidget()
    panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)

    grid_widgets = _build_display_direction_grid(side)
    layout.addWidget(grid_widgets[f"display_grid_{side}"])

    # Path display (read-only QLineEdit)
    input_display = QLineEdit()
    input_display.setReadOnly(True)
    input_display.setAlignment(__import__("PyQt6.QtCore", fromlist=["Qt"]).Qt.AlignmentFlag.AlignCenter)
    input_display.setPlaceholderText(f"{'Left' if side == 'l' else 'Right'} image path")

    path_row = QWidget()
    path_row_layout = QHBoxLayout(path_row)
    path_row_layout.setContentsMargins(0, 0, 0, 0)
    path_row_layout.addWidget(input_display)

    # Clear button
    btn_clr = QPushButton(f"Clear-{side.upper()}")
    _set_button_icon(btn_clr, "icons", "lucide", "folder-x.svg")

    clear_row = QWidget()
    clear_row_layout = QHBoxLayout(clear_row)
    clear_row_layout.setContentsMargins(0, 0, 0, 0)
    clear_row_layout.addStretch()
    clear_row_layout.addWidget(btn_clr)

    layout.addWidget(path_row)
    layout.addWidget(clear_row)

    return {
        f"input_display_{side}": input_display,
        f"btn_clr_path_{side}": btn_clr,
        f"panel_{side}": panel,
        **grid_widgets,
    }


def build_compose_grid_section() -> dict[str, Any]:
    """Build the 3-column compose grid (left panel / center panel / right panel)."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QGridLayout,
        QLabel,
        QSizePolicy,
        QWidget,
    )

    compose_grid_widget = QWidget()
    grid = QGridLayout(compose_grid_widget)
    grid.setColumnStretch(0, 1)
    grid.setColumnStretch(1, 0)
    grid.setColumnStretch(2, 1)
    grid.setSpacing(24)
    grid.setContentsMargins(0, 0, 0, 0)

    left_widgets = _build_display_panel("l")
    right_widgets = _build_display_panel("r")

    center_panel = QWidget()
    center_panel.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
    from PyQt6.QtWidgets import QVBoxLayout
    center_layout = QVBoxLayout(center_panel)
    center_layout.setContentsMargins(0, 0, 0, 0)
    pick_state_label = QLabel("")
    pick_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    center_layout.addWidget(pick_state_label)

    from PyQt6.QtWidgets import QPushButton

    btn_swap = QPushButton("")
    btn_swap.setToolTip("Swap L/R")
    _set_button_icon(btn_swap, "icons", "lucide", "arrow-left-right.svg")
    center_layout.addWidget(btn_swap, alignment=Qt.AlignmentFlag.AlignHCenter)

    grid.addWidget(left_widgets["panel_l"], 0, 0)
    grid.addWidget(center_panel, 0, 1)
    grid.addWidget(right_widgets["panel_r"], 0, 2)

    return {
        "compose_grid": compose_grid_widget,
        "left_panel": left_widgets["panel_l"],
        "center_panel": center_panel,
        "right_panel": right_widgets["panel_r"],
        "pick_state_label": pick_state_label,
        "btn_swap_input_paths": btn_swap,
        **{k: v for k, v in left_widgets.items() if k != "panel_l"},
        **{k: v for k, v in right_widgets.items() if k != "panel_r"},
    }


# ---------------------------------------------------------------------------
# Action cluster
# ---------------------------------------------------------------------------


def _build_preview_group() -> dict[str, Any]:
    """Build the Preview group (preview boxes + assignment / result / state labels)."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QHBoxLayout,
        QLabel,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )

    group = QWidget()
    group_layout = QVBoxLayout(group)
    group_layout.setContentsMargins(0, 0, 0, 0)
    group_layout.setSpacing(4)

    preview_section_label = QLabel("Preview")
    group_layout.addWidget(preview_section_label)

    images_row = QWidget()
    images_row_layout = QHBoxLayout(images_row)
    images_row_layout.setContentsMargins(0, 0, 0, 0)
    images_row_layout.setSpacing(6)

    def _make_preview_side(name: str) -> dict[str, Any]:
        box = QWidget()
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(0, 0, 0, 0)
        box_layout.setSpacing(4)

        assignment = QLabel(f"{name.upper()} display <- -")
        assignment.setAlignment(Qt.AlignmentFlag.AlignLeft)

        preview_lbl = QLabel(f"Preview {name.upper()}: not-ready")
        preview_lbl.setFixedSize(160, 90)
        preview_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        preview_lbl.setStyleSheet("background: #222; color: #888; border: 1px solid #555;")

        result = QLabel("Result: not-ready")
        result.setAlignment(Qt.AlignmentFlag.AlignLeft)

        box_layout.addWidget(assignment)
        box_layout.addWidget(preview_lbl)
        box_layout.addWidget(result)
        return {"box": box, "assignment": assignment, "preview": preview_lbl, "result": result}

    left_side = _make_preview_side("l")
    right_side = _make_preview_side("r")
    images_row_layout.addWidget(left_side["box"])
    images_row_layout.addWidget(right_side["box"])
    group_layout.addWidget(images_row)

    preview_state_label = QLabel("Preview: not-ready")
    preview_source_label = QLabel("Preview source: -")
    preview_assist_label = QLabel("Assist: not-ready")
    for lbl in (preview_state_label, preview_source_label, preview_assist_label):
        lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        group_layout.addWidget(lbl)

    return {
        "preview_group": group,
        "preview_section_label": preview_section_label,
        "preview_left": left_side["preview"],
        "preview_right": right_side["preview"],
        "preview_left_assignment": left_side["assignment"],
        "preview_right_assignment": right_side["assignment"],
        "preview_left_result": left_side["result"],
        "preview_right_result": right_side["result"],
        "preview_state_label": preview_state_label,
        "preview_source_label": preview_source_label,
        "preview_assist_label": preview_assist_label,
    }


def _build_optimize_group() -> dict[str, Any]:
    """Build the Optimize group (button + result label)."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QHBoxLayout,
        QLabel,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    group = QWidget()
    group_layout = QVBoxLayout(group)
    group_layout.setContentsMargins(0, 0, 0, 0)
    group_layout.setSpacing(6)

    optimize_section_label = QLabel("Optimize")
    group_layout.addWidget(optimize_section_label)

    optimize_modern_btn = QPushButton("Optimize")
    optimize_modern_btn.setEnabled(False)
    _set_button_icon(optimize_modern_btn, "icons", "lucide", "image.svg")

    btn_row = QWidget()
    btn_row_layout = QHBoxLayout(btn_row)
    btn_row_layout.setContentsMargins(0, 0, 0, 0)
    btn_row_layout.addWidget(optimize_modern_btn)
    btn_row_layout.addStretch()
    group_layout.addWidget(btn_row)

    optimize_result = QLabel("Optimize result: not-run")
    optimize_result.setAlignment(Qt.AlignmentFlag.AlignLeft)
    optimize_result.setWordWrap(True)
    group_layout.addWidget(optimize_result)

    return {
        "optimize_group": group,
        "optimize_section_label": optimize_section_label,
        "optimize_modern_btn": optimize_modern_btn,
        "optimize_result": optimize_result,
    }


def _build_apply_group(default_apply_mode: str) -> dict[str, Any]:
    """Build the Apply group (button + target + apply mode radio + help text)."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QButtonGroup,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QRadioButton,
        QVBoxLayout,
        QWidget,
    )

    group = QWidget()
    group_layout = QVBoxLayout(group)
    group_layout.setContentsMargins(0, 0, 0, 0)
    group_layout.setSpacing(6)

    apply_section_label = QLabel("Apply")
    group_layout.addWidget(apply_section_label)

    apply_btn = QPushButton("Apply")
    apply_btn.setEnabled(False)
    _set_button_icon(apply_btn, "icons", "lucide", "wallpaper.svg")

    apply_btn_row = QWidget()
    apply_btn_row_layout = QHBoxLayout(apply_btn_row)
    apply_btn_row_layout.setContentsMargins(0, 0, 0, 0)
    apply_btn_row_layout.addWidget(apply_btn)
    apply_btn_row_layout.addStretch()
    group_layout.addWidget(apply_btn_row)

    apply_target = QLabel("Apply target: not-ready")
    apply_target.setAlignment(Qt.AlignmentFlag.AlignLeft)
    apply_target.setWordWrap(True)
    group_layout.addWidget(apply_target)

    # Apply mode radio row
    apply_mode_row_widget = QWidget()
    apply_mode_row_layout = QHBoxLayout(apply_mode_row_widget)
    apply_mode_row_layout.setContentsMargins(0, 0, 0, 0)
    apply_mode_row_layout.setSpacing(6)

    from harite.apply_surface import (
        apply_mode_help_text as build_apply_mode_help,
        per_monitor_mode_radio_label,
        single_file_mode_radio_label,
    )

    rad_apply_per_monitor = QRadioButton(per_monitor_mode_radio_label())
    rad_apply_single = QRadioButton(single_file_mode_radio_label())

    apply_mode_group = QButtonGroup(group)
    apply_mode_group.addButton(rad_apply_per_monitor)
    apply_mode_group.addButton(rad_apply_single)

    if default_apply_mode == "per-monitor-auto-split":
        rad_apply_per_monitor.setChecked(True)
        apply_mode_help_text = build_apply_mode_help("per-monitor-auto-split")
    else:
        rad_apply_single.setChecked(True)
        apply_mode_help_text = build_apply_mode_help("single-file")

    apply_mode_row_layout.addWidget(rad_apply_per_monitor)
    apply_mode_row_layout.addWidget(rad_apply_single)
    apply_mode_row_layout.addStretch()
    group_layout.addWidget(apply_mode_row_widget)

    # Apply mode help row
    apply_mode_help_row_widget = QWidget()
    apply_mode_help_row_layout = QHBoxLayout(apply_mode_help_row_widget)
    apply_mode_help_row_layout.setContentsMargins(0, 0, 0, 0)

    apply_mode_label = QLabel(apply_mode_help_text)
    apply_mode_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    apply_mode_label.setWordWrap(True)
    apply_mode_help_row_layout.addWidget(apply_mode_label, stretch=1)
    group_layout.addWidget(apply_mode_help_row_widget)

    return {
        "apply_group": group,
        "apply_section_label": apply_section_label,
        "apply_btn": apply_btn,
        "apply_target": apply_target,
        "rad_apply_single": rad_apply_single,
        "rad_apply_per_monitor": rad_apply_per_monitor,
        "apply_mode_label": apply_mode_label,
        "_apply_mode_button_group": apply_mode_group,
    }


def build_action_cluster_section(default_apply_mode: str) -> dict[str, Any]:
    """Build the action cluster (Preview | Optimize | Apply) horizontal row."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QHBoxLayout, QWidget

    cluster = QWidget()
    cluster_layout = QHBoxLayout(cluster)
    cluster_layout.setContentsMargins(0, 0, 0, 0)
    cluster_layout.setSpacing(24)
    cluster_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    preview_widgets = _build_preview_group()
    optimize_widgets = _build_optimize_group()
    apply_widgets = _build_apply_group(default_apply_mode)

    top_align = Qt.AlignmentFlag.AlignTop
    cluster_layout.addWidget(preview_widgets["preview_group"], alignment=top_align)
    cluster_layout.addWidget(optimize_widgets["optimize_group"], alignment=top_align)
    cluster_layout.addWidget(apply_widgets["apply_group"], alignment=top_align)

    return {
        "action_cluster_row": cluster,
        **preview_widgets,
        **optimize_widgets,
        **apply_widgets,
    }


# ---------------------------------------------------------------------------
# Runtime state labels (referenced by sync functions)
# ---------------------------------------------------------------------------


def build_runtime_state_labels() -> dict[str, Any]:
    """Build auxiliary state labels shared across tabs."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QLabel

    def _lbl(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        return lbl

    return {
        "do_it_plan_label": _lbl("Apply updates wallpaper immediately"),
        "save_path_state_label": _lbl("Export path: idle"),
        "save_target_label": _lbl("Export target: not-selected"),
        # Shared with Margins tab
        "priority_note_label": _lbl("Rule: margins define area; align/valign act inside it"),
        "style_legend_label": _lbl("Current behavior: margins are global to the composite canvas"),
        "current_state_section_label": _lbl("Main Window Current alignment:"),
        "current_margins_label": _lbl("margins=0,0,0,0"),
        "current_left_label": _lbl("L: align=center valign=center"),
        "current_right_label": _lbl("R: align=center valign=center"),
    }


# ---------------------------------------------------------------------------
# Full Main tab assembly
# ---------------------------------------------------------------------------


def build_main_tab() -> dict[str, Any]:
    """Build the complete Main tab widget and return the widget registry.

    Structure (top to bottom inside main_col):
        compose_grid  – 3-column panel (L / center / R)
        action_cluster – Preview | Optimize | Apply
    """
    from PyQt6.QtWidgets import QVBoxLayout, QWidget

    main_col = QWidget()
    layout = QVBoxLayout(main_col)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(12)

    compose_widgets = build_compose_grid_section()
    layout.addWidget(compose_widgets["compose_grid"])

    action_widgets = build_action_cluster_section(_default_apply_mode())
    layout.addWidget(action_widgets["action_cluster_row"])
    layout.addStretch()

    state_labels = build_runtime_state_labels()

    return {
        "main_col": main_col,
        **compose_widgets,
        **action_widgets,
        **state_labels,
    }

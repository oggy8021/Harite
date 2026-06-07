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

    from harite.gui.views.icon_button_surface import apply_icon_only_button

    def _tgl(tooltip: str, icon_name: str) -> QPushButton:
        btn = QPushButton("")
        btn.setCheckable(True)
        btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        _set_button_icon(btn, "icons", "lucide", icon_name)
        apply_icon_only_button(btn, tooltip)
        return btn

    from harite.gui.views.compose_surface import direction_alignment_tooltip

    tgl_upper = _tgl(direction_alignment_tooltip("Top", side), "arrow-up.svg")
    tgl_lower = _tgl(direction_alignment_tooltip("Bottom", side), "arrow-down.svg")
    tgl_push_left = _tgl(direction_alignment_tooltip("Left", side), "arrow-left.svg")
    tgl_push_right = _tgl(direction_alignment_tooltip("Right", side), "arrow-right.svg")
    side_tag = side.upper()
    btn_get_img = QPushButton("")
    _set_button_icon(btn_get_img, "icons", "lucide", "folder-open.svg")
    apply_icon_only_button(btn_get_img, f"Open-{side_tag}")

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


def _build_display_path_section(side: str) -> dict[str, Any]:
    """Build path display + clear row for one display panel (below direction grid)."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QHBoxLayout,
        QLineEdit,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    path_panel = QWidget()
    layout = QVBoxLayout(path_panel)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)

    input_display = QLineEdit()
    input_display.setReadOnly(True)
    input_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
    input_display.setPlaceholderText(f"{'Left' if side == 'l' else 'Right'} image path")

    path_row = QWidget()
    path_row_layout = QHBoxLayout(path_row)
    path_row_layout.setContentsMargins(0, 0, 0, 0)
    path_row_layout.addWidget(input_display)

    btn_clr = QPushButton("")
    _set_button_icon(btn_clr, "icons", "lucide", "folder-x.svg")
    from harite.gui.views.icon_button_surface import apply_icon_only_button

    apply_icon_only_button(btn_clr, f"Clear-{side.upper()}")

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
        f"path_panel_{side}": path_panel,
    }


def _build_display_panel(side: str) -> dict[str, Any]:
    """Build one full display panel (direction grid + path display + clear button)."""
    from PyQt6.QtWidgets import QVBoxLayout, QWidget

    grid_widgets = _build_display_direction_grid(side)
    path_widgets = _build_display_path_section(side)

    panel = QWidget()
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    layout.addWidget(grid_widgets[f"display_grid_{side}"])
    layout.addWidget(path_widgets[f"path_panel_{side}"])

    return {
        f"input_display_{side}": path_widgets[f"input_display_{side}"],
        f"btn_clr_path_{side}": path_widgets[f"btn_clr_path_{side}"],
        f"panel_{side}": panel,
        **grid_widgets,
        **path_widgets,
    }


def _build_compose_center_column(
    pick_state_label: Any,
    btn_swap: Any,
    *,
    top_row_height: int,
    middle_row_height: int,
    bottom_row_height: int,
) -> QWidget:
    """Center column: pick state (top row) + swap on direction-grid middle row."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QGridLayout, QWidget

    center = QWidget()
    layout = QGridLayout(center)
    layout.setSpacing(6)
    layout.setContentsMargins(0, 0, 0, 0)

    pick_state_label.setMinimumHeight(top_row_height)
    pick_state_label.setMaximumHeight(top_row_height)
    btn_swap.setFixedHeight(middle_row_height)

    bottom_band = QWidget()
    bottom_band.setFixedHeight(bottom_row_height)

    layout.addWidget(pick_state_label, 0, 0, alignment=Qt.AlignmentFlag.AlignHCenter)
    layout.addWidget(btn_swap, 1, 0, alignment=Qt.AlignmentFlag.AlignHCenter)
    layout.addWidget(bottom_band, 2, 0)
    return center


def build_compose_grid_section() -> dict[str, Any]:
    """Build the 3-column compose grid (left panel / center panel / right panel)."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QGridLayout,
        QLabel,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    compose_grid_widget = QWidget()
    grid = QGridLayout(compose_grid_widget)
    grid.setColumnStretch(0, 1)
    grid.setColumnStretch(1, 0)
    grid.setColumnStretch(2, 1)
    grid.setSpacing(24)
    grid.setContentsMargins(0, 0, 0, 0)

    left_grid = _build_display_direction_grid("l")
    right_grid = _build_display_direction_grid("r")
    left_path = _build_display_path_section("l")
    right_path = _build_display_path_section("r")

    pick_state_label = QLabel("")
    pick_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    btn_swap = QPushButton("")
    btn_swap.setToolTip("Swap L/R")
    _set_button_icon(btn_swap, "icons", "lucide", "arrow-left-right.svg")

    top_row_height = left_grid["tgl_upper_l"].sizeHint().height()
    middle_row_height = left_grid["btn_get_img_l"].sizeHint().height()
    bottom_row_height = left_grid["tgl_lower_l"].sizeHint().height()

    center_swap = _build_compose_center_column(
        pick_state_label,
        btn_swap,
        top_row_height=top_row_height,
        middle_row_height=middle_row_height,
        bottom_row_height=bottom_row_height,
    )

    left_column = QWidget()
    left_column_layout = QVBoxLayout(left_column)
    left_column_layout.setContentsMargins(0, 0, 0, 0)
    left_column_layout.setSpacing(8)
    left_column_layout.addWidget(left_grid["display_grid_l"])
    left_column_layout.addWidget(left_path["path_panel_l"])

    right_column = QWidget()
    right_column_layout = QVBoxLayout(right_column)
    right_column_layout.setContentsMargins(0, 0, 0, 0)
    right_column_layout.setSpacing(8)
    right_column_layout.addWidget(right_grid["display_grid_r"])
    right_column_layout.addWidget(right_path["path_panel_r"])

    grid.addWidget(left_column, 0, 0, alignment=Qt.AlignmentFlag.AlignTop)
    grid.addWidget(center_swap, 0, 1, alignment=Qt.AlignmentFlag.AlignTop)
    grid.addWidget(right_column, 0, 2, alignment=Qt.AlignmentFlag.AlignTop)

    left_widgets = {**left_grid, **left_path, "panel_l": left_column}
    right_widgets = {**right_grid, **right_path, "panel_r": right_column}

    return {
        "compose_grid": compose_grid_widget,
        "left_panel": left_column,
        "center_panel": center_swap,
        "right_panel": right_column,
        "pick_state_label": pick_state_label,
        "btn_swap_input_paths": btn_swap,
        **{k: v for k, v in left_widgets.items() if k != "panel_l"},
        **{k: v for k, v in right_widgets.items() if k != "panel_r"},
    }


# ---------------------------------------------------------------------------
# Action cluster
# ---------------------------------------------------------------------------


def _build_preview_group() -> dict[str, Any]:
    """Build the Preview group — thumbnails only (P-04)."""
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

    images_row = QWidget()
    images_row_layout = QHBoxLayout(images_row)
    images_row_layout.setContentsMargins(0, 0, 0, 0)
    images_row_layout.setSpacing(6)

    def _make_preview_thumb() -> QLabel:
        preview_lbl = QLabel("")
        preview_lbl.setFixedSize(160, 90)
        preview_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        preview_lbl.setStyleSheet("background: #222; border: 1px solid #555;")
        return preview_lbl

    preview_left = _make_preview_thumb()
    preview_right = _make_preview_thumb()
    images_row_layout.addWidget(preview_left)
    images_row_layout.addWidget(preview_right)
    group_layout.addWidget(images_row)

    return {
        "preview_group": group,
        "preview_images_row": images_row,
        "preview_left": preview_left,
        "preview_right": preview_right,
    }


def _build_optimize_group() -> dict[str, Any]:
    """Build the Optimize group — button only (P-04)."""
    from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget

    group = QWidget()
    group_layout = QVBoxLayout(group)
    group_layout.setContentsMargins(0, 0, 0, 0)
    group_layout.setSpacing(6)

    optimize_modern_btn = QPushButton("Optimize")
    optimize_modern_btn.setEnabled(False)
    _set_button_icon(optimize_modern_btn, "icons", "lucide", "image.svg")
    group_layout.addWidget(optimize_modern_btn)

    return {
        "optimize_group": group,
        "optimize_modern_btn": optimize_modern_btn,
    }


def _build_apply_group(default_apply_mode: str) -> dict[str, Any]:
    """Build the Apply group — button + mode radios; help via tooltip (P-04)."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QButtonGroup,
        QHBoxLayout,
        QPushButton,
        QRadioButton,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )

    from harite.apply_surface import per_monitor_mode_radio_label, single_file_mode_radio_label
    from harite.gui.views.main_action_surface import apply_apply_mode_tooltips

    group = QWidget()
    group.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
    group_layout = QVBoxLayout(group)
    group_layout.setContentsMargins(0, 0, 0, 0)
    group_layout.setSpacing(6)
    group_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    apply_btn = QPushButton("Apply")
    apply_btn.setEnabled(False)
    apply_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
    _set_button_icon(apply_btn, "icons", "lucide", "wallpaper.svg")

    apply_btn_row = QWidget()
    apply_btn_row_layout = QHBoxLayout(apply_btn_row)
    apply_btn_row_layout.setContentsMargins(0, 0, 0, 0)
    apply_btn_row_layout.addStretch()
    apply_btn_row_layout.addWidget(apply_btn)
    apply_btn_row_layout.addStretch()
    group_layout.addWidget(apply_btn_row)

    apply_mode_row_widget = QWidget()
    apply_mode_row_layout = QHBoxLayout(apply_mode_row_widget)
    apply_mode_row_layout.setContentsMargins(0, 0, 0, 0)
    apply_mode_row_layout.setSpacing(6)
    apply_mode_row_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    rad_apply_per_monitor = QRadioButton(per_monitor_mode_radio_label())
    rad_apply_single = QRadioButton(single_file_mode_radio_label())

    apply_mode_group = QButtonGroup(group)
    apply_mode_group.addButton(rad_apply_per_monitor)
    apply_mode_group.addButton(rad_apply_single)

    initial_mode = (
        "per-monitor-auto-split" if default_apply_mode == "per-monitor-auto-split" else "single-file"
    )
    if initial_mode == "per-monitor-auto-split":
        rad_apply_per_monitor.setChecked(True)
    else:
        rad_apply_single.setChecked(True)

    apply_mode_row_layout.addStretch()
    apply_mode_row_layout.addWidget(rad_apply_per_monitor)
    apply_mode_row_layout.addWidget(rad_apply_single)
    apply_mode_row_layout.addStretch()
    group_layout.addWidget(apply_mode_row_widget, alignment=Qt.AlignmentFlag.AlignHCenter)

    apply_apply_mode_tooltips(
        rad_single=rad_apply_single,
        rad_per_monitor=rad_apply_per_monitor,
        apply_btn=apply_btn,
        mode=initial_mode,
    )

    return {
        "apply_group": group,
        "apply_btn": apply_btn,
        "rad_apply_single": rad_apply_single,
        "rad_apply_per_monitor": rad_apply_per_monitor,
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

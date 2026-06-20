"""Qt Slideshow tab builder for Harite GUI (Phase 5).

Builds the Slideshow tab content:
  - srcdir row: Srcdir-L / Srcdir-R buttons with path labels (centred)
  - controls: Mode (sequential/random) + Interval spin + Start/Stop buttons
  - detail row: slideshow_current_label + slideshow_output_label

Widget naming follows the GTK adapter convention.
"""

from __future__ import annotations

from typing import Any

from harite.gui.resource_access import set_qt_button_icon as _set_button_icon
from harite.gui.views.main_window import REGISTRY_NONE_LABEL


# ---------------------------------------------------------------------------
# Srcdir row
# ---------------------------------------------------------------------------


def _build_srcdir_row() -> dict[str, Any]:
    """Three-column srcdir row (L panel / center Swap / R panel), Main tab parity."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )

    row = QWidget()
    grid = QGridLayout(row)
    grid.setColumnStretch(0, 1)
    grid.setColumnStretch(1, 0)
    grid.setColumnStretch(2, 1)
    grid.setSpacing(24)
    grid.setContentsMargins(0, 0, 0, 0)

    def _build_side_panel(side_key: str, side_label: str) -> dict[str, Any]:
        panel = QWidget()
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        saved_row = QWidget()
        saved_row_layout = QVBoxLayout(saved_row)
        saved_row_layout.setContentsMargins(0, 0, 0, 0)
        saved_row_layout.setSpacing(4)
        saved_label = QLabel("Saved source")
        saved_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        combo = QComboBox()
        combo.addItem(REGISTRY_NONE_LABEL, "")
        saved_row_layout.addWidget(saved_label)
        saved_row_layout.addWidget(combo)

        btn_row = QWidget()
        btn_row_layout = QHBoxLayout(btn_row)
        btn_row_layout.setContentsMargins(0, 0, 0, 0)
        btn_row_layout.addStretch()

        from harite.gui.views.icon_button_surface import apply_icon_only_button

        btn = QPushButton("")
        _set_button_icon(btn, "icons", "lucide", "folder-open.svg")
        apply_icon_only_button(btn, f"Srcdir-{side_label}")
        btn_row_layout.addWidget(btn)
        btn_row_layout.addStretch()

        lbl = QLabel(f"{side_label}: -")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setWordWrap(False)
        lbl.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        btn_clr = QPushButton("")
        _set_button_icon(btn_clr, "icons", "lucide", "folder-x.svg")
        apply_icon_only_button(btn_clr, f"Clear-{side_label}")

        chk_auto_scale = QCheckBox("auto")
        chk_auto_scale.setToolTip(
            "Auto upscale small slideshow source images by short-edge thresholds (MAT-14b)"
        )

        clear_row = QWidget()
        clear_row_layout = QHBoxLayout(clear_row)
        clear_row_layout.setContentsMargins(0, 0, 0, 0)
        clear_row_layout.addStretch()
        clear_row_layout.addWidget(chk_auto_scale)
        clear_row_layout.addWidget(btn_clr)

        layout.addWidget(saved_row)
        layout.addWidget(btn_row)
        layout.addWidget(lbl)
        layout.addWidget(clear_row)

        return {
            f"panel_{side_key}_srcdir": panel,
            f"combo_slideshow_source_{side_key}": combo,
            f"btn_open_srcdir_{side_key}": btn,
            f"slideshow_source_label_{side_key}": lbl,
            f"chk_slideshow_auto_display_scale_{side_key}": chk_auto_scale,
            f"btn_clr_srcdir_{side_key}": btn_clr,
        }

    left = _build_side_panel("l", "L")
    right = _build_side_panel("r", "R")

    center_panel = QWidget()
    center_panel.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
    center_layout = QVBoxLayout(center_panel)
    center_layout.setContentsMargins(0, 0, 0, 0)
    center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    btn_swap = QPushButton("")
    btn_swap.setToolTip("Swap L/R")
    _set_button_icon(btn_swap, "icons", "lucide", "arrow-left-right.svg")
    center_layout.addWidget(btn_swap, alignment=Qt.AlignmentFlag.AlignHCenter)

    grid.addWidget(left["panel_l_srcdir"], 0, 0)
    grid.addWidget(center_panel, 0, 1)
    grid.addWidget(right["panel_r_srcdir"], 0, 2)

    return {
        "srcdir_row": row,
        "left_source_block": left["panel_l_srcdir"],
        "right_source_block": right["panel_r_srcdir"],
        "btn_open_srcdir_l": left["btn_open_srcdir_l"],
        "btn_open_srcdir_r": right["btn_open_srcdir_r"],
        "slideshow_source_label_l": left["slideshow_source_label_l"],
        "slideshow_source_label_r": right["slideshow_source_label_r"],
        "btn_clr_srcdir_l": left["btn_clr_srcdir_l"],
        "btn_clr_srcdir_r": right["btn_clr_srcdir_r"],
        "chk_slideshow_auto_display_scale_l": left["chk_slideshow_auto_display_scale_l"],
        "chk_slideshow_auto_display_scale_r": right["chk_slideshow_auto_display_scale_r"],
        "btn_swap_slideshow_srcdirs": btn_swap,
        "combo_slideshow_source_l": left["combo_slideshow_source_l"],
        "combo_slideshow_source_r": right["combo_slideshow_source_r"],
    }


def _build_slideshow_cursor_row() -> dict[str, Any]:
    """Read-only L/R list cursor chips — bottom-left of Slideshow tab (#507)."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QPalette
    from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 4, 0, 0)
    layout.setSpacing(16)

    muted = QLabel("").palette().color(QPalette.ColorRole.PlaceholderText)
    muted_style = f"color: {muted.name()};"

    cursor_l = QLabel("")
    cursor_l.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    cursor_l.setMaximumWidth(176)
    cursor_l.setVisible(False)
    cursor_l.setStyleSheet(muted_style)

    cursor_r = QLabel("")
    cursor_r.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    cursor_r.setMaximumWidth(176)
    cursor_r.setVisible(False)
    cursor_r.setStyleSheet(muted_style)

    layout.addWidget(cursor_l)
    layout.addWidget(cursor_r)
    layout.addStretch()

    return {
        "slideshow_cursor_row": row,
        "slideshow_cursor_l": cursor_l,
        "slideshow_cursor_r": cursor_r,
    }


def _build_slideshow_keyword_chip_row() -> dict[str, Any]:
    """Read-only CODH/NDL keyword chips — top-right of Slideshow tab."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QPalette
    from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 4, 0, 0)
    layout.addStretch()

    muted_style = ""
    codh_chip = QLabel("")
    codh_chip.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    codh_chip.setVisible(False)
    muted = codh_chip.palette().color(QPalette.ColorRole.PlaceholderText)
    muted_style = f"color: {muted.name()};"
    codh_chip.setStyleSheet(muted_style)

    ndl_chip = QLabel("")
    ndl_chip.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    ndl_chip.setVisible(False)
    ndl_chip.setStyleSheet(muted_style)

    layout.addWidget(codh_chip)
    layout.addSpacing(12)
    layout.addWidget(ndl_chip)

    return {
        "slideshow_codh_keyword_chip_row": row,
        "slideshow_codh_keyword_chip": codh_chip,
        "slideshow_ndl_keyword_chip": ndl_chip,
    }


def _build_profile_row() -> dict[str, Any]:
    """Profile preset combo centred above srcdir grid."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QPixmap
    from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QWidget

    from harite.gui.resource_access import gui_resource_path

    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    profile_icon_label = QLabel()
    profile_icon_label.setToolTip("Saved profile preset")
    with gui_resource_path("icons", "lucide", "bookmark.svg") as icon_path:
        pixmap = QPixmap(str(icon_path))
        profile_icon_label.setPixmap(
            pixmap.scaled(
                16,
                16,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    profile_label = QLabel("Profile")
    combo_slideshow_profile = QComboBox()
    combo_slideshow_profile.addItem(REGISTRY_NONE_LABEL, "")
    combo_slideshow_profile.setToolTip("Selecting a profile applies L/R sources together.")

    layout.addWidget(profile_icon_label)
    layout.addWidget(profile_label)
    layout.addWidget(combo_slideshow_profile)

    return {
        "slideshow_profile_row": row,
        "slideshow_profile_icon_label": profile_icon_label,
        "combo_slideshow_profile": combo_slideshow_profile,
    }


def _build_manage_registry_row() -> dict[str, Any]:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget

    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    btn_manage_source_registry = QPushButton("Manage sources and profiles…")
    _set_button_icon(btn_manage_source_registry, "icons", "lucide", "archive.svg")
    layout.addWidget(btn_manage_source_registry)

    return {
        "slideshow_manage_registry_row": row,
        "btn_manage_source_registry": btn_manage_source_registry,
    }


# ---------------------------------------------------------------------------
# Controls section (interval + start/stop on tab front; mode in drawer)
# ---------------------------------------------------------------------------


def _build_mode_section() -> dict[str, Any]:
    """Mode selector and help row — placed inside the options drawer."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QButtonGroup,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QRadioButton,
        QSpinBox,
        QVBoxLayout,
        QWidget,
    )

    mode_group_host = QWidget()
    mode_group_layout = QVBoxLayout(mode_group_host)
    mode_group_layout.setContentsMargins(0, 0, 0, 0)
    mode_group_layout.setSpacing(6)
    mode_group_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    # -- mode row --
    mode_row = QWidget()
    mode_row_layout = QHBoxLayout(mode_row)
    mode_row_layout.setContentsMargins(0, 0, 0, 0)
    mode_row_layout.setSpacing(8)
    mode_row_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    slideshow_mode_label = QLabel("Mode")
    rad_slideshow_mode_sequential = QRadioButton("sequential")
    rad_slideshow_mode_random = QRadioButton("random")
    rad_slideshow_mode_random.setChecked(True)

    mode_group = QButtonGroup(mode_group_host)
    mode_group.addButton(rad_slideshow_mode_sequential)
    mode_group.addButton(rad_slideshow_mode_random)

    mode_row_layout.addWidget(slideshow_mode_label)
    mode_row_layout.addWidget(rad_slideshow_mode_sequential)
    mode_row_layout.addWidget(rad_slideshow_mode_random)

    # -- mode help row --
    mode_help_row = QWidget()
    mode_help_row_layout = QHBoxLayout(mode_help_row)
    mode_help_row_layout.setContentsMargins(0, 0, 0, 0)
    mode_help_row_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    slideshow_mode_help_label = QLabel("Random rotates images.")
    slideshow_mode_help_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    slideshow_mode_help_label.setWordWrap(True)
    mode_help_row_layout.addWidget(slideshow_mode_help_label)

    mode_group_layout.addWidget(mode_row)
    mode_group_layout.addWidget(mode_help_row)

    return {
        "slideshow_mode_group": mode_group_host,
        "slideshow_mode_row": mode_row,
        "slideshow_mode_help_row": mode_help_row,
        "slideshow_mode_label": slideshow_mode_label,
        "slideshow_mode_help_label": slideshow_mode_help_label,
        "rad_slideshow_mode_sequential": rad_slideshow_mode_sequential,
        "rad_slideshow_mode_random": rad_slideshow_mode_random,
        "_slideshow_mode_group": mode_group,
    }


def _build_interval_controls_section() -> dict[str, Any]:
    """Interval spin and Start/Stop buttons — centred on the tab front."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QHBoxLayout,
        QLabel,
        QPushButton,
        QSpinBox,
        QVBoxLayout,
        QWidget,
    )

    controls_group = QWidget()
    controls_group_layout = QVBoxLayout(controls_group)
    controls_group_layout.setContentsMargins(0, 0, 0, 0)
    controls_group_layout.setSpacing(6)
    controls_group_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    controls_row = QWidget()
    controls_row_layout = QHBoxLayout(controls_row)
    controls_row_layout.setContentsMargins(0, 0, 0, 0)
    controls_row_layout.setSpacing(10)
    controls_row_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    interval_label = QLabel("Interval")

    interval_spin = QSpinBox()
    interval_spin.setMinimum(1)
    interval_spin.setMaximum(86400)
    interval_spin.setSingleStep(1)
    interval_spin.setValue(60)

    btn_daemonize = QPushButton("Slideshow Start")
    _set_button_icon(btn_daemonize, "icons", "lucide", "play.svg")

    btn_cancel_daemonize = QPushButton("Slideshow Stop")
    _set_button_icon(btn_cancel_daemonize, "icons", "lucide", "pause.svg")

    controls_row_layout.addWidget(interval_label)
    controls_row_layout.addWidget(interval_spin)
    controls_row_layout.addWidget(btn_daemonize)
    controls_row_layout.addWidget(btn_cancel_daemonize)

    controls_group_layout.addWidget(controls_row)

    # Outer shell with horizontal stretch
    shell = QWidget()
    shell_layout = QHBoxLayout(shell)
    shell_layout.setContentsMargins(0, 0, 0, 0)
    shell_layout.addStretch()
    shell_layout.addWidget(controls_group)
    shell_layout.addStretch()

    return {
        "slideshow_controls_shell": shell,
        "slideshow_controls_group": controls_group,
        "slideshow_controls_row": controls_row,
        "interval_label": interval_label,
        "interval_spin": interval_spin,
        "btn_daemonize": btn_daemonize,
        "btn_cancel_daemonize": btn_cancel_daemonize,
    }


def _build_startup_slideshow_row() -> dict[str, Any]:
    """Session autostart resume checkbox (#518)."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QCheckBox, QHBoxLayout, QWidget

    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 4, 0, 0)
    layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    chk_startup_slideshow = QCheckBox("Resume slideshow on session startup")
    chk_startup_slideshow.setToolTip(
        "When enabled, a --startup-launch session restart resumes slideshow "
        "if it was running when Harite last exited."
    )
    layout.addWidget(chk_startup_slideshow)

    return {
        "slideshow_startup_row": row,
        "chk_startup_slideshow": chk_startup_slideshow,
    }


def _build_options_drawer_trigger() -> dict[str, Any]:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget

    from harite.gui.views.slideshow_options_drawer import MORE_LABEL, QT_TRIGGER_OBJECT_NAME

    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    btn_slideshow_options_more = QPushButton(MORE_LABEL)
    btn_slideshow_options_more.setObjectName(QT_TRIGGER_OBJECT_NAME)
    _set_button_icon(btn_slideshow_options_more, "icons", "lucide", "arrow-down.svg")
    layout.addWidget(btn_slideshow_options_more)

    return {
        "slideshow_options_trigger_row": row,
        "btn_slideshow_options_more": btn_slideshow_options_more,
    }


def _build_options_drawer() -> dict[str, Any]:
    """Collapsible panel: mode, manage registry, current/output detail."""
    from PyQt6.QtWidgets import QFrame, QSizePolicy, QVBoxLayout, QWidget

    mode_widgets = _build_mode_section()
    manage_widgets = _build_manage_registry_row()
    detail_widgets = _build_detail_row()

    from harite.gui.views.slideshow_options_drawer import QT_DRAWER_OBJECT_NAME

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
    drawer_layout.addWidget(mode_widgets["slideshow_mode_group"])
    drawer_layout.addWidget(manage_widgets["slideshow_manage_registry_row"])
    drawer_layout.addWidget(detail_widgets["slideshow_detail_shell"])

    return {
        "slideshow_options_drawer": drawer,
        "slideshow_options_drawer_top_border": drawer_top_border,
        **mode_widgets,
        **manage_widgets,
        **detail_widgets,
    }


# ---------------------------------------------------------------------------
# Detail row
# ---------------------------------------------------------------------------


def _build_detail_row() -> dict[str, Any]:
    """Current image and output-path status labels, centred."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

    detail_row = QWidget()
    detail_row_layout = QVBoxLayout(detail_row)
    detail_row_layout.setContentsMargins(0, 0, 0, 0)
    detail_row_layout.setSpacing(2)
    detail_row_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    slideshow_current_label = QLabel("Slideshow current: idle")
    slideshow_current_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    slideshow_current_label.setWordWrap(False)
    slideshow_current_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)

    slideshow_output_label = QLabel("Slideshow output: .")
    slideshow_output_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    slideshow_output_label.setWordWrap(False)
    slideshow_output_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)

    detail_row_layout.addWidget(slideshow_current_label)
    detail_row_layout.addWidget(slideshow_output_label)

    shell = QWidget()
    shell_layout = QHBoxLayout(shell)
    shell_layout.setContentsMargins(0, 0, 0, 0)
    shell_layout.addStretch()
    shell_layout.addWidget(detail_row)
    shell_layout.addStretch()

    return {
        "slideshow_detail_shell": shell,
        "slideshow_detail_row": detail_row,
        "slideshow_current_label": slideshow_current_label,
        "slideshow_output_label": slideshow_output_label,
    }


# ---------------------------------------------------------------------------
# Full Slideshow tab assembly
# ---------------------------------------------------------------------------


def build_slideshow_tab() -> dict[str, Any]:
    """Build the complete Slideshow tab widget and return the widget registry.

    Layout (top → bottom, Option B frame-resize parity with Main):
        keyword_chip_row        (top-right CODH/NDL chips, hidden unless keyword preset active)
        profile_row
        srcdir_row          (L/R source grid + Swap)
        controls_shell      (Interval + Start/Stop centred)
        cursor_row          (bottom-left L/R list cursor chips)
        options trigger     ("More slideshow options…")
        options drawer      (Mode, Manage, current/output — hidden by default)

    The tab title label ``slideshow_tab_title`` is kept in the registry so
    signal-wiring code can update it (e.g. "Slideshow (running)").
    """
    from PyQt6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

    slideshow_tab_box = QWidget()
    slideshow_tab_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    tab_layout = QVBoxLayout(slideshow_tab_box)
    tab_layout.setContentsMargins(8, 0, 8, 0)
    tab_layout.setSpacing(0)

    # GTK kept an empty label at the top; keep a logical placeholder
    slideshow_label = QLabel("")

    # Dynamic tab title label (adapter can update text via this reference)
    slideshow_tab_title = QLabel("Slideshow (stopped)")

    chip_widgets = _build_slideshow_keyword_chip_row()
    profile_widgets = _build_profile_row()
    srcdir_widgets = _build_srcdir_row()
    controls_widgets = _build_interval_controls_section()
    startup_widgets = _build_startup_slideshow_row()
    cursor_widgets = _build_slideshow_cursor_row()
    trigger_widgets = _build_options_drawer_trigger()
    drawer_widgets = _build_options_drawer()

    tab_layout.addWidget(chip_widgets["slideshow_codh_keyword_chip_row"], stretch=0)
    tab_layout.addWidget(profile_widgets["slideshow_profile_row"], stretch=0)
    tab_layout.addSpacing(12)
    tab_layout.addWidget(srcdir_widgets["srcdir_row"], stretch=0)
    tab_layout.addSpacing(12)
    tab_layout.addWidget(controls_widgets["slideshow_controls_shell"], stretch=0)
    tab_layout.addWidget(startup_widgets["slideshow_startup_row"], stretch=0)
    tab_layout.addWidget(cursor_widgets["slideshow_cursor_row"], stretch=0)
    tab_layout.addSpacing(8)
    tab_layout.addWidget(trigger_widgets["slideshow_options_trigger_row"], stretch=0)
    tab_layout.addWidget(drawer_widgets["slideshow_options_drawer"], stretch=0)

    return {
        "slideshow_tab_box": slideshow_tab_box,
        "slideshow_label": slideshow_label,
        "slideshow_tab_title": slideshow_tab_title,
        **chip_widgets,
        **profile_widgets,
        **srcdir_widgets,
        **controls_widgets,
        **startup_widgets,
        **cursor_widgets,
        **trigger_widgets,
        **drawer_widgets,
    }

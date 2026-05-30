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


# ---------------------------------------------------------------------------
# Srcdir row
# ---------------------------------------------------------------------------


def _build_srcdir_row() -> dict[str, Any]:
    """Two source-directory selector blocks (L / R) spread across the row."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QHBoxLayout,
        QLabel,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    row = QWidget()
    row_layout = QHBoxLayout(row)
    row_layout.setContentsMargins(0, 0, 0, 0)
    row_layout.setSpacing(0)

    def _make_block(side: str) -> dict[str, Any]:
        block = QWidget()
        layout = QVBoxLayout(block)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        btn = QPushButton(f"Srcdir-{side}")
        _set_button_icon(btn, "icons", "lucide", "folder-open.svg")

        lbl = QLabel(f"{side}: -")
        lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(btn)
        layout.addWidget(lbl)
        return {"block": block, "btn": btn, "lbl": lbl}

    left = _make_block("L")
    right = _make_block("R")

    row_layout.addStretch()
    row_layout.addWidget(left["block"])
    row_layout.addStretch()
    row_layout.addWidget(right["block"])
    row_layout.addStretch()

    return {
        "srcdir_row": row,
        "left_source_block": left["block"],
        "right_source_block": right["block"],
        "btn_open_srcdir_l": left["btn"],
        "btn_open_srcdir_r": right["btn"],
        "slideshow_source_label_l": left["lbl"],
        "slideshow_source_label_r": right["lbl"],
    }


# ---------------------------------------------------------------------------
# Controls section (mode + interval + start/stop)
# ---------------------------------------------------------------------------


def _build_controls_section() -> dict[str, Any]:
    """Mode selector, interval spin, and Start/Stop buttons — all centred."""
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

    controls_group = QWidget()
    controls_group_layout = QVBoxLayout(controls_group)
    controls_group_layout.setContentsMargins(0, 0, 0, 0)
    controls_group_layout.setSpacing(6)
    controls_group_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

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

    mode_group = QButtonGroup(controls_group)
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
    mode_help_row_layout.addWidget(slideshow_mode_help_label)

    # -- controls row: interval + start + stop --
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

    controls_group_layout.addWidget(mode_row)
    controls_group_layout.addWidget(mode_help_row)
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
        "slideshow_mode_row": mode_row,
        "slideshow_mode_help_row": mode_help_row,
        "interval_label": interval_label,
        "interval_spin": interval_spin,
        "slideshow_mode_label": slideshow_mode_label,
        "slideshow_mode_help_label": slideshow_mode_help_label,
        "rad_slideshow_mode_sequential": rad_slideshow_mode_sequential,
        "rad_slideshow_mode_random": rad_slideshow_mode_random,
        "btn_daemonize": btn_daemonize,
        "btn_cancel_daemonize": btn_cancel_daemonize,
        "_slideshow_mode_group": mode_group,
    }


# ---------------------------------------------------------------------------
# Detail row
# ---------------------------------------------------------------------------


def _build_detail_row() -> dict[str, Any]:
    """Current image and output-path status labels, centred."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

    detail_row = QWidget()
    detail_row_layout = QVBoxLayout(detail_row)
    detail_row_layout.setContentsMargins(0, 0, 0, 0)
    detail_row_layout.setSpacing(2)
    detail_row_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    slideshow_current_label = QLabel("Slideshow current: idle")
    slideshow_current_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

    slideshow_output_label = QLabel("Slideshow output: .")
    slideshow_output_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

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

    Layout (top → bottom, with vertical stretch around content):
        [stretch]
        srcdir_row          (Srcdir-L / Srcdir-R centred)
        [spacer ~54 px]
        controls_shell      (Mode + Interval + Start/Stop centred)
        [spacer ~54 px]
        detail_shell        (current / output labels centred)
        [stretch]

    The tab title label ``slideshow_tab_title`` is kept in the registry so
    signal-wiring code can update it (e.g. "Slideshow (running)").
    """
    from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

    slideshow_tab_box = QWidget()
    tab_layout = QVBoxLayout(slideshow_tab_box)
    tab_layout.setContentsMargins(8, 0, 8, 0)
    tab_layout.setSpacing(0)

    # GTK kept an empty label at the top; keep a logical placeholder
    slideshow_label = QLabel("")

    # Dynamic tab title label (adapter can update text via this reference)
    slideshow_tab_title = QLabel("Slideshow (stopped)")

    srcdir_widgets = _build_srcdir_row()
    controls_widgets = _build_controls_section()
    detail_widgets = _build_detail_row()

    tab_layout.addStretch()
    tab_layout.addWidget(srcdir_widgets["srcdir_row"])
    tab_layout.addSpacing(54)
    tab_layout.addWidget(controls_widgets["slideshow_controls_shell"])
    tab_layout.addSpacing(54)
    tab_layout.addWidget(detail_widgets["slideshow_detail_shell"])
    tab_layout.addStretch()

    return {
        "slideshow_tab_box": slideshow_tab_box,
        "slideshow_label": slideshow_label,
        "slideshow_tab_title": slideshow_tab_title,
        **srcdir_widgets,
        **controls_widgets,
        **detail_widgets,
    }

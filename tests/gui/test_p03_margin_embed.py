"""P-03 regression: margin embed must work on single display (Position is not second slot)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

pytest.importorskip("PyQt6")

from PyQt6.QtWidgets import QApplication

from harite.gui.adapters.ui_adapter import (
    RUNTIME_HANDLER_MAP,
    connect_signal_dispatch,
    create_mainwindow_signal_dispatch,
)
from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend
from harite.gui.dual_display_ui import SECOND_SLOT_WIDGET_NAMES
from harite.gui.views.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def _light_pixels_in_band(image, box: tuple[int, int, int, int]) -> int:
    band = image.crop(box)
    return sum(1 for pixel in band.getdata() if pixel[0] > 200 and pixel[1] > 200)


def test_margin_position_radios_not_in_second_slot_list():
    names = set(SECOND_SLOT_WIDGET_NAMES)
    assert "radMarginTextPositionRightTop" not in names
    assert "radMarginTextPositionRightBottom" not in names


def test_single_display_margin_embed_settings_left_bottom(tmp_path: Path, qapp, monkeypatch):
    from PIL import Image

    monkeypatch.setattr(
        "harite.gui.views.main_window.dual_display_detected",
        lambda: False,
    )

    input_image = tmp_path / "input.png"
    Image.new("RGB", (64, 64), (0, 128, 255)).save(input_image)

    window = MainWindow()
    backend = load_qt_runtime_signal_backend()
    dispatch = create_mainwindow_signal_dispatch(
        window,
        tuple(RUNTIME_HANDLER_MAP.keys()),
        handler_map=RUNTIME_HANDLER_MAP,
    )
    connect_signal_dispatch(backend, dispatch)

    monkeypatch.setattr(
        "harite.workspace.detect_displays",
        lambda: [__import__("harite.workspace", fromlist=["Display"]).Display(name="", width=2048, height=1280, x_offset=0)],
    )
    window.form_state.output_dir = str(tmp_path / "out")
    window.input_path_l = str(input_image)
    window._apply_input_paths()

    for spin_name, value in (
        ("left_margin_spin", 100),
        ("right_margin_spin", 100),
        ("top_margin_spin", 200),
        ("bottom_margin_spin", 200),
    ):
        backend._objects[spin_name].setValue(value)

    backend._objects["margin_text_mode_settings"].click()
    backend._objects["margin_position_left_bottom"].click()

    assert window.form_state.embed_info == "params"
    assert window.form_state.embed_position == "left-bottom"
    assert window.form_state.margins == "100,100,200,200"
    assert backend._objects["margin_position_right_bottom"].isEnabled() is True

    assert window.on_optimize() is True
    assert window.last_saved_files

    output = window.last_saved_files[0]
    image = Image.open(output)
    # left-bottom margin band for 2048x1280 with L/R=100, bottom=200
    assert _light_pixels_in_band(image, (100, 1080, 400, 1280)) > 100

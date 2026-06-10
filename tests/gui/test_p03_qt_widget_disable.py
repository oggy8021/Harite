"""P-03: Qt second-slot widgets are disabled when single display is detected."""

from __future__ import annotations

import sys

import pytest

pytest.importorskip("PyQt6")

from PyQt6.QtWidgets import QApplication

from harite.gui.adapters.gui_runtime_owner_sync import sync_non_preview_state_from_owner
from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend
from harite.gui.views.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_qt_second_slot_widgets_disabled_on_single_display(qapp, monkeypatch):
    monkeypatch.setattr(
        "harite.gui.views.main_window.dual_display_detected",
        lambda: False,
    )
    window = MainWindow()
    backend = load_qt_runtime_signal_backend()
    sync_non_preview_state_from_owner(backend, window)

    disabled_aliases = (
        "btnGetImgR",
        "btnClrPathR",
        "btnSwapInputPaths",
        "entPathR",
        "tglPushLeftR",
        "comboSlideshowSourceR",
        "btnOpenSrcdirR",
        "btnClrSrcdirR",
        "btnSwapSlideshowSrcdirs",
        "lblSlideshowSourceR",
    )
    for name in disabled_aliases:
        widget = backend._objects.get(name)
        assert widget is not None, f"missing widget alias: {name}"
        assert widget.isEnabled() is False, name

    # L-side controls stay enabled.
    assert backend._objects["btnGetImgL"].isEnabled() is True
    assert backend._objects["btnClrPathL"].isEnabled() is True

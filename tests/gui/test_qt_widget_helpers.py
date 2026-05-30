"""Tests for qt_widget_helpers.py (Phase 8)."""

from __future__ import annotations

import pytest

pytest.importorskip("PyQt6.QtWidgets")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class _FakeBackend:
    """Minimal backend stub with a widget registry."""

    def __init__(self) -> None:
        self._objects: dict = {}


@pytest.fixture
def backend(qapp):
    return _FakeBackend()


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------


def test_qt_widget_helpers_importable():
    from harite.gui.adapters_qt import qt_widget_helpers  # noqa: F401


# ---------------------------------------------------------------------------
# set_label_text / set_status / set_error / set_feedback
# ---------------------------------------------------------------------------


def test_set_label_text_updates_qlabel(qapp, backend):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_widget_helpers import set_label_text

    lbl = QLabel("")
    backend._objects["myLabel"] = lbl
    set_label_text(backend, "myLabel", "hello")
    assert lbl.text() == "hello"


def test_set_label_text_noop_on_missing(qapp, backend):
    from harite.gui.adapters_qt.qt_widget_helpers import set_label_text

    set_label_text(backend, "nonexistent", "hi")  # must not raise


def test_set_status_updates_lblStatus(qapp, backend):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_widget_helpers import set_status

    lbl = QLabel("")
    backend._objects["lblStatus"] = lbl
    set_status(backend, "state-ok")
    assert lbl.text() == "state-ok"


def test_set_error_updates_lblError(qapp, backend):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_widget_helpers import set_error

    lbl = QLabel("")
    backend._objects["lblError"] = lbl
    set_error(backend, "boom")
    assert lbl.text() == "boom"


def test_set_error_clears_on_none(qapp, backend):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_widget_helpers import set_error

    lbl = QLabel("previous")
    backend._objects["lblError"] = lbl
    set_error(backend, None)
    assert lbl.text() == ""


def test_set_feedback_sets_status_and_error(qapp, backend):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_widget_helpers import set_feedback

    status = QLabel()
    error = QLabel()
    backend._objects["lblStatus"] = status
    backend._objects["lblError"] = error
    set_feedback(backend, phase="Test", state="done", error="oops")
    assert "Test: done" == status.text()
    assert "oops" == error.text()


# ---------------------------------------------------------------------------
# set_entry_text / read_entry_text
# ---------------------------------------------------------------------------


def test_set_entry_text_qlineedit(qapp, backend):
    from PyQt6.QtWidgets import QLineEdit

    from harite.gui.adapters_qt.qt_widget_helpers import set_entry_text

    entry = QLineEdit()
    backend._objects["ent"] = entry
    set_entry_text(backend, "ent", "path/to/file")
    assert entry.text() == "path/to/file"


def test_set_entry_text_qplaintextedit(qapp, backend):
    from PyQt6.QtWidgets import QPlainTextEdit

    from harite.gui.adapters_qt.qt_widget_helpers import set_entry_text

    pte = QPlainTextEdit()
    backend._objects["txt"] = pte
    set_entry_text(backend, "txt", "hello\nworld")
    assert pte.toPlainText() == "hello\nworld"


def test_read_entry_text_qlineedit(qapp, backend):
    from PyQt6.QtWidgets import QLineEdit

    from harite.gui.adapters_qt.qt_widget_helpers import read_entry_text

    entry = QLineEdit()
    entry.setText("abc")
    backend._objects["e"] = entry
    assert read_entry_text(backend, "e") == "abc"


def test_read_entry_text_missing_returns_empty(qapp, backend):
    from harite.gui.adapters_qt.qt_widget_helpers import read_entry_text

    assert read_entry_text(backend, "nope") == ""


# ---------------------------------------------------------------------------
# set_spin_value / read_spin_int
# ---------------------------------------------------------------------------


def test_set_spin_value_and_read(qapp, backend):
    from PyQt6.QtWidgets import QSpinBox

    from harite.gui.adapters_qt.qt_widget_helpers import read_spin_int, set_spin_value

    spin = QSpinBox()
    spin.setRange(0, 9999)
    backend._objects["spn"] = spin
    set_spin_value(backend, "spn", 42)
    assert read_spin_int(backend, "spn") == 42


def test_read_spin_int_missing_returns_zero(qapp, backend):
    from harite.gui.adapters_qt.qt_widget_helpers import read_spin_int

    assert read_spin_int(backend, "missing") == 0


# ---------------------------------------------------------------------------
# set_button_enabled / set_widget_enabled
# ---------------------------------------------------------------------------


def test_set_button_enabled(qapp, backend):
    from PyQt6.QtWidgets import QPushButton

    from harite.gui.adapters_qt.qt_widget_helpers import set_button_enabled

    btn = QPushButton("x")
    backend._objects["btn"] = btn
    set_button_enabled(backend, "btn", False)
    assert not btn.isEnabled()
    set_button_enabled(backend, "btn", True)
    assert btn.isEnabled()


# ---------------------------------------------------------------------------
# set_toggle_active / is_toggle_active
# ---------------------------------------------------------------------------


def test_set_toggle_active_qcheckbox(qapp, backend):
    from PyQt6.QtWidgets import QCheckBox

    from harite.gui.adapters_qt.qt_widget_helpers import is_toggle_active, set_toggle_active

    cb = QCheckBox()
    backend._objects["chk"] = cb
    assert not is_toggle_active(backend, "chk")
    set_toggle_active(backend, "chk", True)
    assert is_toggle_active(backend, "chk")


def test_is_toggle_active_missing_returns_false(qapp, backend):
    from harite.gui.adapters_qt.qt_widget_helpers import is_toggle_active

    assert is_toggle_active(backend, "gone") is False


# ---------------------------------------------------------------------------
# set_notebook_page
# ---------------------------------------------------------------------------


def test_set_notebook_page(qapp, backend):
    from PyQt6.QtWidgets import QTabWidget, QWidget

    from harite.gui.adapters_qt.qt_widget_helpers import set_notebook_page

    tabs = QTabWidget()
    tabs.addTab(QWidget(), "A")
    tabs.addTab(QWidget(), "B")
    tabs.addTab(QWidget(), "C")
    backend._objects["tabs"] = tabs
    set_notebook_page(backend, "tabs", 2)
    assert tabs.currentIndex() == 2


# ---------------------------------------------------------------------------
# format_input_display
# ---------------------------------------------------------------------------


def test_format_input_display_short():
    from harite.gui.adapters_qt.qt_widget_helpers import format_input_display

    assert format_input_display("abc") == "abc"


def test_format_input_display_long():
    from harite.gui.adapters_qt.qt_widget_helpers import format_input_display

    long_path = "/a/" + "b" * 80
    result = format_input_display(long_path)
    assert result.startswith("…")
    assert len(result) <= 61


def test_format_input_display_empty():
    from harite.gui.adapters_qt.qt_widget_helpers import format_input_display

    assert format_input_display("") == ""


# ---------------------------------------------------------------------------
# refresh_slideshow_source_labels
# ---------------------------------------------------------------------------


def test_refresh_slideshow_source_labels(qapp, backend):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_widget_helpers import refresh_slideshow_source_labels

    lbl_l = QLabel()
    lbl_r = QLabel()
    backend._objects["lblSlideshowSourceL"] = lbl_l
    backend._objects["lblSlideshowSourceR"] = lbl_r
    backend._slideshow_srcdir_l = "/tmp/left"
    backend._slideshow_srcdir_r = ""
    refresh_slideshow_source_labels(backend)
    assert "/tmp/left" in lbl_l.text()
    assert "-" in lbl_r.text()

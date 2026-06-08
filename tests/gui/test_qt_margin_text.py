"""Tests for Qt margin text Enter/cursor behavior (MAT-07)."""

from __future__ import annotations

import pytest


def test_read_margin_text_widget_text_reads_qplain_text_edit(qapp):
    from PyQt6.QtWidgets import QPlainTextEdit

    from harite.gui.adapters.gtk_runtime_margin_text import read_margin_text_widget_text

    entry = QPlainTextEdit()
    entry.setPlainText("line1\nline2\n")

    assert read_margin_text_widget_text(entry) == "line1\nline2\n"


def test_set_entry_text_unchanged_preserves_cursor(qapp):
    from PyQt6.QtGui import QTextCursor
    from PyQt6.QtWidgets import QPlainTextEdit

    from harite.gui.adapters_qt.qt_widget_helpers import set_entry_text

    entry = QPlainTextEdit()
    entry.setPlainText("line1\nline2\n")
    cursor = entry.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)
    entry.setTextCursor(cursor)
    end_position = entry.textCursor().position()

    backend = type("Backend", (), {"_objects": {"txtMarginText": entry}})()
    set_entry_text(backend, "txtMarginText", "line1\nline2\n")

    assert entry.toPlainText() == "line1\nline2\n"
    assert entry.textCursor().position() == end_position


def test_margin_text_enter_on_line_two_preserves_cursor(qapp):
    from PyQt6.QtGui import QTextCursor
    from PyQt6.QtWidgets import QPlainTextEdit

    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend
    from harite.gui.views.main_window import MainWindow

    backend = load_qt_runtime_signal_backend()
    window = MainWindow()
    backend._signal_handlers["on_change_margin_text"] = window.on_change_margin_text

    entry = backend._objects["margin_text_entry"]
    assert entry is not None
    backend._objects["margin_text_mode_text"].click()
    entry.setReadOnly(False)

    entry.setPlainText("line1\nline2")
    cursor = entry.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)
    entry.setTextCursor(cursor)

    entry.insertPlainText("\n")
    backend._on_margin_text_changed(entry)

    assert entry.toPlainText() == "line1\nline2\n"
    assert window.form_state.embed_text == "line1\nline2\n"
    assert entry.textCursor().position() == len("line1\nline2\n")


def test_margin_text_enter_guard_blocks_sixth_line(qapp):
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QKeyEvent
    from PyQt6.QtWidgets import QPlainTextEdit

    from harite.gui.adapters_qt.qt_margin_text import install_margin_text_key_handler

    entry = QPlainTextEdit()
    install_margin_text_key_handler(entry)
    entry.setPlainText("1\n2\n3\n4\n5")
    guard = entry._harite_margin_text_enter_guard

    blocked = guard.eventFilter(
        entry,
        QKeyEvent(
            QKeyEvent.Type.KeyPress,
            int(Qt.Key.Key_Return),
            Qt.KeyboardModifier.NoModifier,
        ),
    )

    assert blocked is True
    assert entry.toPlainText() == "1\n2\n3\n4\n5"

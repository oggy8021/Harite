"""Tests for icon-primary button surface helpers (C-04 Wave c)."""

from __future__ import annotations


def test_apply_icon_only_button_qt(qapp):
    from PyQt6.QtWidgets import QPushButton

    from harite.gui.views.icon_button_surface import apply_icon_only_button

    btn = QPushButton("Clear-L")
    apply_icon_only_button(btn, "Clear-L")
    assert btn.text() == ""
    assert btn.toolTip() == "Clear-L"


def test_apply_icon_only_button_gtk_style_label():
    class _FakeBtn:
        def __init__(self):
            self.label = "Open-L"
            self.tooltip_text = ""

        def set_label(self, text):
            self.label = text

        def set_tooltip_text(self, text):
            self.tooltip_text = text

    from harite.gui.views.icon_button_surface import apply_icon_only_button

    btn = _FakeBtn()
    apply_icon_only_button(btn, "Open-L")
    assert btn.label == ""
    assert btn.tooltip_text == "Open-L"

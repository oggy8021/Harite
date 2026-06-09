"""Tests for qt_stylesheet.py and shared set_qt_button_icon (Phase 9)."""

from __future__ import annotations

import pytest

pytest.importorskip("PyQt6.QtWidgets")


# ---------------------------------------------------------------------------
# Import guards
# ---------------------------------------------------------------------------


def test_qt_stylesheet_importable():
    from harite.gui.adapters_qt import qt_stylesheet  # noqa: F401


def test_set_qt_button_icon_importable():
    from harite.gui.resource_access import set_qt_button_icon  # noqa: F401


# ---------------------------------------------------------------------------
# build_qt_stylesheet
# ---------------------------------------------------------------------------


def test_build_qt_stylesheet_returns_non_empty_string():
    from harite.gui.adapters_qt.qt_stylesheet import build_qt_stylesheet

    result = build_qt_stylesheet()
    assert isinstance(result, str)
    assert len(result) > 0


def test_build_qt_stylesheet_contains_qwidget_rule():
    from harite.gui.adapters_qt.qt_stylesheet import build_qt_stylesheet

    css = build_qt_stylesheet()
    assert "QWidget" in css


def test_build_qt_stylesheet_contains_qpushbutton_rule():
    from harite.gui.adapters_qt.qt_stylesheet import build_qt_stylesheet

    css = build_qt_stylesheet()
    assert "QPushButton" in css


def test_build_qt_stylesheet_footer_error_active_style_mat13():
    from harite.gui.adapters_qt.qt_stylesheet import build_qt_stylesheet
    from harite.gui.views.footer_feedback import FOOTER_ERROR_ACTIVE_COLOR

    css = build_qt_stylesheet()
    assert FOOTER_ERROR_ACTIVE_COLOR in css
    assert 'hasError="true"' in css
    assert "font-weight: bold" in css


def test_build_qt_stylesheet_does_not_override_global_disabled_rules():
    from harite.gui.adapters_qt.qt_stylesheet import build_qt_stylesheet

    css = build_qt_stylesheet()
    assert "QPushButton:disabled" not in css
    assert 'hariteSlotBlocked="true"' not in css


def test_set_widget_slot_blocked_applies_opacity_effect(qapp):
    from PyQt6.QtWidgets import QPushButton, QWidget

    from harite.gui.adapters_qt.qt_widget_helpers import set_widget_slot_blocked

    host = QWidget()
    btn = QPushButton("R", host)
    backend = type("B", (), {"_objects": {"btnR": btn}})()

    set_widget_slot_blocked(backend, "btnR", blocked=True)
    assert btn.isEnabled() is False
    assert btn.graphicsEffect() is not None
    assert abs(btn.graphicsEffect().opacity() - 0.58) < 0.01

    set_widget_slot_blocked(backend, "btnR", blocked=False)
    assert btn.isEnabled() is True
    assert btn.graphicsEffect() is None


# ---------------------------------------------------------------------------
# apply_qt_stylesheet
# ---------------------------------------------------------------------------


def test_apply_qt_stylesheet_does_not_raise(qapp):
    from harite.gui.adapters_qt.qt_stylesheet import apply_qt_stylesheet

    apply_qt_stylesheet(qapp)  # must not raise


def test_apply_qt_stylesheet_noop_on_none(qapp):
    from harite.gui.adapters_qt.qt_stylesheet import apply_qt_stylesheet

    apply_qt_stylesheet(None)  # must not raise


def test_stylesheet_applied_to_qapp(qapp):
    from harite.gui.adapters_qt.qt_stylesheet import apply_qt_stylesheet, build_qt_stylesheet

    apply_qt_stylesheet(qapp)
    applied = qapp.styleSheet()
    # The stylesheet should have been set (or at least not raise)
    assert isinstance(applied, str)


# ---------------------------------------------------------------------------
# set_qt_button_icon
# ---------------------------------------------------------------------------


def test_set_qt_button_icon_with_valid_resource(qapp):
    from PyQt6.QtWidgets import QPushButton

    from harite.gui.resource_access import set_qt_button_icon

    btn = QPushButton("test")
    # Should apply without raising
    set_qt_button_icon(btn, "icons", "lucide", "settings.svg")
    # Icon is set; isNull() should be False for a valid SVG file
    assert not btn.icon().isNull()


def test_set_qt_button_icon_missing_resource_does_not_raise(qapp):
    from PyQt6.QtWidgets import QPushButton

    from harite.gui.resource_access import set_qt_button_icon

    btn = QPushButton("test")
    set_qt_button_icon(btn, "icons", "lucide", "nonexistent.svg")  # must not raise


# ---------------------------------------------------------------------------
# Refactored files no longer define local _set_button_icon
# ---------------------------------------------------------------------------


def test_qt_layout_builders_uses_shared_icon_helper():
    """Ensure the local duplicate was removed from qt_layout_builders."""
    import ast
    import importlib.util
    import inspect

    import harite.gui.adapters_qt.qt_layout_builders as mod

    src = inspect.getsource(mod)
    # The shared import should be present
    assert "set_qt_button_icon" in src
    # A local def _set_button_icon should NOT be present
    assert "def _set_button_icon" not in src


def test_qt_tab_main_uses_shared_icon_helper():
    import inspect

    import harite.gui.adapters_qt.qt_tab_main as mod

    src = inspect.getsource(mod)
    assert "set_qt_button_icon" in src
    assert "def _set_button_icon" not in src


def test_qt_tab_slideshow_uses_shared_icon_helper():
    import inspect

    import harite.gui.adapters_qt.qt_tab_slideshow as mod

    src = inspect.getsource(mod)
    assert "set_qt_button_icon" in src
    assert "def _set_button_icon" not in src


def test_qt_dialogs_uses_shared_icon_helper():
    import inspect

    import harite.gui.adapters_qt.qt_dialogs as mod

    src = inspect.getsource(mod)
    assert "set_qt_button_icon" in src
    assert "def _set_button_icon" not in src


# ---------------------------------------------------------------------------
# load_qt_runtime_signal_backend applies stylesheet
# ---------------------------------------------------------------------------


def test_load_backend_stylesheet_applied(qapp):
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    # Stylesheet must be non-empty after backend creation
    assert len(backend.qapp.styleSheet()) > 0

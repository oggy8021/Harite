"""Tests for qt_svg_support.py."""

from __future__ import annotations


def test_audit_qt_svg_support_reports_keys(qapp):
    from harite.gui.adapters_qt.qt_svg_support import audit_qt_svg_support

    report = audit_qt_svg_support()

    assert "svg_image_format" in report
    assert "packaged_svg_icon_loads" in report
    assert "package_hint" in report


def test_warn_missing_qt_svg_support_noop_when_icons_load(monkeypatch, qapp):
    from harite.gui.adapters_qt import qt_svg_support

    monkeypatch.setattr(qt_svg_support, "probe_packaged_svg_icon", lambda: True)
    qt_svg_support.warn_missing_qt_svg_support()


def test_warn_missing_qt_svg_support_logs_on_linux_when_broken(monkeypatch, caplog, qapp):
    import logging

    from harite.gui.adapters_qt import qt_svg_support

    monkeypatch.setattr(qt_svg_support.sys, "platform", "linux")
    monkeypatch.setattr(qt_svg_support, "probe_packaged_svg_icon", lambda: False)

    with caplog.at_level(logging.WARNING):
        qt_svg_support.warn_missing_qt_svg_support()

    assert any("python3-pyqt6.qtsvg" in record.message for record in caplog.records)

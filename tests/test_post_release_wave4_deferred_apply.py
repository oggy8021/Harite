"""Post-release Wave 4: deferred slideshow apply on next tick (#495)."""

from __future__ import annotations

import json

import pytest


def test_running_interval_change_defers_timer_until_tick_consume():
    from harite.gui.views.main_window import MainWindow

    window = MainWindow()
    window.slideshow_running = True
    window.slideshow_interval_seconds = 3600
    window._slideshow_timer_interval_seconds = 3600

    assert window.on_slideshow_interval_change(5) is True
    assert window.slideshow_interval_seconds == 5
    assert window._slideshow_timer_interval_seconds == 3600
    assert "next tick" in window.status_message

    assert window.consume_slideshow_deferred_timer_interval() == 5
    assert window._slideshow_timer_interval_seconds == 5
    assert window.consume_slideshow_deferred_timer_interval() is None


def test_idle_interval_change_has_no_active_timer_interval():
    from harite.gui.views.main_window import MainWindow

    window = MainWindow()
    assert window.on_slideshow_interval_change(45) is True
    assert window.slideshow_interval_seconds == 45
    assert window._slideshow_timer_interval_seconds is None
    assert window.consume_slideshow_deferred_timer_interval() is None


def test_running_auto_display_scale_defers_reapply(monkeypatch):
    from harite.gui.views.main_window import MainWindow

    window = MainWindow()
    window.slideshow_running = True
    reapply_calls: list[int] = []
    monkeypatch.setattr(window, "_reapply_slideshow_if_running", lambda: reapply_calls.append(1))

    window.on_change_slideshow_auto_display_scale("L", True)

    assert window.slideshow_l_auto_display_scale is True
    assert reapply_calls == []
    assert window._slideshow_pending_auto_scale is True
    assert "next tick" in window.status_message


def test_slideshow_stop_clears_deferred_apply_state():
    from harite.gui.views.main_window import MainWindow

    window = MainWindow()
    window.slideshow_running = True
    window._slideshow_timer_interval_seconds = 60
    window._slideshow_pending_auto_scale = True

    assert window.on_slideshow_stop() is True

    assert window._slideshow_timer_interval_seconds is None
    assert window._slideshow_pending_auto_scale is False


def test_deferred_apply_op_log_after_tick(monkeypatch, tmp_path):
    from harite.gui.views.main_window import MainWindow

    log_path = tmp_path / "slideshow-op.jsonl"
    monkeypatch.setenv("HARITE_SLIDESHOW_OP_LOG", str(log_path))

    window = MainWindow()
    window.slideshow_running = True
    window._slideshow_timer_interval_seconds = 60
    window.slideshow_interval_seconds = 12
    window._slideshow_pending_auto_scale = True

    window.log_slideshow_deferred_apply_after_tick(timer_interval_applied=12)

    records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(records) == 1
    record = records[0]
    assert record["step"] == "SLIDESHOW_DEFERRED_APPLY"
    assert record["ok"] is True
    assert record["interval_seconds"] == 12
    assert record["slideshow_auto_display_scale"] is True
    assert window._slideshow_pending_auto_scale is False


def test_qt_timer_event_applies_deferred_interval_after_tick(monkeypatch):
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend
    from harite.gui.views.main_window import MainWindow

    monkeypatch.setattr(MainWindow, "_default_plugin_name", lambda self: "windows")
    monkeypatch.setattr(MainWindow, "_default_output_dir", lambda self: ".")

    window = MainWindow()
    window.slideshow_running = True
    window.slideshow_interval_seconds = 5
    window._slideshow_timer_interval_seconds = 3600

    backend = load_qt_runtime_signal_backend()
    timer_starts: list[int] = []
    monkeypatch.setattr(backend, "_start_slideshow_timer", lambda seconds: timer_starts.append(int(seconds)) or True)

    backend._apply_deferred_slideshow_timer_from_owner(window)

    assert timer_starts == [5]


def test_qt_timer_event_skips_reschedule_when_tick_stops_slideshow(monkeypatch):
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend
    from harite.gui.views.main_window import MainWindow

    monkeypatch.setattr(MainWindow, "_default_plugin_name", lambda self: "windows")
    monkeypatch.setattr(MainWindow, "_default_output_dir", lambda self: ".")

    window = MainWindow()
    backend = load_qt_runtime_signal_backend()
    timer_starts: list[int] = []
    monkeypatch.setattr(backend, "_start_slideshow_timer", lambda seconds: timer_starts.append(int(seconds)) or True)
    monkeypatch.setattr(window, "on_slideshow_tick", lambda: False)

    backend._signal_handlers["on_slideshow_tick"] = window.on_slideshow_tick

    backend._on_slideshow_timer_event()

    assert timer_starts == []

from __future__ import annotations

import pytest

from harite import apply_surface


def test_per_monitor_radio_label_on_windows(monkeypatch):
    monkeypatch.setattr(apply_surface.platform, "system", lambda: "Windows")
    assert apply_surface.per_monitor_mode_radio_label() == "Span"


def test_per_monitor_radio_label_on_linux(monkeypatch):
    monkeypatch.setattr(apply_surface.platform, "system", lambda: "Linux")
    assert apply_surface.per_monitor_mode_radio_label() == "Auto-Split"


def test_preview_result_notes_windows_span_mode(monkeypatch):
    monkeypatch.setattr(apply_surface.platform, "system", lambda: "Windows")
    left, right = apply_surface.preview_result_notes("per-monitor-auto-split")
    assert "monitor region" in left
    assert "monitor region" in right
    assert "auto-split" not in left.lower()


def test_apply_mode_help_windows_span_opt_in(monkeypatch):
    monkeypatch.setattr(apply_surface.platform, "system", lambda: "Windows")
    text = apply_surface.apply_mode_help_text("per-monitor-auto-split", windows_apply_span=True)
    assert "Span" in text
    assert "Harite will switch" in text


def test_dual_display_detected_true_when_two_or_more(monkeypatch):
    monkeypatch.setattr(apply_surface, "count_detected_displays", lambda: 2)
    assert apply_surface.dual_display_detected() is True


def test_dual_display_detected_false_when_single(monkeypatch):
    monkeypatch.setattr(apply_surface, "count_detected_displays", lambda: 1)
    assert apply_surface.dual_display_detected() is False

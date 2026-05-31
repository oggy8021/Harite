from __future__ import annotations

from harite.settings import AppSettings, ApplySettings
from harite.workspace import Display


def test_apply_settings_windows_apply_span_roundtrip():
    settings = ApplySettings(
        plugin_name="windows",
        apply_mode="per-monitor-auto-split",
        windows_apply_span=True,
    )
    data = settings.to_settings_dict()
    restored = ApplySettings.from_settings_dict(data, default_plugin="windows")
    assert restored.windows_apply_span is True
    assert restored.apply_mode == "per-monitor-auto-split"


def test_apply_settings_parses_truthy_span_strings():
    restored = ApplySettings.from_settings_dict(
        {"windows_apply_span": "yes", "apply_mode": "single-file"},
        default_plugin="windows",
    )
    assert restored.windows_apply_span is True


def test_default_apply_mode_windows_two_displays(monkeypatch):
    monkeypatch.setattr(
        "harite.workspace.detect_displays",
        lambda: [
            Display(name="1", width=3840, height=2160, x_offset=0),
            Display(name="2", width=3840, height=2160, x_offset=3840),
        ],
    )
    assert AppSettings._default_apply_mode("windows") == "per-monitor-auto-split"


def test_default_apply_mode_windows_single_display(monkeypatch):
    monkeypatch.setattr(
        "harite.workspace.detect_displays",
        lambda: [Display(name="1", width=3840, height=2160, x_offset=0)],
    )
    assert AppSettings._default_apply_mode("windows") == "single-file"

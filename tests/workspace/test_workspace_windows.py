"""Windows display detection tests (W-03-C)."""

from __future__ import annotations

import platform

import pytest

from harite import workspace
from harite.display_context import build_two_screen_optimize_context


def test_scale_percent_from_effective_dpi():
    assert workspace._scale_percent_from_effective_dpi(96) == 100
    assert workspace._scale_percent_from_effective_dpi(144) == 150
    assert workspace._scale_percent_from_effective_dpi(120) == 125


def test_display_from_win32_monitor_builds_display():
    display = workspace._display_from_win32_monitor(
        name=r"\\.\DISPLAY1",
        left=0,
        top=0,
        right=2560,
        bottom=1440,
        primary=True,
        scale_percent=150,
    )

    assert display.name == r"\\.\DISPLAY1"
    assert display.width == 2560
    assert display.height == 1440
    assert display.x_offset == 0
    assert display.y_offset == 0
    assert display.primary is True
    assert display.scale_percent == 150


def test_detect_windows_uses_enumerator(monkeypatch):
    class User32:
        def SetProcessDpiAwarenessContext(self, _ctx):
            return 1

        def SetProcessDPIAware(self):
            return 1

    expected = [
        workspace.Display(
            name=r"\\.\DISPLAY1",
            width=2560,
            height=1440,
            x_offset=0,
            y_offset=0,
            primary=True,
            scale_percent=150,
        ),
        workspace.Display(
            name=r"\\.\DISPLAY2",
            width=2560,
            height=1440,
            x_offset=2560,
            y_offset=0,
            primary=False,
            scale_percent=150,
        ),
    ]

    monkeypatch.setattr(platform, "system", lambda: "Windows")
    monkeypatch.setattr(workspace, "_win32_user32", lambda: User32())
    monkeypatch.setattr(workspace, "_enumerate_windows_displays", lambda _user32: expected)

    assert workspace.detect_displays() == expected


def test_detect_windows_falls_back_to_system_metrics(monkeypatch):
    class User32:
        def SetProcessDpiAwarenessContext(self, _ctx):
            return 1

        def SetProcessDPIAware(self):
            return 1

        def GetSystemMetrics(self, idx):
            return 1920 if idx == 0 else 1080

        def GetDpiForSystem(self):
            return 144

    monkeypatch.setattr(platform, "system", lambda: "Windows")
    monkeypatch.setattr(workspace, "_enumerate_windows_displays", lambda _user32: [])
    monkeypatch.setattr(workspace, "_win32_user32", lambda: User32())

    displays = workspace.detect_displays()

    assert len(displays) == 1
    assert displays[0].name == ""
    assert displays[0].width == 1920
    assert displays[0].height == 1080
    assert displays[0].primary is True
    assert displays[0].scale_percent == 150


def test_two_screen_context_from_windows_like_displays():
    displays = [
        workspace.Display(
            name=r"\\.\DISPLAY1",
            width=2560,
            height=1440,
            x_offset=0,
            y_offset=0,
            primary=True,
        ),
        workspace.Display(
            name=r"\\.\DISPLAY2",
            width=2560,
            height=1440,
            x_offset=2560,
            y_offset=0,
            primary=False,
        ),
    ]

    context = build_two_screen_optimize_context(displays)

    assert context is not None
    assert context.resolution == (5120, 1440)
    assert context.l_display == (2560, 1440)
    assert context.r_display == (2560, 1440)


@pytest.mark.skipif(platform.system() != "Windows", reason="requires Win32 display API")
def test_detect_displays_on_real_windows_host():
    displays = workspace.detect_displays()

    assert len(displays) >= 1
    assert all(display.width > 0 and display.height > 0 for display in displays)
    assert all(
        display.scale_percent is None or 100 <= display.scale_percent <= 500
        for display in displays
    )
    if len(displays) >= 2:
        names = {display.name for display in displays}
        assert any("DISPLAY" in name.upper() for name in names)

from harite.display_context import TwoScreenOptimizeContext
from harite.optimize_settings import resolve_optimize_display_settings
from harite.workspace import Display


def test_resolve_optimize_display_settings_auto_two_screen(monkeypatch):
    monkeypatch.setattr(
        "harite.optimize_settings.build_two_screen_optimize_context",
        lambda: TwoScreenOptimizeContext(
            displays=(
                Display(name="L", width=1920, height=1080, x_offset=0),
                Display(name="R", width=1280, height=1024, x_offset=1920),
            ),
            resolution=(3200, 1080),
            l_display=(1920, 1080),
            r_display=(1280, 1024),
        ),
    )

    resolved = resolve_optimize_display_settings(
        input_values=["left.jpg", "right.jpg"],
        resolution="auto",
        two_screen=None,
        l_display="auto",
        r_display="auto",
    )

    assert resolved.two_screen is True
    assert resolved.resolution == "3200x1080"
    assert resolved.l_display == "1920x1080"
    assert resolved.r_display == "1280x1024"


def test_resolve_optimize_display_settings_single_display_auto(monkeypatch):
    monkeypatch.setattr("harite.optimize_settings.build_two_screen_optimize_context", lambda: None)
    monkeypatch.setattr(
        "harite.workspace.detect_displays",
        lambda: [Display(name="", width=2560, height=1440, x_offset=0)],
    )

    resolved = resolve_optimize_display_settings(
        input_values=["left.jpg"],
        resolution="auto",
        two_screen=None,
        l_display="auto",
        r_display="auto",
    )

    assert resolved.two_screen is False
    assert resolved.resolution == "2560x1440"


def test_resolve_optimize_display_settings_preserves_explicit_values_without_context(monkeypatch):
    monkeypatch.setattr("harite.optimize_settings.build_two_screen_optimize_context", lambda: None)

    resolved = resolve_optimize_display_settings(
        input_values=["left.jpg", "right.jpg"],
        resolution="1600x900",
        two_screen=True,
        l_display=None,
        r_display=None,
    )

    assert resolved.two_screen is True
    assert resolved.resolution == "1600x900"
    assert resolved.l_display is None
    assert resolved.r_display is None
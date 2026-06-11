import pytest

from harite.display_context import TwoScreenOptimizeContext
from harite.optimize_settings import (
    DUAL_INPUT_REQUIRES_TWO_DISPLAYS,
    DUAL_INPUT_REQUIRES_TWO_SCREEN,
    resolve_optimize_display_settings,
)
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


def test_optimize_settings_roundtrips_display_scale_fields():
    from harite.settings import OptimizeSettings

    loaded = OptimizeSettings.from_settings_dict(
        {
            "l_display_scale": 1.25,
            "r_display_scale": 2,
        }
    )
    assert loaded.l_display_scale == 1.25
    assert loaded.r_display_scale == 2.0
    assert loaded.to_settings_dict()["l_display_scale"] == 1.25
    assert loaded.to_settings_dict()["r_display_scale"] == 2.0


def test_resolve_optimize_display_settings_rejects_dual_input_without_two_displays(monkeypatch):
    monkeypatch.setattr("harite.optimize_settings.build_two_screen_optimize_context", lambda: None)

    with pytest.raises(ValueError, match="two detected displays"):
        resolve_optimize_display_settings(
            input_values=["left.jpg", "right.jpg"],
            resolution="auto",
            two_screen=None,
            l_display="auto",
            r_display="auto",
        )


def test_resolve_optimize_display_settings_rejects_dual_input_with_two_screen_off(monkeypatch):
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

    with pytest.raises(ValueError, match="two-screen mode"):
        resolve_optimize_display_settings(
            input_values=["left.jpg", "right.jpg"],
            resolution="auto",
            two_screen=False,
            l_display="auto",
            r_display="auto",
        )

    assert DUAL_INPUT_REQUIRES_TWO_SCREEN.startswith("Two input images require two-screen")
    assert DUAL_INPUT_REQUIRES_TWO_DISPLAYS.startswith("Two input images require two detected")


def test_optimize_settings_maps_legacy_four_x_to_two_x():
    from harite.settings import OptimizeSettings

    loaded = OptimizeSettings.from_settings_dict({"l_display_scale": 4})
    assert loaded.l_display_scale == 2.0
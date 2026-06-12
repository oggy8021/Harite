import pytest

from harite.display_context import TwoScreenOptimizeContext
from harite.optimize_settings import (
    DUAL_INPUT_REQUIRES_TWO_DISPLAYS,
    normalize_canvas_scale_percent,
    resolve_optimize_display_settings,
)
from harite.workspace import Display


def test_resolve_optimize_display_settings_dual_auto(monkeypatch):
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
        canvas_scale_percent=100,
    )

    assert resolved.two_screen is True
    assert resolved.resolution == "3200x1080"
    assert resolved.l_display == "1920x1080"
    assert resolved.r_display == "1280x1024"
    assert resolved.canvas_scale_percent == 100


def test_resolve_optimize_display_settings_dual_scaled(monkeypatch):
    monkeypatch.setattr(
        "harite.optimize_settings.build_two_screen_optimize_context",
        lambda: TwoScreenOptimizeContext(
            displays=(
                Display(name="L", width=1920, height=1080, x_offset=0),
                Display(name="R", width=1920, height=1080, x_offset=1920),
            ),
            resolution=(3840, 1080),
            l_display=(1920, 1080),
            r_display=(1920, 1080),
        ),
    )

    resolved = resolve_optimize_display_settings(
        input_values=["left.jpg", "right.jpg"],
        canvas_scale_percent=50,
    )

    assert resolved.resolution == "1920x540"
    assert resolved.l_display == "1920x1080"
    assert resolved.r_display == "1920x1080"


def test_resolve_optimize_display_settings_single_display_auto(monkeypatch):
    monkeypatch.setattr("harite.optimize_settings.build_two_screen_optimize_context", lambda: None)
    monkeypatch.setattr(
        "harite.workspace.detect_displays",
        lambda: [Display(name="", width=2560, height=1440, x_offset=0)],
    )

    resolved = resolve_optimize_display_settings(
        input_values=["left.jpg"],
        canvas_scale_percent=100,
    )

    assert resolved.two_screen is False
    assert resolved.resolution == "2560x1440"


def test_resolve_optimize_display_settings_rejects_dual_input_without_two_displays(monkeypatch):
    monkeypatch.setattr("harite.optimize_settings.build_two_screen_optimize_context", lambda: None)

    with pytest.raises(ValueError, match="two detected displays"):
        resolve_optimize_display_settings(
            input_values=["left.jpg", "right.jpg"],
            canvas_scale_percent=100,
        )

    assert DUAL_INPUT_REQUIRES_TWO_DISPLAYS.startswith("Two input images require two detected")


def test_optimize_settings_roundtrips_display_scale_fields():
    from harite.settings import OptimizeSettings

    loaded = OptimizeSettings.from_settings_dict(
        {
            "l_display_scale": 1.25,
            "r_display_scale": 2,
            "canvas_scale_percent": 75,
        }
    )
    assert loaded.l_display_scale == 1.25
    assert loaded.r_display_scale == 2.0
    assert loaded.canvas_scale_percent == 75
    assert loaded.to_settings_dict()["canvas_scale_percent"] == 75


def test_optimize_settings_ignores_legacy_geometry_keys():
    from harite.settings import OptimizeSettings

    loaded = OptimizeSettings.from_settings_dict(
        {
            "resolution": "9999x9999",
            "two_screen": True,
            "l_display": "800x600",
            "canvas_scale_percent": 80,
        }
    )
    assert loaded.canvas_scale_percent == 80


def test_normalize_canvas_scale_percent_bounds():
    assert normalize_canvas_scale_percent(100) == 100
    assert normalize_canvas_scale_percent(None) == 100
    with pytest.raises(ValueError):
        normalize_canvas_scale_percent(0)
    with pytest.raises(ValueError):
        normalize_canvas_scale_percent(101)


def test_optimize_settings_maps_legacy_four_x_to_two_x():
    from harite.settings import OptimizeSettings

    loaded = OptimizeSettings.from_settings_dict({"l_display_scale": 4})
    assert loaded.l_display_scale == 2.0

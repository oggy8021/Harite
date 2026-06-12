from harite.settings import AppSettings


def test_app_settings_round_trip_canvas_scale_and_slideshow():
    settings = AppSettings.from_settings_dict(
        {
            "canvas_scale_percent": 80,
            "plugin": "linux",
            "apply_mode": "per-monitor-auto-split",
            "slideshow_interval_seconds": 120,
            "slideshow_mode": "random",
            "slideshow_srcdir_l": "/slideshow/left",
            "slideshow_srcdir_r": "/slideshow/right",
            "slideshow_l_auto_display_scale": True,
            "slideshow_r_auto_display_scale": False,
        },
        default_plugin="windows",
    )

    exported = settings.to_settings_dict()

    assert exported["canvas_scale_percent"] == 80
    assert "resolution" not in exported
    assert "two_screen" not in exported
    assert exported["align"] == ["center", "center"]
    assert exported["valign"] == ["center", "center"]
    assert exported["background_color"] == "#1E1E1E"
    assert exported["plugin"] == "linux"
    assert exported["apply_mode"] == "per-monitor-auto-split"
    assert exported["slideshow_interval_seconds"] == 120
    assert exported["slideshow_mode"] == "random"
    assert exported["slideshow_srcdir_l"] == "/slideshow/left"
    assert exported["slideshow_srcdir_r"] == "/slideshow/right"
    assert exported["slideshow_l_auto_display_scale"] is True
    assert exported["slideshow_r_auto_display_scale"] is False

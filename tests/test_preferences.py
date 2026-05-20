from harite.settings import AppSettings


def test_app_settings_round_trip_settings_with_auto_values():
    settings = AppSettings.from_settings_dict(
        {
            "resolution": "auto",
            "two_screen": "auto",
            "l_display": "auto",
            "r_display": "auto",
            "plugin": "linux",
            "apply_mode": "per-monitor-auto-split",
            "slideshow_interval_seconds": 120,
            "slideshow_mode": "random",
            "slideshow_srcdir_l": "/slideshow/left",
            "slideshow_srcdir_r": "/slideshow/right",
        },
        default_plugin="windows",
    )

    exported = settings.to_settings_dict()

    assert exported["resolution"] == "auto"
    assert exported["two_screen"] == "auto"
    assert exported["l_display"] == "auto"
    assert exported["r_display"] == "auto"
    assert exported["align"] == ["center", "center"]
    assert exported["valign"] == ["center", "center"]
    assert exported["background_color"] == "#1E1E1E"
    assert exported["plugin"] == "linux"
    assert exported["apply_mode"] == "per-monitor-auto-split"
    assert exported["slideshow_interval_seconds"] == 120
    assert exported["slideshow_mode"] == "random"
    assert exported["slideshow_srcdir_l"] == "/slideshow/left"
    assert exported["slideshow_srcdir_r"] == "/slideshow/right"
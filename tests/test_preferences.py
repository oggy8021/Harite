from harite.preferences import AppPreferences


def test_app_preferences_round_trip_config_with_auto_values():
    prefs = AppPreferences.from_config_dict(
        {
            "resolution": "auto",
            "two_screen": "auto",
            "l_display": "auto",
            "r_display": "auto",
            "plugin": "linux",
            "apply_mode": "per-monitor-auto-split",
            "watch_interval_seconds": 120,
            "watch_srcdir_l": "/watch/left",
            "watch_srcdir_r": "/watch/right",
        },
        default_plugin="windows",
    )

    exported = prefs.to_config_dict()

    assert exported["resolution"] == "auto"
    assert exported["two_screen"] == "auto"
    assert exported["l_display"] == "auto"
    assert exported["r_display"] == "auto"
    assert exported["align"] == ["center", "center"]
    assert exported["valign"] == ["center", "center"]
    assert exported["background_color"] == "#1E1E1E"
    assert exported["plugin"] == "linux"
    assert exported["apply_mode"] == "per-monitor-auto-split"
    assert exported["watch_interval_seconds"] == 120
    assert exported["watch_srcdir_l"] == "/watch/left"
    assert exported["watch_srcdir_r"] == "/watch/right"
from harite import cli


def test_resolve_plugin_name_uses_settings_over_os_default(monkeypatch) -> None:
    monkeypatch.setattr(cli, "_default_plugin_name", lambda: "linux")

    assert cli._resolve_plugin_name({"plugin": "windows"}) == "windows"


def test_resolve_plugin_name_falls_back_to_os_default(monkeypatch) -> None:
    monkeypatch.setattr(cli, "_default_plugin_name", lambda: "windows")

    assert cli._resolve_plugin_name({}) == "windows"

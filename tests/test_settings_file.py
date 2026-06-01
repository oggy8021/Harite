from __future__ import annotations

from pathlib import Path

import pytest

from harite.settings_file import resolve_default_settings_path


def test_resolve_default_settings_path_linux_with_xdg_config_home(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    xdg = tmp_path / "xdg"
    monkeypatch.setattr("harite.settings_file.sys.platform", "linux")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg))

    assert resolve_default_settings_path() == xdg / "harite" / "harite-settings.json"


def test_resolve_default_settings_path_linux_default_config_home(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr("harite.settings_file.sys.platform", "linux")
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setattr("harite.settings_file.Path.home", lambda: tmp_path)

    assert resolve_default_settings_path() == tmp_path / ".config" / "harite" / "harite-settings.json"


def test_resolve_default_settings_path_windows_uses_appdata(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    appdata = tmp_path / "Roaming"
    appdata.mkdir()
    monkeypatch.setattr("harite.settings_file.sys.platform", "win32")
    monkeypatch.setenv("APPDATA", str(appdata))

    assert resolve_default_settings_path() == appdata / "harite" / "harite-settings.json"


def test_resolve_default_settings_path_windows_falls_back_when_appdata_unset(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    home = tmp_path / "user"
    home.mkdir()
    monkeypatch.setattr("harite.settings_file.sys.platform", "win32")
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setattr("harite.settings_file.Path.home", lambda: home)

    assert resolve_default_settings_path() == home / "AppData" / "Roaming" / "harite" / "harite-settings.json"

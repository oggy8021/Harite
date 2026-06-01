from __future__ import annotations

from pathlib import Path

import pytest

from harite.sources_file import resolve_default_sources_path


def test_resolve_default_sources_path_linux_with_xdg_config_home(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    xdg = tmp_path / "xdg"
    monkeypatch.setattr("harite.sources_file.sys.platform", "linux")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg))

    assert resolve_default_sources_path() == xdg / "harite" / "sources.json"


def test_resolve_default_sources_path_windows_uses_appdata(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    appdata = tmp_path / "Roaming"
    appdata.mkdir()
    monkeypatch.setattr("harite.sources_file.sys.platform", "win32")
    monkeypatch.setenv("APPDATA", str(appdata))

    assert resolve_default_sources_path() == appdata / "harite" / "sources.json"

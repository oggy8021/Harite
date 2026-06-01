from __future__ import annotations

from pathlib import Path

import pytest

from harite.sources_file import (
    LEGACY_SOURCES_CATALOG_FILENAME,
    SOURCES_CATALOG_FILENAME,
    resolve_default_sources_path,
    resolve_sources_path_for_load,
)


def test_resolve_default_sources_path_linux_with_xdg_config_home(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    xdg = tmp_path / "xdg"
    monkeypatch.setattr("harite.sources_file.sys.platform", "linux")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg))

    assert resolve_default_sources_path() == xdg / "harite" / SOURCES_CATALOG_FILENAME


def test_resolve_default_sources_path_windows_uses_appdata(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    appdata = tmp_path / "Roaming"
    appdata.mkdir()
    monkeypatch.setattr("harite.sources_file.sys.platform", "win32")
    monkeypatch.setenv("APPDATA", str(appdata))

    assert resolve_default_sources_path() == appdata / "harite" / SOURCES_CATALOG_FILENAME


def test_resolve_sources_path_for_load_prefers_legacy_when_new_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    harite_dir = tmp_path / "harite"
    harite_dir.mkdir()
    legacy = harite_dir / LEGACY_SOURCES_CATALOG_FILENAME
    legacy.write_text('{"schema_version": 1, "sources": [], "profiles": []}\n', encoding="utf-8")
    monkeypatch.setattr("harite.sources_file._harite_config_dir", lambda: harite_dir)

    assert resolve_sources_path_for_load() == legacy


def test_load_catalog_reads_legacy_filename(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from harite.sources import add_source, load_catalog, save_catalog

    harite_dir = tmp_path / "harite"
    harite_dir.mkdir()
    left = tmp_path / "left"
    left.mkdir()
    monkeypatch.setattr("harite.sources_file._harite_config_dir", lambda: harite_dir)

    legacy = harite_dir / LEGACY_SOURCES_CATALOG_FILENAME
    catalog = load_catalog(legacy)
    add_source(catalog, name="Legacy", path=left)
    save_catalog(catalog, legacy)

    loaded = load_catalog()
    assert len(loaded.sources) == 1
    assert loaded.sources[0].name == "Legacy"


def test_save_catalog_uses_harite_sources_filename(tmp_path: Path) -> None:
    from harite.sources import empty_catalog, save_catalog

    target = tmp_path / "harite" / SOURCES_CATALOG_FILENAME
    save_catalog(empty_catalog(), target)
    assert target.is_file()

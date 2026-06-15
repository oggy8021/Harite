from __future__ import annotations

from pathlib import Path

import pytest

from harite.sources_file import SOURCES_CATALOG_FILENAME, resolve_default_sources_path


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


def test_save_catalog_uses_harite_sources_filename(tmp_path: Path) -> None:
    from harite.sources import empty_catalog, save_catalog

    target = tmp_path / "harite" / SOURCES_CATALOG_FILENAME
    save_catalog(empty_catalog(), target)
    assert target.is_file()


def test_load_sources_json_empty_file_returns_empty_payload(tmp_path: Path) -> None:
    from harite.sources_file import empty_sources_json_payload, load_sources_json

    target = tmp_path / SOURCES_CATALOG_FILENAME
    target.write_bytes(b"")
    assert load_sources_json(target) == empty_sources_json_payload()


def test_load_sources_json_whitespace_only_returns_empty_payload(tmp_path: Path) -> None:
    from harite.sources_file import empty_sources_json_payload, load_sources_json

    target = tmp_path / SOURCES_CATALOG_FILENAME
    target.write_text("  \n\t", encoding="utf-8")
    assert load_sources_json(target) == empty_sources_json_payload()


def test_load_sources_json_invalid_non_empty_still_raises(tmp_path: Path) -> None:
    from harite.sources_file import load_sources_json

    target = tmp_path / SOURCES_CATALOG_FILENAME
    target.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid JSON sources catalog"):
        load_sources_json(target)


def test_load_catalog_empty_file_returns_empty_catalog(tmp_path: Path) -> None:
    from harite.sources import empty_catalog, load_catalog

    target = tmp_path / SOURCES_CATALOG_FILENAME
    target.write_bytes(b"")
    catalog = load_catalog(target)
    assert catalog.schema_version == empty_catalog().schema_version
    assert catalog.sources == []
    assert catalog.profiles == []


def test_materialize_empty_sources_file_bootstraps_presets(tmp_path: Path) -> None:
    from harite.gui.adapters_qt.qt_source_catalog import materialize_source_catalog_at_path

    target = tmp_path / SOURCES_CATALOG_FILENAME
    target.write_bytes(b"")
    catalog = materialize_source_catalog_at_path(target)
    assert catalog.sources
    assert target.read_text(encoding="utf-8").strip()
    assert '"schema_version": 1' in target.read_text(encoding="utf-8")

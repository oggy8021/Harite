"""C-01-E-KW: CODH user keyword in settings and sync."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.request import Request

import pytest

from harite.sources import empty_catalog, import_preset_source, update_source
from harite.sources_preset import canonical_preset_source_notes, load_source_presets, repair_preset_source_notes
from harite.sources_remote import (
    CODH_KEYWORD_DEFAULT,
    CODH_KEYWORD_NOTE_PREFIX,
    CODH_KEYWORD_SETTINGS_KEY,
    apply_codh_keyword_to_settings,
    codh_keyword_from_notes,
    codh_keyword_from_settings,
    migrate_codh_keyword_notes_to_settings,
    format_remote_sync_error,
    resolve_codh_keyword,
    strip_codh_keyword_from_notes,
    sync_remote_source,
    validate_codh_keyword,
)
from harite.settings_file import save_settings

def _legacy_notes_with_keyword(notes: str, keyword: str) -> str:
    return f"{notes}\n{CODH_KEYWORD_NOTE_PREFIX}{keyword}"


_JPEG_BYTES = b"\xff\xd8\xff" + b"\x00" * 16
_CODH_RESULTS = {
    "total": 3,
    "results": [{"canvasThumbnail": "https://example.test/iiif/x/200,/0/default.jpg"}],
}


def test_validate_codh_keyword_rejects_empty_and_long() -> None:
    assert validate_codh_keyword("桜") == "桜"
    with pytest.raises(ValueError, match="empty"):
        validate_codh_keyword("   ")
    with pytest.raises(ValueError, match="exceeds"):
        validate_codh_keyword("a" * 17)


def test_bundled_keyword_preset_json_has_no_machine_keyword_line() -> None:
    presets = load_source_presets()
    for preset_id in ("codh-edo-spots-keyword", "codh-edo-shops-keyword"):
        template = next(item for item in presets.sources if item.preset_id == preset_id)
        assert CODH_KEYWORD_NOTE_PREFIX not in template.notes


def test_canonical_preset_notes_exclude_keyword_line() -> None:
    presets = load_source_presets()
    template = next(item for item in presets.sources if item.preset_id == "codh-edo-spots-keyword")
    assert CODH_KEYWORD_NOTE_PREFIX not in canonical_preset_source_notes(template)


def test_keyword_preset_import_does_not_store_keyword_in_notes(tmp_path: Path) -> None:
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-spots-keyword", cache_root=tmp_path / "cache")
    assert CODH_KEYWORD_NOTE_PREFIX not in entry.notes


def test_migrate_codh_keyword_notes_to_settings(tmp_path: Path) -> None:
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-spots-keyword", cache_root=tmp_path / "cache")
    entry.notes = _legacy_notes_with_keyword(entry.notes, "飛鳥山")
    settings: dict[str, Any] = {}
    settings, catalog_changed, settings_changed = migrate_codh_keyword_notes_to_settings(catalog, settings)
    assert catalog_changed is True
    assert settings_changed is True
    assert settings[CODH_KEYWORD_SETTINGS_KEY] == "飛鳥山"
    assert codh_keyword_from_notes(entry.notes) is None


def test_repair_preset_source_notes_strips_legacy_keyword_line(tmp_path: Path) -> None:
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-spots-keyword", cache_root=tmp_path / "cache")
    entry.notes = _legacy_notes_with_keyword(entry.notes, "梅")
    presets = load_source_presets()
    assert repair_preset_source_notes(catalog, preset_catalog=presets) is True
    assert CODH_KEYWORD_NOTE_PREFIX not in entry.notes


def test_codh_spots_keyword_sync_reads_settings(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    seen: list[str] = []

    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        seen.append(target)
        if "mp.ex.nii.ac.jp/api/edo-spots/search" in target:

            class _Codh:
                def read(self) -> bytes:
                    return json.dumps(_CODH_RESULTS).encode("utf-8")

                def __enter__(self) -> "_Codh":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Codh()
        if target.startswith("https://example.test/iiif/"):

            class _Img:
                def read(self) -> bytes:
                    return _JPEG_BYTES

                def __enter__(self) -> "_Img":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Img()
        raise AssertionError(target)

    settings_path = tmp_path / "harite-settings.json"
    save_settings(settings_path, apply_codh_keyword_to_settings({}, "花火"))
    monkeypatch.setattr("harite.sources_remote.urlopen", fake_urlopen)
    monkeypatch.setattr("harite.sources_remote.random.randint", lambda _a, _b: 1)
    monkeypatch.setattr("harite.settings_file.resolve_default_settings_path", lambda: settings_path)

    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-spots-keyword", cache_root=tmp_path / "cache")
    sync_remote_source(catalog, entry.id, cache_root=tmp_path / "cache")

    search_urls = [u for u in seen if "edo-spots/search" in u]
    assert search_urls
    assert "where=" in search_urls[-1]
    assert "where_metadata_label" not in search_urls[-1]
    assert (Path(entry.path) / "latest.jpg").is_file()


def test_resolve_codh_keyword_defaults_without_settings(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing-settings.json"
    monkeypatch.setattr("harite.settings_file.resolve_default_settings_path", lambda: missing)
    assert resolve_codh_keyword() == CODH_KEYWORD_DEFAULT


def test_codh_keyword_from_settings() -> None:
    assert codh_keyword_from_settings({}) == CODH_KEYWORD_DEFAULT
    assert codh_keyword_from_settings({CODH_KEYWORD_SETTINGS_KEY: "飛鳥山"}) == "飛鳥山"


def test_format_remote_sync_error_includes_side_and_source_name() -> None:
    cause = ValueError("CODH search returned no canvases")
    err = format_remote_sync_error("R", "江戸買物（キーワード）", cause)
    assert str(err) == "remote sync failed (R — 江戸買物（キーワード）): CODH search returned no canvases"


def test_format_remote_sync_error_without_side() -> None:
    cause = ValueError("CODH search returned no canvases")
    err = format_remote_sync_error(None, "江戸観光（キーワード）", cause)
    assert str(err) == "remote sync failed (江戸観光（キーワード）): CODH search returned no canvases"


def test_strip_codh_keyword_from_notes() -> None:
    notes = "harite-preset:x\n出典：CODH\nharite-codh-keyword:桜"
    assert strip_codh_keyword_from_notes(notes) == "harite-preset:x\n出典：CODH"

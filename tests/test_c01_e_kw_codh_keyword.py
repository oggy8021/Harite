"""C-01-E-KW: CODH user keyword in notes and sync."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.request import Request

import pytest

from harite.sources import empty_catalog, import_preset_source
from harite.sources_preset import canonical_preset_source_notes, load_source_presets, repair_preset_source_notes
from harite.sources_remote import (
    CODH_KEYWORD_DEFAULT,
    CODH_KEYWORD_NOTE_PREFIX,
    codh_keyword_from_notes,
    sync_remote_source,
    upsert_codh_keyword_in_notes,
    validate_codh_keyword,
)

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


def test_upsert_codh_keyword_in_notes_replaces_line() -> None:
    notes = "harite-preset:codh-edo-spots-keyword\n出典：CODH\nharite-codh-keyword:桜"
    updated = upsert_codh_keyword_in_notes(notes, "花火")
    assert codh_keyword_from_notes(updated) == "花火"
    assert updated.count(CODH_KEYWORD_NOTE_PREFIX) == 1


def test_bundled_keyword_preset_json_has_no_machine_keyword_line() -> None:
    presets = load_source_presets()
    for preset_id in ("codh-edo-spots-keyword", "codh-edo-shops-keyword"):
        template = next(item for item in presets.sources if item.preset_id == preset_id)
        assert CODH_KEYWORD_NOTE_PREFIX not in template.notes


def test_canonical_preset_notes_injects_default_keyword() -> None:
    presets = load_source_presets()
    template = next(item for item in presets.sources if item.preset_id == "codh-edo-spots-keyword")
    assert codh_keyword_from_notes(canonical_preset_source_notes(template)) == CODH_KEYWORD_DEFAULT


def test_keyword_preset_import_includes_default_keyword(tmp_path: Path) -> None:
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-spots-keyword", cache_root=tmp_path / "cache")
    assert codh_keyword_from_notes(entry.notes) == CODH_KEYWORD_DEFAULT


def test_repair_preset_source_notes_preserves_user_keyword(tmp_path: Path) -> None:
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-spots-keyword", cache_root=tmp_path / "cache")
    entry.notes = upsert_codh_keyword_in_notes(entry.notes, "梅")
    presets = load_source_presets()
    assert repair_preset_source_notes(catalog, preset_catalog=presets) is False
    assert codh_keyword_from_notes(entry.notes) == "梅"


def test_codh_spots_keyword_sync_uses_metadata_in_url(
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

    monkeypatch.setattr("harite.sources_remote.urlopen", fake_urlopen)
    monkeypatch.setattr("harite.sources_remote.random.randint", lambda _a, _b: 1)

    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-spots-keyword", cache_root=tmp_path / "cache")
    entry.notes = upsert_codh_keyword_in_notes(entry.notes, "花火")
    sync_remote_source(catalog, entry.id, cache_root=tmp_path / "cache")

    search_urls = [u for u in seen if "edo-spots/search" in u]
    assert search_urls
    assert "where_metadata_label" in search_urls[-1]
    assert "where_metadata_value" in search_urls[-1]
    assert (Path(entry.path) / "latest.jpg").is_file()

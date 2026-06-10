"""C-01-E-KW-NDL: NDL user keyword in settings and sync."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

import pytest

from harite.sources import empty_catalog, import_preset_source
from harite.sources_remote import (
    NDL_KEYWORD_DEFAULT,
    NDL_KEYWORD_SETTINGS_KEY,
    NDL_SEARCHBYTEXT_URL,
    ndl_keyword_from_settings,
    resolve_ndl_keyword,
    save_ndl_keyword_settings,
    sync_remote_source,
    validate_ndl_keyword,
)
from harite.settings_file import save_settings
from tests.remote_sync_http_mocks import JPEG_BYTES, install_ndl_codh_urlopen_mock


def test_validate_ndl_keyword_rejects_empty_and_long() -> None:
    assert validate_ndl_keyword("妖怪") == "妖怪"
    with pytest.raises(ValueError, match="empty"):
        validate_ndl_keyword("   ")
    with pytest.raises(ValueError, match="exceeds"):
        validate_ndl_keyword("a" * 17)


def test_ndl_keyword_from_settings_uses_default() -> None:
    assert ndl_keyword_from_settings({}) == NDL_KEYWORD_DEFAULT
    assert ndl_keyword_from_settings({NDL_KEYWORD_SETTINGS_KEY: "  桜  "}) == "桜"


def test_ndl_keyword_preset_sync_writes_latest_jpg(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    install_ndl_codh_urlopen_mock(monkeypatch)
    settings_path = tmp_path / "harite-settings.json"
    save_settings(settings_path, {NDL_KEYWORD_SETTINGS_KEY: "ペンギン"})
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "ndl-search-keyword", cache_root=cache_root)

    sync_remote_source(catalog, entry.id, cache_root=cache_root)

    latest = Path(entry.path) / "latest.jpg"
    assert latest.is_file()
    assert latest.read_bytes() == JPEG_BYTES


def test_resolve_ndl_keyword_reads_settings_file(tmp_path: Path) -> None:
    settings_path = tmp_path / "harite-settings.json"
    save_ndl_keyword_settings(settings_path, "飛鳥山")
    assert resolve_ndl_keyword(settings_path) == "飛鳥山"


def test_ndl_searchbytext_url_includes_keyword(tmp_path: Path) -> None:
    from harite.sources_remote import _ndl_meta_url
    from harite.sources_remote_ndl_keyword import NDL_SEARCH_PAGE_SIZE

    settings_path = tmp_path / "harite-settings.json"
    save_settings(settings_path, {NDL_KEYWORD_SETTINGS_KEY: "妖怪"})
    url, searchbytext = _ndl_meta_url("ndl-search-keyword", settings_path=settings_path)
    assert searchbytext is True
    assert url.startswith(NDL_SEARCHBYTEXT_URL)
    assert f"keyword2vec={quote('妖怪')}" in url
    assert f"size={NDL_SEARCH_PAGE_SIZE}" in url
    assert "from=0" in url

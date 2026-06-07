"""C-01: remote-cache orphan directory pruning."""

from __future__ import annotations

from pathlib import Path

import pytest

from harite.sources import empty_catalog, get_source
from harite.sources_preset import import_preset_source
from harite.sources_remote import (
    infer_remote_cache_root_from_catalog,
    prune_orphan_remote_cache_dirs,
    resolve_default_remote_cache_root,
)


def test_prune_orphan_remote_cache_dirs_removes_unreferenced_uuid_dirs(
    tmp_path: Path,
) -> None:
    cache_root = tmp_path / "remote-cache"
    cache_root.mkdir()
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "jma-near-color", cache_root=cache_root)

    active_dir = Path(entry.path)
    active_dir.mkdir(parents=True, exist_ok=True)
    (active_dir / "latest.png").write_bytes(b"png")

    orphan_a = cache_root / "00000000-0000-4000-8000-000000000001"
    orphan_b = cache_root / "00000000-0000-4000-8000-000000000002"
    orphan_a.mkdir()
    orphan_b.mkdir()
    (orphan_a / "latest.png").write_bytes(b"x")

    removed = prune_orphan_remote_cache_dirs(catalog, cache_root=cache_root)

    assert removed == 2
    assert active_dir.is_dir()
    assert (active_dir / "latest.png").is_file()
    assert not orphan_a.exists()
    assert not orphan_b.exists()


def test_prune_orphan_remote_cache_dirs_keeps_all_catalog_remote_ids(
    tmp_path: Path,
) -> None:
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    left = import_preset_source(catalog, "jma-near-color", cache_root=cache_root)
    right = import_preset_source(catalog, "jma-asia-color", cache_root=cache_root)

    for entry in (left, right):
        path = Path(entry.path)
        path.mkdir(parents=True, exist_ok=True)
        (path / "latest.png").write_bytes(b"x")

    assert prune_orphan_remote_cache_dirs(catalog, cache_root=cache_root) == 0
    assert Path(left.path).is_dir()
    assert Path(right.path).is_dir()


def test_materialize_prunes_orphans(tmp_path: Path) -> None:
    from harite.gui.adapters_qt.qt_source_catalog import materialize_source_catalog_at_path
    from harite.sources import load_catalog, save_catalog

    cache_root = tmp_path / "remote-cache"
    cache_root.mkdir()

    catalog_path = tmp_path / "harite-sources.json"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "ndl-random-illust", cache_root=cache_root)
    save_catalog(catalog, catalog_path)

    orphan = cache_root / "orphan-id-not-in-catalog"
    orphan.mkdir()

    materialize_source_catalog_at_path(catalog_path, sync_remote=False)

    reloaded = load_catalog(catalog_path)
    assert get_source(reloaded, entry.id) is not None
    assert not orphan.exists()


def test_infer_remote_cache_root_from_catalog_single_root(tmp_path: Path) -> None:
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    import_preset_source(catalog, "jma-near-color", cache_root=cache_root)
    import_preset_source(catalog, "jma-asia-color", cache_root=cache_root)

    assert infer_remote_cache_root_from_catalog(catalog) == cache_root.resolve()


def test_infer_remote_cache_root_from_catalog_ambiguous_returns_none(tmp_path: Path) -> None:
    catalog = empty_catalog()
    import_preset_source(catalog, "jma-near-color", cache_root=tmp_path / "cache-a")
    import_preset_source(catalog, "jma-asia-color", cache_root=tmp_path / "cache-b")

    assert infer_remote_cache_root_from_catalog(catalog) is None


def test_resolve_default_remote_cache_root_honors_env_override(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    override = tmp_path / "env-remote-cache"
    monkeypatch.setenv("HARITE_REMOTE_CACHE_ROOT", str(override))

    assert resolve_default_remote_cache_root() == override
    assert override.is_dir()

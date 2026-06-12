from pathlib import Path

import pytest

from harite.last_optimize_run import (
    LAST_OPTIMIZE_RUN_FILENAME,
    default_last_optimize_search_dirs,
    read_last_optimize_run,
    write_last_optimize_run,
)


def test_write_and_read_last_optimize_run(tmp_path, monkeypatch):
    config_dir = tmp_path / "config" / "harite"
    settings_path = config_dir / "harite-settings.json"
    monkeypatch.setattr("harite.last_optimize_run.resolve_default_settings_path", lambda: settings_path)

    output_dir = tmp_path / "out"
    output_dir.mkdir()
    composite = output_dir / "harite_output_0001.jpg"
    composite.write_bytes(b"x")

    tracking = write_last_optimize_run(output_dir=output_dir, composite_path=composite)

    assert tracking == output_dir / LAST_OPTIMIZE_RUN_FILENAME
    assert (config_dir / LAST_OPTIMIZE_RUN_FILENAME).exists()

    loaded = read_last_optimize_run(search_dirs=default_last_optimize_search_dirs(output_hint=output_dir))
    assert loaded.composite_path == composite.resolve()
    assert loaded.output_dir == output_dir.resolve()


def test_read_last_optimize_run_missing(tmp_path):
    with pytest.raises(ValueError, match="No last optimize run found"):
        read_last_optimize_run(search_dirs=[tmp_path])


def test_read_last_optimize_run_invalid_json(tmp_path):
    tracking = tmp_path / LAST_OPTIMIZE_RUN_FILENAME
    tracking.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="missing composite_path"):
        read_last_optimize_run(search_dirs=[tmp_path])

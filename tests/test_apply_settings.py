from pathlib import Path

import pytest

from harite.apply_settings import resolve_apply_settings
from harite.workspace import Display


def test_resolve_apply_settings_single_file_uses_string_target(tmp_path):
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")

    resolved = resolve_apply_settings(
        file=wall,
        apply_mode="single-file",
    )

    assert resolved.apply_mode == "single-file"
    assert resolved.target == str(wall)
    assert not hasattr(resolved, "plugin_name")


def test_resolve_apply_settings_explicit_mapping_uses_ordered_displays(tmp_path):
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")
    left = tmp_path / "left.jpg"
    right = tmp_path / "right.jpg"
    left.write_bytes(b"l")
    right.write_bytes(b"r")

    resolved = resolve_apply_settings(
        file=wall,
        apply_mode="per-monitor-explicit",
        left_file=left,
        right_file=right,
        displays=[
            Display(name="R", width=1280, height=1024, x_offset=1920),
            Display(name="L", width=1920, height=1080, x_offset=0),
        ],
    )

    assert resolved.target == {"L": str(left), "R": str(right)}


def test_resolve_apply_settings_auto_split_resolves_target_without_plugin_capability_check(tmp_path, monkeypatch):
    monkeypatch.setattr("harite.apply_settings.sys.platform", "linux")
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")

    def fake_build_auto_split_display_map(file, displays, output_dir):
        assert file == wall
        assert [display.name for display in displays] == ["L", "R"]
        assert output_dir == wall.parent
        return {"L": str(tmp_path / "split-left.jpg"), "R": str(tmp_path / "split-right.jpg")}

    monkeypatch.setattr("harite.apply_settings.build_auto_split_display_map", fake_build_auto_split_display_map)

    resolved = resolve_apply_settings(
        file=wall,
        apply_mode="per-monitor-auto-split",
        displays=[
            Display(name="L", width=1920, height=1080, x_offset=0),
            Display(name="R", width=1280, height=1024, x_offset=1920),
        ],
    )

    assert resolved.apply_mode == "per-monitor-auto-split"
    assert resolved.target == {"L": str(tmp_path / "split-left.jpg"), "R": str(tmp_path / "split-right.jpg")}


def test_resolve_apply_settings_windows_span_mode_uses_single_file(tmp_path, monkeypatch):
    monkeypatch.setattr("harite.apply_settings.sys.platform", "win32")
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")

    resolved = resolve_apply_settings(
        file=wall,
        apply_mode="per-monitor-auto-split",
        displays=[],
    )

    assert resolved.windows_span is True
    assert resolved.apply_mode == "single-file"
    assert resolved.target == str(wall)
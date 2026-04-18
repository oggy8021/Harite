from pathlib import Path

import pytest

from harite.apply_settings import resolve_apply_settings
from harite.workspace import Display


def test_resolve_apply_settings_single_file_uses_string_target(tmp_path):
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")

    resolved = resolve_apply_settings(
        file=wall,
        plugin_name="linux",
        apply_mode="single-file",
    )

    assert resolved.apply_mode == "single-file"
    assert resolved.target == str(wall)


def test_resolve_apply_settings_explicit_mapping_uses_ordered_displays(tmp_path):
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")
    left = tmp_path / "left.jpg"
    right = tmp_path / "right.jpg"
    left.write_bytes(b"l")
    right.write_bytes(b"r")

    resolved = resolve_apply_settings(
        file=wall,
        plugin_name="linux",
        apply_mode="per-monitor-explicit",
        left_file=left,
        right_file=right,
        displays=[
            Display(name="R", width=1280, height=1024, x_offset=1920),
            Display(name="L", width=1920, height=1080, x_offset=0),
        ],
    )

    assert resolved.target == {"L": str(left), "R": str(right)}


def test_resolve_apply_settings_auto_split_requires_linux(tmp_path):
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")

    with pytest.raises(ValueError, match="per-monitor apply requires linux plugin"):
        resolve_apply_settings(
            file=wall,
            plugin_name="windows",
            apply_mode="per-monitor-auto-split",
            displays=[Display(name="L", width=1920, height=1080, x_offset=0), Display(name="R", width=1280, height=1024, x_offset=1920)],
        )
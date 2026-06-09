"""MAT-15: core geometry audit — align/margin precedence, scaling noop, MAT-14 interaction."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from harite.core import optimize_wallpapers


def _make_image(path: Path, size: tuple[int, int], color: tuple[int, int, int] = (200, 100, 50)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color=color).save(path, format="JPEG")


def test_scaling_setting_does_not_change_placement(tmp_path):
    img = tmp_path / "img.jpg"
    _make_image(img, (120, 80))
    out = tmp_path / "out"

    _fit_saved, fit_placements = optimize_wallpapers(
        [str(img)],
        (640, 480),
        out,
        scaling="fit",
        align="center",
        valign="center",
    )
    _fill_saved, fill_placements = optimize_wallpapers(
        [str(img)],
        (640, 480),
        out / "fill",
        scaling="fill",
        align="center",
        valign="center",
    )

    assert fit_placements[0].x == fill_placements[0].x
    assert fit_placements[0].y == fill_placements[0].y
    assert fit_placements[0].width == fill_placements[0].width
    assert fit_placements[0].height == fill_placements[0].height
    assert fit_placements[0].scale == fill_placements[0].scale == 1.0


def test_margins_constrain_size_not_align_cell(tmp_path):
    img = tmp_path / "small.jpg"
    _make_image(img, (80, 60))

    _saved, no_margin = optimize_wallpapers(
        [str(img)],
        (500, 400),
        tmp_path / "no-margin",
        margins=(0, 0, 0, 0),
        align="left",
        valign="top",
    )
    _saved, with_margin = optimize_wallpapers(
        [str(img)],
        (500, 400),
        tmp_path / "with-margin",
        margins=(100, 100, 50, 50),
        align="left",
        valign="top",
    )

    assert no_margin[0].x == 0
    assert no_margin[0].y == 0
    assert with_margin[0].x == 0
    assert with_margin[0].y == 0


def test_margins_shrink_oversized_image_before_align(tmp_path):
    img = tmp_path / "wide.jpg"
    _make_image(img, (900, 400))

    _saved, placements = optimize_wallpapers(
        [str(img)],
        (500, 300),
        tmp_path / "out",
        margins=(40, 40, 20, 20),
        align="right",
        valign="bottom",
    )

    placement = placements[0]
    assert placement.scale < 1.0
    assert placement.x + placement.width <= 500
    assert placement.y + placement.height <= 300
    assert placement.x > 0
    assert placement.y > 0


def test_mat14_source_scale_runs_before_align(tmp_path):
    img = tmp_path / "small.jpg"
    _make_image(img, (100, 100))

    _saved, placements = optimize_wallpapers(
        [str(img)],
        (500, 500),
        tmp_path / "out",
        l_display_scale=1.25,
        align="center",
        valign="center",
        margins=(0, 0, 0, 0),
    )

    placement = placements[0]
    assert placement.width == 125
    assert placement.height == 125
    assert placement.scale == 1.25
    assert placement.x == (500 - 125) // 2
    assert placement.y == (500 - 125) // 2


def test_mat14_with_margins_and_right_align(tmp_path):
    img = tmp_path / "small.jpg"
    _make_image(img, (80, 60))

    _saved, placements = optimize_wallpapers(
        [str(img)],
        (400, 300),
        tmp_path / "out",
        l_display_scale=1.25,
        margins=(20, 20, 10, 10),
        align="right",
        valign="bottom",
    )

    placement = placements[0]
    assert placement.width == 100
    assert placement.height == 75
    assert placement.x == 400 - 100
    assert placement.y == 300 - 75

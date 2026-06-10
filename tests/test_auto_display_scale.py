"""MAT-14b: auto display scale from short-edge thresholds."""

from __future__ import annotations

from PIL import Image

from harite.auto_display_scale import (
    compute_auto_display_scale_factor,
    resolve_effective_display_scale,
)
from harite.core import optimize_wallpapers


def test_compute_auto_display_scale_factor_thresholds():
    margins = (0, 0, 0, 0)
    assert compute_auto_display_scale_factor(800, 700, screen_w=1920, screen_h=1080, margins=margins) == 1.0
    assert compute_auto_display_scale_factor(400, 300, screen_w=1920, screen_h=1080, margins=margins) == 1.5
    assert compute_auto_display_scale_factor(200, 150, screen_w=1920, screen_h=1080, margins=margins) == 2.0


def test_resolve_effective_display_scale_manual_overrides_auto():
    margins = (0, 0, 0, 0)
    assert (
        resolve_effective_display_scale(
            200,
            150,
            screen_w=1920,
            screen_h=1080,
            margins=margins,
            manual_scale=1.25,
            auto_enabled=True,
        )
        == 1.25
    )


def test_optimize_wallpapers_applies_auto_scale_when_enabled(tmp_path):
    inp_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    inp_dir.mkdir()
    out_dir.mkdir()

    img = inp_dir / "small.jpg"
    Image.new("RGB", (400, 300), color=(120, 80, 40)).save(img, format="JPEG")

    saved, placements = optimize_wallpapers(
        [str(img)],
        (1920, 1080),
        out_dir,
        l_auto_display_scale=True,
    )

    assert saved
    assert placements[0].width == 600
    assert placements[0].height == 450
    assert placements[0].scale == 1.5

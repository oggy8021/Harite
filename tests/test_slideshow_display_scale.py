"""Slideshow optimize uses Slideshow-tab auto only; manual scale stays 100%."""

from __future__ import annotations

from dataclasses import replace

from PIL import Image

from harite.core import optimize_wallpapers
from harite.gui.controllers.optimize_controller import OptimizeFormState


def test_slideshow_optimize_state_uses_slideshow_auto_not_main_manual(tmp_path):
    inp_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    inp_dir.mkdir()
    out_dir.mkdir()

    img = inp_dir / "small.jpg"
    Image.new("RGB", (400, 300), color=(80, 120, 160)).save(img, format="JPEG")

    base = OptimizeFormState(
        input_value=str(img),
        output_dir=str(out_dir),
        l_display_scale=2.0,
        r_display_scale=2.0,
        l_auto_display_scale=True,
        r_auto_display_scale=True,
    )
    slideshow_state = replace(
        base,
        l_display_scale=1.0,
        r_display_scale=1.0,
        l_auto_display_scale=False,
        r_auto_display_scale=False,
    )

    _, placements_main_auto = optimize_wallpapers(
        [str(img)],
        (1024, 768),
        out_dir,
        l_display_scale=base.l_display_scale,
        r_display_scale=base.r_display_scale,
        l_auto_display_scale=base.l_auto_display_scale,
        r_auto_display_scale=base.r_auto_display_scale,
    )
    _, placements_slideshow_off = optimize_wallpapers(
        [str(img)],
        (1024, 768),
        out_dir,
        l_display_scale=slideshow_state.l_display_scale,
        r_display_scale=slideshow_state.r_display_scale,
        l_auto_display_scale=slideshow_state.l_auto_display_scale,
        r_auto_display_scale=slideshow_state.r_auto_display_scale,
    )

    assert placements_main_auto[0].width == 800
    assert placements_slideshow_off[0].width == 400
    assert placements_slideshow_off[0].scale == 1.0

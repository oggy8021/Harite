import pytest
from PIL import Image

from harite.core import optimize_wallpapers, validate_intentional_image_scales
from harite.display_scale import (
    DISPLAY_SCALE_PRESETS,
    MAX_OPTIMIZE_EDGE,
    format_display_scale_label,
    image_scale_for_index,
    is_unity_display_scale,
    normalize_display_scale,
    scale_image_dimensions,
    validate_scaled_image_edge,
)
from harite.optimize_settings import resolve_optimize_display_settings


def test_normalize_display_scale_accepts_presets_only():
    assert normalize_display_scale(1) == 1.0
    assert normalize_display_scale(1.25) == 1.25
    assert normalize_display_scale(1.5) == 1.5
    assert normalize_display_scale(2) == 2.0
    assert normalize_display_scale("150%") == 1.5
    assert normalize_display_scale("125") == 1.25
    assert normalize_display_scale(3) == 1.0
    assert normalize_display_scale(4) == 2.0


def test_format_display_scale_label_uses_percent():
    assert format_display_scale_label(1.0) == "100%"
    assert format_display_scale_label(1.25) == "125%"
    assert format_display_scale_label(1.5) == "150%"
    assert format_display_scale_label(2.0) == "200%"


def test_scale_image_dimensions_rounds_scaled_pixels():
    assert scale_image_dimensions(400, 300, 1.25) == (500, 375)
    assert scale_image_dimensions(400, 300, 1.5) == (600, 450)
    assert scale_image_dimensions(400, 300, 2.0) == (800, 600)


def test_validate_scaled_image_edge_rejects_oversized_dimensions():
    with pytest.raises(ValueError, match="exceeds limit"):
        validate_scaled_image_edge(MAX_OPTIMIZE_EDGE + 1, 1080)


def test_image_scale_for_index_maps_left_and_right():
    assert image_scale_for_index(0, l_display_scale=1.25, r_display_scale=2.0) == 1.25
    assert image_scale_for_index(1, l_display_scale=1.25, r_display_scale=2.0) == 2.0


def test_is_unity_display_scale_detects_default_only():
    assert is_unity_display_scale(1.0)
    assert is_unity_display_scale("100%")
    assert not is_unity_display_scale(1.25)


def test_resolve_optimize_display_settings_keeps_display_resolution_unscaled(monkeypatch):
    from harite.display_context import TwoScreenOptimizeContext
    from harite.workspace import Display

    monkeypatch.setattr(
        "harite.optimize_settings.build_two_screen_optimize_context",
        lambda: TwoScreenOptimizeContext(
            displays=(
                Display(name="L", width=1920, height=1080, x_offset=0),
                Display(name="R", width=1280, height=1024, x_offset=1920),
            ),
            resolution=(3200, 1080),
            l_display=(1920, 1080),
            r_display=(1280, 1024),
        ),
    )

    resolved = resolve_optimize_display_settings(
        input_values=["left.jpg", "right.jpg"],
        canvas_scale_percent=100,
    )

    assert resolved.resolution == "3200x1080"
    assert resolved.l_display == "1920x1080"
    assert resolved.r_display == "1280x1024"


def test_optimize_wallpapers_post_downscales_composite_by_canvas_scale(tmp_path):
    inp_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    inp_dir.mkdir()
    out_dir.mkdir()

    left = inp_dir / "left.jpg"
    right = inp_dir / "right.jpg"
    Image.new("RGB", (1920, 1080), color=(200, 0, 0)).save(left, format="JPEG")
    Image.new("RGB", (1920, 1080), color=(0, 0, 200)).save(right, format="JPEG")

    saved, placements = optimize_wallpapers(
        [str(left), str(right)],
        (3840, 1080),
        out_dir,
        two_screen=True,
        l_display=(1920, 1080),
        r_display=(1920, 1080),
        canvas_scale_percent=50,
    )

    assert len(placements) == 2
    assert placements[0].scale == 1.0
    assert placements[1].scale == 1.0
    composite = Image.open(saved[0])
    assert composite.size == (1920, 540)


def test_optimize_wallpapers_scales_source_image_not_canvas(tmp_path):
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
        l_display_scale=1.25,
    )

    assert saved
    assert len(placements) == 1
    assert placements[0].width == 500
    assert placements[0].height == 375
    assert placements[0].scale == 1.25

    composite = Image.open(saved[0])
    assert composite.size == (1920, 1080)


def test_validate_intentional_image_scales_falls_back_to_down_only_on_overflow(tmp_path):
    inp_dir = tmp_path / "in"
    inp_dir.mkdir()
    img = inp_dir / "large.jpg"
    Image.new("RGB", (1200, 900), color=(10, 20, 30)).save(img, format="JPEG")

    validate_intentional_image_scales(
        [str(img)],
        (1920, 1080),
        l_display_scale=2.0,
    )


def test_intentional_upscale_falls_back_for_tall_narrow_image():
    from harite.core import _resolve_intentional_image_dimensions

    img = Image.new("RGB", (439, 1524), color=(1, 2, 3))
    width, height, scale = _resolve_intentional_image_dimensions(
        img,
        2048,
        1280,
        (0, 0, 0, 0),
        2.0,
        side_label="L",
    )
    assert width <= 2048
    assert height <= 1280
    assert scale <= 1.0


def test_display_scale_presets_are_fixed_steps():
    assert DISPLAY_SCALE_PRESETS == (1.0, 1.25, 1.5, 2.0)

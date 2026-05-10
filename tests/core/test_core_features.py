from pathlib import Path
import pytest
from PIL import Image
import tempfile


def make_image(path: Path, size=(200, 200), color=(100, 150, 200)):
    img = Image.new("RGB", size, color=color)
    img.save(path, quality=90)


def test_optimize_wallpapers_creates_output_and_placements(tmp_path):
    from harite.core import optimize_wallpapers

    inp_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    inp_dir.mkdir()
    out_dir.mkdir()

    # create two input images
    img1 = inp_dir / "a1.jpg"
    img2 = inp_dir / "a2.jpg"
    make_image(img1, size=(300, 200))
    make_image(img2, size=(100, 400))

    saved, placements = optimize_wallpapers([str(img1), str(img2)], (800, 600), out_dir)

    assert isinstance(saved, list) and len(saved) >= 1
    assert saved[0].exists()
    assert isinstance(placements, list)
    # placement entries should reference original images
    assert any('a1' in p.image_path.name or 'a2' in p.image_path.name for p in placements)


def test_optimize_wallpapers_uses_selected_background_color(tmp_path):
    from harite.core import optimize_wallpapers

    inp_dir = tmp_path / "in-bg"
    out_dir = tmp_path / "out-bg"
    inp_dir.mkdir()
    out_dir.mkdir()

    img1 = inp_dir / "a.jpg"
    make_image(img1, size=(100, 100), color=(100, 150, 200))

    saved, _ = optimize_wallpapers(
        [str(img1)],
        (300, 300),
        out_dir,
        margins=(40, 40, 40, 40),
        background_color="#224466",
    )

    out = Image.open(saved[0]).convert("RGB")
    red, green, blue = out.getpixel((5, 5))
    assert abs(red - 34) <= 1
    assert abs(green - 68) <= 1
    assert abs(blue - 102) <= 1


def test_optimize_wallpapers_rejects_directory_input(tmp_path):
    from harite.core import optimize_wallpapers

    inp_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    inp_dir.mkdir()
    out_dir.mkdir()

    with pytest.raises(ValueError, match="optimize --input does not accept directories"):
        optimize_wallpapers([str(inp_dir)], (800, 600), out_dir)


def test_compute_placement_centers_and_scales(tmp_path):
    from harite.core import compute_placement

    img = tmp_path / "single.jpg"
    make_image(img, size=(400, 300))
    pr = compute_placement(img, (800, 600))
    assert pr.width <= 800 and pr.height <= 600
    assert pr.x >= 0 and pr.y >= 0


def test_split_composite_for_displays_creates_per_display_files(tmp_path):
    from harite.core import split_composite_for_displays
    from harite.workspace import Display

    comp = tmp_path / "comp.jpg"
    # create a wide composite (1000x300)
    make_image(comp, size=(1000, 300), color=(10, 20, 30))

    displays = [Display(name="left", width=400, height=300, x_offset=0, primary=True),
                Display(name="right", width=600, height=300, x_offset=400, primary=False)]

    out = split_composite_for_displays(comp, displays, tmp_path / "out")
    assert isinstance(out, dict)
    assert "left" in out and "right" in out
    for p in out.values():
        assert Path(p).exists()
        img = Image.open(p)
        assert img.size == (displays[0].width, displays[0].height) or img.size == (displays[1].width, displays[1].height)


def test_build_embed_lines_without_datetime():
    from harite.core import _build_embed_lines

    lines = _build_embed_lines(
        "combo",
        target_resolution=(1920, 1080),
        margins=(10, 20, 30, 40),
        align="center",
        valign="center",
        input_count=2,
        two_screen=True,
        l_display=(1920, 1080),
        r_display=(1280, 1024),
        free_text="hello",
    )
    joined = "\n".join(lines)
    assert "res=1920x1080" in joined
    assert "two_screen=1" in joined
    assert "hello" in joined
    assert "pad=" not in joined
    assert "datetime" not in joined


def test_phase8_embed_position_helpers_map_to_quadrants():
    from harite.core import describe_embed_position, resolve_embed_margin_region

    assert describe_embed_position("top") == "left top"
    assert describe_embed_position("left") == "left bottom"
    assert describe_embed_position("right") == "right top"
    assert describe_embed_position("bottom") == "right bottom"

    assert resolve_embed_margin_region((1920, 1080), (10, 10, 20, 30), "top") == (10, 0, 960, 20)
    assert resolve_embed_margin_region((1920, 1080), (10, 10, 20, 30), "left") == (10, 1050, 960, 1080)
    assert resolve_embed_margin_region((1920, 1080), (10, 10, 20, 30), "right") == (960, 0, 1910, 20)
    assert resolve_embed_margin_region((1920, 1080), (10, 10, 20, 30), "bottom") == (960, 1050, 1910, 1080)


def test_phase8_embed_position_helpers_use_display_slices_for_two_screen():
    from harite.core import resolve_embed_margin_region

    assert resolve_embed_margin_region(
        (3200, 1080),
        (100, 150, 80, 90),
        "top",
        two_screen=True,
        l_display=(1920, 1080),
        r_display=(1280, 1024),
    ) == (100, 0, 1770, 80)
    assert resolve_embed_margin_region(
        (3200, 1080),
        (100, 150, 80, 90),
        "right",
        two_screen=True,
        l_display=(1920, 1080),
        r_display=(1280, 1024),
    ) == (2020, 0, 3050, 80)
    assert resolve_embed_margin_region(
        (3840, 1080),
        (100, 150, 80, 90),
        "bottom",
        two_screen=True,
    ) == (2020, 990, 3690, 1080)


def test_embed_text_drawn_on_top_margin(tmp_path):
    from harite.core import optimize_wallpapers

    inp_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    inp_dir.mkdir()
    out_dir.mkdir()

    img1 = inp_dir / "a.jpg"
    make_image(img1, size=(300, 200), color=(90, 120, 150))

    saved, _ = optimize_wallpapers(
        [str(img1)],
        (400, 220),
        out_dir,
        margins=(10, 10, 40, 10),
        embed_info="free",
        embed_text="margin-note",
        embed_position="top",
    )

    out = Image.open(saved[0]).convert("RGB")
    # top margin area should include text pixels not equal to pure background.
    sample_area = out.crop((12, 2, 200, 30))
    assert any(px != (30, 30, 30) for px in sample_area.getdata())


def test_embed_text_drawn_in_right_display_margin_for_two_screen(tmp_path):
    from harite.core import optimize_wallpapers

    inp_dir = tmp_path / "in-two-screen-text"
    out_dir = tmp_path / "out-two-screen-text"
    inp_dir.mkdir()
    out_dir.mkdir()

    img1 = inp_dir / "left.jpg"
    img2 = inp_dir / "right.jpg"
    make_image(img1, size=(900, 600), color=(90, 120, 150))
    make_image(img2, size=(900, 600), color=(60, 100, 170))

    saved, _ = optimize_wallpapers(
        [str(img1), str(img2)],
        (3200, 1080),
        out_dir,
        two_screen=True,
        l_display=(1920, 1080),
        r_display=(1280, 1024),
        margins=(100, 150, 80, 90),
        embed_info="free",
        embed_text="right-slice",
        embed_position="right",
    )

    out = Image.open(saved[0]).convert("RGB")
    left_sample = out.crop((110, 2, 500, 60))
    right_sample = out.crop((2025, 2, 2450, 60))

    assert all(px == (30, 30, 30) for px in left_sample.getdata())
    assert any(px != (30, 30, 30) for px in right_sample.getdata())


def test_two_screen_explicit_with_outer_margins_keeps_placements_within_display_slices(tmp_path):
    from harite.core import optimize_wallpapers

    inp_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    inp_dir.mkdir()
    out_dir.mkdir()

    img1 = inp_dir / "left.jpg"
    img2 = inp_dir / "right.jpg"
    make_image(img1, size=(1600, 900), color=(90, 120, 150))
    make_image(img2, size=(900, 1600), color=(40, 80, 160))

    saved, placements = optimize_wallpapers(
        [str(img1), str(img2)],
        (4096, 1280),
        out_dir,
        two_screen=True,
        l_display=(2048, 1280),
        r_display=(2048, 1280),
        margins=(200, 200, 200, 200),
        align=("right", "center"),
        valign=("center", "top"),
    )

    assert saved
    assert len(placements) == 2
    left, right = placements
    assert left.x >= 200
    assert left.x + left.width <= 2048
    assert left.y >= 200
    assert left.y + left.height <= 1280 - 200
    assert right.x >= 2048 + 200
    assert right.x + right.width <= 4096 - 200
    assert right.y >= 200
    assert right.y + right.height <= 1280 - 200


def test_two_screen_without_explicit_displays_applies_margins_per_half(tmp_path):
    from harite.core import optimize_wallpapers

    inp_dir = tmp_path / "in-implicit"
    out_dir = tmp_path / "out-implicit"
    inp_dir.mkdir()
    out_dir.mkdir()

    img1 = inp_dir / "left.jpg"
    img2 = inp_dir / "right.jpg"
    make_image(img1, size=(1400, 900), color=(100, 120, 140))
    make_image(img2, size=(1200, 900), color=(50, 90, 180))

    saved, placements = optimize_wallpapers(
        [str(img1), str(img2)],
        (3840, 1080),
        out_dir,
        two_screen=True,
        margins=(100, 150, 80, 90),
        align=("left", "right"),
        valign=("top", "bottom"),
    )

    assert saved
    assert len(placements) == 2
    left, right = placements
    half_w = 3840 // 2

    assert left.x >= 100
    assert left.x + left.width <= half_w - 150
    assert left.y >= 80
    assert left.y + left.height <= 1080 - 90

    assert right.x >= half_w + 100
    assert right.x + right.width <= 3840 - 150
    assert right.y >= 80
    assert right.y + right.height <= 1080 - 90


def test_two_screen_equal_displays_keep_identical_inputs_in_matching_positions(tmp_path):
    from harite.core import optimize_wallpapers

    inp_dir = tmp_path / "in-identical-two-screen"
    out_dir = tmp_path / "out-identical-two-screen"
    inp_dir.mkdir()
    out_dir.mkdir()

    img1 = inp_dir / "same.jpg"
    make_image(img1, size=(1600, 900), color=(90, 120, 150))

    saved, placements = optimize_wallpapers(
        [str(img1), str(img1)],
        (4096, 1280),
        out_dir,
        two_screen=True,
        l_display=(2048, 1280),
        r_display=(2048, 1280),
        margins=(200, 200, 200, 200),
        align=("center", "center"),
        valign=("center", "center"),
    )

    assert saved
    assert len(placements) == 2
    left, right = placements

    assert left.width == right.width
    assert left.height == right.height
    assert left.y == right.y
    assert right.x - left.x == 2048


def test_load_preferred_font_tries_explicit_path_first(monkeypatch):
    import harite.core as core

    tried = []
    base_font = Image.new("RGB", (1, 1))
    fallback = core.ImageFont.load_default()

    def fake_truetype(path, size):
        tried.append((path, size))
        if path == "custom-font.ttf":
            return fallback
        raise OSError("font not found")

    monkeypatch.setattr(core.ImageFont, "truetype", fake_truetype)

    font = core._load_preferred_font(14, explicit_path="custom-font.ttf")
    assert font is fallback
    assert tried[0][0] == "custom-font.ttf"

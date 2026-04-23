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
        padding=5,
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
    assert "datetime" not in joined


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
    assert right.x >= 2048
    assert right.x + right.width <= 4096 - 200


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

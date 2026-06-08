from pathlib import Path
from PIL import Image


def make_image(path: Path, size=(200, 200), color=(100, 150, 200), mode="RGB"):
    img = Image.new(mode, size, color=color)
    img.save(path)


def test_optimize_wallpapers_handles_transparent_png(tmp_path):
    from harite.core import optimize_wallpapers

    inp = tmp_path / "in"
    out = tmp_path / "out"
    inp.mkdir()
    out.mkdir()

    png = inp / "alpha.png"
    # create RGBA image with partial transparency
    make_image(png, size=(300, 300), color=(255, 0, 0, 128), mode="RGBA")

    saved, placements = optimize_wallpapers([str(png)], (800, 600), out)
    assert isinstance(saved, list) and len(saved) >= 1
    assert saved[0].exists()
    assert isinstance(placements, list)


def test_optimize_wallpapers_large_image_resizes(tmp_path):
    from harite.core import optimize_wallpapers

    inp = tmp_path / "in"
    out = tmp_path / "out"
    inp.mkdir()
    out.mkdir()

    large = inp / "large.jpg"
    # very large image (simulate high-res wallpaper)
    make_image(large, size=(5000, 3000))

    saved, placements = optimize_wallpapers([str(large)], (1920, 1080), out)
    assert saved and all(p.exists() for p in saved)
    # placement should fit within target
    assert all(getattr(p, "width", 1920) <= 1920 and getattr(p, "height", 1080) <= 1080 for p in placements)


def test_compute_placement_keeps_native_size_when_small(tmp_path):
    from harite.core import compute_placement

    small = tmp_path / "small.jpg"
    make_image(small, size=(100, 50))

    pr = compute_placement(small, (800, 600))
    assert pr.width == 100 and pr.height == 50
    assert pr.scale == 1.0
    assert pr.x == 350 and pr.y == 275


def test_split_composite_with_offscreen_display(tmp_path):
    from harite.core import split_composite_for_displays
    from harite.workspace import Display

    comp = tmp_path / "comp.jpg"
    make_image(comp, size=(400, 200))

    # display whose x_offset starts beyond composite width
    displays = [Display(name="off", width=300, height=200, x_offset=500, primary=False)]

    out = split_composite_for_displays(comp, displays, tmp_path / "out")
    assert isinstance(out, dict)
    # even if offscreen, implementation should create a file (possibly blank) or raise handled
    assert "off" in out
    assert Path(out["off"]).exists()

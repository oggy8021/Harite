from pathlib import Path
from PIL import Image
from harite.core import optimize_wallpapers


def _make_image(path: Path, size=(100, 100), color=(255, 0, 0)):
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, color=color)
    img.save(path)


def test_horizontal_align(tmp_path):
    # image 100x100, canvas 500x100 -> horizontal space exists
    img = tmp_path / "img1.jpg"
    _make_image(img, size=(100, 100))

    out_dir = tmp_path / "out"

    # left
    saved, placements = optimize_wallpapers([str(img)], (500, 100), out_dir, padding=0, quality=80, align="left", valign="center")
    assert len(placements) == 1
    left_x = placements[0].x

    # center
    saved, placements = optimize_wallpapers([str(img)], (500, 100), out_dir, padding=0, quality=80, align="center", valign="center")
    center_x = placements[0].x

    # right
    saved, placements = optimize_wallpapers([str(img)], (500, 100), out_dir, padding=0, quality=80, align="right", valign="center")
    right_x = placements[0].x

    assert left_x < center_x < right_x


def test_vertical_valign(tmp_path):
    # image 100x50, canvas 100x300 -> vertical space exists
    img = tmp_path / "img2.jpg"
    _make_image(img, size=(50, 50))

    out_dir = tmp_path / "out2"

    # top
    saved, placements = optimize_wallpapers([str(img)], (100, 300), out_dir, padding=0, quality=80, align="center", valign="top")
    top_y = placements[0].y

    # center
    saved, placements = optimize_wallpapers([str(img)], (100, 300), out_dir, padding=0, quality=80, align="center", valign="center")
    center_y = placements[0].y

    # bottom
    saved, placements = optimize_wallpapers([str(img)], (100, 300), out_dir, padding=0, quality=80, align="center", valign="bottom")
    bottom_y = placements[0].y

    assert top_y < center_y < bottom_y

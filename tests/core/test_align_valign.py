from pathlib import Path
from PIL import Image
from harite.core import optimize_wallpapers


def _make_image(path: Path, size=(100, 100), color=(255, 0, 0)):
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, color=color)
    img.save(path)


def test_small_image_stays_native_size(tmp_path):
    img = tmp_path / "small.jpg"
    _make_image(img, size=(80, 60))

    out_dir = tmp_path / "out-native"
    _saved, placements = optimize_wallpapers(
        [str(img)],
        (1920, 1080),
        out_dir,
        quality=80,
        align="left",
        valign="top",
    )

    assert len(placements) == 1
    assert placements[0].scale == 1.0
    assert placements[0].width == 80
    assert placements[0].height == 60
    assert placements[0].x == 0
    assert placements[0].y == 0


def test_horizontal_align(tmp_path):
    # image 100x100, canvas 500x100 -> horizontal space exists
    img = tmp_path / "img1.jpg"
    _make_image(img, size=(100, 100))

    out_dir = tmp_path / "out"

    # left
    saved, placements = optimize_wallpapers([str(img)], (500, 100), out_dir, quality=80, align="left", valign="center")
    assert len(placements) == 1
    left_x = placements[0].x

    # center
    saved, placements = optimize_wallpapers([str(img)], (500, 100), out_dir, quality=80, align="center", valign="center")
    center_x = placements[0].x

    # right
    saved, placements = optimize_wallpapers([str(img)], (500, 100), out_dir, quality=80, align="right", valign="center")
    right_x = placements[0].x

    assert left_x < center_x < right_x


def test_vertical_valign(tmp_path):
    # image 100x50, canvas 100x300 -> vertical space exists
    img = tmp_path / "img2.jpg"
    _make_image(img, size=(50, 50))

    out_dir = tmp_path / "out2"

    # top
    saved, placements = optimize_wallpapers([str(img)], (100, 300), out_dir, quality=80, align="center", valign="top")
    top_y = placements[0].y

    # center
    saved, placements = optimize_wallpapers([str(img)], (100, 300), out_dir, quality=80, align="center", valign="center")
    center_y = placements[0].y

    # bottom
    saved, placements = optimize_wallpapers([str(img)], (100, 300), out_dir, quality=80, align="center", valign="bottom")
    bottom_y = placements[0].y

    assert top_y < center_y < bottom_y


def test_pair_align_and_valign_apply_per_side_in_two_screen_mode(tmp_path):
    left = tmp_path / "left.jpg"
    right = tmp_path / "right.jpg"
    _make_image(left, size=(50, 100), color=(255, 0, 0))
    _make_image(right, size=(100, 50), color=(0, 255, 0))

    out_dir = tmp_path / "out-pair"

    _saved, placements = optimize_wallpapers(
        [str(left), str(right)],
        (400, 200),
        out_dir,
        quality=80,
        two_screen=True,
        l_display=(200, 200),
        r_display=(200, 200),
        align=("left", "right"),
        valign=("top", "bottom"),
    )

    assert len(placements) == 2
    assert placements[0].x == 0
    assert placements[0].y == 0
    assert placements[0].width == 50
    assert placements[0].height == 100
    assert placements[1].x == 300
    assert placements[1].y == 150
    assert placements[1].width == 100
    assert placements[1].height == 50

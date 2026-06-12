from pathlib import Path
from harite.core import optimize_wallpapers


def test_margins_reduce_available_space(tmp_path):
    left = Path("tests/data/left.jpg")
    right = Path("tests/data/right.jpg")
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    w_target, h_target = 2000, 1000
    margins = (10, 30, 5, 5)  # left, right, top, bottom

    saved, placements = optimize_wallpapers(
        inputs=[str(left), str(right)],
        target_resolution=(w_target, h_target),
        output_dir=out_dir,
        two_screen=True,
        l_display=(1000, 1000),
        r_display=(1000, 1000),
        margins=margins,
    )

    assert len(placements) == 2
    for p in placements:
        assert p.width <= 1000
        assert p.y >= 0


def test_two_screen_allocation_keeps_input_order(tmp_path):
    left = Path("tests/data/left.jpg")
    right = Path("tests/data/right.jpg")
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    saved, placements = optimize_wallpapers(
        inputs=[str(right), str(left)],
        target_resolution=(1920, 1080),
        output_dir=out_dir,
        two_screen=True,
        l_display=(960, 1080),
        r_display=(960, 1080),
    )

    assert len(placements) >= 2
    # Two-screen allocation follows input order: first input -> left monitor
    assert placements[0].monitor == "left"
    assert placements[1].monitor == "right"

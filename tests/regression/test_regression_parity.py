from pathlib import Path
from harite.core import optimize_wallpapers


def test_two_screen_basic_parity(tmp_path):
    # Use provided test assets to run a basic parity check: two inputs -> two placements
    left = Path("tests/data/left.jpg")
    right = Path("tests/data/right.jpg")
    assert left.exists() and right.exists()

    out_dir = tmp_path / "out"
    out_dir.mkdir()

    saved, placements = optimize_wallpapers(
        inputs=[str(left), str(right)],
        target_resolution=(3840, 1080),
        output_dir=out_dir,
        scaling="fit",
        two_screen=True,
        l_display=(1920, 1080),
        r_display=(1920, 1080),
    )

    assert len(saved) == 1
    assert len(placements) == 2

    w_target, h_target = 3840, 1080

    assert placements[0].monitor == "left"
    assert placements[1].monitor == "right"

    for p in placements:
        assert 0 <= p.x < w_target
        assert 0 <= p.y < h_target
        assert 1 <= p.width <= 1920
        assert 1 <= p.height <= h_target
        assert p.scale > 0.0

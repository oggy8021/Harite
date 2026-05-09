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
    )

    # Expect one output file and two placement entries
    assert len(saved) == 1
    assert len(placements) == 2

    # Left/right posit assigned and sizes within bounds
    w_target, h_target = 3840, 1080
    count = 2
    cell_w = max(1, w_target // count)

    assert placements[0].posit == "left"
    assert placements[1].posit == "right"

    for p in placements:
        assert 0 <= p.x < w_target
        assert 0 <= p.y < h_target
        assert 1 <= p.width <= cell_w
        assert 1 <= p.height <= h_target
        assert p.scale > 0.0

from pathlib import Path
from harite.core import optimize_wallpapers


def test_two_screen_basic(tmp_path):
    # use existing test images in tests/data
    tests_root = Path(__file__).resolve().parent.parent
    left = tests_root / "data" / "left.jpg"
    right = tests_root / "data" / "right.jpg"

    out_dir = tmp_path / "out"
    out_dir.mkdir()

    saved, placements = optimize_wallpapers(
        inputs=[left, right],
        target_resolution=(3840, 1080),
        output_dir=out_dir,
        scaling="fit",
        quality=85,
        two_screen=True,
        l_display=(1920, 1080),
        r_display=(1920, 1080),
        margins=(10, 10, 5, 5),
    )

    # one output file
    assert len(saved) == 1
    # two placements (left/right)
    assert len(placements) >= 2
    pos = [p.monitor for p in placements]
    assert "left" in pos and "right" in pos

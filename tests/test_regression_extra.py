from pathlib import Path
from harite.core import optimize_wallpapers


def test_upscale_when_target_larger(tmp_path):
    p = Path("tests/data/left.jpg")
    assert p.exists()

    out_dir = tmp_path / "out"
    out_dir.mkdir()

    saved, placements = optimize_wallpapers(
        inputs=[str(p)],
        target_resolution=(4000, 3000),
        output_dir=out_dir,
    )

    assert len(placements) == 1
    # target bigger than source -> scale should be > 1
    assert placements[0].scale > 1.0


def test_padding_creates_gap(tmp_path):
    left = Path("tests/data/left.jpg")
    right = Path("tests/data/right.jpg")
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    saved_a, placements_a = optimize_wallpapers(
        inputs=[str(left), str(right)],
        target_resolution=(2000, 1000),
        output_dir=out_dir,
        padding=0,
    )

    saved_b, placements_b = optimize_wallpapers(
        inputs=[str(left), str(right)],
        target_resolution=(2000, 1000),
        output_dir=out_dir,
        padding=50,
    )

    # compute horizontal gap between first and second placement
    gap_a = placements_a[1].x - (placements_a[0].x + placements_a[0].width)
    gap_b = placements_b[1].x - (placements_b[0].x + placements_b[0].width)

    assert gap_b >= gap_a + 49


def test_three_images_split(tmp_path):
    a = Path("tests/data/left.jpg")
    b = Path("tests/data/right.jpg")
    c = Path("tests/data/img_wide.jpg")
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    saved, placements = optimize_wallpapers(
        inputs=[str(a), str(b), str(c)],
        target_resolution=(3000, 1000),
        output_dir=out_dir,
        padding=10,
    )

    assert len(placements) == 3
    inner_w = 3000
    # each width should be roughly inner_w/3 (allow some slack)
    for p in placements:
        assert p.width <= inner_w // 3 + 200


def test_output_filename_contains_prefix(tmp_path):
    p = Path("tests/data/left.jpg")
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    saved, _ = optimize_wallpapers(inputs=[str(p)], target_resolution=(800, 600), output_dir=out_dir)
    assert len(saved) == 1
    assert "harite_wallopt_" in saved[0].name

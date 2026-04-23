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
    assert "harite_output_" in saved[0].name


def test_output_path_overrides_default_filename(tmp_path):
    p = Path("tests/data/left.jpg")
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    explicit = tmp_path / "picked" / "my_save.jpg"

    saved, _ = optimize_wallpapers(
        inputs=[str(p)],
        target_resolution=(800, 600),
        output_dir=out_dir,
        output_path=explicit,
    )

    assert len(saved) == 1
    assert saved[0] == explicit
    assert explicit.exists()

from pathlib import Path
from harite.core import optimize_wallpapers


def test_native_size_when_target_larger(tmp_path):
    """MAT-01b: small images stay native size (parent parity; no upscale)."""
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
    assert placements[0].scale == 1.0


def test_multi_input_without_two_screen_raises(tmp_path):
    import pytest

    a = Path("tests/data/left.jpg")
    b = Path("tests/data/right.jpg")
    c = Path("tests/data/img_wide.jpg")
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    with pytest.raises(ValueError, match="two-screen mode"):
        optimize_wallpapers(
            inputs=[str(a), str(b), str(c)],
            target_resolution=(3000, 1000),
            output_dir=out_dir,
        )


def test_output_filename_contains_prefix(tmp_path):
    p = Path("tests/data/left.jpg")
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    saved, _ = optimize_wallpapers(inputs=[str(p)], target_resolution=(800, 600), output_dir=out_dir)
    assert len(saved) == 1
    assert "harite_output_" in saved[0].name


def test_output_filename_uses_four_digit_zero_padding(tmp_path):
    p = Path("tests/data/left.jpg")
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    saved, _ = optimize_wallpapers(inputs=[str(p)], target_resolution=(800, 600), output_dir=out_dir)

    assert len(saved) == 1
    assert saved[0].name == "harite_output_0001.jpg"


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

from pathlib import Path

from scripts.xfce_smoke_runner import collect_images


def test_collect_images_returns_absolute_paths():
    images = collect_images(["tests/data"])
    assert images
    assert all(p.is_absolute() for p in images)


def test_collect_images_deduplicates_same_file_from_file_and_dir():
    direct = Path("tests/data/left.jpg")
    images = collect_images(["tests/data", str(direct)])
    left = [p for p in images if p.name == "left.jpg"]
    assert len(left) == 1

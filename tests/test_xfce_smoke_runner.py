from pathlib import Path
import importlib.util


def _load_collect_images():
    runner_path = Path(__file__).resolve().parents[1] / "scripts" / "xfce_smoke_runner.py"
    spec = importlib.util.spec_from_file_location("xfce_smoke_runner", runner_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.collect_images


collect_images = _load_collect_images()


def test_collect_images_returns_absolute_paths():
    images = collect_images(["tests/data"])
    assert images
    assert all(p.is_absolute() for p in images)


def test_collect_images_deduplicates_same_file_from_file_and_dir():
    direct = Path("tests/data/left.jpg")
    images = collect_images(["tests/data", str(direct)])
    left = [p for p in images if p.name == "left.jpg"]
    assert len(left) == 1

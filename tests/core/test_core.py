import pytest
from pathlib import Path


def test_single_monitor_smoke():
    """単画面 optimize の基本結果を確認する軽量 smoke test。"""
    try:
        from harite import core
    except ImportError:
        pytest.skip("harite.core を import できないためスキップ")

    inputs = [Path("tests/data/img_wide.jpg")]
    target_resolution = (1920, 1080)

    # テスト用画像がない環境では smoke を成立させられない。
    if not all(p.exists() for p in inputs):
        pytest.skip("tests/data sample images not present")

    optimized_files, placements = core.optimize_wallpapers(
        inputs=inputs,
        target_resolution=target_resolution,
        output_dir=Path("tests/out"),
        scaling="fill",
        quality=90,
    )

    assert len(placements) >= 1
    p = placements[0]
    assert hasattr(p, "x") and hasattr(p, "y")
    assert p.width >= 1920 or p.height >= 1080


def test_dual_monitor_smoke():
    try:
        from harite import core
    except ImportError:
        pytest.skip("harite.core を import できないためスキップ")

    inputs = [Path("tests/data/left.jpg"), Path("tests/data/right.jpg")]
    target_resolution = (3840, 1080)

    # テスト用画像がない環境では smoke を成立させられない。
    if not all(p.exists() for p in inputs):
        pytest.skip("tests/data sample images not present")

    optimized_files, placements = core.optimize_wallpapers(
        inputs=inputs,
        target_resolution=target_resolution,
        output_dir=Path("tests/out"),
        scaling="fit",
        quality=90,
    )

    assert len(placements) == 2
    left, right = placements
    assert getattr(left, "posit", None) in ("left", "right")
    assert getattr(right, "posit", None) in ("left", "right")

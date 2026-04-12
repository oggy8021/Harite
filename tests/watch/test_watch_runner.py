from __future__ import annotations

import random
from pathlib import Path

import pytest

from harite.watch import run_watch_cycles, select_next_image


def test_select_next_image_sequential_cycles() -> None:
    images = [Path("a.jpg"), Path("b.jpg"), Path("c.jpg")]

    selected1, index1 = select_next_image(images, "sequential", 0)
    selected2, index2 = select_next_image(images, "sequential", index1)
    selected3, index3 = select_next_image(images, "sequential", index2)
    selected4, index4 = select_next_image(images, "sequential", index3)

    assert selected1 == images[0]
    assert selected2 == images[1]
    assert selected3 == images[2]
    assert selected4 == images[0]
    assert index4 == 4


def test_select_next_image_random_stays_in_candidates() -> None:
    images = [Path("a.jpg"), Path("b.jpg"), Path("c.jpg")]
    rng = random.Random(42)

    selected, index = select_next_image(images, "random", 5, rng=rng)

    assert selected in images
    assert index == 5


def test_select_next_image_random_avoids_repeat_if_possible() -> None:
    images = [Path("a.jpg"), Path("b.jpg"), Path("c.jpg")]
    rng = random.Random(1)

    selected, index = select_next_image(
        images,
        "random",
        0,
        previous_selected=Path("a.jpg"),
        rng=rng,
    )

    assert selected in (Path("b.jpg"), Path("c.jpg"))
    assert index == 0


def test_select_next_image_random_allows_repeat_with_single_image() -> None:
    images = [Path("a.jpg")]
    rng = random.Random(1)

    selected, index = select_next_image(
        images,
        "random",
        0,
        previous_selected=Path("a.jpg"),
        rng=rng,
    )

    assert selected == Path("a.jpg")
    assert index == 0


def test_select_next_image_rejects_empty_images() -> None:
    with pytest.raises(ValueError, match="images must not be empty"):
        select_next_image([], "sequential", 0)


def test_select_next_image_rejects_unknown_mode() -> None:
    images = [Path("a.jpg")]

    with pytest.raises(ValueError, match="mode must be one of"):
        select_next_image(images, "shuffle", 0)


def test_run_watch_cycles_respects_iterations() -> None:
    images = [Path("a.jpg"), Path("b.jpg")]
    selected: list[Path] = []
    slept: list[float] = []

    def on_cycle(path: Path, _idx: int) -> None:
        selected.append(path)

    def fake_sleep(sec: float) -> None:
        slept.append(sec)

    completed = run_watch_cycles(
        images=images,
        mode="sequential",
        interval_sec=3,
        iterations=3,
        on_cycle=on_cycle,
        sleep_fn=fake_sleep,
    )

    assert completed == 3
    assert selected == [Path("a.jpg"), Path("b.jpg"), Path("a.jpg")]
    assert slept == [3, 3]


def test_run_watch_cycles_rejects_invalid_interval() -> None:
    images = [Path("a.jpg")]

    with pytest.raises(ValueError, match="interval_sec must be >= 1"):
        run_watch_cycles(
            images=images,
            mode="sequential",
            interval_sec=0,
            iterations=1,
            on_cycle=lambda *_: None,
        )

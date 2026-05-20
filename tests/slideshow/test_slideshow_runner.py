from __future__ import annotations

import random
from pathlib import Path

import pytest

from harite.slideshow import SlideshowCycleState, run_slideshow_cycle, run_slideshow_cycles, select_next_image


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


def test_run_slideshow_cycle_updates_state_for_sequential_mode() -> None:
    images = [Path("a.jpg"), Path("b.jpg"), Path("c.jpg")]
    state = SlideshowCycleState()

    selected1, state = run_slideshow_cycle(images, "sequential", state)
    selected2, state = run_slideshow_cycle(images, "sequential", state)

    assert selected1 == Path("a.jpg")
    assert selected2 == Path("b.jpg")
    assert state.index == 2
    assert state.completed == 2
    assert state.previous_selected == Path("b.jpg")


def test_run_slideshow_cycle_random_avoids_repeat_when_possible() -> None:
    images = [Path("a.jpg"), Path("b.jpg"), Path("c.jpg")]
    rng = random.Random(1)
    state = SlideshowCycleState(previous_selected=Path("a.jpg"), completed=4)

    selected, next_state = run_slideshow_cycle(images, "random", state, rng=rng)

    assert selected in (Path("b.jpg"), Path("c.jpg"))
    assert next_state.index == 0
    assert next_state.completed == 5
    assert next_state.previous_selected == selected


def test_run_slideshow_cycle_rejects_empty_images() -> None:
    with pytest.raises(ValueError, match="images must not be empty"):
        run_slideshow_cycle([], "sequential", SlideshowCycleState())


def test_run_slideshow_cycle_rejects_unknown_mode() -> None:
    images = [Path("a.jpg")]

    with pytest.raises(ValueError, match="mode must be one of"):
        run_slideshow_cycle(images, "shuffle", SlideshowCycleState())


def test_run_slideshow_cycles_runs_until_callback_stops_loop() -> None:
    images = [Path("a.jpg"), Path("b.jpg")]
    selected: list[Path] = []
    slept: list[float] = []

    def on_cycle(path: Path, _idx: int) -> None:
        selected.append(path)
        if len(selected) == 3:
            raise RuntimeError("stop loop")

    def fake_sleep(sec: float) -> None:
        slept.append(sec)

    with pytest.raises(RuntimeError, match="stop loop"):
        run_slideshow_cycles(
            images=images,
            mode="sequential",
            interval_sec=3,
            on_cycle=on_cycle,
            sleep_fn=fake_sleep,
        )

    assert selected == [Path("a.jpg"), Path("b.jpg"), Path("a.jpg")]
    assert slept == [3, 3]


def test_run_slideshow_cycles_rejects_invalid_interval() -> None:
    images = [Path("a.jpg")]

    with pytest.raises(ValueError, match="interval_sec must be >= 1"):
        run_slideshow_cycles(
            images=images,
            mode="sequential",
            interval_sec=0,
            on_cycle=lambda *_: None,
        )

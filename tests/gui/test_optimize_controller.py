from pathlib import Path

import pytest

from harite.gui.controllers.optimize_controller import OptimizeController, OptimizeFormState


def _base_state(tmp_path) -> OptimizeFormState:
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    return OptimizeFormState(
        input_value="a.jpg",
        resolution="1920x1080",
        output_dir=str(out_dir),
    )


def test_validate_rejects_margins_with_wrong_arity(tmp_path):
    controller = OptimizeController()
    state = _base_state(tmp_path)
    state.margins = "1,2,3"

    with pytest.raises(ValueError, match="margins must have 4 comma-separated integers"):
        controller.validate(state)


def test_validate_rejects_negative_margins(tmp_path):
    controller = OptimizeController()
    state = _base_state(tmp_path)
    state.margins = "1,-2,3,4"

    with pytest.raises(ValueError, match="margins must be non-negative"):
        controller.validate(state)


def test_validate_accepts_valid_margins_and_displays(tmp_path):
    controller = OptimizeController()
    state = _base_state(tmp_path)
    state.margins = "1,2,3,4"
    state.l_display = "1920x1080"
    state.r_display = "1280x1024"

    controller.validate(state)


def test_run_optimize_passes_parsed_margins(monkeypatch, tmp_path):
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [Path(kwargs["output_dir"]) / "dummy.jpg"], []

    monkeypatch.setattr(
        "harite.gui.controllers.optimize_controller.optimize_wallpapers",
        fake_optimize_wallpapers,
    )

    controller = OptimizeController()
    state = _base_state(tmp_path)
    state.margins = "10,20,30,40"

    saved, placements = controller.run_optimize(state)

    assert saved
    assert placements == []
    assert captured["margins"] == (10, 20, 30, 40)


def test_run_optimize_passes_save_path(monkeypatch, tmp_path):
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        out = kwargs.get("output_path") or (Path(kwargs["output_dir"]) / "dummy.jpg")
        return [Path(out)], []

    monkeypatch.setattr(
        "harite.gui.controllers.optimize_controller.optimize_wallpapers",
        fake_optimize_wallpapers,
    )

    controller = OptimizeController()
    state = _base_state(tmp_path)
    state.save_path = str(tmp_path / "picked" / "legacy-save.jpg")

    saved, placements = controller.run_optimize(state)

    assert saved
    assert placements == []
    assert captured["output_path"] == Path(state.save_path)

from pathlib import Path

import pytest

from harite.display_context import TwoScreenOptimizeContext
from harite.gui.controllers.optimize_controller import OptimizeController, OptimizeFormState
from harite.workspace import Display


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
    assert captured["align"] == ("center", "center")
    assert captured["valign"] == ("center", "center")


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
    state.save_path = str(tmp_path / "picked" / "save-path.jpg")

    saved, placements = controller.run_optimize(state)

    assert saved
    assert placements == []
    assert captured["output_path"] == Path(state.output_dir) / "harite_output_0001.jpg"


def test_run_optimize_uses_unique_gui_output_path_each_time(monkeypatch, tmp_path):
    captured = []

    def fake_optimize_wallpapers(**kwargs):
        captured.append(kwargs["output_path"])
        Path(kwargs["output_path"]).parent.mkdir(parents=True, exist_ok=True)
        Path(kwargs["output_path"]).write_bytes(b"x")
        return [Path(kwargs["output_path"])], []

    monkeypatch.setattr(
        "harite.gui.controllers.optimize_controller.optimize_wallpapers",
        fake_optimize_wallpapers,
    )

    controller = OptimizeController()
    state = _base_state(tmp_path)

    first_saved, _ = controller.run_optimize(state)
    second_saved, _ = controller.run_optimize(state)

    assert first_saved[0].name == "harite_output_0001.jpg"
    assert second_saved[0].name == "harite_output_0002.jpg"
    assert captured == [first_saved[0], second_saved[0]]


def test_run_export_passes_exact_save_path(monkeypatch, tmp_path):
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        out = Path(kwargs["output_path"])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"x")
        return [out], []

    monkeypatch.setattr(
        "harite.gui.controllers.optimize_controller.optimize_wallpapers",
        fake_optimize_wallpapers,
    )

    controller = OptimizeController()
    state = _base_state(tmp_path)
    export_path = tmp_path / "picked" / "save-path.jpg"

    saved, placements = controller.run_export(state, str(export_path))

    assert saved == [export_path]
    assert placements == []
    assert captured["output_path"] == export_path


def test_run_optimize_resolves_auto_display_values(monkeypatch, tmp_path):
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [Path(kwargs["output_path"])], []

    monkeypatch.setattr(
        "harite.gui.controllers.optimize_controller.optimize_wallpapers",
        fake_optimize_wallpapers,
    )
    monkeypatch.setattr(
        "harite.optimize_settings.build_two_screen_optimize_context",
        lambda: TwoScreenOptimizeContext(
            displays=(
                Display(name="L", width=1920, height=1080, x_offset=0),
                Display(name="R", width=1280, height=1024, x_offset=1920),
            ),
            resolution=(3200, 1080),
            l_display=(1920, 1080),
            r_display=(1280, 1024),
        ),
    )

    controller = OptimizeController()
    state = _base_state(tmp_path)
    state.input_value = "left.jpg,right.jpg"
    state.resolution = "auto"
    state.two_screen = True
    state.l_display = "auto"
    state.r_display = "auto"

    saved, placements = controller.run_optimize(state)

    assert saved
    assert placements == []
    assert captured["target_resolution"] == (3200, 1080)
    assert captured["two_screen"] is True
    assert captured["l_display"] == (1920, 1080)
    assert captured["r_display"] == (1280, 1024)

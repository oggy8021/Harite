"""Tests for issue #317 / slideshow spec §6.1–6.3 (R1–R5).

Red-phase tests: expect implementation in MainWindow + OptimizeController.
See docs/specs/slideshow/harite-slideshow-spec.md.
"""

from __future__ import annotations

from pathlib import Path

from harite.apply_settings import EffectiveApplySettings
from harite.display_context import TwoScreenOptimizeContext
from harite.gui.controllers.optimize_controller import OptimizeController, OptimizeFormState
from harite.gui.views.main_window import MainWindow
from harite.workspace import Display

SLIDESHOW_COMPOSITE_FILENAME = "harite_slideshow.jpg"
SLIDESHOW_WORK_SUBDIR = Path("Harite") / "slideshow"


def _slot_split_path(work_dir: Path, display_name: str) -> Path:
    return work_dir / f"harite_slideshow_{display_name}.jpg"


def _composite_path(work_dir: Path) -> Path:
    return work_dir / SLIDESHOW_COMPOSITE_FILENAME


def _setup_linux_pictures_env(monkeypatch, tmp_path: Path) -> tuple[Path, Path]:
    home = tmp_path / "home"
    pictures_root = home / "Pictures"
    pictures_root.mkdir(parents=True)
    xdg_config = tmp_path / "xdg-config"
    xdg_config.mkdir()
    (xdg_config / "user-dirs.dirs").write_text('XDG_PICTURES_DIR="$HOME/Pictures"\n', encoding="utf-8")
    monkeypatch.setattr("harite.gui.views.main_window.Path.home", lambda: home)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_config))
    monkeypatch.setattr("harite.gui.views.main_window.sys.platform", "linux")
    work_dir = pictures_root / SLIDESHOW_WORK_SUBDIR
    return pictures_root, work_dir


def _dual_screen_context() -> TwoScreenOptimizeContext:
    return TwoScreenOptimizeContext(
        displays=(
            Display(name="HDMI-1", width=1920, height=1080, x_offset=0, y_offset=0),
            Display(name="DP-1", width=1920, height=1080, x_offset=1920, y_offset=0),
        ),
        resolution=(3840, 1080),
        l_display=(1920, 1080),
        r_display=(1920, 1080),
    )


def _install_dual_source_slideshow_mocks(monkeypatch, *, work_dir: Path) -> None:
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        _dual_screen_context,
    )

    split_hdmi = _slot_split_path(work_dir, "HDMI-1")
    split_dp = _slot_split_path(work_dir, "DP-1")
    composite = _composite_path(work_dir)

    def fake_resolve_apply_settings(**kwargs):
        assert kwargs["file"] == composite
        assert Path(kwargs["output_dir"]) == work_dir
        return EffectiveApplySettings(
            apply_mode="per-monitor-auto-split",
            target={"HDMI-1": str(split_hdmi), "DP-1": str(split_dp)},
        )

    monkeypatch.setattr("harite.gui.views.main_window.resolve_apply_settings", fake_resolve_apply_settings)


def _make_dual_source_dirs(tmp_path: Path) -> tuple[Path, Path]:
    left_dir = tmp_path / "slideshow-left"
    right_dir = tmp_path / "slideshow-right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")
    (right_dir / "right-1.png").write_bytes(b"right")
    (right_dir / "right-2.png").write_bytes(b"right-2")
    return left_dir, right_dir


class DummySlideshowPlugin:
    def __init__(self) -> None:
        self.calls: list[object] = []

    def apply(self, path: object) -> bool:
        self.calls.append(path)
        return True


# --- R5: work directory separation ---


def test_resolve_slideshow_work_dir_is_pictures_harite_slideshow(monkeypatch, tmp_path):
    pictures_root, work_dir = _setup_linux_pictures_env(monkeypatch, tmp_path)
    window = MainWindow()

    resolved = window._resolve_slideshow_work_dir()

    assert resolved == work_dir
    assert pictures_root in resolved.parents


def test_slideshow_start_leaves_manual_output_dir_and_shows_work_dir(monkeypatch, tmp_path):
    pictures_root, work_dir = _setup_linux_pictures_env(monkeypatch, tmp_path)
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummySlideshowPlugin())

    window = MainWindow()
    window.form_state.output_dir = str(pictures_root)
    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_slideshow_start() is True

    assert window.form_state.output_dir == str(pictures_root)
    assert window.slideshow_output_display == f"Slideshow output: {work_dir}"


# --- R2 + R5: fixed slots via run_slideshow_optimize ---


def test_dual_source_calls_run_slideshow_optimize_in_work_dir(monkeypatch, tmp_path):
    pictures_root, work_dir = _setup_linux_pictures_env(monkeypatch, tmp_path)
    plugin = DummySlideshowPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)
    _install_dual_source_slideshow_mocks(monkeypatch, work_dir=work_dir)

    observed: list[tuple[str, Path]] = []

    def fake_run_slideshow_optimize(state):
        observed.append((state.output_dir, _composite_path(work_dir)))
        work_dir.mkdir(parents=True, exist_ok=True)
        composite = _composite_path(work_dir)
        composite.write_bytes(b"composite")
        for path in (_slot_split_path(work_dir, "HDMI-1"), _slot_split_path(work_dir, "DP-1")):
            path.write_bytes(b"split")
        return [composite], []

    window = MainWindow()
    window.plugin_name = "linux"
    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)

    left_dir, right_dir = _make_dual_source_dirs(tmp_path)
    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_pick_slideshow_srcdir(str(right_dir), "R") is True
    assert window.on_slideshow_start() is True

    assert len(observed) == 1
    assert observed[0][0] == str(work_dir)
    assert not any(path.name.startswith("harite_output_") for path in work_dir.glob("*.jpg"))


def test_run_slideshow_optimize_writes_fixed_composite_slot(monkeypatch, tmp_path):
    work_dir = tmp_path / "Pictures" / "Harite" / "slideshow"
    work_dir.mkdir(parents=True)
    captured: dict = {}

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
    state = OptimizeFormState(
        input_value="left.jpg,right.jpg",
        resolution="3840x1080",
        output_dir=str(work_dir),
        two_screen=True,
        l_display="1920x1080",
        r_display="1920x1080",
    )

    saved, _placements = controller.run_slideshow_optimize(state)

    assert captured["output_path"] == _composite_path(work_dir)
    assert saved == [_composite_path(work_dir)]


# --- R3: pause / rollback ---


def test_pause_tick_rolls_back_orphan_composite_in_work_dir(monkeypatch, tmp_path):
    pictures_root, work_dir = _setup_linux_pictures_env(monkeypatch, tmp_path)
    plugin = DummySlideshowPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        _dual_screen_context,
    )

    optimize_calls = 0

    def fake_run_slideshow_optimize(_state):
        nonlocal optimize_calls
        optimize_calls += 1
        work_dir.mkdir(parents=True, exist_ok=True)
        composite = _composite_path(work_dir)
        composite.write_bytes(b"orphan-composite")
        return [composite], []

    def fake_resolve_apply_settings(**_kwargs):
        if optimize_calls == 1:
            split_hdmi = _slot_split_path(work_dir, "HDMI-1")
            split_dp = _slot_split_path(work_dir, "DP-1")
            split_hdmi.write_bytes(b"split")
            split_dp.write_bytes(b"split")
            return EffectiveApplySettings(
                apply_mode="per-monitor-auto-split",
                target={"HDMI-1": str(split_hdmi), "DP-1": str(split_dp)},
            )
        raise ValueError("per-monitor apply requires at least two detected displays")

    window = MainWindow()
    window.plugin_name = "linux"
    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)
    monkeypatch.setattr("harite.gui.views.main_window.resolve_apply_settings", fake_resolve_apply_settings)

    left_dir, right_dir = _make_dual_source_dirs(tmp_path)
    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_pick_slideshow_srcdir(str(right_dir), "R") is True
    assert window.on_slideshow_start() is True

    assert window.on_slideshow_tick() is True
    assert window.slideshow_paused is True
    assert not _composite_path(work_dir).exists()
    assert not any(path.name.startswith("harite_output_") for path in work_dir.glob("*.jpg"))


# --- R1: work-dir cleanup ---


def test_dual_source_success_removes_legacy_harite_output_from_work_dir(monkeypatch, tmp_path):
    pictures_root, work_dir = _setup_linux_pictures_env(monkeypatch, tmp_path)
    work_dir.mkdir(parents=True)
    legacy = work_dir / "harite_output_0001.jpg"
    legacy.write_bytes(b"legacy")
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummySlideshowPlugin())
    _install_dual_source_slideshow_mocks(monkeypatch, work_dir=work_dir)

    def fake_run_slideshow_optimize(_state):
        work_dir.mkdir(parents=True, exist_ok=True)
        composite = _composite_path(work_dir)
        composite.write_bytes(b"composite")
        for path in (_slot_split_path(work_dir, "HDMI-1"), _slot_split_path(work_dir, "DP-1")):
            path.write_bytes(b"split")
        return [composite], []

    window = MainWindow()
    window.plugin_name = "linux"
    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)

    left_dir, right_dir = _make_dual_source_dirs(tmp_path)
    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_pick_slideshow_srcdir(str(right_dir), "R") is True
    assert window.on_slideshow_start() is True

    assert not legacy.exists()
    assert _composite_path(work_dir).exists()


def test_single_source_success_removes_work_dir_slot_files(monkeypatch, tmp_path):
    pictures_root, work_dir = _setup_linux_pictures_env(monkeypatch, tmp_path)
    work_dir.mkdir(parents=True)
    composite = _composite_path(work_dir)
    split_hdmi = _slot_split_path(work_dir, "HDMI-1")
    composite.write_bytes(b"old-composite")
    split_hdmi.write_bytes(b"old-split")
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummySlideshowPlugin())

    window = MainWindow()
    window._slideshow_active_generated_files = (composite, split_hdmi)
    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_slideshow_start() is True

    assert not composite.exists()
    assert not split_hdmi.exists()
    assert window._slideshow_active_generated_files == ()


# --- R4: stop keeps files, clears tracking ---


def test_slideshow_stop_keeps_slot_files_and_clears_tracking(monkeypatch, tmp_path):
    pictures_root, work_dir = _setup_linux_pictures_env(monkeypatch, tmp_path)
    plugin = DummySlideshowPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)
    _install_dual_source_slideshow_mocks(monkeypatch, work_dir=work_dir)

    def fake_run_slideshow_optimize(_state):
        work_dir.mkdir(parents=True, exist_ok=True)
        composite = _composite_path(work_dir)
        composite.write_bytes(b"composite")
        for path in (_slot_split_path(work_dir, "HDMI-1"), _slot_split_path(work_dir, "DP-1")):
            path.write_bytes(b"split")
        return [composite], []

    window = MainWindow()
    window.plugin_name = "linux"
    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)

    left_dir, right_dir = _make_dual_source_dirs(tmp_path)
    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_pick_slideshow_srcdir(str(right_dir), "R") is True
    assert window.on_slideshow_start() is True
    assert window._slideshow_active_generated_files

    assert window.on_slideshow_stop() is True

    assert _composite_path(work_dir).exists()
    assert _slot_split_path(work_dir, "HDMI-1").exists()
    assert _slot_split_path(work_dir, "DP-1").exists()
    assert window._slideshow_active_generated_files == ()
    assert window._slideshow_tick_generated_files == ()

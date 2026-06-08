"""MAT-11: single-source slideshow runs Optimize like Main."""

from __future__ import annotations

from pathlib import Path

import pytest

from harite.gui.views.main_window import MainWindow

SLIDESHOW_COMPOSITE_FILENAME = "harite_slideshow.jpg"
SLIDESHOW_WORK_SUBDIR = Path("Harite") / "slideshow"


def _composite_path(work_dir: Path) -> Path:
    return work_dir / SLIDESHOW_COMPOSITE_FILENAME


def _slot_split_path(work_dir: Path, display_name: str) -> Path:
    return work_dir / f"harite_slideshow_{display_name}.jpg"


def _setup_linux_pictures_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> tuple[Path, Path]:
    home = tmp_path / "home"
    xdg_config = tmp_path / "xdg-config"
    pictures_root = home / "Pictures"
    pictures_root.mkdir(parents=True)
    xdg_config.mkdir(parents=True)
    (xdg_config / "user-dirs.dirs").write_text('XDG_PICTURES_DIR="$HOME/Pictures"\n', encoding="utf-8")
    monkeypatch.setattr("harite.gui.views.main_window.Path.home", lambda: home)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_config))
    monkeypatch.setattr("harite.gui.views.main_window.sys.platform", "linux")
    work_dir = pictures_root / SLIDESHOW_WORK_SUBDIR
    return pictures_root, work_dir


class DummySlideshowPlugin:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def apply(self, path: str) -> bool:
        self.calls.append(path)
        return True


def _install_single_source_optimize_mock(
    monkeypatch: pytest.MonkeyPatch,
    window: MainWindow,
    work_dir: Path,
    *,
    observed_states: list | None = None,
) -> None:
    def fake_run_slideshow_optimize(state):
        if observed_states is not None:
            observed_states.append(state)
        work_dir.mkdir(parents=True, exist_ok=True)
        composite = _composite_path(work_dir)
        composite.write_bytes(b"optimized")
        return [composite], []

    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)


def test_single_source_calls_run_slideshow_optimize_in_work_dir(monkeypatch, tmp_path):
    pictures_root, work_dir = _setup_linux_pictures_env(monkeypatch, tmp_path)
    plugin = DummySlideshowPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)
    observed: list = []

    window = MainWindow()
    window.form_state.margins = "10,20,30,40"
    _install_single_source_optimize_mock(monkeypatch, window, work_dir, observed_states=observed)

    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_slideshow_start() is True

    assert len(observed) == 1
    assert observed[0].input_value == str(left_dir / "left-1.jpg")
    assert observed[0].output_dir == str(work_dir)
    assert observed[0].margins == "10,20,30,40"
    assert plugin.calls == [str(_composite_path(work_dir))]
    assert window._slideshow_active_generated_files == (_composite_path(work_dir),)


def test_single_source_tick_applies_optimized_composite(monkeypatch, tmp_path):
    pictures_root, work_dir = _setup_linux_pictures_env(monkeypatch, tmp_path)
    plugin = DummySlideshowPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)

    window = MainWindow()
    _install_single_source_optimize_mock(monkeypatch, window, work_dir)

    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_slideshow_start() is True
    assert window.on_slideshow_tick() is True

    assert len(plugin.calls) == 2
    assert all(call == str(_composite_path(work_dir)) for call in plugin.calls)


def test_single_source_r1_removes_stale_split_slots(monkeypatch, tmp_path):
    pictures_root, work_dir = _setup_linux_pictures_env(monkeypatch, tmp_path)
    plugin = DummySlideshowPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)

    work_dir.mkdir(parents=True)
    stale_split = _slot_split_path(work_dir, "HDMI-1")
    stale_split.write_bytes(b"old-split")

    window = MainWindow()
    _install_single_source_optimize_mock(monkeypatch, window, work_dir)

    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_slideshow_start() is True

    assert not stale_split.exists()
    assert _composite_path(work_dir).exists()

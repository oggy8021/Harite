"""Post-release Wave 2: JMA tick skip and display-loss pause (#493, #497)."""

from __future__ import annotations


from harite.display_context import TwoScreenOptimizeContext
from harite.optimize_settings import DUAL_INPUT_REQUIRES_TWO_DISPLAYS
from harite.sources import empty_catalog
from harite.sources_preset import import_preset_source
from harite.sources_remote import sync_remote_source
from harite.workspace import Display
from tests.test_c01_f_jma_interval_sync import _install_jma_tick_mock

_DUAL_JMA_LIST = {
    "near": {"now": ["stale_JRcolor.png", "fresh_JRcolor.png"]},
    "asia": {"now": ["stale_JRcolor.png", "fresh_JRcolor_asia.png"]},
}


def test_slideshow_tick_skips_apply_when_dual_jma_filename_unchanged(monkeypatch, tmp_path):
    from harite.apply_settings import EffectiveApplySettings

    class DummyPlugin:
        def apply(self, path: object) -> bool:
            return True

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: TwoScreenOptimizeContext(
            displays=(
                Display(name="HDMI-1", width=1920, height=1080, x_offset=0, y_offset=0),
                Display(name="DP-1", width=1920, height=1080, x_offset=1920, y_offset=0),
            ),
            resolution=(3840, 1080),
            l_display=(1920, 1080),
            r_display=(1920, 1080),
        ),
    )
    _install_jma_tick_mock(monkeypatch, list_payloads=[_DUAL_JMA_LIST])

    from harite.gui.views.main_window import MainWindow

    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry_l = import_preset_source(catalog, "jma-near-color", cache_root=cache_root)
    entry_r = import_preset_source(catalog, "jma-asia-color", cache_root=cache_root)
    sync_remote_source(catalog, entry_l.id, cache_root=cache_root)
    sync_remote_source(catalog, entry_r.id, cache_root=cache_root)

    work_dir = tmp_path / "slideshow-work"
    composite = work_dir / "harite_slideshow.jpg"
    split_hdmi = work_dir / "harite_slideshow_HDMI-1.jpg"
    split_dp = work_dir / "harite_slideshow_DP-1.jpg"
    optimize_calls = 0

    window = MainWindow()
    window.plugin_name = "linux"
    window.slideshow_profile_id = ""
    window.slideshow_source_id_l = entry_l.id
    window.slideshow_srcdir_l = entry_l.path
    window.slideshow_source_id_r = entry_r.id
    window.slideshow_srcdir_r = entry_r.path

    def fake_run_slideshow_optimize(_state):
        nonlocal optimize_calls
        optimize_calls += 1
        work_dir.mkdir(parents=True, exist_ok=True)
        composite.write_bytes(b"composite")
        split_hdmi.write_bytes(b"hdmi")
        split_dp.write_bytes(b"dp")
        return [composite], []

    def fake_resolve_apply_settings(**_kwargs):
        return EffectiveApplySettings(
            apply_mode="per-monitor-auto-split",
            target={"HDMI-1": str(split_hdmi), "DP-1": str(split_dp)},
        )

    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)
    monkeypatch.setattr("harite.gui.views.main_window.resolve_apply_settings", fake_resolve_apply_settings)
    monkeypatch.setattr(window, "_resolve_slideshow_work_dir", lambda: work_dir)
    monkeypatch.setattr(window, "_sync_remote_sources_for_slideshow_start", lambda _catalog: None)
    monkeypatch.setattr(window, "load_source_catalog", lambda: catalog)

    assert window.on_slideshow_start() is True, window.last_error
    assert optimize_calls == 1

    assert window.on_slideshow_tick() is True
    assert optimize_calls == 1
    assert window.slideshow_running is True
    assert any("tick skipped: no remote update" in line for line in window.logs)


def test_slideshow_tick_pauses_on_dual_input_display_loss(monkeypatch, tmp_path):
    from harite.apply_settings import EffectiveApplySettings

    class DummyPlugin:
        def apply(self, path: object) -> bool:
            return True

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: TwoScreenOptimizeContext(
            displays=(
                Display(name="HDMI-1", width=1920, height=1080, x_offset=0, y_offset=0),
                Display(name="DP-1", width=1920, height=1080, x_offset=1920, y_offset=0),
            ),
            resolution=(3840, 1080),
            l_display=(1920, 1080),
            r_display=(1920, 1080),
        ),
    )

    from harite.gui.views.main_window import MainWindow

    work_dir = tmp_path / "slideshow-work"
    composite = work_dir / "harite_slideshow.jpg"
    split_hdmi = work_dir / "harite_slideshow_HDMI-1.jpg"
    split_dp = work_dir / "harite_slideshow_DP-1.jpg"
    optimize_calls = 0

    window = MainWindow()
    window.plugin_name = "linux"

    def fake_run_slideshow_optimize(_state):
        nonlocal optimize_calls
        optimize_calls += 1
        if optimize_calls >= 2:
            raise ValueError(DUAL_INPUT_REQUIRES_TWO_DISPLAYS)
        work_dir.mkdir(parents=True, exist_ok=True)
        composite.write_bytes(b"composite")
        split_hdmi.write_bytes(b"hdmi")
        split_dp.write_bytes(b"dp")
        return [composite], []

    def fake_resolve_apply_settings(**_kwargs):
        return EffectiveApplySettings(
            apply_mode="per-monitor-auto-split",
            target={"HDMI-1": str(split_hdmi), "DP-1": str(split_dp)},
        )

    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)
    monkeypatch.setattr("harite.gui.views.main_window.resolve_apply_settings", fake_resolve_apply_settings)
    monkeypatch.setattr(window, "_resolve_slideshow_work_dir", lambda: work_dir)

    left_dir = tmp_path / "slideshow-left"
    right_dir = tmp_path / "slideshow-right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")
    (right_dir / "right-1.png").write_bytes(b"right")
    (right_dir / "right-2.png").write_bytes(b"right-2")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_pick_slideshow_srcdir(str(right_dir), "R") is True
    assert window.on_slideshow_start() is True

    assert window.on_slideshow_tick() is True
    assert window.slideshow_running is True
    assert window.slideshow_paused is True
    assert "waiting for two detected displays" in window.status_message

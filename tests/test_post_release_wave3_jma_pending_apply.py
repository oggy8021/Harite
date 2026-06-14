"""Post-release Wave 3 (#503): recover pending remote apply after display pause."""

from __future__ import annotations

import json

from harite.apply_settings import EffectiveApplySettings
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


def _setup_dual_jma_window(monkeypatch, tmp_path):
    from harite.gui.views.main_window import MainWindow

    class DummyPlugin:
        def apply(self, path: object) -> bool:
            return True

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())
    monkeypatch.setattr("harite.gui.views.main_window.dual_display_detected", lambda: True)
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

    window = MainWindow()
    window.plugin_name = "linux"
    window.slideshow_profile_id = ""
    window.slideshow_source_id_l = entry_l.id
    window.slideshow_srcdir_l = entry_l.path
    window.slideshow_source_id_r = entry_r.id
    window.slideshow_srcdir_r = entry_r.path

    optimize_calls = {"count": 0}

    def fake_run_slideshow_optimize(_state):
        optimize_calls["count"] += 1
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

    return window, optimize_calls


def test_slideshow_tick_reapplies_when_pending_remote_apply_set(monkeypatch, tmp_path):
    window, optimize_calls = _setup_dual_jma_window(monkeypatch, tmp_path)

    assert window.on_slideshow_start() is True
    assert optimize_calls["count"] == 1

    assert window.on_slideshow_tick() is True
    assert optimize_calls["count"] == 1
    assert window._slideshow_pending_remote_apply is False

    window._slideshow_pending_remote_apply = True
    assert window.on_slideshow_tick() is True
    assert optimize_calls["count"] == 2
    assert window._slideshow_pending_remote_apply is False


def test_slideshow_tick_pause_logs_display_paused_with_pending(monkeypatch, tmp_path):
    window, optimize_calls = _setup_dual_jma_window(monkeypatch, tmp_path)
    log_path = tmp_path / "slideshow-op.jsonl"
    monkeypatch.setenv("HARITE_SLIDESHOW_OP_LOG", str(log_path))

    optimize_calls_ref = {"count": 0}

    def fake_run_slideshow_optimize(_state):
        optimize_calls_ref["count"] += 1
        if optimize_calls_ref["count"] >= 2:
            raise ValueError(DUAL_INPUT_REQUIRES_TWO_DISPLAYS)
        work_dir = tmp_path / "slideshow-work"
        work_dir.mkdir(parents=True, exist_ok=True)
        composite = work_dir / "harite_slideshow.jpg"
        composite.write_bytes(b"composite")
        return [composite], []

    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)

    left_dir = tmp_path / "slideshow-left"
    right_dir = tmp_path / "slideshow-right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (right_dir / "right-1.png").write_bytes(b"right")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_pick_slideshow_srcdir(str(right_dir), "R") is True

    assert window.on_slideshow_start() is True
    log_path.write_text("", encoding="utf-8")

    assert window.on_slideshow_tick() is True
    assert window.slideshow_paused is True
    assert window._slideshow_pending_remote_apply is False

    records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    paused = [record for record in records if record.get("skip_reason") == "display_paused"]
    assert len(paused) == 1
    assert paused[0]["ok"] is True
    assert "detected_display_count" in paused[0]


def test_remote_update_then_pause_then_filename_unchanged_still_reapplies(monkeypatch, tmp_path):
    from harite.sources_remote import RemoteSlideshowTickOutcome

    window, _optimize_calls = _setup_dual_jma_window(monkeypatch, tmp_path)
    optimize_calls_ref = {"count": 0}
    jma_tick_calls = {"count": 0}

    def fake_jma_tick(*_args, **_kwargs):
        jma_tick_calls["count"] += 1
        if jma_tick_calls["count"] <= 2:
            return RemoteSlideshowTickOutcome(ok=True, no_update=False)
        return RemoteSlideshowTickOutcome(ok=True, no_update=True)

    monkeypatch.setattr("harite.sources_remote_jma.jma_slideshow_tick", fake_jma_tick)

    def fake_run_slideshow_optimize(_state):
        optimize_calls_ref["count"] += 1
        if optimize_calls_ref["count"] == 2:
            raise ValueError(DUAL_INPUT_REQUIRES_TWO_DISPLAYS)
        work_dir = tmp_path / "slideshow-work"
        work_dir.mkdir(parents=True, exist_ok=True)
        composite = work_dir / "harite_slideshow.jpg"
        composite.write_bytes(b"composite")
        return [composite], []

    def fake_resolve_apply_settings(**_kwargs):
        return EffectiveApplySettings(apply_mode="single", target=str(tmp_path / "slideshow-work" / "harite_slideshow.jpg"))

    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)
    monkeypatch.setattr("harite.gui.views.main_window.resolve_apply_settings", fake_resolve_apply_settings)

    assert window.on_slideshow_start() is True

    assert window.on_slideshow_tick() is True
    assert window.slideshow_paused is True
    assert window._slideshow_pending_remote_apply is True

    assert window.on_slideshow_tick() is True
    assert optimize_calls_ref["count"] == 3
    assert window._slideshow_pending_remote_apply is False
    assert window.slideshow_paused is False

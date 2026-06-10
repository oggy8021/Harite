from __future__ import annotations

from pathlib import Path

import pytest

from harite.slideshow_optimize import (
    apply_slideshow_selection,
    build_slideshow_optimize_config,
    validate_dual_source_slideshow,
)
def test_build_slideshow_optimize_config_reads_optimize_keys() -> None:
    cfg = {
        "resolution": "2560x1440",
        "margins": "10,0,10,0",
        "align": ["left", "right"],
        "slideshow_interval_seconds": 90,
        "plugin": "windows",
    }
    config = build_slideshow_optimize_config(cfg, default_plugin="linux")

    assert config.base_form_state.resolution == "2560x1440"
    assert config.base_form_state.margins == "10,0,10,0"
    assert config.base_form_state.align == ("left", "right")
    assert config.apply_mode in {"single-file", "per-monitor-auto-split"}


def test_build_slideshow_optimize_config_uses_slideshow_auto_scale_keys() -> None:
    cfg = {
        "l_auto_display_scale": False,
        "r_auto_display_scale": False,
        "l_display_scale": 1.5,
        "r_display_scale": 2.0,
        "slideshow_l_auto_display_scale": True,
        "slideshow_r_auto_display_scale": True,
    }
    config = build_slideshow_optimize_config(cfg, default_plugin="linux")

    assert config.base_form_state.l_auto_display_scale is True
    assert config.base_form_state.r_auto_display_scale is True
    assert config.base_form_state.l_display_scale == 1.0
    assert config.base_form_state.r_display_scale == 1.0


def test_build_slideshow_optimize_config_ignores_optimize_auto_scale_keys() -> None:
    cfg = {
        "l_auto_display_scale": True,
        "r_auto_display_scale": True,
        "slideshow_l_auto_display_scale": False,
        "slideshow_r_auto_display_scale": False,
    }
    config = build_slideshow_optimize_config(cfg, default_plugin="linux")

    assert config.base_form_state.l_auto_display_scale is False
    assert config.base_form_state.r_auto_display_scale is False


def test_apply_slideshow_single_source_runs_optimize_and_apply(tmp_path, monkeypatch) -> None:
    img = tmp_path / "src.jpg"
    img.write_bytes(b"fake")

    work_dir = tmp_path / "work"
    config = build_slideshow_optimize_config({}, default_plugin="windows")
    config = type(config)(
        base_form_state=type(config.base_form_state)(
            input_value="",
            resolution=config.base_form_state.resolution,
            output_dir=str(work_dir),
            scaling=config.base_form_state.scaling,
            two_screen=config.base_form_state.two_screen,
            margins=config.base_form_state.margins,
            l_display=config.base_form_state.l_display,
            r_display=config.base_form_state.r_display,
            l_display_scale=config.base_form_state.l_display_scale,
            r_display_scale=config.base_form_state.r_display_scale,
            align=config.base_form_state.align,
            valign=config.base_form_state.valign,
            quality=config.base_form_state.quality,
            background_color=config.base_form_state.background_color,
            embed_info=config.base_form_state.embed_info,
            embed_text=config.base_form_state.embed_text,
            embed_position=config.base_form_state.embed_position,
            embed_max_lines=config.base_form_state.embed_max_lines,
        ),
        apply_mode=config.apply_mode,
        windows_apply_span=config.windows_apply_span,
        work_dir=work_dir,
        dual_auto_split=False,
    )

    composite = work_dir / "harite_slideshow.jpg"

    class FakeController:
        def run_slideshow_optimize(self, state):
            work_dir.mkdir(parents=True, exist_ok=True)
            composite.write_bytes(b"optimized")
            return [composite], []

    applied = []

    class FakePlugin:
        def apply(self, target):
            applied.append(target)
            return True

    ok, err, target = apply_slideshow_selection(
        str(img),
        "-",
        config=config,
        controller=FakeController(),
        plugin_impl=FakePlugin(),
    )

    assert ok is True
    assert err is None
    assert Path(str(target)) == composite
    assert applied == [str(composite)]


def test_validate_dual_source_rejects_unknown_plugin() -> None:
    with pytest.raises(ValueError, match="not supported"):
        validate_dual_source_slideshow("macos")


def test_validate_dual_source_requires_two_displays(monkeypatch) -> None:
    monkeypatch.setattr(
        "harite.slideshow_optimize.build_two_screen_optimize_context",
        lambda *_args, **_kwargs: None,
    )
    with pytest.raises(ValueError, match="two detected displays"):
        validate_dual_source_slideshow("windows")

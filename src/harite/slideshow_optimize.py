"""Headless slideshow optimize + apply (MAT-11 parity for CLI)."""

from __future__ import annotations

import ctypes
import os
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Callable, Sequence

from harite.apply_settings import resolve_apply_settings
from harite.core import normalize_background_color
from harite.display_context import build_two_screen_optimize_context
from harite.gui.controllers.optimize_controller import OptimizeController, OptimizeFormState
from harite.settings import AppSettings
from harite.slideshow import SlideshowCycleState, collect_slideshow_input_images, run_slideshow_cycle
from harite.workspace import detect_displays

_EMBED_POSITION_VALUES = frozenset({"left-top", "left-bottom", "right-top", "right-bottom"})


@dataclass
class SlideshowOptimizeConfig:
    base_form_state: OptimizeFormState
    apply_mode: str
    windows_apply_span: bool
    work_dir: Path
    dual_auto_split: bool


def resolve_default_pictures_dir() -> Path:
    if sys.platform == "win32":
        try:
            buffer = ctypes.create_unicode_buffer(260)
            result = ctypes.windll.shell32.SHGetFolderPathW(None, 0x27, None, 0, buffer)
            if result == 0 and buffer.value:
                return Path(buffer.value)
        except (AttributeError, OSError):
            pass

    env_value = str(os.environ.get("XDG_PICTURES_DIR", "") or "").strip()
    if env_value:
        return _normalize_pictures_dir(env_value)

    config_home = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))
    user_dirs_path = config_home / "user-dirs.dirs"
    if user_dirs_path.is_file():
        try:
            for raw_line in user_dirs_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or not line.startswith("XDG_PICTURES_DIR="):
                    continue
                return _normalize_pictures_dir(line.split("=", 1)[1].strip())
        except OSError:
            pass

    return Path.home() / "Pictures"


def resolve_slideshow_work_dir() -> Path:
    return resolve_default_pictures_dir() / "Harite" / "slideshow"


def _normalize_pictures_dir(raw_value: str) -> Path:
    value = raw_value.strip().strip('"').strip("'")
    home = str(Path.home())
    value = value.replace("$HOME", home).replace("${HOME}", home)
    value = os.path.expandvars(value)
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return Path.home() / path


def _normalize_embed_position(value: str) -> str:
    normalized = str(value or "right-bottom").strip().lower()
    if normalized in _EMBED_POSITION_VALUES:
        return normalized
    return "right-bottom"


def build_slideshow_optimize_config(cfg: dict, *, default_plugin: str) -> SlideshowOptimizeConfig:
    app = (
        AppSettings.from_settings_dict(cfg, default_plugin=default_plugin)
        if cfg
        else AppSettings.defaults(default_plugin=default_plugin)
    )
    work_dir = resolve_slideshow_work_dir()
    optimize = app.optimize

    base_form_state = OptimizeFormState(
        input_value="",
        output_dir=str(work_dir),
        canvas_scale_percent=optimize.canvas_scale_percent,
        scaling=optimize.scaling,
        margins=optimize.margins,
        l_display_scale=1.0,
        r_display_scale=1.0,
        l_auto_display_scale=app.slideshow.l_auto_display_scale,
        r_auto_display_scale=app.slideshow.r_auto_display_scale,
        align=optimize.align,
        valign=optimize.valign,
        quality=optimize.quality,
        background_color=normalize_background_color(optimize.background_color),
        embed_info=optimize.embed_info,
        embed_text=optimize.embed_text,
        embed_position=_normalize_embed_position(optimize.embed_position),
        embed_max_lines=optimize.embed_max_lines,
    )

    return SlideshowOptimizeConfig(
        base_form_state=base_form_state,
        apply_mode=app.apply.apply_mode,
        windows_apply_span=app.apply.windows_apply_span,
        work_dir=work_dir,
        dual_auto_split=False,
    )


def validate_dual_source_slideshow(plugin_name: str) -> None:
    if plugin_name not in ("linux", "windows"):
        raise ValueError(f"dual-source slideshow is not supported for plugin {plugin_name}")
    if build_two_screen_optimize_context() is None:
        raise ValueError("dual-source slideshow requires two detected displays")


def _build_dual_optimize_state(base: OptimizeFormState, left: str, right: str) -> OptimizeFormState:
    state = replace(base, input_value=f"{left},{right}")
    context = build_two_screen_optimize_context()
    if context is not None:
        state = replace(
            state,
            two_screen=True,
            l_display=f"{context.l_display[0]}x{context.l_display[1]}",
            r_display=f"{context.r_display[0]}x{context.r_display[1]}",
            resolution=f"{context.resolution[0]}x{context.resolution[1]}",
        )
    return state


def _cleanup_tick_files(paths: Sequence[Path]) -> None:
    for path in paths:
        try:
            if path.exists():
                path.unlink()
        except OSError:
            pass


def _cleanup_work_dir_orphans(work_dir: Path, keep: frozenset[Path]) -> None:
    try:
        for pattern in ("harite_output_*.jpg", "harite_slideshow.jpg", "harite_slideshow_*.jpg"):
            for path in work_dir.glob(pattern):
                if path not in keep:
                    try:
                        path.unlink()
                    except OSError:
                        pass
    except OSError:
        pass


def _apply_plugin_target(plugin_impl, target: object, *, windows_span: bool, windows_apply_span: bool) -> bool:
    if windows_span and windows_apply_span:
        from harite.windows_wallpaper import ensure_span_style

        ensure_span_style()
    return bool(plugin_impl.apply(target))


def apply_slideshow_single_source(
    image_path: str,
    *,
    config: SlideshowOptimizeConfig,
    controller: OptimizeController,
    plugin_impl,
) -> tuple[bool, str | None, Path | None]:
    tick_files: list[Path] = []
    try:
        slideshow_state = replace(config.base_form_state, input_value=image_path)
        saved_files, _placements = controller.run_slideshow_optimize(slideshow_state)
        composite_path = saved_files[-1]
        tick_files.append(composite_path)
    except ValueError as exc:
        _cleanup_tick_files(tick_files)
        return False, f"slideshow single-source optimize failed: {exc}", None

    try:
        success = _apply_plugin_target(
            plugin_impl,
            str(composite_path),
            windows_span=False,
            windows_apply_span=config.windows_apply_span,
        )
    except Exception as exc:
        _cleanup_tick_files(tick_files)
        return False, f"slideshow single-file apply error: {exc}", None

    if success:
        _cleanup_work_dir_orphans(config.work_dir, frozenset(tick_files))
        return True, None, composite_path

    _cleanup_tick_files(tick_files)
    return False, "slideshow single-file apply failed", None


def apply_slideshow_dual_source(
    left: str,
    right: str,
    *,
    config: SlideshowOptimizeConfig,
    controller: OptimizeController,
    plugin_impl,
) -> tuple[bool, str | None, object | None]:
    tick_files: list[Path] = []
    try:
        slideshow_state = _build_dual_optimize_state(config.base_form_state, left, right)
        saved_files, _placements = controller.run_slideshow_optimize(slideshow_state)
        composite_path = saved_files[-1]
        tick_files.append(composite_path)
        effective_apply = resolve_apply_settings(
            file=composite_path,
            apply_mode="per-monitor-auto-split",
            output_dir=config.work_dir,
            displays=detect_displays(),
        )
    except ValueError as exc:
        _cleanup_tick_files(tick_files)
        return False, f"slideshow auto-split prepare failed: {exc}", None

    generated_files = [composite_path]
    if not effective_apply.windows_span and isinstance(effective_apply.target, dict):
        generated_files.extend(Path(str(path)) for path in effective_apply.target.values())

    try:
        success = _apply_plugin_target(
            plugin_impl,
            effective_apply.target,
            windows_span=effective_apply.windows_span,
            windows_apply_span=config.windows_apply_span,
        )
    except Exception as exc:
        _cleanup_tick_files(generated_files)
        return False, f"slideshow per-monitor auto-split apply error: {exc}", None

    if success:
        _cleanup_work_dir_orphans(config.work_dir, frozenset(generated_files))
        return True, None, effective_apply.target

    _cleanup_tick_files(generated_files)
    return False, "slideshow per-monitor auto-split apply failed", None


def apply_slideshow_selection(
    left: str,
    right: str,
    *,
    config: SlideshowOptimizeConfig,
    controller: OptimizeController,
    plugin_impl,
) -> tuple[bool, str | None, object | None]:
    selected_paths = [path for path in (left, right) if path != "-"]
    if not selected_paths:
        return True, None, None
    if len(selected_paths) == 1:
        ok, err, target = apply_slideshow_single_source(
            selected_paths[0],
            config=config,
            controller=controller,
            plugin_impl=plugin_impl,
        )
        return ok, err, target
    if not config.dual_auto_split:
        return False, "dual-source slideshow auto-split is not enabled", None
    return apply_slideshow_dual_source(
        selected_paths[0],
        selected_paths[1],
        config=config,
        controller=controller,
        plugin_impl=plugin_impl,
    )


def run_slideshow_optimize_cycles(
    *,
    input_dirs: Sequence[Path],
    mode: str,
    interval_sec: int,
    config: SlideshowOptimizeConfig,
    controller: OptimizeController,
    plugin_impl,
    on_cycle: Callable[[object | None, int, bool, str | None], None],
    sleep_fn: Callable[[float], None] = time.sleep,
) -> int:
    if interval_sec < 1:
        raise ValueError("interval_sec must be >= 1")
    if not input_dirs:
        raise ValueError("input_dirs must not be empty")

    images_by_dir = [collect_slideshow_input_images([directory]) for directory in input_dirs]
    state_l = SlideshowCycleState()
    state_r = SlideshowCycleState()
    completed = 0

    while True:
        if len(input_dirs) == 1:
            selected, state_l = run_slideshow_cycle(images_by_dir[0], mode, state_l)
            ok, err, target = apply_slideshow_single_source(
                str(selected),
                config=config,
                controller=controller,
                plugin_impl=plugin_impl,
            )
            on_cycle(target, completed, ok, err)
        else:
            selected_l, state_l = run_slideshow_cycle(images_by_dir[0], mode, state_l)
            selected_r, state_r = run_slideshow_cycle(images_by_dir[1], mode, state_r)
            ok, err, target = apply_slideshow_selection(
                str(selected_l),
                str(selected_r),
                config=config,
                controller=controller,
                plugin_impl=plugin_impl,
            )
            on_cycle(target, completed, ok, err)

        completed += 1
        sleep_fn(interval_sec)

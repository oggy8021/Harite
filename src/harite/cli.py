"""CLI entrypoints for Harite."""
from __future__ import annotations

import sys
import typer
from pathlib import Path
from typing import Optional, List, Tuple
import json

from . import __version__
from .apply_settings import resolve_apply_settings
from .core import (
    DEFAULT_BACKGROUND_COLOR_HEX,
    PlacementResult,
    is_background_color_literal,
    normalize_background_color,
    normalize_optimize_input_paths,
    optimize_wallpapers,
)
from .plugins import registry as plugin_registry
from .settings import AppSettings, SlideshowSettings
from .settings_file import load_settings
from .linux_xdg_launcher import install_desktop_entry as install_linux_desktop_entry
from .last_optimize_run import default_last_optimize_search_dirs, read_last_optimize_run, write_last_optimize_run
from .optimize_settings import normalize_canvas_scale_percent, resolve_optimize_display_settings
from .positioning import parse_position_pair
from .resolution import parse_resolution
from .slideshow import collect_slideshow_input_images
from .slideshow_optimize import (
    build_slideshow_optimize_config,
    run_slideshow_optimize_cycles,
    validate_dual_source_slideshow,
)

app = typer.Typer(help="Harite - wallpaper optimizer")


def _default_plugin_name() -> str:
    platform_map = {
        "win32": "windows",
        "darwin": "macos",
    }
    preferred = platform_map.get(sys.platform, "linux")
    available = plugin_registry.list()
    if preferred in available:
        return preferred
    if available:
        return available[0]
    return "windows"


def _resolve_plugin_name(cfg: dict) -> str:
    """Resolve apply/slideshow plugin: settings ``plugin`` key, else OS default."""
    return AppSettings.from_settings_dict(cfg, default_plugin=_default_plugin_name()).apply.plugin_name


def format_placement_line(placement: PlacementResult) -> str:
    """Format one placement for CLI stdout (harite-cli-spec §4.1)."""
    name = placement.image_path.name
    line = (
        f"{name} @ ({placement.x},{placement.y}) "
        f"{placement.width}x{placement.height} scale={placement.scale}"
    )
    if placement.posit:
        line = f"{line} posit={placement.posit}"
    return line


def parse_margins(value: str) -> Tuple[int, int, int, int]:
    """Parse margins as left,right,top,bottom pixel values."""
    parts = [p.strip() for p in value.split(",") if p.strip()]
    if len(parts) != 4:
        raise ValueError("Margins must have four comma-separated integers: l,r,top,bottom")
    try:
        vals = tuple(int(p) for p in parts)
    except Exception:
        raise ValueError("Margins must be integers")
    if any(v < 0 for v in vals):
        raise ValueError("Margins must be non-negative")
    return vals


def parse_display(value: str) -> Tuple[int, int]:
    """Parse display size strings like '1920x1080'."""
    return parse_resolution(value)


def parse_config_bool(name: str, value: object) -> bool:
    """Parse a bool-like config value strictly.

    Accepted values:
    - bool: True/False
    - int: 1/0
    - str: true/false/1/0/yes/no/on/off
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        if value in (0, 1):
            return bool(value)
        raise ValueError(f"invalid settings bool for {name}: {value}")
    if isinstance(value, str):
        raw = value.strip().lower()
        truthy = {"1", "true", "yes", "on"}
        falsy = {"0", "false", "no", "off"}
        if raw in truthy:
            return True
        if raw in falsy:
            return False
        raise ValueError(f"invalid settings bool for {name}: {value}")
    raise ValueError(f"invalid settings bool for {name}: {value}")


def _parameter_source_is_commandline(ctx: typer.Context, name: str) -> bool:
    """Return True when the option was explicitly provided on the CLI.

    Typer/Click may expose ``ParameterSource`` members whose numeric values differ
    across Click releases (e.g. COMMANDLINE was renumbered in Click 8.4). Compare
    by stable member name instead of enum identity/value.
    """
    try:
        source = ctx.get_parameter_source(name)
    except (AttributeError, LookupError):
        return False
    if source is None:
        return False
    return getattr(source, "name", None) == "COMMANDLINE"


def resolve_bool_option(
    name: str,
    cli_value: bool,
    cfg: dict,
    ctx: typer.Context,
) -> bool:
    """Resolve a bool option with priority CLI > config > default."""
    if _parameter_source_is_commandline(ctx, name):
        return bool(cli_value)
    if name in cfg:
        return parse_config_bool(name, cfg[name])
    return bool(cli_value)


def resolve_option_value(
    name: str,
    cli_value: object,
    cfg: dict,
    ctx: typer.Context,
) -> object:
    if _parameter_source_is_commandline(ctx, name):
        return cli_value
    return cfg.get(name, cli_value)


def _slideshow_srcdir_paths_from_settings(cfg: dict) -> List[Path]:
    slideshow = SlideshowSettings.from_settings_dict(cfg)
    dirs: List[Path] = []
    for raw in (slideshow.srcdir_l, slideshow.srcdir_r):
        if raw is None:
            continue
        text = str(raw).strip()
        if text:
            dirs.append(Path(text).expanduser())
    return dirs[:2]


def _expand_slideshow_cli_input_dirs(input: List[str] | None) -> List[Path]:
    input_dirs: List[Path] = []
    if not input:
        return input_dirs
    for it in input:
        parts = [p.strip() for p in it.split(",") if p.strip()]
        input_dirs.extend(Path(part).expanduser() for part in parts)
    return input_dirs[:2]


@app.callback(invoke_without_command=True)
def _callback(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(False, "--version", help="Show version and exit"),
) -> None:
    if version:
        typer.echo(__version__)
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.echo("Harite CLI. Use --help for commands.")
        raise typer.Exit()


@app.command()
def optimize(
    ctx: typer.Context,
    input: Optional[List[str]] = typer.Option(
        None,
        "--input",
        "-i",
        help="Input file(s). Use comma-separated paths or repeat --input.",
        rich_help_panel="必須に近い入力",
    ),
    output: Path = typer.Option(
        Path("."),
        "--output",
        "-o",
        help="Output directory",
        rich_help_panel="基本オプション",
    ),
    canvas_scale: Optional[int] = typer.Option(
        None,
        "--canvas-scale",
        help="Composite canvas size as percent of detected desktop (1-100, default 100).",
        rich_help_panel="条件付きオプション（通常は省略可）",
    ),
    margins: Optional[str] = typer.Option(
        None,
        "--margins",
        help="Margins as left,right,top,bottom in pixels (e.g. 10,10,0,0). Constrain fit only; align uses full slot.",
        rich_help_panel="条件付きオプション（通常は省略可）",
    ),
    align: str = typer.Option(
        "center",
        "--align",
        help=(
            "Horizontal align for left,right images (e.g. left,right). "
            "A single value applies to both. Uses full display slot, not margin inset."
        ),
        rich_help_panel="条件付きオプション（通常は省略可）",
    ),
    valign: str = typer.Option(
        "center",
        "--valign",
        help=(
            "Vertical align for left,right images (e.g. top,bottom). "
            "A single value applies to both. Uses full display slot, not margin inset."
        ),
        rich_help_panel="条件付きオプション（通常は省略可）",
    ),
    quality: int = typer.Option(
        90,
        "--quality",
        help="JPEG quality",
        rich_help_panel="詳細調整",
    ),
    background_color: str = typer.Option(
        DEFAULT_BACKGROUND_COLOR_HEX,
        "--background-color",
        help="Background color as hex RGB (e.g. E0E0E0)",
        rich_help_panel="詳細調整",
    ),
    settings_file: Optional[Path] = typer.Option(
        None,
        "--settings-file",
        "-c",
        help="Optional path to optimize settings JSON",
        rich_help_panel="詳細調整",
    ),
    embed_info: str = typer.Option(
        "none",
        "--embed-info",
        help="Embed info text in margins: none|params|free|combo",
        rich_help_panel="条件付きオプション（通常は省略可）",
    ),
    embed_text: Optional[str] = typer.Option(
        None,
        "--embed-text",
        help="Free text used by --embed-info free|combo",
        rich_help_panel="条件付きオプション（通常は省略可）",
    ),
    embed_position: str = typer.Option(
        "right-bottom",
        "--embed-position",
        help="Margin text position: left-top|left-bottom|right-top|right-bottom",
        rich_help_panel="条件付きオプション（通常は省略可）",
    ),
    embed_max_lines: int = typer.Option(
        3,
        "--embed-max-lines",
        help="Maximum lines for embedded text",
        rich_help_panel="詳細調整",
    ),
    embed_font: Optional[Path] = typer.Option(
        None,
        "--embed-font",
        help="Font file path (.ttf/.otf/.ttc) used for --embed-text rendering",
        rich_help_panel="詳細調整",
    ),
) -> None:
    """Optimize wallpapers.

    `--input` accepts image files only (not directories), via comma-separated paths
    or repeated `--input` (max 2 images).

    Display geometry is inferred from workspace and input count (max 2 images / 2 monitors).
    Use `--canvas-scale` (1-100) to shrink the composite canvas below detected desktop size.

    Geometry (core-spec §4.1): `margins` (left,right,top,bottom) constrain image
    fit/shrink; `align` / `valign` use the full display slot for positioning.

    Embed: `--embed-info` is `none|params|free|combo`; use `--embed-text` with
    `free` or `combo`. `--embed-font` is optional (auto font discovery when omitted).
    """
    # Load settings if provided and merge defaults (CLI options override settings)
    cfg: dict = {}
    if settings_file is not None:
        try:
            cfg = load_settings(settings_file)
        except Exception as exc:
            typer.echo(f"Failed to load settings: {exc}")
            raise typer.Exit(code=2)

    # validate numeric options
    if not (1 <= quality <= 100):
        typer.echo("--quality must be between 1 and 100")
        raise typer.Exit(code=2)
    embed_info = str(resolve_option_value("embed_info", embed_info, cfg, ctx) or "none").lower()
    if embed_info not in ("none", "params", "free", "combo"):
        typer.echo("--embed-info must be one of: none, params, free, combo")
        raise typer.Exit(code=2)
    embed_position = str(resolve_option_value("embed_position", embed_position, cfg, ctx) or "right-bottom").lower()
    if embed_position not in ("left-top", "left-bottom", "right-top", "right-bottom"):
        typer.echo("--embed-position must be one of: left-top, left-bottom, right-top, right-bottom")
        raise typer.Exit(code=2)
    eff_embed_max_lines = int(resolve_option_value("embed_max_lines", embed_max_lines, cfg, ctx))
    if eff_embed_max_lines <= 0:
        typer.echo("--embed-max-lines must be positive")
        raise typer.Exit(code=2)

    # determine inputs (CLI > settings)
    eff_input = input if input is not None else cfg.get("input")
    if not eff_input:
        typer.echo("--input is required (or provide in --settings-file)")
        raise typer.Exit(code=2)
    expanded_inputs: List[str] = []
    for it in eff_input:
        parts = [p.strip() for p in it.split(",") if p.strip()]
        expanded_inputs.extend(parts)
    expanded_inputs = expanded_inputs[:2]
    try:
        expanded_inputs = [str(path) for path in normalize_optimize_input_paths(expanded_inputs)]
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2)

    if _parameter_source_is_commandline(ctx, "canvas_scale"):
        raw_canvas_scale = canvas_scale
    else:
        raw_canvas_scale = cfg.get("canvas_scale_percent", cfg.get("canvas_scale", 100))
    try:
        eff_canvas_scale = normalize_canvas_scale_percent(raw_canvas_scale)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2)

    try:
        resolved_display_settings = resolve_optimize_display_settings(
            input_values=expanded_inputs,
            canvas_scale_percent=eff_canvas_scale,
        )
        w, h = parse_resolution(resolved_display_settings.resolution)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2)

    eff_scaling = "fit"
    eff_align = parse_position_pair(resolve_option_value("align", align, cfg, ctx) or "center", axis="align")
    eff_valign = parse_position_pair(resolve_option_value("valign", valign, cfg, ctx) or "center", axis="valign")
    eff_quality = int(resolve_option_value("quality", quality, cfg, ctx))
    raw_background_color = resolve_option_value("background_color", background_color, cfg, ctx)
    if not is_background_color_literal(raw_background_color):
        typer.echo("--background-color must be a hex RGB value like 1E1E1E")
        raise typer.Exit(code=2)
    eff_background_color = normalize_background_color(raw_background_color)
    eff_margins = resolve_option_value("margins", margins, cfg, ctx)
    eff_embed_text = resolve_option_value("embed_text", embed_text, cfg, ctx)
    eff_embed_font = resolve_option_value("embed_font", embed_font, cfg, ctx)

    if not (1 <= eff_quality <= 100):
        typer.echo("--quality must be between 1 and 100")
        raise typer.Exit(code=2)

    if cfg:
        optimize_settings = AppSettings.from_settings_dict(cfg, default_plugin=_default_plugin_name()).optimize
        eff_l_display_scale = optimize_settings.l_display_scale
        eff_r_display_scale = optimize_settings.r_display_scale
        eff_l_auto_display_scale = optimize_settings.l_auto_display_scale
        eff_r_auto_display_scale = optimize_settings.r_auto_display_scale
    else:
        eff_l_display_scale = 1.0
        eff_r_display_scale = 1.0
        eff_l_auto_display_scale = False
        eff_r_auto_display_scale = False

    try:
        saved_files, placements = optimize_wallpapers(
            inputs=expanded_inputs,
            target_resolution=(w, h),
            output_dir=output,
            scaling=eff_scaling,
            quality=eff_quality,
            two_screen=resolved_display_settings.two_screen,
            margins=(0, 0, 0, 0) if eff_margins is None else parse_margins(str(eff_margins)),
            l_display=None if resolved_display_settings.l_display is None else parse_display(resolved_display_settings.l_display),
            r_display=None if resolved_display_settings.r_display is None else parse_display(resolved_display_settings.r_display),
            l_display_scale=eff_l_display_scale,
            r_display_scale=eff_r_display_scale,
            l_auto_display_scale=eff_l_auto_display_scale,
            r_auto_display_scale=eff_r_auto_display_scale,
            align=eff_align,
            valign=eff_valign,
            embed_info=embed_info,
            background_color=eff_background_color,
            embed_text=eff_embed_text,
            embed_position=embed_position,
            embed_max_lines=eff_embed_max_lines,
            embed_font=(str(eff_embed_font) if eff_embed_font is not None else None),
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2)
    typer.echo(f"Saved: {saved_files}")
    for p in placements:
        typer.echo(f"Placement: {format_placement_line(p)}")
    if saved_files:
        try:
            write_last_optimize_run(output_dir=output, composite_path=Path(saved_files[-1]))
        except OSError as exc:
            typer.echo(f"Warning: failed to record last optimize run: {exc}")


@app.command()
def apply(
    settings_file: Optional[Path] = typer.Option(
        None,
        "--settings-file",
        "-c",
        help="Optional path to harite-settings.json (apply_mode, plugin, windows_apply_span)",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory from the prior optimize run (optional tracking hint)",
    ),
    file: Optional[Path] = typer.Option(
        None,
        "--file",
        "-f",
        help="Optional composite image path (default: last optimize output)",
    ),
) -> None:
    """Apply the latest optimized wallpaper using settings apply_mode.

    Run ``harite optimize`` first. When ``--file`` is omitted, the CLI reads
    ``.harite-last-optimize.json`` written by the prior optimize command.
    """
    cfg: dict = {}
    if settings_file is not None:
        try:
            cfg = load_settings(settings_file)
        except Exception as exc:
            typer.echo(f"Failed to load settings: {exc}")
            raise typer.Exit(code=2)

    app_settings = AppSettings.from_settings_dict(cfg, default_plugin=_default_plugin_name())
    eff_plugin = _resolve_plugin_name(cfg)
    apply_mode = app_settings.apply.apply_mode
    windows_apply_span = app_settings.apply.windows_apply_span

    if file is not None:
        composite_path = Path(file)
    else:
        try:
            last_run = read_last_optimize_run(
                search_dirs=default_last_optimize_search_dirs(
                    output_hint=output,
                ),
            )
            composite_path = last_run.composite_path
        except ValueError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=2)

    try:
        plugin_impl = plugin_registry.get(eff_plugin)
    except KeyError:
        typer.echo(f"Unknown plugin: {eff_plugin}")
        typer.echo(f"Available plugins: {', '.join(plugin_registry.list())}")
        raise typer.Exit(code=2)

    try:
        effective_apply = resolve_apply_settings(
            file=composite_path,
            apply_mode=apply_mode,
            output_dir=composite_path.parent,
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2)

    if effective_apply.windows_span and windows_apply_span:
        from harite.windows_wallpaper import ensure_span_style

        ensure_span_style()

    path_or_map = effective_apply.target

    success = plugin_impl.apply(path_or_map)
    # Prepare a human-friendly path string for logging (handle per-monitor mapping)
    if isinstance(path_or_map, dict):
        try:
            path_str = json.dumps(path_or_map, ensure_ascii=False)
        except Exception:
            path_str = str(path_or_map)
    else:
        path_str = str(path_or_map)

    if success:
        typer.echo(f"Plugin '{eff_plugin}' applied wallpaper: {path_str}")
    else:
        typer.echo(f"Plugin '{eff_plugin}' failed to apply wallpaper: {path_str}")
        raise typer.Exit(code=3)


@app.command(help="Rotate wallpapers from directories using the existing apply path.")
def slideshow(
    ctx: typer.Context,
    input: Optional[List[str]] = typer.Option(
        None,
        "--input",
        help="Input directories. Use comma-separated paths or repeat --input.",
    ),
    interval_sec: Optional[int] = typer.Option(
        None,
        "--interval-sec",
        help="Cycle interval in seconds (>=1)",
    ),
    mode: str = typer.Option("sequential", "--mode", help="Selection mode: sequential|random"),
    settings_file: Optional[Path] = typer.Option(
        None,
        "--settings-file",
        "-c",
        help="Optional path to harite-settings.json",
    ),
) -> None:
    """Rotate wallpapers from directories (minimum execution control)."""
    cfg: dict = {}
    if settings_file is not None:
        try:
            cfg = load_settings(settings_file)
        except Exception as exc:
            typer.echo(f"Failed to load settings: {exc}")
            raise typer.Exit(code=2)

    slideshow_settings = SlideshowSettings.from_settings_dict(cfg) if cfg else SlideshowSettings()

    if _parameter_source_is_commandline(ctx, "input"):
        input_dirs = _expand_slideshow_cli_input_dirs(input)
    else:
        input_dirs = _slideshow_srcdir_paths_from_settings(cfg)

    if not input_dirs:
        typer.echo("--input is required (or provide slideshow_srcdir_l/r in --settings-file)")
        raise typer.Exit(code=2)

    if _parameter_source_is_commandline(ctx, "interval_sec"):
        eff_interval = interval_sec
    elif cfg:
        eff_interval = slideshow_settings.interval_seconds
    else:
        eff_interval = interval_sec

    if eff_interval is None:
        typer.echo("--interval-sec is required (or provide slideshow_interval_seconds in --settings-file)")
        raise typer.Exit(code=2)

    if eff_interval < 1:
        typer.echo("--interval-sec must be >= 1")
        raise typer.Exit(code=2)

    if _parameter_source_is_commandline(ctx, "mode"):
        eff_mode = mode
    elif cfg:
        eff_mode = slideshow_settings.mode
    else:
        eff_mode = mode

    eff_mode = eff_mode.lower().strip()
    if eff_mode not in ("sequential", "random"):
        typer.echo("--mode must be one of: sequential, random")
        raise typer.Exit(code=2)

    eff_plugin = _resolve_plugin_name(cfg)

    try:
        image_counts = []
        for directory in input_dirs:
            images = collect_slideshow_input_images([directory])
            image_counts.append(len(images))
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2)

    optimize_config = build_slideshow_optimize_config(cfg, default_plugin=eff_plugin)
    if len(input_dirs) > 1:
        try:
            validate_dual_source_slideshow(eff_plugin)
        except ValueError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=2)
        optimize_config.dual_auto_split = True

    input_summary = ",".join(str(path) for path in input_dirs)
    images_total = sum(image_counts)
    source_layout = "dual" if len(input_dirs) > 1 else "single"

    typer.echo(
        f"Slideshow start: input={input_summary} images={images_total} sources={source_layout} "
        f"interval_sec={eff_interval} mode={eff_mode} plugin={eff_plugin} "
        f"optimize=yes work_dir={optimize_config.work_dir}"
    )

    try:
        plugin_impl = plugin_registry.get(eff_plugin)
    except KeyError:
        typer.echo(f"Unknown plugin: {eff_plugin}")
        typer.echo(f"Available plugins: {', '.join(plugin_registry.list())}")
        raise typer.Exit(code=2)

    from harite.gui.controllers.optimize_controller import OptimizeController as _OptimizeController

    controller = _OptimizeController()

    stats = {
        "apply_ok": 0,
        "apply_failed": 0,
        "apply_error": 0,
    }

    def _on_cycle(target: object | None, cycle_index: int, success: bool, error_message: str | None) -> None:
        if success:
            stats["apply_ok"] += 1
            return

        if error_message and "apply error" in error_message:
            stats["apply_error"] += 1
            typer.echo(
                f"Slideshow cycle={cycle_index + 1} target={target} "
                f"apply=error reason=optimize-or-apply-exception message={error_message}"
            )
            return

        stats["apply_failed"] += 1
        typer.echo(
            f"Slideshow cycle={cycle_index + 1} target={target} "
            f"apply=failed reason={error_message or 'plugin-returned-false'}"
        )

    try:
        completed = run_slideshow_optimize_cycles(
            input_dirs=input_dirs,
            mode=eff_mode,
            interval_sec=eff_interval,
            config=optimize_config,
            controller=controller,
            plugin_impl=plugin_impl,
            on_cycle=_on_cycle,
        )
    except KeyboardInterrupt:
        typer.echo("Slideshow interrupted by user")
        raise typer.Exit(code=0)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2)

    apply_failed_total = stats["apply_failed"] + stats["apply_error"]
    typer.echo(
        f"Slideshow completed cycles={completed} apply_ok={stats['apply_ok']} "
        f"apply_failed={stats['apply_failed']} apply_error={stats['apply_error']} "
        f"apply_failed_total={apply_failed_total}"
    )


@app.command("install-desktop-entry", help="Install a user-local XDG desktop launcher for Harite GUI.")
def install_desktop_entry_command(
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        help="Optional output path for the .desktop file",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite an existing desktop entry",
    ),
) -> None:
    if not sys.platform.startswith("linux"):
        typer.echo("install-desktop-entry is only supported on Linux/XDG")
        raise typer.Exit(code=2)

    try:
        path = install_linux_desktop_entry(target_path=output, overwrite=force)
    except FileExistsError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2)

    typer.echo(f"Installed desktop entry: {path}")


def run() -> None:
    app()


if __name__ == "__main__":
    run()

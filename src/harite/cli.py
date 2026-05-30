"""CLI entrypoints for Harite."""
from __future__ import annotations

import sys
import typer
from pathlib import Path
from typing import Optional, List, Tuple
import json

from . import __version__
from .apply_settings import resolve_apply_settings
from .core import DEFAULT_BACKGROUND_COLOR_HEX, is_background_color_literal, normalize_background_color, normalize_optimize_input_paths, optimize_wallpapers
from .plugins import registry as plugin_registry
from .settings_file import load_settings
from .linux_xdg_launcher import install_desktop_entry as install_linux_desktop_entry
from .optimize_settings import is_auto_value, resolve_optimize_display_settings
from .positioning import parse_position_pair
from .slideshow import collect_slideshow_input_images, run_slideshow_cycles

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


def parse_resolution(value: str) -> Tuple[int, int]:
    """Parse resolution strings like '1920x1080'."""
    try:
        w_str, h_str = value.lower().split("x")
        w, h = int(w_str), int(h_str)
        if w <= 0 or h <= 0:
            raise ValueError("resolution must be positive")
        return w, h
    except Exception:
        raise ValueError("Invalid resolution format. Use WIDTHxHEIGHT, e.g. 3840x2160")


def parse_margins(value: str) -> Tuple[int, int, int, int]:
    """Parse margins as 'left,top,right,bottom' or 'l,r,t,b' in pixels."""
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


def resolve_bool_or_auto_option(
    name: str,
    cli_value: bool,
    cfg: dict,
    ctx: typer.Context,
) -> bool | None:
    if _parameter_source_is_commandline(ctx, name):
        return bool(cli_value)
    if name in cfg:
        raw = cfg[name]
        if is_auto_value(raw):
            return None
        return parse_config_bool(name, raw)
    return bool(cli_value)


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
    resolution: Optional[str] = typer.Option(
        None,
        "--resolution",
        "-r",
        help="Target resolution WxH (e.g. 3840x2160)",
        rich_help_panel="必須に近い入力",
    ),
    output: Path = typer.Option(
        Path("."),
        "--output",
        "-o",
        help="Output directory",
        rich_help_panel="基本オプション",
    ),
    two_screen: bool = typer.Option(
        False,
        "--two-screen/--no-two-screen",
        help="Enable two-screen mode. For explicit left/right widths, use with --l-display and --r-display.",
        rich_help_panel="条件付きオプション（通常は省略可）",
    ),
    margins: Optional[str] = typer.Option(
        None,
        "--margins",
        help="Margins as l,r,top,bottom in pixels (e.g. 10,0,10,0)",
        rich_help_panel="条件付きオプション（通常は省略可）",
    ),
    l_display: Optional[str] = typer.Option(
        None,
        "--l-display",
        help="Left display size WxH (e.g. 1920x1080). Effective with --two-screen.",
        rich_help_panel="条件付きオプション（通常は省略可）",
    ),
    r_display: Optional[str] = typer.Option(
        None,
        "--r-display",
        help="Right display size WxH (e.g. 1280x1024). Effective with --two-screen.",
        rich_help_panel="条件付きオプション（通常は省略可）",
    ),
    align: str = typer.Option(
        "center",
        "--align",
        help="Horizontal align for left,right images (e.g. left,right). A single value applies to both.",
        rich_help_panel="条件付きオプション（通常は省略可）",
    ),
    valign: str = typer.Option(
        "center",
        "--valign",
        help="Vertical align for left,right images (e.g. top,bottom). A single value applies to both.",
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

    `--input` は複数指定可。カンマ区切りまたは `--input` の繰り返しで複数パスを指定できます。
    `optimize` では画像ファイルのみを受け付け、ディレクトリは受け付けません。

    `--two-screen` は左右2画面向けモードです。
    `--l-display` / `--r-display` を併用した場合は、先頭2入力を左・右へ割り当てます。

    パラメータの強弱（現状）:
    - `margins` はまず有効領域を決め、その内側で `align` / `valign` が効きます。
    - `two-screen` は `--l-display` / `--r-display` 併用時に効きが強くなります。

    余白情報埋め込み:
    - `--embed-info` は `none|params|free|combo` を指定できます。
    - `free` / `combo` では `--embed-text` を併用できます。
    - `--embed-font` は任意指定です。既定では自動的に利用可能なフォントを探索します。
    """
    # Load settings if provided and merge defaults (CLI options override settings)
    cfg: dict = {}
    if settings_file is not None:
        try:
            cfg = load_settings(settings_file)
        except Exception as exc:
            typer.echo(f"Failed to load settings: {exc}")
            raise typer.Exit(code=2)

    # resolve effective values: CLI > settings > required check
    eff_resolution = resolve_option_value("resolution", resolution, cfg, ctx)

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

    try:
        eff_two_screen = resolve_bool_or_auto_option("two_screen", two_screen, cfg, ctx)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2)

    try:
        resolved_display_settings = resolve_optimize_display_settings(
            input_values=expanded_inputs,
            resolution=None if is_auto_value(eff_resolution) else str(eff_resolution or "").strip() or None,
            two_screen=eff_two_screen,
            l_display=None if is_auto_value(resolve_option_value("l_display", l_display, cfg, ctx)) else resolve_option_value("l_display", l_display, cfg, ctx),
            r_display=None if is_auto_value(resolve_option_value("r_display", r_display, cfg, ctx)) else resolve_option_value("r_display", r_display, cfg, ctx),
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
        align=eff_align,
        valign=eff_valign,
        embed_info=embed_info,
        background_color=eff_background_color,
        embed_text=eff_embed_text,
        embed_position=embed_position,
        embed_max_lines=eff_embed_max_lines,
        embed_font=(str(eff_embed_font) if eff_embed_font is not None else None),
    )
    typer.echo(f"Saved: {saved_files}")
    for p in placements:
        typer.echo(f"Placement: {p}")


@app.command()
def apply(
    plugin: str = typer.Option(_default_plugin_name(), "--plugin", "-p", help="Plugin name to apply wallpaper with"),
    file: Path = typer.Option(..., "--file", "-f", help="Path to wallpaper image file"),
    per_monitor: bool = typer.Option(False, "--per-monitor", "-m", help="Apply per-monitor files (requires --left-file/--right-file or --auto-split)"),
    left_file: Optional[Path] = typer.Option(None, "--left-file", help="File to apply to left monitor"),
    right_file: Optional[Path] = typer.Option(None, "--right-file", help="File to apply to right monitor"),
    auto_split: bool = typer.Option(False, "--auto-split", help="Auto-split the composite file per detected displays"),
) -> None:
    """Apply a wallpaper using a registered plugin.
    """
    try:
        plugin_impl = plugin_registry.get(plugin)
    except KeyError:
        typer.echo(f"Unknown plugin: {plugin}")
        typer.echo(f"Available plugins: {', '.join(plugin_registry.list())}")
        raise typer.Exit(code=2)

    apply_mode = "single-file"
    if auto_split:
        apply_mode = "per-monitor-auto-split"
    elif left_file or right_file:
        apply_mode = "per-monitor-explicit"
    elif per_monitor:
        typer.echo("--per-monitor requires --left-file/--right-file or --auto-split")
        raise typer.Exit(code=2)

    try:
        effective_apply = resolve_apply_settings(
            file=file,
            apply_mode=apply_mode,
            left_file=left_file,
            right_file=right_file,
            output_dir=Path("."),
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2)

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
        typer.echo(f"Plugin '{plugin}' applied wallpaper: {path_str}")
    else:
        typer.echo(f"Plugin '{plugin}' failed to apply wallpaper: {path_str}")
        raise typer.Exit(code=3)


@app.command(help="Rotate wallpapers from directories using the existing apply path.")
def slideshow(
    input: List[str] = typer.Option(..., "--input", help="Input directories. Use comma-separated paths or repeat --input."),
    interval_sec: int = typer.Option(..., "--interval-sec", help="Cycle interval in seconds (>=1)"),
    mode: str = typer.Option("sequential", "--mode", help="Selection mode: sequential|random"),
    plugin: str = typer.Option(_default_plugin_name(), "--plugin", "-p", help="Plugin name used to apply each selected image"),
) -> None:
    """Rotate wallpapers from directories (minimum execution control)."""
    if interval_sec < 1:
        typer.echo("--interval-sec must be >= 1")
        raise typer.Exit(code=2)

    mode = mode.lower().strip()
    if mode not in ("sequential", "random"):
        typer.echo("--mode must be one of: sequential, random")
        raise typer.Exit(code=2)

    input_dirs: List[Path] = []
    for it in input:
        parts = [p.strip() for p in it.split(",") if p.strip()]
        input_dirs.extend(Path(part).expanduser() for part in parts)
    input_dirs = input_dirs[:2]

    try:
        images = collect_slideshow_input_images(input_dirs)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2)

    input_summary = ",".join(str(path) for path in input_dirs)

    typer.echo(
        f"Slideshow start: input={input_summary} images={len(images)} interval_sec={interval_sec} "
        f"mode={mode} plugin={plugin}"
    )

    try:
        plugin_impl = plugin_registry.get(plugin)
    except KeyError:
        typer.echo(f"Unknown plugin: {plugin}")
        typer.echo(f"Available plugins: {', '.join(plugin_registry.list())}")
        raise typer.Exit(code=2)

    stats = {
        "apply_ok": 0,
        "apply_failed": 0,
        "apply_error": 0,
    }

    def _on_cycle(selected: Path, cycle_index: int) -> None:
        try:
            success = bool(plugin_impl.apply(str(selected)))
        except Exception as exc:
            stats["apply_error"] += 1
            typer.echo(
                f"Slideshow cycle={cycle_index + 1} selected={selected} "
                f"apply=error reason=plugin-exception error_type={type(exc).__name__} message={exc}"
            )
            return

        if success:
            stats["apply_ok"] += 1
        else:
            stats["apply_failed"] += 1
            typer.echo(
                f"Slideshow cycle={cycle_index + 1} selected={selected} "
                "apply=failed reason=plugin-returned-false"
            )

    try:
        completed = run_slideshow_cycles(
            images=images,
            mode=mode,
            interval_sec=interval_sec,
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

"""CLI entrypoints for Harite (skeleton)."""
from __future__ import annotations

import sys
import typer
from pathlib import Path
from typing import Optional, List, Tuple
import json
from click.core import ParameterSource

from . import __version__
from .apply_settings import resolve_apply_settings
from .core import optimize_wallpapers
from .plugins import registry as plugin_registry
from .config import load_config
from .optimize_settings import is_auto_value, resolve_optimize_display_settings
from .positioning import parse_position_pair
from .watch import collect_watch_input_images, run_watch_cycles

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
        raise ValueError(f"invalid config bool for {name}: {value}")
    if isinstance(value, str):
        raw = value.strip().lower()
        truthy = {"1", "true", "yes", "on"}
        falsy = {"0", "false", "no", "off"}
        if raw in truthy:
            return True
        if raw in falsy:
            return False
        raise ValueError(f"invalid config bool for {name}: {value}")
    raise ValueError(f"invalid config bool for {name}: {value}")


def resolve_bool_option(
    name: str,
    cli_value: bool,
    cfg: dict,
    ctx: typer.Context,
) -> bool:
    """Resolve a bool option with priority CLI > config > default."""
    if ctx.get_parameter_source(name) == ParameterSource.COMMANDLINE:
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
    if ctx.get_parameter_source(name) == ParameterSource.COMMANDLINE:
        return cli_value
    return cfg.get(name, cli_value)


def resolve_bool_or_auto_option(
    name: str,
    cli_value: bool,
    cfg: dict,
    ctx: typer.Context,
) -> bool | None:
    if ctx.get_parameter_source(name) == ParameterSource.COMMANDLINE:
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
        help="Input file(s) or directory(ies). Use comma-separated paths or repeat --input.",
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
    format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Output format: text|json",
        rich_help_panel="基本オプション",
    ),
    layout: str = typer.Option(
        "mosaic",
        "--layout",
        help="Layout mode (current implementation is effectively mosaic; other values are treated equivalently)",
        rich_help_panel="基本オプション",
    ),
    scaling: str = typer.Option(
        "fit",
        "--scaling",
        help="Scaling mode (fit|fill|crop). Current optimize implementation has limited behavior differences.",
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
    fixed: bool = typer.Option(
        False,
        "--fixed/--no-fixed",
        help="Fix allocation by input order (left then right). Current optimize implementation impact is limited.",
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
    padding: int = typer.Option(
        0,
        "--padding",
        help="Padding (px) between images",
        rich_help_panel="詳細調整",
    ),
    quality: int = typer.Option(
        90,
        "--quality",
        help="JPEG quality",
        rich_help_panel="詳細調整",
    ),
    random_seed: Optional[int] = typer.Option(
        None,
        "--random-seed",
        help="Random seed for reproducibility (currently limited impact in optimize placement)",
        rich_help_panel="詳細調整",
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to JSON config file to load defaults from",
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
        "auto",
        "--embed-position",
        help="Margin side for info text: auto|top|bottom|left|right",
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
    ディレクトリを指定すると、その直下の画像（jpg/jpeg/png/bmp）が対象になります。

    `--two-screen` は左右2画面向けモードです。
    `--l-display` / `--r-display` を併用した場合は、先頭2入力を左・右へ割り当てます。

    パラメータの強弱（現状）:
    - `margins` はまず有効領域を決め、その内側で `align` / `valign` が効きます。
    - `two-screen` は `--l-display` / `--r-display` 併用時に効きが強くなります。
    - `layout` / `scaling` / `fixed` / `random-seed` は現状の optimize 実装では効きが限定的です。

    余白情報埋め込み:
    - `--embed-info` は `none|params|free|combo` を指定できます。
    - `free` / `combo` では `--embed-text` を併用できます。
    - `--embed-font` は任意指定です。既定では自動的に利用可能なフォントを探索します。
    """
    # Load config if provided and merge defaults (CLI options override config)
    cfg: dict = {}
    if config is not None:
        try:
            cfg = load_config(config)
        except Exception as exc:
            typer.echo(f"Failed to load config: {exc}")
            raise typer.Exit(code=2)

    # resolve effective values: CLI > config > required check
    eff_resolution = resolve_option_value("resolution", resolution, cfg, ctx)

    # validate numeric options
    if padding < 0:
        typer.echo("--padding must be non-negative")
        raise typer.Exit(code=2)
    if not (1 <= quality <= 100):
        typer.echo("--quality must be between 1 and 100")
        raise typer.Exit(code=2)
    embed_info = str(resolve_option_value("embed_info", embed_info, cfg, ctx) or "none").lower()
    if embed_info not in ("none", "params", "free", "combo"):
        typer.echo("--embed-info must be one of: none, params, free, combo")
        raise typer.Exit(code=2)
    embed_position = str(resolve_option_value("embed_position", embed_position, cfg, ctx) or "auto").lower()
    if embed_position not in ("auto", "top", "bottom", "left", "right"):
        typer.echo("--embed-position must be one of: auto, top, bottom, left, right")
        raise typer.Exit(code=2)
    eff_embed_max_lines = int(resolve_option_value("embed_max_lines", embed_max_lines, cfg, ctx))
    if eff_embed_max_lines <= 0:
        typer.echo("--embed-max-lines must be positive")
        raise typer.Exit(code=2)

    # determine inputs (CLI > config)
    eff_input = input if input is not None else cfg.get("input")
    if not eff_input:
        typer.echo("--input is required (or provide in --config)")
        raise typer.Exit(code=2)
    expanded_inputs: List[str] = []
    for it in eff_input:
        parts = [p.strip() for p in it.split(",") if p.strip()]
        expanded_inputs.extend(parts)

    try:
        eff_two_screen = resolve_bool_or_auto_option("two_screen", two_screen, cfg, ctx)
        eff_fixed = resolve_bool_option("fixed", fixed, cfg, ctx)
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

    eff_layout = str(resolve_option_value("layout", layout, cfg, ctx) or "mosaic")
    eff_scaling = str(resolve_option_value("scaling", scaling, cfg, ctx) or "fit")
    eff_align = parse_position_pair(resolve_option_value("align", align, cfg, ctx) or "center", axis="align")
    eff_valign = parse_position_pair(resolve_option_value("valign", valign, cfg, ctx) or "center", axis="valign")
    eff_padding = int(resolve_option_value("padding", padding, cfg, ctx))
    eff_quality = int(resolve_option_value("quality", quality, cfg, ctx))
    eff_random_seed = resolve_option_value("random_seed", random_seed, cfg, ctx)
    eff_margins = resolve_option_value("margins", margins, cfg, ctx)
    eff_embed_text = resolve_option_value("embed_text", embed_text, cfg, ctx)
    eff_embed_font = resolve_option_value("embed_font", embed_font, cfg, ctx)

    if eff_padding < 0:
        typer.echo("--padding must be non-negative")
        raise typer.Exit(code=2)
    if not (1 <= eff_quality <= 100):
        typer.echo("--quality must be between 1 and 100")
        raise typer.Exit(code=2)

    saved_files, placements = optimize_wallpapers(
        inputs=expanded_inputs,
        target_resolution=(w, h),
        output_dir=output,
        layout=eff_layout,
        scaling=eff_scaling,
        padding=eff_padding,
        quality=eff_quality,
        random_seed=eff_random_seed,
        two_screen=resolved_display_settings.two_screen,
        margins=(0, 0, 0, 0) if eff_margins is None else parse_margins(str(eff_margins)),
        l_display=None if resolved_display_settings.l_display is None else parse_display(resolved_display_settings.l_display),
        r_display=None if resolved_display_settings.r_display is None else parse_display(resolved_display_settings.r_display),
        fixed=eff_fixed,
        align=eff_align,
        valign=eff_valign,
        embed_info=embed_info,
        embed_text=eff_embed_text,
        embed_position=embed_position,
        embed_max_lines=eff_embed_max_lines,
        embed_font=(str(eff_embed_font) if eff_embed_font is not None else None),
    )
    fmt = format.lower()
    if fmt not in ("json", "text"):
        typer.echo("Invalid --format. Use 'text' or 'json'.")
        raise typer.Exit(code=2)

    if fmt == "json":
        out = {
            "optimized_files": [str(p) for p in saved_files],
            "layout_metadata": [p.to_dict() for p in placements],
        }
        typer.echo(json.dumps(out, ensure_ascii=False))
    else:
        typer.echo(f"Saved: {saved_files}")
        for p in placements:
            typer.echo(f"Placement: {p}")


@app.command("compute-placement")
def compute_placement(
    input: str = typer.Option(..., "--input", "-i", help="Input image file"),
    resolution: str = typer.Option(..., "--resolution", "-r", help="Target resolution WxH"),
    layout: str = typer.Option("cover", "--layout", help="Layout mode"),
) -> None:
    """Compute placement for a single image (placeholder)."""
    typer.echo(f"COMPUTE: input={input} resolution={resolution} layout={layout}")


@app.command()
def apply(
    plugin: str = typer.Option(_default_plugin_name(), "--plugin", "-p", help="Plugin name to apply wallpaper with"),
    file: Path = typer.Option(..., "--file", "-f", help="Path to wallpaper image file"),
    do_it: bool = typer.Option(False, "--do-it", help="Actually change the system wallpaper (dry-run by default)"),
    per_monitor: bool = typer.Option(False, "--per-monitor", "-m", help="Apply per-monitor files (requires --left-file/--right-file or --auto-split)"),
    left_file: Optional[Path] = typer.Option(None, "--left-file", help="File to apply to left monitor"),
    right_file: Optional[Path] = typer.Option(None, "--right-file", help="File to apply to right monitor"),
    auto_split: bool = typer.Option(False, "--auto-split", help="Auto-split the composite file per detected displays"),
) -> None:
    """Apply a wallpaper using a registered plugin.

    By default this performs a dry-run; pass `--do-it` to actually attempt
    changing the system wallpaper.
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
            plugin_name=plugin,
            apply_mode=apply_mode,
            left_file=left_file,
            right_file=right_file,
            output_dir=Path("."),
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2)

    path_or_map = effective_apply.target

    success = plugin_impl.apply(path_or_map, dry_run=not do_it)
    # Prepare a human-friendly path string for logging (handle per-monitor mapping)
    if isinstance(path_or_map, dict):
        try:
            path_str = json.dumps(path_or_map, ensure_ascii=False)
        except Exception:
            path_str = str(path_or_map)
    else:
        path_str = str(path_or_map)

    if success:
        typer.echo(f"Plugin '{plugin}' applied wallpaper: {path_str} (dry_run={not do_it})")
    else:
        typer.echo(f"Plugin '{plugin}' failed to apply wallpaper: {path_str}")
        raise typer.Exit(code=3)


@app.command(help="Watch a directory and rotate wallpapers with the existing apply path.")
def watch(
    input: Path = typer.Option(..., "--input", help="Input directory containing images"),
    interval_sec: int = typer.Option(..., "--interval-sec", help="Cycle interval in seconds (>=1)"),
    mode: str = typer.Option("sequential", "--mode", help="Selection mode: sequential|random"),
    log_level: str = typer.Option("normal", "--log-level", help="Log level: normal|detail"),
    plugin: str = typer.Option(_default_plugin_name(), "--plugin", "-p", help="Plugin name used when --do-it is enabled"),
    dry_run: bool = typer.Option(True, "--dry-run/--do-it", help="Dry-run by default; pass --do-it to apply"),
    iterations: Optional[int] = typer.Option(None, "--iterations", help="Maximum cycles; omit for unbounded"),
) -> None:
    """Watch a directory and rotate wallpapers (minimum execution control)."""
    if interval_sec < 1:
        typer.echo("--interval-sec must be >= 1")
        raise typer.Exit(code=2)

    mode = mode.lower().strip()
    if mode not in ("sequential", "random"):
        typer.echo("--mode must be one of: sequential, random")
        raise typer.Exit(code=2)

    log_level = log_level.lower().strip()
    if log_level not in ("normal", "detail"):
        typer.echo("--log-level must be one of: normal, detail")
        raise typer.Exit(code=2)

    if iterations is not None and iterations < 1:
        typer.echo("--iterations must be >= 1")
        raise typer.Exit(code=2)

    try:
        images = collect_watch_input_images(input)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2)

    typer.echo(
        f"WATCH start: input={input} images={len(images)} interval_sec={interval_sec} "
        f"mode={mode} log_level={log_level} "
        f"plugin={plugin} dry_run={dry_run} iterations={iterations}"
    )

    plugin_impl = None
    if not dry_run:
        try:
            plugin_impl = plugin_registry.get(plugin)
        except KeyError:
            typer.echo(f"Unknown plugin: {plugin}")
            typer.echo(f"Available plugins: {', '.join(plugin_registry.list())}")
            raise typer.Exit(code=2)

    stats = {
        "dry_run_cycles": 0,
        "apply_ok": 0,
        "apply_failed": 0,
        "apply_error": 0,
    }

    def _on_cycle(selected: Path, cycle_index: int) -> None:
        if dry_run:
            stats["dry_run_cycles"] += 1
            if log_level == "detail":
                typer.echo(
                    f"WATCH cycle={cycle_index + 1} selected={selected} dry_run=True"
                )
            return

        try:
            success = bool(plugin_impl.apply(str(selected), dry_run=False))
        except Exception as exc:
            stats["apply_error"] += 1
            typer.echo(
                f"WATCH cycle={cycle_index + 1} selected={selected} "
                f"apply=error reason=plugin-exception error_type={type(exc).__name__} message={exc}"
            )
            return

        if success:
            stats["apply_ok"] += 1
            if log_level == "detail":
                typer.echo(
                    f"WATCH cycle={cycle_index + 1} selected={selected} apply=ok dry_run=False"
                )
        else:
            stats["apply_failed"] += 1
            typer.echo(
                f"WATCH cycle={cycle_index + 1} selected={selected} "
                "apply=failed reason=plugin-returned-false dry_run=False"
            )

    try:
        completed = run_watch_cycles(
            images=images,
            mode=mode,
            interval_sec=interval_sec,
            iterations=iterations,
            on_cycle=_on_cycle,
        )
    except KeyboardInterrupt:
        typer.echo("WATCH interrupted by user")
        raise typer.Exit(code=0)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2)

    if dry_run:
        typer.echo(
            f"WATCH completed cycles={completed} dry_run_cycles={stats['dry_run_cycles']}"
        )
    else:
        apply_failed_total = stats["apply_failed"] + stats["apply_error"]
        typer.echo(
            f"WATCH completed cycles={completed} apply_ok={stats['apply_ok']} "
            f"apply_failed={stats['apply_failed']} apply_error={stats['apply_error']} "
            f"apply_failed_total={apply_failed_total}"
        )


def run() -> None:
    app()


if __name__ == "__main__":
    run()

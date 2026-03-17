"""CLI entrypoints for Harite (skeleton)."""
from __future__ import annotations

import typer
from pathlib import Path
from typing import Optional, List, Tuple
import json

from . import __version__
from .core import optimize_wallpapers
from .plugins import registry as plugin_registry
from .workspace import detect_displays
from .core import split_composite_for_displays
from .config import load_config

app = typer.Typer(help="Harite - wallpaper optimizer")


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
    input: Optional[List[str]] = typer.Option(None, "--input", "-i", help="Input file(s) or directory(ies)"),
    resolution: Optional[str] = typer.Option(None, "--resolution", "-r", help="Target resolution WxH (e.g. 3840x2160)"),
    layout: str = typer.Option("mosaic", "--layout", help="Layout mode"),
    scaling: str = typer.Option("fit", "--scaling", help="Scaling mode (fit|fill|crop)"),
    padding: int = typer.Option(0, "--padding", help="Padding (px) between images"),
    two_screen: bool = typer.Option(False, "--two-screen", help="Enable two-screen (left/right) composition"),
    margins: Optional[str] = typer.Option(None, "--margins", help="Margins as l,r,top,bottom in pixels (e.g. 10,0,10,0)"),
    l_display: Optional[str] = typer.Option(None, "--l-display", help="Left display size WxH (e.g. 1920x1080)"),
    r_display: Optional[str] = typer.Option(None, "--r-display", help="Right display size WxH (e.g. 1280x1024)"),
    fixed: bool = typer.Option(False, "--fixed", help="Fix allocation by input order (left then right)"),
    output: Path = typer.Option(Path("."), "--output", "-o", help="Output directory"),
    quality: int = typer.Option(90, "--quality", help="JPEG quality"),
    random_seed: Optional[int] = typer.Option(None, "--random-seed", help="Random seed for reproducibility"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text|json"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to JSON config file to load defaults from"),
) -> None:
    """Optimize wallpapers.

    `--input` は複数指定可。ディレクトリを指定するとその中の画像が対象になります。
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
    eff_resolution = resolution or cfg.get("resolution")
    if not eff_resolution:
        typer.echo("--resolution is required (or provide in --config)")
        raise typer.Exit(code=2)
    try:
        w, h = parse_resolution(eff_resolution)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2)

    # validate numeric options
    if padding < 0:
        typer.echo("--padding must be non-negative")
        raise typer.Exit(code=2)
    if not (1 <= quality <= 100):
        typer.echo("--quality must be between 1 and 100")
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

    saved_files, placements = optimize_wallpapers(
        inputs=expanded_inputs,
        target_resolution=(w, h),
        output_dir=output,
        layout=layout,
        scaling=scaling,
        padding=padding,
        quality=quality,
        random_seed=random_seed,
        two_screen=two_screen,
        margins=(0, 0, 0, 0) if (margins is None and cfg.get("margins") is None) else parse_margins(margins or cfg.get("margins")),
        l_display=None if (l_display is None and cfg.get("l_display") is None) else parse_display(l_display or cfg.get("l_display")),
        r_display=None if (r_display is None and cfg.get("r_display") is None) else parse_display(r_display or cfg.get("r_display")),
        fixed=fixed,
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
    plugin: str = typer.Option("windows", "--plugin", "-p", help="Plugin name to apply wallpaper with"),
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

    # Determine what to pass to plugin.apply: either a string path or a dict
    path_or_map = None
    if auto_split:
        displays = detect_displays()
        if not displays:
            typer.echo("No displays detected for --auto-split")
            raise typer.Exit(code=2)
        per_map = split_composite_for_displays(file, displays, output_dir=Path("."))
        path_or_map = per_map
    elif left_file or right_file:
        displays = detect_displays()
        if len(displays) < 2:
            typer.echo("Need at least two displays to use --left-file/--right-file")
            raise typer.Exit(code=2)
        mapping = {}
        if left_file:
            mapping[displays[0].name] = str(left_file)
        if right_file:
            mapping[displays[1].name] = str(right_file)
        path_or_map = mapping
    elif per_monitor:
        typer.echo("--per-monitor requires --left-file/--right-file or --auto-split")
        raise typer.Exit(code=2)
    else:
        path_or_map = str(file)

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


def run() -> None:
    app()


if __name__ == "__main__":
    run()

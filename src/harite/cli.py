"""CLI entrypoints for Harite (skeleton)."""
from __future__ import annotations

import typer
from pathlib import Path
from typing import Optional

from . import __version__
from .core import optimize_wallpapers

from . import __version__

app = typer.Typer(help="Harite - wallpaper optimizer")


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
    input: str = typer.Option(..., "--input", "-i", help="Input file or directory"),
    resolution: str = typer.Option(..., "--resolution", "-r", help="Target resolution WxH"),
    layout: str = typer.Option("mosaic", "--layout", help="Layout mode"),
    output: Path = typer.Option(Path("."), "--output", "-o", help="Output directory"),
    quality: int = typer.Option(90, "--quality", help="JPEG quality"),
) -> None:
    """Optimize wallpapers (placeholder implementation)."""
    # parse resolution like 3840x2160
    try:
        w_str, h_str = resolution.lower().split("x")
        w, h = int(w_str), int(h_str)
    except Exception:
        typer.echo("Invalid resolution format. Use WIDTHxHEIGHT, e.g. 3840x2160")
        raise typer.Exit(code=2)

    inputs = [input]
    saved_files, placements = optimize_wallpapers(
        inputs=inputs,
        target_resolution=(w, h),
        output_dir=output,
        layout=layout,
        scaling="fit",
        padding=0,
        quality=quality,
        random_seed=None,
    )
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


def run() -> None:
    app()


if __name__ == "__main__":
    run()

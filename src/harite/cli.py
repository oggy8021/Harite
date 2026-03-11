"""CLI entrypoints for Harite (skeleton)."""
from __future__ import annotations

import typer
from pathlib import Path
from typing import Optional, List
import json

from . import __version__
from .core import optimize_wallpapers

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
    input: List[str] = typer.Option(..., "--input", "-i", help="Input file(s) or directory(ies)"),
    resolution: str = typer.Option(..., "--resolution", "-r", help="Target resolution WxH"),
    layout: str = typer.Option("mosaic", "--layout", help="Layout mode"),
    scaling: str = typer.Option("fit", "--scaling", help="Scaling mode (fit|fill|crop)"),
    padding: int = typer.Option(0, "--padding", help="Padding (px) between images"),
    output: Path = typer.Option(Path("."), "--output", "-o", help="Output directory"),
    quality: int = typer.Option(90, "--quality", help="JPEG quality"),
    random_seed: Optional[int] = typer.Option(None, "--random-seed", help="Random seed for reproducibility"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text|json"),
) -> None:
    """Optimize wallpapers.

    `--input` は複数指定可。ディレクトリを指定するとその中の画像が対象になります。
    """
    # parse resolution like 3840x2160
    try:
        w_str, h_str = resolution.lower().split("x")
        w, h = int(w_str), int(h_str)
    except Exception:
        typer.echo("Invalid resolution format. Use WIDTHxHEIGHT, e.g. 3840x2160")
        raise typer.Exit(code=2)

    # flatten inputs (allow comma-separated items too)
    expanded_inputs: List[str] = []
    for it in input:
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
    )
    if format.lower() == "json":
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


def run() -> None:
    app()


if __name__ == "__main__":
    run()

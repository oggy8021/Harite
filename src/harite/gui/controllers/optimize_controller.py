"""Controller for GUI optimize actions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from harite.cli import parse_resolution
from harite.core import optimize_wallpapers


@dataclass
class OptimizeFormState:
    input_value: str
    resolution: str
    output_dir: str
    layout: str = "mosaic"
    scaling: str = "fit"
    two_screen: bool = False
    margins: Optional[str] = None
    l_display: Optional[str] = None
    r_display: Optional[str] = None
    fixed: bool = False
    align: str = "center"
    valign: str = "center"
    padding: int = 0
    quality: int = 90
    embed_info: str = "none"
    embed_text: Optional[str] = None
    embed_position: str = "auto"
    embed_max_lines: int = 3


class OptimizeController:
    """Thin adapter from GUI form values to core.optimize_wallpapers."""

    def _parse_margins(self, margins: Optional[str]) -> tuple[int, int, int, int]:
        if not margins:
            return (0, 0, 0, 0)

        parts = [x.strip() for x in margins.split(",")]
        if len(parts) != 4:
            raise ValueError("margins must have 4 comma-separated integers")

        try:
            vals = tuple(int(x) for x in parts)
        except ValueError as exc:
            raise ValueError("margins must have 4 comma-separated integers") from exc

        if any(v < 0 for v in vals):
            raise ValueError("margins must be non-negative")

        return vals

    def validate(self, state: OptimizeFormState) -> None:
        if not state.input_value.strip():
            raise ValueError("input is required")
        parse_resolution(state.resolution)
        if state.padding < 0:
            raise ValueError("padding must be non-negative")
        if state.quality < 1 or state.quality > 100:
            raise ValueError("quality must be between 1 and 100")
        if state.embed_info not in ("none", "params", "free", "combo"):
            raise ValueError("embed_info must be one of: none, params, free, combo")
        self._parse_margins(state.margins)
        if state.l_display:
            parse_resolution(state.l_display)
        if state.r_display:
            parse_resolution(state.r_display)

    def run_optimize(self, state: OptimizeFormState) -> tuple[list[Path], list]:
        self.validate(state)
        w, h = parse_resolution(state.resolution)
        inputs = [p.strip() for p in state.input_value.split(",") if p.strip()]
        output = Path(state.output_dir)
        margins = self._parse_margins(state.margins)

        return optimize_wallpapers(
            inputs=inputs,
            target_resolution=(w, h),
            output_dir=output,
            layout=state.layout,
            scaling=state.scaling,
            padding=state.padding,
            quality=state.quality,
            two_screen=state.two_screen,
            margins=margins,
            l_display=None if not state.l_display else parse_resolution(state.l_display),
            r_display=None if not state.r_display else parse_resolution(state.r_display),
            fixed=state.fixed,
            align=state.align,
            valign=state.valign,
            embed_info=state.embed_info,
            embed_text=state.embed_text,
            embed_position=state.embed_position,
            embed_max_lines=state.embed_max_lines,
        )

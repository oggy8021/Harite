"""Controller for GUI optimize actions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from harite.resolution import parse_resolution
from harite.core import (
    DEFAULT_BACKGROUND_COLOR_HEX,
    normalize_background_color,
    normalize_optimize_input_paths,
    optimize_wallpapers,
    validate_intentional_image_scales,
)
from harite.optimize_settings import resolve_optimize_display_settings
from harite.positioning import parse_position_pair, position_value_for_side


def resolve_embed_max_lines(embed_info: str, configured: int = 3) -> int:
    mode = str(embed_info or "none").strip().lower()
    if mode == "free":
        return 5
    if mode == "combo":
        return 8
    if mode == "params":
        return max(1, int(configured or 3))
    return max(1, int(configured or 3))


@dataclass
class OptimizeFormState:
    input_value: str
    resolution: str
    output_dir: str
    save_path: Optional[str] = None
    scaling: str = "fit"
    two_screen: Optional[bool] = None
    margins: Optional[str] = None
    l_display: Optional[str] = None
    r_display: Optional[str] = None
    l_display_scale: float = 1.0
    r_display_scale: float = 1.0
    align: tuple[str, str] = ("center", "center")
    valign: tuple[str, str] = ("center", "center")
    quality: int = 90
    background_color: str = DEFAULT_BACKGROUND_COLOR_HEX
    embed_info: str = "none"
    embed_text: Optional[str] = None
    embed_position: str = "right-bottom"
    embed_max_lines: int = 3

    def __post_init__(self) -> None:
        self.align = parse_position_pair(self.align, axis="align")
        self.valign = parse_position_pair(self.valign, axis="valign")
        self.background_color = normalize_background_color(self.background_color)

    def align_for(self, side: str) -> str:
        return position_value_for_side(self.align, side, axis="align")

    def valign_for(self, side: str) -> str:
        return position_value_for_side(self.valign, side, axis="valign")


SLIDESHOW_COMPOSITE_FILENAME = "harite_slideshow.jpg"


class OptimizeController:
    """Thin adapter from GUI form values to core.optimize_wallpapers."""

    def _build_gui_output_path(self, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)

        counter = 1
        while True:
            candidate = output_dir / f"harite_output_{counter:04d}.jpg"
            if not candidate.exists():
                return candidate
            counter += 1

    def _run_with_output_path(self, state: OptimizeFormState, output_path: Path) -> tuple[list[Path], list]:
        self.validate(state)
        inputs = [p.strip() for p in state.input_value.split(",") if p.strip()]
        display_settings = resolve_optimize_display_settings(
            input_values=inputs,
            resolution=state.resolution,
            two_screen=state.two_screen,
            l_display=state.l_display,
            r_display=state.r_display,
        )
        w, h = parse_resolution(display_settings.resolution)
        output = Path(state.output_dir)
        margins = self._parse_margins(state.margins)
        l_display = None if not display_settings.l_display else parse_resolution(display_settings.l_display)
        r_display = None if not display_settings.r_display else parse_resolution(display_settings.r_display)

        return optimize_wallpapers(
            inputs=inputs,
            target_resolution=(w, h),
            output_dir=output,
            output_path=output_path,
            scaling=state.scaling,
            quality=state.quality,
            two_screen=display_settings.two_screen,
            margins=margins,
            l_display=l_display,
            r_display=r_display,
            l_display_scale=state.l_display_scale,
            r_display_scale=state.r_display_scale,
            align=state.align,
            valign=state.valign,
            embed_info=state.embed_info,
            background_color=state.background_color,
            embed_text=state.embed_text,
            embed_position=state.embed_position,
            embed_max_lines=resolve_embed_max_lines(state.embed_info, state.embed_max_lines),
        )

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
        inputs = [p.strip() for p in state.input_value.split(",") if p.strip()]
        normalize_optimize_input_paths(inputs)
        display_settings = resolve_optimize_display_settings(
            input_values=inputs,
            resolution=state.resolution,
            two_screen=state.two_screen,
            l_display=state.l_display,
            r_display=state.r_display,
        )
        w, h = parse_resolution(display_settings.resolution)
        margins = self._parse_margins(state.margins)
        if state.quality < 1 or state.quality > 100:
            raise ValueError("quality must be between 1 and 100")
        if state.embed_info not in ("none", "params", "free", "combo"):
            raise ValueError("embed_info must be one of: none, params, free, combo")
        l_display = None if not display_settings.l_display else parse_resolution(display_settings.l_display)
        r_display = None if not display_settings.r_display else parse_resolution(display_settings.r_display)
        from harite.display_scale import is_unity_display_scale

        if not is_unity_display_scale(state.l_display_scale) or not is_unity_display_scale(state.r_display_scale):
            validate_intentional_image_scales(
                inputs,
                (w, h),
                two_screen=display_settings.two_screen,
                margins=margins,
                l_display=l_display,
                r_display=r_display,
                l_display_scale=state.l_display_scale,
                r_display_scale=state.r_display_scale,
            )

    def run_optimize(self, state: OptimizeFormState) -> tuple[list[Path], list]:
        output = Path(state.output_dir)
        output_path = self._build_gui_output_path(output)
        return self._run_with_output_path(state, output_path)

    def run_export(self, state: OptimizeFormState, save_path: str) -> tuple[list[Path], list]:
        value = (save_path or "").strip()
        if not value:
            raise ValueError("save path is required")
        return self._run_with_output_path(state, Path(value))

    def run_slideshow_optimize(self, state: OptimizeFormState) -> tuple[list[Path], list]:
        """Run optimize for slideshow using a fixed composite slot file in state.output_dir."""
        work_dir = Path(state.output_dir)
        work_dir.mkdir(parents=True, exist_ok=True)
        output_path = work_dir / SLIDESHOW_COMPOSITE_FILENAME
        return self._run_with_output_path(state, output_path)

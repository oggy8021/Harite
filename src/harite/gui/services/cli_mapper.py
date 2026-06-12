"""Map GUI state to CLI-like options for core execution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from harite.core import DEFAULT_BACKGROUND_COLOR_HEX, normalize_background_color
from harite.positioning import format_position_pair, parse_position_pair


@dataclass
class OptimizeRequest:
    input_value: str
    output_dir: Path
    canvas_scale_percent: int = 100
    scaling: str = "fit"
    margins: Optional[str] = None
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


def to_cli_args(req: OptimizeRequest) -> list[str]:
    """Build a deterministic optimize command argument list from GUI state."""
    args = [
        "optimize",
        "--input",
        req.input_value,
        "--output",
        str(req.output_dir),
        "--canvas-scale",
        str(req.canvas_scale_percent),
        "--align",
        format_position_pair(req.align, axis="align"),
        "--valign",
        format_position_pair(req.valign, axis="valign"),
        "--quality",
        str(req.quality),
        "--background-color",
        req.background_color,
        "--embed-info",
        req.embed_info,
        "--embed-position",
        req.embed_position,
    ]
    if req.margins:
        args.extend(["--margins", req.margins])
    if req.embed_text:
        args.extend(["--embed-text", req.embed_text])
    return args

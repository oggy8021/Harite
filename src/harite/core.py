"""Core optimization routines for Harite (minimal, functional stub)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, Tuple, List, Optional
from PIL import Image
from .workspace import Display


@dataclass
class PlacementResult:
    image_path: Path
    x: int
    y: int
    width: int
    height: int
    rotation: float = 0.0
    scale: float = 1.0
    score: float = 1.0
    posit: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "image_path": str(self.image_path),
            "x": int(self.x),
            "y": int(self.y),
            "width": int(self.width),
            "height": int(self.height),
            "rotation": float(self.rotation),
            "scale": float(self.scale),
            "score": float(self.score),
            "posit": self.posit,
        }


def _parse_inputs(inputs: Sequence[Path | str]) -> List[Path]:
    paths: List[Path] = []
    for p in inputs:
        pp = Path(p)
        if pp.is_dir():
            for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp"):
                for f in sorted(pp.glob(ext)):
                    paths.append(f)
        else:
            paths.append(pp)
    return paths


def _scale_to_fit(img: Image.Image, max_w: int, max_h: int) -> Tuple[int, int, float]:
    w, h = img.size
    if w == 0 or h == 0:
        return 1, 1, 1.0
    scale = min(max_w / w, max_h / h)
    nw = max(1, int(w * scale))
    nh = max(1, int(h * scale))
    return nw, nh, scale


def optimize_wallpapers(
    inputs: Sequence[Path | str],
    target_resolution: Tuple[int, int],
    output_dir: Path,
    layout: str = "mosaic",
    scaling: str = "fit",
    padding: int = 0,
    quality: int = 90,
    random_seed: int | None = None,
    **kwargs,
) -> Tuple[List[Path], List[PlacementResult]]:
    """Simple implementation that composes one background image and places 1..N images.

    This is a minimal, well-documented stub intended for early integration and tests.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    items = _parse_inputs(inputs)
    w_target, h_target = target_resolution

    # Compatibility: accept upstream-style kwargs
    two_screen = bool(kwargs.get("two_screen", False))
    margins = kwargs.get("margins", (0, 0, 0, 0))
    try:
        ml, mr, mt, mb = tuple(int(x) for x in margins)
    except Exception:
        ml, mr, mt, mb = (0, 0, 0, 0)
    l_display = kwargs.get("l_display")
    r_display = kwargs.get("r_display")
    _fixed = bool(kwargs.get("fixed", False))

    # Background image
    bg = Image.new("RGB", (w_target, h_target), color=(30, 30, 30))

    placements: List[PlacementResult] = []
    saved_files: List[Path] = []

    count = max(1, len(items))

    # Compute inner available area after margins
    inner_w = max(1, w_target - (ml + mr))
    inner_h = max(1, h_target - (mt + mb))

    # If two-screen with explicit displays, prefer those widths
    if two_screen and l_display and r_display:
        # Force count to 2
        count = 2
        left_w = int(l_display[0])
        right_w = int(r_display[0])
        cell_w_list = [left_w, right_w]
        cell_h = inner_h
    else:
        # Simple layout: split inner width horizontally among items
        cell_w = max(1, (inner_w - padding * (count - 1)) // count)
        cell_h = inner_h
        cell_w_list = [cell_w] * count

    for i, img_path in enumerate(items[:count]):
        try:
            img = Image.open(img_path).convert("RGB")
        except Exception:
            # Skip unreadable images
            continue

        # determine this cell's width
        this_cell_w = cell_w_list[i] if i < len(cell_w_list) else cell_w_list[-1]
        nw, nh, scale = _scale_to_fit(img, this_cell_w, cell_h)
        img_resized = img.resize((nw, nh), Image.LANCZOS)

        # determine alignment offsets (defaults: center)
        align = str(kwargs.get("align", "center")).lower()
        valign = str(kwargs.get("valign", "center")).lower()

        # horizontal offset within this cell
        space_x = max(0, this_cell_w - nw)
        if align == "left":
            inner_x = 0
        elif align == "right":
            inner_x = space_x
        else:
            inner_x = space_x // 2

        # vertical offset within this cell
        space_y = max(0, cell_h - nh)
        if valign == "top":
            inner_y = 0
        elif valign == "bottom":
            inner_y = space_y
        else:
            inner_y = space_y // 2

        # compute x offset: start from left margin
        if two_screen and l_display and r_display:
            if i == 0:
                x = ml + inner_x
            else:
                x = ml + cell_w_list[0] + padding + inner_x
        else:
            x = ml + i * (this_cell_w + padding) + inner_x

        y = mt + inner_y

        bg.paste(img_resized, (x, y))

        pr = PlacementResult(
            image_path=Path(img_path),
            x=int(x),
            y=int(y),
            width=int(nw),
            height=int(nh),
            rotation=0.0,
            scale=float(scale),
            score=1.0,
            posit=("left" if i == 0 else ("right" if i == 1 else None)),
        )
        placements.append(pr)

    # Save result
    out_path = output_dir / ("harite_wallopt_" + str(abs(hash(tuple(items))))[:8] + ".jpg")
    bg.save(out_path, quality=quality)
    saved_files.append(out_path)

    return saved_files, placements


def compute_placement(
    image_path: Path,
    target_resolution: Tuple[int, int],
    layout: str = "mosaic",
    scaling: str = "fit",
    padding: int = 0,
) -> PlacementResult:
    img = Image.open(image_path).convert("RGB")
    nw, nh, scale = _scale_to_fit(img, target_resolution[0], target_resolution[1])
    x = max(0, (target_resolution[0] - nw) // 2)
    y = max(0, (target_resolution[1] - nh) // 2)
    return PlacementResult(image_path=Path(image_path), x=x, y=y, width=nw, height=nh, scale=scale)


def split_composite_for_displays(
    composite_path: Path,
    displays: List[Display],
    output_dir: Path,
) -> dict:
    """Split a composite image into per-display files.

    For each `Display` in `displays`, crop the composite at the display's
    `x_offset` with width `display.width`, then fit the crop into the
    display resolution preserving aspect ratio. Returns mapping
    {display.name: Path} for the saved files.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    comp = Image.open(composite_path).convert("RGB")
    comp_w, comp_h = comp.size

    if not displays:
        return {}

    # Derive virtual desktop bounds from display offsets/sizes.
    # Cropping is then mapped by ratio so a smaller same-aspect composite can
    # still be split in proportion to the real desktop layout.
    min_x = min(d.x_offset for d in displays)
    max_x = max(d.x_offset + d.width for d in displays)
    virtual_w = max(1, max_x - min_x)

    result = {}
    for d in displays:
        left_norm = (d.x_offset - min_x) / virtual_w
        right_norm = (d.x_offset + d.width - min_x) / virtual_w

        left = int(round(left_norm * comp_w))
        right = int(round(right_norm * comp_w))

        left = max(0, min(comp_w, left))
        right = max(0, min(comp_w, right))
        if right <= left:
            if left < comp_w:
                right = left + 1
            else:
                left = max(0, comp_w - 1)
                right = comp_w

        box = (left, 0, right, comp_h)
        try:
            region = comp.crop(box)
        except Exception:
            region = comp.copy()

        # Fit region into target display preserving aspect ratio (fit)
        target_w, target_h = d.width, d.height
        region_w, region_h = region.size
        if region_w == 0 or region_h == 0:
            # fallback: create blank
            out_img = Image.new("RGB", (target_w, target_h), color=(30, 30, 30))
        else:
            scale = min(target_w / region_w, target_h / region_h)
            new_w = max(1, int(region_w * scale))
            new_h = max(1, int(region_h * scale))
            resized = region.resize((new_w, new_h), Image.LANCZOS)
            out_img = Image.new("RGB", (target_w, target_h), color=(30, 30, 30))
            ox = (target_w - new_w) // 2
            oy = (target_h - new_h) // 2
            out_img.paste(resized, (ox, oy))

        name_safe = d.name if d.name else f"display_{d.x_offset}"
        out_path = output_dir / (composite_path.stem + f"_{name_safe}.jpg")
        out_img.save(out_path, quality=90)
        result[d.name] = out_path

    return result

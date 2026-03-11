"""Core optimization routines for Harite (minimal, functional stub)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, Tuple, List, Optional
from PIL import Image


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
) -> Tuple[List[Path], List[PlacementResult]]:
    """Simple implementation that composes one background image and places 1..N images.

    This is a minimal, well-documented stub intended for early integration and tests.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    items = _parse_inputs(inputs)
    w_target, h_target = target_resolution

    # Background image
    bg = Image.new("RGB", (w_target, h_target), color=(30, 30, 30))

    placements: List[PlacementResult] = []
    saved_files: List[Path] = []

    count = max(1, len(items))
    # Simple layout: if multiple images, split horizontally
    cell_w = max(1, (w_target - padding * (count - 1)) // count)
    cell_h = h_target

    for i, img_path in enumerate(items[:count]):
        try:
            img = Image.open(img_path).convert("RGB")
        except Exception:
            # Skip unreadable images
            continue

        nw, nh, scale = _scale_to_fit(img, cell_w, cell_h)
        img_resized = img.resize((nw, nh), Image.LANCZOS)

        x = i * (cell_w + padding) + max(0, (cell_w - nw) // 2)
        y = max(0, (cell_h - nh) // 2)

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

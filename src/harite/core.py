"""Core optimization routines for Harite (minimal, functional stub)."""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Sequence, Tuple, List, Optional
from PIL import Image, ImageDraw, ImageFont
from .positioning import format_position_pair, parse_position_pair
from .workspace import Display


EMBED_POSITION_VALUES: tuple[str, str, str, str] = (
    "left-top",
    "left-bottom",
    "right-top",
    "right-bottom",
)

DEFAULT_BACKGROUND_COLOR_HEX = "#1E1E1E"


def is_background_color_literal(value: object | None) -> bool:
    raw = value
    if isinstance(raw, (tuple, list)) and len(raw) >= 3:
        try:
            return all(0 <= int(channel) <= 255 for channel in raw[:3])
        except Exception:
            return False

    normalized = str(raw or "").strip().upper()
    if not normalized:
        return False
    if normalized.startswith("#"):
        normalized = normalized[1:]
    if len(normalized) != 6:
        return False
    try:
        int(normalized, 16)
    except ValueError:
        return False
    return True


def normalize_background_color(value: object | None) -> str:
    raw = value
    if isinstance(raw, (tuple, list)) and len(raw) >= 3:
        try:
            red = max(0, min(255, int(raw[0])))
            green = max(0, min(255, int(raw[1])))
            blue = max(0, min(255, int(raw[2])))
            return f"#{red:02X}{green:02X}{blue:02X}"
        except Exception:
            return DEFAULT_BACKGROUND_COLOR_HEX

    normalized = str(raw or "").strip().upper()
    if not is_background_color_literal(normalized):
        return DEFAULT_BACKGROUND_COLOR_HEX
    if not normalized.startswith("#"):
        normalized = f"#{normalized}"
    return normalized


def background_color_rgb(value: object | None) -> tuple[int, int, int]:
    normalized = normalize_background_color(value)
    return (
        int(normalized[1:3], 16),
        int(normalized[3:5], 16),
        int(normalized[5:7], 16),
    )


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
        """Convert placement result to serializable dictionary.

        Summary:
            `PlacementResult` の内容を JSON 直列化可能な辞書に変換して返す。

        Returns:
            辞書表現。
        """
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


def normalize_optimize_input_paths(inputs: Sequence[Path | str]) -> List[Path]:
    """optimize 用入力パス群を file-only として正規化する。

    Summary:
        optimize では画像ファイルのみを受け付ける。
        既存ディレクトリが渡された場合は明示エラーにする。

    Args:
        inputs: Path または文字列の列。

    Returns:
        `Path` のリスト。
    """
    paths: List[Path] = []
    for p in inputs:
        pp = Path(p).expanduser()
        if pp.is_dir():
            raise ValueError(f"optimize --input does not accept directories: {pp}")
        paths.append(pp)
    return paths


def _parse_inputs(inputs: Sequence[Path | str]) -> List[Path]:
    """入力パス群を optimize 用 file-only ルールで正規化して返す。"""
    return normalize_optimize_input_paths(inputs)


def _scale_to_fit(img: Image.Image, max_w: int, max_h: int) -> Tuple[int, int, float]:
    """画像を指定領域に収めるスケールを計算して新サイズを返す。

    Args:
        img: Pillow 画像オブジェクト。
        max_w: 最大幅。
        max_h: 最大高さ。

    Returns:
        (new_width, new_height, scale_factor)
    """
    w, h = img.size
    if w == 0 or h == 0:
        return 1, 1, 1.0
    scale = min(max_w / w, max_h / h)
    nw = max(1, int(w * scale))
    nh = max(1, int(h * scale))
    return nw, nh, scale


def _image_fits_with_margins(
    img_w: int,
    img_h: int,
    screen_w: int,
    screen_h: int,
    margins: Tuple[int, int, int, int],
) -> bool:
    """Return True when image plus margins fit inside the display rectangle."""
    ml, mr, mt, mb = margins
    return screen_w >= img_w + ml + mr and screen_h >= img_h + mt + mb


def _downsize_to_fit_margins(
    img_w: int,
    img_h: int,
    screen_w: int,
    screen_h: int,
    margins: Tuple[int, int, int, int],
) -> Tuple[int, int, float]:
    """Shrink image to fit a display with margins (parent down-only; never upscale)."""
    if img_w == 0 or img_h == 0:
        return 1, 1, 1.0
    ml, mr, mt, mb = margins
    max_w = max(1, screen_w - ml - mr)
    max_h = max(1, screen_h - mt - mb)
    w, h = img_w, img_h
    orig_w, orig_h = w, h
    if w > max_w:
        h = max(1, int(h * max_w / w))
        w = max_w
    if h > max_h:
        w = max(1, int(w * max_h / h))
        h = max_h
    scale = min(w / orig_w, h / orig_h)
    return w, h, float(scale)


def _resolve_native_dimensions(
    img: Image.Image,
    screen_w: int,
    screen_h: int,
    margins: Tuple[int, int, int, int],
) -> Tuple[int, int, float]:
    """Keep native size when image+margins fit; otherwise parent-style downsize only."""
    w, h = img.size
    if _image_fits_with_margins(w, h, screen_w, screen_h, margins):
        return w, h, 1.0
    return _downsize_to_fit_margins(w, h, screen_w, screen_h, margins)


def _allocate_on_display(
    img_w: int,
    img_h: int,
    screen_w: int,
    screen_h: int,
    align: str,
    valign: str,
) -> Tuple[int, int]:
    """Position image within a display rectangle (origin left/top; parent parity)."""
    space_x = max(0, screen_w - img_w)
    space_y = max(0, screen_h - img_h)
    if align == "right":
        x = space_x
    elif align == "center":
        x = space_x // 2
    else:
        x = 0
    if valign == "bottom":
        y = space_y
    elif valign == "center":
        y = space_y // 2
    else:
        y = 0
    return x, y


def _resolve_display_slots(
    *,
    w_target: int,
    h_target: int,
    count: int,
    two_screen: bool,
    l_display: Optional[Tuple[int, int]],
    r_display: Optional[Tuple[int, int]],
    ml: int,
    mr: int,
    mt: int,
    mb: int,
) -> List[Tuple[int, int, int, int, Tuple[int, int, int, int]]]:
    """Return per-image slots: (origin_x, origin_y, screen_w, screen_h, side_margins)."""
    slots: List[Tuple[int, int, int, int, Tuple[int, int, int, int]]] = []

    if two_screen and l_display and r_display:
        left_w = int(l_display[0])
        right_w = int(r_display[0])
        total_display_w = max(1, left_w + right_w)
        split_x = int(round((left_w / total_display_w) * w_target))
        split_x = max(1, min(w_target - 1, split_x)) if w_target > 1 else w_target
        left_slice_w = max(1, int(split_x or 0))
        right_slice_w = max(1, w_target - left_slice_w)
        left_screen_h = max(1, min(h_target, int(l_display[1])))
        right_screen_h = max(1, min(h_target, int(r_display[1])))
        slots.append((0, 0, left_slice_w, left_screen_h, (ml, 0, mt, mb)))
        slots.append((split_x, 0, right_slice_w, right_screen_h, (0, mr, mt, mb)))
        return slots[:count]

    if two_screen:
        left_slice_w = max(1, w_target // 2)
        right_slice_w = max(1, w_target - left_slice_w)
        slots.append((0, 0, left_slice_w, h_target, (ml, 0, mt, mb)))
        slots.append((left_slice_w, 0, right_slice_w, h_target, (0, mr, mt, mb)))
        return slots[:count]

    if count <= 1:
        slots.append((0, 0, w_target, h_target, (ml, mr, mt, mb)))
        return slots

    base_w = max(1, w_target // count)
    widths = [base_w] * count
    widths[-1] = max(1, w_target - base_w * (count - 1))
    origin_x = 0
    for i, slice_w in enumerate(widths):
        if i == 0:
            side_margins = (ml, 0, mt, mb)
        elif i == count - 1:
            side_margins = (0, mr, mt, mb)
        else:
            side_margins = (0, 0, mt, mb)
        slots.append((origin_x, 0, slice_w, h_target, side_margins))
        origin_x += slice_w
    return slots


def _build_embed_lines(
    mode: str,
    *,
    target_resolution: Tuple[int, int],
    margins: Tuple[int, int, int, int],
    align: str,
    valign: str,
    input_count: int,
    two_screen: bool,
    l_display: Optional[Tuple[int, int]],
    r_display: Optional[Tuple[int, int]],
    free_text: Optional[str],
) -> List[str]:
    """余白に埋め込む情報行を構築する。

    Summary:
        埋め込みモードに応じてパラメータ行やフリーテキストを生成する。

    Args:
        mode: 埋め込みモード文字列。
        target_resolution: 目標解像度 (w, h)。
        margins: (l, r, t, b) の各余白。
        align: 横寄せ。
        valign: 縦寄せ。
        input_count: 入力画像数。
        two_screen: 2画面モードフラグ。
        l_display: 左画面解像度。
        r_display: 右画面解像度。
        free_text: フリーテキスト。

    Returns:
        表示用の行リスト。
    """
    mode_norm = str(mode or "none").lower()
    if mode_norm == "none":
        return []

    params_lines: List[str] = []
    if mode_norm in ("params", "combo"):
        w_target, h_target = target_resolution
        ml, mr, mt, mb = margins
        params_lines.append(f"res={w_target}x{h_target} margins={ml},{mr},{mt},{mb}")
        params_lines.append(f"align={align}/{valign} inputs={input_count}")
        if two_screen:
            if l_display and r_display:
                params_lines.append(
                    f"two_screen=1 l={l_display[0]}x{l_display[1]} r={r_display[0]}x{r_display[1]}"
                )
            else:
                params_lines.append("two_screen=1")

    free_lines: List[str] = []
    if mode_norm in ("free", "combo") and free_text:
        for line in str(free_text).splitlines():
            v = line.strip()
            if v:
                free_lines.append(v)

    return params_lines + free_lines


def describe_embed_position(position: str) -> str:
    """Return the canonical embed_position label."""
    normalized = str(position or "").strip().lower()
    if normalized in EMBED_POSITION_VALUES:
        return normalized.replace("-", " ")
    return "right bottom"


def resolve_embed_margin_region(
    target_size: Tuple[int, int],
    margins: Tuple[int, int, int, int],
    position: str,
    *,
    two_screen: bool = False,
    l_display: Tuple[int, int] | None = None,
    r_display: Tuple[int, int] | None = None,
) -> Tuple[int, int, int, int] | None:
    """Resolve canonical margin-text placement to a concrete display-aware region."""
    normalized = str(position or "").strip().lower()
    if normalized not in EMBED_POSITION_VALUES:
        return None

    w_target, h_target = target_size
    ml, mr, mt, mb = margins

    def _vertical_region(x0: int, x1: int, slice_h: int, *, top_side: bool) -> Tuple[int, int, int, int]:
        inner_x0 = max(0, x0)
        inner_x1 = max(inner_x0, x1)
        inner_y1 = max(0, min(h_target, max(0, slice_h)))
        if top_side:
            return (inner_x0, 0, inner_x1, max(0, mt))
        return (inner_x0, max(0, inner_y1 - max(0, mb)), inner_x1, inner_y1)

    if two_screen and l_display and r_display:
        left_x0 = max(0, ml)
        left_x1 = max(left_x0, int(l_display[0]) - max(0, mr))
        right_offset = int(l_display[0])
        right_x0 = right_offset + max(0, ml)
        right_x1 = max(right_x0, right_offset + int(r_display[0]) - max(0, mr))
        if normalized == "left-top":
            return _vertical_region(left_x0, left_x1, int(l_display[1]), top_side=True)
        if normalized == "left-bottom":
            return _vertical_region(left_x0, left_x1, int(l_display[1]), top_side=False)
        if normalized == "right-top":
            return _vertical_region(right_x0, right_x1, int(r_display[1]), top_side=True)
        return _vertical_region(right_x0, right_x1, int(r_display[1]), top_side=False)

    if two_screen:
        left_slice_w = max(1, w_target // 2)
        left_x0 = max(0, ml)
        left_x1 = max(left_x0, left_slice_w - max(0, mr))
        right_x0 = left_slice_w + max(0, ml)
        right_x1 = max(right_x0, w_target - max(0, mr))
        if normalized == "left-top":
            return _vertical_region(left_x0, left_x1, h_target, top_side=True)
        if normalized == "left-bottom":
            return _vertical_region(left_x0, left_x1, h_target, top_side=False)
        if normalized == "right-top":
            return _vertical_region(right_x0, right_x1, h_target, top_side=True)
        return _vertical_region(right_x0, right_x1, h_target, top_side=False)

    usable_left = max(0, ml)
    usable_right = max(usable_left, w_target - max(0, mr))
    usable_width = max(0, usable_right - usable_left)
    left_slice_width = usable_width // 2
    right_slice_width = usable_width - left_slice_width

    if normalized == "left-top":
        return (usable_left, 0, usable_left + left_slice_width, max(0, mt))
    if normalized == "left-bottom":
        return (usable_left, max(0, h_target - mb), usable_left + left_slice_width, h_target)
    if normalized == "right-top":
        return (usable_right - right_slice_width, 0, usable_right, max(0, mt))
    return (usable_right - right_slice_width, max(0, h_target - mb), usable_right, h_target)


def _resolve_cell_alignment(kwargs: dict[str, object], index: int) -> tuple[str, str]:
    align_left, align_right = parse_position_pair(kwargs.get("align", "center"), axis="align")
    valign_left, valign_right = parse_position_pair(kwargs.get("valign", "center"), axis="valign")
    if index == 0:
        return align_left, valign_left
    if index == 1:
        return align_right, valign_right
    return align_left, valign_left


def _truncate_to_width(draw: ImageDraw.ImageDraw, text: str, max_w: int, font: ImageFont.ImageFont) -> str:
    """テキストを最大幅に収まるよう切り詰める（末尾に省略記号）。

    Args:
        draw: `ImageDraw` インスタンス。
        text: 元のテキスト。
        max_w: 最大幅(px)。
        font: 使用フォント。

    Returns:
        切り詰めたテキスト。
    """
    if max_w <= 0:
        return ""
    if draw.textlength(text, font=font) <= max_w:
        return text
    ellipsis = "..."
    if draw.textlength(ellipsis, font=font) > max_w:
        return ""
    out = ""
    for ch in text:
        candidate = out + ch
        if draw.textlength(candidate + ellipsis, font=font) > max_w:
            break
        out = candidate
    return out + ellipsis


def _load_preferred_font(size: int, explicit_path: Optional[str] = None) -> ImageFont.ImageFont:
    """Load a preferred font for embed text with CJK-capable candidates.

    Args:
        size: Font size in px.
        explicit_path: Optional explicit font path from CLI.

    Returns:
        Loaded PIL font object. Falls back to `ImageFont.load_default()`.
    """
    font_size = max(8, int(size))

    candidates: List[str] = []
    if explicit_path:
        candidates.append(str(explicit_path))

    # Common CJK-capable fonts by platform (best effort).
    candidates.extend(
        [
            # Windows
            r"C:\Windows\Fonts\meiryo.ttc",
            r"C:\Windows\Fonts\msgothic.ttc",
            r"C:\Windows\Fonts\YuGothM.ttc",
            # Linux
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansJP-Regular.otf",
            # macOS
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        ]
    )

    # Keep order while removing duplicates.
    deduped: List[str] = []
    seen = set()
    for c in candidates:
        if c and c not in seen:
            deduped.append(c)
            seen.add(c)

    for path in deduped:
        # Explicit path should be tried even if existence check is unreliable.
        if explicit_path and path == str(explicit_path):
            try:
                return ImageFont.truetype(path, font_size)
            except Exception:
                pass
            continue

        if not os.path.exists(path):
            continue
        try:
            return ImageFont.truetype(path, font_size)
        except Exception:
            continue

    return ImageFont.load_default()


def _draw_embed_text_in_margin(
    bg: Image.Image,
    lines: List[str],
    *,
    margins: Tuple[int, int, int, int],
    position: str,
    max_lines: int,
    embed_font: Optional[str] = None,
    two_screen: bool = False,
    l_display: Tuple[int, int] | None = None,
    r_display: Tuple[int, int] | None = None,
) -> None:
    """余白に埋め込みテキストを描画する。

    Args:
        bg: 背景画像。
        lines: 描画する行リスト。
        margins: 余白 (l, r, t, b)。
        position: 描画位置指定。
        max_lines: 最大行数。

    Returns:
        None
    """
    if not lines:
        return

    ml, mr, mt, mb = margins
    w_target, h_target = bg.size
    pos = str(position or "right-bottom").lower()

    area = resolve_embed_margin_region(
        (w_target, h_target),
        (ml, mr, mt, mb),
        pos,
        two_screen=two_screen,
        l_display=l_display,
        r_display=r_display,
    )
    if area is None:
        return

    x0, y0, x1, y1 = area
    area_w = max(0, x1 - x0)
    area_h = max(0, y1 - y0)
    if area_w < 40 or area_h < 12:
        return

    draw = ImageDraw.Draw(bg)
    preferred_size = max(12, min(24, area_h // max(1, max_lines + 1)))
    font = _load_preferred_font(preferred_size, explicit_path=embed_font)
    line_h = max(10, font.getbbox("Ag")[3] - font.getbbox("Ag")[1] + 2)

    fit_lines = max(0, area_h // line_h)
    line_limit = min(max(1, int(max_lines)), fit_lines)
    if line_limit <= 0:
        return

    cropped_lines = lines[:line_limit]
    if len(lines) > line_limit:
        cropped_lines[-1] = cropped_lines[-1] + " ..."

    longest_px = 0
    for line in cropped_lines:
        bbox = font.getbbox(line or " ")
        longest_px = max(longest_px, max(0, bbox[2] - bbox[0]))

    quartile_offset = max(4, min(max(1, area_w // 4), max(1, longest_px // 4 or 1)))
    text_x = x0 + quartile_offset
    text_y = y0 + 2
    max_text_w = max(0, area_w - quartile_offset - 4)
    for line in cropped_lines:
        if text_y + line_h > y1:
            break
        one_line = _truncate_to_width(draw, line, max_text_w, font)
        if one_line:
            draw.text((text_x, text_y), one_line, fill=(235, 235, 235), font=font)
        text_y += line_h


def optimize_wallpapers(
    inputs: Sequence[Path | str],
    target_resolution: Tuple[int, int],
    output_dir: Path,
    scaling: str = "fit",
    quality: int = 90,
    output_path: Path | None = None,
    **kwargs,
) -> Tuple[List[Path], List[PlacementResult]]:
    """壁紙最適化（簡易実装）。

    Summary:
        複数の入力画像を受け取り、指定解像度に合わせて合成背景を生成し、
        配置情報と保存ファイル一覧を返す簡易実装。

    Args:
        inputs: 入力ファイルパス列。
        target_resolution: 出力解像度 (w, h)。
        output_dir: 出力先ディレクトリ。
        output_path: 出力先ファイルパス（指定時は自動命名より優先）。
        scaling: スケーリングモード。
        quality: JPEG 品質。
        **kwargs: 互換性のための追加オプション（two_screen, margins, 等）。

    Returns:
        (saved_files, placements) を返す。`saved_files` は生成画像のパス一覧、
        `placements` は `PlacementResult` のリスト。
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
    embed_info = str(kwargs.get("embed_info", "none")).lower()
    background_color = normalize_background_color(kwargs.get("background_color", DEFAULT_BACKGROUND_COLOR_HEX))
    embed_text = kwargs.get("embed_text")
    embed_position = str(kwargs.get("embed_position", "right-bottom")).lower()
    try:
        embed_max_lines = int(kwargs.get("embed_max_lines", 3))
    except Exception:
        embed_max_lines = 3

    # Background image
    bg = Image.new("RGB", (w_target, h_target), color=background_color_rgb(background_color))

    placements: List[PlacementResult] = []
    saved_files: List[Path] = []

    count = max(1, len(items))
    if two_screen:
        count = min(2, count)

    display_slots = _resolve_display_slots(
        w_target=w_target,
        h_target=h_target,
        count=count,
        two_screen=two_screen,
        l_display=l_display,
        r_display=r_display,
        ml=ml,
        mr=mr,
        mt=mt,
        mb=mb,
    )

    for i, img_path in enumerate(items[:count]):
        try:
            img = Image.open(img_path).convert("RGB")
        except Exception:
            # Skip unreadable images
            continue

        slot = display_slots[i] if i < len(display_slots) else display_slots[-1]
        origin_x, origin_y, screen_w, screen_h, side_margins = slot
        nw, nh, scale = _resolve_native_dimensions(img, screen_w, screen_h, side_margins)
        if (nw, nh) != img.size:
            img_resized = img.resize((nw, nh), Image.LANCZOS)
        else:
            img_resized = img

        align, valign = _resolve_cell_alignment(kwargs, i)
        inner_x, inner_y = _allocate_on_display(nw, nh, screen_w, screen_h, align, valign)
        x = origin_x + inner_x
        y = origin_y + inner_y

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
    embed_lines = _build_embed_lines(
        embed_info,
        target_resolution=target_resolution,
        margins=(ml, mr, mt, mb),
        align=format_position_pair(kwargs.get("align", "center"), axis="align"),
        valign=format_position_pair(kwargs.get("valign", "center"), axis="valign"),
        input_count=len(items),
        two_screen=two_screen,
        l_display=l_display,
        r_display=r_display,
        free_text=embed_text,
    )
    _draw_embed_text_in_margin(
        bg,
        embed_lines,
        margins=(ml, mr, mt, mb),
        position=embed_position,
        max_lines=embed_max_lines,
        embed_font=kwargs.get("embed_font"),
        two_screen=two_screen,
        l_display=l_display,
        r_display=r_display,
    )

    if output_path is not None:
        out_path = Path(output_path)
        if not out_path.suffix:
            out_path = out_path.with_suffix(".jpg")
        out_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        counter = 1
        while True:
            candidate = output_dir / f"harite_output_{counter:04d}.jpg"
            if not candidate.exists():
                out_path = candidate
                break
            counter += 1
    bg.save(out_path, quality=quality)
    saved_files.append(out_path)

    return saved_files, placements


def compute_placement(
    image_path: Path,
    target_resolution: Tuple[int, int],
    scaling: str = "fit",
) -> PlacementResult:
    """単一画像の中央配置を計算して `PlacementResult` を返す。

    Args:
        image_path: 画像ファイルのパス。
        target_resolution: (w, h) の目標解像度。
        scaling: スケーリングモード。

    Returns:
        `PlacementResult`。
    """
    img = Image.open(image_path).convert("RGB")
    screen_w, screen_h = target_resolution
    zero_margins = (0, 0, 0, 0)
    nw, nh, scale = _resolve_native_dimensions(img, screen_w, screen_h, zero_margins)
    x, y = _allocate_on_display(nw, nh, screen_w, screen_h, "center", "center")
    return PlacementResult(image_path=Path(image_path), x=x, y=y, width=nw, height=nh, scale=scale)


def split_composite_for_displays(
    composite_path: Path,
    displays: List[Display],
    output_dir: Path,
    background_color: object | None = None,
) -> dict:
    """合成画像を各ディスプレイ向けに分割してファイルを作成する。

    Summary:
        各 `Display` の `x_offset` と幅に基づいて合成画像をクロップし、
        表示解像度に合わせてリサイズして保存する。保存先のパスを
        {display.name: Path} の辞書で返す。

    Args:
        composite_path: 合成画像のパス。
        displays: `Display` オブジェクトのリスト。
        output_dir: 出力ディレクトリ。

    Returns:
        ディスプレイ名 -> 出力ファイルパスの辞書。
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    comp = Image.open(composite_path).convert("RGB")
    comp_w, comp_h = comp.size
    normalized_background_color = normalize_background_color(
        DEFAULT_BACKGROUND_COLOR_HEX if background_color is None else background_color
    )

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
            out_img = Image.new("RGB", (target_w, target_h), color=background_color_rgb(normalized_background_color))
        else:
            scale = min(target_w / region_w, target_h / region_h)
            new_w = max(1, int(region_w * scale))
            new_h = max(1, int(region_h * scale))
            resized = region.resize((new_w, new_h), Image.LANCZOS)
            out_img = Image.new("RGB", (target_w, target_h), color=background_color_rgb(normalized_background_color))
            ox = (target_w - new_w) // 2
            oy = (target_h - new_h) // 2
            out_img.paste(resized, (ox, oy))

        name_safe = d.name if d.name else f"display_{d.x_offset}"
        out_path = output_dir / (composite_path.stem + f"_{name_safe}.jpg")
        out_img.save(out_path, quality=90)
        result[d.name] = out_path

    return result

"""Generate packaging/windows/harite_app.ico from harite_app.svg for PyInstaller."""

from __future__ import annotations

import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG_PATH = ROOT / "src/harite/gui/resources/icons/product/harite_app.svg"
ICO_PATH = ROOT / "packaging/windows/harite_app.ico"
ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)


def _qimage_to_pil(image) -> "object":
    from PIL import Image
    from PyQt6.QtCore import QBuffer, QIODevice

    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    if not image.save(buffer, "PNG"):
        raise RuntimeError("failed to encode QImage as PNG")
    data = bytes(buffer.data().data())
    return Image.open(io.BytesIO(data)).convert("RGBA")


def build_icon(svg_path: Path = SVG_PATH, ico_path: Path = ICO_PATH) -> Path:
    from PyQt6.QtCore import QSize
    from PyQt6.QtGui import QImage, QPainter
    from PyQt6.QtSvg import QSvgRenderer
    from PyQt6.QtWidgets import QApplication

    if not svg_path.is_file():
        raise FileNotFoundError(f"SVG not found: {svg_path}")

    app = QApplication.instance() or QApplication(sys.argv)
    _ = app  # keep reference

    renderer = QSvgRenderer(str(svg_path))
    if not renderer.isValid():
        raise RuntimeError(f"Invalid SVG: {svg_path}")

    pil_images = []
    for size in ICON_SIZES:
        qimage = QImage(QSize(size, size), QImage.Format.Format_ARGB32)
        qimage.fill(0)
        painter = QPainter(qimage)
        renderer.render(painter)
        painter.end()
        pil_images.append(_qimage_to_pil(qimage))

    ico_path.parent.mkdir(parents=True, exist_ok=True)
    master = pil_images[-1]
    master.save(
        ico_path,
        format="ICO",
        sizes=[(img.width, img.height) for img in pil_images],
        append_images=pil_images[:-1],
    )
    return ico_path


def main() -> None:
    path = build_icon()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()

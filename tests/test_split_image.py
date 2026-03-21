from PIL import Image

from harite.core import split_composite_for_displays
from harite.workspace import Display


def test_split_image(tmp_path):
    comp = Image.new("RGB", (3840, 1080), (255, 0, 0))
    comp_path = tmp_path / "comp.jpg"
    comp.save(comp_path)

    displays = [Display("DP-1", 1920, 1080, 0, True), Display("HDMI-1", 1920, 1080, 1920, False)]
    out = split_composite_for_displays(comp_path, displays, output_dir=tmp_path)

    assert "DP-1" in out
    assert "HDMI-1" in out

    from PIL import Image as PILImage

    li = PILImage.open(out["DP-1"]) 
    ri = PILImage.open(out["HDMI-1"]) 
    assert li.size == (1920, 1080)
    assert ri.size == (1920, 1080)


def test_split_image_with_scaled_composite_ratio_mapping(tmp_path):
    # Simulate a 4096x1280 virtual desktop represented by a half-scale
    # composite (2048x640): left half red, right half blue.
    comp = Image.new("RGB", (2048, 640), (0, 0, 0))
    left = Image.new("RGB", (1024, 640), (255, 0, 0))
    right = Image.new("RGB", (1024, 640), (0, 0, 255))
    comp.paste(left, (0, 0))
    comp.paste(right, (1024, 0))

    comp_path = tmp_path / "comp_scaled.jpg"
    comp.save(comp_path)

    displays = [
        Display("DP-1", 2048, 1280, 0, True),
        Display("HDMI-1", 2048, 1280, 2048, False),
    ]
    out = split_composite_for_displays(comp_path, displays, output_dir=tmp_path)

    from PIL import Image as PILImage

    li = PILImage.open(out["DP-1"])
    ri = PILImage.open(out["HDMI-1"])
    assert li.size == (2048, 1280)
    assert ri.size == (2048, 1280)

    # Center pixel should keep dominant color of each half after resize.
    lpx = li.getpixel((li.size[0] // 2, li.size[1] // 2))
    rpx = ri.getpixel((ri.size[0] // 2, ri.size[1] // 2))
    assert lpx[0] > lpx[2]
    assert rpx[2] > rpx[0]

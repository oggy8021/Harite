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

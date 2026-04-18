from pathlib import Path

from PIL import Image

from harite.display_context import build_auto_split_display_map, build_two_screen_optimize_context, derive_virtual_resolution, order_displays
from harite.workspace import Display


def test_order_displays_sorts_by_offsets_then_name():
    displays = [
        Display(name="R", width=1280, height=1024, x_offset=1920),
        Display(name="L", width=1920, height=1080, x_offset=0),
    ]

    ordered = order_displays(displays)

    assert [display.name for display in ordered] == ["L", "R"]


def test_derive_virtual_resolution_uses_display_bounds():
    displays = [
        Display(name="L", width=1920, height=1080, x_offset=0, y_offset=120),
        Display(name="R", width=1280, height=1024, x_offset=1920, y_offset=0),
    ]

    resolution = derive_virtual_resolution(displays)

    assert resolution == (3200, 1200)


def test_build_two_screen_optimize_context_returns_ordered_displays(monkeypatch):
    monkeypatch.setattr(
        "harite.display_context.detect_displays",
        lambda: [
            Display(name="R", width=1280, height=1024, x_offset=1920),
            Display(name="L", width=1920, height=1080, x_offset=0),
        ],
    )

    context = build_two_screen_optimize_context()

    assert context is not None
    assert context.displays[0].name == "L"
    assert context.displays[1].name == "R"
    assert context.resolution == (3200, 1080)
    assert context.l_display == (1920, 1080)
    assert context.r_display == (1280, 1024)


def test_build_auto_split_display_map_uses_parent_output_by_default(tmp_path):
    comp = Image.new("RGB", (1000, 300), (10, 20, 30))
    comp_path = tmp_path / "comp.jpg"
    comp.save(comp_path)

    displays = [
        Display(name="left", width=400, height=300, x_offset=0),
        Display(name="right", width=600, height=300, x_offset=400),
    ]

    result = build_auto_split_display_map(comp_path, displays)

    assert set(result.keys()) == {"left", "right"}
    for path in result.values():
        assert Path(path).exists()
        assert Path(path).parent == tmp_path
from pathlib import Path

from harite.gui.services.cli_mapper import OptimizeRequest, to_cli_args


def test_to_cli_args_contains_required_fields(tmp_path):
    out_dir = tmp_path / "out"
    req = OptimizeRequest(
        input_value="a.jpg,b.jpg",
        output_dir=out_dir,
        canvas_scale_percent=75,
    )

    args = to_cli_args(req)

    assert args[:2] == ["optimize", "--input"]
    assert "--input" in args and "a.jpg,b.jpg" in args
    assert "--canvas-scale" in args and "75" in args
    assert "--output" in args and str(out_dir) in args
    assert "--align" in args and "center,center" in args
    assert "--valign" in args and "center,center" in args


def test_to_cli_args_omits_optional_flags_when_unset(tmp_path):
    req = OptimizeRequest(
        input_value="a.jpg",
        output_dir=tmp_path / "out",
    )

    args = to_cli_args(req)

    assert "--two-screen" not in args
    assert "--margins" not in args
    assert "--l-display" not in args
    assert "--r-display" not in args
    assert "--embed-text" not in args


def test_to_cli_args_includes_optional_flags_when_set(tmp_path):
    req = OptimizeRequest(
        input_value="a.jpg",
        output_dir=tmp_path / "out",
        margins="1,2,3,4",
        align=("left", "right"),
        valign=("top", "bottom"),
        embed_text="note",
    )

    args = to_cli_args(req)

    assert "--margins" in args and "1,2,3,4" in args
    assert "--align" in args and "left,right" in args
    assert "--valign" in args and "top,bottom" in args
    assert "--embed-text" in args and "note" in args

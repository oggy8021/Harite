from pathlib import Path

from harite.gui.services.cli_mapper import OptimizeRequest, to_cli_args


def test_to_cli_args_contains_required_fields(tmp_path):
    out_dir = tmp_path / "out"
    req = OptimizeRequest(
        input_value="a.jpg,b.jpg",
        resolution="1920x1080",
        output_dir=out_dir,
    )

    args = to_cli_args(req)

    assert args[:2] == ["optimize", "--input"]
    assert "--input" in args and "a.jpg,b.jpg" in args
    assert "--resolution" in args and "1920x1080" in args
    assert "--output" in args and str(out_dir) in args


def test_to_cli_args_omits_optional_flags_when_unset(tmp_path):
    req = OptimizeRequest(
        input_value="a.jpg",
        resolution="1280x720",
        output_dir=tmp_path / "out",
    )

    args = to_cli_args(req)

    assert "--two-screen" not in args
    assert "--margins" not in args
    assert "--l-display" not in args
    assert "--r-display" not in args
    assert "--fixed" not in args
    assert "--embed-text" not in args


def test_to_cli_args_includes_optional_flags_when_set(tmp_path):
    req = OptimizeRequest(
        input_value="a.jpg",
        resolution="1280x720",
        output_dir=tmp_path / "out",
        two_screen=True,
        margins="1,2,3,4",
        l_display="1920x1080",
        r_display="1280x1024",
        fixed=True,
        embed_text="note",
    )

    args = to_cli_args(req)

    assert "--two-screen" in args
    assert "--margins" in args and "1,2,3,4" in args
    assert "--l-display" in args and "1920x1080" in args
    assert "--r-display" in args and "1280x1024" in args
    assert "--fixed" in args
    assert "--embed-text" in args and "note" in args

import pytest

from harite import cli
from typer.testing import CliRunner


def test_parse_resolution_valid():
    assert cli.parse_resolution("1920x1080") == (1920, 1080)
    assert cli.parse_resolution("3840X2160") == (3840, 2160)


def test_parse_resolution_invalid():
    with pytest.raises(ValueError):
        cli.parse_resolution("bad")
    with pytest.raises(ValueError):
        cli.parse_resolution("0x1080")


def test_parse_margins_valid():
    assert cli.parse_margins("10,20,30,40") == (10, 20, 30, 40)


def test_parse_margins_invalid():
    with pytest.raises(ValueError):
        cli.parse_margins("10,20,30")
    with pytest.raises(ValueError):
        cli.parse_margins("10,-5,0,0")


def test_parse_display_valid():
    assert cli.parse_display("1280x720") == (1280, 720)


def test_optimize_rejects_invalid_embed_info(tmp_path):
    runner = CliRunner()
    img = tmp_path / "a.jpg"
    from PIL import Image

    Image.new("RGB", (10, 10), (100, 100, 100)).save(img)
    result = runner.invoke(
        cli.app,
        [
            "optimize",
            "--input",
            str(img),
            "--resolution",
            "100x100",
            "--embed-info",
            "datetime",
        ],
    )
    assert result.exit_code == 2
    assert "--embed-info must be one of" in result.output


def test_optimize_rejects_invalid_embed_position(tmp_path):
    runner = CliRunner()
    img = tmp_path / "a.jpg"
    from PIL import Image

    Image.new("RGB", (10, 10), (100, 100, 100)).save(img)
    result = runner.invoke(
        cli.app,
        [
            "optimize",
            "--input",
            str(img),
            "--resolution",
            "100x100",
            "--embed-position",
            "middle",
        ],
    )
    assert result.exit_code == 2
    assert "--embed-position must be one of" in result.output

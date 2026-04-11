import pytest
import json

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


def test_optimize_uses_config_for_required_values(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    cfg = tmp_path / "config.json"
    cfg.write_text(
        json.dumps(
            {
                "input": ["from_config.jpg"],
                "resolution": "1600x900",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)

    result = runner.invoke(cli.app, ["optimize", "--config", str(cfg)])

    assert result.exit_code == 0
    assert captured["inputs"] == ["from_config.jpg"]
    assert captured["target_resolution"] == (1600, 900)


def test_optimize_cli_values_override_config(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    cfg = tmp_path / "config.json"
    cfg.write_text(
        json.dumps(
            {
                "input": ["from_config.jpg"],
                "resolution": "1600x900",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)

    result = runner.invoke(
        cli.app,
        [
            "optimize",
            "--config",
            str(cfg),
            "--input",
            "from_cli.jpg",
            "--resolution",
            "1920x1080",
        ],
    )

    assert result.exit_code == 0
    assert captured["inputs"] == ["from_cli.jpg"]
    assert captured["target_resolution"] == (1920, 1080)


def test_optimize_uses_config_for_margins_and_displays(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    cfg = tmp_path / "config.json"
    cfg.write_text(
        json.dumps(
            {
                "input": ["from_config.jpg"],
                "resolution": "1600x900",
                "margins": "1,2,3,4",
                "l_display": "1920x1080",
                "r_display": "1280x1024",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)

    result = runner.invoke(cli.app, ["optimize", "--config", str(cfg)])

    assert result.exit_code == 0
    assert captured["margins"] == (1, 2, 3, 4)
    assert captured["l_display"] == (1920, 1080)
    assert captured["r_display"] == (1280, 1024)


def test_optimize_cli_values_override_config_for_margins_and_displays(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    cfg = tmp_path / "config.json"
    cfg.write_text(
        json.dumps(
            {
                "input": ["from_config.jpg"],
                "resolution": "1600x900",
                "margins": "1,2,3,4",
                "l_display": "1920x1080",
                "r_display": "1280x1024",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)

    result = runner.invoke(
        cli.app,
        [
            "optimize",
            "--config",
            str(cfg),
            "--margins",
            "10,20,30,40",
            "--l-display",
            "2560x1440",
            "--r-display",
            "1920x1200",
        ],
    )

    assert result.exit_code == 0
    assert captured["margins"] == (10, 20, 30, 40)
    assert captured["l_display"] == (2560, 1440)
    assert captured["r_display"] == (1920, 1200)


def test_optimize_reads_two_screen_and_fixed_from_config(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    cfg = tmp_path / "config.json"
    cfg.write_text(
        json.dumps(
            {
                "input": ["from_config.jpg"],
                "resolution": "1600x900",
                "two_screen": True,
                "fixed": True,
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)

    result = runner.invoke(cli.app, ["optimize", "--config", str(cfg)])

    assert result.exit_code == 0
    assert captured["two_screen"] is True
    assert captured["fixed"] is True


def test_optimize_cli_two_screen_and_fixed_override_config_false(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    cfg = tmp_path / "config.json"
    cfg.write_text(
        json.dumps(
            {
                "input": ["from_config.jpg"],
                "resolution": "1600x900",
                "two_screen": False,
                "fixed": False,
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)

    result = runner.invoke(
        cli.app,
        [
            "optimize",
            "--config",
            str(cfg),
            "--two-screen",
            "--fixed",
        ],
    )

    assert result.exit_code == 0
    assert captured["two_screen"] is True
    assert captured["fixed"] is True


def test_optimize_cli_no_flags_override_config_true(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    cfg = tmp_path / "config.json"
    cfg.write_text(
        json.dumps(
            {
                "input": ["from_config.jpg"],
                "resolution": "1600x900",
                "two_screen": True,
                "fixed": True,
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)

    result = runner.invoke(
        cli.app,
        [
            "optimize",
            "--config",
            str(cfg),
            "--no-two-screen",
            "--no-fixed",
        ],
    )

    assert result.exit_code == 0
    assert captured["two_screen"] is False
    assert captured["fixed"] is False


def test_optimize_rejects_invalid_bool_in_config(tmp_path, monkeypatch):
    runner = CliRunner()

    def fake_optimize_wallpapers(**kwargs):
        return [], []

    cfg = tmp_path / "config.json"
    cfg.write_text(
        json.dumps(
            {
                "input": ["from_config.jpg"],
                "resolution": "1600x900",
                "two_screen": "maybe",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)

    result = runner.invoke(cli.app, ["optimize", "--config", str(cfg)])

    assert result.exit_code == 2
    assert "invalid config bool for two_screen" in result.output

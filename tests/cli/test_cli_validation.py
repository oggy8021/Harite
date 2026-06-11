import pytest
import json
import re

from harite import cli
from harite.display_context import TwoScreenOptimizeContext
from harite.workspace import Display
from typer.testing import CliRunner


def _normalize_cli_output(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)


def _stub_dual_display_context() -> TwoScreenOptimizeContext:
    return TwoScreenOptimizeContext(
        displays=(
            Display(name="L", width=1920, height=1080, x_offset=0),
            Display(name="R", width=1920, height=1080, x_offset=1920),
        ),
        resolution=(3840, 1080),
        l_display=(1920, 1080),
        r_display=(1920, 1080),
    )


@pytest.fixture(autouse=True)
def _block_real_optimize_side_effects(monkeypatch):
    def fail_optimize_wallpapers(**_kwargs):
        raise AssertionError("test must stub cli.optimize_wallpapers before reaching real optimize execution")

    monkeypatch.setattr(cli, "optimize_wallpapers", fail_optimize_wallpapers)


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


def test_cli_help_excludes_removed_compute_placement_command():
    runner = CliRunner()

    result = runner.invoke(cli.app, ["--help"])
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 0
    assert "compute-placement" not in output


def test_optimize_help_reflects_current_surface() -> None:
    runner = CliRunner()

    result = runner.invoke(cli.app, ["optimize", "--help"])
    output = _normalize_cli_output(result.output)
    compact_output = " ".join(output.split())

    assert result.exit_code == 0
    assert "--settings-file" in output
    assert "--embed-position" in output
    assert "--scaling" not in output
    assert "left,right,top,bottom" in compact_output
    assert "その内側で" not in output
    assert "効きが強く" not in output
    assert "auto-detect" in compact_output


def test_optimize_reports_embed_overlap_error(tmp_path, monkeypatch):
    from harite.core import optimize_wallpapers as real_optimize_wallpapers

    monkeypatch.setattr(cli, "optimize_wallpapers", real_optimize_wallpapers)

    runner = CliRunner()
    img = tmp_path / "wide.jpg"
    from PIL import Image

    Image.new("RGB", (460, 360), (200, 50, 50)).save(img)

    result = runner.invoke(
        cli.app,
        [
            "optimize",
            "--input",
            str(img),
            "--resolution",
            "500x400",
            "--align",
            "right",
            "--valign",
            "bottom",
            "--margins",
            "0,0,0,40",
            "--embed-info",
            "params",
            "--embed-position",
            "right-bottom",
        ],
    )

    assert result.exit_code == 2
    assert "Embed position overlaps pasted image" in result.output
    assert "embed_position" in result.output


def test_format_placement_line_matches_cli_spec() -> None:
    from pathlib import Path

    from harite.core import PlacementResult

    line = cli.format_placement_line(
        PlacementResult(
            image_path=Path("C:/photos/a.jpg"),
            x=960,
            y=540,
            width=1920,
            height=1080,
            scale=1.0,
            posit="left",
        )
    )
    assert line == "a.jpg @ (960,540) 1920x1080 scale=1.0 posit=left"


def test_root_help_lists_typer_shell_completion_options() -> None:
    runner = CliRunner()

    result = runner.invoke(cli.app, ["--help"])
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 0
    assert "--install-completion" in output
    assert "--show-completion" in output


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


def test_optimize_rejects_invalid_embed_position_value_from_settings(tmp_path):
    runner = CliRunner()

    settings_file = tmp_path / "settings.json"
    settings_file.write_text(
        json.dumps(
            {
                "input": ["from_config.jpg"],
                "resolution": "1600x900",
                "embed_position": "middle",
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(cli.app, ["optimize", "--settings-file", str(settings_file)])

    assert result.exit_code == 2
    assert "--embed-position must be one of" in result.output
    assert "left-top" in result.output
    assert "right-bottom" in result.output


def test_optimize_rejects_invalid_background_color(tmp_path):
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
            "--background-color",
            "blue",
        ],
    )
    assert result.exit_code == 2
    assert "--background-color must be a hex RGB value" in result.output


def test_optimize_rejects_legacy_random_seed_option(tmp_path):
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
            "--random-seed",
            "42",
        ],
    )
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 2
    assert "no such option" in output.lower()
    assert "random-seed" in output


def test_optimize_rejects_directory_input(tmp_path):
    runner = CliRunner()
    input_dir = tmp_path / "images"
    input_dir.mkdir()

    result = runner.invoke(
        cli.app,
        [
            "optimize",
            "--input",
            str(input_dir),
            "--resolution",
            "100x100",
        ],
    )

    assert result.exit_code == 2
    assert f"optimize --input does not accept directories: {input_dir}" in _normalize_cli_output(result.output)


def test_optimize_uses_settings_for_required_values(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    settings_file = tmp_path / "settings.json"
    settings_file.write_text(
        json.dumps(
            {
                "input": ["from_config.jpg"],
                "resolution": "1600x900",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)

    result = runner.invoke(cli.app, ["optimize", "--settings-file", str(settings_file)])

    assert result.exit_code == 0
    assert captured["inputs"] == ["from_config.jpg"]
    assert captured["target_resolution"] == (1600, 900)


def test_optimize_cli_values_override_settings(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    settings_file = tmp_path / "settings.json"
    settings_file.write_text(
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
            "--settings-file",
            str(settings_file),
            "--input",
            "from_cli.jpg",
            "--resolution",
            "1920x1080",
        ],
    )

    assert result.exit_code == 0
    assert captured["inputs"] == ["from_cli.jpg"]
    assert captured["target_resolution"] == (1920, 1080)


def test_optimize_uses_only_first_two_cli_inputs(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    first = tmp_path / "first.jpg"
    second = tmp_path / "second.jpg"
    third = tmp_path / "third.jpg"
    for path in (first, second, third):
        path.write_bytes(b"x")

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)
    monkeypatch.setattr(
        "harite.optimize_settings.build_two_screen_optimize_context",
        _stub_dual_display_context,
    )

    result = runner.invoke(
        cli.app,
        [
            "optimize",
            "--input",
            f"{first},{second}",
            "--input",
            str(third),
            "--resolution",
            "1920x1080",
        ],
    )

    assert result.exit_code == 0
    assert captured["inputs"] == [str(first), str(second)]


def test_optimize_ignores_invalid_third_input_after_first_two(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    first = tmp_path / "first.jpg"
    second = tmp_path / "second.jpg"
    invalid_third = tmp_path / "third-dir"
    first.write_bytes(b"x")
    second.write_bytes(b"x")
    invalid_third.mkdir()

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)
    monkeypatch.setattr(
        "harite.optimize_settings.build_two_screen_optimize_context",
        _stub_dual_display_context,
    )

    result = runner.invoke(
        cli.app,
        [
            "optimize",
            "--input",
            str(first),
            "--input",
            str(second),
            "--input",
            str(invalid_third),
            "--resolution",
            "1920x1080",
        ],
    )

    assert result.exit_code == 0
    assert captured["inputs"] == [str(first), str(second)]


def test_optimize_expands_tilde_for_each_comma_separated_input(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    left = tmp_path / "left.jpg"
    right = tmp_path / "right.jpg"
    left.write_bytes(b"x")
    right.write_bytes(b"x")

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)
    monkeypatch.setattr(
        "harite.optimize_settings.build_two_screen_optimize_context",
        _stub_dual_display_context,
    )
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))

    result = runner.invoke(
        cli.app,
        [
            "optimize",
            "--input",
            f"~/{left.name},~/{right.name}",
            "--resolution",
            "1920x1080",
        ],
    )

    assert result.exit_code == 0
    assert captured["inputs"] == [str(left), str(right)]


def test_optimize_uses_settings_for_margins_and_displays(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    settings_file = tmp_path / "settings.json"
    settings_file.write_text(
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

    result = runner.invoke(cli.app, ["optimize", "--settings-file", str(settings_file)])

    assert result.exit_code == 0
    assert captured["margins"] == (1, 2, 3, 4)
    assert captured["l_display"] == (1920, 1080)
    assert captured["r_display"] == (1280, 1024)


def test_optimize_cli_values_override_settings_for_margins_and_displays(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    settings_file = tmp_path / "settings.json"
    settings_file.write_text(
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
            "--settings-file",
            str(settings_file),
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


def test_optimize_reads_two_screen_from_settings(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    settings_file = tmp_path / "settings.json"
    settings_file.write_text(
        json.dumps(
            {
                "input": ["from_config.jpg"],
                "resolution": "1600x900",
                "two_screen": True,
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)

    result = runner.invoke(cli.app, ["optimize", "--settings-file", str(settings_file)])

    assert result.exit_code == 0
    assert captured["two_screen"] is True


def test_optimize_cli_two_screen_overrides_settings_false(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    settings_file = tmp_path / "settings.json"
    settings_file.write_text(
        json.dumps(
            {
                "input": ["from_config.jpg"],
                "resolution": "1600x900",
                "two_screen": False,
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)

    result = runner.invoke(
        cli.app,
        [
            "optimize",
            "--settings-file",
            str(settings_file),
            "--two-screen",
        ],
    )

    assert result.exit_code == 0
    assert captured["two_screen"] is True


def test_optimize_cli_no_two_screen_rejects_dual_input(tmp_path, monkeypatch):
    runner = CliRunner()
    left = tmp_path / "left.jpg"
    right = tmp_path / "right.jpg"
    left.write_bytes(b"x")
    right.write_bytes(b"x")

    monkeypatch.setattr(cli, "optimize_wallpapers", lambda **_kwargs: ([], []))
    monkeypatch.setattr(
        "harite.optimize_settings.build_two_screen_optimize_context",
        lambda: None,
    )

    result = runner.invoke(
        cli.app,
        [
            "optimize",
            "--input",
            f"{left},{right}",
            "--resolution",
            "1600x900",
            "--no-two-screen",
        ],
    )

    assert result.exit_code == 2
    assert "two-screen mode" in result.output


def test_optimize_rejects_removed_fixed_flag(tmp_path):
    runner = CliRunner()

    img = tmp_path / "from_cli.jpg"
    img.write_bytes(b"x")

    result = runner.invoke(
        cli.app,
        [
            "optimize",
            "--input",
            str(img),
            "--resolution",
            "1600x900",
            "--fixed",
        ],
    )

    assert result.exit_code == 2
    output = _normalize_cli_output(result.output)
    assert "No such option" in output
    assert "--fixed" in output


def test_optimize_rejects_invalid_bool_in_settings(tmp_path, monkeypatch):
    runner = CliRunner()

    def fake_optimize_wallpapers(**kwargs):
        return [], []

    settings_file = tmp_path / "settings.json"
    settings_file.write_text(
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

    result = runner.invoke(cli.app, ["optimize", "--settings-file", str(settings_file)])

    assert result.exit_code == 2
    assert "invalid settings bool for two_screen" in result.output


def test_optimize_combined_two_screen_margins_displays(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    settings_file = tmp_path / "settings.json"
    settings_file.write_text(
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
            "--settings-file",
            str(settings_file),
            "--two-screen",
            "--margins",
            "10,20,30,40",
            "--l-display",
            "1920x1080",
            "--r-display",
            "1280x1024",
        ],
    )

    assert result.exit_code == 0
    assert captured["two_screen"] is True
    assert captured["margins"] == (10, 20, 30, 40)
    assert captured["l_display"] == (1920, 1080)
    assert captured["r_display"] == (1280, 1024)


def test_optimize_passes_embed_font_to_core(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    img = tmp_path / "a.jpg"
    from PIL import Image

    Image.new("RGB", (10, 10), (100, 100, 100)).save(img)
    font = tmp_path / "font.ttf"
    font.write_bytes(b"dummy")

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)

    result = runner.invoke(
        cli.app,
        [
            "optimize",
            "--input",
            str(img),
            "--resolution",
            "100x100",
            "--embed-info",
            "free",
            "--embed-text",
            "テスト",
            "--embed-font",
            str(font),
        ],
    )

    assert result.exit_code == 0
    assert captured["embed_font"] == str(font)


def test_optimize_uses_settings_for_align_and_valign_and_ignores_scaling(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    settings_file = tmp_path / "settings.json"
    settings_file.write_text(
        json.dumps(
            {
                "input": ["from_config.jpg"],
                "resolution": "1600x900",
                "scaling": "fill",
                "align": "right",
                "valign": "bottom",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)

    result = runner.invoke(cli.app, ["optimize", "--settings-file", str(settings_file)])

    assert result.exit_code == 0
    assert captured["scaling"] == "fit"
    assert captured["align"] == ("right", "right")
    assert captured["valign"] == ("bottom", "bottom")


def test_optimize_defaults_embed_position_to_right_bottom(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    img = tmp_path / "a.jpg"
    from PIL import Image

    Image.new("RGB", (10, 10), (100, 100, 100)).save(img)

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)

    result = runner.invoke(
        cli.app,
        [
            "optimize",
            "--input",
            str(img),
            "--resolution",
            "100x100",
        ],
    )

    assert result.exit_code == 0
    assert captured["embed_position"] == "right-bottom"


def test_optimize_mat14_scale_keys_can_come_from_settings(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    settings_file = tmp_path / "settings.json"
    settings_file.write_text(
        json.dumps(
            {
                "input": ["a.jpg"],
                "resolution": "100x100",
                "l_display_scale": 1.5,
                "r_display_scale": 2.0,
                "l_auto_display_scale": True,
                "r_auto_display_scale": False,
            }
        ),
        encoding="utf-8",
    )

    img = tmp_path / "a.jpg"
    from PIL import Image

    Image.new("RGB", (10, 10), (100, 100, 100)).save(img)
    settings_payload = json.loads(settings_file.read_text(encoding="utf-8"))
    settings_payload["input"] = [str(img)]
    settings_file.write_text(json.dumps(settings_payload), encoding="utf-8")

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)

    result = runner.invoke(cli.app, ["optimize", "--settings-file", str(settings_file)])

    assert result.exit_code == 0
    assert captured["l_display_scale"] == 1.5
    assert captured["r_display_scale"] == 2.0
    assert captured["l_auto_display_scale"] is True
    assert captured["r_auto_display_scale"] is False


def test_optimize_auto_display_values_can_come_from_settings(tmp_path, monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    settings_file = tmp_path / "settings.json"
    settings_file.write_text(
        json.dumps(
            {
                "input": ["left.jpg", "right.jpg"],
                "resolution": "auto",
                "two_screen": "auto",
                "l_display": "auto",
                "r_display": "auto",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)
    monkeypatch.setattr(
        "harite.optimize_settings.build_two_screen_optimize_context",
        lambda: TwoScreenOptimizeContext(
            displays=(
                Display(name="L", width=1920, height=1080, x_offset=0),
                Display(name="R", width=1280, height=1024, x_offset=1920),
            ),
            resolution=(3200, 1080),
            l_display=(1920, 1080),
            r_display=(1280, 1024),
        ),
    )

    result = runner.invoke(cli.app, ["optimize", "--settings-file", str(settings_file)])

    assert result.exit_code == 0
    assert captured["target_resolution"] == (3200, 1080)
    assert captured["two_screen"] is True
    assert captured["l_display"] == (1920, 1080)
    assert captured["r_display"] == (1280, 1024)


def test_optimize_two_screen_defaults_to_auto_when_unspecified_with_context(tmp_path, monkeypatch):
    """--two-screen 未指定時に2入力＋display context があれば自動で two-screen が有効になる (CLI1)。"""
    runner = CliRunner()
    captured = {}
    left = tmp_path / "left.jpg"
    right = tmp_path / "right.jpg"
    left.write_bytes(b"x")
    right.write_bytes(b"x")

    def fake_optimize_wallpapers(**kwargs):
        captured.update(kwargs)
        return [], []

    monkeypatch.setattr(cli, "optimize_wallpapers", fake_optimize_wallpapers)
    monkeypatch.setattr(
        "harite.optimize_settings.build_two_screen_optimize_context",
        lambda: TwoScreenOptimizeContext(
            displays=(
                Display(name="L", width=1920, height=1080, x_offset=0),
                Display(name="R", width=1280, height=1024, x_offset=1920),
            ),
            resolution=(3200, 1080),
            l_display=(1920, 1080),
            r_display=(1280, 1024),
        ),
    )

    result = runner.invoke(
        cli.app,
        ["optimize", "--input", str(left), "--input", str(right)],
    )

    assert result.exit_code == 0, result.output
    assert captured["two_screen"] is True
    assert captured["target_resolution"] == (3200, 1080)
    assert captured["l_display"] == (1920, 1080)
    assert captured["r_display"] == (1280, 1024)


def test_optimize_dual_input_errors_when_only_one_display_detected(tmp_path, monkeypatch):
    """MAT-21: 2 inputs + auto + no two-screen context → exit 2."""
    runner = CliRunner()
    left = tmp_path / "left.jpg"
    right = tmp_path / "right.jpg"
    left.write_bytes(b"x")
    right.write_bytes(b"x")

    monkeypatch.setattr(cli, "optimize_wallpapers", lambda **_kwargs: ([], []))
    monkeypatch.setattr(
        "harite.optimize_settings.build_two_screen_optimize_context",
        lambda: None,
    )

    result = runner.invoke(
        cli.app,
        ["optimize", "--input", str(left), "--input", str(right), "--resolution", "1920x1080"],
    )

    assert result.exit_code == 2, result.output
    assert "two detected displays" in result.output


def test_version_flag_exits_zero() -> None:
    """--version は exit 0 でバージョン文字列を出力する（CLI21）。"""
    runner = CliRunner()
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() != ""


def test_no_subcommand_exits_zero() -> None:
    """subcommand 未指定は help を表示して exit 0（CLI21）。"""
    runner = CliRunner()
    result = runner.invoke(cli.app, [])
    assert result.exit_code == 0

from pathlib import Path
import re

import pytest
from typer.testing import CliRunner

from harite import cli


def _strip_cli_output(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


@pytest.fixture(autouse=True)
def _block_real_apply_side_effects(monkeypatch):
    def fail_get_plugin(_name):
        raise AssertionError("test must stub cli.plugin_registry.get before reaching real apply execution")

    monkeypatch.setattr(cli.plugin_registry, "get", fail_get_plugin)


def test_apply_help_excludes_legacy_do_it_option() -> None:
    runner = CliRunner()

    result = runner.invoke(cli.app, ["apply", "--help"])
    output = _strip_cli_output(result.output).lower()
    compact_output = " ".join(output.split())

    assert result.exit_code == 0
    assert "--do-it" not in compact_output
    assert "dry-run" not in compact_output
    assert "settings-file" in compact_output
    assert "-c" in compact_output
    assert "--auto-split" not in compact_output
    assert "--left-file" not in compact_output
    assert "--right-file" not in compact_output
    assert "--per-monitor" not in compact_output
    assert "--plugin" not in compact_output
    assert ".harite-last-optimize.json" in compact_output


def test_apply_rejects_legacy_plugin_option(tmp_path) -> None:
    runner = CliRunner()
    image_path = tmp_path / "wall.jpg"
    image_path.write_bytes(b"x")

    result = runner.invoke(
        cli.app,
        ["apply", "--plugin", "windows", "--file", str(image_path)],
    )
    output = _strip_cli_output(result.output).lower()

    assert result.exit_code == 2
    assert "no such option" in output


def test_apply_rejects_legacy_do_it_option(tmp_path) -> None:
    runner = CliRunner()
    image_path = tmp_path / "wall.jpg"
    image_path.write_bytes(b"x")

    result = runner.invoke(
        cli.app,
        [
            "apply",
            "--file",
            str(image_path),
            "--do-it",
        ],
    )
    output = _strip_cli_output(result.output).lower()

    assert result.exit_code == 2
    assert "no such option" in output


def test_apply_uses_immediate_apply_mode(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    image_path = tmp_path / "wall.jpg"
    image_path.write_bytes(b"x")

    class FakePlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path_or_map):
            self.calls.append(path_or_map)
            return True

    fake_plugin = FakePlugin()
    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: fake_plugin)

    result = runner.invoke(
        cli.app,
        [
            "apply",
            "--file",
            str(image_path),
        ],
    )

    assert result.exit_code == 0
    assert fake_plugin.calls == [str(Path(image_path))]
    assert "applied wallpaper" in result.output.lower()
    assert "dry_run" not in result.output.lower()


def test_apply_uses_last_optimize_run_when_file_omitted(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    composite = output_dir / "harite_output_0001.jpg"
    composite.write_bytes(b"x")
    settings_path = tmp_path / "settings.json"
    settings_path.write_text(
        '{"plugin":"windows","apply_mode":"single-file"}',
        encoding="utf-8",
    )

    from harite.last_optimize_run import write_last_optimize_run

    write_last_optimize_run(output_dir=output_dir, composite_path=composite)

    class FakePlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path_or_map):
            self.calls.append(path_or_map)
            return True

    fake_plugin = FakePlugin()
    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: fake_plugin)

    result = runner.invoke(
        cli.app,
        [
            "apply",
            "-c",
            str(settings_path),
            "-o",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert fake_plugin.calls == [str(composite.resolve())]


def test_apply_without_file_or_last_run_exits_code_2(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    monkeypatch.setattr(
        "harite.cli.default_last_optimize_search_dirs",
        lambda **_kwargs: [tmp_path / "missing"],
    )

    result = runner.invoke(cli.app, ["apply"])

    assert result.exit_code == 2
    assert "no last optimize run found" in result.output.lower()


def test_apply_plugin_returns_false_exits_code_3(tmp_path, monkeypatch) -> None:
    """plugin が False を返した場合は終了コード 3（CLI11）。"""
    runner = CliRunner()
    image_path = tmp_path / "wall.jpg"
    image_path.write_bytes(b"x")

    class FailingPlugin:
        def apply(self, path_or_map):
            return False

    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: FailingPlugin())

    result = runner.invoke(
        cli.app,
        ["apply", "--file", str(image_path)],
    )

    assert result.exit_code == 3
    assert "failed to apply wallpaper" in result.output.lower()
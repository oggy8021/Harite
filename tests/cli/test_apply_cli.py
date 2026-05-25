from pathlib import Path

import pytest
from typer.testing import CliRunner

from harite import cli


@pytest.fixture(autouse=True)
def _block_real_apply_side_effects(monkeypatch):
    def fail_get_plugin(_name):
        raise AssertionError("test must stub cli.plugin_registry.get before reaching real apply execution")

    monkeypatch.setattr(cli.plugin_registry, "get", fail_get_plugin)


def test_apply_help_excludes_legacy_do_it_option() -> None:
    runner = CliRunner()

    result = runner.invoke(cli.app, ["apply", "--help"])
    output = result.output.lower()

    assert result.exit_code == 0
    assert "--do-it" not in output
    assert "dry-run" not in output


def test_apply_rejects_legacy_do_it_option(tmp_path) -> None:
    runner = CliRunner()
    image_path = tmp_path / "wall.jpg"
    image_path.write_bytes(b"x")

    result = runner.invoke(
        cli.app,
        [
            "apply",
            "--plugin",
            "windows",
            "--file",
            str(image_path),
            "--do-it",
        ],
    )
    output = result.output.lower()

    assert result.exit_code == 2
    assert "no such option" in output
    assert "do-it" in output


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
            "--plugin",
            "windows",
            "--file",
            str(image_path),
        ],
    )

    assert result.exit_code == 0
    assert fake_plugin.calls == [str(Path(image_path))]
    assert "applied wallpaper" in result.output.lower()
    assert "dry_run" not in result.output.lower()
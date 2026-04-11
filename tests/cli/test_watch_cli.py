import pytest
from typer.testing import CliRunner

from harite import cli


def _require_watch_command(runner: CliRunner) -> None:
    result = runner.invoke(cli.app, ["watch", "--help"])
    if result.exit_code != 0 and "No such command 'watch'" in result.output:
        pytest.skip("watch command is not implemented yet")


def test_watch_requires_input_option() -> None:
    runner = CliRunner()
    _require_watch_command(runner)

    result = runner.invoke(cli.app, ["watch", "--interval-sec", "1"])

    assert result.exit_code == 2
    assert "--input" in result.output


def test_watch_requires_interval_option() -> None:
    runner = CliRunner()
    _require_watch_command(runner)

    result = runner.invoke(cli.app, ["watch", "--input", "."])

    assert result.exit_code == 2
    assert "--interval-sec" in result.output


def test_watch_rejects_interval_less_than_one(tmp_path) -> None:
    runner = CliRunner()
    _require_watch_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()

    result = runner.invoke(
        cli.app,
        [
            "watch",
            "--input",
            str(img_dir),
            "--interval-sec",
            "0",
            "--iterations",
            "1",
        ],
    )

    assert result.exit_code == 2
    assert "interval" in result.output.lower()


def test_watch_help_includes_dry_run_and_do_it() -> None:
    runner = CliRunner()
    _require_watch_command(runner)

    result = runner.invoke(cli.app, ["watch", "--help"])

    assert result.exit_code == 0
    assert "--dry-run" in result.output
    assert "--do-it" in result.output

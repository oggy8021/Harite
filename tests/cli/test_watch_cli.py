import pytest
import re
from typer.testing import CliRunner

from harite import cli


def _normalize_cli_output(text: str) -> str:
    # Remove ANSI escape sequences emitted by rich/typer in CI terminals.
    cleaned = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)
    return cleaned.lower()


def _require_watch_command(runner: CliRunner) -> None:
    result = runner.invoke(cli.app, ["watch", "--help"])
    if result.exit_code != 0 and "No such command 'watch'" in result.output:
        pytest.skip("watch command is not implemented yet")


def test_watch_requires_input_option() -> None:
    runner = CliRunner()
    _require_watch_command(runner)

    result = runner.invoke(cli.app, ["watch", "--interval-sec", "1"])
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 2
    assert "missing option" in output
    assert "input" in output


def test_watch_requires_interval_option() -> None:
    runner = CliRunner()
    _require_watch_command(runner)

    result = runner.invoke(cli.app, ["watch", "--input", "."])
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 2
    assert "missing option" in output
    assert "interval" in output


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
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 0
    assert "dry-run" in output
    assert "do-it" in output

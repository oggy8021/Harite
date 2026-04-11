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


def test_watch_runs_iterations_and_reports_completion(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_watch_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")

    captured = {}

    def fake_run_watch_cycles(*, images, mode, interval_sec, iterations, on_cycle, sleep_fn=None):
        captured["images"] = images
        captured["mode"] = mode
        captured["interval_sec"] = interval_sec
        captured["iterations"] = iterations
        on_cycle(images[0], 0)
        return 1

    monkeypatch.setattr(cli, "run_watch_cycles", fake_run_watch_cycles)

    result = runner.invoke(
        cli.app,
        [
            "watch",
            "--input",
            str(img_dir),
            "--interval-sec",
            "1",
            "--iterations",
            "1",
        ],
    )
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 0
    assert captured["mode"] == "sequential"
    assert captured["interval_sec"] == 1
    assert captured["iterations"] == 1
    assert len(captured["images"]) == 1
    assert "watch completed cycles=1" in output


def test_watch_handles_keyboard_interrupt_as_normal_exit(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_watch_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")

    def fake_run_watch_cycles(*args, **kwargs):
        raise KeyboardInterrupt()

    monkeypatch.setattr(cli, "run_watch_cycles", fake_run_watch_cycles)

    result = runner.invoke(
        cli.app,
        ["watch", "--input", str(img_dir), "--interval-sec", "1", "--iterations", "1"],
    )
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 0
    assert "watch interrupted by user" in output

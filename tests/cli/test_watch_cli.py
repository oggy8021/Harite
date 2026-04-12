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
    assert "log-level" in output


def test_watch_rejects_unknown_log_level(tmp_path) -> None:
    runner = CliRunner()
    _require_watch_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")

    result = runner.invoke(
        cli.app,
        [
            "watch",
            "--input",
            str(img_dir),
            "--interval-sec",
            "1",
            "--log-level",
            "verbose",
            "--iterations",
            "1",
        ],
    )
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 2
    assert "--log-level must be one of: normal, detail" in output


def test_watch_runs_iterations_and_reports_completion(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_watch_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")

    captured = {}

    def fake_run_watch_cycles(
        *,
        images,
        mode,
        interval_sec,
        iterations,
        on_cycle,
        sleep_fn=None,
    ):
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
    assert "dry_run_cycles=1" in output


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


def test_watch_dry_run_does_not_resolve_plugin(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_watch_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")

    def fake_get_plugin(_name):
        raise AssertionError("plugin lookup should not happen in dry-run")

    monkeypatch.setattr(cli.plugin_registry, "get", fake_get_plugin)

    def fake_run_watch_cycles(
        *,
        images,
        mode,
        interval_sec,
        iterations,
        on_cycle,
        sleep_fn=None,
    ):
        on_cycle(images[0], 0)
        return 1

    monkeypatch.setattr(cli, "run_watch_cycles", fake_run_watch_cycles)

    result = runner.invoke(
        cli.app,
        ["watch", "--input", str(img_dir), "--interval-sec", "1", "--iterations", "1"],
    )
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 0
    assert "dry_run=true" in output


def test_watch_do_it_applies_and_continues_on_failure(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_watch_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")
    (img_dir / "b.jpg").write_bytes(b"x")

    class FakePlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path_or_map, dry_run=False):
            self.calls.append((path_or_map, dry_run))
            return len(self.calls) != 1

    fake_plugin = FakePlugin()

    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: fake_plugin)

    def fake_run_watch_cycles(
        *,
        images,
        mode,
        interval_sec,
        iterations,
        on_cycle,
        sleep_fn=None,
    ):
        on_cycle(images[0], 0)
        on_cycle(images[1], 1)
        return 2

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
            "2",
            "--log-level",
            "detail",
            "--do-it",
            "--plugin",
            "windows",
        ],
    )
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 0
    assert len(fake_plugin.calls) == 2
    assert fake_plugin.calls[0][1] is False
    assert fake_plugin.calls[1][1] is False
    assert "apply=failed" in output
    assert "reason=plugin-returned-false" in output
    assert "apply=ok" in output
    assert "watch completed cycles=2" in output
    assert "apply_ok=1" in output
    assert "apply_failed=1" in output
    assert "apply_error=0" in output
    assert "apply_failed_total=1" in output


def test_watch_normal_log_level_suppresses_success_cycle_line(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_watch_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")

    class FakePlugin:
        def apply(self, _path_or_map, dry_run=False):
            assert dry_run is False
            return True

    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: FakePlugin())

    def fake_run_watch_cycles(
        *,
        images,
        mode,
        interval_sec,
        iterations,
        on_cycle,
        sleep_fn=None,
    ):
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
            "--log-level",
            "normal",
            "--do-it",
            "--plugin",
            "windows",
        ],
    )
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 0
    assert "apply=ok" not in output
    assert "watch completed cycles=1" in output


def test_watch_detail_log_level_emits_dry_run_cycle_line(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_watch_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")

    def fake_run_watch_cycles(
        *,
        images,
        mode,
        interval_sec,
        iterations,
        on_cycle,
        sleep_fn=None,
    ):
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
            "--log-level",
            "detail",
        ],
    )
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 0
    assert "watch cycle=1" in output
    assert "dry_run=true" in output


def test_watch_do_it_exception_is_reported_and_counted(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_watch_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")

    class FakePlugin:
        def apply(self, _path_or_map, dry_run=False):
            assert dry_run is False
            raise RuntimeError("boom")

    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: FakePlugin())

    def fake_run_watch_cycles(
        *,
        images,
        mode,
        interval_sec,
        iterations,
        on_cycle,
        sleep_fn=None,
    ):
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
            "--do-it",
            "--plugin",
            "windows",
        ],
    )
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 0
    assert "apply=error" in output
    assert "reason=plugin-exception" in output
    assert "error_type=runtimeerror" in output
    assert "watch completed cycles=1" in output
    assert "apply_ok=0" in output
    assert "apply_failed=0" in output
    assert "apply_error=1" in output
    assert "apply_failed_total=1" in output

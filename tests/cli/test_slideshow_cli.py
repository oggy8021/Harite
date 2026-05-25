import pytest
import re
from typer.testing import CliRunner

from harite import cli


def _strip_cli_output(text: str) -> str:
    # Remove ANSI escape sequences emitted by rich/typer in CI terminals.
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)


def _normalize_cli_output(text: str) -> str:
    return _strip_cli_output(text).lower()


def _require_slideshow_command(runner: CliRunner) -> None:
    result = runner.invoke(cli.app, ["slideshow", "--help"])
    if result.exit_code != 0 and "No such command 'slideshow'" in result.output:
        pytest.skip("slideshow command is not implemented yet")


@pytest.fixture(autouse=True)
def _block_real_slideshow_side_effects(monkeypatch):
    def fail_run_slideshow_cycles(*_args, **_kwargs):
        raise AssertionError("test must stub cli.run_slideshow_cycles before reaching real slideshow loop")

    def fail_get_plugin(_name):
        raise AssertionError("test must stub cli.plugin_registry.get before reaching real slideshow apply")

    monkeypatch.setattr(cli, "run_slideshow_cycles", fail_run_slideshow_cycles)
    monkeypatch.setattr(cli.plugin_registry, "get", fail_get_plugin)


def test_slideshow_requires_input_option() -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    result = runner.invoke(cli.app, ["slideshow", "--interval-sec", "1"])
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 2
    assert "missing option" in output
    assert "input" in output


def test_slideshow_requires_interval_option() -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    result = runner.invoke(cli.app, ["slideshow", "--input", "."])
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 2
    assert "missing option" in output
    assert "interval" in output


def test_slideshow_rejects_interval_less_than_one(tmp_path) -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()

    result = runner.invoke(
        cli.app,
        [
            "slideshow",
            "--input",
            str(img_dir),
            "--interval-sec",
            "0",
        ],
    )

    assert result.exit_code == 2
    assert "interval" in result.output.lower()


def test_slideshow_help_includes_mode_and_excludes_legacy_options() -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    result = runner.invoke(cli.app, ["slideshow", "--help"])
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 0
    assert "mode" in output
    assert "dry-run" not in output
    assert "do-it" not in output
    assert "log-level" not in output
    assert "iterations" not in output


def test_slideshow_rejects_legacy_do_it_option(tmp_path) -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")

    result = runner.invoke(
        cli.app,
        [
            "slideshow",
            "--input",
            str(img_dir),
            "--interval-sec",
            "1",
            "--do-it",
        ],
    )
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 2
    assert "no such option" in output
    assert "do-it" in output


def test_slideshow_rejects_legacy_log_level_option(tmp_path) -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")

    result = runner.invoke(
        cli.app,
        [
            "slideshow",
            "--input",
            str(img_dir),
            "--interval-sec",
            "1",
            "--log-level",
            "detail",
        ],
    )
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 2
    assert "no such option" in output
    assert "log-level" in output


def test_slideshow_rejects_legacy_iterations_option(tmp_path) -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")

    result = runner.invoke(
        cli.app,
        [
            "slideshow",
            "--input",
            str(img_dir),
            "--interval-sec",
            "1",
            "--iterations",
            "1",
        ],
    )
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 2
    assert "no such option" in output
    assert "iterations" in output


def test_slideshow_runs_and_reports_completion(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")

    class FakePlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path_or_map):
            self.calls.append(path_or_map)
            return True

    fake_plugin = FakePlugin()
    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: fake_plugin)

    captured = {}

    def fake_run_slideshow_cycles(
        *,
        images,
        mode,
        interval_sec,
        on_cycle,
        sleep_fn=None,
    ):
        captured["images"] = images
        captured["mode"] = mode
        captured["interval_sec"] = interval_sec
        on_cycle(images[0], 0)
        return 1

    monkeypatch.setattr(cli, "run_slideshow_cycles", fake_run_slideshow_cycles)

    result = runner.invoke(
        cli.app,
        [
            "slideshow",
            "--input",
            str(img_dir),
            "--interval-sec",
            "1",
        ],
    )
    output = _normalize_cli_output(result.output)
    raw_output = _strip_cli_output(result.output)

    assert result.exit_code == 0
    assert captured["mode"] == "sequential"
    assert captured["interval_sec"] == 1
    assert len(captured["images"]) == 1
    assert fake_plugin.calls == [str(img_dir / "a.jpg")]
    assert "log_level" not in output
    assert "iterations" not in output
    assert "Slideshow completed cycles=1" in raw_output
    assert "apply_ok=1" in output
    assert "dry_run" not in output


def test_slideshow_handles_keyboard_interrupt_as_normal_exit(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")

    def fake_run_slideshow_cycles(*args, **kwargs):
        raise KeyboardInterrupt()

    class FakePlugin:
        def apply(self, _path_or_map):
            return True

    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: FakePlugin())
    monkeypatch.setattr(cli, "run_slideshow_cycles", fake_run_slideshow_cycles)

    result = runner.invoke(
        cli.app,
        ["slideshow", "--input", str(img_dir), "--interval-sec", "1"],
    )
    raw_output = _strip_cli_output(result.output)

    assert result.exit_code == 0
    assert "Slideshow interrupted by user" in raw_output


def test_slideshow_resolves_plugin_and_applies_without_do_it_option(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")

    plugin_requested = []

    class FakePlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path_or_map):
            self.calls.append(path_or_map)
            return True

    fake_plugin = FakePlugin()

    def fake_get_plugin(name):
        plugin_requested.append(name)
        return fake_plugin

    monkeypatch.setattr(cli.plugin_registry, "get", fake_get_plugin)

    def fake_run_slideshow_cycles(
        *,
        images,
        mode,
        interval_sec,
        on_cycle,
        sleep_fn=None,
    ):
        on_cycle(images[0], 0)
        return 1

    monkeypatch.setattr(cli, "run_slideshow_cycles", fake_run_slideshow_cycles)

    result = runner.invoke(
        cli.app,
        ["slideshow", "--input", str(img_dir), "--interval-sec", "1"],
    )
    output = _normalize_cli_output(result.output)
    raw_output = _strip_cli_output(result.output)

    assert result.exit_code == 0
    assert plugin_requested
    assert fake_plugin.calls == [str(img_dir / "a.jpg")]
    assert "log_level" not in output
    assert "iterations" not in output
    assert "dry_run" not in output
    assert "slideshow cycle=" not in output
    assert "Slideshow cycle=" not in raw_output


def test_slideshow_applies_and_continues_on_failure(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")
    (img_dir / "b.jpg").write_bytes(b"x")

    class FakePlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path_or_map):
            self.calls.append(path_or_map)
            return len(self.calls) != 1

    fake_plugin = FakePlugin()

    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: fake_plugin)

    def fake_run_slideshow_cycles(
        *,
        images,
        mode,
        interval_sec,
        on_cycle,
        sleep_fn=None,
    ):
        on_cycle(images[0], 0)
        on_cycle(images[1], 1)
        return 2

    monkeypatch.setattr(cli, "run_slideshow_cycles", fake_run_slideshow_cycles)

    result = runner.invoke(
        cli.app,
        [
            "slideshow",
            "--input",
            str(img_dir),
            "--interval-sec",
            "1",
            "--plugin",
            "windows",
        ],
    )
    output = _normalize_cli_output(result.output)
    raw_output = _strip_cli_output(result.output)

    assert result.exit_code == 0
    assert fake_plugin.calls == [str(img_dir / "a.jpg"), str(img_dir / "b.jpg")]
    assert "apply=failed" in output
    assert "reason=plugin-returned-false" in output
    assert "apply=ok" not in output
    assert "Slideshow cycle=1" in raw_output
    assert "Slideshow cycle=2" not in raw_output
    assert "log_level" not in output
    assert "iterations" not in output
    assert "Slideshow completed cycles=2" in raw_output
    assert "apply_ok=1" in output
    assert "apply_failed=1" in output
    assert "apply_error=0" in output
    assert "apply_failed_total=1" in output


def test_slideshow_success_does_not_emit_success_cycle_line(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")

    class FakePlugin:
        def apply(self, _path_or_map):
            return True

    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: FakePlugin())

    def fake_run_slideshow_cycles(
        *,
        images,
        mode,
        interval_sec,
        on_cycle,
        sleep_fn=None,
    ):
        on_cycle(images[0], 0)
        return 1

    monkeypatch.setattr(cli, "run_slideshow_cycles", fake_run_slideshow_cycles)

    result = runner.invoke(
        cli.app,
        [
            "slideshow",
            "--input",
            str(img_dir),
            "--interval-sec",
            "1",
            "--plugin",
            "windows",
        ],
    )
    output = _normalize_cli_output(result.output)
    raw_output = _strip_cli_output(result.output)

    assert result.exit_code == 0
    assert "apply=ok" not in output
    assert "Slideshow cycle=" not in raw_output
    assert "log_level" not in output
    assert "iterations" not in output
    assert "Slideshow completed cycles=1" in raw_output


def test_slideshow_default_run_does_not_emit_dry_run_markers(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")

    class FakePlugin:
        def apply(self, _path_or_map):
            return True

    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: FakePlugin())

    def fake_run_slideshow_cycles(
        *,
        images,
        mode,
        interval_sec,
        on_cycle,
        sleep_fn=None,
    ):
        on_cycle(images[0], 0)
        return 1

    monkeypatch.setattr(cli, "run_slideshow_cycles", fake_run_slideshow_cycles)

    result = runner.invoke(
        cli.app,
        [
            "slideshow",
            "--input",
            str(img_dir),
            "--interval-sec",
            "1",
        ],
    )
    output = _normalize_cli_output(result.output)
    raw_output = _strip_cli_output(result.output)

    assert result.exit_code == 0
    assert "Slideshow cycle=" not in raw_output
    assert "Slideshow completed cycles=1" in raw_output
    assert "slideshow cycle=" not in output
    assert "slideshow completed cycles=1" in output
    assert "dry_run" not in output
    assert "log_level" not in output
    assert "iterations" not in output


def test_slideshow_exception_is_reported_and_counted(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.jpg").write_bytes(b"x")

    class FakePlugin:
        def apply(self, _path_or_map):
            raise RuntimeError("boom")

    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: FakePlugin())

    def fake_run_slideshow_cycles(
        *,
        images,
        mode,
        interval_sec,
        on_cycle,
        sleep_fn=None,
    ):
        on_cycle(images[0], 0)
        return 1

    monkeypatch.setattr(cli, "run_slideshow_cycles", fake_run_slideshow_cycles)

    result = runner.invoke(
        cli.app,
        [
            "slideshow",
            "--input",
            str(img_dir),
            "--interval-sec",
            "1",
            "--plugin",
            "windows",
        ],
    )
    output = _normalize_cli_output(result.output)
    raw_output = _strip_cli_output(result.output)

    assert result.exit_code == 0
    assert "apply=error" in output
    assert "reason=plugin-exception" in output
    assert "error_type=runtimeerror" in output
    assert "Slideshow completed cycles=1" in raw_output
    assert "apply_ok=0" in output
    assert "apply_failed=0" in output
    assert "apply_error=1" in output
    assert "apply_failed_total=1" in output
    assert "log_level" not in output
    assert "iterations" not in output

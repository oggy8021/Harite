import json
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


def _fake_optimize_cycle_runner(captured: dict, *, success: bool = True, error: str | None = None):
    def fake_run_slideshow_optimize_cycles(
        *,
        input_dirs,
        mode,
        interval_sec,
        config,
        controller,
        plugin_impl,
        on_cycle,
        sleep_fn=None,
    ):
        captured["input_dirs"] = list(input_dirs)
        captured["mode"] = mode
        captured["interval_sec"] = interval_sec
        on_cycle("optimized-target", 0, success, error)
        return 1

    return fake_run_slideshow_optimize_cycles


@pytest.fixture(autouse=True)
def _block_real_slideshow_side_effects(monkeypatch):
    def fail_run_slideshow_optimize_cycles(*_args, **_kwargs):
        raise AssertionError(
            "test must stub cli.run_slideshow_optimize_cycles before reaching real slideshow loop"
        )

    def fail_get_plugin(_name):
        raise AssertionError("test must stub cli.plugin_registry.get before reaching real slideshow apply")

    monkeypatch.setattr(cli, "run_slideshow_optimize_cycles", fail_run_slideshow_optimize_cycles)
    monkeypatch.setattr(cli.plugin_registry, "get", fail_get_plugin)


def test_slideshow_requires_input_option() -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    result = runner.invoke(cli.app, ["slideshow", "--interval-sec", "1"])
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 2
    assert "--input is required" in output


def test_slideshow_requires_interval_option() -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    result = runner.invoke(cli.app, ["slideshow", "--input", "."])
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 2
    assert "--interval-sec is required" in output


def test_slideshow_uses_only_first_two_input_directories(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    extra_dir = tmp_path / "extra"
    for directory in (left_dir, right_dir, extra_dir):
        directory.mkdir()

    captured = {}

    def fake_collect_slideshow_input_images(input_dirs):
        return [input_dirs[0] / "a.jpg"]

    class FakePlugin:
        def apply(self, _path_or_map):
            return True

    monkeypatch.setattr(cli, "collect_slideshow_input_images", fake_collect_slideshow_input_images)
    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: FakePlugin())
    monkeypatch.setattr(
        cli,
        "run_slideshow_optimize_cycles",
        _fake_optimize_cycle_runner(captured),
    )
    monkeypatch.setattr(cli, "validate_dual_source_slideshow", lambda _name: None)

    result = runner.invoke(
        cli.app,
        [
            "slideshow",
            "--input",
            str(left_dir),
            "--input",
            str(right_dir),
            "--input",
            str(extra_dir),
            "--interval-sec",
            "1",
        ],
    )

    assert result.exit_code == 0
    assert captured["input_dirs"] == [left_dir, right_dir]


def test_slideshow_ignores_invalid_third_directory_after_first_two(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    invalid_third = tmp_path / "missing"
    for directory in (left_dir, right_dir):
        directory.mkdir()

    captured = {}

    def fake_collect_slideshow_input_images(input_dirs):
        return [input_dirs[0] / "a.jpg"]

    class FakePlugin:
        def apply(self, _path_or_map):
            return True

    monkeypatch.setattr(cli, "collect_slideshow_input_images", fake_collect_slideshow_input_images)
    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: FakePlugin())
    monkeypatch.setattr(
        cli,
        "run_slideshow_optimize_cycles",
        _fake_optimize_cycle_runner(captured),
    )
    monkeypatch.setattr(cli, "validate_dual_source_slideshow", lambda _name: None)

    result = runner.invoke(
        cli.app,
        [
            "slideshow",
            "--input",
            str(left_dir),
            "--input",
            str(right_dir),
            "--input",
            str(invalid_third),
            "--interval-sec",
            "1",
        ],
    )

    assert result.exit_code == 0
    assert captured["input_dirs"] == [left_dir, right_dir]


def test_slideshow_uses_only_first_two_directories_from_comma_separated_input(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    extra_dir = tmp_path / "extra"
    for directory in (left_dir, right_dir, extra_dir):
        directory.mkdir()

    captured = {}

    def fake_collect_slideshow_input_images(input_dirs):
        return [input_dirs[0] / "a.jpg"]

    class FakePlugin:
        def apply(self, _path_or_map):
            return True

    monkeypatch.setattr(cli, "collect_slideshow_input_images", fake_collect_slideshow_input_images)
    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: FakePlugin())
    monkeypatch.setattr(
        cli,
        "run_slideshow_optimize_cycles",
        _fake_optimize_cycle_runner(captured),
    )
    monkeypatch.setattr(cli, "validate_dual_source_slideshow", lambda _name: None)

    result = runner.invoke(
        cli.app,
        [
            "slideshow",
            "--input",
            f"{left_dir},{right_dir},{extra_dir}",
            "--interval-sec",
            "1",
        ],
    )

    assert result.exit_code == 0
    assert captured["input_dirs"] == [left_dir, right_dir]


def test_slideshow_expands_tilde_for_each_comma_separated_input(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    left_dir.mkdir()
    right_dir.mkdir()

    captured = {}

    def fake_collect_slideshow_input_images(input_dirs):
        return [input_dirs[0] / "a.jpg"]

    class FakePlugin:
        def apply(self, _path_or_map):
            return True

    monkeypatch.setattr(cli, "collect_slideshow_input_images", fake_collect_slideshow_input_images)
    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: FakePlugin())
    monkeypatch.setattr(
        cli,
        "run_slideshow_optimize_cycles",
        _fake_optimize_cycle_runner(captured),
    )
    monkeypatch.setattr(cli, "validate_dual_source_slideshow", lambda _name: None)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))

    result = runner.invoke(
        cli.app,
        [
            "slideshow",
            "--input",
            "~/left,~/right",
            "--interval-sec",
            "1",
        ],
    )

    assert result.exit_code == 0
    assert captured["input_dirs"] == [left_dir, right_dir]


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


def test_slideshow_help_describes_comma_separated_or_repeated_input() -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    result = runner.invoke(cli.app, ["slideshow", "--help"])
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 0
    assert "comma-separated" in output
    assert "repeat --input" in output


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
        def apply(self, _path_or_map):
            return True

    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: FakePlugin())

    captured = {}

    monkeypatch.setattr(
        cli,
        "run_slideshow_optimize_cycles",
        _fake_optimize_cycle_runner(captured),
    )

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
    assert captured["input_dirs"] == [img_dir]
    assert "optimize=yes" in output
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

    def fake_run_slideshow_optimize_cycles(*_args, **_kwargs):
        raise KeyboardInterrupt()

    class FakePlugin:
        def apply(self, _path_or_map):
            return True

    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: FakePlugin())
    monkeypatch.setattr(cli, "run_slideshow_optimize_cycles", fake_run_slideshow_optimize_cycles)

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
        def apply(self, _path_or_map):
            return True

    def fake_get_plugin(name):
        plugin_requested.append(name)
        return FakePlugin()

    monkeypatch.setattr(cli.plugin_registry, "get", fake_get_plugin)
    monkeypatch.setattr(cli, "run_slideshow_optimize_cycles", _fake_optimize_cycle_runner({}))

    result = runner.invoke(
        cli.app,
        ["slideshow", "--input", str(img_dir), "--interval-sec", "1"],
    )
    output = _normalize_cli_output(result.output)
    raw_output = _strip_cli_output(result.output)

    assert result.exit_code == 0
    assert plugin_requested
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
        def apply(self, _path_or_map):
            return True

    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: FakePlugin())

    def fake_run_slideshow_optimize_cycles(
        *,
        input_dirs,
        mode,
        interval_sec,
        config,
        controller,
        plugin_impl,
        on_cycle,
        sleep_fn=None,
    ):
        on_cycle("first", 0, False, "plugin-returned-false")
        on_cycle("second", 1, True, None)
        return 2

    monkeypatch.setattr(cli, "run_slideshow_optimize_cycles", fake_run_slideshow_optimize_cycles)

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
    monkeypatch.setattr(cli, "run_slideshow_optimize_cycles", _fake_optimize_cycle_runner({}))

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
    monkeypatch.setattr(cli, "run_slideshow_optimize_cycles", _fake_optimize_cycle_runner({}))

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
            return True

    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: FakePlugin())
    monkeypatch.setattr(
        cli,
        "run_slideshow_optimize_cycles",
        _fake_optimize_cycle_runner({}, success=False, error="slideshow single-file apply error: boom"),
    )

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
    assert "reason=optimize-or-apply-exception" in output
    assert "boom" in output
    assert "Slideshow completed cycles=1" in raw_output
    assert "apply_ok=0" in output
    assert "apply_failed=0" in output
    assert "apply_error=1" in output
    assert "apply_failed_total=1" in output
    assert "log_level" not in output
    assert "iterations" not in output


def test_slideshow_help_includes_settings_file_option() -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    result = runner.invoke(cli.app, ["slideshow", "--help"])
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 0
    assert "--settings-file" in output


def test_slideshow_reads_settings_srcdir_interval_mode_and_plugin(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "l.jpg").write_bytes(b"jpeg")
    (right_dir / "r.jpg").write_bytes(b"jpeg")

    settings_file = tmp_path / "harite-settings.json"
    settings_file.write_text(
        json.dumps(
            {
                "slideshow_srcdir_l": str(left_dir),
                "slideshow_srcdir_r": str(right_dir),
                "slideshow_interval_seconds": 120,
                "slideshow_mode": "random",
                "plugin": "windows",
            }
        ),
        encoding="utf-8",
    )

    captured = {}

    class FakePlugin:
        def apply(self, _path_or_map):
            return True

    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: FakePlugin())
    monkeypatch.setattr(
        cli,
        "run_slideshow_optimize_cycles",
        _fake_optimize_cycle_runner(captured),
    )
    monkeypatch.setattr(cli, "validate_dual_source_slideshow", lambda _name: None)

    result = runner.invoke(cli.app, ["slideshow", "--settings-file", str(settings_file)])
    output = _strip_cli_output(result.output)

    assert result.exit_code == 0
    assert str(left_dir) in output
    assert str(right_dir) in output
    assert "sources=dual" in output
    assert "interval_sec=120" in output
    assert "mode=random" in output
    assert "plugin=windows" in output
    assert captured["mode"] == "random"
    assert captured["interval_sec"] == 120
    assert captured["input_dirs"] == [left_dir, right_dir]


def test_slideshow_cli_overrides_settings(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    left_dir = tmp_path / "left"
    cli_dir = tmp_path / "cli-only"
    left_dir.mkdir()
    cli_dir.mkdir()
    (cli_dir / "c.jpg").write_bytes(b"jpeg")

    settings_file = tmp_path / "harite-settings.json"
    settings_file.write_text(
        json.dumps(
            {
                "slideshow_srcdir_l": str(left_dir),
                "slideshow_interval_seconds": 600,
                "slideshow_mode": "random",
                "plugin": "windows",
            }
        ),
        encoding="utf-8",
    )

    captured = {}

    class FakePlugin:
        def apply(self, _path_or_map):
            return True

    monkeypatch.setattr(cli.plugin_registry, "get", lambda _name: FakePlugin())
    monkeypatch.setattr(
        cli,
        "run_slideshow_optimize_cycles",
        _fake_optimize_cycle_runner(captured),
    )

    result = runner.invoke(
        cli.app,
        [
            "slideshow",
            "--settings-file",
            str(settings_file),
            "--input",
            str(cli_dir),
            "--interval-sec",
            "5",
            "--mode",
            "sequential",
            "--plugin",
            "linux",
        ],
    )
    output = _strip_cli_output(result.output)

    assert result.exit_code == 0
    assert f"input={cli_dir}" in output
    assert "sources=single" in output
    assert "interval_sec=5" in output
    assert "mode=sequential" in output
    assert "plugin=linux" in output
    assert captured["input_dirs"] == [cli_dir]
    assert captured["mode"] == "sequential"
    assert captured["interval_sec"] == 5


def test_slideshow_settings_file_load_error(tmp_path) -> None:
    runner = CliRunner()
    _require_slideshow_command(runner)

    missing = tmp_path / "missing.json"
    result = runner.invoke(cli.app, ["slideshow", "--settings-file", str(missing)])
    output = _normalize_cli_output(result.output)

    assert result.exit_code == 2
    assert "failed to load settings" in output

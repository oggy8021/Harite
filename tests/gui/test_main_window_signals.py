from pathlib import Path

from PIL import Image

from harite.gui.views.main_window import MainWindow


def test_on_change_input_text_updates_state():
    window = MainWindow()

    window.on_change_input_text("")
    assert window.can_optimize is False
    assert window.last_error == "input is required"

    window.on_change_input_text("a.jpg")
    assert window.can_optimize is True
    assert window.last_error == ""


def test_on_clear_input_resets_optimize_state():
    window = MainWindow()
    window.on_change_input_text("a.jpg")
    assert window.on_save_legacy() is True
    assert window.save_dialog_open is True

    ok = window.on_clear_input()

    assert ok is True
    assert window.can_optimize is False
    assert window.save_dialog_open is False
    assert window.status_phase == "input"
    assert window.status_message == "input is required"


def test_on_about_is_planned():
    window = MainWindow()

    ok = window.on_about()

    assert ok is False
    assert window.status_level == "planned"
    assert window.status_phase == "about"
    assert window.status_message == "about dialog is planned"


def test_on_set_color_is_planned():
    window = MainWindow()

    ok = window.on_set_color()

    assert ok is False
    assert window.status_level == "planned"
    assert window.status_phase == "color"
    assert window.status_message == "color picker is planned"


def test_save_dialog_confirm_and_cancel_have_distinct_meanings():
    window = MainWindow()

    assert window.on_save_dialog_cancel() is False
    assert window.status_level == "idle"
    assert window.status_phase == "save_dialog"
    assert window.status_message == "save dialog ignored (closed)"

    assert window.on_save_legacy() is True
    assert window.save_dialog_open is True
    assert window.status_level == "idle"
    assert window.status_phase == "save_dialog"
    assert window.status_message == "save dialog opened"

    assert window.on_save_dialog_cancel() is True
    assert window.save_dialog_open is False
    assert window.status_level == "idle"
    assert window.status_phase == "save_dialog"
    assert window.status_message == "save dialog canceled (path unchanged)"

    assert window.on_save_dialog_confirm() is False
    assert window.status_level == "idle"
    assert window.status_phase == "save_dialog"
    assert window.status_message == "save dialog ignored (closed)"

    assert window.on_save_legacy() is True
    assert window.on_save_dialog_confirm() is False
    assert window.status_level == "error"
    assert window.status_phase == "save_dialog"
    assert window.status_message == "save path is required"
    assert window.last_error == "save path is required"

    assert window.on_save_dialog_confirm("/tmp/result.jpg") is True
    assert window.form_state.save_path == "/tmp/result.jpg"
    assert window.status_level == "idle"
    assert window.status_phase == "save_dialog"
    assert window.status_message == "save path selected"


def test_save_dialog_confirm_without_argument_uses_existing_path():
    window = MainWindow()
    window.form_state.save_path = "/tmp/existing-save.jpg"
    window.save_dialog_open = True

    ok = window.on_save_dialog_confirm()

    assert ok is True
    assert window.save_dialog_open is False
    assert window.form_state.save_path == "/tmp/existing-save.jpg"
    assert window.status_level == "idle"
    assert window.status_phase == "save_dialog"
    assert window.status_message == "save path selected"


def test_save_dialog_cancel_keeps_existing_save_path():
    window = MainWindow()
    window.form_state.save_path = "/tmp/existing-save.jpg"
    window.save_dialog_open = True

    ok = window.on_save_dialog_cancel()

    assert ok is True
    assert window.save_dialog_open is False
    assert window.form_state.save_path == "/tmp/existing-save.jpg"
    assert window.status_level == "idle"
    assert window.status_phase == "save_dialog"
    assert window.status_message == "save dialog canceled (path unchanged)"


def test_save_dialog_confirm_runs_legacy_save_flow_when_input_ready(monkeypatch, tmp_path):
    class DummyController:
        def __init__(self) -> None:
            self.calls = []

        def run_optimize(self, form_state):
            self.calls.append(form_state.save_path)
            out = Path(form_state.save_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(b"x")
            return [out], []

    window = MainWindow()
    window.controller = DummyController()
    window.on_change_input_text("a.jpg")
    assert window.on_save_legacy() is True
    assert window.save_dialog_open is True

    picked = tmp_path / "picked" / "legacy-save.jpg"
    ok = window.on_save_dialog_confirm(str(picked))

    assert ok is True
    assert window.save_dialog_open is False
    assert window.form_state.save_path == str(picked)
    assert window.status_level == "success"
    assert window.status_phase == "optimize"
    assert window.status_message == "optimize completed"
    assert any("Save dialog confirm: running legacy save flow" in line for line in window.logs)


def test_layout_blueprint_defines_grouping_and_flow():
    window = MainWindow()

    bp = window.get_layout_blueprint()

    assert bp["title"] == "Harite Studio"
    assert bp["subtitle"] == "Compose -> Optimize -> Apply"
    assert bp["layout_version"] == "phase5-radical-mainwindow"
    assert isinstance(bp["sections"], tuple)
    assert bp["sections"][0][0] == "hero"
    assert bp["sections"][-1][0] == "status_panel"
    assert "hero-first" in bp["layout_highlights"]
    assert bp["primary_action_flow"] == (
        "hero",
        "optimize",
        "apply_dry_run",
        "apply_do_it",
    )
    assert bp["suggested_next_action"] == "input"
    assert bp["status"]["level"] == "idle"
    assert bp["status"]["phase"] == "init"
    assert bp["status"]["message"] == "ready"


def test_on_optimize_runs_and_logs(tmp_path):
    window = MainWindow()

    img_path = tmp_path / "in.jpg"
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    Image.new("RGB", (120, 80), color=(10, 20, 30)).save(img_path)

    window.form_state.output_dir = str(out_dir)
    window.form_state.resolution = "320x180"
    window.on_change_input_text(str(img_path))

    ok = window.on_optimize()
    assert ok is True
    assert window.can_apply is True
    assert window.status_level == "success"
    assert window.status_phase == "optimize"
    assert window.status_message == "optimize completed"
    assert any(line.startswith("Saved ") for line in window.logs)
    assert any(line.startswith("Saved: ") for line in window.logs)
    assert any("Next action: apply dry-run" in line for line in window.logs)


def test_on_close_marks_window_closed():
    window = MainWindow()
    assert window.closed is False

    window.on_close()
    assert window.closed is True
    assert "Window closed" in window.logs


def test_on_pick_input_appends_unique_paths():
    window = MainWindow()

    window.on_pick_input("a.jpg")
    window.on_pick_input("b.jpg")
    window.on_pick_input("a.jpg")

    assert window.form_state.input_value == "a.jpg,b.jpg"
    assert window.can_optimize is True


def test_on_change_margins_updates_form_state():
    window = MainWindow()

    window.on_change_margins(10, 20, 30, 40)
    assert window.form_state.margins == "10,20,30,40"
    assert window.last_error == ""

    window.on_change_margins(-1, 0, 0, 0)
    assert window.last_error == "margins must be non-negative"


def test_on_change_margins_keeps_previous_value_on_invalid_input():
    window = MainWindow()
    window.on_change_margins(1, 2, 3, 4)

    window.on_change_margins(-1, 2, 3, 4)

    assert window.form_state.margins == "1,2,3,4"
    assert window.last_error == "margins must be non-negative"


def test_on_toggle_fixed_updates_flag():
    window = MainWindow()
    assert window.form_state.fixed is False

    window.on_toggle_fixed(True)
    assert window.form_state.fixed is True

    window.on_toggle_fixed(False)
    assert window.form_state.fixed is False


def test_on_apply_dry_run_uses_latest_saved_file(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path: str, *, dry_run: bool = True) -> bool:
            self.calls.append((path, dry_run))
            return True

    plugin = DummyPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)

    window = MainWindow()
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")
    window.last_saved_files = [wall]

    ok = window.on_apply_dry_run()
    assert ok is True
    assert plugin.calls == [(str(wall), True)]
    assert any("Applied wallpaper" in line for line in window.logs)


def test_on_apply_do_it_calls_plugin_with_non_dry_run(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path: str, *, dry_run: bool = True) -> bool:
            self.calls.append((path, dry_run))
            return True

    plugin = DummyPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)

    window = MainWindow()
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")
    window.last_saved_files = [wall]

    ok = window.on_apply_do_it()
    assert ok is True
    assert plugin.calls == [(str(wall), False)]


def test_on_apply_without_optimized_file_fails():
    window = MainWindow()
    ok = window.on_apply_dry_run()

    assert ok is False
    assert window.last_error == "no optimized file to apply"
    assert window.status_level == "error"
    assert window.status_phase == "apply"


def test_watch_handlers_are_planned_and_interval_is_validated():
    window = MainWindow()

    assert window.on_watch_start() is False
    assert window.status_level == "planned"
    assert window.status_phase == "watch"
    assert window.status_message == "watch start is planned"

    assert window.on_watch_stop() is False
    assert window.status_level == "planned"
    assert window.status_phase == "watch"
    assert window.status_message == "watch stop is planned"

    assert window.on_watch_interval_change(120) is True
    assert window.watch_interval_seconds == 120
    assert window.status_level == "planned"
    assert window.status_phase == "watch"
    assert window.status_message == "watch interval planned: 120s"

    assert window.on_watch_interval_change(0) is False
    assert window.status_level == "error"
    assert window.status_phase == "watch"
    assert window.last_error == "watch interval must be positive"


def test_suggest_next_action_transitions(tmp_path):
    window = MainWindow()
    assert window.suggest_next_action() == "input"

    img_path = tmp_path / "in.jpg"
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    Image.new("RGB", (120, 80), color=(10, 20, 30)).save(img_path)

    window.form_state.output_dir = str(out_dir)
    window.form_state.resolution = "320x180"
    window.on_change_input_text(str(img_path))
    assert window.suggest_next_action() == "optimize"

    assert window.on_optimize() is True
    assert window.suggest_next_action() == "apply_dry_run"


def test_run_primary_flow_step_runs_optimize_then_apply(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path: str, *, dry_run: bool = True) -> bool:
            self.calls.append((path, dry_run))
            return True

    plugin = DummyPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)

    window = MainWindow()
    img_path = tmp_path / "in.jpg"
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    Image.new("RGB", (120, 80), color=(10, 20, 30)).save(img_path)

    window.form_state.output_dir = str(out_dir)
    window.form_state.resolution = "320x180"
    window.on_change_input_text(str(img_path))

    # first step should run optimize
    assert window.run_primary_flow_step() is True
    assert window.can_apply is True

    # second step should run apply dry-run
    assert window.run_primary_flow_step() is True
    assert window.status_level == "success"
    assert window.status_phase == "apply"
    assert window.status_message == "apply completed"
    assert plugin.calls
    assert plugin.calls[-1][1] is True


def test_status_unified_for_input_transitions():
    window = MainWindow()

    window.on_change_input_text("")
    assert window.status_level == "error"
    assert window.status_phase == "input"
    assert window.status_message == "input is required"
    assert window.last_error == "input is required"

    window.on_change_input_text("a.jpg")
    assert window.status_level == "idle"
    assert window.status_phase == "input"
    assert window.status_message == "input ready"
    assert window.last_error == ""


def test_default_plugin_is_known():
    window = MainWindow()
    assert window.plugin_name in window.available_plugins


def test_on_change_plugin_accepts_registered_plugin():
    window = MainWindow()
    ok = window.on_change_plugin("linux")

    assert ok is True
    assert window.plugin_name == "linux"
    assert window.last_error == ""


def test_on_change_plugin_rejects_unknown_plugin():
    window = MainWindow()
    previous = window.plugin_name
    ok = window.on_change_plugin("no-such-plugin")

    assert ok is False
    assert window.plugin_name == previous
    assert window.last_error == "unknown plugin: no-such-plugin"


def test_on_change_plugin_rejects_empty_value():
    window = MainWindow()
    previous = window.plugin_name

    ok = window.on_change_plugin("   ")

    assert ok is False
    assert window.plugin_name == previous
    assert window.last_error == "plugin is required"


def test_on_pick_input_empty_value_sets_error_and_keeps_input():
    window = MainWindow()
    window.on_change_input_text("a.jpg")

    window.on_pick_input("   ")

    assert window.form_state.input_value == "a.jpg"
    assert window.last_error == "input path is empty"


def test_build_optimize_cli_preview_contains_required_args(tmp_path):
    window = MainWindow()
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    window.form_state.input_value = "a.jpg,b.jpg"
    window.form_state.output_dir = str(out_dir)
    preview = window.build_optimize_cli_preview()

    assert preview.startswith("harite optimize ")
    assert "--input a.jpg,b.jpg" in preview
    assert f"--output {out_dir}" in preview


def test_build_optimize_cli_preview_includes_optional_flags(tmp_path):
    window = MainWindow()
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    window.form_state.input_value = "a.jpg"
    window.form_state.output_dir = str(out_dir)
    window.form_state.two_screen = True
    window.form_state.margins = "1,2,3,4"
    window.form_state.fixed = True
    window.form_state.embed_text = "hello"
    preview = window.build_optimize_cli_preview()

    assert "--two-screen" in preview
    assert "--margins 1,2,3,4" in preview
    assert "--fixed" in preview
    assert "--embed-text hello" in preview


def test_on_close_error_dialog_clears_last_error():
    window = MainWindow()
    window.last_error = "something failed"

    window.on_close_error_dialog()

    assert window.last_error == ""
    assert "Error dialog closed" in window.logs


def test_on_close_open_image_dialog_logs_close_event():
    window = MainWindow()
    previous_error = "keep this"
    window.last_error = previous_error

    window.on_close_open_image_dialog()

    assert window.last_error == previous_error
    assert "Open image dialog closed" in window.logs


def test_on_close_save_dialog_logs_close_event():
    window = MainWindow()
    window.on_close_save_dialog()

    assert "Save dialog closed" in window.logs


def test_on_close_settings_dialog_logs_close_event():
    window = MainWindow()
    window.on_close_settings_dialog()

    assert "Settings dialog closed" in window.logs


def test_on_close_color_dialog_logs_close_event():
    window = MainWindow()
    window.on_close_color_dialog()

    assert "Color selection dialog closed" in window.logs


def test_on_close_srcdir_dialog_logs_close_event():
    window = MainWindow()
    window.on_close_srcdir_dialog()

    assert "Source directory dialog closed" in window.logs


def test_on_apply_dry_run_unknown_plugin_fails(monkeypatch, tmp_path):
    def raise_key_error(_name):
        raise KeyError(_name)

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", raise_key_error)

    window = MainWindow()
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")
    window.last_saved_files = [wall]
    window.plugin_name = "missing-plugin"

    ok = window.on_apply_dry_run()

    assert ok is False
    assert window.last_error == "unknown plugin: missing-plugin"


def test_on_apply_dry_run_when_plugin_returns_false_sets_error(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str, *, dry_run: bool = True) -> bool:
            return False

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())

    window = MainWindow()
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")
    window.last_saved_files = [wall]

    ok = window.on_apply_dry_run()

    assert ok is False
    assert window.last_error == "failed to apply wallpaper"


def test_on_apply_dry_run_when_plugin_raises_sets_error(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str, *, dry_run: bool = True) -> bool:
            raise RuntimeError("boom")

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())

    window = MainWindow()
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")
    window.last_saved_files = [wall]

    ok = window.on_apply_dry_run()

    assert ok is False
    assert window.last_error == "failed to apply wallpaper: boom"

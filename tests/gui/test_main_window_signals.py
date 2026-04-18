from pathlib import Path

from PIL import Image

from harite.gui.views.main_window import MainWindow
from harite.workspace import Display


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
    assert window.on_save() is True
    assert window.save_path_dialog_open is True

    ok = window.on_clear_input()

    assert ok is True
    assert window.can_optimize is False
    assert window.save_path_dialog_open is False
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
    assert window.status_level == "deferred"
    assert window.status_phase == "color"
    assert window.status_message == "color picker is deferred to phase7"


def test_save_path_selection_and_cancel_have_distinct_meanings():
    window = MainWindow()

    assert window.on_save_path_selection_canceled() is False
    assert window.status_level == "idle"
    assert window.status_phase == "save_path"
    assert window.status_message == "save path cancel ignored (closed)"

    assert window.on_save() is True
    assert window.save_path_dialog_open is True
    assert window.status_level == "idle"
    assert window.status_phase == "save_path"
    assert window.status_message == "save path dialog opened"

    assert window.on_save_path_selection_canceled() is True
    assert window.save_path_dialog_open is False
    assert window.status_level == "idle"
    assert window.status_phase == "save_path"
    assert window.status_message == "save path canceled (path unchanged)"

    assert window.on_save_path_selected() is False
    assert window.status_level == "idle"
    assert window.status_phase == "save_path"
    assert window.status_message == "save path ignored (closed)"

    assert window.on_save() is True
    assert window.on_save_path_selected() is False
    assert window.status_level == "error"
    assert window.status_phase == "save_path"
    assert window.status_message == "save path is required"
    assert window.last_error == "save path is required"

    assert window.on_save_path_selected("/tmp/result.jpg") is False
    assert window.form_state.save_path == "/tmp/result.jpg"
    assert window.status_level == "error"
    assert window.status_phase == "save"
    assert window.status_message == "input is required"


def test_save_path_selected_without_argument_uses_existing_path():
    window = MainWindow()
    window.form_state.save_path = "/tmp/existing-save.jpg"
    window.on_change_input_text("a.jpg")
    window._update_save_target_display()
    window.save_path_dialog_open = True

    class DummyController:
        def run_export(self, form_state, save_path):
            out = Path(save_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(b"x")
            return [out], []

    window.controller = DummyController()

    ok = window.on_save_path_selected()

    assert ok is True
    assert window.save_path_dialog_open is False
    assert window.form_state.save_path == "/tmp/existing-save.jpg"
    assert window.save_target_display == "Save target: /tmp/existing-save.jpg"
    assert window.status_level == "success"
    assert window.status_phase == "save"
    assert window.status_message == "save completed"


def test_save_path_selection_canceled_keeps_existing_save_path():
    window = MainWindow()
    window.form_state.save_path = "/tmp/existing-save.jpg"
    window.save_path_dialog_open = True

    ok = window.on_save_path_selection_canceled()

    assert ok is True
    assert window.save_path_dialog_open is False
    assert window.form_state.save_path == "/tmp/existing-save.jpg"
    assert window.status_level == "idle"
    assert window.status_phase == "save_path"
    assert window.status_message == "save path canceled (path unchanged)"


def test_save_path_selected_runs_export_flow_when_input_ready(monkeypatch, tmp_path):
    class DummyController:
        def __init__(self) -> None:
            self.calls = []

        def run_export(self, form_state, save_path):
            self.calls.append((form_state.save_path, save_path))
            out = Path(save_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(b"x")
            return [out], []

    window = MainWindow()
    window.controller = DummyController()
    window.on_change_input_text("a.jpg")
    assert window.on_save() is True
    assert window.save_path_dialog_open is True

    picked = tmp_path / "picked" / "save-path.jpg"
    ok = window.on_save_path_selected(str(picked))

    assert ok is True
    assert window.save_path_dialog_open is False
    assert window.form_state.save_path == str(picked)
    assert window.status_level == "success"
    assert window.status_phase == "save"
    assert window.status_message == "save completed"
    assert window.controller.calls == [(str(picked), str(picked))]
    assert window.last_saved_files == []


def test_layout_blueprint_defines_grouping_and_flow():
    window = MainWindow()

    bp = window.get_layout_blueprint()

    assert bp["title"] == "Harite"
    assert bp["subtitle"] == "Compose -> Optimize -> Apply"
    assert bp["layout_version"] == "phase6-layout-redefinition"
    assert isinstance(bp["sections"], tuple)
    assert bp["sections"][0][0] == "title_menu_flow"
    assert bp["sections"][-1][0] == "debug_footer"
    assert "menu-bar-header" in bp["layout_highlights"]
    assert bp["primary_action_flow"] == (
        "save_as",
        "optimize",
        "apply",
    )
    assert bp["suggested_next_action"] == "input"
    assert bp["status"]["level"] == "idle"
    assert bp["status"]["phase"] == "init"
    assert bp["status"]["message"] == "ready"
    assert bp["status"]["save_target"] == "Save target: not-selected"
    assert bp["status"]["watch_sources"] == "Watch srcdirs: L=- | R=-"
    assert bp["status"]["watch_current"] == "Watch current: idle"


def test_save_path_selected_updates_single_save_target_display():
    window = MainWindow()

    class DummyController:
        def run_export(self, form_state, save_path):
            out = Path(save_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(b"x")
            return [out], []

    window.controller = DummyController()
    window.on_change_input_text("a.jpg")

    assert window.save_target_display == "Save target: not-selected"

    assert window.on_save() is True
    assert window.save_target_display == "Save target: not-selected"

    assert window.on_save_path_selected("/tmp/result.jpg") is True
    assert window.save_target_display == "Save target: /tmp/result.jpg"


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
    assert any("Next action: apply" in line for line in window.logs)


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


def test_on_pick_input_updates_side_specific_paths():
    window = MainWindow()

    window.on_pick_input("left-a.jpg", "L")
    window.on_pick_input("right-a.jpg", "R")
    window.on_pick_input("left-b.jpg", "L")

    assert window.input_path_l == "left-b.jpg"
    assert window.input_path_r == "right-a.jpg"
    assert window.form_state.input_value == "left-b.jpg,right-a.jpg"
    assert window.can_optimize is True


def test_two_screen_auto_configures_when_both_inputs_and_displays_exist(monkeypatch):
    monkeypatch.setattr(
        "harite.gui.views.main_window.detect_displays",
        lambda: [
            Display(name="L", width=1920, height=1080),
            Display(name="R", width=1280, height=1024, x_offset=1920),
        ],
    )

    window = MainWindow()
    window.on_pick_input("left.jpg", "L")
    window.on_pick_input("right.jpg", "R")

    assert window.form_state.two_screen is True
    assert window.form_state.l_display == "1920x1080"
    assert window.form_state.r_display == "1280x1024"


def test_two_screen_auto_disables_without_two_inputs(monkeypatch):
    monkeypatch.setattr(
        "harite.gui.views.main_window.detect_displays",
        lambda: [
            Display(name="L", width=1920, height=1080),
            Display(name="R", width=1280, height=1024, x_offset=1920),
        ],
    )

    window = MainWindow()
    window.on_pick_input("left.jpg", "L")

    assert window.form_state.two_screen is False
    assert window.form_state.l_display is None
    assert window.form_state.r_display is None


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


def test_on_change_margins_supports_single_widget_update():
    window = MainWindow()

    window.on_change_margins(1, 2, 3, 4)
    window.on_change_margins("spnTopMergin", 99)

    assert window.form_state.margins == "1,2,99,4"
    assert window.last_error == ""


def test_on_toggle_fixed_updates_flag():
    window = MainWindow()
    assert window.form_state.fixed is False

    window.on_toggle_fixed(True)
    assert window.form_state.fixed is True

    window.on_toggle_fixed(False)
    assert window.form_state.fixed is False


def test_on_toggle_position_updates_alignment_and_reset():
    window = MainWindow()

    window.on_toggle_position("tglPushRightL", True)
    window.on_toggle_position("tglUpperR", True)

    assert window.form_state.align == "right"
    assert window.form_state.valign == "top"

    window.on_toggle_position_reset("tglPushRightL")
    window.on_toggle_position_reset("tglUpperR")

    assert window.form_state.align == "center"
    assert window.form_state.valign == "center"


def test_on_apply_uses_immediate_apply(monkeypatch, tmp_path):
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

    ok = window.on_apply()
    assert ok is True
    assert plugin.calls == [(str(wall), False)]
    assert any("Applied wallpaper" in line for line in window.logs)


def test_on_change_apply_mode_accepts_per_monitor_auto_split():
    window = MainWindow()

    ok = window.on_change_apply_mode("per-monitor-auto-split")

    assert ok is True
    assert window.apply_mode == "per-monitor-auto-split"
    assert window.last_error == ""


def test_on_apply_per_monitor_auto_split_uses_split_mapping(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path, *, dry_run: bool = True) -> bool:
            self.calls.append((path, dry_run))
            return True

    plugin = DummyPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)
    monkeypatch.setattr(
        "harite.gui.views.main_window.detect_displays",
        lambda: [
            Display(name="HDMI-1", width=1920, height=1080),
            Display(name="DP-1", width=1280, height=1024, x_offset=1920),
        ],
    )
    expected = {
        "HDMI-1": tmp_path / "wall_HDMI-1.jpg",
        "DP-1": tmp_path / "wall_DP-1.jpg",
    }
    monkeypatch.setattr(
        "harite.gui.views.main_window.split_composite_for_displays",
        lambda _path, _displays, _output_dir: expected,
    )

    window = MainWindow()
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")
    window.last_saved_files = [wall]
    window.plugin_name = "linux"
    window.apply_mode = "per-monitor-auto-split"

    ok = window.on_apply()

    assert ok is True
    assert plugin.calls == [(expected, False)]
    assert any("Apply per-monitor auto-split" in line for line in window.logs)


def test_on_apply_without_optimized_file_fails():
    window = MainWindow()
    ok = window.on_apply()

    assert ok is False
    assert window.last_error == "no optimized file to apply"
    assert window.status_level == "error"
    assert window.status_phase == "apply"


def test_watch_handlers_use_srcdirs_and_interval_validation(tmp_path):
    window = MainWindow()

    assert window.on_watch_start() is False
    assert window.status_level == "error"
    assert window.status_phase == "watch"
    assert window.last_error == "watch srcdir is required"

    left_dir = tmp_path / "watch-left"
    right_dir = tmp_path / "watch-right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (right_dir / "right-1.png").write_bytes(b"right")

    assert window.on_pick_watch_srcdir(str(left_dir), "L") is True
    assert window.on_pick_watch_srcdir(str(right_dir), "R") is True
    assert window.watch_source_display == f"Watch srcdirs: L={left_dir} | R={right_dir}"

    assert window.on_watch_start() is True
    assert window.watch_running is True
    assert window.status_level == "success"
    assert window.status_phase == "watch"
    assert window.status_message == "watch started"
    assert window.watch_current_display == (
        f"Watch current: L={left_dir / 'left-1.jpg'} | R={right_dir / 'right-1.png'}"
    )

    assert window.on_watch_stop() is True
    assert window.watch_running is False
    assert window.status_level == "idle"
    assert window.status_phase == "watch"
    assert window.status_message == "watch stopped"

    assert window.on_watch_interval_change(120) is True
    assert window.watch_interval_seconds == 120
    assert window.status_level == "idle"
    assert window.status_phase == "watch"
    assert window.status_message == "watch interval updated: 120s"

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
    assert window.suggest_next_action() == "apply"


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

    # second step should run apply
    assert window.run_primary_flow_step() is True
    assert window.status_level == "success"
    assert window.status_phase == "apply"
    assert window.status_message == "apply completed"
    assert plugin.calls
    assert plugin.calls[-1][1] is False


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


def test_on_close_save_path_dialog_logs_close_event():
    window = MainWindow()
    window.on_close_save_path_dialog()

    assert "Save path dialog closed" in window.logs


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


def test_on_apply_unknown_plugin_fails(monkeypatch, tmp_path):
    def raise_key_error(_name):
        raise KeyError(_name)

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", raise_key_error)

    window = MainWindow()
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")
    window.last_saved_files = [wall]
    window.plugin_name = "missing-plugin"

    ok = window.on_apply()

    assert ok is False
    assert window.last_error == "unknown plugin: missing-plugin"


def test_on_apply_when_plugin_returns_false_sets_error(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str, *, dry_run: bool = True) -> bool:
            return False

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())

    window = MainWindow()
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")
    window.last_saved_files = [wall]

    ok = window.on_apply()

    assert ok is False
    assert window.last_error == "failed to apply wallpaper"


def test_on_apply_when_plugin_raises_sets_error(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str, *, dry_run: bool = True) -> bool:
            raise RuntimeError("boom")

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())

    window = MainWindow()
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")
    window.last_saved_files = [wall]

    ok = window.on_apply()

    assert ok is False
    assert window.last_error == "failed to apply wallpaper: boom"

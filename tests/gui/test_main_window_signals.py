from pathlib import Path

from PIL import Image

from harite.apply_settings import EffectiveApplySettings
from harite.display_context import TwoScreenOptimizeContext
from harite.preferences import AppPreferences
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


def test_on_change_input_text_disables_optimize_when_resolution_unresolved():
    window = MainWindow()
    window.form_state.resolution = ""

    window.on_change_input_text("a.jpg")

    assert window.can_optimize is False
    assert window.status_phase == "optimize"
    assert window.status_message == "resolution is unresolved"
    assert window.last_error == "resolution is unresolved"
    assert window.on_optimize() is False
    assert window.status_message == "resolution is unresolved"


def test_on_clear_input_resets_optimize_state():
    window = MainWindow()
    window.on_change_input_text("a.jpg")
    assert window.on_save_as() is True
    assert window.save_path_dialog_open is True

    ok = window.on_clear_input()

    assert ok is True
    assert window.can_optimize is False
    assert window.save_path_dialog_open is False
    assert window.status_phase == "input"
    assert window.status_message == "input is required"


def test_on_about_opens_dialog():
    window = MainWindow()

    ok = window.on_about()

    assert ok is True
    assert window.about_dialog_open is True
    assert window.status_level == "idle"
    assert window.status_phase == "about"
    assert window.status_message == "about dialog opened"


def test_on_get_about_dialog_info_returns_metadata():
    window = MainWindow()

    info = window.on_get_about_dialog_info()

    assert info["app_name"] == "Harite"
    assert info["version"]
    assert info["license_name"] == "MIT License"


def test_on_set_color_opens_dialog_state():
    window = MainWindow()

    ok = window.on_set_color()

    assert ok is True
    assert window.status_level == "idle"
    assert window.status_phase == "color"
    assert window.status_message == "color dialog opened"


def test_on_set_color_updates_background_color():
    window = MainWindow()

    ok = window.on_set_color("#224466")

    assert ok is True
    assert window.form_state.background_color == "#224466"
    assert window.status_level == "success"
    assert window.status_phase == "color"
    assert window.status_message == "background color updated: #224466"


def test_save_path_selection_and_cancel_have_distinct_meanings():
    window = MainWindow()

    assert window.on_save_path_selection_canceled() is False
    assert window.status_level == "idle"
    assert window.status_phase == "save_path"
    assert window.status_message == "save path cancel ignored (closed)"

    assert window.on_save_as() is True
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

    assert window.on_save_as() is True
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
    assert window.on_save_as() is True
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
    assert bp["sections"][-1][0] == "status_footer"
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

    assert window.on_save_as() is True
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


def test_build_result_preview_state_uses_latest_saved_file(tmp_path):
    window = MainWindow()
    saved = tmp_path / "result.jpg"
    saved.write_bytes(b"x")

    window.last_saved_files = [saved]
    window.form_state.input_value = "single-source.jpg"

    state = window.build_result_preview_state()

    assert state.source_file == saved
    assert state.apply_mode == window.apply_mode
    assert state.assist_summary == "Assist: same optimized image will be applied to both displays"
    assert state.l_assignment == "L display <- single-source.jpg"
    assert state.r_assignment == "R display <- single-source.jpg"
    assert state.l_result_note == "Result: full optimized image"
    assert state.r_result_note == "Result: full optimized image"


def test_build_result_preview_state_includes_two_screen_display_sizes(tmp_path):
    window = MainWindow()
    saved = tmp_path / "result.jpg"
    saved.write_bytes(b"x")

    window.last_saved_files = [saved]
    window.apply_mode = "per-monitor-auto-split"
    window.form_state.input_value = "left.jpg,right.jpg"
    window.form_state.two_screen = True
    window.form_state.resolution = "320x180"
    window.form_state.l_display = "200x180"
    window.form_state.r_display = "120x180"

    state = window.build_result_preview_state()

    assert state.source_file == saved
    assert state.apply_mode == "per-monitor-auto-split"
    assert state.l_display == (200, 180)
    assert state.r_display == (120, 180)
    assert state.assist_summary == "Assist: auto-split as L 200x180 | R 120x180"
    assert state.l_assignment == "L display <- left.jpg"
    assert state.r_assignment == "R display <- right.jpg"
    assert state.l_result_note == "Result: auto-split left crop"
    assert state.r_result_note == "Result: auto-split right crop"


def test_build_result_preview_state_truncates_long_assignment_names(tmp_path):
    window = MainWindow()
    saved = tmp_path / "result.jpg"
    saved.write_bytes(b"x")

    window.last_saved_files = [saved]
    window.form_state.input_value = (
        "Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg,"
        "Higashiyama-Kaii-Zansho-1920x1080-1-700x394.jpg"
    )

    state = window.build_result_preview_state()

    assert state.l_assignment == "L display <- Higashiyama-Kaii-Cho-...700x1244.jpg"
    assert state.r_assignment == "R display <- Higashiyama-Kaii-Zans...-700x394.jpg"


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
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: TwoScreenOptimizeContext(
            displays=(
                Display(name="L", width=1920, height=1080, x_offset=0),
                Display(name="R", width=1280, height=1024, x_offset=1920),
            ),
            resolution=(3200, 1080),
            l_display=(1920, 1080),
            r_display=(1280, 1024),
        ),
    )

    window = MainWindow()
    window.on_pick_input("left.jpg", "L")
    window.on_pick_input("right.jpg", "R")

    assert window.form_state.two_screen is True
    assert window.form_state.l_display == "1920x1080"
    assert window.form_state.r_display == "1280x1024"
    assert window.form_state.resolution == "3200x1080"


def test_two_screen_auto_restores_prior_resolution_when_second_input_removed(monkeypatch):
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: TwoScreenOptimizeContext(
            displays=(
                Display(name="L", width=1920, height=1080, x_offset=0),
                Display(name="R", width=1280, height=1024, x_offset=1920),
            ),
            resolution=(3200, 1080),
            l_display=(1920, 1080),
            r_display=(1280, 1024),
        ),
    )

    window = MainWindow()
    window.form_state.resolution = "1600x900"

    window.on_pick_input("left.jpg", "L")
    window.on_pick_input("right.jpg", "R")
    assert window.form_state.resolution == "3200x1080"

    window.on_change_input_text("left.jpg")

    assert window.form_state.two_screen is False
    assert window.form_state.l_display is None
    assert window.form_state.r_display is None
    assert window.form_state.resolution == "1600x900"


def test_two_screen_auto_disables_without_two_inputs(monkeypatch):
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: None,
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
    window.on_change_margins("spnTopMargin", 99)

    assert window.form_state.margins == "1,2,99,4"
    assert window.last_error == ""

def test_on_toggle_position_updates_alignment_and_reset():
    window = MainWindow()

    window.on_toggle_position("tglPushRightL", True)
    window.on_toggle_position("tglUpperR", True)

    assert window.form_state.align == ("right", "center")
    assert window.form_state.valign == ("center", "top")

    window.on_toggle_position_reset("tglPushRightL")
    window.on_toggle_position_reset("tglUpperR")

    assert window.form_state.align == ("center", "center")
    assert window.form_state.valign == ("center", "center")


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
        "harite.gui.views.main_window.resolve_apply_settings",
        lambda **_kwargs: EffectiveApplySettings(
            plugin_name="linux",
            apply_mode="per-monitor-auto-split",
            target={
                "HDMI-1": tmp_path / "wall_HDMI-1.jpg",
                "DP-1": tmp_path / "wall_DP-1.jpg",
            },
        ),
    )

    window = MainWindow()
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")
    window.last_saved_files = [wall]
    window.plugin_name = "linux"
    window.apply_mode = "per-monitor-auto-split"

    ok = window.on_apply()

    assert ok is True
    assert plugin.calls == [({"HDMI-1": tmp_path / "wall_HDMI-1.jpg", "DP-1": tmp_path / "wall_DP-1.jpg"}, False)]
    assert any("Apply per-monitor auto-split" in line for line in window.logs)


def test_on_apply_per_monitor_auto_split_requires_context(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "harite.gui.views.main_window.resolve_apply_settings",
        lambda **_kwargs: (_ for _ in ()).throw(ValueError("per-monitor apply requires at least two detected displays")),
    )

    window = MainWindow()
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")
    window.last_saved_files = [wall]
    window.plugin_name = "linux"
    window.apply_mode = "per-monitor-auto-split"

    ok = window.on_apply()

    assert ok is False
    assert window.last_error == "per-monitor apply requires at least two detected displays"


def test_open_settings_dialog_tracks_state():
    window = MainWindow()

    ok = window.on_open_settings_dialog()

    assert ok is True
    assert window.settings_dialog_open is True
    assert "Settings dialog opened" in window.logs


def test_apply_settings_updates_runtime_state():
    window = MainWindow()
    prefs = AppPreferences.from_config_dict(
        {
            "resolution": "auto",
            "two_screen": "auto",
            "l_display": "auto",
            "r_display": "auto",
            "plugin": "linux",
            "apply_mode": "per-monitor-auto-split",
            "watch_interval_seconds": 120,
            "watch_srcdir_l": "/watch/left",
            "watch_srcdir_r": "/watch/right",
        },
        default_plugin=window.plugin_name,
    )

    ok = window.on_apply_settings(prefs)

    assert ok is True
    assert window.form_state.resolution == "auto"
    assert window.form_state.two_screen is None
    assert window.form_state.l_display == "auto"
    assert window.form_state.r_display == "auto"
    assert window.plugin_name == "linux"
    assert window.apply_mode == "per-monitor-auto-split"
    assert window.watch_interval_seconds == 120
    assert window.watch_srcdir_l == "/watch/left"
    assert window.watch_srcdir_r == "/watch/right"
    assert window.watch_source_display == "Watch srcdirs: L=/watch/left | R=/watch/right"


def test_export_and_reload_settings_config_round_trips():
    window = MainWindow()
    window.form_state.resolution = "auto"
    window.form_state.two_screen = None
    window.form_state.l_display = "auto"
    window.form_state.r_display = "auto"
    window.plugin_name = "linux"
    window.apply_mode = "per-monitor-auto-split"
    window.watch_interval_seconds = 90
    window.watch_srcdir_l = "/watch/left"
    window.watch_srcdir_r = "/watch/right"
    window._update_watch_source_display()

    exported = window.export_settings_config()

    assert exported["resolution"] == "auto"
    assert exported["two_screen"] == "auto"
    assert exported["align"] == ["center", "center"]
    assert exported["valign"] == ["center", "center"]
    assert exported["plugin"] == "linux"
    assert exported["apply_mode"] == "per-monitor-auto-split"
    assert exported["watch_interval_seconds"] == 90
    assert exported["watch_srcdir_l"] == "/watch/left"
    assert exported["watch_srcdir_r"] == "/watch/right"

    other = MainWindow()
    assert other.load_settings_config(exported) is True
    assert other.form_state.resolution == "auto"
    assert other.form_state.two_screen is None
    assert other.form_state.align == ("center", "center")
    assert other.form_state.valign == ("center", "center")
    assert other.plugin_name == "linux"
    assert other.watch_interval_seconds == 90
    assert other.watch_srcdir_l == "/watch/left"
    assert other.watch_srcdir_r == "/watch/right"


def test_settings_file_save_and_load_round_trip(tmp_path):
    window = MainWindow()
    window.form_state.resolution = "auto"
    window.form_state.two_screen = None
    window.form_state.l_display = "auto"
    window.form_state.r_display = "auto"
    window.plugin_name = "linux"
    window.apply_mode = "per-monitor-auto-split"
    window.watch_interval_seconds = 75
    window.watch_srcdir_l = "/watch/left"
    window.watch_srcdir_r = "/watch/right"

    target = tmp_path / "prefs.json"

    assert window.on_save_settings_file(str(target)) is True
    assert target.exists() is True

    other = MainWindow()
    assert other.on_load_settings_file(str(target)) is True
    assert other.form_state.resolution == "auto"
    assert other.form_state.two_screen is None
    assert other.form_state.l_display == "auto"
    assert other.form_state.r_display == "auto"
    assert other.form_state.align == ("center", "center")
    assert other.form_state.valign == ("center", "center")
    assert other.plugin_name == "linux"
    assert other.apply_mode == "per-monitor-auto-split"
    assert other.watch_interval_seconds == 75
    assert other.watch_srcdir_l == "/watch/left"
    assert other.watch_srcdir_r == "/watch/right"


def test_settings_file_handlers_require_path():
    window = MainWindow()

    assert window.on_save_settings_file("") is False
    assert window.status_phase == "settings"
    assert window.last_error == "settings path is required"

    assert window.on_load_settings_file("") is False
    assert window.status_phase == "settings"
    assert window.last_error == "settings path is required"


def test_settings_file_save_accepts_explicit_dialog_config(tmp_path):
    window = MainWindow()
    target = tmp_path / "prefs-dialog.json"

    assert window.on_save_settings_file(
        str(target),
        {
            "resolution": "auto",
            "two_screen": "auto",
            "plugin": "linux",
            "apply_mode": "per-monitor-auto-split",
            "watch_interval_seconds": 33,
            "watch_srcdir_l": "/watch/left",
        },
    ) is True

    loaded = window.on_load_settings_file(str(target))

    assert loaded is True
    assert window.form_state.resolution == "auto"
    assert window.form_state.two_screen is None
    assert window.plugin_name == "linux"
    assert window.apply_mode == "per-monitor-auto-split"
    assert window.watch_interval_seconds == 33
    assert window.watch_srcdir_l == "/watch/left"


def test_settings_file_round_trips_explicit_apply_mode_without_gui_projection(tmp_path):
    window = MainWindow()
    target = tmp_path / "prefs-explicit.json"

    assert window.on_save_settings_file(
        str(target),
        {
            "plugin": "linux",
            "apply_mode": "per-monitor-explicit",
        },
    ) is True

    other = MainWindow()
    assert other.on_load_settings_file(str(target)) is True
    assert other.plugin_name == "linux"
    assert other.apply_mode == "per-monitor-explicit"


def test_on_apply_without_optimized_file_fails():
    window = MainWindow()
    ok = window.on_apply()

    assert ok is False
    assert window.last_error == "no optimized file to apply"
    assert window.status_level == "error"
    assert window.status_phase == "apply"


def test_watch_handlers_use_srcdirs_and_interval_validation(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str, *, dry_run: bool = True) -> bool:
            return True

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())

    window = MainWindow()

    assert window.on_watch_start() is False
    assert window.status_level == "error"
    assert window.status_phase == "watch"
    assert window.last_error == "watch srcdir is required"

    left_dir = tmp_path / "watch-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")

    assert window.on_pick_watch_srcdir(str(left_dir), "L") is True
    assert window.watch_source_display == f"Watch srcdirs: L={left_dir} | R=-"

    assert window.on_watch_start() is True
    assert window.watch_running is True
    assert window.status_level == "success"
    assert window.status_phase == "watch"
    assert window.status_message == "watch started"
    assert window.watch_current_display == f"Watch current: L={left_dir / 'left-1.jpg'} | R=-"

    (left_dir / "left-2.jpg").write_bytes(b"left-2")

    assert window.on_watch_tick() is True
    assert window.watch_current_display == f"Watch current: L={left_dir / 'left-2.jpg'} | R=-"

    assert window.on_watch_stop() is True
    assert window.watch_running is False
    assert window.status_level == "idle"
    assert window.status_phase == "watch"
    assert window.status_message == "watch stopped"

    assert window.on_watch_tick() is False

    assert window.on_watch_interval_change(120) is True
    assert window.watch_interval_seconds == 120
    assert window.status_level == "idle"
    assert window.status_phase == "watch"
    assert window.status_message == "watch interval updated: 120s"

    assert window.on_watch_interval_change(0) is False
    assert window.status_level == "error"
    assert window.status_phase == "watch"
    assert window.last_error == "watch interval must be positive"


def test_watch_single_source_applies_on_start_and_tick(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path: str, *, dry_run: bool = True) -> bool:
            self.calls.append((path, dry_run))
            return True

    plugin = DummyPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)

    window = MainWindow()
    left_dir = tmp_path / "watch-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")

    assert window.on_pick_watch_srcdir(str(left_dir), "L") is True
    assert window.on_watch_start() is True
    assert plugin.calls == [(str(left_dir / "left-1.jpg"), False)]

    assert window.on_watch_tick() is True
    assert plugin.calls[-1] == (str(left_dir / "left-2.jpg"), False)

    assert window.on_watch_stop() is True


def test_watch_single_source_start_fails_when_plugin_apply_fails(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str, *, dry_run: bool = True) -> bool:
            return False

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())

    window = MainWindow()
    left_dir = tmp_path / "watch-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")

    assert window.on_pick_watch_srcdir(str(left_dir), "L") is True
    assert window.on_watch_start() is False
    assert window.watch_running is False
    assert window.status_level == "error"
    assert window.status_phase == "watch"
    assert window.status_message == "watch start single-file apply failed"
    assert window.last_error == "watch start single-file apply failed"


def test_watch_start_normalizes_empty_output_dir(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str, *, dry_run: bool = True) -> bool:
            return True

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())
    home = tmp_path / "home"
    xdg_config = tmp_path / "xdg-config"
    home.mkdir()
    xdg_config.mkdir()
    (xdg_config / "user-dirs.dirs").write_text('XDG_PICTURES_DIR="$HOME/Pictures"\n', encoding="utf-8")
    monkeypatch.setattr("harite.gui.views.main_window.Path.home", lambda: home)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_config))
    monkeypatch.setattr("harite.gui.views.main_window.sys.platform", "linux")

    window = MainWindow()
    window.form_state.output_dir = ""
    left_dir = tmp_path / "watch-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")

    assert window.on_pick_watch_srcdir(str(left_dir), "L") is True
    assert window.on_watch_start() is True
    assert window.form_state.output_dir == str(home / "Pictures")
    assert window.watch_output_display == f"Watch output: {home / 'Pictures'}"


def test_main_window_defaults_output_dir_to_xdg_pictures(monkeypatch, tmp_path):
    home = tmp_path / "home"
    xdg_config = tmp_path / "xdg-config"
    home.mkdir()
    xdg_config.mkdir()
    (xdg_config / "user-dirs.dirs").write_text('XDG_PICTURES_DIR="$HOME/MyPictures"\n', encoding="utf-8")
    monkeypatch.setattr("harite.gui.views.main_window.Path.home", lambda: home)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_config))
    monkeypatch.setattr("harite.gui.views.main_window.sys.platform", "linux")

    window = MainWindow()

    assert window.form_state.output_dir == str(home / "MyPictures")
    assert window.watch_output_display == f"Watch output: {home / 'MyPictures'}"


def test_main_window_defaults_output_dir_to_home_pictures_when_xdg_config_missing(monkeypatch, tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr("harite.gui.views.main_window.Path.home", lambda: home)
    monkeypatch.delenv("XDG_PICTURES_DIR", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "missing-xdg-config"))
    monkeypatch.setattr("harite.gui.views.main_window.sys.platform", "linux")

    window = MainWindow()

    assert window.form_state.output_dir == str(home / "Pictures")
    assert window.watch_output_display == f"Watch output: {home / 'Pictures'}"


def test_main_window_defaults_output_dir_to_home_pictures_when_windows_known_folder_unavailable(monkeypatch, tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr("harite.gui.views.main_window.Path.home", lambda: home)
    monkeypatch.delenv("XDG_PICTURES_DIR", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setattr("harite.gui.views.main_window.sys.platform", "win32")
    monkeypatch.setattr(MainWindow, "_resolve_windows_pictures_dir", lambda self: None)
    monkeypatch.setattr(MainWindow, "_resolve_xdg_pictures_dir", lambda self: None)

    window = MainWindow()

    assert window.form_state.output_dir == str(home / "Pictures")
    assert window.watch_output_display == f"Watch output: {home / 'Pictures'}"


def test_watch_single_source_tick_stops_when_plugin_apply_fails(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = 0

        def apply(self, path: str, *, dry_run: bool = True) -> bool:
            self.calls += 1
            return self.calls == 1

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())

    window = MainWindow()
    left_dir = tmp_path / "watch-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")

    assert window.on_pick_watch_srcdir(str(left_dir), "L") is True
    assert window.on_watch_start() is True
    assert window.on_watch_tick() is False
    assert window.watch_running is False
    assert window.status_level == "error"
    assert window.status_phase == "watch"
    assert window.status_message == "watch tick single-file apply failed"
    assert window.last_error == "watch tick single-file apply failed"


def test_watch_single_source_success_cleans_previous_generated_files(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str, *, dry_run: bool = True) -> bool:
            return True

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())

    window = MainWindow()
    left_dir = tmp_path / "watch-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")

    old_composite = tmp_path / "harite_output_0001.jpg"
    old_split = tmp_path / "harite_output_0001_HDMI-1.jpg"
    old_composite.write_bytes(b"old-composite")
    old_split.write_bytes(b"old-split")
    window._watch_active_generated_files = (old_composite, old_split)

    assert window.on_pick_watch_srcdir(str(left_dir), "L") is True
    assert window.on_watch_start() is True

    assert old_composite.exists() is False
    assert old_split.exists() is False


def test_watch_dual_source_falls_back_to_per_monitor_auto_split(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path, *, dry_run: bool = True) -> bool:
            self.calls.append((path, dry_run))
            return True

    plugin = DummyPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: TwoScreenOptimizeContext(
            displays=(
                Display(name="HDMI-1", width=1920, height=1080, x_offset=0, y_offset=0),
                Display(name="DP-1", width=1920, height=1080, x_offset=1920, y_offset=0),
            ),
            resolution=(3840, 1080),
            l_display=(1920, 1080),
            r_display=(1920, 1080),
        ),
    )
    monkeypatch.setattr(
        "harite.gui.views.main_window.resolve_apply_settings",
        lambda **kwargs: EffectiveApplySettings(
            plugin_name="linux",
            apply_mode="per-monitor-auto-split",
            target=(
                {"HDMI-1": split1_hdmi, "DP-1": split1_dp}
                if kwargs["file"] == composite
                else {"HDMI-1": split2_hdmi, "DP-1": split2_dp}
            ),
        ),
    )

    composite = tmp_path / "watch-composite.jpg"
    composite.write_bytes(b"composite")
    composite2 = tmp_path / "watch-composite-2.jpg"
    composite2.write_bytes(b"composite-2")
    split1_hdmi = tmp_path / "watch_HDMI-1.jpg"
    split1_dp = tmp_path / "watch_DP-1.jpg"
    split2_hdmi = tmp_path / "watch2_HDMI-1.jpg"
    split2_dp = tmp_path / "watch2_DP-1.jpg"
    split1_hdmi.write_bytes(b"split1-hdmi")
    split1_dp.write_bytes(b"split1-dp")
    split2_hdmi.write_bytes(b"split2-hdmi")
    split2_dp.write_bytes(b"split2-dp")

    window = MainWindow()
    window.plugin_name = "linux"
    observed_inputs = []
    optimize_calls = 0

    def fake_run_optimize(state):
        nonlocal optimize_calls
        optimize_calls += 1
        observed_inputs.append(state.input_value)
        return ([composite], []) if optimize_calls == 1 else ([composite2], [])

    monkeypatch.setattr(window.controller, "run_optimize", fake_run_optimize)

    left_dir = tmp_path / "watch-left"
    right_dir = tmp_path / "watch-right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")
    (right_dir / "right-1.png").write_bytes(b"right")
    (right_dir / "right-2.png").write_bytes(b"right-2")

    assert window.on_pick_watch_srcdir(str(left_dir), "L") is True
    assert window.on_pick_watch_srcdir(str(right_dir), "R") is True
    assert window.on_watch_start() is True

    assert observed_inputs == [f"{left_dir / 'left-1.jpg'},{right_dir / 'right-1.png'}"]
    assert plugin.calls == [({"HDMI-1": split1_hdmi, "DP-1": split1_dp}, False)]
    assert any("Watch start per-monitor auto-split" in line for line in window.logs)

    assert window.on_watch_tick() is True
    assert observed_inputs[-1] == f"{left_dir / 'left-2.jpg'},{right_dir / 'right-2.png'}"
    assert plugin.calls[-1] == ({"HDMI-1": split2_hdmi, "DP-1": split2_dp}, False)
    assert composite.exists() is False
    assert split1_hdmi.exists() is False
    assert split1_dp.exists() is False
    assert composite2.exists() is True
    assert split2_hdmi.exists() is True
    assert split2_dp.exists() is True


def test_watch_dual_source_start_fails_without_two_detected_displays(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: None,
    )

    window = MainWindow()
    window.plugin_name = "linux"

    left_dir = tmp_path / "watch-left"
    right_dir = tmp_path / "watch-right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (right_dir / "right-1.png").write_bytes(b"right")

    assert window.on_pick_watch_srcdir(str(left_dir), "L") is True
    assert window.on_pick_watch_srcdir(str(right_dir), "R") is True
    assert window.on_watch_start() is False
    assert window.watch_running is False
    assert window.status_level == "error"
    assert window.status_phase == "watch"
    assert window.status_message == "dual-source watch requires two detected displays"
    assert window.last_error == "dual-source watch requires two detected displays"
    assert any("Watch start blocked: dual-source watch requires two detected displays" in line for line in window.logs)


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
    window.form_state.embed_text = "hello"
    preview = window.build_optimize_cli_preview()

    assert "--two-screen" in preview
    assert "--margins 1,2,3,4" in preview
    assert "--embed-text hello" in preview


def test_margin_text_change_handlers_update_form_state():
    window = MainWindow()
    window.form_state.resolution = "1920x1080"
    window.form_state.margins = "10,10,20,30"

    assert window.on_change_margin_text_mode("combo") is True
    assert window.on_change_margin_text("hello") is True
    assert window.on_change_margin_text_position("bottom") is True
    assert window.on_change_margin_text_max_lines(4) is True

    assert window.form_state.embed_info == "combo"
    assert window.form_state.embed_text == "hello"
    assert window.form_state.embed_position == "bottom"
    assert window.form_state.embed_max_lines == 4
    assert window.status_phase == "margins"
    assert window.status_message == "margin text ready in right bottom position (950x30)"
    assert window.last_error == ""


def test_margin_text_change_handlers_reject_invalid_values():
    window = MainWindow()

    assert window.on_change_margin_text_mode("weird") is False
    assert window.on_change_margin_text_position("auto") is False
    assert window.on_change_margin_text_position("middle") is False
    assert window.on_change_margin_text_max_lines(0) is False


def test_margin_text_is_clamped_to_five_lines():
    window = MainWindow()

    assert window.on_change_margin_text("1\n2\n3\n4\n5\n6") is True
    assert window.form_state.embed_text == "1\n2\n3\n4\n5"


def test_margin_text_preserves_trailing_newline_during_edit():
    window = MainWindow()

    assert window.on_change_margin_text("1\n") is True
    assert window.form_state.embed_text == "1\n"


def test_margin_text_preflight_reports_margin_area_too_small():
    window = MainWindow()
    window.form_state.resolution = "1920x1080"
    window.form_state.margins = "10,10,20,10"

    assert window.on_change_margin_text_mode("params") is True
    assert window.on_change_margin_text_position("bottom") is True

    assert window.status_phase == "margins"
    assert window.status_message == "margin text does not fit current margin area"
    assert window.last_error == "selected margin area is too small for margin text"


def test_margin_text_preflight_uses_display_slice_area_for_two_screen():
    window = MainWindow()
    window.form_state.two_screen = True
    window.form_state.resolution = "3200x1080"
    window.form_state.l_display = "1920x1080"
    window.form_state.r_display = "1280x1024"
    window.form_state.margins = "100,150,80,90"

    assert window.on_change_margin_text_mode("params") is True
    assert window.on_change_margin_text_position("right") is True

    assert window.status_phase == "margins"
    assert window.status_message == "margin text ready in right top position (1030x80)"
    assert window.last_error == ""


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

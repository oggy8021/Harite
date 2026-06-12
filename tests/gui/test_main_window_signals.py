from pathlib import Path

from PIL import Image
import pytest

from harite.apply_settings import EffectiveApplySettings
from harite.apply_surface import preview_assist_summary, preview_result_notes
from harite.settings_file import load_settings
from harite.settings_file import save_settings
from harite.display_context import TwoScreenOptimizeContext
from harite.settings import AppSettings
from harite.gui.views.main_window import MainWindow
from harite.workspace import Display

from tests.gui.conftest import patch_detect_displays


def test_on_change_input_text_updates_state():
    window = MainWindow()

    window.on_change_input_text("")
    assert window.can_optimize is False
    assert window.last_error == "input is required"

    window.on_change_input_text("a.jpg")
    assert window.can_optimize is True
    assert window.last_error == ""


def test_can_optimize_with_detected_display(monkeypatch):
    window = MainWindow()
    monkeypatch.setattr(
        "harite.workspace.detect_displays",
        lambda: [Display(name="", width=1920, height=1080, x_offset=0)],
    )

    window.on_change_input_text("a.jpg")

    assert window.can_optimize is True
    assert window.status_message == "input ready"


def test_on_change_input_text_disables_optimize_when_display_unresolved(monkeypatch):
    patch_detect_displays(monkeypatch, lambda: [])
    window = MainWindow()

    window.on_change_input_text("a.jpg")

    assert window.can_optimize is False
    assert window.status_phase == "optimize"
    assert window.status_message == "display context is unresolved"
    assert window.last_error == "display context is unresolved"
    assert window.on_optimize() is False
    assert window.status_message == "display context is unresolved"


def test_on_clear_input_resets_optimize_state():
    window = MainWindow()
    window.on_change_input_text("a.jpg")
    assert window.on_save_as() is True
    assert window.save_path_dialog_open is True

    ok = window.on_clear_input("L")

    assert ok is True
    assert window.can_optimize is False
    assert window.save_path_dialog_open is False
    assert window.status_phase == "input"
    assert window.status_message == "input is required"


def test_on_clear_input_rejects_invalid_side():
    window = MainWindow()
    window.on_change_input_text("a.jpg")

    ok = window.on_clear_input("")

    assert ok is False
    assert window.last_error == "input clear side is required"


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

    assert window.on_save_path_selected("") is False
    assert window.status_level == "idle"
    assert window.status_phase == "save_path"
    assert window.status_message == "save path ignored (closed)"

    assert window.on_save_as() is True
    assert window.on_save_path_selected("") is False
    assert window.status_level == "error"
    assert window.status_phase == "save_path"
    assert window.status_message == "save path is required"
    assert window.last_error == "save path is required"

    assert window.on_save_path_selected("/tmp/result.jpg") is False
    assert window.form_state.save_path == "/tmp/result.jpg"
    assert window.status_level == "error"
    assert window.status_phase == "save"
    assert window.status_message == "input is required"


def test_save_path_selected_uses_explicit_existing_path():
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

    ok = window.on_save_path_selected("/tmp/existing-save.jpg")

    assert ok is True
    assert window.save_path_dialog_open is False
    assert window.form_state.save_path == "/tmp/existing-save.jpg"
    assert window.save_target_display == "Export target: /tmp/existing-save.jpg"
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


def test_save_path_selected_propagates_unexpected_export_runtime_error(tmp_path):
    class DummyController:
        def run_export(self, _form_state, _save_path):
            raise RuntimeError("export runtime exploded")

    window = MainWindow()
    window.controller = DummyController()
    window.on_change_input_text("a.jpg")
    assert window.on_save_as() is True

    picked = tmp_path / "picked" / "save-path.jpg"

    with pytest.raises(RuntimeError, match="export runtime exploded"):
        window.on_save_path_selected(str(picked))


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
    assert bp["status"]["save_target"] == "Export target: not-selected"
    assert bp["status"]["slideshow_sources"] == "Slideshow srcdirs: L=- | R=-"
    assert bp["status"]["slideshow_current"] == "Slideshow current: idle"


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

    assert window.save_target_display == "Export target: not-selected"

    assert window.on_save_as() is True
    assert window.save_target_display == "Export target: not-selected"

    assert window.on_save_path_selected("/tmp/result.jpg") is True
    assert window.save_target_display == "Export target: /tmp/result.jpg"


def test_on_optimize_runs_and_logs(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "harite.workspace.detect_displays",
        lambda: [Display(name="", width=320, height=180, x_offset=0)],
    )
    window = MainWindow()

    img_path = tmp_path / "in.jpg"
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    Image.new("RGB", (120, 80), color=(10, 20, 30)).save(img_path)

    window.form_state.output_dir = str(out_dir)
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


def test_on_optimize_propagates_unexpected_runtime_error(monkeypatch):
    monkeypatch.setattr(
        "harite.workspace.detect_displays",
        lambda: [Display(name="", width=320, height=180, x_offset=0)],
    )
    window = MainWindow()
    window.form_state.output_dir = "/tmp/out"
    window.on_change_input_text("a.jpg")

    monkeypatch.setattr(
        window.controller,
        "run_optimize",
        lambda _state: (_ for _ in ()).throw(RuntimeError("optimize runtime exploded")),
    )

    with pytest.raises(RuntimeError, match="optimize runtime exploded"):
        window.on_optimize()


def test_build_result_preview_state_uses_latest_saved_file(tmp_path):
    window = MainWindow()
    saved = tmp_path / "result.jpg"
    saved.write_bytes(b"x")

    window.last_saved_files = [saved]
    window.apply_mode = "single-file"
    window.form_state.input_value = "single-source.jpg"

    state = window.build_result_preview_state()

    assert state.source_file == saved
    assert state.apply_mode == window.apply_mode
    assert state.assist_summary == preview_assist_summary(window.apply_mode, None, None)
    assert state.l_assignment == "L display <- single-source.jpg"
    assert state.r_assignment == "R display <- single-source.jpg"
    assert state.l_result_note == "Result: full optimized image"
    assert state.r_result_note == "Result: full optimized image"


def test_build_result_preview_state_includes_two_screen_display_sizes(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "harite.gui.views.main_window_preview.resolve_optimize_display_settings",
        lambda **_kwargs: type(
            "S",
            (),
            {
                "l_display": "200x180",
                "r_display": "120x180",
                "resolution": "320x180",
                "two_screen": True,
                "canvas_scale_percent": 100,
            },
        )(),
    )
    window = MainWindow()
    saved = tmp_path / "result.jpg"
    saved.write_bytes(b"x")

    window.last_saved_files = [saved]
    window.apply_mode = "per-monitor-auto-split"
    window.form_state.input_value = "left.jpg,right.jpg"

    state = window.build_result_preview_state()

    assert state.source_file == saved
    assert state.apply_mode == "per-monitor-auto-split"
    assert state.l_display == (200, 180)
    assert state.r_display == (120, 180)
    assert state.assist_summary == preview_assist_summary(
        window.apply_mode,
        state.l_display,
        state.r_display,
    )
    assert state.l_assignment == "L display <- left.jpg"
    assert state.r_assignment == "R display <- right.jpg"
    l_result_note, r_result_note = preview_result_notes(window.apply_mode)
    assert state.l_result_note == l_result_note
    assert state.r_result_note == r_result_note


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


def test_build_result_preview_state_propagates_unexpected_display_settings_failure(tmp_path, monkeypatch):
    window = MainWindow()
    saved = tmp_path / "result.jpg"
    saved.write_bytes(b"x")

    window.last_saved_files = [saved]
    window.form_state.input_value = "left.jpg,right.jpg"

    monkeypatch.setattr(
        "harite.gui.views.main_window_preview.resolve_optimize_display_settings",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("preview display settings failed")),
    )

    with pytest.raises(RuntimeError, match="preview display settings failed"):
        window.build_result_preview_state()


def test_on_close_marks_window_closed():
    window = MainWindow()
    assert window.closed is False

    window.on_close()
    assert window.closed is True
    assert "Window closed" in window.logs


def test_on_pick_input_rejects_invalid_side():
    window = MainWindow()

    window.on_pick_input("a.jpg", "")

    assert window.last_error == "input side is required"
    assert window.form_state.input_value == ""
    assert window.can_optimize is False


def test_on_pick_input_updates_side_specific_paths():
    window = MainWindow()

    window.on_pick_input("left-a.jpg", "L")
    window.on_pick_input("right-a.jpg", "R")
    window.on_pick_input("left-b.jpg", "L")

    assert window.input_path_l == "left-b.jpg"
    assert window.input_path_r == "right-a.jpg"
    assert window.form_state.input_value == "left-b.jpg,right-a.jpg"
    assert window.can_optimize is True


def test_dual_input_enables_optimize_when_two_displays_exist(monkeypatch):
    monkeypatch.setattr(
        "harite.optimize_settings.build_two_screen_optimize_context",
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

    assert window.can_optimize is True
    resolved = window._resolved_display_settings()
    assert resolved.two_screen is True
    assert resolved.resolution == "3200x1080"


def test_dual_input_blocks_optimize_when_second_input_removed_with_one_display(monkeypatch):
    patch_detect_displays(
        monkeypatch,
        lambda: [Display(name="", width=1600, height=900, x_offset=0)],
    )

    window = MainWindow()
    window.on_pick_input("left.jpg", "L")
    window.on_pick_input("right.jpg", "R")
    assert window.can_optimize is False

    window.on_change_input_text("left.jpg")

    assert window.can_optimize is True


def test_dual_input_blocks_when_only_one_display_detected(monkeypatch):
    monkeypatch.setattr(
        "harite.optimize_settings.build_two_screen_optimize_context",
        lambda: None,
    )

    window = MainWindow()
    window.on_pick_input("left.jpg", "L")
    window.on_pick_input("right.jpg", "R")

    assert window.can_optimize is False


def test_on_change_margins_updates_form_state():
    window = MainWindow()

    window.on_change_margins("spnLeftMargin", 10)
    window.on_change_margins("spnRightMargin", 20)
    window.on_change_margins("spnTopMargin", 30)
    window.on_change_margins("spnBottomMargin", 40)

    assert window.form_state.margins == "10,20,30,40"
    assert window.last_error == ""

    window.on_change_margins("spnLeftMargin", -1)
    assert window.last_error == "margins must be non-negative"


def test_on_change_margins_keeps_previous_value_on_invalid_input():
    window = MainWindow()
    window.form_state.margins = "1,2,3,4"

    window.on_change_margins("spnLeftMargin", -1)

    assert window.form_state.margins == "1,2,3,4"
    assert window.last_error == "margins must be non-negative"


def test_on_change_margins_supports_single_widget_update():
    window = MainWindow()

    window.form_state.margins = "1,2,3,4"
    window.on_change_margins("spnTopMargin", 99)

    assert window.form_state.margins == "1,2,99,4"
    assert window.last_error == ""


def test_on_change_all_margins_sets_uniform_values():
    window = MainWindow()

    window.on_change_margins("spnAllMargins", 12)

    assert window.form_state.margins == "12,12,12,12"
    assert window.last_error == ""


def test_on_change_all_margins_zero_resets_default():
    window = MainWindow()
    window.form_state.margins = "5,5,5,5"

    window.on_change_margins("spnAllMargins", 0)

    assert window.form_state.margins == "0,0,0,0"


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

        def apply(self, path: str) -> bool:
            self.calls.append(path)
            return True

    plugin = DummyPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)

    window = MainWindow()
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")
    window.last_saved_files = [wall]

    ok = window.on_apply()
    assert ok is True
    assert plugin.calls == [str(wall)]
    assert any("Applied wallpaper" in line for line in window.logs)


def test_on_change_apply_mode_accepts_per_monitor_auto_split():
    window = MainWindow()

    ok = window.on_change_apply_mode("per-monitor-auto-split")

    assert ok is True
    assert window.apply_mode == "per-monitor-auto-split"
    assert window.last_error == ""


def test_on_change_slideshow_mode_accepts_random():
    window = MainWindow()

    ok = window.on_change_slideshow_mode("random")

    assert ok is True
    assert window.slideshow_mode == "random"
    assert window._slideshow_active_mode == "random"
    assert window.last_error == ""


def test_running_slideshow_keeps_active_mode_until_stop(monkeypatch, tmp_path):
    window = MainWindow()
    window.slideshow_mode = "sequential"
    window._slideshow_active_mode = "sequential"
    window.slideshow_running = True
    observed: dict[str, str] = {}

    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")

    def fake_run_slideshow_cycle(images, mode, state, rng=None):
        observed["mode"] = mode
        return images[0], state

    monkeypatch.setattr("harite.gui.views.main_window.run_slideshow_cycle", fake_run_slideshow_cycle)

    assert window.on_change_slideshow_mode("random") is True
    assert window._run_slideshow_cycle_for_side("L", left_dir) == str(left_dir / "left-1.jpg")
    assert window.slideshow_mode == "random"
    assert observed["mode"] == "sequential"


def test_on_apply_per_monitor_auto_split_uses_split_mapping(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path) -> bool:
            self.calls.append(path)
            return True

    plugin = DummyPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)
    monkeypatch.setattr(
        "harite.gui.views.main_window.resolve_apply_settings",
        lambda **_kwargs: EffectiveApplySettings(
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
    assert plugin.calls == [{"HDMI-1": tmp_path / "wall_HDMI-1.jpg", "DP-1": tmp_path / "wall_DP-1.jpg"}]
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


def test_open_settings_dialog_tracks_state(monkeypatch):
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: TwoScreenOptimizeContext(
            displays=(
                Display(name="L", width=2560, height=1440, x_offset=0),
                Display(name="R", width=1536, height=864, x_offset=2560),
            ),
            resolution=(4096, 1440),
            l_display=(2560, 1440),
            r_display=(1536, 864),
        ),
    )

    window = MainWindow()
    window.form_state.input_value = "left.jpg,right.jpg"

    ok = window.on_open_settings_dialog()

    assert ok is True
    assert window.settings_dialog_open is True
    assert "Settings dialog opened" in window.logs


def test_apply_settings_updates_runtime_state():
    window = MainWindow()
    settings = AppSettings.from_settings_dict(
        {
            "canvas_scale_percent": 75,
            "plugin": "linux",
            "apply_mode": "per-monitor-auto-split",
            "slideshow_interval_seconds": 120,
            "slideshow_mode": "random",
            "slideshow_srcdir_l": "/slideshow/left",
            "slideshow_srcdir_r": "/slideshow/right",
        },
        default_plugin=window.plugin_name,
    )

    ok = window.on_apply_settings(settings)

    assert ok is True
    assert window.form_state.canvas_scale_percent == 75
    assert window.plugin_name == "linux"
    assert window.apply_mode == "per-monitor-auto-split"
    assert window.slideshow_interval_seconds == 120
    assert window.slideshow_mode == "random"
    assert window.slideshow_srcdir_l == "/slideshow/left"
    assert window.slideshow_srcdir_r == "/slideshow/right"
    assert window.slideshow_source_display == "Slideshow srcdirs: L=/slideshow/left | R=/slideshow/right"


def test_export_and_reload_settings_round_trips():
    window = MainWindow()
    window.form_state.canvas_scale_percent = 80
    window.plugin_name = "linux"
    window.apply_mode = "per-monitor-auto-split"
    window.slideshow_interval_seconds = 90
    window.slideshow_mode = "random"
    window.slideshow_srcdir_l = "/slideshow/left"
    window.slideshow_srcdir_r = "/slideshow/right"
    window._update_slideshow_source_display()

    exported = window.export_settings()

    assert exported["canvas_scale_percent"] == 80
    assert exported["align"] == ["center", "center"]
    assert exported["valign"] == ["center", "center"]
    assert exported["plugin"] == "linux"
    assert exported["apply_mode"] == "per-monitor-auto-split"
    assert exported["slideshow_interval_seconds"] == 90
    assert exported["slideshow_mode"] == "random"
    assert exported["slideshow_srcdir_l"] == "/slideshow/left"
    assert exported["slideshow_srcdir_r"] == "/slideshow/right"

    other = MainWindow()
    assert other.load_settings(exported) is True
    assert other.form_state.canvas_scale_percent == 80
    assert other.form_state.align == ("center", "center")
    assert other.form_state.valign == ("center", "center")
    assert other.plugin_name == "linux"
    assert other.slideshow_interval_seconds == 90
    assert other.slideshow_mode == "random"
    assert other.slideshow_srcdir_l == "/slideshow/left"
    assert other.slideshow_srcdir_r == "/slideshow/right"


def test_get_settings_expands_current_detected_display_values(monkeypatch):
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

    settings = window.on_get_settings()

    assert "resolution" not in settings
    assert "two_screen" not in settings
    assert "l_display" not in settings
    assert "r_display" not in settings


def test_get_settings_uses_auto_for_fully_unresolved_defaults(monkeypatch):
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: None,
    )
    window = MainWindow()

    settings = window.on_get_settings()

    assert "resolution" not in settings
    assert "l_display" not in settings
    assert "r_display" not in settings


def test_settings_file_save_normalizes_fully_unresolved_defaults(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: None,
    )
    window = MainWindow()
    target = tmp_path / "settings-unresolved.json"

    assert window.on_save_settings_file(str(target)) is True

    saved = load_settings(target)
    assert "resolution" not in saved
    assert "l_display" not in saved
    assert "r_display" not in saved


def test_settings_file_save_prefers_detected_display_context_without_inputs(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: TwoScreenOptimizeContext(
            displays=(
                Display(name="L", width=2048, height=1280, x_offset=0),
                Display(name="R", width=2048, height=1280, x_offset=2048),
            ),
            resolution=(4096, 1280),
            l_display=(2048, 1280),
            r_display=(2048, 1280),
        ),
    )
    window = MainWindow()
    target = tmp_path / "settings-detected.json"

    assert window.on_save_settings_file(str(target)) is True

    saved = load_settings(target)
    assert "resolution" not in saved
    assert "l_display" not in saved
    assert "r_display" not in saved


def test_settings_file_load_without_canvas_scale_keeps_default(tmp_path, monkeypatch):
    patch_detect_displays(monkeypatch, lambda: [])
    target = tmp_path / "settings-missing-display.json"
    target.write_text('{"plugin":"linux","apply_mode":"per-monitor-auto-split"}', encoding="utf-8")

    window = MainWindow()

    assert window.on_load_settings_file(str(target)) is True
    assert window.form_state.canvas_scale_percent == 100


def test_settings_file_save_and_load_round_trip(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: None,
    )
    window = MainWindow()
    window.form_state.canvas_scale_percent = 80
    window.plugin_name = "linux"
    window.apply_mode = "per-monitor-auto-split"
    window.slideshow_interval_seconds = 75
    window.slideshow_srcdir_l = "/slideshow/left"
    window.slideshow_srcdir_r = "/slideshow/right"

    target = tmp_path / "settings.json"

    assert window.on_save_settings_file(str(target)) is True
    assert target.exists() is True

    other = MainWindow()
    assert other.on_load_settings_file(str(target)) is True
    assert other.form_state.canvas_scale_percent == 80
    assert other.form_state.align == ("center", "center")
    assert other.form_state.valign == ("center", "center")
    assert other.plugin_name == "linux"
    assert other.apply_mode == "per-monitor-auto-split"
    assert other.slideshow_interval_seconds == 75
    assert other.slideshow_srcdir_l == "/slideshow/left"
    assert other.slideshow_srcdir_r == "/slideshow/right"


def test_settings_file_save_uses_default_fixed_path_when_path_is_empty(monkeypatch, tmp_path):
    window = MainWindow()
    target = tmp_path / "xdg-config" / "harite" / "harite-settings.json"
    monkeypatch.setattr("harite.gui.views.main_window.resolve_default_settings_path", lambda: target)

    assert window.on_save_settings_file("") is True
    assert target.exists() is True


def test_settings_file_save_accepts_path_object(tmp_path):
    window = MainWindow()
    target = tmp_path / "harite-settings.json"

    assert window.on_save_settings_file(target) is True
    assert target.exists() is True


def test_settings_file_load_rejects_empty_path():
    window = MainWindow()

    assert window.on_load_settings_file("") is False
    assert window.status_phase == "settings"
    assert window.last_error == "settings path is required"


def test_settings_file_load_propagates_unexpected_runtime_error(monkeypatch, tmp_path):
    window = MainWindow()
    target = tmp_path / "settings.json"
    target.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(
        "harite.gui.views.main_window.load_settings",
        lambda _path: (_ for _ in ()).throw(RuntimeError("settings load probe failed")),
    )

    with pytest.raises(RuntimeError, match="settings load probe failed"):
        window.on_load_settings_file(str(target))


def test_main_window_loads_default_settings_on_startup(monkeypatch, tmp_path):
    target = tmp_path / "harite-settings.json"
    save_settings(
        target,
        {
            "plugin": "linux",
            "apply_mode": "per-monitor-auto-split",
            "slideshow_interval_seconds": 33,
            "slideshow_srcdir_l": "/slideshow/left",
            "slideshow_srcdir_r": "/slideshow/right",
        },
    )
    monkeypatch.setattr("harite.gui.views.main_window.resolve_default_settings_path", lambda: target)

    window = MainWindow()

    assert window.plugin_name == "linux"
    assert window.apply_mode == "per-monitor-auto-split"
    assert window.slideshow_interval_seconds == 33
    assert window.slideshow_srcdir_l == "/slideshow/left"
    assert window.slideshow_srcdir_r == "/slideshow/right"
    assert window.can_start_slideshow is True


def test_main_window_startup_settings_load_propagates_unexpected_runtime_error(monkeypatch, tmp_path):
    target = tmp_path / "harite-settings.json"
    target.write_text("{}", encoding="utf-8")
    monkeypatch.setattr("harite.gui.views.main_window.resolve_default_settings_path", lambda: target)
    monkeypatch.setattr(
        "harite.gui.views.main_window.load_settings",
        lambda _path: (_ for _ in ()).throw(RuntimeError("startup settings probe failed")),
    )

    with pytest.raises(RuntimeError, match="startup settings probe failed"):
        MainWindow()


def test_settings_file_save_accepts_explicit_dialog_settings(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: None,
    )
    window = MainWindow()
    target = tmp_path / "settings-dialog.json"

    assert window.on_save_settings_file(
        str(target),
        {
            "canvas_scale_percent": 90,
            "plugin": "linux",
            "apply_mode": "per-monitor-auto-split",
            "slideshow_interval_seconds": 33,
            "slideshow_srcdir_l": "/slideshow/left",
        },
    ) is True

    loaded = window.on_load_settings_file(str(target))

    assert loaded is True
    assert window.form_state.canvas_scale_percent == 90
    assert window.plugin_name == "linux"
    assert window.apply_mode == "per-monitor-auto-split"
    assert window.slideshow_interval_seconds == 33
    assert window.slideshow_srcdir_l == "/slideshow/left"


def test_settings_file_save_propagates_unexpected_payload_build_failure(monkeypatch, tmp_path):
    window = MainWindow()
    target = tmp_path / "settings-dialog.json"

    monkeypatch.setattr(
        window,
        "_build_settings_dialog_config",
        lambda: (_ for _ in ()).throw(RuntimeError("settings payload build failed")),
    )

    with pytest.raises(RuntimeError, match="settings payload build failed"):
        window.on_save_settings_file(str(target))


def test_settings_file_round_trips_explicit_apply_mode_without_gui_projection(tmp_path):
    window = MainWindow()
    target = tmp_path / "settings-explicit.json"

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


def test_slideshow_handlers_use_srcdirs_and_interval_validation(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str) -> bool:
            return True

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())

    window = MainWindow()
    window.slideshow_mode = "sequential"

    assert window.on_slideshow_start() is False
    assert window.status_level == "error"
    assert window.status_phase == "slideshow"
    assert window.last_error == "slideshow srcdir is required"

    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.slideshow_source_display == f"Slideshow srcdirs: L={left_dir} | R=-"

    assert window.on_slideshow_start() is True
    assert window.slideshow_running is True
    assert window.status_level == "success"
    assert window.status_phase == "slideshow"
    assert window.status_message == "slideshow started"
    assert window.slideshow_current_display == "Slideshow current: L=left-1.jpg | R=-"

    (left_dir / "left-2.jpg").write_bytes(b"left-2")

    assert window.on_slideshow_tick() is True
    assert window.slideshow_current_display == "Slideshow current: L=left-2.jpg | R=-"

    assert window.on_slideshow_stop() is True
    assert window.slideshow_running is False
    assert window.status_level == "idle"
    assert window.status_phase == "slideshow"
    assert window.status_message == "slideshow stopped"

    assert window.on_slideshow_tick() is False

    assert window.on_slideshow_interval_change(120) is True
    assert window.slideshow_interval_seconds == 120
    assert window.status_level == "idle"
    assert window.status_phase == "slideshow"
    assert window.status_message == "slideshow interval updated: 120s"

    assert window.on_slideshow_interval_change(0) is False
    assert window.status_level == "error"
    assert window.status_phase == "slideshow"
    assert window.last_error == "slideshow interval must be positive"


def test_slideshow_tick_writes_op_log_steps(monkeypatch, tmp_path):
    import json

    class DummyPlugin:
        def apply(self, path: str) -> bool:
            return True

    log_path = tmp_path / "slideshow-op.jsonl"
    monkeypatch.setenv("HARITE_SLIDESHOW_OP_LOG", str(log_path))
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())
    monkeypatch.setattr("harite.gui.views.main_window.dual_display_detected", lambda: False)

    work_dir = tmp_path / "Pictures" / "Harite" / "slideshow"
    composite = work_dir / "harite_slideshow.jpg"

    window = MainWindow()

    def fake_run_slideshow_optimize(_state):
        work_dir.mkdir(parents=True, exist_ok=True)
        composite.write_bytes(b"x")
        return [composite], []

    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)
    monkeypatch.setattr(window, "_resolve_slideshow_work_dir", lambda: work_dir)

    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_slideshow_start() is True
    log_path.write_text("", encoding="utf-8")

    assert window.on_slideshow_tick() is True

    records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    steps = [record["step"] for record in records]
    assert "SLIDESHOW_TICK" in steps
    assert "SLIDESHOW_APPLY" in steps
    assert any(record["step"] == "SLIDESHOW_TICK" and record.get("ok") is True for record in records)


def test_slideshow_current_display_abbreviates_long_paths():
    window = MainWindow()
    long_path = "G:/My Drive/very/long/nested/folder/structure/wallpaper.jpg"
    window.slideshow_running = True
    window._update_slideshow_current_display(long_path, "-")
    assert long_path not in window.slideshow_current_display
    assert "wallpaper.jpg" in window.slideshow_current_display


def test_slideshow_single_source_applies_on_start_and_tick(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path: str) -> bool:
            self.calls.append(path)
            return True

    plugin = DummyPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)

    work_dir = tmp_path / "Pictures" / "Harite" / "slideshow"
    composite = work_dir / "harite_slideshow.jpg"

    window = MainWindow()
    window.slideshow_mode = "sequential"

    def fake_run_slideshow_optimize(state):
        work_dir.mkdir(parents=True, exist_ok=True)
        composite.write_bytes(state.input_value.encode("utf-8"))
        return [composite], []

    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)
    monkeypatch.setattr(window, "_resolve_slideshow_work_dir", lambda: work_dir)

    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_slideshow_start() is True
    assert plugin.calls == [str(composite)]

    assert window.on_slideshow_tick() is True
    assert plugin.calls[-1] == str(composite)

    assert window.on_slideshow_stop() is True


def test_slideshow_single_source_start_fails_when_plugin_apply_fails(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str) -> bool:
            return False

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())

    work_dir = tmp_path / "Pictures" / "Harite" / "slideshow"
    composite = work_dir / "harite_slideshow.jpg"

    window = MainWindow()

    def fake_run_slideshow_optimize(_state):
        work_dir.mkdir(parents=True, exist_ok=True)
        composite.write_bytes(b"x")
        return [composite], []

    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)
    monkeypatch.setattr(window, "_resolve_slideshow_work_dir", lambda: work_dir)

    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_slideshow_start() is False
    assert window.slideshow_running is False
    assert window.status_level == "error"
    assert window.status_phase == "slideshow"
    assert window.status_message == "slideshow start single-file apply failed"
    assert window.last_error == "slideshow start single-file apply failed"


def test_slideshow_start_normalizes_empty_output_dir(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str) -> bool:
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

    work_dir = home / "Pictures" / "Harite" / "slideshow"
    composite = work_dir / "harite_slideshow.jpg"

    def fake_run_slideshow_optimize(_state):
        work_dir.mkdir(parents=True, exist_ok=True)
        composite.write_bytes(b"x")
        return [composite], []

    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)

    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_slideshow_start() is True
    assert window.form_state.output_dir == str(home / "Pictures")
    assert window.slideshow_output_display == f"Slideshow output: {home / 'Pictures' / 'Harite' / 'slideshow'}"


def test_slideshow_start_propagates_unexpected_autosplit_prepare_failure(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str) -> bool:
            return True

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: TwoScreenOptimizeContext(
            displays=(
                Display(name="L", width=1920, height=1080, x_offset=0),
                Display(name="R", width=1920, height=1080, x_offset=1920),
            ),
            resolution=(3840, 1080),
            l_display=(1920, 1080),
            r_display=(1920, 1080),
        ),
    )

    window = MainWindow()
    window.plugin_name = "linux"
    monkeypatch.setattr(
        window.controller,
        "run_slideshow_optimize",
        lambda _state: (_ for _ in ()).throw(RuntimeError("slideshow autosplit prepare exploded")),
    )

    left_dir = tmp_path / "slideshow-left"
    right_dir = tmp_path / "slideshow-right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (right_dir / "right-1.png").write_bytes(b"right")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_pick_slideshow_srcdir(str(right_dir), "R") is True

    with pytest.raises(RuntimeError, match="slideshow autosplit prepare exploded"):
        window.on_slideshow_start()


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
    assert window.slideshow_output_display == f"Slideshow output: {home / 'MyPictures' / 'Harite' / 'slideshow'}"


def test_main_window_defaults_output_dir_to_home_pictures_when_xdg_config_missing(monkeypatch, tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr("harite.gui.views.main_window.Path.home", lambda: home)
    monkeypatch.delenv("XDG_PICTURES_DIR", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "missing-xdg-config"))
    monkeypatch.setattr("harite.gui.views.main_window.sys.platform", "linux")

    window = MainWindow()

    assert window.form_state.output_dir == str(home / "Pictures")
    assert window.slideshow_output_display == f"Slideshow output: {home / 'Pictures' / 'Harite' / 'slideshow'}"


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
    assert window.slideshow_output_display == f"Slideshow output: {home / 'Pictures' / 'Harite' / 'slideshow'}"


def test_main_window_windows_pictures_probe_propagates_unexpected_runtime_error(monkeypatch):
    monkeypatch.setattr("harite.gui.views.main_window.sys.platform", "win32")
    monkeypatch.setattr(
        "harite.gui.views.main_window.ctypes.create_unicode_buffer",
        lambda _size: (_ for _ in ()).throw(RuntimeError("pictures probe failed")),
    )

    with pytest.raises(RuntimeError, match="pictures probe failed"):
        MainWindow()._resolve_windows_pictures_dir()


def test_slideshow_single_source_tick_stops_when_plugin_apply_fails(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = 0

        def apply(self, path: str) -> bool:
            self.calls += 1
            return self.calls == 1

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())
    monkeypatch.setattr("harite.gui.views.main_window.dual_display_detected", lambda: False)

    work_dir = tmp_path / "Pictures" / "Harite" / "slideshow"
    composite = work_dir / "harite_slideshow.jpg"

    window = MainWindow()

    def fake_run_slideshow_optimize(_state):
        work_dir.mkdir(parents=True, exist_ok=True)
        composite.write_bytes(b"x")
        return [composite], []

    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)
    monkeypatch.setattr(window, "_resolve_slideshow_work_dir", lambda: work_dir)
    window.slideshow_srcdir_r = ""
    window.slideshow_source_id_r = ""
    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_slideshow_start() is True
    assert window.on_slideshow_tick() is False
    assert window.slideshow_running is False
    # P-03: single display allows restart with L-only srcdir after stop.
    assert window.can_start_slideshow is True
    assert window.status_level == "error"
    assert window.status_phase == "slideshow"
    assert window.status_message == "slideshow cycle single-file apply failed"
    assert window.last_error == "slideshow cycle single-file apply failed"


def test_slideshow_dual_source_cycle_pauses_when_detected_displays_temporarily_drop(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, _path: object) -> bool:
            return True

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())
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

    composite = tmp_path / "slideshow-composite.jpg"
    composite.write_bytes(b"composite")

    window = MainWindow()
    window.plugin_name = "linux"

    optimize_calls = 0

    def fake_run_slideshow_optimize(state):
        nonlocal optimize_calls
        optimize_calls += 1
        return ([composite], [])

    def fake_resolve_apply_settings(**_kwargs):
        if optimize_calls == 1:
            return EffectiveApplySettings(
                apply_mode="per-monitor-auto-split",
                target={"HDMI-1": str(tmp_path / "split1.jpg"), "DP-1": str(tmp_path / "split2.jpg")},
            )
        raise ValueError("per-monitor apply requires at least two detected displays")

    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)
    monkeypatch.setattr("harite.gui.views.main_window.resolve_apply_settings", fake_resolve_apply_settings)

    left_dir = tmp_path / "slideshow-left"
    right_dir = tmp_path / "slideshow-right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")
    (right_dir / "right-1.png").write_bytes(b"right")
    (right_dir / "right-2.png").write_bytes(b"right-2")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_pick_slideshow_srcdir(str(right_dir), "R") is True
    assert window.on_slideshow_start() is True

    assert window.on_slideshow_tick() is True
    assert window.slideshow_running is True
    assert window.slideshow_paused is True
    assert window.can_start_slideshow is False
    assert window.slideshow_summary_display == "Slideshow: paused"
    assert window.status_level == "paused"
    assert window.status_message == "slideshow paused: waiting for two detected displays for auto-split"
    assert window.last_error == ""


def test_slideshow_dual_source_cycle_resumes_after_transient_display_drop(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path: object) -> bool:
            self.calls.append(path)
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

    composite = tmp_path / "slideshow-composite.jpg"
    composite.write_bytes(b"composite")
    composite2 = tmp_path / "slideshow-composite-2.jpg"
    composite2.write_bytes(b"composite2")
    split1_hdmi = str(tmp_path / "split1.jpg")
    split1_dp = str(tmp_path / "split2.jpg")
    split2_hdmi = str(tmp_path / "split3.jpg")
    split2_dp = str(tmp_path / "split4.jpg")

    window = MainWindow()
    window.plugin_name = "linux"

    optimize_calls = 0
    resolve_calls = 0

    def fake_run_slideshow_optimize(state):
        nonlocal optimize_calls
        optimize_calls += 1
        return ([composite], []) if optimize_calls < 3 else ([composite2], [])

    def fake_resolve_apply_settings(**_kwargs):
        nonlocal resolve_calls
        resolve_calls += 1
        if resolve_calls == 1:
            return EffectiveApplySettings(
                apply_mode="per-monitor-auto-split",
                target={"HDMI-1": split1_hdmi, "DP-1": split1_dp},
            )
        if resolve_calls == 2:
            raise ValueError("per-monitor apply requires at least two detected displays")
        return EffectiveApplySettings(
            apply_mode="per-monitor-auto-split",
            target={"HDMI-1": split2_hdmi, "DP-1": split2_dp},
        )

    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)
    monkeypatch.setattr("harite.gui.views.main_window.resolve_apply_settings", fake_resolve_apply_settings)

    left_dir = tmp_path / "slideshow-left"
    right_dir = tmp_path / "slideshow-right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")
    (right_dir / "right-1.png").write_bytes(b"right")
    (right_dir / "right-2.png").write_bytes(b"right-2")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_pick_slideshow_srcdir(str(right_dir), "R") is True
    assert window.on_slideshow_start() is True
    assert window.on_slideshow_tick() is True
    assert window.slideshow_paused is True

    assert window.on_slideshow_tick() is True
    assert window.slideshow_running is True
    assert window.slideshow_paused is False
    assert window.slideshow_summary_display == "Slideshow: running"
    assert window.status_message == "slideshow resumed"
    assert window.last_error == ""
    assert plugin.calls[-1] == {"HDMI-1": split2_hdmi, "DP-1": split2_dp}


def test_slideshow_single_source_success_cleans_previous_generated_files(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str) -> bool:
            return True

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())

    work_dir = tmp_path / "Pictures" / "Harite" / "slideshow"
    composite = work_dir / "harite_slideshow.jpg"

    window = MainWindow()

    def fake_run_slideshow_optimize(_state):
        work_dir.mkdir(parents=True, exist_ok=True)
        composite.write_bytes(b"x")
        return [composite], []

    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)
    monkeypatch.setattr(window, "_resolve_slideshow_work_dir", lambda: work_dir)

    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")

    old_composite = tmp_path / "harite_output_0001.jpg"
    old_split = tmp_path / "harite_output_0001_HDMI-1.jpg"
    old_composite.write_bytes(b"old-composite")
    old_split.write_bytes(b"old-split")
    window._slideshow_active_generated_files = (old_composite, old_split)

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_slideshow_start() is True

    assert old_composite.exists() is False
    assert old_split.exists() is False


def test_slideshow_dual_source_falls_back_to_per_monitor_auto_split(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path) -> bool:
            self.calls.append(path)
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

    # Use a deterministic XDG pictures root so work_dir is predictable
    home = tmp_path / "home"
    home.mkdir()
    xdg_config = tmp_path / "xdg-config"
    xdg_config.mkdir()
    (xdg_config / "user-dirs.dirs").write_text('XDG_PICTURES_DIR="$HOME/Pictures"\n', encoding="utf-8")
    monkeypatch.setattr("harite.gui.views.main_window.Path.home", lambda: home)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_config))
    monkeypatch.setattr("harite.gui.views.main_window.sys.platform", "linux")

    work_dir = home / "Pictures" / "Harite" / "slideshow"
    composite_slot = work_dir / "harite_slideshow.jpg"
    split_hdmi = work_dir / "harite_slideshow_HDMI-1.jpg"
    split_dp = work_dir / "harite_slideshow_DP-1.jpg"

    optimize_calls = 0
    resolve_calls = 0

    def fake_resolve_apply_settings(**kwargs):
        nonlocal resolve_calls
        resolve_calls += 1
        split_hdmi.write_bytes(f"split-hdmi-{resolve_calls}".encode())
        split_dp.write_bytes(f"split-dp-{resolve_calls}".encode())
        return EffectiveApplySettings(
            apply_mode="per-monitor-auto-split",
            target={"HDMI-1": str(split_hdmi), "DP-1": str(split_dp)},
        )

    monkeypatch.setattr("harite.gui.views.main_window.resolve_apply_settings", fake_resolve_apply_settings)

    window = MainWindow()
    window.plugin_name = "linux"
    window.slideshow_mode = "sequential"
    observed_inputs = []

    def fake_run_slideshow_optimize(state):
        nonlocal optimize_calls
        optimize_calls += 1
        observed_inputs.append(state.input_value)
        Path(state.output_dir).mkdir(parents=True, exist_ok=True)
        composite = Path(state.output_dir) / "harite_slideshow.jpg"
        composite.write_bytes(f"composite-{optimize_calls}".encode())
        return ([composite], [])

    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)

    left_dir = tmp_path / "slideshow-left"
    right_dir = tmp_path / "slideshow-right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")
    (right_dir / "right-1.png").write_bytes(b"right")
    (right_dir / "right-2.png").write_bytes(b"right-2")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_pick_slideshow_srcdir(str(right_dir), "R") is True
    assert window.on_slideshow_start() is True

    assert observed_inputs == [f"{left_dir / 'left-1.jpg'},{right_dir / 'right-1.png'}"]
    assert plugin.calls == [{"HDMI-1": str(split_hdmi), "DP-1": str(split_dp)}]
    assert any("Slideshow start per-monitor auto-split" in line for line in window.logs)
    assert composite_slot.exists() is True
    assert composite_slot.read_bytes() == b"composite-1"

    assert window.on_slideshow_tick() is True
    assert observed_inputs[-1] == f"{left_dir / 'left-2.jpg'},{right_dir / 'right-2.png'}"
    assert plugin.calls[-1] == {"HDMI-1": str(split_hdmi), "DP-1": str(split_dp)}
    assert composite_slot.exists() is True
    assert composite_slot.read_bytes() == b"composite-2"
    assert split_hdmi.read_bytes() == b"split-hdmi-2"
    assert split_dp.read_bytes() == b"split-dp-2"


def test_slideshow_dual_source_start_fails_without_two_detected_displays(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: None,
    )

    window = MainWindow()
    window.plugin_name = "linux"

    left_dir = tmp_path / "slideshow-left"
    right_dir = tmp_path / "slideshow-right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (right_dir / "right-1.png").write_bytes(b"right")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_pick_slideshow_srcdir(str(right_dir), "R") is True
    assert window.on_slideshow_start() is False
    assert window.slideshow_running is False
    assert window.status_level == "error"
    assert window.status_phase == "slideshow"
    assert window.status_message == "dual-source slideshow requires two detected displays"
    assert window.last_error == "dual-source slideshow requires two detected displays"
    assert any("Slideshow start blocked: dual-source slideshow requires two detected displays" in line for line in window.logs)


def test_prepare_slideshow_apply_allows_windows_dual_source(monkeypatch):
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: TwoScreenOptimizeContext(
            displays=(
                Display(name="\\\\.\\DISPLAY1", width=3840, height=2160, x_offset=0, y_offset=0),
                Display(name="\\\\.\\DISPLAY2", width=3840, height=2160, x_offset=3840, y_offset=0),
            ),
            resolution=(7680, 2160),
            l_display=(3840, 2160),
            r_display=(3840, 2160),
        ),
    )
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: object())

    window = MainWindow()
    window.plugin_name = "windows"

    assert window._prepare_slideshow_apply(2) is True
    assert window._slideshow_dual_auto_split_enabled is True


def test_slideshow_windows_dual_source_start_applies_single_file(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls: list[object] = []

        def apply(self, path: object) -> bool:
            self.calls.append(path)
            return True

    plugin = DummyPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)
    monkeypatch.setattr("harite.apply_settings.sys.platform", "win32")
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: TwoScreenOptimizeContext(
            displays=(
                Display(name="\\\\.\\DISPLAY1", width=3840, height=2160, x_offset=0, y_offset=0),
                Display(name="\\\\.\\DISPLAY2", width=3840, height=2160, x_offset=3840, y_offset=0),
            ),
            resolution=(7680, 2160),
            l_display=(3840, 2160),
            r_display=(3840, 2160),
        ),
    )

    window = MainWindow()
    window.plugin_name = "windows"
    window.form_state.output_dir = str(tmp_path / "Pictures")

    def fake_run_slideshow_optimize(state):
        out = Path(state.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        composite = out / "harite_slideshow.jpg"
        composite.write_bytes(b"composite-1")
        return ([composite], [])

    monkeypatch.setattr(window.controller, "run_slideshow_optimize", fake_run_slideshow_optimize)

    left_dir = tmp_path / "slideshow-left"
    right_dir = tmp_path / "slideshow-right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (right_dir / "right-1.png").write_bytes(b"right")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_pick_slideshow_srcdir(str(right_dir), "R") is True
    assert window.on_slideshow_start() is True
    assert len(plugin.calls) == 1
    assert Path(str(plugin.calls[0])).name == "harite_slideshow.jpg"
    assert any("Windows Span" in line for line in window.logs)


def test_slideshow_dual_source_start_rejects_unsupported_plugin(monkeypatch, tmp_path):
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

    window = MainWindow()
    window.plugin_name = "macos"

    left_dir = tmp_path / "slideshow-left"
    right_dir = tmp_path / "slideshow-right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (right_dir / "right-1.png").write_bytes(b"right")

    assert window.on_pick_slideshow_srcdir(str(left_dir), "L") is True
    assert window.on_pick_slideshow_srcdir(str(right_dir), "R") is True
    assert window.on_slideshow_start() is False
    assert "not supported for plugin macos" in window.last_error


def test_suggest_next_action_transitions(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "harite.workspace.detect_displays",
        lambda: [Display(name="", width=320, height=180, x_offset=0)],
    )
    window = MainWindow()
    assert window.suggest_next_action() == "input"

    img_path = tmp_path / "in.jpg"
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    Image.new("RGB", (120, 80), color=(10, 20, 30)).save(img_path)

    window.form_state.output_dir = str(out_dir)
    window.on_change_input_text(str(img_path))
    assert window.suggest_next_action() == "optimize"

    assert window.on_optimize() is True
    assert window.suggest_next_action() == "apply"


def test_run_primary_flow_step_runs_optimize_then_apply(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path: str) -> bool:
            self.calls.append(path)
            return True

    plugin = DummyPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)
    monkeypatch.setattr(
        "harite.workspace.detect_displays",
        lambda: [Display(name="", width=320, height=180, x_offset=0)],
    )

    window = MainWindow()
    img_path = tmp_path / "in.jpg"
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    Image.new("RGB", (120, 80), color=(10, 20, 30)).save(img_path)

    window.form_state.output_dir = str(out_dir)
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
    assert plugin.calls[-1] == str(window.last_saved_files[-1])


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

    window.on_pick_input("   ", "L")

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
    window.form_state.margins = "1,2,3,4"
    window.form_state.embed_text = "hello"
    preview = window.build_optimize_cli_preview()

    assert "--canvas-scale 100" in preview
    assert "--margins 1,2,3,4" in preview
    assert "--embed-text hello" in preview


def test_margin_text_change_handlers_update_form_state(monkeypatch):
    monkeypatch.setattr(
        "harite.workspace.detect_displays",
        lambda: [Display(name="", width=1920, height=1080, x_offset=0)],
    )
    window = MainWindow()
    window.form_state.margins = "10,10,20,30"
    window.on_change_input_text("a.jpg")

    assert window.on_change_margin_text_mode("combo") is True
    assert window.on_change_margin_text("hello") is True
    assert window.on_change_margin_text_position("right-bottom") is True
    assert window.on_change_margin_text_max_lines(4) is True

    assert window.form_state.embed_info == "combo"
    assert window.form_state.embed_text == "hello"
    assert window.form_state.embed_position == "right-bottom"
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


def test_margin_text_preflight_reports_margin_area_too_small(monkeypatch):
    monkeypatch.setattr(
        "harite.workspace.detect_displays",
        lambda: [Display(name="", width=1920, height=1080, x_offset=0)],
    )
    window = MainWindow()
    window.form_state.margins = "10,10,20,10"
    window.on_change_input_text("a.jpg")

    assert window.on_change_margin_text_mode("params") is True
    assert window.on_change_margin_text_position("right-bottom") is True

    assert window.status_phase == "margins"
    assert window.status_message == "margin text does not fit current margin area"
    assert window.last_error == "selected margin area is too small for margin text"


def test_margin_text_preflight_uses_display_slice_area_for_two_screen(monkeypatch):
    monkeypatch.setattr(
        "harite.optimize_settings.build_two_screen_optimize_context",
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
    window.form_state.margins = "100,150,80,90"
    window.on_change_input_text("left.jpg,right.jpg")

    assert window.on_change_margin_text_mode("params") is True
    assert window.on_change_margin_text_position("right-top") is True

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
        def apply(self, path: str) -> bool:
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
        def apply(self, path: str) -> bool:
            raise RuntimeError("boom")

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())

    window = MainWindow()
    wall = tmp_path / "wall.jpg"
    wall.write_bytes(b"x")
    window.last_saved_files = [wall]

    ok = window.on_apply()

    assert ok is False
    assert window.last_error == "failed to apply wallpaper: boom"


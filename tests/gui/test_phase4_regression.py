from pathlib import Path

from PIL import Image

from harite.gui.views.main_window import MainWindow


def _prepare_input(window: MainWindow, tmp_path: Path) -> Path:
    img_path = tmp_path / "in.jpg"
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    Image.new("RGB", (120, 80), color=(10, 20, 30)).save(img_path)
    window.form_state.output_dir = str(out_dir)
    window.form_state.resolution = "320x180"
    window.on_change_input_text(str(img_path))
    return img_path


def test_phase4_a_layout_structure_sections_are_stable():
    win = MainWindow()
    bp = win.get_layout_blueprint()

    section_names = [name for name, _items in bp["sections"]]
    assert section_names == ["hero", "optimize_panel", "apply_panel", "status_panel"]

    section_items = {name: items for name, items in bp["sections"]}
    assert "input_value" in section_items["hero"]
    assert "resolution" in section_items["hero"]
    assert "output_dir" in section_items["hero"]
    assert "plugin" in section_items["hero"]
    assert "apply_dry_run" in section_items["apply_panel"]
    assert "apply_do_it" in section_items["apply_panel"]


def test_phase4_b_status_running_success_on_optimize(tmp_path):
    win = MainWindow()
    _prepare_input(win, tmp_path)

    assert win.on_optimize() is True
    assert win.status_level == "success"
    assert win.status_phase == "optimize"
    assert win.status_message == "optimize completed"


def test_phase4_b_status_error_on_apply_failure(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str, *, dry_run: bool = True) -> bool:
            return False

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())

    win = MainWindow()
    _prepare_input(win, tmp_path)
    assert win.on_optimize() is True

    assert win.on_apply_dry_run() is False
    assert win.status_level == "error"
    assert win.status_phase == "apply"
    assert win.status_message == "apply failed"
    assert win.last_error == "failed to apply wallpaper"


def test_phase4_c_primary_flow_reaches_apply_in_two_steps(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path: str, *, dry_run: bool = True) -> bool:
            self.calls.append((path, dry_run))
            return True

    plugin = DummyPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)

    win = MainWindow()
    _prepare_input(win, tmp_path)

    assert win.run_primary_flow_step() is True  # optimize
    assert win.suggest_next_action() == "apply_dry_run"
    assert win.run_primary_flow_step() is True  # apply dry-run
    assert plugin.calls
    assert plugin.calls[-1][1] is True


def test_phase4_d_input_reset_clears_apply_readiness(tmp_path):
    win = MainWindow()
    _prepare_input(win, tmp_path)
    assert win.on_optimize() is True
    assert win.can_apply is True

    win.on_change_input_text("")

    assert win.can_optimize is False
    assert win.can_apply is False
    assert win.last_saved_files == []
    assert win.status_level == "error"
    assert win.status_phase == "input"
    assert win.status_message == "input is required"

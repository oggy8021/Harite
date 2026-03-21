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
    assert any(line.startswith("Saved ") for line in window.logs)
    assert any(line.startswith("Saved: ") for line in window.logs)


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

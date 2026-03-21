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

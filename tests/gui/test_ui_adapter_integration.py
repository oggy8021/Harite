from pathlib import Path

from harite.gui.views.main_window import MainWindow
from harite.gui.adapters.fake_adapter import create_fake_widget_map
from harite.gui.adapters.ui_loader import UiLoadResult


def test_fake_adapter_maps_signals_to_mainwindow():
    win = MainWindow()

    result = UiLoadResult(
        file_path=Path("/tmp/wallpositapplet.glade"),
        root_tag="interface",
        widget_count=5,
        signal_count=4,
    )

    widgets = create_fake_widget_map(win, result)

    # Simulate input text change
    widgets["input_text"]("/tmp/img.jpg")
    assert win.form_state.input_value == "/tmp/img.jpg"
    assert win.can_optimize is True

    # Simulate plugin change (valid or invalid handled by MainWindow)
    plugin_name = win.available_plugins[0] if win.available_plugins else "windows"
    widgets["plugin_change"](plugin_name)
    assert win.plugin_name == plugin_name

    # Simulate margins change
    widgets["margins_change"](1, 2, 3, 4)
    assert "1,2,3,4" in win.form_state.margins

    # Simulate toggle fixed
    widgets["toggle_fixed"](True)
    assert win.form_state.fixed is True

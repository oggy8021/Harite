from __future__ import annotations

from harite.gui.adapters.gtk_backend import GtkRuntimeSignalBackend
from harite.gui.views.main_window import MainWindow

from test_gtk_runtime_backend import _FakeGtk


def test_phase5_visual_tokens_snapshot_is_stable():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    from harite.apply_surface import apply_mode_help_text

    rad_per_monitor = backend.get_object("radApplyPerMonitor")
    initial_mode = (
        "per-monitor-auto-split"
        if rad_per_monitor.get_active()
        else "single-file"
    )
    active_radio = (
        backend.get_object("radApplyPerMonitor")
        if initial_mode == "per-monitor-auto-split"
        else backend.get_object("radApplySingle")
    )

    snapshot = {
        "main_section": backend.get_object("lblMainSection").text,
        "apply_mode_tooltip": active_radio.tooltip_text,
        "flow": backend.get_object("lblFlowLegend").text,
        "save": backend.get_object("btnSave").label,
        "optimize": backend.get_object("btnOptimize").label,
        "apply": backend.get_object("btnSetWall").label,
        "settings": backend.get_object("btnSetting").label,
        "about": backend.get_object("btnAbout").label,
        "open_l": backend.get_object("btnGetImgL").label,
        "open_r": backend.get_object("btnGetImgR").label,
    }

    assert snapshot == {
        "main_section": "Main",
        "apply_mode_tooltip": apply_mode_help_text(initial_mode),
        "flow": "Compose -> Optimize -> Apply",
        "save": "Export Image",
        "optimize": "Optimize",
        "apply": "Apply",
        "settings": "Settings",
        "about": "About",
        "open_l": "",
        "open_r": "",
    }


def test_phase5_runtime_smoke_optimize_then_apply_updates_visual_states():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    entry = backend.get_object("entPathL")
    save_btn = backend.get_object("btnSave")
    optimize_btn = backend.get_object("btnOptimize")
    apply_btn = backend.get_object("btnSetWall")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    backend.connect_signals({"on_change_input_text": lambda _text: None})
    backend.connect_signals({"on_optimize": lambda: True})
    backend.connect_signals({"on_apply": lambda: True})

    assert optimize_btn.sensitive is False
    assert apply_btn.sensitive is False

    entry.set_text("/tmp/phase5-input.jpg")
    entry.emit("changed", entry)

    assert save_btn.sensitive is True
    assert optimize_btn.sensitive is True
    assert apply_btn.sensitive is False

    optimize_btn.click()

    assert apply_btn.sensitive is True
    assert error.text == "Error: none"

    apply_btn.click()

    assert status.text == "Status: wallpaper applied"
    assert error.text == "Error: none"


def test_phase5_mainwindow_blueprint_smoke_matches_visual_checklist_scope():
    win = MainWindow()
    bp = win.get_layout_blueprint()

    assert bp["layout_version"] == "phase6-layout-redefinition"
    assert [name for name, _ in bp["sections"]] == [
        "title_menu_flow",
        "compose_input",
        "main_margins",
        "action_cluster",
        "slideshow_tab",
        "status_footer",
    ]
    assert bp["primary_action_flow"] == (
        "save_as",
        "optimize",
        "apply",
    )
    assert bp["subtitle"] == "Compose -> Optimize -> Apply"

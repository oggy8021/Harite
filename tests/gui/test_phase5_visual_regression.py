from __future__ import annotations

from harite.gui.adapters.gtk_backend import GtkRuntimeSignalBackend
from harite.gui.views.main_window import MainWindow

from test_gtk_runtime_backend import _FakeGtk


def test_phase5_visual_tokens_snapshot_is_stable():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    snapshot = {
        "main_section": backend.get_object("lblMainSection").text,
        "optimize_section": backend.get_object("lblOptimizeSection").text,
        "apply_section": backend.get_object("lblApplySection").text,
        "apply_mode": backend.get_object("lblApplyMode").text,
        "flow": backend.get_object("lblFlowLegend").text,
        "save": backend.get_object("btnSave").label,
        "optimize": backend.get_object("btnOptimize").label,
        "apply": backend.get_object("btnSetWall").label,
        "prefs": backend.get_object("btnSetting").label,
        "about": backend.get_object("btnAbout").label,
        "help": backend.get_object("btnHelp").label,
        "open_l": backend.get_object("btnGetImgL").label,
        "open_r": backend.get_object("btnGetImgR").label,
    }

    assert snapshot == {
        "main_section": "Main",
        "optimize_section": "Optimize",
        "apply_section": "Apply",
        "apply_mode": "Default: normal apply",
        "flow": "Compose -> Optimize -> Apply",
        "save": "Save As",
        "optimize": "Optimize",
        "apply": "Apply",
        "prefs": "Prefs",
        "about": "About",
        "help": "Help",
        "open_l": "Open-L",
        "open_r": "Open-R",
    }


def test_phase5_runtime_smoke_optimize_then_apply_updates_visual_states():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    entry = backend.get_object("entPathL")
    save_btn = backend.get_object("btnSave")
    optimize_btn = backend.get_object("btnOptimize")
    apply_btn = backend.get_object("btnSetWall")
    optimize_result = backend.get_object("lblOptimizeResult")
    apply_target = backend.get_object("lblApplyTarget")
    status = backend.get_object("lblStatus")

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
    assert optimize_result.text == "Optimize result: success"
    assert apply_target.text == "Apply target: ready"

    apply_btn.click()

    assert status.text == "Apply: ok"
    assert apply_target.text == "Apply target: last applied"


def test_phase5_mainwindow_blueprint_smoke_matches_visual_checklist_scope():
    win = MainWindow()
    bp = win.get_layout_blueprint()

    assert bp["layout_version"] == "phase6-layout-redefinition"
    assert [name for name, _ in bp["sections"]] == [
        "title_menu_flow",
        "compose_input",
        "action_cluster",
        "watch_tab",
        "status_footer",
    ]
    assert bp["primary_action_flow"] == (
        "save_as",
        "optimize",
        "apply",
    )
    assert bp["subtitle"] == "Compose -> Optimize -> Apply"

"""Shared fixtures for GUI tests.

Provides a module-scoped QApplication fixture for Qt backend tests.
The fixture is skipped automatically when PyQt6.QtWidgets is not available.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolate_gui_test_runtime(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Keep GUI unit tests independent of host display count and settings file.

    Pre-P-03 tests assume two displays; CI runners often report ``len==1``.
    P-03 single-display tests live in ``test_p03_*.py`` and patch detection themselves.

    Redirect the default settings path to a non-existent file so a developer's
    ``harite-settings.json`` does not leak margins, slideshow paths, etc.
    Tests that exercise startup settings load override ``resolve_default_settings_path``.
    """
    module_name = Path(str(request.node.fspath)).name
    if not module_name.startswith("test_p03_"):
        monkeypatch.setattr(
            "harite.gui.views.main_window.dual_display_detected",
            lambda: True,
        )

    missing_settings = tmp_path / "harite-settings-missing.json"
    monkeypatch.setattr(
        "harite.gui.views.main_window.resolve_default_settings_path",
        lambda: missing_settings,
    )


@pytest.fixture(scope="session")
def qapp():
    """Session-scoped QApplication for Qt backend tests.

    Skipped automatically when PyQt6.QtWidgets is not importable (e.g. in
    environments without PyQt6 installed).
    """
    pytest.importorskip("PyQt6.QtWidgets")

    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv)
    yield app

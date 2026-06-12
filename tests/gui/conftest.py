"""Shared fixtures for GUI tests.

Provides a module-scoped QApplication fixture for Qt backend tests.
The fixture is skipped automatically when PyQt6.QtWidgets is not available.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

import pytest

from harite.workspace import Display

DETECT_DISPLAYS_PATCH_TARGETS = (
    "harite.workspace.detect_displays",
    "harite.display_context.detect_displays",
    "harite.slideshow_optimize.detect_displays",
    "harite.apply_surface.detect_displays",
)


def _default_stub_displays() -> list[Display]:
    return [
        Display(name="stub-L", width=1920, height=1080, x_offset=0, y_offset=0),
        Display(name="stub-R", width=1920, height=1080, x_offset=1920, y_offset=0),
    ]


def patch_detect_displays(
    monkeypatch: pytest.MonkeyPatch,
    provider: Callable[[], Sequence[Display]],
) -> None:
    """Patch every module-level ``detect_displays`` import used by optimize paths."""
    for target in DETECT_DISPLAYS_PATCH_TARGETS:
        monkeypatch.setattr(target, provider)


@pytest.fixture(autouse=True)
def isolate_gui_test_runtime(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Keep GUI unit tests independent of host display count and settings file.

    MAT-21b resolves optimize canvas from ``detect_displays()``; Linux CI often
    reports zero displays. Stub two displays for all GUI tests except ``test_p03_*``,
    which exercise single-display UX and patch detection themselves.

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
        patch_detect_displays(monkeypatch, _default_stub_displays)

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

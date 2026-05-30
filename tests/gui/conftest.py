"""Shared fixtures for GUI tests.

Provides a module-scoped QApplication fixture for Qt backend tests.
The fixture is skipped automatically when PyQt6.QtWidgets is not available.
"""

from __future__ import annotations

import pytest


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

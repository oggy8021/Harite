"""Standalone GUI app entrypoint (skeleton)."""

from __future__ import annotations

from .views.main_window import MainWindow


def run() -> None:
    """Run standalone GUI skeleton.

    For now this is a placeholder entrypoint to keep CI green while
    GUI framework integration is being prepared.
    """
    window = MainWindow()
    window.show()


if __name__ == "__main__":
    run()

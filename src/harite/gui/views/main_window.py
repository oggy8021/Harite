"""GUI view placeholder.

This file intentionally avoids hard dependency on GTK/PyGObject so the core
package remains importable in environments without GUI libraries.
"""

from __future__ import annotations


class MainWindow:
    """Framework-neutral placeholder for the first standalone GUI window."""

    def __init__(self) -> None:
        self.title = "Harite GUI (MVP)"

    def show(self) -> None:
        print(self.title)
        print("GUI skeleton is ready. Next step: bind real GTK widgets.")

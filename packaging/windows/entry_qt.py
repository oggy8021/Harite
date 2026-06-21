"""PyInstaller entrypoint for the Harite Qt GUI (windowed)."""

from harite.gui.app_qt import main

if __name__ == "__main__":
    raise SystemExit(main())

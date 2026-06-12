# Harite

Harite — wallpaper optimization tool (v2.0.0)

## Overview

Harite generates, arranges, and applies wallpapers in multi-display environments. It supports per-display placement, margins, slideshow rotation, and wallpaper apply plugins.

- **CLI:** `harite optimize` / `apply` / `slideshow`
- **GUI:** Qt 6 (`harite-qt` / `harite-gui` — same entry point)

## Installation

### Python package (Linux / development)

```bash
pip install harite-2.0.0-py3-none-any.whl   # or: pip install -e ".[gui-qt]"
```

For the GUI on Linux, see [requirements-linux-qt.txt](requirements-linux-qt.txt) (distro `python3-pyqt6`, etc.).

### Windows (binary zip)

Extract the onedir folders from the GitHub Release attachment to any location. **There is no installer.**

| Folder | EXE | Role |
| --- | --- | --- |
| `harite/` | `harite.exe` | CLI |
| `harite-qt/` | `harite-qt.exe` | GUI |

See [packaging/windows/README.md](packaging/windows/README.md) for build details.

#### Start menu and shortcuts

**Nothing is added automatically.** The PyInstaller onedir zip is folder-only extraction. Harite does not register Start menu entries or create desktop shortcuts on Windows (`install-desktop-entry` is **Linux/XDG only**).

To launch the GUI from the Start menu, do it manually:

- Pin `harite-qt.exe` to Start, or
- Create a shortcut (`.lnk`) to `harite-qt.exe` and place it on Start menu / Desktop.

#### CLI and PATH (optional)

To run `harite` from any directory without a full path, add the extracted `harite` folder to your **user `Path` environment variable**. This is optional.

```powershell
# Example after adding C:\Apps\harite to Path:
C:\Apps\harite\harite.exe optimize --help
```

You normally do not need `harite-qt` on `Path` (launch the GUI EXE directly).

## CLI examples (v2)

Workspace geometry is detected automatically. Use `--canvas-scale` only to shrink the saved JPEG (placement always uses full geometry).

```bash
harite optimize --input left.jpg,right.jpg \
  --margins 10,10,5,5 --output ./out
```

Two inputs imply dual layout (detection failure is an error). To reduce file size:

```bash
harite optimize --input left.jpg,right.jpg --canvas-scale 50 -o ./out
```

Apply plugin and mode are set via settings JSON (`-c`). v1 flags `--resolution`, `--two-screen`, and `--plugin` are **removed in v2**.

See `harite optimize --help` and [CHANGELOG.md](CHANGELOG.md).

## GUI startup

```bash
harite-qt
# or
harite-gui
```

v2 GUI is **Qt 6 only**. GTK / `python3-gi` are not required.

On Linux/XFCE, for an application-menu launcher:

```bash
harite install-desktop-entry
```

(Writes `~/.local/share/applications/*.desktop`. Not available on Windows.)

## Dependencies

Harite is a Python package (or a self-contained binary on Windows). Wallpaper apply and display detection may use external tools.

- **Common (Python distribution):**
  - Python 3.12+ (`pyproject.toml`)
  - `typer`, `Pillow` (bundled via wheel / editable install)

- **GUI (Qt):**
  - `PyQt6` or distro `python3-pyqt6` ([requirements-linux-qt.txt](requirements-linux-qt.txt))

- **On XFCE:**
  - `xrandr` — display information
  - `xfconf-query` — wallpaper settings (xfce plugin)

## Distribution

- Linux: `harite-<version>-py3-none-any.whl` / `.tar.gz` ([docs/release-delivery.md](docs/release-delivery.md))
- Windows: onedir zip (CLI + GUI)
- PyPI publish for v2.0.0 is TBD

## License

Harite is distributed under the MIT License. Artifacts include [LICENSE](LICENSE).

Lucide SVG icons bundled with the GUI have separate upstream notices. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

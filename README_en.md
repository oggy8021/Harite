# Harite

Harite - wallpaper optimization tool.

## Overview

Harite is a tool for generating, arranging, and applying wallpapers in multi-display environments. It can build wallpapers from one or more input images and supports per-display placement, margins, fixed positioning, and single-display use.

## CLI examples

Basic usage:

```bash
harite optimize --input left.jpg,right.jpg --resolution 3840x1080 \
 --two-screen --l-display 1920x1080 --r-display 1920x1080 \
 --margins 10,10,5,5 --fixed --output ./out
```

See `harite optimize --help` for detailed options.

## GUI startup

```bash
harite-gui
```

## Dependencies

Harite itself is a Python package, but wallpaper setting and display detection on XFCE may use external tools.

- Required:
  - Python 3.12+ (specified in `pyproject.toml`)
  - Python packages: `typer`, `Pillow` (installed via `pip install -e .`)

- On XFCE:
  - `xrandr` - may be used to read display information.
  - `xfconf-query` - may be used to apply wallpaper settings.

On XFCE, assume these two tools are available.

## License

Harite itself is distributed under the MIT License. Distributed artifacts include [LICENSE](LICENSE).

For the Lucide SVG icons bundled with the GUI, upstream notices are kept separately. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for details.

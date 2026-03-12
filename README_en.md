# Harite

Harite: wallpaper optimizer refactor and modernization.

## CLI examples

Basic mosaic:

```bash
harite optimize --input ./imgs --resolution 3840x2160 --output ./out --quality 90
```

Two-screen (left/right) composition:

```bash
harite optimize --input left.jpg,right.jpg --resolution 3840x1080 \
	--two-screen --l-display 1920x1080 --r-display 1920x1080 \
	--margins 10,10,5,5 --fixed --output ./out
```

Save JSON metadata:

```bash
harite optimize --input ./imgs --resolution 1920x1080 --output ./out --format json
```

Use `harite optimize --help` to see all available options.

Note on `apply --do-it` safety
--------------------------------

The CLI `apply` command defaults to a dry-run: it will simulate applying a wallpaper
without changing system settings. To actually change the system wallpaper, pass
`--do-it`. This is a privileged and platform-specific operation; before using
`--do-it` on a target machine:

- Verify the plugin you select (default `windows`, or `macos`/`linux`) is appropriate
    for that system.
- On Linux/XFCE, `xfconf-query` and the desktop property names vary by distro and
    user configuration. Use `xfconf-query -c xfce4-desktop -l` to inspect which
    properties control the background on that machine.
- Run `apply` once without `--do-it` to confirm the dry-run output.
- Use `--do-it` only when you accept the change to the system wallpaper.

Example:

```bash
# dry-run
harite apply --plugin linux --file out/wallpaper.jpg

# actually set wallpaper (if you are sure)
harite apply --plugin linux --file out/wallpaper.jpg --do-it
```

Dependencies
--------

This project runs on Python but the platform-specific "set wallpaper" features
depend on external system commands.

- **Required (runtime)**:
  - Python 3.12+ (see `pyproject.toml`)
  - Python packages: `typer`, `Pillow` (install via `pip install -e .`)

- **Optional (external tools used by plugins / detection)**:
  - `xrandr` — recommended on Linux to query display information (common on XFCE and other DEs).
  - `xfconf-query` — used on XFCE to set wallpaper properties (`xfce4-desktop` channel).
  - `gsettings` — used on GNOME-based environments to set wallpaper (org.gnome.desktop.background).
  - `feh` — lightweight image viewer used as an alternative wallpaper setter.

These tools are not strictly required, but Linux `linux` plugin may call them when available. Install them on the target machine if needed. On Debian/Ubuntu you can:

```bash
sudo apt update
sudo apt install x11-xserver-utils xfce4-tools feh gsettings-desktop-schemas
```

On Fedora:

```bash
sudo dnf install xorg-x11-server-utils xfce4-settings feh dconf
```

macOS includes `osascript` by default; Windows uses Win32 APIs so no external tools are necessary.

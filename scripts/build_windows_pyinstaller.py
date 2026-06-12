"""Build Windows onedir distributions for harite (CLI) and harite-qt (GUI).

Prerequisites (dev environment):
  pip install -e ".[gui-qt]"
  pip install pyinstaller

Usage:
  python scripts/build_windows_pyinstaller.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGING = ROOT / "packaging" / "windows"
DIST_ROOT = ROOT / "dist" / "windows"
BUILD_ROOT = ROOT / "build" / "pyinstaller"
ICON_SCRIPT = ROOT / "scripts" / "build_windows_icon.py"
ICON_PATH = PACKAGING / "harite_app.ico"


def _run(cmd: list[str], *, cwd: Path = ROOT) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def _harite_package_datas() -> list[tuple[str, str]]:
    import harite

    resources = Path(harite.__file__).resolve().parent / "gui" / "resources"
    return [(str(resources), "harite/gui/resources")]


def _common_pyinstaller_args(name: str, entry: Path, *, console: bool) -> list[str]:
    datas = _harite_package_datas()
    args = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        f"--name={name}",
        f"--distpath={DIST_ROOT}",
        f"--workpath={BUILD_ROOT / name}",
        f"--specpath={PACKAGING}",
        "--hidden-import=harite",
        "--hidden-import=harite.cli",
        "--hidden-import=harite.core",
        "--hidden-import=harite.plugins",
        "--hidden-import=harite.gui.app_qt",
        "--collect-submodules=harite",
        "--copy-metadata=harite",
        "--copy-metadata=typer",
        "--copy-metadata=click",
    ]
    if ICON_PATH.is_file():
        args.append(f"--icon={ICON_PATH}")
    if not console:
        args.append("--noconsole")
        args.append("--windowed")
    for src, dest in datas:
        args.append(f"--add-data={src}{os.pathsep}{dest}")
    args.append(str(entry))
    return args


def ensure_icon() -> None:
    if ICON_PATH.is_file():
        return
    _run([sys.executable, str(ICON_SCRIPT)])


def build() -> None:
    try:
        import PyInstaller  # noqa: F401
    except ImportError as exc:
        raise SystemExit(
            "PyInstaller is required. Install with: pip install pyinstaller"
        ) from exc

    ensure_icon()

    if DIST_ROOT.exists():
        shutil.rmtree(DIST_ROOT)
    BUILD_ROOT.mkdir(parents=True, exist_ok=True)

    _run(_common_pyinstaller_args("harite", PACKAGING / "entry_cli.py", console=True))
    _run(_common_pyinstaller_args("harite-qt", PACKAGING / "entry_qt.py", console=False))

    print()
    print("Build complete:")
    print(f"  CLI: {DIST_ROOT / 'harite' / 'harite.exe'}")
    print(f"  GUI: {DIST_ROOT / 'harite-qt' / 'harite-qt.exe'}")
    print()
    print("Zip each folder for GitHub Release attachment, e.g.:")
    print(f"  dist/windows/harite/  -> harite-2.0.0-windows-cli.zip")
    print(f"  dist/windows/harite-qt/ -> harite-2.0.0-windows-gui.zip")


def main() -> None:
    if sys.platform != "win32":
        print(
            "Warning: this script targets Windows (win32). "
            "PyInstaller cross-build is not supported; run on Windows.",
            file=sys.stderr,
        )
    build()


if __name__ == "__main__":
    main()

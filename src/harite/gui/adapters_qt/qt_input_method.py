"""Qt input-method helpers for Linux desktop IME (fcitx / ibus)."""

from __future__ import annotations

import importlib.util
import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_FCITX_QT_IM_MODULE = "fcitx"
_IBUS_QT_IM_MODULE = "ibus"

_FCITX_PLUGIN_NAMES = (
    "libfcitx5platforminputcontextplugin.so",
    "libfcitxplatforminputcontextplugin-qt6.so",
)

_SYSTEM_PLUGIN_DIRS = (
    Path("/usr/lib/qt6/plugins/platforminputcontexts"),
    Path("/usr/lib/x86_64-linux-gnu/qt6/plugins/platforminputcontexts"),
    Path("/usr/lib/aarch64-linux-gnu/qt6/plugins/platforminputcontexts"),
    Path("/usr/lib64/qt6/plugins/platforminputcontexts"),
    Path("/usr/lib/qt/plugins/platforminputcontexts"),
    Path("/usr/lib/x86_64-linux-gnu/qt/plugins/platforminputcontexts"),
)

_SYSTEM_LIB_SEARCH_ROOTS = (
    Path("/usr/lib"),
    Path("/usr/lib64"),
)

_FCITX_QT_PACKAGE_HINT = (
    "Install the fcitx Qt6 IM frontend (Debian/Ubuntu/Mint: fcitx5-frontend-qt6; "
    "libfcitx5-qt6-1 is only the shared library and libfcitx5-qt-data has no .so). "
    "A Qt5-only plugin under .../qt5/plugins/... cannot be used with pip PyQt6."
)

_FCITX_PIP_PYQT6_HINT = (
    "pip PyQt6 bundles its own Qt6 and cannot load the distro fcitx plugin "
    "(QT_DEBUG_PLUGINS shows Qt_6_PRIVATE_API undefined symbol). "
    "Use distro PyQt6 instead (Debian/Ubuntu/Mint: sudo apt install python3-pyqt6, "
    "then recreate the venv with --system-site-packages). "
    "Quick probe: QT_IM_MODULE=ibus harite-qt when fcitx ibus frontend is available."
)

_FCITX_ABI_MISMATCH_HINT = _FCITX_PIP_PYQT6_HINT

_SYSTEM_QT6_LIBRARY_DIRS = (
    Path("/usr/lib/x86_64-linux-gnu"),
    Path("/usr/lib/aarch64-linux-gnu"),
    Path("/usr/lib64"),
    Path("/usr/lib"),
)


def _is_qt6_plugin_path(path: Path) -> bool:
    normalized = path.as_posix()
    if "/qt5/" in normalized:
        return False
    return "/qt6/" in normalized


def discover_system_fcitx_qt5_plugins() -> list[Path]:
    """Find fcitx Qt5 IM plugins (not usable with PyQt6; diagnostic only)."""
    found: list[Path] = []
    for root in _SYSTEM_LIB_SEARCH_ROOTS:
        if not root.is_dir():
            continue
        for plugin_name in ("libfcitxplatforminputcontextplugin.so", "libfcitx5platforminputcontextplugin.so"):
            for source in root.glob(f"**/qt5/**/{plugin_name}"):
                if source.is_file():
                    found.append(source)
    return sorted(found, key=lambda path: str(path))


def _normalize_gtk_im_module(value: str) -> str | None:
    module = value.strip().lower()
    if module in {"fcitx", "fcitx5"}:
        return _FCITX_QT_IM_MODULE
    if module == "ibus":
        return _IBUS_QT_IM_MODULE
    return None


def _im_module_from_xmodifiers(value: str) -> str | None:
    lowered = value.strip().lower()
    if "@im=fcitx" in lowered or "@im=fcitx5" in lowered:
        return _FCITX_QT_IM_MODULE
    if "@im=ibus" in lowered:
        return _IBUS_QT_IM_MODULE
    return None


def resolve_qt_im_module(
    *,
    qt_im_module: str | None = None,
    gtk_im_module: str | None = None,
    xmodifiers: str | None = None,
) -> str | None:
    """Infer ``QT_IM_MODULE`` from the active desktop IME environment."""
    if qt_im_module and qt_im_module.strip():
        return qt_im_module.strip()

    if gtk_im_module:
        resolved = _normalize_gtk_im_module(gtk_im_module)
        if resolved is not None:
            return resolved

    if xmodifiers:
        resolved = _im_module_from_xmodifiers(xmodifiers)
        if resolved is not None:
            return resolved

    return None


def _resolve_pyqt6_package_root() -> Path | None:
    spec = importlib.util.find_spec("PyQt6")
    if spec is None or not spec.origin:
        return None
    return Path(spec.origin).resolve().parent


def pyqt6_install_is_pip_venv() -> bool:
    root = _resolve_pyqt6_package_root()
    if root is None:
        return False
    return "/site-packages/" in root.as_posix()


def pip_pyqt6_fcitx_plugin_incompatible() -> bool:
    if not sys.platform.startswith("linux"):
        return False
    if not pyqt6_install_is_pip_venv():
        return False
    return bool(discover_system_fcitx_qt_plugins())


def _pyqt6_platform_input_context_dir_from_root() -> Path | None:
    root = _resolve_pyqt6_package_root()
    if root is None:
        return None
    plugins_dir = root / "Qt6" / "plugins" / "platforminputcontexts"
    return plugins_dir if plugins_dir.is_dir() else None


def remove_incompatible_fcitx_plugin_symlink() -> bool:
    """Drop a distro fcitx symlink from pip PyQt6; it cannot load (PRIVATE_API)."""
    if not pip_pyqt6_fcitx_plugin_incompatible():
        return False

    plugins_dir = _pyqt6_platform_input_context_dir_from_root()
    if plugins_dir is None:
        return False

    removed = False
    for name in _FCITX_PLUGIN_NAMES:
        destination = plugins_dir / name
        if not destination.is_symlink():
            continue
        try:
            if destination.resolve().as_posix().startswith("/usr/"):
                destination.unlink()
                removed = True
                logger.info(
                    "Removed incompatible distro fcitx symlink from pip PyQt6: %s",
                    destination,
                )
        except OSError:
            continue
    return removed


def warn_pip_pyqt6_fcitx_incompatible() -> None:
    if pip_pyqt6_fcitx_plugin_incompatible():
        logger.warning("Qt IM: %s", _FCITX_PIP_PYQT6_HINT)


def pyqt6_qt_library_dir() -> Path | None:
    root = _resolve_pyqt6_package_root()
    if root is None:
        return None
    lib_dir = root / "Qt6" / "lib"
    return lib_dir if lib_dir.is_dir() else None


def system_qt6_library_dirs() -> list[Path]:
    return [path for path in _SYSTEM_QT6_LIBRARY_DIRS if path.is_dir()]


def _prepend_ld_library_path(paths: list[Path]) -> None:
    entries = [str(path) for path in paths if path.is_dir()]
    if not entries:
        return
    prefix = ":".join(entries)
    current = os.environ.get("LD_LIBRARY_PATH", "")
    if current.startswith(prefix):
        return
    os.environ["LD_LIBRARY_PATH"] = f"{prefix}:{current}" if current else prefix


def _fcitx_plugin_uses_system_origin(target_dir: Path) -> bool:
    for name in _FCITX_PLUGIN_NAMES:
        destination = target_dir / name
        if not destination.exists():
            continue
        try:
            resolved = destination.resolve()
        except OSError:
            continue
        if resolved.as_posix().startswith("/usr/"):
            return True
    return False


def _linux_fcitx_system_libs_enabled() -> bool:
    raw = os.environ.get("HARITE_QT_FCITX_SYSTEM_LIBS", "1").strip().lower()
    return raw not in {"0", "false", "no", "off"}


def _fcitx_loader_paths() -> list[Path]:
    paths: list[Path] = []
    pyqt_lib = pyqt6_qt_library_dir()
    if pyqt_lib is not None:
        paths.append(pyqt_lib)
    paths.extend(system_qt6_library_dirs())
    return paths


def configure_linux_fcitx_dynamic_loader() -> bool:
    """Prepend loader paths before PyQt6 import when a distro fcitx plugin exists."""
    if not sys.platform.startswith("linux") or not _linux_fcitx_system_libs_enabled():
        return False
    if not discover_system_fcitx_qt_plugins() and not _fcitx_plugin_already_linked():
        return False

    _prepend_ld_library_path(_fcitx_loader_paths())
    logger.info(
        "Qt IM: prepended LD_LIBRARY_PATH for distro fcitx plugin compatibility"
    )
    return True


def _fcitx_plugin_already_linked() -> bool:
    root = _resolve_pyqt6_package_root()
    if root is None:
        return False
    plugins_dir = root / "Qt6" / "plugins" / "platforminputcontexts"
    if not plugins_dir.is_dir():
        return False
    return _fcitx_plugin_uses_system_origin(plugins_dir)


def _should_log_qt_im_diagnostics() -> bool:
    raw = os.environ.get("HARITE_QT_IM_DIAG", "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def log_qt_input_method_diagnostics(qapp: Any) -> None:
    """Log Qt IM runtime details for Linux fcitx troubleshooting."""
    if not sys.platform.startswith("linux"):
        return

    report = audit_qt_fcitx_input_method()
    try:
        from PyQt6.QtCore import QLibraryInfo
        from PyQt6.QtGui import QGuiApplication

        report["qt_runtime_version"] = QLibraryInfo.version().toString()
        report["qt_plugin_path"] = QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)
        input_method = QGuiApplication.inputMethod()
        report["input_method_available"] = input_method is not None
        if input_method is not None:
            report["input_method_locale"] = input_method.locale().name()
    except Exception as exc:  # pragma: no cover - diagnostic only
        report["runtime_probe_error"] = str(exc)

    if report.get("pip_pyqt6_fcitx_incompatible"):
        report["pip_pyqt6_hint"] = _FCITX_PIP_PYQT6_HINT

    if _should_log_qt_im_diagnostics():
        logger.info("Qt IM diagnostics: %s", report)
    elif report.get("fcitx_plugins_present") or report.get("pip_pyqt6_fcitx_incompatible"):
        logger.debug("Qt IM diagnostics: %s", report)


def prepare_qt_input_method_env() -> str | None:
    """Apply best-effort Qt IM env vars before ``QApplication`` construction."""
    if not sys.platform.startswith("linux"):
        return os.environ.get("QT_IM_MODULE")

    resolved = resolve_qt_im_module(
        qt_im_module=os.environ.get("QT_IM_MODULE"),
        gtk_im_module=os.environ.get("GTK_IM_MODULE"),
        xmodifiers=os.environ.get("XMODIFIERS"),
    )
    if resolved and not os.environ.get("QT_IM_MODULE"):
        os.environ["QT_IM_MODULE"] = resolved

    if os.environ.get("QT_IM_MODULE", "").strip().lower() in {_FCITX_QT_IM_MODULE, "fcitx5"}:
        remove_incompatible_fcitx_plugin_symlink()
        if pip_pyqt6_fcitx_plugin_incompatible():
            warn_pip_pyqt6_fcitx_incompatible()
        else:
            configure_linux_fcitx_dynamic_loader()
            linked = link_system_fcitx_qt_plugin_if_missing()
            if linked is None and not fcitx_input_context_plugin_names():
                candidates = discover_system_fcitx_qt_plugins()
                qt5_only = discover_system_fcitx_qt5_plugins()
                logger.warning(
                    "Qt IM: QT_IM_MODULE=fcitx but no fcitx platforminputcontext plugin in PyQt6. "
                    "GTK/Firefox may work while Qt widgets do not. "
                    "%s Qt6 candidates: %s; Qt5-only (ignored): %s",
                    _FCITX_QT_PACKAGE_HINT,
                    [str(path) for path in candidates] or "none",
                    [str(path) for path in qt5_only] or "none",
                )

    return os.environ.get("QT_IM_MODULE")


def pyqt6_platform_input_context_dir() -> Path | None:
    try:
        import PyQt6
    except ImportError:
        return None

    plugins_dir = Path(PyQt6.__file__).resolve().parent / "Qt6" / "plugins" / "platforminputcontexts"
    if plugins_dir.is_dir():
        return plugins_dir
    return None


def fcitx_input_context_plugin_names(target_dir: Path | None = None) -> list[str]:
    """Return fcitx-related plugin filenames present under PyQt6 IM plugins."""
    plugins_dir = target_dir or pyqt6_platform_input_context_dir()
    if plugins_dir is None:
        return []
    return sorted(
        path.name
        for path in plugins_dir.iterdir()
        if path.is_file() and "fcitx" in path.name.lower()
    )


def discover_system_fcitx_qt_plugins() -> list[Path]:
    """Find fcitx Qt6 IM plugin files under common system library trees."""
    found: list[Path] = []
    seen: set[Path] = set()
    for plugin_dir in _SYSTEM_PLUGIN_DIRS:
        if not plugin_dir.is_dir() or not _is_qt6_plugin_path(plugin_dir):
            continue
        for path in plugin_dir.iterdir():
            if not path.is_file() or "fcitx" not in path.name.lower():
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            found.append(path)
    for root in _SYSTEM_LIB_SEARCH_ROOTS:
        if not root.is_dir():
            continue
        for plugin_name in _FCITX_PLUGIN_NAMES:
            for source in root.glob(f"**/{plugin_name}"):
                if not source.is_file() or not _is_qt6_plugin_path(source):
                    continue
                resolved = source.resolve()
                if resolved in seen:
                    continue
                seen.add(resolved)
                found.append(source)
    return sorted(found, key=lambda path: str(path))


def audit_qt_fcitx_input_method() -> dict[str, object]:
    """Summarize Qt IM plugin availability for Linux troubleshooting."""
    target_dir = pyqt6_platform_input_context_dir()
    system_candidates = discover_system_fcitx_qt_plugins()
    incompatible = pip_pyqt6_fcitx_plugin_incompatible()
    return {
        "qt_im_module": os.environ.get("QT_IM_MODULE"),
        "gtk_im_module": os.environ.get("GTK_IM_MODULE"),
        "xmodifiers": os.environ.get("XMODIFIERS"),
        "pyqt_install": "pip-venv" if pyqt6_install_is_pip_venv() else "system",
        "pyqt_plugins_dir": str(target_dir) if target_dir is not None else None,
        "fcitx_plugins_present": fcitx_input_context_plugin_names(target_dir),
        "system_fcitx_qt6_plugin_candidates": [str(path) for path in system_candidates],
        "system_fcitx_qt5_plugins_ignored": [str(path) for path in discover_system_fcitx_qt5_plugins()],
        "pip_pyqt6_fcitx_incompatible": incompatible,
        "ld_library_path": os.environ.get("LD_LIBRARY_PATH"),
        "package_hint": _FCITX_QT_PACKAGE_HINT,
        "pip_pyqt6_hint": _FCITX_PIP_PYQT6_HINT if incompatible else None,
    }


def link_system_fcitx_qt_plugin_if_missing() -> Path | None:
    """Symlink a system fcitx Qt plugin into distro PyQt6 when it lacks one."""
    if pip_pyqt6_fcitx_plugin_incompatible():
        return None

    target_dir = pyqt6_platform_input_context_dir()
    if target_dir is None:
        return None

    if any((target_dir / name).exists() for name in _FCITX_PLUGIN_NAMES):
        return None

    for source in discover_system_fcitx_qt_plugins():
        destination = target_dir / source.name
        try:
            if destination.exists() or destination.is_symlink():
                return destination
            destination.symlink_to(source)
            logger.info("Linked fcitx Qt IM plugin: %s -> %s", destination, source)
            return destination
        except OSError as exc:
            logger.debug("Could not link fcitx Qt IM plugin %s: %s", destination, exc)
    return None


def configure_text_input_widget(widget: Any) -> None:
    """Ensure a text widget accepts desktop IME input."""
    try:
        from PyQt6.QtCore import Qt
    except ImportError:
        return

    if hasattr(widget, "setFocusPolicy"):
        widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    if hasattr(widget, "setAttribute"):
        widget.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
    if hasattr(widget, "setInputMethodHints"):
        widget.setInputMethodHints(Qt.InputMethodHint.ImhNone)

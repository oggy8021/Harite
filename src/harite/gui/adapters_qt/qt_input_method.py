"""Qt input-method helpers for Linux desktop IME (fcitx / ibus)."""

from __future__ import annotations

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
    "A Qt5-only plugin under .../qt5/plugins/... cannot be used with pip PyQt6. "
    "Then restart harite-qt so Harite can symlink the Qt6 plugin into the venv PyQt6."
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
        linked = link_system_fcitx_qt_plugin_if_missing()
        if linked is None and not fcitx_input_context_plugin_names():
            candidates = discover_system_fcitx_qt_plugins()
            qt5_only = discover_system_fcitx_qt5_plugins()
            logger.warning(
                "Qt IM: QT_IM_MODULE=fcitx but no fcitx platforminputcontext plugin in PyQt6 "
                "(typical pip wheel gap). GTK/Firefox may work while Qt widgets do not. "
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
    linked = link_system_fcitx_qt_plugin_if_missing() if target_dir is not None else None
    return {
        "qt_im_module": os.environ.get("QT_IM_MODULE"),
        "gtk_im_module": os.environ.get("GTK_IM_MODULE"),
        "xmodifiers": os.environ.get("XMODIFIERS"),
        "pyqt_plugins_dir": str(target_dir) if target_dir is not None else None,
        "fcitx_plugins_before_link": fcitx_input_context_plugin_names(target_dir),
        "system_fcitx_qt6_plugin_candidates": [str(path) for path in system_candidates],
        "system_fcitx_qt5_plugins_ignored": [str(path) for path in discover_system_fcitx_qt5_plugins()],
        "linked_plugin": str(linked) if linked is not None else None,
        "fcitx_plugins_after_link": fcitx_input_context_plugin_names(target_dir),
        "package_hint": _FCITX_QT_PACKAGE_HINT,
    }


def link_system_fcitx_qt_plugin_if_missing() -> Path | None:
    """Symlink a system fcitx Qt plugin into PyQt6 when the pip wheel lacks it."""
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

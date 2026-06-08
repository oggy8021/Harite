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
    Path("/usr/lib/qt/plugins/platforminputcontexts"),
    Path("/usr/lib/x86_64-linux-gnu/qt/plugins/platforminputcontexts"),
)


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
        link_system_fcitx_qt_plugin_if_missing()

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


def link_system_fcitx_qt_plugin_if_missing() -> Path | None:
    """Symlink a system fcitx Qt plugin into PyQt6 when the pip wheel lacks it."""
    target_dir = pyqt6_platform_input_context_dir()
    if target_dir is None:
        return None

    if any((target_dir / name).exists() for name in _FCITX_PLUGIN_NAMES):
        return None

    for plugin_dir in _SYSTEM_PLUGIN_DIRS:
        if not plugin_dir.is_dir():
            continue
        for plugin_name in _FCITX_PLUGIN_NAMES:
            source = plugin_dir / plugin_name
            if not source.is_file():
                continue
            destination = target_dir / plugin_name
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

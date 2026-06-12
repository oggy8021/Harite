"""Normalize embed_info mode strings across CLI, GUI, and settings."""

from __future__ import annotations

EMBED_INFO_NONE = "none"
EMBED_INFO_SETTINGS = "settings"
EMBED_INFO_FREE = "free"
EMBED_INFO_COMBO = "combo"

EMBED_INFO_VALUES: frozenset[str] = frozenset(
    {EMBED_INFO_NONE, EMBED_INFO_SETTINGS, EMBED_INFO_FREE, EMBED_INFO_COMBO}
)

CLI_EMBED_INFO_CHOICES: tuple[str, ...] = (
    EMBED_INFO_SETTINGS,
    EMBED_INFO_FREE,
    EMBED_INFO_COMBO,
)

_LEGACY_ALIASES: dict[str, str] = {"params": EMBED_INFO_SETTINGS}


def normalize_embed_info(value: object | None) -> str:
    """Return a canonical embed_info mode.

    Legacy settings value ``params`` maps to ``settings``. Empty / missing
    values map to ``none``.
    """
    if value is None:
        return EMBED_INFO_NONE
    raw = str(value).strip().lower()
    if not raw:
        return EMBED_INFO_NONE
    raw = _LEGACY_ALIASES.get(raw, raw)
    if raw not in EMBED_INFO_VALUES:
        allowed = ", ".join(sorted(CLI_EMBED_INFO_CHOICES))
        raise ValueError(f"embed_info must be one of: {allowed} (or omit for none)")
    return raw


def embed_info_includes_settings(mode: str) -> bool:
    normalized = normalize_embed_info(mode)
    return normalized in {EMBED_INFO_SETTINGS, EMBED_INFO_COMBO}


def embed_info_includes_free_text(mode: str) -> bool:
    normalized = normalize_embed_info(mode)
    return normalized in {EMBED_INFO_FREE, EMBED_INFO_COMBO}

from __future__ import annotations

from typing import Iterable


DEFAULT_ALIGN = "center"
DEFAULT_VALIGN = "center"


def _normalize_valign(value: str) -> str:
    raw = str(value or "").strip().lower()
    if raw == "middle":
        return "center"
    return raw or DEFAULT_VALIGN


def _normalize_align(value: str) -> str:
    raw = str(value or "").strip().lower()
    return raw or DEFAULT_ALIGN


def _normalize_pair_tokens(values: Iterable[object], *, axis: str) -> tuple[str, str]:
    tokens = [str(value or "").strip() for value in values if str(value or "").strip()]
    if not tokens:
        tokens = [DEFAULT_VALIGN if axis == "valign" else DEFAULT_ALIGN]
    if len(tokens) == 1:
        tokens = [tokens[0], tokens[0]]
    else:
        tokens = [tokens[0], tokens[1]]

    if axis == "valign":
        return (_normalize_valign(tokens[0]), _normalize_valign(tokens[1]))
    return (_normalize_align(tokens[0]), _normalize_align(tokens[1]))


def parse_position_pair(value: object, *, axis: str) -> tuple[str, str]:
    if isinstance(value, (list, tuple)):
        return _normalize_pair_tokens(value, axis=axis)

    raw = str(value or "").strip()
    if not raw:
        return _normalize_pair_tokens((), axis=axis)

    if "," in raw:
        return _normalize_pair_tokens(raw.split(","), axis=axis)

    return _normalize_pair_tokens((raw,), axis=axis)


def format_position_pair(value: object, *, axis: str) -> str:
    left, right = parse_position_pair(value, axis=axis)
    return f"{left},{right}"


def position_value_for_side(value: object, side: str, *, axis: str) -> str:
    left, right = parse_position_pair(value, axis=axis)
    return left if side.upper() == "L" else right


def update_position_pair(value: object, side: str, new_value: str, *, axis: str) -> tuple[str, str]:
    left, right = parse_position_pair(value, axis=axis)
    normalized_side = side.upper()
    if normalized_side == "L":
        left = position_value_for_side((new_value, right), "L", axis=axis)
    elif normalized_side == "R":
        right = position_value_for_side((left, new_value), "R", axis=axis)
    return parse_position_pair((left, right), axis=axis)


def reset_position_pair(value: object, side: str, *, axis: str) -> tuple[str, str]:
    default = DEFAULT_VALIGN if axis == "valign" else DEFAULT_ALIGN
    return update_position_pair(value, side, default, axis=axis)

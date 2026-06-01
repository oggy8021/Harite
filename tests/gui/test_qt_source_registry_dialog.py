"""Tests for qt_source_registry_dialog profile slot sync (C-02)."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PyQt6.QtWidgets")


def test_apply_profile_slot_combos_avoids_stale_sibling_slot(qapp):
    from PyQt6.QtWidgets import QComboBox

    from harite.gui.adapters_qt.qt_source_registry_dialog import apply_profile_slot_combos

    items = [("— empty —", ""), ("Source A", "id-a"), ("Source B", "id-b")]
    slot_l = QComboBox()
    slot_r = QComboBox()
    for label, value in items:
        slot_l.addItem(label, value)
        slot_r.addItem(label, value)
    slot_r.setCurrentIndex(2)

    loading = {"profile_slots_loading": False}
    persisted: list[tuple[object, object]] = []

    def _capture() -> None:
        if loading.get("profile_slots_loading"):
            return
        persisted.append((slot_l.currentData(), slot_r.currentData()))

    slot_l.currentIndexChanged.connect(_capture)
    slot_r.currentIndexChanged.connect(_capture)

    apply_profile_slot_combos(
        slot_l,
        slot_r,
        member_l=None,
        member_r=None,
        items=items,
        loading_state=loading,
    )

    assert slot_l.currentData() in ("", None)
    assert slot_r.currentData() in ("", None)
    assert persisted == []


def test_select_combo_by_data_finds_new_profile(qapp):
    from PyQt6.QtWidgets import QComboBox

    from harite.gui.adapters_qt.qt_source_registry_dialog import _normalize_id, _select_combo_by_data

    combo = QComboBox()
    combo.addItem("First", "profile-1")
    combo.addItem("Second", "profile-2")

    assert _select_combo_by_data(combo, "profile-2") is True
    assert _normalize_id(combo.currentData()) == "profile-2"


def test_profile_slot_persist_does_not_touch_other_profile(qapp, tmp_path: Path):
    """Regression: editing profile 2 must not overwrite profile 1 members."""
    from PyQt6.QtWidgets import QComboBox

    from harite.gui.adapters_qt.qt_source_registry_dialog import (
        _normalize_id,
        _select_combo_by_data,
        apply_profile_slot_combos,
        source_slot_items,
    )
    from harite.sources import add_profile, add_source, empty_catalog, get_profile, save_catalog, update_profile

    left = tmp_path / "left"
    right = tmp_path / "right"
    third = tmp_path / "third"
    left.mkdir()
    right.mkdir()
    third.mkdir()

    catalog = empty_catalog()
    source_a = add_source(catalog, name="A", path=left)
    source_b = add_source(catalog, name="B", path=right)
    source_c = add_source(catalog, name="C", path=third)
    first = add_profile(catalog, name="First", members={"L": source_a.id, "R": None})
    second = add_profile(catalog, name="Second", members={"L": None, "R": None})

    profile_combo = QComboBox()
    slot_l = QComboBox()
    slot_r = QComboBox()
    for entry in (first, second):
        profile_combo.addItem(entry.name, entry.id)

    items = source_slot_items(catalog)
    editor_state = {"profile_slots_loading": False}

    def _on_slot_changed() -> None:
        if editor_state.get("profile_slots_loading"):
            return
        profile_id = _normalize_id(profile_combo.currentData())
        if not profile_id:
            return
        update_profile(
            catalog,
            profile_id,
            members={
                "L": _normalize_id(slot_l.currentData()),
                "R": _normalize_id(slot_r.currentData()),
            },
        )

    slot_l.currentIndexChanged.connect(_on_slot_changed)
    slot_r.currentIndexChanged.connect(_on_slot_changed)

    assert _select_combo_by_data(profile_combo, second.id) is True
    apply_profile_slot_combos(
        slot_l,
        slot_r,
        member_l=None,
        member_r=None,
        items=items,
        loading_state=editor_state,
    )

    for combo, source_id in ((slot_l, source_b.id), (slot_r, source_c.id)):
        for index in range(combo.count()):
            if _normalize_id(combo.itemData(index)) == source_id:
                combo.setCurrentIndex(index)
                break

    first_profile = get_profile(catalog, first.id)
    second_profile = get_profile(catalog, second.id)
    assert first_profile is not None and second_profile is not None
    assert first_profile.members.L == source_a.id
    assert first_profile.members.R is None
    assert second_profile.members.L == source_b.id
    assert second_profile.members.R == source_c.id

    save_catalog(catalog, tmp_path / "harite-sources.json")

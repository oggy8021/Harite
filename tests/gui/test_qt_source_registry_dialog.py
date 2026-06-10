"""Tests for qt_source_registry_dialog profile slot sync (C-02)."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PyQt6.QtWidgets")


def test_sync_manage_dialog_keyword_fields_preserves_entry_text(qapp, tmp_path: Path):
    from PyQt6.QtWidgets import QLineEdit

    from harite.gui.adapters_qt.qt_source_registry_dialog import sync_manage_dialog_keyword_fields
    from harite.sources import empty_catalog, import_preset_source

    cache = tmp_path / "cache"
    catalog = empty_catalog()
    keyword_source = import_preset_source(catalog, "codh-edo-spots-keyword", cache_root=cache)

    codh_entry = QLineEdit("edited-draft")
    ndl_entry = QLineEdit("ndl-draft")
    sync_manage_dialog_keyword_fields(
        codh_entry,
        ndl_entry,
        selected_entry=keyword_source,
    )

    assert codh_entry.text() == "edited-draft"
    assert codh_entry.isEnabled() is True
    assert ndl_entry.text() == "ndl-draft"
    assert ndl_entry.isEnabled() is False


def test_sync_manage_dialog_keyword_fields_enables_ndl_keyword_preset(qapp, tmp_path: Path):
    from PyQt6.QtWidgets import QLineEdit

    from harite.gui.adapters_qt.qt_source_registry_dialog import sync_manage_dialog_keyword_fields
    from harite.sources import empty_catalog, import_preset_source

    cache = tmp_path / "cache"
    catalog = empty_catalog()
    keyword_source = import_preset_source(catalog, "ndl-search-keyword", cache_root=cache)

    codh_entry = QLineEdit("codh-draft")
    ndl_entry = QLineEdit("ペンギン")
    sync_manage_dialog_keyword_fields(
        codh_entry,
        ndl_entry,
        selected_entry=keyword_source,
    )

    assert codh_entry.isEnabled() is False
    assert ndl_entry.text() == "ペンギン"
    assert ndl_entry.isEnabled() is True


def test_sync_manage_dialog_keyword_fields_disables_for_non_keyword_preset(qapp, tmp_path: Path):
    from PyQt6.QtWidgets import QLineEdit

    from harite.gui.adapters_qt.qt_source_registry_dialog import sync_manage_dialog_keyword_fields
    from harite.sources import empty_catalog, import_preset_source

    cache = tmp_path / "cache"
    catalog = empty_catalog()
    random_source = import_preset_source(catalog, "codh-edo-spots-random", cache_root=cache)

    codh_entry = QLineEdit("edited-draft")
    ndl_entry = QLineEdit("ndl-draft")
    sync_manage_dialog_keyword_fields(
        codh_entry,
        ndl_entry,
        selected_entry=random_source,
    )

    assert codh_entry.text() == "edited-draft"
    assert codh_entry.isEnabled() is False
    assert ndl_entry.isEnabled() is False


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


def test_add_profile_uses_slot_values_without_overwriting_first(qapp, tmp_path: Path):
    """Regression: set L/R, type new name, Add profile — first profile unchanged."""
    from PyQt6.QtWidgets import QComboBox

    from harite.gui.adapters_qt.qt_source_registry_dialog import (
        _normalize_id,
        _select_combo_by_data,
        apply_profile_slot_combos,
        read_slot_members,
        source_slot_items,
    )
    from harite.sources import add_profile, add_source, empty_catalog, get_profile, save_catalog

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

    profile_combo = QComboBox()
    slot_l = QComboBox()
    slot_r = QComboBox()
    profile_combo.addItem(first.name, first.id)

    items = source_slot_items(catalog)
    loading = {"profile_slots_loading": False}

    apply_profile_slot_combos(
        slot_l,
        slot_r,
        member_l=first.members.L,
        member_r=first.members.R,
        items=items,
        loading_state=loading,
    )

    for combo, source_id in ((slot_l, source_b.id), (slot_r, source_c.id)):
        for index in range(combo.count()):
            if _normalize_id(combo.itemData(index)) == source_id:
                combo.setCurrentIndex(index)
                break

    second = add_profile(catalog, name="Second", members=read_slot_members(slot_l, slot_r))
    save_catalog(catalog, tmp_path / "harite-sources.json")

    profile_combo.addItem(second.name, second.id)
    assert _select_combo_by_data(profile_combo, second.id) is True

    first_profile = get_profile(catalog, first.id)
    second_profile = get_profile(catalog, second.id)
    assert first_profile is not None and second_profile is not None
    assert first_profile.members.L == source_a.id
    assert first_profile.members.R is None
    assert second_profile.members.L == source_b.id
    assert second_profile.members.R == source_c.id


def test_profile_switch_flushes_previous_members(qapp, tmp_path: Path):
    from PyQt6.QtWidgets import QComboBox

    from harite.gui.adapters_qt.qt_source_registry_dialog import (
        _normalize_id,
        apply_profile_slot_combos,
        read_slot_members,
        source_slot_items,
    )
    from harite.sources import add_profile, add_source, empty_catalog, get_profile, update_profile

    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()

    catalog = empty_catalog()
    source_a = add_source(catalog, name="A", path=left)
    source_b = add_source(catalog, name="B", path=right)
    first = add_profile(catalog, name="First", members={"L": source_a.id, "R": None})
    second = add_profile(catalog, name="Second", members={"L": None, "R": None})

    slot_l = QComboBox()
    slot_r = QComboBox()
    items = source_slot_items(catalog)
    loading = {"profile_slots_loading": False}

    apply_profile_slot_combos(slot_l, slot_r, member_l=source_a.id, member_r=None, items=items, loading_state=loading)
    for index in range(slot_r.count()):
        if _normalize_id(slot_r.itemData(index)) == source_b.id:
            slot_r.setCurrentIndex(index)
            break

    update_profile(catalog, first.id, members=read_slot_members(slot_l, slot_r))

    first_profile = get_profile(catalog, first.id)
    second_profile = get_profile(catalog, second.id)
    assert first_profile is not None and second_profile is not None
    assert first_profile.members.R == source_b.id
    assert second_profile.members.L is None

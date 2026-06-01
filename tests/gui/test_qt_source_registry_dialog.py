"""Tests for qt_source_registry_dialog profile slot sync (C-02)."""

from __future__ import annotations

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

    captured: list[tuple[object, object]] = []

    def _capture() -> None:
        captured.append((slot_l.currentData(), slot_r.currentData()))

    slot_l.currentIndexChanged.connect(_capture)
    slot_r.currentIndexChanged.connect(_capture)

    apply_profile_slot_combos(
        slot_l,
        slot_r,
        member_l=None,
        member_r=None,
        items=items,
    )

    assert slot_l.currentData() == ""
    assert slot_r.currentData() == ""
    for left, right in captured:
        assert (left or "") == ""
        assert (right or "") == ""


def test_add_profile_selects_new_entry_not_first(qapp, tmp_path):
    from harite.gui.adapters_qt.qt_source_registry_dialog import source_slot_items
    from harite.sources import add_profile, add_source, empty_catalog, get_profile, save_catalog

    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    catalog = empty_catalog()
    source_a = add_source(catalog, name="A", path=left)
    source_b = add_source(catalog, name="B", path=right)
    first = add_profile(
        catalog,
        name="First",
        members={"L": source_a.id, "R": None},
    )
    second = add_profile(
        catalog,
        name="Second",
        members={"L": None, "R": source_b.id},
    )
    save_catalog(catalog, tmp_path / "harite-sources.json")

    assert get_profile(catalog, first.id).members.L == source_a.id
    assert get_profile(catalog, second.id).members.R == source_b.id
    assert second.id != first.id
    assert len(source_slot_items(catalog)) == 3

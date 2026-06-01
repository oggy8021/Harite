"""Qt dialog for C-02 source registry management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harite.sources import (
    Catalog,
    add_profile,
    add_source,
    delete_profile,
    delete_source,
    get_profile,
    list_profiles,
    list_sources,
    load_catalog,
    save_catalog,
    update_profile,
)


def source_slot_items(catalog: Catalog) -> list[tuple[str, str]]:
    items = [("— empty —", "")]
    for entry in list_sources(catalog):
        items.append((entry.name, entry.id))
    return items


def fill_source_slot_combo(
    combo: Any,
    selected_id: str | None,
    items: list[tuple[str, str]],
    *,
    block_signals: bool = True,
) -> None:
    if block_signals:
        combo.blockSignals(True)
    combo.clear()
    selected = selected_id or ""
    index_to_select = 0
    for idx, (label, value) in enumerate(items):
        combo.addItem(label, value)
        if value == selected:
            index_to_select = idx
    combo.setCurrentIndex(index_to_select)
    if block_signals:
        combo.blockSignals(False)


def apply_profile_slot_combos(
    slot_l: Any,
    slot_r: Any,
    *,
    member_l: str | None,
    member_r: str | None,
    items: list[tuple[str, str]],
) -> None:
    """Set L/R slot combos without emitting intermediate slot-change signals."""
    slot_l.blockSignals(True)
    slot_r.blockSignals(True)
    try:
        fill_source_slot_combo(slot_l, member_l, items, block_signals=False)
        fill_source_slot_combo(slot_r, member_r, items, block_signals=False)
    finally:
        slot_r.blockSignals(False)
        slot_l.blockSignals(False)


def run_source_registry_dialog(parent: Any, *, catalog_path: Path) -> bool:
    """Show sources/profiles editor. Returns True if catalog was saved."""
    from PyQt6.QtWidgets import (
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QFileDialog,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QMessageBox,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    catalog = load_catalog(catalog_path)
    changed = False

    dialog = QDialog(parent)
    dialog.setWindowTitle("Manage sources and profiles")
    dialog.resize(560, 520)
    layout = QVBoxLayout(dialog)

    source_list = QListWidget()
    layout.addWidget(QLabel("Sources (local directory)"))
    layout.addWidget(source_list)

    add_row = QWidget()
    add_layout = QHBoxLayout(add_row)
    add_layout.setContentsMargins(0, 0, 0, 0)
    name_entry = QLineEdit()
    name_entry.setPlaceholderText("Name")
    path_display = QLineEdit()
    path_display.setReadOnly(True)
    path_display.setPlaceholderText("Directory path")
    browse_btn = QPushButton("Browse…")
    add_btn = QPushButton("Add")
    delete_btn = QPushButton("Delete")
    add_layout.addWidget(name_entry)
    add_layout.addWidget(path_display)
    add_layout.addWidget(browse_btn)
    add_layout.addWidget(add_btn)
    add_layout.addWidget(delete_btn)
    layout.addWidget(add_row)

    layout.addWidget(QLabel("Profiles (L/R preset)"))
    profile_combo = QComboBox()
    layout.addWidget(profile_combo)

    slots_row = QWidget()
    slots_layout = QHBoxLayout(slots_row)
    slots_layout.setContentsMargins(0, 0, 0, 0)
    slot_l = QComboBox()
    slot_r = QComboBox()
    slots_layout.addWidget(QLabel("L"))
    slots_layout.addWidget(slot_l)
    slots_layout.addWidget(QLabel("R"))
    slots_layout.addWidget(slot_r)
    layout.addWidget(slots_row)

    profile_actions = QWidget()
    profile_actions_layout = QHBoxLayout(profile_actions)
    profile_actions_layout.setContentsMargins(0, 0, 0, 0)
    new_profile_name = QLineEdit()
    new_profile_name.setPlaceholderText("New profile name")
    add_profile_btn = QPushButton("Add profile")
    delete_profile_btn = QPushButton("Delete profile")
    profile_actions_layout.addWidget(new_profile_name)
    profile_actions_layout.addWidget(add_profile_btn)
    profile_actions_layout.addWidget(delete_profile_btn)
    layout.addWidget(profile_actions)

    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)

    pending_path: dict[str, Path | None] = {"value": None}

    def _refresh_source_list() -> None:
        source_list.clear()
        for entry in list_sources(catalog):
            source_list.addItem(f"{entry.name} — {entry.path}")

    def _source_slot_items() -> list[tuple[str, str]]:
        return source_slot_items(catalog)

    def _apply_profile_slots(member_l: str | None, member_r: str | None) -> None:
        apply_profile_slot_combos(
            slot_l,
            slot_r,
            member_l=member_l,
            member_r=member_r,
            items=_source_slot_items(),
        )

    def _refresh_profile_combo(select_id: str | None = None) -> None:
        profiles = list_profiles(catalog)
        if select_id is None or not str(select_id).strip():
            prior = profile_combo.currentData()
            if prior:
                select_id = str(prior)

        profile_combo.blockSignals(True)
        profile_combo.clear()
        if not profiles:
            profile_combo.addItem("— none —", "")
            _apply_profile_slots(None, None)
            profile_combo.blockSignals(False)
            return

        selected = str(select_id).strip() if select_id else profiles[0].id
        selected_index = 0
        for idx, entry in enumerate(profiles):
            profile_combo.addItem(entry.name, entry.id)
            if entry.id == selected:
                selected_index = idx
        profile_combo.setCurrentIndex(selected_index)
        current = get_profile(catalog, str(profile_combo.currentData() or selected))
        if current is not None:
            _apply_profile_slots(current.members.L, current.members.R)
        profile_combo.blockSignals(False)

    def _persist() -> None:
        nonlocal changed
        save_catalog(catalog, catalog_path)
        changed = True

    def _on_browse() -> None:
        folder = QFileDialog.getExistingDirectory(dialog, "Select source directory")
        if folder:
            pending_path["value"] = Path(folder)
            path_display.setText(folder)

    def _on_add_source() -> None:
        name = name_entry.text().strip()
        folder = pending_path["value"]
        if folder is None:
            QMessageBox.warning(dialog, "Add source", "Browse for a directory first.")
            return
        try:
            add_source(catalog, name=name, path=folder)
            _persist()
            _refresh_source_list()
            _refresh_profile_combo(profile_combo.currentData())
            name_entry.clear()
            path_display.clear()
            pending_path["value"] = None
        except ValueError as exc:
            QMessageBox.warning(dialog, "Add source", str(exc))

    def _on_delete_source() -> None:
        row = source_list.currentRow()
        sources = list_sources(catalog)
        if row < 0 or row >= len(sources):
            return
        entry = sources[row]
        try:
            delete_source(catalog, entry.id)
            _persist()
            _refresh_source_list()
            _refresh_profile_combo(profile_combo.currentData())
        except ValueError as exc:
            QMessageBox.warning(dialog, "Delete source", str(exc))

    def _on_profile_changed() -> None:
        profile_id = profile_combo.currentData()
        if not profile_id:
            _apply_profile_slots(None, None)
            return
        current = get_profile(catalog, str(profile_id))
        if current is None:
            return
        _apply_profile_slots(current.members.L, current.members.R)

    def _on_slot_changed() -> None:
        profile_id = profile_combo.currentData()
        if not profile_id:
            return
        try:
            update_profile(
                catalog,
                str(profile_id),
                members={"L": slot_l.currentData() or None, "R": slot_r.currentData() or None},
            )
            _persist()
        except ValueError as exc:
            QMessageBox.warning(dialog, "Update profile", str(exc))
            _refresh_profile_combo(str(profile_id))

    def _on_add_profile() -> None:
        name = new_profile_name.text().strip()
        if not name:
            QMessageBox.warning(dialog, "Add profile", "Profile name is required.")
            return
        try:
            entry = add_profile(catalog, name=name, members={"L": None, "R": None})
            _persist()
            _refresh_profile_combo(entry.id)
            new_profile_name.clear()
        except ValueError as exc:
            QMessageBox.warning(dialog, "Add profile", str(exc))

    def _on_delete_profile() -> None:
        profile_id = profile_combo.currentData()
        if not profile_id:
            return
        try:
            delete_profile(catalog, str(profile_id))
            _persist()
            _refresh_profile_combo()
        except ValueError as exc:
            QMessageBox.warning(dialog, "Delete profile", str(exc))

    browse_btn.clicked.connect(_on_browse)
    add_btn.clicked.connect(_on_add_source)
    delete_btn.clicked.connect(_on_delete_source)
    profile_combo.currentIndexChanged.connect(_on_profile_changed)
    slot_l.currentIndexChanged.connect(_on_slot_changed)
    slot_r.currentIndexChanged.connect(_on_slot_changed)
    add_profile_btn.clicked.connect(_on_add_profile)
    delete_profile_btn.clicked.connect(_on_delete_profile)

    _refresh_source_list()
    _refresh_profile_combo()

    dialog.exec()
    return changed

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
from harite.sources_remote import (
    CODH_KEYWORD_MAX_LEN,
    apply_codh_keyword_to_settings,
    codh_keyword_from_settings,
    is_remote_kind,
    load_codh_keyword_settings,
    source_supports_codh_keyword,
    sync_remote_source,
    validate_codh_keyword,
)


def _normalize_id(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _select_combo_by_data(combo: Any, value: object) -> bool:
    target = _normalize_id(value)
    if target is None:
        if combo.count() > 0:
            combo.setCurrentIndex(0)
        return False
    for index in range(combo.count()):
        if _normalize_id(combo.itemData(index)) == target:
            combo.setCurrentIndex(index)
            return True
    if combo.count() > 0:
        combo.setCurrentIndex(0)
    return False


def source_slot_items(catalog: Catalog) -> list[tuple[str, str]]:
    from harite.gui.adapters_qt.qt_source_catalog import slideshow_source_combo_label

    items = [("— empty —", "")]
    for entry in list_sources(catalog):
        items.append((slideshow_source_combo_label(entry), entry.id))
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
    selected = _normalize_id(selected_id) or ""
    index_to_select = 0
    for idx, (label, value) in enumerate(items):
        combo.addItem(label, value)
        if (_normalize_id(value) or "") == selected:
            index_to_select = idx
    combo.setCurrentIndex(index_to_select)
    if block_signals:
        combo.blockSignals(False)


def read_slot_members(slot_l: Any, slot_r: Any) -> dict[str, str | None]:
    return {
        "L": _normalize_id(slot_l.currentData()),
        "R": _normalize_id(slot_r.currentData()),
    }


def apply_profile_slot_combos(
    slot_l: Any,
    slot_r: Any,
    *,
    member_l: str | None,
    member_r: str | None,
    items: list[tuple[str, str]],
    loading_state: dict[str, bool] | None = None,
) -> None:
    """Set L/R slot combos without persisting programmatic loads to catalog."""
    if loading_state is not None:
        loading_state["profile_slots_loading"] = True
    slot_l.blockSignals(True)
    slot_r.blockSignals(True)
    try:
        fill_source_slot_combo(slot_l, member_l, items, block_signals=False)
        fill_source_slot_combo(slot_r, member_r, items, block_signals=False)
    finally:
        slot_r.blockSignals(False)
        slot_l.blockSignals(False)
        if loading_state is not None:
            loading_state["profile_slots_loading"] = False


def run_source_registry_dialog(
    parent: Any,
    *,
    catalog_path: Path,
    settings_path: Path | None = None,
) -> bool:
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

    from harite.gui.adapters_qt.qt_source_catalog import materialize_source_catalog_at_path
    from harite.settings_file import resolve_default_settings_path, save_settings

    resolved_settings_path = settings_path or resolve_default_settings_path()
    catalog = materialize_source_catalog_at_path(catalog_path)
    settings_data = load_codh_keyword_settings(resolved_settings_path)
    changed = False
    settings_changed = False
    persisted_keyword = {"value": codh_keyword_from_settings(settings_data)}

    dialog = QDialog(parent)
    dialog.setWindowTitle("Manage sources and profiles")
    dialog.resize(560, 520)
    layout = QVBoxLayout(dialog)

    source_list = QListWidget()
    layout.addWidget(QLabel("Sources"))
    layout.addWidget(source_list)

    keyword_row = QWidget()
    keyword_row_layout = QHBoxLayout(keyword_row)
    keyword_row_layout.setContentsMargins(0, 0, 0, 0)
    keyword_label = QLabel("keyword(CODH)")
    keyword_entry = QLineEdit(persisted_keyword["value"])
    keyword_entry.setMaxLength(CODH_KEYWORD_MAX_LEN)
    keyword_row_layout.addWidget(keyword_label)
    keyword_row_layout.addWidget(keyword_entry, 1)
    layout.addWidget(keyword_row)

    source_actions = QWidget()
    source_actions_layout = QHBoxLayout(source_actions)
    source_actions_layout.setContentsMargins(0, 0, 0, 0)
    refresh_source_btn = QPushButton("Refresh")
    delete_btn = QPushButton("Delete")
    source_actions_layout.addWidget(refresh_source_btn)
    source_actions_layout.addStretch(1)
    source_actions_layout.addWidget(delete_btn)
    layout.addWidget(source_actions)

    add_row = QWidget()
    add_layout = QHBoxLayout(add_row)
    add_layout.setContentsMargins(0, 0, 0, 0)
    name_entry = QLineEdit()
    name_entry.setPlaceholderText("Local directory name")
    path_display = QLineEdit()
    path_display.setReadOnly(True)
    path_display.setPlaceholderText("Directory path")
    browse_btn = QPushButton("Browse…")
    add_btn = QPushButton("Add local")
    add_layout.addWidget(name_entry)
    add_layout.addWidget(path_display)
    add_layout.addWidget(browse_btn)
    add_layout.addWidget(add_btn)
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
    layout.addWidget(buttons)

    pending_path: dict[str, Path | None] = {"value": None}
    editor_state: dict[str, bool] = {"profile_slots_loading": False}
    active_profile_id: dict[str, str | None] = {"value": None}

    def _read_slot_members() -> dict[str, str | None]:
        return read_slot_members(slot_l, slot_r)

    def _flush_profile_slots(profile_id: str | None) -> None:
        if not profile_id:
            return
        update_profile(catalog, profile_id, members=_read_slot_members())
        _persist()

    def _selected_source_entry():
        row = source_list.currentRow()
        sources = list_sources(catalog)
        if row < 0 or row >= len(sources):
            return None
        return sources[row]

    def _refresh_source_list() -> None:
        source_list.clear()
        for entry in list_sources(catalog):
            kind_hint = entry.kind if is_remote_kind(entry.kind) else "local-dir"
            source_list.addItem(f"{entry.name} [{kind_hint}] — {entry.path}")

    def _sync_keyword_field_from_selection() -> None:
        entry = _selected_source_entry()
        keyword_entry.setEnabled(entry is not None and source_supports_codh_keyword(entry))
        keyword_entry.setText(persisted_keyword["value"])

    def _flush_keyword_to_settings() -> None:
        nonlocal settings_data, settings_changed
        keyword = validate_codh_keyword(keyword_entry.text())
        if keyword == persisted_keyword["value"]:
            return
        settings_data = apply_codh_keyword_to_settings(settings_data, keyword)
        save_settings(resolved_settings_path, settings_data)
        persisted_keyword["value"] = keyword
        settings_changed = True

    def _on_refresh_source() -> None:
        entry = _selected_source_entry()
        if entry is None:
            QMessageBox.information(dialog, "Refresh", "Select a source first.")
            return
        if not is_remote_kind(entry.kind):
            QMessageBox.information(dialog, "Refresh", "Refresh applies to remote sources only.")
            return
        try:
            if source_supports_codh_keyword(entry):
                _flush_keyword_to_settings()
            sync_remote_source(catalog, entry.id)
            _persist()
            _refresh_source_list()
        except ValueError as exc:
            QMessageBox.warning(dialog, "Refresh", str(exc))

    def _on_source_selection_changed() -> None:
        _sync_keyword_field_from_selection()

    def _source_slot_items() -> list[tuple[str, str]]:
        return source_slot_items(catalog)

    def _apply_profile_slots(member_l: str | None, member_r: str | None) -> None:
        apply_profile_slot_combos(
            slot_l,
            slot_r,
            member_l=member_l,
            member_r=member_r,
            items=_source_slot_items(),
            loading_state=editor_state,
        )

    def _refresh_profile_combo(select_id: str | None = None) -> None:
        profiles = list_profiles(catalog)
        if select_id is None or not str(select_id).strip():
            prior = _normalize_id(profile_combo.currentData())
            if prior:
                select_id = prior

        profile_combo.blockSignals(True)
        profile_combo.clear()
        if not profiles:
            profile_combo.addItem("— none —", "")
            _apply_profile_slots(None, None)
            profile_combo.blockSignals(False)
            return

        for entry in profiles:
            profile_combo.addItem(entry.name, entry.id)

        selected = _normalize_id(select_id) or profiles[0].id
        if not _select_combo_by_data(profile_combo, selected):
            profile_combo.setCurrentIndex(0)
            selected = _normalize_id(profiles[0].id)

        current = get_profile(catalog, selected or "")
        if current is not None:
            _apply_profile_slots(current.members.L, current.members.R)
        profile_combo.blockSignals(False)
        active_profile_id["value"] = _normalize_id(profile_combo.currentData())

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
            _refresh_profile_combo(_normalize_id(profile_combo.currentData()))
            name_entry.clear()
            path_display.clear()
            pending_path["value"] = None
        except ValueError as exc:
            QMessageBox.warning(dialog, "Add source", str(exc))

    def _on_delete_source() -> None:
        entry = _selected_source_entry()
        if entry is None:
            return
        try:
            delete_source(catalog, entry.id)
            _persist()
            _refresh_source_list()
            _refresh_profile_combo(_normalize_id(profile_combo.currentData()))
        except ValueError as exc:
            QMessageBox.warning(dialog, "Delete source", str(exc))

    def _on_profile_changed() -> None:
        if editor_state.get("profile_slots_loading"):
            return

        new_id = _normalize_id(profile_combo.currentData())
        previous_id = active_profile_id["value"]
        if previous_id and previous_id != new_id:
            try:
                _flush_profile_slots(previous_id)
            except ValueError as exc:
                QMessageBox.warning(dialog, "Update profile", str(exc))
                profile_combo.blockSignals(True)
                _select_combo_by_data(profile_combo, previous_id)
                profile_combo.blockSignals(False)
                return

        active_profile_id["value"] = new_id
        if not new_id:
            _apply_profile_slots(None, None)
            return
        current = get_profile(catalog, new_id)
        if current is None:
            return
        _apply_profile_slots(current.members.L, current.members.R)

    def _on_add_profile() -> None:
        name = new_profile_name.text().strip()
        if not name:
            QMessageBox.warning(dialog, "Add profile", "Profile name is required.")
            return
        try:
            entry = add_profile(catalog, name=name, members=_read_slot_members())
            _persist()
            active_profile_id["value"] = entry.id
            _refresh_profile_combo(entry.id)
            new_profile_name.clear()
        except ValueError as exc:
            QMessageBox.warning(dialog, "Add profile", str(exc))

    def _on_delete_profile() -> None:
        profile_id = _normalize_id(profile_combo.currentData())
        if not profile_id:
            return
        try:
            delete_profile(catalog, profile_id)
            _persist()
            _refresh_profile_combo()
        except ValueError as exc:
            QMessageBox.warning(dialog, "Delete profile", str(exc))

    browse_btn.clicked.connect(_on_browse)
    add_btn.clicked.connect(_on_add_source)
    source_list.currentRowChanged.connect(lambda *_args: _on_source_selection_changed())
    refresh_source_btn.clicked.connect(_on_refresh_source)
    delete_btn.clicked.connect(_on_delete_source)
    profile_combo.currentIndexChanged.connect(_on_profile_changed)
    add_profile_btn.clicked.connect(_on_add_profile)
    delete_profile_btn.clicked.connect(_on_delete_profile)

    _refresh_source_list()
    _refresh_profile_combo()
    _sync_keyword_field_from_selection()

    def _close_dialog() -> None:
        if not editor_state.get("profile_slots_loading"):
            try:
                _flush_profile_slots(active_profile_id["value"])
            except ValueError:
                pass
        try:
            _flush_keyword_to_settings()
        except ValueError:
            pass
        dialog.reject()

    buttons.rejected.connect(_close_dialog)

    dialog.exec()
    return changed or settings_changed

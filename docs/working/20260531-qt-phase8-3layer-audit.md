# Qt Phase 8 三層照合監査レポート

作成日: 2026-05-31  
対象: `src/harite/gui/adapters_qt/qt_backend.py` (Phase 8 signal wiring)  
照合源: `docs/specs/gui/harite-gui-spec.md` / `tests/gui/test_qt_signal_wiring.py` / `src/harite/gui/adapters_qt/qt_backend.py`

---

## 凡例

| 記号 | 意味 |
|---|---|
| ✅ | 仕様・テスト・実装 すべて整合 |
| 🐛 | 実装バグ（既修正 or 未修正） |
| ❌ | 仕様に記載された振る舞いが未実装 |
| ⚠️ | テスト漏れ（実装は存在するが自動テストなし） |

---

## 1. コールバック引数順序

### on_pick_input

| 層 | 内容 |
|---|---|
| 仕様 (gui-spec §4) | 入力パス選択後に `MainWindow.on_pick_input(path, side)` を呼ぶ |
| GTK 実装 | `callback(filename, side)` — (path, side) 順 |
| Qt 実装 (修正前) | `callback(side, path)` — **逆順** |
| Qt 実装 (修正後 ed72e83) | `callback(path, side)` — 正しい |
| テスト | ❌ 引数順序を検証するテストなし |

**ステータス: 🐛 修正済み / ⚠️ テスト要追加**

### on_pick_slideshow_srcdir

| 層 | 内容 |
|---|---|
| 仕様 (gui-spec §6) | `MainWindow.on_pick_slideshow_srcdir(path, side)` |
| GTK 実装 | `callback(folder, side)` — (path, side) 順 |
| Qt 実装 (修正前) | `callback(side, path)` — **逆順** |
| Qt 実装 (修正後 ed72e83) | `callback(path, side)` — 正しい |
| テスト | ❌ 引数順序を検証するテストなし |

**ステータス: 🐛 修正済み / ⚠️ テスト要追加**

---

## 2. Export Image (Save) フロー

| 層 | 内容 |
|---|---|
| 仕様 (gui-spec §3 "Export Image") | ① `on_save_as()` (no-arg) でダイアログ open 状態を設定 → ② ファイル選択後 `on_save_path_selected(path)` → ③ キャンセル時 `on_save_path_selection_canceled()` → ④ どちらの場合も最終的に `on_close_save_path_dialog()` |
| GTK 実装 | `on_save_as()` 呼び出し後、native dialog または fallback path で `_handle_save_path_confirm(path)` → `on_save_path_selected(path)` |
| Qt 実装 (現状) | `callback = on_save_as`, `callback(path)` — **`on_save_as` は引数なしのため TypeError が発生、または Path として解釈される** |
| テスト | ❌ save フロー全体のテストなし |

**ステータス: 🐛 未修正 — on_save_as() は引数を取らない。Qt 実装は on_save_as() → Qt file dialog → on_save_path_selected(path) → on_close_save_path_dialog() の正しいフローに書き直す必要あり**

---

## 3. ダイアログ close ハンドラの未呼び出し

### 3-A. on_close_open_image_dialog

| 層 | 内容 |
|---|---|
| 仕様 | ファイル選択 dialog が閉じるたびに呼ぶ (`MainWindow.open_image_dialog_open = False` を設定) |
| GTK 実装 | GTK destroy 通知で `_notify_open_dialog_destroy()` → `on_close_open_image_dialog()` |
| Qt 実装 | `_on_pick_input_clicked` の `_confirmed` と proxy.open() のどちらも呼ばない |
| テスト | ❌ |

**ステータス: ❌ 未実装 — confirm/cancel どちらの後も呼ぶ必要あり**

### 3-B. on_close_srcdir_dialog

| 層 | 内容 |
|---|---|
| 仕様 | srcdir dialog が閉じるたびに呼ぶ |
| GTK 実装 | `_notify_srcdir_dialog_destroy()` → `on_close_srcdir_dialog()` |
| Qt 実装 | `_on_pick_srcdir_clicked` の `_confirmed` のみ呼び、close は未通知 |
| テスト | ❌ |

**ステータス: ❌ 未実装**

### 3-C. on_save_path_selection_canceled / on_close_save_path_dialog

| 層 | 内容 |
|---|---|
| 仕様 | キャンセル時 `on_save_path_selection_canceled()` + `on_close_save_path_dialog()` |
| Qt 実装 | どちらも未呼び出し |
| テスト | ❌ |

**ステータス: ❌ 未実装**

---

## 4. Apply mode ヘルプラベル未更新

| 層 | 内容 |
|---|---|
| 仕様 (gui-spec §4) | `No Split` 時: `Apply the optimized image as a single file.` / `Auto-Split` 時: `Split the optimized image and apply per display.` を `lblApplyMode` に表示する |
| GTK 実装 (`gtk_backend._on_apply_mode_toggled` line 989-992) | `self._set_label_text("lblApplyMode", label)` を実行している |
| Qt 実装 | `on_settings_apply_mode_toggled` を呼ぶだけで `lblApplyMode` 更新なし |
| テスト | ❌ |

**ステータス: ❌ 未実装**

---

## 5. Slideshow mode ヘルプラベル未更新

| 層 | 内容 |
|---|---|
| 仕様 (gui-spec §6) | `sequential` 時: `Sequential rotates images.` / `random` 時: `Random rotates images.` を `lblSlideshowModeHelp` に表示する |
| GTK 実装 (`gtk_backend._on_slideshow_mode_toggled` line 1012-1015) | `self._set_label_text("lblSlideshowModeHelp", help_text)` を実行している |
| Qt 実装 | `_on_slideshow_mode_toggled` に当該ロジックなし |
| テスト | ❌ |

**ステータス: ❌ 未実装**

---

## 6. Apply mode 同期スコープの相違

| 層 | 内容 |
|---|---|
| 仕様 (gui-spec §4) | apply mode 変更後は preview 面を同期する |
| GTK 実装 | `_sync_preview_state_from_owner(owner)` |
| Qt 実装 | `_sync_non_preview_state_from_owner(owner)` (スコープが広すぎる) |
| テスト | ❌ |

**ステータス: ⚠️ 機能は損なわないが spec から乖離**

---

## 7. 整合確認済み項目

| ハンドラ | 仕様 | テスト | 実装 | 状態 |
|---|---|---|---|---|
| on_pick_input (修正後) | (path,side) | テスト不足 | 修正済 | ✅ |
| on_clear_input | `callback(side)` | ⚠️ | ✓ | ✅ |
| on_optimize | `callback()` | ✓ | ✓ | ✅ |
| on_apply | `callback()` | ✓ | ✓ | ✅ |
| on_slideshow_start | `callback()` | ✓ | ✓ | ✅ |
| on_slideshow_stop | `callback()` | ✓ | ✓ | ✅ |
| on_change_margins | `callback(margin_str)` | ⚠️ | ✓ | ✅ |
| on_change_margin_text_mode | `callback(value)` | ⚠️ | ✓ | ✅ |
| on_change_margin_text_position | `callback(value)` | ⚠️ | ✓ | ✅ |
| on_change_margin_text_max_lines | `callback(int)` | ⚠️ | ✓ | ✅ |
| on_close_settings_dialog | `callback()` | ⚠️ | ✓ | ✅ |
| on_close_about_dialog | `callback()` | ⚠️ | ✓ | ✅ |

---

## 修正優先順位

| 優先度 | 項目 | 影響 |
|---|---|---|
| 高 | §2 Export Image フロー (`on_save_as` 引数・`on_save_path_selected` 未呼び出し) | TypeError / 保存不可 |
| 高 | §3 ダイアログ close ハンドラ未呼び出し (3 件) | MainWindow state 齟齬 |
| 中 | §4 Apply mode ヘルプラベル | 視覚フィードバック欠如 |
| 中 | §5 Slideshow mode ヘルプラベル | 視覚フィードバック欠如 |
| 低 | §6 Apply mode 同期スコープ | 機能的問題なし |

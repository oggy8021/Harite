# W-03-B-lite 3層比較（spec / tests / impl）

実施日: 2026-05-31  
対象: Windows Span（B-lite）— issue #343 / gui-spec / plugin-spec 追記

## 参照 spec

| 文書 | 要点 |
|------|------|
| `docs/specs/gui/harite-gui-spec.md` | Windows ラベル **Span**、2+ display 既定 Span、`windows_apply_span` opt-in、プレビュー B' |
| `docs/specs/plugins/harite-plugin-spec.md` §4.1 | Windows plugin は single-file のみ；Span は core が single-file に解決 |
| `docs/online-issues/issue-343.md` | B-lite 方針、Tile 非推奨、style restore 非実装 |

## 比較マトリクス

| 要件 | spec | tests | impl | 判定 |
|------|------|-------|------|------|
| Win32 `per-monitor-auto-split` → single-file + `windows_span` | gui-spec | `test_resolve_apply_settings_windows_span_mode_uses_single_file` | `apply_settings.resolve_apply_settings` | OK |
| `windows_apply_span` 設定キー（既定 false） | gui-spec | **追加** `test_apply_settings_windows_apply_span_roundtrip` | `ApplySettings` | OK（テスト追加） |
| Windows 2+ display 既定 Span | gui-spec | **追加** `test_default_apply_mode_windows_two_displays` | `AppSettings._default_apply_mode` | OK |
| MainWindow 初期 `apply_mode` が上記と一致 | gui-spec | **追加** 同上 | `MainWindow.__init__` → `preferences.apply.apply_mode` | **修正済** |
| UI ラベル Span / No Split | gui-spec | `test_apply_surface`, **追加** Qt Span ラベル | `apply_surface`, tab builders | OK |
| プレビュー B'（monitor region） | gui-spec | `test_preview_result_notes_windows_span_mode` | `apply_surface`, preview adapters | OK |
| Apply 前 `ensure_span_style`（opt-in のみ） | gui-spec | **追加** `test_ensure_span_style_sets_registry` | `windows_wallpaper`, `MainWindow._apply_latest` | OK（テスト追加） |
| Slideshow も Span 経路 | issue-343 | 既存 slideshow テスト（Linux 中心） | `MainWindow` slideshow apply | OK（手動 Windows 確認） |
| Settings チェックボックス GTK/Qt | gui-spec | GTK settings sync 既存 | Qt + **GTK checkbox 追加** | **修正済** |
| connect 後 UI と owner の apply mode 一致 | gui-spec 暗黙 | — | **追加** `sync_apply_mode_from_owner` | **修正済** |
| plugin-spec §4.1 B-lite 記載 | plugin-spec | — | — | **追記済** |
| Style restore | issue-343 非実装 | なし | なし | 意図的スコープ外 |
| core-spec への Span 解決記載 | 任意 | — | — | 未着手（低優先） |

## 検出ギャップと対応

### 修正した impl ギャップ

1. **`MainWindow._default_apply_mode`** — XFCE のみの旧ロジック → `AppSettings._default_apply_mode(plugin_name)` に委譲。初期値は `preferences.apply.apply_mode` から取得。
2. **`gtk_backend._default_apply_mode` / `qt_tab_main._default_apply_mode`** — `"windows"` 固定または XFCE のみ → ホスト plugin 推定 + `AppSettings._default_apply_mode`。
3. **GTK Settings `chkWindowsApplySpan`** — runtime が参照するが dialog builder に未配置 → checkbox 追加 + object registry 登録。
4. **起動時 apply mode ラジオ不一致** — settings ロード後も UI が layout 時 default のまま → `sync_apply_mode_from_owner` を `sync_main_state_from_owner` から呼ぶ。
5. **GTK `_on_apply_mode_toggled`** — ハードコード Linux 文言 → `apply_surface.apply_mode_help_text` に統一。

### テスト追加

- `tests/test_windows_wallpaper.py` — winreg mock
- `tests/test_settings_apply.py` — `windows_apply_span` / default mode
- `tests/gui/test_qt_tab_main.py` — Windows Span ラベル

### 意図的に残す項目

- **core-spec** への Windows span 解決の明文化（plugin-spec で足りる）
- **E2E Windows Apply** — CI は Linux；ユーザー環境で Span ON/OFF 確認
- **Style restore** — slideshow 破壊リスクのため B-lite スコープ外

## 結論

3層比較で **6 件の impl ギャップ** と **4 件のテストギャップ** を検出。本 PR で impl 修正・plugin-spec 追記・不足テスト追加まで含める。

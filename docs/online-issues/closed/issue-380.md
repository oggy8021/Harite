# Issue #380

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/380>
- opened: 2026-06-02
- **closed: 2026-06-04**（XFCE 実機確認後、#402 マージ）
- title: `Windows以外の設定ダイアログにおいて、 Windows とのラベルだけの箇所がある`

## 事象

- Windows では Settings に「Windows」行と `Apply with Span when using Span mode` チェックボックスが表示される。
- XFCE（Qt バックエンド）ではチェックボックスだけ `setVisible(False)` され、行ラベル「Windows」だけが残る。

## 分類

- `bug` / `polish` → **resolved**

## 関連

- feature-overview: W-03 B-lite — [20260518-2047-feature-overview.md](../../working/finished/20260518-2047-feature-overview.md)
- 正本: [harite-gui-spec.md](../../specs/gui/harite-gui-spec.md) — `windows_apply_span`
- 他 Issue: [#343](issue-343.md)（Span opt-in 実装）
- 実装: `src/harite/gui/adapters_qt/qt_dialogs.py`, `src/harite/gui/adapters/gtk_dialog_builders.py`

## 取り込み方針

- **完了（小 fix）。** 非 Windows ホストでは Settings の Windows 行をレイアウトに載せない（GTK も同様）。設定キー `windows_apply_span` のシリアライズ用ウィジェットはレジストリ用に残す。

## 調査メモ

- **原因（Qt）:** `_add_row("Windows", prefs_windows_apply_span)` は常に実行し、チェックボックスのみ `setVisible(False)` → 行ラベルだけ表示。
- **原因（GTK）:** `_prefs_row("Windows", ...)` に `set_no_show_all(True)` の子だけを載せると、行ラベル「Windows」は表示されたまま。
- **修正:** `is_windows_host()` のときだけ `_add_row` / `_prefs_row` を呼ぶ。非 Windows ではチェックボックスを非表示のままレジストリに登録（sync 用）。

## resolution

- **closed:** 2026-06-04
- **正本反映:** 不要（表示バグのみ）
- **PR:** [#402](https://github.com/oggy8021/Harite/pull/402)
- **手元確認:** XFCE 実機 — Settings に孤立「Windows」ラベルなし（オーナー 2026-06-04）
- **テスト:** `tests/gui/test_qt_dialogs.py::test_settings_dialog_windows_span_row_only_on_windows_host`

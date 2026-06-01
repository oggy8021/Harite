# Issue #354

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/354>
- opened: 2026-05-31
- **closed: 2026-06-01**（F-01 完了 — Windows 実機確認）
- title: `Windows) 設定ファイル置き場は、果たして $env:USERPROFILE で正しいのか。`

## 事象

- Windows 既定設定 path が `Path.home() / "harite-settings.json"`（= `%USERPROFILE%\harite-settings.json`）。
- 一般的な Windows アプリは `AppData\Local` または `AppData\Roaming` 配下に置くことが多い。
- ホーム直下が `.bash_history` や `.gitconfig` 程度しかなく、settings を直下に置く妥当性に疑問。

## 分類

- investigation / foundation → **resolved**

## 関連

- feature-overview: [F-01](../../working/20260518-2047-feature-overview.md)
- 実装: `src/harite/settings_file.py` — `resolve_default_settings_path()`
- 正本: [harite-core-spec.md §6.1](../../specs/core/harite-core-spec.md)、[harite-foundation-spec.md §7](../../specs/harite-foundation-spec.md)、[harite-gui-spec.md §5](../../specs/gui/harite-gui-spec.md)
- 参考: [Windows フォルダ構造（User Profile）](https://jpwinsup.github.io/blog/2026/04/16/ActiveDirectory/UserProfile/windows-folder-structure/)

## 取り込み方針

- **完了（F-01）。** 第2波 P-01/P-02 へ移行。
- **方針確定:** Windows 既定 path = **`%APPDATA%\harite\harite-settings.json`**（Roaming）。
- **旧 path 互換なし:** `%USERPROFILE%\harite-settings.json` からの読み取り・移行は行わない。

## 調査メモ

- memo（オーナー）: AppData 準拠を検討すべきでは、との観測。
- **2026-06-01:** Roaming 採用（オーナー）。旧 path 互換・移行は不要。
- **2026-06-01:** Windows 実機で save / 事前配置 load を確認（オーナー）。

## 3 層 audit（事後・2026-06-01）

| 層 | 内容 | PR / 根拠 |
| --- | --- | --- |
| **spec** | Windows 既定 path、APPDATA 未設定時 fallback、旧 path 非互換 | #365 — core §6.1、foundation §7 |
| **tests** | `resolve_default_settings_path`（Linux / Windows APPDATA / fallback） | #366 — `tests/test_settings_file.py` |
| **impl** | `settings_file.py` Roaming 解決 | #366 |
| **gui（gap → 修正）** | startup 読込後 Qt widget へ owner 状態を反映 | #367 — `connect_signals` で `_sync_non_preview_state_from_owner`（gui-spec §5 追記） |

**プロセスメモ:** 第1波は正本停止・テスト/impl 分離・事前 3 層 audit を省略してマージした。事後 audit で gui 層 gap を検出。第2波以降は段階停止を守る。

## resolution

- **closed:** 2026-06-01
- **正本:** [core-spec §6.1](../../specs/core/harite-core-spec.md)、[foundation-spec §7](../../specs/harite-foundation-spec.md)、[gui-spec §5 startup / widget 同期](../../specs/gui/harite-gui-spec.md)
- **PR:** #365（spec）、#366（path + tests）、#367（Qt startup widget sync）
- **手元確認:** Windows — Roaming へ save、事前配置 `harite-settings.json` の load（#367 後）

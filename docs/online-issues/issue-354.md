# Issue #354

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/354>
- opened: 2026-05-31
- title: `Windows) 設定ファイル置き場は、果たして $env:USERPROFILE で正しいのか。`

## 事象

- Windows 既定設定 path が `Path.home() / "harite-settings.json"`（= `%USERPROFILE%\harite-settings.json`）。
- 一般的な Windows アプリは `AppData\Local` または `AppData\Roaming` 配下に置くことが多い。
- ホーム直下が `.bash_history` や `.gitconfig` 程度しかなく、settings を直下に置く妥当性に疑問。

## 分類

- investigation / foundation

## 関連

- feature-overview: [F-01](../working/20260518-2047-feature-overview.md)
- 実装: `src/harite/settings_file.py` — `resolve_default_settings_path()`
- 正本候補: [harite-foundation-spec.md](../specs/harite-foundation-spec.md)（settings path 節）
- 参考: [Windows フォルダ構造（User Profile）](https://jpwinsup.github.io/blog/2026/04/16/ActiveDirectory/UserProfile/windows-folder-structure/)

## 取り込み方針

- **近端着手候補**。C-02 / P-01 / P-02 と **並行** でよい（2026-06-01 オーナー確認）。
- **方針確定（2026-06-01）:** Windows 既定 path は **`%APPDATA%\harite\harite-settings.json`**（= `AppData\Roaming\harite\`）。通例に沿い、変な配置にしない。
- 残タスク: foundation-spec / core-spec §6.1 へ反映 → impl。
- **旧 path 互換なし（2026-06-01）:** `%USERPROFILE%\harite-settings.json` からの読み取り・移行は **行わない**。Windows 正式ユーザー未存在のため。clone 開発者は Roaming 新 path へ手動で置き直す想定。
- Linux は現行どおり `XDG_CONFIG_HOME/harite/...`（`Roaming` 相当の config 領域）— 対称性は app 名サブディレクトリで揃う。

## 調査メモ

- memo（オーナー）: AppData 準拠を検討すべきでは、との観測。
- **2026-06-01:** Roaming 採用で問題なし（オーナー）。Local ではなく Roaming（設定の持ち運び・バックアップ対象として一般的）。
- 現行コード: Linux は `$XDG_CONFIG_HOME/harite/harite-settings.json`（未設定時 `~/.config/harite/...`）、Windows は `~/harite-settings.json`。
- **2026-06-01:** 旧 `%USERPROFILE%\harite-settings.json` 互換・移行は **不要**（正式 Windows ユーザー未存在）。
- 正本現状: [core-spec §6.1](../specs/core/harite-core-spec.md) は非 Linux を `~/harite-settings.json` と記載 — F-01 spec PR で Roaming に更新予定。

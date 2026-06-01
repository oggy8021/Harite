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

- **近端着手候補（調査 → spec 先行）**。C-02 とは独立。
- 先に決めること: Roaming vs Local、既存 `%USERPROFILE%` 配置ユーザーの移行要否、Linux XDG との対称性。
- 現状動作を **bug とは断定しない** — 意図確認と spec 化が先。変更する場合は migration / 後方互換を spec に書く。

## 調査メモ

- memo（オーナー）: AppData 準拠を検討すべきでは、との観測。
- 現行コード: Linux は `$XDG_CONFIG_HOME/harite/harite-settings.json`（未設定時 `~/.config/harite/...`）、Windows は `~/harite-settings.json`。

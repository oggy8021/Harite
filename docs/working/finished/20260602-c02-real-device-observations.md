# C-02 実機観測メモ

実施日: 2026-06-02  
対象: `harite-qt` Slideshow source registry（#378 マージ後）

## 対応済み（follow-up PR）

| 観測 | 対応 |
|------|------|
| catalog ファイル名 `sources.json` が `harite-settings.json` とバランス不良 | 既定名を **`harite-sources.json`** に変更。load 時のみ旧 `sources.json` を fallback |
| Manage dialog — Profiles 登録で L/R slot が 1 件ずれ | L/R combo 更新中に `currentIndexChanged` が中間状態を persist していた → **両 slot を一括 blockSignals** |

## 観測のみ（低優先・ガード未実装）

### Thunar / GVFS 経由の NAS path

- Thunar から見える NAS ディレクトリを Sources に追加すると、path として  
  `/run/user/1000/gvfs/smb-share:server=fortress.local,share=share/Picture`  
  のような **GVFS マウント path** がそのまま登録される。
- Linux では `Path.resolve()` / directory 存在チェックを通過しうるが、**永続的に参照すべき path ではない**。
- この path を Slideshow 実行すると、ターミナルに GLib-GIO-CRITICAL が出る例:

```text
(python3:186470): GLib-GIO-CRITICAL **: GFileInfo created without standard::content-type
(python3:186470): GLib-GIO-CRITICAL **: g_file_info_get_content_type: should not be reached
```

- **クラッシュ等は確認されていない**（2026-06-02 観測）。
- 将来検討: GVFS path 拒否、mount 済み実 path への正規化、または source-spec §4 に Linux NAS 向け注意書き。

## 参照

- [harite-source-spec.md](../../specs/source/harite-source-spec.md) §6.1
- [20260601-c02-3layer-audit.md](20260601-c02-3layer-audit.md)（#379 — audit close PR）

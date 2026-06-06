# C-01-E — 軽量 3-layer audit（NDL / CODH）

最終更新: 2026-06-06

## 位置づけ

| 項目 | 内容 |
| --- | --- |
| 親 | [C-01 3-layer audit（JMA）](20260603-c01-3layer-audit.md) の provider 拡張 |
| 統合索引 | [20260603-c01-e-merged-inventory.md](20260603-c01-e-merged-inventory.md) |
| 実装 | #400 merge（`remote-ndl-tsugidigi` / `remote-codh-edo` + preset 5 種） |

本書は C-01 本 audit の **差分確認** のみ。気象庁（§15.5）の再監査は [20260603-c01-3layer-audit.md](20260603-c01-3layer-audit.md) を正とする。

## 3 層照合

| 層 | 状態 | 根拠 |
| --- | --- | --- |
| **spec** | OK | [harite-source-spec.md](../../specs/source/harite-source-spec.md) §12.3–12.4、§15.6–15.7 |
| **tests** | OK | `test_c01_remote_ndl_codh_sync.py`、`test_c01_remote_cache_prune.py`、preset 件数更新 |
| **impl** | OK | `sources_remote.py`、`harite-source-presets.json`、`qt_source_catalog.py`（materialize 非ブロック + prune）、`resolve` 再作成 |

## 実機・オーナー確認（要約）

[統合索引 §実現性検証](20260603-c01-e-merged-inventory.md) に記録。NDL L/R、CODH 桜/おまかせ、cache UUID 削除・再作成、Start 直前 sync。

## 意図的に残す / 先送り

| 項目 | 扱い |
| --- | --- |
| CODH キーワードユーザー指定 | **完了**（#413）— [C-01-E-KW planning](20260605-c01-e-kw-codh-keyword-planning.md) |
| NDL 地図 facet の見た目 | ML タグのため文字中心もありうる（inventory 記載） |
| 専用「キャッシュ掃除」GUI | 不要 — materialize 時 `prune_orphan_remote_cache_dirs` |

## 結論

**C-01-E（V1）は完了** — spec / tests / impl / 実現性検証が一致。**C-01-E-KW**（#413）も完了。次の inventory 入口は [feature-overview](../20260518-2047-feature-overview.md) §1（P-05 / P-03）。

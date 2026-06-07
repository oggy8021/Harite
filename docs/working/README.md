# working

正本（`docs/specs/`）改訂前の planning / gap analysis / 横断 backlog を置く。

## ディレクトリ構成

```text
docs/working/
  YYYYMMDD-HHMM-説明.md   ← 進行中（現状は overview のみ）
  design/                  ← GUI mock / 見た目合意 artifact（HTML 等）
  finished/
    YYYYMMDD-HHMM-説明.md ← 完了（テーマ確定・正本反映後に git mv）
```

ファイル名は `.cursorrules` §7 の `YYYYMMDD-HHMM-説明.md` 形式。

## 現在の active（`working/` 直下）

| ファイル | 内容 |
| --- | --- |
| [20260518-2047-feature-overview.md](20260518-2047-feature-overview.md) | post-1.0.0 機能 inventory（C-xx / W-xx / P-xx）。**継続更新する唯一の planning 入口** |
| [20260608-p08-main-margins-drawer-planning-draft.md](20260608-p08-main-margins-drawer-planning-draft.md) | P-08 Main + Margins Drawer — gate pass、gui-spec #433 反映済。**impl 完了後**に `finished/` へ |

**2026-06-08 棚卸:** 直下は **overview + P-08 planning** のみ。完了済み P-04〜P-07 / C-01-F / C-04 は [finished/](finished/)。design の P-08 slice は gate 記録として [design/](design/20260608-p08-main-margins-drawer-slice-memo.md) に残す。

## design（GUI 合意 artifact）

icon board / widget slice 等は [design/README.md](design/README.md) を参照。実装済み slice も参照用に残す。

## finished アーカイブ

[finished/README.md](finished/README.md) — Qt 移行、Windows backlog、第4波 planning / inventory / audit、C-01-F / C-04。

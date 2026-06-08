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
| [20260609-1200-feature-overview.md](20260609-1200-feature-overview.md) | 第2期 inventory 入口（熟成運転期間）。**継続更新する唯一の planning 入口** |
| [20260608-1200-feature-pending.md](20260608-1200-feature-pending.md) | 破棄候補 / 保留延長（H-xx / K-05 等） |

**2026-06-09 分割:** 第1期完了記録は [finished/20260518-2047-feature-overview.md](finished/20260518-2047-feature-overview.md) へ。P-08 は #436 マージ・[3層 audit](../specs/gui/audit/p08-3layer-audit.md) 反映済み。

## design（GUI 合意 artifact）

icon board / widget slice 等は [design/README.md](design/README.md) を参照。実装済み slice も参照用に残す。

## finished アーカイブ

[finished/README.md](finished/README.md) — Qt 移行、Windows backlog、第4波 planning / inventory / audit、C-01-F / C-04。

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
| [20260518-2047-feature-overview.md](20260518-2047-feature-overview.md) | post-1.0.0 機能 inventory（C-xx / W-xx）。**継続更新する唯一の planning 入口** |

第4波（C-02 / C-05 / C-01 / C-01-J / C-01-E）の planning・調査・audit は **2026-06-04 に [finished/](finished/) へ移動済み**。

## design（GUI 合意 artifact）

icon board / widget slice 等は [design/README.md](design/README.md) を参照。実装済み slice も参照用に残す。

## finished アーカイブ

[finished/README.md](finished/README.md) — Qt 移行、Windows backlog、第4波 planning / inventory / audit。

# Harite Project Initial Build Reformation WS2 Docs Reformation

最終更新: 2026-05-16

## 位置づけ

- 本書は [docs/reformation/harite-project-initial-build-reformation.md](docs/reformation/harite-project-initial-build-reformation.md) の Workstream 2 を具体化する子文書である。
- 主題は、planning / closing / validation record / 常設文書 / 将来構想文書が混在した現状 docs を、運用可能な体系へ再編することである。
- 仕様書本文の執筆は Workstream 3 の主責務とし、本書ではその受け皿を整える。

## この stream で固定すること

- 何を常設文書として残すか。
- 何を履歴保存文書として残すか。
- 何を統合、縮退、アーカイブ候補とみなすか。

## 対象

- `docs/specs/gui/` の重い planning / validation 系文書群
- 大憲章、大構想資料、親文書の重複
- docs の参照導線
- 常設文書と履歴文書の役割分担

## 非対象

- packaging 実務
- release version judgement
- 仕様書本文の詳細章立て
- post-1.0.0 機能棚卸し

## 現時点の論点

### 1. 常設文書と履歴文書の境界

- 現在の docs には、今読むべきものと歴史として残すべきものが混在している。
- 特に GUI 系は phase planning と validation record が厚く、入口が重い。

### 2. 親文書の数と責務

- roadmap、closing、planning、補助メモが段階的に増えており、親文書の責務が分散しやすい。
- 正本として読む文書と、補助として参照する文書を分ける必要がある。

### 3. 大型構想資料の扱い

- 今の Harite と整合するもの
- 歴史的には有用だが常設参照には重いもの
- 役割が薄くなったもの

## 初動タスク

1. docs を「常設」「履歴」「運用」「将来構想」に仮分類する。
2. `docs/specs/gui/` の中で、常設で残すべき文書と履歴保存へ寄せる文書を粗く分ける。
3. 大憲章・大型構想資料の一覧を作り、保持理由または縮退理由を付ける。
4. 再編後の docs map の最小案を作る。

## 完了条件

- docs の役割分類が説明可能になっている。
- 常設文書と履歴保存文書の境界が説明可能になっている。
- GUI 系 docs の重さをどこで減らすか説明可能になっている。
- Workstream 3 の仕様書正本をどこへ受けるか説明可能になっている。

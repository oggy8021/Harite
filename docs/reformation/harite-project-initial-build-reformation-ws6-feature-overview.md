# Harite Project Initial Build Reformation WS6 Feature Overview

最終更新: 2026-05-20

## 位置づけ

- 本書は [docs/reformation/harite-project-initial-build-reformation.md](docs/reformation/harite-project-initial-build-reformation.md) の Workstream 6 を具体化する子文書である。
- 主題は、`1.0.0` 後の新運用で扱う後続機能の棚卸しと feature overview の作成である。
- 本書は `1.0.0` gate ではなく、その後に開く backlog / planning 入口として扱う。

## この stream で固定すること

- 断片的な feature アイデアを inventory 化する。
- 実装候補、構想保持、破棄候補を粗く切り分ける。
- post-`1.0.0` の feature planning 入口文書として、次期 planning の土台を作る。

## 対象

- 外部壁紙サイト連携
- watch / sources / plugins の将来拡張案
- GUI / CLI の新導線案
- 将来の product improvement 候補

## 非対象

- `1.0.0` 前に実装を始めること
- release / packaging 整理
- docs 再編そのもの
- 現行 surface の内部 issue 解決

## 現時点の論点

### 1. 構想の棚卸し方

- 断片メモのまま残すのではなく、一覧として集約する必要がある。
- ただし、いまは優先順位の精密化より inventory 化を優先する。

### 2. 分類の粒度

- すぐ着手候補
- 中期の構想保持
- 破棄または保留延長

### 3. 次期 planning への渡し方

- overview から次の親 planning へどう送るか。
- 単発メモを増やしすぎず、入口文書で受ける必要がある。

### 4. 入口カテゴリの初期案

- 外部ソース連携や取得導線の拡張
- watch / sources / plugins の機能拡張
- GUI / CLI の新しい利用導線
- product improvement と UX 強化

## 初動タスク

1. 現在頭にある後続機能案を列挙する。
2. それぞれを「着手候補 / 構想保持 / 破棄候補」に粗く分類する。
3. 外部壁紙サイト連携のような大きめ構想を、単発案ではなく overview 項目として受ける。
4. post-`1.0.0` planning の入口となる最小構造を定める。

## 完了条件

- 後続機能 inventory の枠組みが説明可能になっている。
- `1.0.0` gate の外に置く理由が説明可能になっている。
- 構想の受け皿として overview を置く理由が説明可能になっている。
- Workstream 1・3・4・5 と混線せずに次段へ送れる状態になっている。

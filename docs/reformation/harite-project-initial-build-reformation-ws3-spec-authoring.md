# Harite Project Initial Build Reformation WS3 Spec Authoring

最終更新: 2026-05-16

## 位置づけ

- 本書は [docs/reformation/harite-project-initial-build-reformation.md](docs/reformation/harite-project-initial-build-reformation.md) の Workstream 3 を具体化する子文書である。
- 主題は、planning 履歴の集積ではなく、現行 Harite を読むための仕様書正本を起こすことである。
- docs 再編の情報設計は Workstream 2 の主責務であり、本書はその結果を受けて仕様本文を整える。

## この stream で固定すること

- 仕様書正本は「どう決まったか」ではなく「今どうなっているか」を書く。
- 仕様書は履歴の要約ではなく、現行 Harite の理解導線である。
- GUI / CLI / watch / settings / tray を、利用者と保守者の両方が読める粒度で整理する。

## 対象

- Harite の目的と前提
- 対象利用者と主要環境
- GUI / CLI / watch の関係
- settings / save / apply / watch / tray / application icon の現行仕様
- README と常設仕様の役割分担

## 非対象

- planning 履歴の保存
- 過去判断の時系列説明
- packaging 実務
- post-1.0.0 機能構想

## 現時点の論点

### 1. 仕様書の親文書をどう切るか

- 1 枚の foundation spec に寄せるか。
- core / cli / gui / watch の分冊にするか。
- README と重複しすぎないようにどう分けるか。

### 2. 現行仕様として何を正本にするか

- GUI の現在地
- tray / app icon surface の現在地
- settings / watch / apply の現在地
- CLI との関係

### 3. 読み手の想定

- owner が日常参照する文書
- 将来の保守者が最初に読む文書
- 新機能 planning の前提として参照する文書

## 初動タスク

1. 仕様書正本の親文書候補と分冊候補を並べる。
2. 現行 Harite の正本として書くべき章題を列挙する。
3. README と仕様書の責務分担を仮置きする。
4. Workstream 2 の docs map と矛盾しない配置案を作る。

## 完了条件

- 仕様書正本の役割が説明可能になっている。
- 仕様書で扱う章題の骨格が説明可能になっている。
- planning 履歴と仕様本文の境界が説明可能になっている。
- Workstream 2 の docs 再編と矛盾しない配置方針が説明可能になっている。

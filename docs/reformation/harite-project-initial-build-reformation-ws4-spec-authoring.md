# Harite Project Initial Build Reformation WS4 Spec Authoring

最終更新: 2026-05-19

## 位置づけ

- 本書は [docs/reformation/harite-project-initial-build-reformation.md](docs/reformation/harite-project-initial-build-reformation.md) の Workstream 4 を具体化する子文書である。
- 主題は、planning 履歴の集積ではなく、現行 Harite を読むための仕様書正本を起こすことである。
- docs 再編の情報設計は Workstream 3 の主責務であり、本書はその結果を受けて仕様本文を整える。

## この stream で固定すること

- 仕様書正本は「どう決まったか」ではなく「今どうなっているか」を書く。
- 仕様書は履歴の要約ではなく、現行 Harite の理解導線である。
- GUI / CLI / watch / settings / tray を、利用者と保守者の両方が読める粒度で整理する。
- 用語ぶれや責務ずれが見えても、WS4 ではまず抽出と事実記載に留め、直す / 直さないの working は WS5 へ送る。

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
- 用語統一、rename、cleanup 実働の可否判断

## 現在の状態

- 2026-05-19 時点で、WS3 により `docs/specs/core/` `cli/` `gui/` `watch/` は正本受け皿として空け直されている。
- 仕様構成の下案は [docs/reformation/harite-project-initial-build-reformation-ws4-spec-structure-draft.md](docs/reformation/harite-project-initial-build-reformation-ws4-spec-structure-draft.md) に切り出し済みである。
- あわせて [docs/specs/harite-foundation-spec.md](docs/specs/harite-foundation-spec.md)、[docs/specs/core/harite-core-spec.md](docs/specs/core/harite-core-spec.md)、[docs/specs/cli/harite-cli-spec.md](docs/specs/cli/harite-cli-spec.md)、[docs/specs/gui/harite-gui-spec.md](docs/specs/gui/harite-gui-spec.md)、[docs/specs/watch/harite-watch-spec.md](docs/specs/watch/harite-watch-spec.md) の skeleton は作成済みである。
- したがって WS4 の主作業は、分冊線引きの再検討ではなく、各 skeleton を「今どうなっているか」を書く本文へ育てる段階に入っている。

## 現時点の論点

### 1. 仕様書の親文書をどう切るか

- foundation + core / cli / gui / watch の 5 面で開始したが、この切り方で本文を書き進めて破綻しないか。
- README と重複しすぎないように、導入説明と現行仕様の境界をどう保つか。

### 2. 現行仕様として何を正本にするか

- GUI の現在地
- tray / app icon surface の現在地
- 設定 / watch / apply の現在地
- CLI との関係

補足:

- 正本に書くのは現行挙動と現行 surface の事実であり、そこから先の rename 判断や wording 正規化は WS5 の inventory / planning に委ねる。

### 3. skeleton をどの順で厚くするか

- foundation を入口として先に厚くするか。
- core の設定ファイル・apply・メッセージ分類から固めるか。
- GUI / watch の運用面を先に具体化するか。

### 4. 読み手の想定

- owner が日常参照する文書
- 将来の保守者が最初に読む文書
- 新機能 planning の前提として参照する文書

## 初動タスク

1. foundation / core / cli / gui / watch の skeleton を、各分冊の本文へ育てる。
   - 2026-05-19 時点で skeleton 作成までは完了済み。
2. foundation に、全体像、分冊導線、ソース構成、責務境界を書く。
3. core に、設定ファイル、最適化、適用、メッセージ分類の現行仕様を書く。
4. GUI / watch に、sequence diagram と運用責務を伴う本文を書く。
5. README と仕様書の責務境界を、本文を書きながら固定する。

## 次の焦点

- [docs/specs/harite-foundation-spec.md](docs/specs/harite-foundation-spec.md) を、入口文書として読める密度まで先に厚くする。
- [docs/specs/core/harite-core-spec.md](docs/specs/core/harite-core-spec.md) の設定ファイル、apply、メッセージ分類を実装準拠で固める。
- [docs/specs/gui/harite-gui-spec.md](docs/specs/gui/harite-gui-spec.md) と [docs/specs/watch/harite-watch-spec.md](docs/specs/watch/harite-watch-spec.md) の sequence / flow 図を本文説明へ接続する。
- README に残す導入情報と、仕様書側へ寄せる現行仕様の境界を明文化する。

## 完了条件

- 仕様書正本の役割が説明可能になっている。
- 仕様書で扱う章題の骨格が説明可能になっている。
- skeleton ではなく、現行仕様を読める本文として各分冊が成立している。
- planning 履歴と仕様本文の境界が説明可能になっている。
- Workstream 3 の docs 再編と矛盾しない配置方針が説明可能になっている。

# Harite Project Initial Build Reformation WS5 Feature Overview

最終更新: 2026-05-18

## 位置づけ

- 本書は [docs/reformation/harite-project-initial-build-reformation.md](docs/reformation/harite-project-initial-build-reformation.md) の Workstream 5 を具体化する子文書である。
- 主題は、`1.0.0` 後の新運用で扱う後続機能の棚卸しと overview の作成である。
- 本書は `1.0.0` gate ではなく、その後に開く backlog / planning 入口として扱う。

## この stream で固定すること

- 断片的なアイデアを inventory 化する。
- 実装候補、構想保持、破棄候補を粗く切り分ける。
- post-1.0.0 の入口文書として、次期 planning の土台を作る。

## 対象

- 外部壁紙サイト連携
- watch / sources / plugins の将来拡張案
- GUI / CLI の新導線案
- 将来の product improvement 候補

## 非対象

- `1.0.0` 前に実装を始めること
- release / packaging 整理
- docs 再編そのもの
- 仕様書正本の本文執筆

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

### 4. 用語と責務の再整理候補

- CLI watch の `log_level` は実態として stdout 出力粒度の切り替えであり、一般的な「ログ」機能として読むと誤解しやすい。
- GUI 側の message history と CLI 側の watch 出力を、同じ「ログ」で語らずに整理し直す余地がある。
- 将来的には名称、保存先、観測面の分離を WS5 候補として見直す。

### 5. watch の棚卸候補

- watch helper と CLI watch には `sequential` / `random` の選択モードがある。
- 一方で GUI watch は現状 `sequential` 固定で、対応する mode 選択 UI を持たない。
- `iterations` は現行 CLI watch と helper には存在するが、GUI と母体相当の操作面には対応概念がない。
- `iterations` は changer としての通常利用では直感的でなく、回数制限付きの実行確認やテスト補助寄りの性格が強い。
- 以上を踏まえ、watch mode と `iterations` は、GUI へ露出するか、CLI 専用概念として残すか、あるいは削除・整理するかを棚卸候補として扱う。

### 6. CLI `compute-placement` の棚卸候補

- `compute-placement` は command 名としては残っているが、現行 CLI では受理した値を表示するだけで、placement 計算機能を提供していない。
- core 層には `compute_placement(...)` 関数が存在する一方、CLI command はその実体へ接続されていない。
- 用途が不明瞭で常用 command surface として未成立であるため、WS5 では廃止候補として扱う。

### 7. CLI surface 全体の棚卸候補

- CLI には、command 名や option 名は存在するが、実際の効き方や役割が弱い項目がまだ残っている可能性がある。
- 直近で見えている代表例は、`compute-placement` の未接続、watch の `mode` / `iterations` の CLI 偏在、`log_level` の名称と実態のずれである。
- `optimize` 側でも `scaling` や `random-seed` は help 上で「効きが限定的」とされており、surface の強さに対して実体が弱い可能性がある。
- WS5 では CLI command / option を「主力として成立しているもの」「存在はするが未成立または効きが弱いもの」「削除または整理候補」に棚卸しする。

### 8. 設定ファイル名の棚卸候補

- 現行の設定ファイル名は `harite-preferences.json` で、foundation / core などの正本にもこの名称で記載されている。
- ただし媒体上のファイル名としては `preferences` が残っており、`prefs` をやめた後の残滓として不一致感がある。
- `設定` / `設定ファイル` という現在の呼び方と揃えるなら、ファイル名も含めて命名を見直す余地がある。
- そのため `harite-preferences.json` は WS5 での命名棚卸候補として扱う。

### 9. `config` と `設定` の用語不一致候補

- GUI / foundation / core の正本では `設定` / `設定ファイル` を主語にしている一方、CLI help と CLI 実装では `config` が前面に出ている。
- 母体側では `config` で揃っていた認識に対して、現行文書群では `設定` と `config` が混在しており、呼び方の統一が崩れている。
- そのため WS5 では、媒体上の help / option 名 / module 名を含めて `config` を軸に揃えるのか、文書側に合わせて `設定` へ寄せるのかを棚卸対象とする。

## 初動タスク

1. 現在頭にある後続機能案を列挙する。
2. それぞれを「着手候補 / 構想保持 / 破棄候補」に粗く分類する。
3. 外部壁紙サイト連携のような大きめ構想を、単発案ではなく overview 項目として受ける。
4. post-1.0.0 planning の入口となる最小構造を定める。

## 完了条件

- 後続機能 inventory の枠組みが説明可能になっている。
- `1.0.0` gate の外に置く理由が説明可能になっている。
- 構想の受け皿として overview を置く理由が説明可能になっている。
- Workstream 1・3・4 と混線せずに次段へ送れる状態になっている。

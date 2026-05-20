# Harite Project Initial Build Reformation WS5 Internal Issues Overview

最終更新: 2026-05-20

## 位置づけ

- 本書は [docs/reformation/harite-project-initial-build-reformation.md](docs/reformation/harite-project-initial-build-reformation.md) の Workstream 5 を具体化する子文書である。
- 主題は、`1.0.0` 後に扱う現行機能まわりの内部 issue 解決と surface 整理の overview 作成である。
- 本書は `1.0.0` gate ではなく、その後に開く cleanup / rename / consistency planning の入口として扱う。

関連子文書:

- 用語ぶれ一覧: [docs/reformation/harite-project-initial-build-reformation-ws5-terminology-drift-inventory.md](docs/reformation/harite-project-initial-build-reformation-ws5-terminology-drift-inventory.md)

## この stream で固定すること

- 現行機能に残る内部 issue を inventory 化する。
- rename 候補、弱い surface、責務ずれ、用語不一致を粗く切り分ける。
- 丸く書かれている計算過程を、式と決定規則まで含めて記述し直す論点を固定する。
- 後続 cleanup planning の入口文書として、論点の土台を作る。
- WS4 の抽出・事実記載を受けて、直す / 直さないを扱う working の入口を作る。

## 対象

- watch / CLI / core / plugin の surface 不一致
- 実装・help・正本のずれ
- 命名、責務、観測面の再整理候補
- 計算過程と入力値利用規則の明文化不足
- 現行機能の未成立 command / option / helper

## 非対象

- `1.0.0` 前に実装を始めること
- release / packaging 整理
- docs 再編そのもの
- 新規 feature 構想の棚卸し

## 現時点の論点

### 1. 内部 issue の棚卸し方

- 断片的な違和感や不一致を、その場しのぎで直すのではなく一覧として集約する必要がある。
- ただし、いまは優先順位の精密化より inventory 化を優先する。
- 正本側の事実記載 working と、WS5 での直す / 直さない判断 working を混ぜないように、一覧化と意思決定を段階分離する必要がある。

### 2. 分類の粒度

- 現行のまま残す項目
- rename / cleanup 候補
- 削除または縮退候補

### 3. 次期 planning への渡し方

- overview から次の cleanup / rename planning へどう送るか。
- 単発メモを増やしすぎず、入口文書で受ける必要がある。

### 4. 計算過程の明文化候補

- 現行の正本では、特に core を中心に「xx と yy を計算し、zz に収まるかを判断する」「margin 内の表示領域へ解決する」のような丸い説明が残っている。
- しかし optimize / placement / auto-split / embed では、user が投入した `resolution`, `margins`, `align`, `valign`, `two_screen`, `l_display`, `r_display` などが最終的にどの式へ入るかを追える必要がある。
- そのため WS5 では、まず core 正本を最優先に、各入力値がどの中間値へ変換され、どの比較や判定に使われ、どの出力値へ落ちるかを式と決定規則で明文化する。
- その後、CLI / watch / plugin / GUI は、core の計算規則を前提にしつつ、自分たちの分冊で必要な追加計算や値解決だけを追記する。
- 特に `margins`、有効描画領域、fit / fill 系の scale 決定、two-screen 時の左右割当、auto-split 時の切り出し範囲、embed 位置解決は、文章要約だけでなく式または段階列として記述する候補に含める。
- この論点は、用語ぶれ棚卸しより先に着手する WS5 の先頭級課題として扱う。

### 5. 用語と責務の再整理候補

- CLI watch の `log_level` は実態として stdout 出力粒度の切り替えであり、一般的な「ログ」機能として読むと誤解しやすい。
- GUI 側の message history と CLI 側の watch 出力を、同じ「ログ」で語らずに整理し直す余地がある。
- 将来的には名称、保存先、観測面の分離を WS5 候補として見直す。

### 6. watch の棚卸候補

- watch helper と CLI watch には `sequential` / `random` の選択モードがある。
- 一方で GUI watch は現状 `sequential` 固定で、対応する mode 選択 UI を持たない。
- `iterations` は現行 CLI watch と helper には存在するが、GUI と母体相当の操作面には対応概念がない。
- `iterations` は changer としての通常利用では直感的でなく、回数制限付きの実行確認やテスト補助寄りの性格が強い。
- 現行の `watch` は filesystem event 監視ではなく、一定間隔で画像候補を巡回して次画像を選ぶ changer / rotation 的な継続実行である。
- そのため `watch` という名称自体が実態とずれており、WS5 では rename を含む大改編候補として棚卸対象にする。
- watch 関連の用語として `interval`, `周期`, `cycle`, `サイクル` が併存しており、特に watch 間隔と 1 回分処理の単位が文脈ごとに揺れている。
- 先ごろ user-facing では `周期` を立てたが、helper / CLI / summary では `cycle` が広く残っているため、WS5 では `サイクル` を正系とする可能性も含めて用語整理する。
- 以上を踏まえ、watch mode と `iterations` は、GUI へ露出するか、CLI 専用概念として残すか、あるいは削除・整理するかを棚卸候補として扱う。

### 7. CLI `compute-placement` の棚卸候補

- `compute-placement` は command 名としては残っているが、現行 CLI では受理した値を表示するだけで、placement 計算機能を提供していない。
- core 層には `compute_placement(...)` 関数が存在する一方、CLI command はその実体へ接続されていない。
- 用途が不明瞭で常用 command surface として未成立であるため、WS5 では廃止候補として扱う。

### 8. CLI surface 全体の棚卸候補

- CLI には、command 名や option 名は存在するが、実際の効き方や役割が弱い項目がまだ残っている可能性がある。
- 直近で見えている代表例は、`compute-placement` の未接続、watch の `mode` / `iterations` の CLI 偏在、`log_level` の名称と実態のずれである。
- `optimize` 側でも `scaling` や `random-seed` は help 上で「効きが限定的」とされており、surface の強さに対して実体が弱い可能性がある。
- core 側でも `PlacementResult.to_dict()` のように、実装には残っているが現行の主要 surface では使い所が弱く見える helper があるため、WS5 で整理候補として棚卸対象に含める。
- Linux plugin の apply fallback (`xfconf-query`, `gsettings`, `feh`) は履歴上の説明と現行 dry-run / 実適用の実装がずれて見えるため、WS5 で command surface と正本記述の両方を棚卸対象とする。
- WS5 では CLI command / option を「主力として成立しているもの」「存在はするが未成立または効きが弱いもの」「削除または整理候補」に棚卸しする。

### 9. 設定ファイル名の棚卸候補

- 現行の設定ファイル名は `harite-preferences.json` で、foundation / core などの正本にもこの名称で記載されている。
- ただし媒体上のファイル名としては `preferences` が残っており、`prefs` をやめた後の残滓として不一致感がある。
- `設定` / `設定ファイル` という現在の呼び方と揃えるなら、ファイル名も含めて命名を見直す余地がある。
- そのため `harite-preferences.json` は WS5 での命名棚卸候補として扱う。

### 10. `config` と `設定` の用語不一致候補

- GUI / foundation / core の正本では `設定` / `設定ファイル` を主語にしている一方、CLI help と CLI 実装では `config` が前面に出ている。
- 母体側では `config` で揃っていた認識に対して、現行文書群では `設定` と `config` が混在しており、呼び方の統一が崩れている。
- そのため WS5 では、媒体上の help / option 名 / module 名を含めて `config` を軸に揃えるのか、文書側に合わせて `設定` へ寄せるのかを棚卸対象とする。

## 初動タスク

1. 現時点で見えている内部 issue を列挙する。
2. それぞれを「残す / rename・cleanup / 削除候補」に粗く分類する。
3. core を起点に、計算過程の丸い説明を式と決定規則へ落とし直す対象を洗い出す。
4. 実装・help・正本のずれを、後続 planning に送れる論点として固定する。
5. post-`1.0.0` cleanup の入口となる最小構造を定める。

## 完了条件

- internal issue inventory の枠組みが説明可能になっている。
- `1.0.0` gate の外に置く理由が説明可能になっている。
- cleanup / rename の受け皿として overview を置く理由が説明可能になっている。
- Workstream 1・3・4・6 と混線せずに次段へ送れる状態になっている。

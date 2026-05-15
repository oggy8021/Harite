# GUI Phase10 Layout Restructure Contract

- 本書は、current GTK runtime GUI の layout をウィンドウ外周から内側へ向かって切り直すための合意メモである。
- 目的は、見た目の重心を末端 button の微調整ではなく親コンテナの責務で決めること、および空余白しか生まない冗長な Grid / Box / spacer を減らすことにある。
- 本書は、実機スクリーンショット往復の途中で揺れた解釈を固定し、以後の実装と確認の正本とする。

## 現在の前提

- 対象は Main / Watch / Margins の 3 tab である。
- tab 内再編の対象は command tabs の各ページ本体であり、window 最下段の footer message surface は対象外とする。
- Preview の将来可能性は本書では扱わない。現時点では layout 構造の責務整理に集中する。
- icon 方針自体は別途 Phase10 icon planning で扱っており、本書は icon library 選定文書ではない。

## 全体原則

1. Window から widget へ向かって、1 段ずつ責務を狭める。
2. 中央寄せしたいものは、中央寄せ専用の親コンテナを 1 回だけ置く。
3. 同じ目的の centering shell を二重三重に重ねない。
4. 空ラベル spacer で無理に幅を作るより、親コンテナの配置責務で幅を決める。
5. tab ごとに「どこで幅を使うか」と「どこで中央寄せするか」を先に固定する。

## 外側から内側への分解順

1. Window
2. Root 縦カラム
3. Header / Tabs / Footer
4. 各 Tab の実コンテンツ本体
5. Tab 内の主要ブロック
6. 各ブロック内の widget 群

この順番で責務を切る。見た目の違和感を見つけた場合も、末端 button の位置より先に 1 つ外側の親コンテナを確認する。

## Main Contract

### Main の構造

- Main は 3 層で考える。
  1. Main タブ本体の縦カラム
  2. 上段の compose 領域
  3. 下段の action 領域

- 上段 compose 領域は 3 カラムで扱う。
  1. 左 display ブロック
  2. 中央の状態ブロック
  3. 右 display ブロック

- 左 display ブロックと右 display ブロックは同型とする。
  1. 十字ボタン本体
  2. 短縮ファイル名表示
  3. clear ボタン

### Clear の配置契約

- `Clear-L/R` は十字の縦線上に置かない。
- `Clear-L/R` はブロックの外へ逃がしすぎない。
- `Clear-L` は左ブロック内の内側右寄せに置く。
- `Clear-R` は右ブロック内の内側右寄せに置く。

### action 領域の契約

- `Preview` / `Optimize` / `Apply` は compose 用 Grid の子にしない。
- 下段 action 領域は compose 領域と完全に分離した別段に置く。
- Main の重心判断は、十字ボタンと action 領域を別責務に分けたうえで行う。

## Watch Contract

### Watch の構造

- Watch は 3 段で扱う。
  1. 上段の source block（`Srcdir-L` / `Srcdir-R` と各 path）
  2. 中段 `Interval` と `Watch Start/Stop`
  3. 下段の状態ラベル群

- 下段の状態ラベル群は Watch tab 内の局所読取面であり、次の 2 点に絞る。
  1. current
  2. output

- Watch 下段に source summary や追加 summary を増やして肥大化させない。
- Srcdir path は下段 summary に集約せず、上段の各 source block でそれぞれの button 近傍に持つ。
- 配置方針は Main の左右画像 block における短縮ファイル名表示を踏襲し、button の近傍で読めるように置く。
- この移動は、下段を軽く保つことと、上段を button だけの痩せた帯にせず、それなりの占有を持つ source 面として成立させることを兼ねる。

- したがって Watch は「操作列だけの薄い tab」ではなく、「上段で source とその path を決め、中段で watch を操作し、下段で watch 局所状態を読む」面として扱う。

### 幅の使い方

- 上段は左右方向に 3 分割で扱う。
  - 左セルの中央に左 source block
  - 中央セルは余白
  - 右セルの中央に右 source block

- 各 source block は少なくとも次の 2 要素を縦に持つ。
  1. `Srcdir-L/R` button
  2. その side の path 表示

- path 表示は button の近傍に置き、Watch 下段へ追いやらない。
- その見せ方は Main の左右画像で使う短縮ファイル名表示と同系統にする。
- これにより source 情報を上段の幅責務へ戻し、下段を不必要に肥大化させず、かつ上段も button だけで痩せすぎたり、逆に空白だけで広がりすぎたりしない。

- したがって上段は「両端へ極端に押し出す」のではなく、「左ブロック / 中央余白 / 右ブロック」で自然に離す。

- 中段は中央寄せでよい。
  - `Interval`
  - 値
  - increment/decrement
  - `Watch Start`
  - `Watch Stop`

- したがって Watch は「上段は左ブロック / 中央余白 / 右ブロック」で自然に離す」「中段は中央に寄せる」の 2 ルールで扱う。

### 補足

- tab 見出しに Watch があるため、本文先頭の `Watch` ラベルは不要とする。
- Watch で意味不明な中央閉じ込めを生む専用カラムや centered page shell は避ける。

### Watch と footer の境界

- window 最下段の footer message surface は、本 contract の Watch tab 内再編では動かさない。
- footer 側の `status` / `watch summary` / `error` は global summary として残し、Watch tab 内へ吸い上げない。
- 逆に Watch tab 下段の状態ラベル群は local read surface であり、footer の役割を背負わせない。
- したがって今回の Watch 再編で守るべき境界は「tab 内 local state」と「window footer の global status / error」を混線させないことである。

## Margins Contract

### Margins の構造

- Margins は「大きい十字」を最優先で固定する。
  - 上に `Top`
  - 左に `Left`
  - 中央に本文
  - 右に `Right`
  - 下に `Bottom`

- `Left/Right` は `Top` と同列ではない。
- `Left/Right` は中央本文を挟んだ左右の縦アームである。

### 3x3 発想

- 実装発想としては 3x3 を使ってよい。
  - 上中に `Top`
  - 中左に `Left`
  - 中中に本文
  - 中右に `Right`
  - 下中に `Bottom`

- ただし、空マスを埋めるためだけの widget は増やさない。
- 余白は空セル量産より親コンテナの責務で作る。

### サイズ配分の契約

- `中中` は Margins tab の主面であり、本文が十分な面積を保てる大きさで残す。
- `Top` / `Left` / `Right` / `Bottom` は、ラベルと control 類を無理なく収められる大きさを確保する。
- したがって 3x3 は「5 点を置ければよい」ではなく、「中央本文を潰さず、周辺 4 面も破綻なく成立する」配分でなければならない。
- 中央本文が極端に痩せる、または周辺 4 面の label / spin / control が窮屈になる配分は不採用とする。

### 本文の契約

- 中央本文には次を積む。
  1. current state summary
  2. embed pattern
  3. settings/text notebook
  4. position
  5. notes

- `position` は横一列の説明行ではなく、`Left` 列と `Right` 列を並べ、その下に各 `Top` / `Bottom` を縦に積む形を基本とする。

### 余白の契約

- Margins では外側の無意味な左右余白を作らない。
- Margins は必要なら centered page shell を使わない。
- 「margin 設定なのに外側へさらに大きな margin がある」状態は不正とみなす。

## 削減対象

- 中央寄せのためだけの二重 shell
- 空ラベル spacer
- action 領域を compose grid にぶら下げる構造
- Watch の中央閉じ込め専用カラム
- Margins の外周余白だけを作る shell

## 実装順

1. Main を contract に合わせて切り直す
2. Margins を大きい十字へ固定する
3. Watch を「上段幅使用 / 中段中央」の 2 ルールへ戻す
4. 最後に debug layout で余計な箱が残っていないか確認する

## debug 方針

- layout 調整時は `HARITE_DEBUG_LAYOUT=1` により `Box` / `Grid` / `Notebook` の枠線を可視化して確認する。
- スクリーンショット往復で違和感が出た場合も、まず 1 つ外側の親コンテナ責務を見直す。

## 非対象

- preview の将来増設余地の設計
- icon set の採否や filled variant 判断
- settings dialog semantics
- docs / mock 側の icon comparison 更新
- footer の state row / notice row / error row の意味規約そのもの

## 終了条件

- Main で `Clear-L/R` が十字線上でも外周逃げでもない内側配置になる。
- Watch で上段が幅を使い、中段だけが中央にまとまる。
- Margins で `Top/Left/Right/Bottom` の大きい十字関係が見た目に復元される。
- debug overlay を見たとき、余白しか責務を持たない shell が明確に減っている。

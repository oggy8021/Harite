# Margin Tab Grid Re-layout Contract

最終更新: 2026-04-23

## 目的

- `Margins` tab を、縦積み設定フォームではなく、中央の margin text box を四辺の margin controls が囲む制作画面として再配置する。
- `Current state` と補助文は、主 controls の後ろに流すのではなく、置き場を先に持つ補助領域として扱う。
- 本 contract は `feature/margin-tab-grid-re-layout` の実装正本とする。

## 固定する visible layout

- tab 見出しは `Margins` のままとする。
- `Margins settings` 見出しは置かない。
- 中央に 5 行 textbox 風の `Margin text` 入力領域を置く。
- `Mode` は中央 textbox の直上に横並びで置く。
- `Top margin` は中央 textbox の上中央に置く。
- `Bottom margin` は中央 textbox の下中央に置く。
- `Left margin` は中央 textbox の左に置く。
- `Right margin` は中央 textbox の右に置く。
- `Current state` は中央 textbox の左上寄り補助領域に置く。
- `Margin area` は中央 textbox の直下に置く。
- 行数上限説明、priority rule、current behavior は `Margin area` の下に縦並びで置く。

## Grid contract

- `Margins` tab は outer grid を 3 列で持つ。
  - Owner) `Margins` を `Margins (for each display)` と改称する。
- 左列: `Current state` と左 margin control。
  - Owner) "左列: `Current state`" は意識に無かった レビュ視点としても不足していたため以下に正す。
    - `Current state` は、左列に設定しない。中列に置く、詳細は中列へのコメントを参照のこと 【対処済】
- 中列: top margin, mode, margin text box, bottom margin, margin area, notes。
  - Owner)
    - 上から 次の順序とする。top margin, `Main Window Current alignment:`, embed pattern, embed tab, bottom margin, margin area, notes。
    - `Current state` は `Main Window Current alignment:` に改称する 【対処済】
    - mode は `embed pattern:` に改称する 【対処済】
    - embed tab area を 新設し、以下の動作とする。 【対処済】
      - Setttings tab, Text tab 2つのタブを設置する 【対処済】
      - 旧 mode にて Settings を選択の場合は、Settings tab を有効化し、Settings tab を選択済み表示とすること。記入済みテキストのクリアは行わない。 【対処済】
      - 旧 mode にて Text only を選択の場合は、Text tab を有効化し、Text tab を選択済み表示とすること。 【対処済】
      - 旧 mode にて Both を選択の場合は、Settings tab, Text tab 双方を有効化し、Text tab を選択済み表示とすること。 【対処済】
    - Settings tab は Margin に合成する Settings の 文字列を表示する （書式は gui-phase8-backlog.md にて調整済） 【対処済】
    - Text tab は margin text を 移動 + 改称する 【対処済】
      - text area は 最大5行とする（変更なし） 【対処済】
      - 5行以上は、入力できないものとする。（Gtk-WARNINGが最下行以降 Enter を押すと発生するためケアすること） 【対処済】
      - embed patternとして、text または both の選択がない場合は入力欄を無効化すること。（≒テキスト入力を不可とすること） 【対処済】
      - text area は 白抜き背景色 としてテキスト入力欄と分かるようにすること。 【対処済】
    - margin area は margin position とし、表示ラベルは `Position:` とする。 【対処済】
      - area(= position) は、Top または Bottom マージンのみを対象とし、母体プログラム仕様では左右ディスプレイ均等に確保していた／確保できていたため、左, 右 × Top, Bottom 計 4か所を候補とした上で 1か所 をユーザが選択する。 【対処済】
      - margin の根本仕様 としては 上下左右が交差する コーナー部は top, bottom 側の計算領域とする。（Hariteにて新しく明示な可能性、母体プログラムと比較すること）
        - 本具体化により、margin 矩形は Apply予定サイズより精緻に計算できることとなると想定している。
        - Settings および Text 双方、最大文字列長となる 行 の長さ を 4分割した 最初の 1/4位置（第一四分位数）を書き出し位置とする（Settings や Text 側の合成原点・視点）
- 右列: 右 margin control。
- top margin / bottom margin は中列の中央基準で置く。
- left/right margin controls は textbox の縦中央付近に揃える。
- notes 群は textbox 下端から読み下せる順で固定する。

## Margins Tab Layout

- 2026/4/25 Owner追加
  "Using Overage Badget Until limits reset." の間にレイアウト説明を起こしておく。

+-------------------------------------------------------------------------------------------------------+
|                   |                        Top margin (px) [ 0]-+                 |                   |
|                   |                                                               |                   |
|                   |          Main Window Current alignment:　　　　　              |                   |
|                   |             align=center,center/center,center                 |                   |
|                   |                                                               |                   |
|                   |      embed pattern:                                           |                   |
|                   |             〇off ●Settings 〇Text only 〇Both                |                   |
|                   |                                                               |                   |
|                   |   [Setting][Text]-------------------------------------------+ |                   |
| Left margin (px)  |   |   +-------------------------------------------------+   | | Right margin (px) |
|      [ 0]-+       |   |   |                                                 |   | |      [ 0]-+       |
|                   |   |   |                                                 |   | |                   |
|                   |   |   |                                                 |   | |                   |
|                   |   |   |                                                 |   | |                   |
|                   |   |   |                                                 |   | |                   |
|                   |   |   +-------------------------------------------------+   | |                   |
|                   |   +---------------------------------------------------------+ |                   |
|                   |                   Bottom margin (px) [ 0]-+                   |                   |
|                   |      Position:                                                |                   |
|                   |                 Left:    〇Top 〇Bottom                       |                   |
|                   |                 Right:   〇Top ●Bottom                        |                   |
|                   |                                                               |                   |
|                   | assist                                                        |                   |
+-------------------------------------------------------------------------------------------------------+

## Controls mapping

- 既存 object name は維持する。
- `spnTopMergin`, `spnLMergin`, `spnRMergin`, `spnBtmMergin` は継続使用する。
- `txtMarginText` / `entEmbedText` は同一 widget alias を維持する。
- `lblCurrentMargins`, `lblCurrentStateL`, `lblCurrentStateR` は `Current state` 領域に置く。
- `lblPriorityRule`, `lblStyleLegend` は notes 群に置く。

## 明示的な除外

- `Margins` の意味論を global から display-local へ変えることは、この branch では扱わない。
- `Main` / `Watch` tab の情報設計変更は、この branch では扱わない。
- `Mode` wording や `Settings` wording の再議論は、この branch では扱わない。

## 受け入れ基準

- XFCE 実機で、中央 textbox を四辺の margin controls が囲んで見える。
- `Current state` が margin text box の上側補助領域として読める。
- `Mode`, `Margin text`, `Margin area` の順が視覚的に追える。
- `Margins settings` 見出しが消えている。
- object map と既存 signal wiring は壊さない。

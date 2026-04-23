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
- 左列: `Current state` と左 margin control。
- 中列: top margin, mode, margin text box, bottom margin, margin area, notes。
- 右列: 右 margin control。
- top margin / bottom margin は中列の中央基準で置く。
- left/right margin controls は textbox の縦中央付近に揃える。
- notes 群は textbox 下端から読み下せる順で固定する。

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

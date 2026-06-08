# GUI Phase10 Icon HTML Mock Memo

最終更新: 2026-06-09（用語: Watch → Slideshow。K-01 は [H-08](../20260608-1200-feature-pending.md#h-08) 破棄）
対象: Phase10 Main Window / Slideshow icon mock（当時の design ラベルは Watch）


## 位置づけ（移動後）

- 本ディレクトリ docs/working/design/ は GUI 合意形成用の HTML mock / slice を置く。
- 本 mock は **icon 合意専用**。ウィンドウ全体のレイアウト正本ではない（widget slice は別ファイルで追加）。
- 正本の振る舞いは [harite-gui-spec.md](../../specs/gui/harite-gui-spec.md)。

## 目的

- Phase10 4th planning で決めた Main Window / Slideshow icon 導入候補を、実装前に低コストで見比べる。
- XFCE 実機確認の前段として、Main Window と Slideshow 面の tone、密度、意味差の見え方を早めに掴む。
- Lucide を 1st try としつつ、direction toggle では arrow-normal と arrow-big の 2 派生も見比べる。必要なら Feather 差し替えも同じ面で比較し、差し替え容易性を確認する。

現時点メモ:

- owner 判断では Lucide と Feather の差は大きくなく、icon set 自体は Lucide で進めてよい。
- mock 上の主残論点は、Lucide direction toggle を arrow-normal にするか arrow-big にするかである。
- `icon only` の是非は GTK 実機へ載せないと決め切れないため、feature 試行の初手は `icon + label` を基準にする。
- SVG の filled variant は現時点では作らず、元 asset を GTK へ載せた時の印象を先に見る。

## 位置づけ（Phase10 当時）

- 本メモは Phase10 4th planning の「Main Window icon 適用前の軽量 HTML mock」を具体化するための薄いテンプレである（当時の planning 文書は `_initial-build-history` 参照）。
- 実ファイルは [gui-phase10-icon-mock.html](gui-phase10-icon-mock.html) とし、Main Window 面と Slideshow 面を 2 セクションで持つ。
- 本メモで見るのは実装完成度ではなく、Main Window / Slideshow 面の当たり、icon set 全体の tone、文字併記の要否である。
- ただし Slideshow 面は Main Window より情報量が少なく、縦横比も異なるため、Main Window と同列の重み比較には使わない。
- 正本判定は XFCE 実機に置き、本メモはその前に通す低コストな正式通過点として扱う。

## 対象面

- Main Window 側では、Color、Settings、About、direction toggle 8 件、open / clear 4 件、Save As、Optimize、Apply をまとめて並べる。
- Slideshow 側では、Slideshow Start と Slideshow Stop を pair で並べる。
- Slideshow 側では、Srcdir-L / Srcdir-R も含め、左右戦略が見える形で並べる。
- margin tab は、今回の icon 導入論点では操作 icon が少なく、mock の主対象から外す。

## mock の作り方

- HTML mock は 1 枚とし、Main Window mock と Slideshow mock を縦積みで置き、横幅は揃える。
- 見た目は単なる icon 一覧ではなく、実ウィンドウの印象に寄せた雑な外形を持たせてよい。
- fixed window size の雰囲気を崩さないよう、横幅と主要 row の密度だけは大きく外さない。
- table タグや CSS で row / grid を雑に再現してよく、実装の素直さを優先する。
- mock では段階適用の順番は持ち込まず、今回見たい Main Window / Slideshow の icon 候補を最初から全部並べる。
- icon 単独案と icon + 短い文字列案を切り替えられる形が望ましい。
- ただし HTML mock 上の icon-only は比較補助に留め、feature への初回投入形は icon + label を基準とする。
- Lucide 版を正本候補とし、必要なら同じ DOM 構造で Feather 版に差し替える。
- HTML mock では仮 SVG を描かず、local に保持した Lucide / Feather の実 SVG asset を直接参照する。
- mock 用のローカル作業では、各 icon set の配布 pack や zip を一時的に持ってきて比較してよい。
- 理由は、差し替えや隣接候補の試行のたびに都度フェッチさせず、low-cost に見比べを回すためである。
- ただし mock 段階の取得方法と、repo / 配布物に何を残すかは分けて考え、製品側は必要 SVG だけを選んで持つ前提を崩さない。
- 実装を楽にするため、button の state 遷移や実際の click handler は持たせなくてよい。

## mock で見たい点

1. direction toggle 群が十字配置として一目で読めるか。
2. open / clear が path 補助操作として自然に分離して見えるか。
3. Save As / Optimize / Apply が Main Window 上で過不足ない重みで並ぶか。
4. Slideshow Start / Slideshow Stop が pair として自然に読めるか。
5. Color / Settings / About の header command 群が icon 化されても騒がしすぎないか。
6. Srcdir-L / Srcdir-R を含む Slideshow 面の左右戦略が読めるか。
7. icon 単独で足りるか、短い文字併記を残した方がよいか。最終判定は GTK 実機で行う。
8. Lucide の arrow-normal と arrow-big で、direction cross の読みがどこまで変わるか。
9. Lucide と Feather で、tone の差が実際に乗り換えたいほど出るか。
10. icon set を差し替えるときに、DOM / class / asset path の差し替えコストが重すぎないか。

補足:

- Slideshow 面は、Main Window と重みを見比べるためではなく、pair readability と左右戦略の見え方だけを見る補助面とする。
- 特に Srcdir-L / Srcdir-R は現実装寄せで左右に振り、Start / Stop 周辺の空き方が見えるようにする。

## 固定の仮決め

- direction 系は Lucide の arrow-up / arrow-down / arrow-left / arrow-right を基準案に置く。
- direction 系は Lucide の arrow-big-up / arrow-big-down / arrow-big-left / arrow-big-right も派生案として試す。
- open / clear は folder-open / folder-x を初手に置く。
- Save As は save、Optimize は image、Apply は wallpaper を初手に置く。
- Feather 比較では Apply に完全同名 icon がないため、display 系の近似として monitor を当てる。
- watch 系は play / pause の pair を初手に置く。
- Color は swatch-book、Settings は settings、About は info を初手に置く。
- Srcdir-L / Srcdir-R は folder-open 系を共通に置き、左右戦略は文字で補う。
- margin tab は今回の mock 対象から外す。

## mock 変数テンプレ

- mock 種別: Lucide-arrow-normal / Lucide-arrow-big / Feather / mixed
- mock 面数: 1 枚 / 2 枚
- 文字併記: なし / 短縮文字列あり
- feature 初手: 短縮文字列あり
- 対象面: Main Window のみ / Main Window + Slideshow
- window 幅メモ: [value]
- icon size: [value]
- stroke width: [value]
- gap / padding: [value]

## 評価テンプレ

- mock 名: [name]
- 評価日: [YYYY-MM-DD]
- 評価者: owner
- 比較対象: Lucide-arrow-normal / Lucide-arrow-big / Feather / all

### 判定結果

- direction readability: pass/warn/fail
- open-clear separation: pass/warn/fail
- Save As / Optimize / Apply weight: pass/warn/fail
- watch pair readability: pass/warn/fail
- header command tone: pass/warn/fail
- watch left-right readability: pass/warn/fail
- direction variant readability: pass/warn/fail
- icon-only viability: pass/warn/fail
- feature-first icon+label viability: pass/warn/fail
- swap ease Lucide <-> Feather: pass/warn/fail
- overall: pass/warn/fail

### Notes

- Main Window:
- Slideshow:
- tone:
- 文字併記:
- 差し替えコスト:

## 最小着手テンプレ

1. Main Window 面に Color / Settings / About、direction / open / clear / Save As / Optimize / Apply をまとめて置く。
2. Slideshow 面は同一 HTML の下段 section として置き、Main Window と横幅を揃える。
3. Main Window 面は実ウィンドウっぽい外形を薄く持たせる。
4. Slideshow 面では Srcdir-L / Srcdir-R と Slideshow Start / Stop の左右感を一緒に置く。
5. Lucide arrow-normal 版で icon + label を見る。
6. 同じ面で Lucide arrow-big 版も見る。
7. 比較補助として必要なら icon-only も見る。
8. 必要なら Feather 差し替え版を作る。

## 完了条件

- Main Window / Slideshow icon 面の当たりを HTML mock で一度確認している。
- Lucide の arrow-normal / arrow-big の first impression 差が記録されている。
- feature 試行の初手を icon + label とする判断が記録されている。
- 必要なら Feather 差し替え比較も同じ枠組みで試せる見通しが立っている。
- XFCE 実機確認へ進めるか、mock の段階でもう一度絞るかを判断できる。
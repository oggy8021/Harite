# GUI Phase 8 Precedence Audit Memo

最終更新: 2026-04-23

## 目的

- P8-2A と P8-2B の間で、`設定値の強さ`、`計算過程`、`どの値がどの段階で優先されるか` を再監査するための短いメモである。
- 特に `margins` / `two_screen` / `align` / `valign` / `fixed` / `apply_mode` の意味論が、GUI wording と実際の optimize/apply 計算でズレていないかを確認する。

## 今回の発見

- `margins` は現状 `global outer margins` として効いており、display ごとの margin ではない。
- `two_screen explicit` と `Auto-Split` は同義ではない。
  - `two_screen explicit`: optimize 時の配置前提
  - `Auto-Split`: apply 時の分割適用
- preview は今回、見え方の誤魔化しではなく、optimize/apply 結果の破綻を正直に先出しした。

## 母体の特徴

- 原理、原則としては、まずこの母体の拘束順と幾何モデルを再現基準として扱う。
- Harite 側で新しく導入した機能や user-facing 入口の都合により、そのまま再現できない箇所だけを個別に調整対象とする。
- 母体は `ImgSize` / `WorkSpace` / `Rectangle` / `Screen` 系の構造で、位置決めをかなり強く拘束していた。
- 母体側の `mergin` 表記は概念差ではなく、単純なスペルミスとして扱う。
- そのため、値の優先順は GUI wording よりも、screen 単位の幾何制約で強く守られていた。
- 母体の optimize は概ね次の順で拘束される。
  1. `fixed` または画像種別で left/right screen へ binding
  2. screen ごとの margin 制約
  3. 収まらない場合の downsize
  4. その screen の中で `align` / `valign`
  5. 最後に左右 screen を workspace 上で合成

## Harite 現状の特徴

- Harite は現時点で、母体ほど screen 単位の拘束構造を持っていない。
- 現行 core は概ね次の順で計算している。
  1. canvas 全体の `margins`
  2. `two_screen` 時の display split
  3. split 後の usable area
  4. その area の中で `align` / `valign`
  5. embed は最後に margin 帯へ追記
- このため、母体よりも `global outer margins` の強さが前面に出やすい。

### 現行 optimize 実装の確認結果

- `margins` は optimize 冒頭で `inner_w` / `inner_h` を作る形で先に効いている。
- `two_screen` は `l_display` / `r_display` がある場合に explicit split として扱われ、left/right の cell 幅を後段で作る。
- `align` / `valign` は pair semantics を持つが、実際には split 後の各 cell 内 offset として適用される。
- `fixed` は現行 optimize 実装では値を読んでいるが、配置拘束には使われていない。
- したがって現行 Harite は、母体のような「先に screen へ binding してから収まり判定と寄せを行う」流れではなく、「先に canvas margins を切ってから cell に流し込む」流れになっている。

## 優先して疑うべき箇所

### 1. `two_screen` と `resolution` / `l_display` / `r_display`

- 自動検出値と user 指定値のどちらが勝つかを再確認する。
- 2 入力化や prefs load 後に auto context が強く入りすぎていないかを見る。

### 2. `fixed`

- 母体では左右 binding の強い起点だった。
- Harite では効きが弱く、`two_screen explicit` 時の入力順と差が薄い可能性がある。

### 3. `margins` と `align` / `valign`

- 値の保持自体ではなく、`どの領域の中で center/right/bottom するのか` を監査する。
- 現状は global outer margins の影響が強い。

### 4. `apply_mode` と `two_screen`

- user からは 1 本の two-screen workflow に見えやすいが、内部では別レイヤーである。
- GUI wording と内部責務が混線していないかを見る。

### 現行 apply 実装の確認結果

- 原則として、optimize 側の幾何と拘束順が正しければ、apply はどの mode でもそれ自体が意味論の主因にはならない前提で扱う。
- `apply_mode=single-file` は optimize 済みの 1 ファイルをそのまま apply target に渡す。
- `apply_mode=per-monitor-explicit` は left/right の指定ファイルを display 名へ対応付けるだけで、optimize 結果の再計算は行わない。
- `apply_mode=per-monitor-auto-split` は optimize 済み composite を display offsets と width に基づいて横方向に crop し、各 display 解像度へ fit し直して渡す。
- ここで使われるのは detect 済み display 配置と composite 画像であり、optimize 時の `align` / `valign` / `fixed` / `margins` を apply 側で再解釈して配置し直してはいない。
- したがって `Auto-Split` は「optimize の代替」ではなく、「optimize 後に composite を display ごとへ分配する apply 責務」である。
- 監査上は、まず optimize 側の拘束順を正し、apply 側はその結果をどこまで保存し、どこで単純分配しているかを確認する順で扱う。

### 5. prefs load/apply 後の正規化

- 保存値と GUI 有効値がズレる箇所を把握する。
- 例: `embed_position=auto` を GUI では `bottom` 扱いにする正規化。

### 6. watch の dual-source / auto-split

- watch は optimize/apply よりさらに別の前提で動く。
- 主導線外だが、将来本実装を進める前に precedence audit が必要。

## 現時点の判断

- `margins` の意味論は P8-2A の範囲で直し切るには広すぎる。
- embed wording と max-lines 強化は、この precedence audit を前提に進めないと再び意味論がずれる。
- P8-2A と P8-2B の間で、上記 6 項目のうち少なくとも 1 から 4 を先に確認する。
- `harite optimize` の `--input` は拘束を強め、directory は受け入れず、画像ファイルのみを受け付ける方針で固定する。

## 監査の進め方

### Step 1. optimize 側の拘束順を固定する

- まず `two_screen` / `fixed` / `margins` / `align` / `valign` が optimize でどの順に効くかを文章で固定する。
- ここでは GUI wording ではなく、実計算での拘束順を優先して書く。
- 特に次を曖昧なままにしない。
  - 画像は最初に screen へ binding されるのか
  - 先に canvas 全体の usable area を切るのか
  - `center` は display 基準か、margin を引いた後の area 基準か

### Step 2. apply 側の責務境界を切り分ける

- `apply_mode` が optimize 結果に対して何を再解釈し、何を再計算しないかを分けて書く。
- `Auto-Split` は optimize の代替概念ではなく、apply の出力分割責務であることを固定する。

### Step 3. GUI wording と内部意味論の対応を点検する

- visible wording ごとに、内部で何を指しているかを 1 対 1 で確認する。
- 少なくとも次は個別に確認する。
  - `Auto-Split`
  - `No Split`
  - `Top/Bottom/Left/Right margin`
  - `Params`
  - `fixed`

### Step 4. prefs 正規化を別枠で確認する

- 保存値、GUI 表示値、実行時有効値がずれる箇所を列挙する。
- GUI で user に見せる値と、内部で保持する canonical value が一致しない箇所は、P8-2B 前に明文化する。

## 監査の出口条件

- 次の 4 点が文章で固定できたら、P8-2B へ進んでよい。
  1. optimize 側で各値が効く順番
  2. apply 側で再解釈する範囲としない範囲
  3. GUI wording と内部意味論の対応表
  4. prefs 正規化で意味がずれる箇所の一覧
- 上記が曖昧なままなら、P8-2B の wording 強化や max-lines 再設計には入らない。

## GUI wording 対応表 初版

### `Auto-Split`

- GUI 表示語は Apply の radio `Auto-Split` である。
- 内部値は `apply_mode=per-monitor-auto-split` である。
- 意味論としては、optimize 済み composite を display ごとへ自動分配する apply 責務を指す。
- したがって `two_screen` や optimize 側の 2 入力配置そのものを意味してはいない。
- 現時点の wording は概ね責務と一致している。

### `No Split`

- GUI 表示語は Apply の radio `No Split` である。
- 内部値は `apply_mode=single-file` である。
- 意味論としては、optimize 済み 1 ファイルを追加分割せずそのまま apply する経路を指す。
- `Auto-Split` の対義語としては成立しており、apply 側の追加処理がないことを表す。
- 現時点の wording は概ね責務と一致している。

### `Params`

- GUI 表示語は Embed の radio `Params` である。
- 内部値は `embed_info=params` である。
- 現行 core では `Params` 選択時に、合成画像上へ `res=... margins=...`、`align=.../.. pad=... inputs=...`、必要なら `two_screen=1 ...` を行単位で埋め込む。
- つまり `Params` は「こちらの設定組み合わせを画像へ埋め込む」機能を指している。
- ただし user-facing wording としてはまだ弱く、少なくとも現行実装とのズレが残る。
- `embed info` という語自体が、現時点では何の info かを示せていない
- `Params` も同様に意味が弱く、正確には `Optimize Settings` に近い
- 当初 `info` に将来のリソース使用率などを含める余地があった可能性はあるが、少なくとも current scope ではその種の runtime 情報を合成しない
- 合成画像上では `Params` という見出し自体は出していない
- docs 方針では `pad` / `inputs` / flag 的な `two_screen=1` 露出は避けたい
- したがって `Params` は内部値との対応は取れているが、表示内容の最終意味論は未確定である

### `fixed`

- 母体では `fixed` は単なる補助フラグではなく、`Img1 -> left`、`Img2 -> right` を先に binding する起点だった。
- その後に contain 判定、縮小、寄せ、merge が続くため、母体ではかなり強い値だった。
- Harite 現行では内部値は `fixed: bool` として残っており、GUI にも `入替不可` / `入替可`、Prefs にも `Fixed` が残っている。
- ただし current optimize 実装では `fixed` は読まれているだけで、配置拘束には使われていない。
- ここで GUI については、既存 docs に「Open-L / Open-R で自明配置するため、GUI 版は fixed 指定であると解釈するのが自然」とする整理が残っている。
- したがって GUI 主導線では、`fixed` を user-facing control として見せるより、見えない内部既定動作として吸収する整理が母体追従に近い。
- 最終決定として、CLI/core では `fixed` / `no-fixed` を廃止し、2画面時の左右順は `input=` に投入した順序に従う。
- GUI では `fixed` は独立 control として使わず、Open-L / Open-R の自明配置に吸収されているものとして扱う。
- したがって `fixed` は「GUI では使っていない」「CLI/core では廃止」の整理で閉じる。
- 古い config 互換は持たず、prefs -> json を含めて `fixed` / `no-fixed` の残骸は刈り取る前提で進める。
- 実装時は CLI、core、preferences/json、GUI widget/signal、tests、docs の順に残骸を掃除する。

### `Top/Bottom/Left/Right margin`

- GUI 表示語は Embed の position radio `Top margin` / `Bottom margin` / `Left margin` / `Right margin` である。
- 内部値は `embed_position=top|bottom|left|right` である。
- current draw 実装では、実際に次の margin 帯だけを描画対象にしている。
  - `top`: 左右 margin を引いた上帯
  - `bottom`: 左右 margin を引いた下帯
  - `left`: 上下 margin を引いた左帯
  - `right`: 上下 margin を引いた右帯
- preflight も同じ寸法で判定しており、画像本体への重畳や display 単位の別解釈はしていない。
- したがってこの 4 語は、`Left display` / `Right display` のような画面単位の意味ではなく、あくまで canvas 上の margin 帯を指している。
- 選んだ margin 帯の中での文字配置は、さらに `align` / `valign` されるのではなく、その帯の左上寄せで描かれる。
- GUI では `auto` を外しているが、core の legacy 実装にはなお `auto` が残っており、最大 margin 量の辺を選ぶ。
- したがってこの 4 語は、現行の内部意味論と実描画範囲に対しては概ね正確である。
- `Position` という見出し自体はやや抽象的だが、少なくとも radio 候補は current implementation を正直に表している。

### `Margins` / `Margin text` への再設計方針

- 次段では `Embed` という名称はやめ、tab 全体を `Margins` として再設計する。
- tab 内は少なくとも `Margins` と `Margin text` の 2 段に分ける。
- Main 側に散っている margin 数値 4 項目は `Margins` tab へ移し、margin 関連を一箇所で扱う。
- margin 値は 4 つ 1 組で入力させ、左右に同じ margin として扱う。
- ただしこれは current 実装の `global outer margins` を理想として肯定する意味ではなく、margin まわりの責務を分散させないための UI 再配置として採る。
- `embed info` という語もやめ、CLI/GUI ともに `Margin text` 系の名称へ寄せる。
- `Text` 入力は 1 行 entry ではなく 5 行の multiline textbox 風 control へ広げる。
- `max lines` は user-facing control としては廃止する。
- 行数上限は mode ごとの内部ルールで扱う。
  - `Params` 相当: 自然に決まる行数
  - `Text` 相当: 最大 5 行
  - `Both` 相当: 最大 8 行
- 将来的には margin text の出力先 display を左右どちらかへ限定指定する余地を残す。

### `pad` keyword の点検結果

- `pad` は user-facing GUI 語彙としては不要であり、現行では `embed_info=params` の表示からも除去した。
- `padding` の主経路だった CLI / state model / optimize 実装 surface は phase8 で撤去した。
- なお、母体の `--mergin` は `padding` と対になる別概念ではなく、単なるスペルミスのまま残っている margin オプションである。
- 背景として、Harite には input に directory を許し、その中の画像を無理やり展開して tile する経路が入っている。
- `padding` は主にその通常分割経路の cell 間隔として使われていたが、母体由来の幾何制約ではなかった。
- この directory 展開と tile 前提の optimize は見栄えが悪く、母体を無視した Harite 固有機能の典型とみなす。
- したがって `--padding` は CLI から撤去した。
- `layout=mosaic` も同じ文脈の Harite 固有都合とみなし、optimize の user-facing surface から撤去した。

### `--input` の拘束強化

- `harite optimize` の `--input` は、画像ファイルのみを受け付ける実装へ更新した。
- directory 指定を受けて中身を展開する旧実装は、母体を無視した Harite 固有 convenience とみなし廃止した。
- 2画面時の左右順は、directory 展開後の順ではなく、`input=` に投入した画像ファイルの順に従う。
- この決定は optimize CLI とその周辺 state / docs に対するものであり、watch の input directory 要件とは切り分けて扱う。

### `Compose` の扱い

- `Compose` は内部意味としては理解できるが、display-facing wording としては採らない。
- 既存 docs でも `Compose / Input` のような中間ラベルは主画面へ残さない方針で揃っている。
- したがって今後の visible wording では、内部責務名としての `compose` と、user が触る表示語は分けて扱う。

## 監査の成果物

- 最低限、次のどちらかを残す。
  1. 本メモへの追記として、各論点の確定結果を書く
  2. 論点が大きい場合は、optimize/apply/GUI wording を分けた個別メモを起こす
- 実装に入る前に、「どの値が勝つか」を user-facing wording ではなく内部拘束順で説明できる状態を作る。

## 次の使い方

- P8-2B 着手前に、本メモを見ながら「どの値がどの段階で勝つか」を 1 項目ずつ確認する。
- 新しい visible wording を入れる前に、その wording が指す実計算対象が本当に一致しているかを確認する。

# Harite Project Initial Build Reformation WS6 CLI INTERNAL ISSUES

最終更新: 2026-05-21

## 位置づけ

- intial-build-reformation 下 ws1 ～ ws5 の中間棚卸を行う。
- CLI 関連について、実機確認ができていなかったため、実施してみたところ多くの疑問点・問題を検出したため、これを共有しこれも reformation の中で fix していくものとする。
- 旧ws6 については、飛び番で ws10 に先送りした。

## 作業方針

 直前までの SDD/TDD 踏襲の理想的改修 手順の一段前に、正本に対して発生の疑問点・問題を照らし合わせ、これの原因解析ができるかを点検する。正本で解決できない場合は、その記述拡充を以下の `正本変更` に課すとともに、ソース解析によって原因解析を行う。原因解析結果は、Ownerに知らせるまでを作業入口として、以降は本手順を崩さずに実施し、改修達成する。

1. 正本変更
2. commit/push
3. テストコードを用意
4. commit/push
5. 本体実装
6. commit/push
7. 3層比較 + 必要に応じてテスト強化、正本記述強化
8. commit/push
9. merge

## CLIにおける 内部 issue

- Web UI にて、 issue 番号をとったのは先頭のものだけであり、以降は取得していない。便宜上、A. B. ・・と単純命名しておく。

## 正本照合による束ね直し

### 1. 正本で現行挙動まで概ね説明できる論点

- D. margin なしの `embed-info=params` がエラーにならず、そのまま実行される件
  現行 core 正本では、embed 描画領域が小さすぎる場合は「何も描かない」規則であり、optimize 自体を失敗させる規則にはなっていない。したがって「設定は受理されるが表示は出ない」は正本で説明できる。(harite-core-spec.md:129)
- F. margin あり時の `align`, `valign` の効き方
  現行 core 正本では、まず margin を差し引いた inner/cell を作り、その残り空間に対して `align` / `valign` を適用する計算規則まで定義している。見た目の変化が小さい場合があることも含め、現行挙動は正本で追える。(harite-core-spec.md:108-110)
- G. margin を外したときに `align`, `valign` の差が見えやすくなる件
  これも F と同じく、cell 計算と余白量の差で説明できる。margin がないほうが画像の可動域が増えるため、差が見えやすくなる現行規則になっている。

### 2. 正本で一部は説明できるが、原因説明や利用者理解には補助記述が不足している論点

- A. dry-run slideshow で cycle ごとのメッセージが出ない件
  現行 CLI 正本では、dry-run 時に `Slideshow cycle=...` を出さない方針までは説明できる。一方で、`iterations` 廃止後は `Slideshow completed` が通常運用で発生しえず、停止も `Ctrl+C` 前提になっているため、現行正本の `Slideshow start` / `Slideshow completed` 中心という書き方は stale である。加えて Owner 見解として slideshow dry-run 自体を廃止したい意向が明示され、さらに CLI / GUI を通じて dry-run / do-it の使い方自体を見直し、作用をよりストレート・直接的に表す方向が示されたため、A は現行正本で完結説明できた論点ではなく、正本更新候補を含む論点として扱う。
- E. `embed-position=top` で左ディスプレイ上側に params が出る件
  現行 core 正本には、two-screen かつ display 情報ありの場合、`top` と `left` は左 display slice、`right` と `bottom` は右 display slice に割り当てる旧規則が残っているため、現象自体は読み取れる。ただし Owner 見解では、GUI 相談時に margin 領域矩形の切り方と `left-top/bottom`, `right-top/bottom` のいずれかにのみ置くルールを既に決めており、それを core 側へ反映し損ねた理解である。したがって E は「現行正本どおり」で済ませる論点ではなく、GUI と core の処理を揃える前提の正本更新候補として扱う。
- H. `--background-color #E0E0E0` が受け付けられず、`E0E0E0` だと通る件
  現行の受付基準としては、`#` を除いた HEX 入力を受け付ける扱いで問題ない。論点は値規則の不整合ではなく、help や案内メッセージが `#1E1E1E` 形式を前面に出しているため、利用者に `#` 付き入力が正規だと誤解させている点にある。したがって H は help 表示の見直しを主対象とする論点として扱う。
- I. `--settings-file` の help / 使い方が分かりにくい件
  現行 CLI 正本では、`--settings-file` は optimize で JSON 設定ファイルを読み、CLI 引数で上書きする規則を定めている。また `-c` 単独での失敗は「path 引数必須」で説明でき、I の 2 つ目の実行は Owner の実行方法誤りとして整理できる。残る論点は help 文言で、オプション自体は任意だが指定時は path 必須であり、optimize 用 defaults を読む機能だと一読で分かる書き方が不足している。Owner 方針としては、help は「2. Optional path to optimize settings JSON」の方向で見直す。
- J. `scaling=fit|fill|crop` で差異が出ない件
  現行 core 正本と実装から、内部計算自体は fit 相当の `_scale_to_fit(...)` として意味を持っている一方、`scaling` を user-facing option として露出する意味は薄く、`fill` / `crop` は実体を持たないまま残っている。Owner 方針としては、まず `scaling` のユーザ露出をやめ、`fill` / `crop` を廃止する。そのため J は「現象説明済み」で閉じる論点ではなく、public surface の整理を伴う正本更新候補として扱う。

### 3. 正本だけでは原因説明を閉じられず、source 解析と正本補強が要る論点

- #307. slideshow の `--input dir1,dir2` が existing directory error になる件
  現行 CLI 正本は slideshow 入力を「existing directory」としては定めているが、comma 区切りで複数 directory を受け付ける/受け付けないの正本が固まっていない。加えて、この論点は母体側と GUI 側にも揃っておらず、`Srcdir-L`, `Srcdir-R` 相当を CLI でどう表すかも未記述である。そのため正本だけでは原因説明を閉じられず、改修対象として扱う。
- B. optimize の `--input file1,file2` が 2 枚入力として扱われない件
  現行 CLI 側の help / 案内では、optimize の `--input` は「カンマ区切りまたは `--input` の繰り返しで複数パスを指定できる」と読める一方、実機観測では comma 区切り 1 トークンが 2 枚入力として扱われていない。したがってこの論点は public rule の弱さだけでなく、help と実挙動の矛盾を含んでおり、改修対象として扱う。
- C. 単純 apply で file path を解決できず失敗する件
  現行 plugin 正本には、Linux single-file apply/dry-run は `Path(...).expanduser().resolve()` 後の存在確認で成否を決めるとある。したがって「存在しないと失敗する」 gate 自体は説明できるが、B の試験で直前に成功した出力ファイルを削除していないにもかかわらず C で not found になっている以上、単なる利用者操作ではなく実装側の不整合を疑うべき段階である。よって C は source 解析と再現時の入出力点検を要する改修対象として扱う。

### CLI版スライドショーにて、"--input must be an existing directory" と言われてしまう [#307](https://github.com/oggy8021/Harite/issues/307)

```bash
$ harite slideshow --input /home/katsu/Picture/watch1/,/home/katsu/Picture/watch2/ --interval-sec 5 --mode random --plugin linux
--input must be an existing directory
```

- slideshowにおいて、"," 区切りでパスを指定できない。結果、 `Srcdir-L`, `Srcdir-R` 相当が指定できない

### A. dry-runにおいて、interval-sec=5 として実施したにも関わらず、何もメッセージが出ない

```bash
$ harite slideshow --input /home/katsu/Picture/watch1 --interval-sec 5 --mode random --plugin linux
Slideshow start: input=/home/katsu/Picture/watch1 images=6 interval_sec=5 mode=random plugin=linux dry_run=True
```

- `do-it` を付与して実施したところ、左右両ディスプレイに同じ画像を適用しながら、5s サイクルに正しく変更された
- このとき、`sequential`, `random` 両モードも試しており意図通りに変更できることを確認できた

### B. inputパラメータにおける ２つの画像入力において、"," 区切りが無視される

```bash
$ harite optimize --input ~/ピクチャ/Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg,~/ピクチャ/Higashiyama-Kaii-Zansho-1920x1080-1-700x394.jpg -r 4096x1280 --two-screen --output ~/ピクチャ
Saved: [PosixPath('/home/katsu/ピクチャ/harite_output_0043.jpg')]
Placement: PlacementResult(image_path=PosixPath('/home/katsu/ピクチャ/Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg'), x=664, y=0, width=720, height=1280, rotation=0.0, scale=1.0289389067524115, score=1.0, posit='left')
```

- `posit=left` と見えるとおり、左だけに配置している
- いっぽう以下のように、 `input` パラメータを2つ並べる場合は正しく認識された

```bash
$ harite optimize --input ~/ピクチャ/Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg --input ~/ピクチャ/Higashiyama-Kaii-Zansho-1920x1080-1-700x394.jpg -r 4096x1280 --two-screen --output ~/ピクチャ
Saved: [PosixPath('/home/katsu/ピクチャ/harite_output_0044.jpg')]
Placement: PlacementResult(image_path=PosixPath('/home/katsu/ピクチャ/Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg'), x=664, y=0, width=720, height=1280, rotation=0.0, scale=1.0289389067524115, score=1.0, posit='left')
Placement: PlacementResult(image_path=PosixPath('/home/katsu/ピクチャ/Higashiyama-Kaii-Zansho-1920x1080-1-700x394.jpg'), x=2048, y=64, width=2048, height=1152, rotation=0.0, scale=2.9257142857142857, score=1.0, posit='right')
```

### C. 単純 Apply がファイルパスを解決できず実施できない

```bash
$ harite apply --plugin linux --file ~/ピクチャ/harite_output_044.jpg
Wallpaper file does not exist: /home/katsu/ピクチャ/harite_output_044.jpg
Plugin 'linux' failed to apply wallpaper: /home/katsu/ピクチャ/harite_output_044.jpg
```

- この問題があるため、他 Apply 検証の一切ができなかった。

### D. マージン領域を用意せず、embed-info=params としたときにそのまま実行された

```bash
$ harite optimize --input ~/ピクチャ/Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg --input ~/ピクチャ/Higashiyama-Kaii-Zansho-1920x1080-1-700x394.jpg -r 4096x1280 --two-screen --output ~/ピクチャ --embed-position=top --embed-info=params
Saved: [PosixPath('/home/katsu/ピクチャ/harite_output_0045.jpg')]
Placement: PlacementResult(image_path=PosixPath('/home/katsu/ピクチャ/Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg'), x=664, y=0, width=720, height=1280, rotation=0.0, scale=1.0289389067524115, score=1.0, posit='left')
Placement: PlacementResult(image_path=PosixPath('/home/katsu/ピクチャ/Higashiyama-Kaii-Zansho-1920x1080-1-700x394.jpg'), x=2048, y=64, width=2048, height=1152, rotation=0.0, scale=2.9257142857142857, score=1.0, posit='right')
```

- マージン領域がないため、エラーになる想定であったが認識が異なるか？
- Optimize結果としては、マージン領域を確保していないため 生成後画像中に params表示 はない。
- 引数として params が残る。これは settings が正しいのでは
- embed-position の候補も GUI と異なっており、古い global margin のままである
  `--embed-position                       TEXT  Margin side for info text: auto|top|bottom|left|right [default: auto]`

### E. Dを前提に、マージン領域を確保の上実施したら 左ディスプレイの上側領域に params表示がなされた

```bash
$ harite optimize --input ~/ピクチャ/Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg --input ~/ピクチャ/Higashiyama-Kaii-Zansho-1920x1080-1-700x394.jpg -r 4096x1280 --two-screen --output ~/ピクチャ --embed-position=top --embed-info=params --margins 100,100,100,100
Saved: [PosixPath('/home/katsu/ピクチャ/harite_output_0046.jpg')]
Placement: PlacementResult(image_path=PosixPath('/home/katsu/ピクチャ/Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg'), x=720, y=100, width=607, height=1080, rotation=0.0, scale=0.8681672025723473, score=1.0, posit='left')
Placement: PlacementResult(image_path=PosixPath('/home/katsu/ピクチャ/Higashiyama-Kaii-Zansho-1920x1080-1-700x394.jpg'), x=2148, y=120, width=1848, height=1040, rotation=0.0, scale=2.64, score=1.0, posit='right')
```

- 旧動作における `auto` 指定のままに配置されたものと認識する。
- guiにおける `Margin tab` での扱いとは大きく異なるため、要改修

### F. Eを前提に align, valignを指定したみた。結果が意図通りか点検したい

```bash
$ harite optimize --input ~/ピクチャ/Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg --input ~/ピクチャ/Higashiyama-Kaii-Zansho-1920x1080-1-700x394.jpg -r 4096x1280 --two-screen --output ~/ピクチャ --embed-position=top --embed-info=params --margins 100,100,100,100 --align left,right --valign top,bottom
Saved: [PosixPath('/home/katsu/ピクチャ/harite_output_0047.jpg')]
Placement: PlacementResult(image_path=PosixPath('/home/katsu/ピクチャ/Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg'), x=100, y=100, width=607, height=1080, rotation=0.0, scale=0.8681672025723473, score=1.0, posit='left')
Placement: PlacementResult(image_path=PosixPath('/home/katsu/ピクチャ/Higashiyama-Kaii-Zansho-1920x1080-1-700x394.jpg'), x=2148, y=140, width=1848, height=1040, rotation=0.0, scale=2.64, score=1.0, posit='right')
```

- 生成後画像の変化が小さく、パラメータの優劣・強弱を点検したい。また、同仕様をしっかり書けているか点検したい。

### G. Fを前提に、マージン領域を確保せず（取り去って）実施したところ、意図する align, valign 結果が得られた

```bash
$ harite optimize --input ~/ピクチャ/Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg --input ~/ピクチャ/Higashiyama-Kaii-Zansho-1920x1080-1-700x394.jpg -r 4096x1280 --two-screen --output ~/ピクチャ --align left,right --valign top,bottom
Saved: [PosixPath('/home/katsu/ピクチャ/harite_output_0048.jpg')]
Placement: PlacementResult(image_path=PosixPath('/home/katsu/ピクチャ/Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg'), x=0, y=0, width=720, height=1280, rotation=0.0, scale=1.0289389067524115, score=1.0, posit='left')
Placement: PlacementResult(image_path=PosixPath('/home/katsu/ピクチャ/Higashiyama-Kaii-Zansho-1920x1080-1-700x394.jpg'), x=2048, y=128, width=2048, height=1152, rotation=0.0, scale=2.9257142857142857, score=1.0, posit='right')
```

### H.背景色の指定について、 `#`を付与した16進数表記が使えず `#` を除いたところコマンド受付された

```bash
harite optimize --input ~/ピクチャ/Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg --input ~/ピクチャ/Higashiyama-Kaii-Zansho-1920x1080-1-700x394.jpg -r 4096x1280 --two-screen --output ~/ピクチャ --background-color E0E0E0
```

- 以下のように `#E0E0E0` では引数が必要ですとの的外れなエラーメッセージとなった。

```bash
$ harite optimize --input ~/ピクチャ/Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg --input ~/ピクチャ/Higashiyama-Kaii-Zansho-1920x1080-1-700x394.jpg -r 4096x1280 --two-screen --output ~/ピクチャ --background-color #E0E0E0
╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Option '--background-color' requires an argument.                                                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

- hex じゃなくて適当な文字列だと `#` 付きで書きなさいとのエラーメッセージとなった。先の結果と矛盾する。

```bash
$ harite optimize --input ~/ピクチャ/Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg --input ~/ピクチャ/Higashiyama-Kaii-Zansho-1920x1080-1-700x394.jpg -r 4096x1280 --two-screen --output ~/ピクチャ --background-color hoge
--background-color must be a hex RGB value like #1E1E1E
```

### I. 設定ファイルを使っての実行

- まず、helpより見えるガイド `Path to JSON settings file to load defaults from [default: None]` の意味が分からない。

```bash
$ harite optimize --input ~/ピクチャ/Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg --input ~/ピクチャ/Higashiyama-Kaii-Zansho-1920x1080-1-700x394.jpg -r 4096x1280 --two-screen --output ~/ピクチャ -c
╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Option '-c' requires an argument.                                                                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

- ファイルパス無しだとエラーとなり

```bash
$ harite optimize --input ~/ピクチャ/Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg --input ~/ピクチャ/Higashiyama-Kaii-Zansho-1920x1080-1-700x394.jpg -r 4096x1280 --two-screen --output ~/ピクチャ --background-color --settings-file ~/.config/harite/harite-settings.json 
Usage: harite optimize [OPTIONS]
Try 'harite optimize --help' for help.
╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Got unexpected extra argument (/home/katsu/.config/harite/harite-settings.json)                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

- 具体的ファイル名を与えてもエラーとなる。
- また、Optimizeにしか見えないが slideshow や apply との関わりも不明
- I. の2つ目の実行は Ownerの実行方法誤りであり、settings-file 自体の不具合論点とは切り分ける

### J. scalingパラメータ

```bash
-rw-rw-r--  1 katsu katsu 314758  5月 21 19:53 harite_output_0050.jpg ... fit
-rw-rw-r--  1 katsu katsu 314758  5月 21 19:53 harite_output_0051.jpg ... fill
-rw-rw-r--  1 katsu katsu 314758  5月 21 19:54 harite_output_0052.jpg ... crop
```

- fit, fill, crop 出力結果の diff を上記に示した。差異がない、何をしようとしているのか今一度確認。
- inputに画像を指定して、タイル画像を作るときの並べ方なのであれば廃止する
- applyや plugin 向けのパラメータである場合は、Optimizeにある理由から再点検

## 改修ブランチ 候補案

- `ws6-fix-cli-help-surface`
- `ws6-fix-cli-input-apply-paths`

## ミニ実施順メモ

### 1. help / surface 系

対象:

- A. slideshow dry-run 廃止
- E. embed-position 配置規則の見直しと GUI / core / CLI 整合
- H. background-color help 見直し
- I. settings-file help 見直し
- J. scaling user-facing 露出停止と `fill` / `crop` 廃止
- dry-run / do-it の作用表現見直し

実施順:

1. 正本変更
2. commit/push
3. テストコードを用意
4. commit/push
5. 本体実装
6. commit/push
7. 3層比較 + 必要に応じてテスト強化、正本記述強化
8. commit/push
9. merge

### 2. input / apply-path 系

対象:

- #307. slideshow input directory 指定面の整理
- B. optimize input comma 区切りと help 整合
- C. apply path not found の原因解析と改修

実施順:

1. 正本変更
2. commit/push
3. テストコードを用意
4. commit/push
5. 本体実装
6. commit/push
7. 3層比較 + 必要に応じてテスト強化、正本記述強化
8. commit/push
9. merge

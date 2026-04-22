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

- 母体は `ImgSize` / `WorkSpace` / `Rectangle` / `Screen` 系の構造で、位置決めをかなり強く拘束していた。
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

## 次の使い方

- P8-2B 着手前に、本メモを見ながら「どの値がどの段階で勝つか」を 1 項目ずつ確認する。
- 新しい visible wording を入れる前に、その wording が指す実計算対象が本当に一致しているかを確認する。

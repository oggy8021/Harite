# optimize 入力拘束と two-screen 仕様

最終更新: 2026-03-21

## 目的

- `harite optimize` の `--input` 複数指定ルールと `--two-screen` の期待動作を固定化する。
- 実装変更時に、どこが仕様変更なのかを比較しやすくする。

## 対象範囲

- 対象コマンド: `harite optimize`
- 対象オプション: `--input`, `--two-screen`, `--l-display`, `--r-display`
- 実装参照: `src/harite/cli.py`, `src/harite/core.py`

## `--input` の仕様

### 受け付け形式

- `--input` は複数回指定できる。
- 1 回の `--input` 値内でカンマ区切り指定できる。
- 上記 2 つは同じリストへ連結される。

例:

- `--input ./dirA --input ./dirB`
- `--input ./dirA,./dirB`
- `--input ./dirA,./dirB --input ./img1.jpg`

### 入力拘束

- `--input` は画像ファイルパスのみを受け付ける。
- ディレクトリ指定は受け付けない。
- 複数入力は指定順に連結される。
- 重複パスは除外しない（同一ファイルが複数回入ることがある）。

## `--two-screen` の仕様

### 基本

- `--two-screen` は左右 2 画面向けの配置モード。
- ただし、明確な左右幅の分割は `--l-display` と `--r-display` 併用時に有効。

### `--l-display` / `--r-display` 併用時

- 左セル幅は `--l-display` の幅、右セル幅は `--r-display` の幅を使う。
- 入力は先頭 2 件までを使用する。
- 先頭 1 件目を左、2 件目を右に割り当てる。
- 3 件目以降は使用しない。

### `--two-screen` 単独時

- 現行実装では通常の横分割ロジックに近い動作になる。
- `--l-display` / `--r-display` を指定しない場合、two-screen 固有の左右幅分割は発生しない。

## 既知の制約

- `fixed` は廃止方針であり、左右順は入力順に従う。
- 左右幅合計と `--resolution` の厳密整合チェックは未実装。
- 1 件入力で two-screen + 左右幅指定の場合、片側のみ画像で反対側は背景のままになる。

## パラメータ強弱（現状）

- 強:
  - `margins`: まず有効描画領域を決める。
  - `align` / `valign`: `margins` で決まった領域内で配置位置を決める。
  - `two-screen` + `l_display/r_display`: 左右幅を明示的に固定し、先頭2入力を左右へ割り当てる。
- 中:
  - `padding`: 通常分割時のセル間隔に効く（two-screen 条件では効き方が限定される）。
- 限定的:
  - `layout`: 現行 optimize 実装では実質 mosaic 相当。
  - `scaling`: 指定可能だが現行 optimize 実装での挙動差は限定的。
  - `fixed`: 指定可能だが現行 optimize 実装での影響は限定的。
  - `random_seed`: 指定可能だが現行 optimize 実装での影響は限定的。

## 変更時の更新ルール

- 次のいずれかを変更したら本書を更新する。
  - `--input` のパース方法（カンマ区切り、複数回指定、再帰有無、拡張子対象）
  - `--two-screen` の有効条件や割り当て規則
  - 入力件数に対する利用ルール（先頭 2 件など）
- 仕様変更を伴う場合は、`--help` 文言とテストを同一 PR で更新する。

# CLI: two_screen / fixed の config 連携仕様

最終更新: 2026-04-11

## 目的

- `harite optimize` における `--two-screen` と `--fixed` について、`--config` からの既定値解決を明文化する。
- 既存の優先順位方針（CLI > config > default）と整合する形で、回帰しにくい実装単位を定義する。

## 背景

- `margins` / `l_display` / `r_display` に加え、`two_screen` / `fixed` も config 連携対象として実装した。
- 旧CLI互換の上位5仕様で定義した優先順位（CLI > config > default）を bool オプションにも適用し、挙動を統一した。

## 対象範囲

- 対象コマンド: `harite optimize`
- 対象オプション: `--two-screen`, `--fixed`, `--config`
- 対象ファイル:
  - `src/harite/cli.py`
  - `tests/cli/test_cli_validation.py`

## 仕様

### 優先順位

- `two_screen` と `fixed` は次の優先順位で最終値を解決する。
  - 1. CLI フラグ
  - 1. config の値
  - 1. 既定値（False）

### 値の解釈（config 側）

- config では次の値を受理する。
  - boolean: `true` / `false`
  - string: `"true"`, `"false"`, `"1"`, `"0"`, `"yes"`, `"no"`, `"on"`, `"off"`
  - int: `1` / `0`
- 不正値は `false` 扱いではなく、明示エラーとする（将来の誤設定を検知しやすくするため）。

### CLI フラグとの関係

- `--two-screen` / `--fixed` が指定された場合は config 値より CLI を優先する。
- CLI 未指定時のみ config 値を採用する。

注記:

- `--two-screen/--no-two-screen` と `--fixed/--no-fixed` により、CLI から明示的に false を指定できる。

## 受け入れ基準

- `tests/cli/test_cli_validation.py` で以下が pass する。
  - config の `two_screen=true`, `fixed=true` が optimize 呼び出し引数へ反映される。
  - config の `two_screen=false`, `fixed=false` に対し、CLI フラグ指定時は true が優先される。
  - 不正な config 値は `Exit code=2` で失敗し、エラーメッセージが出る。

## 非対象

- `margins` / `l_display` / `r_display` の既存優先順位の再定義。
- two-screen の配置アルゴリズム変更。
- watch/daemon 系機能。

## 実装PR案（最小）

1. `src/harite/cli.py` に bool config 解決ヘルパを追加。
2. `two_screen` / `fixed` の解決ロジックを helper 経由に変更。
3. `tests/cli/test_cli_validation.py` に優先順位テストを追加・更新。

## オープン事項

- なし（本仕様の対象範囲は実装とテストで反映済み）。

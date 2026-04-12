# harite watch 最小仕様

最終更新: 2026-04-12

## 目的

- 旧 ChangerDir 相当の最低限機能を `harite watch` として定義し、段階的に導入する。
- 常駐系（daemon/applet）へ拡張する前に、CLI単体で安全に検証できる範囲を固定する。

## 背景

- 旧CLI互換の上位優先項目は `optimize` 系を中心に実装済み。
- 次段として「ディレクトリ内画像の順次/ランダム切替」需要があるが、常駐化を同時実装すると設計と検証コストが増える。
- まずは最小仕様で導入し、手動運用とCI負荷のバランスを取る。

## 対象範囲

- 対象コマンド: `harite watch`
- 実装候補ファイル:
  - `src/harite/cli.py`
  - `src/harite/watch.py`（新規）
- テスト候補:
  - `tests/cli/test_watch_cli.py`（新規）
  - `tests/watch/test_watch_runner.py`（新規）

## 非対象

- daemon/applet/tray の常駐機能。
- OS起動時自動実行。
- GUI からの watch 制御。

## 用語

- 入力ソース: 壁紙候補画像を読み込むディレクトリ。
- 列挙戦略: 画像選択順序（順次またはランダム）。
- 1サイクル: 画像選択から apply 実行までの1回分処理。

## インターフェース案（最小）

- `harite watch --input <dir> --interval-sec <int> [--mode sequential|random] [--log-level normal|detail] [--dry-run|--do-it] [--iterations <int>]`

オプション意味（最小）:

- `--input`: 画像ディレクトリ（必須）。
- `--interval-sec`: サイクル間隔秒（必須、1以上）。
- `--mode`: 列挙戦略。既定は `sequential`。
- `--log-level`: ログ出力レベル。`normal`（既定）または `detail`。
- `--dry-run/--do-it`: 既定は `--dry-run`。実適用は `--do-it` 明示時のみ。
- `--iterations`: 実行回数上限。未指定時は無限実行。

注記:

- 無限実行は手動停止（Ctrl+C）を想定する。
- 初期段階では `harite optimize` との統合オプションは持たせず、watch内部で最小経路を固定する。

## 振る舞い仕様

### 入力検証

- `--input` が存在しない場合は即時エラー終了。
- `--interval-sec < 1` は即時エラー終了。
- 対象ディレクトリに有効画像が1件もない場合は即時エラー終了。

### 画像列挙

- `sequential`:
  - ファイル名昇順で並べ、先頭から順に採用。
  - 最後まで到達後は先頭に戻る。
- `random`:
  - 各サイクルで候補から1件選択。
  - 候補が2件以上なら、直前画像を除外して選択する（連続同一画像を回避）。
  - 候補が1件のみの場合は同一画像が連続する。

### 実行制御

- `--iterations` 指定時は回数到達で正常終了。
- Ctrl+C 受信時は終了メッセージを表示して正常終了扱いにする。
- `--do-it` 実行中に1サイクル失敗しても失敗内容を表示し、watch は継続する（fail-fast は採用しない）。

### 適用モード

- `--dry-run`:
  - 選択画像と適用先情報を表示し、システム設定は変更しない。
- `--do-it`:
  - 既存 apply 経路で実適用する。
  - 失敗時はエラーを表示し、watch は継続する。

### ログとサマリ（最小標準）

- `--log-level normal`:
  - start 行と completed 行を出力する。
  - サイクル行は失敗時（`apply=failed` / `apply=error`）のみ出力する。
- `--log-level detail`:
  - start 行と completed 行に加え、全サイクル行を出力する。
- 無限実行時（`--iterations` 未指定）の出力頻度:
  - `normal`: 失敗がない間は start 行のみで進行し、失敗時のみサイクル行を出力する。
  - `detail`: 全サイクル行を継続出力する。

- 1サイクル失敗時のログ理由は固定文字列で出力する。
  - plugin が `False` を返した場合: `reason=plugin-returned-false`
  - plugin が例外を送出した場合: `reason=plugin-exception`
- `--do-it` 時の終了行で以下を出力する。
  - `apply_ok`（成功サイクル数）
  - `apply_failed`（plugin戻り値 `False` の件数）
  - `apply_error`（plugin例外の件数）
  - `apply_failed_total`（`apply_failed + apply_error`）
- `--dry-run` 時の終了行で `dry_run_cycles` を出力する。

## 受け入れ基準

- CLIテスト:
  - 必須引数不足でエラー終了する。
  - `--interval-sec` の境界値（0/1）を検証する。
  - `--dry-run` 既定が有効である。
- ロジックテスト:
  - `sequential` が循環する。
  - `random` が候補集合外を返さない。
  - `--iterations` 指定時に回数どおり終了する。
- 手動確認:
  - Linux Mint (Xfce) で dry-run 実行ログを確認できる。

## 実装ステップ（小PR）

1. 仕様承認後、`watch` コマンドのCLI骨格と入力検証を実装。
2. 列挙戦略（sequential/random）を実装。
3. `--dry-run/--do-it` 分岐を実装し、既存 apply 経路へ接続。
4. `--iterations` と Ctrl+C 終了処理を実装。
5. テストとヘルプ文言を同期。

## 決定事項（2026-04-12 確定）

- `--do-it` の失敗時は watch を継続する（fail-fast は導入しない）。
- 無限実行時のログ頻度は `log-level` に従う（`normal` は失敗時のみサイクル行、`detail` は全サイクル行）。

## 関連仕様

- `docs/specs/cli-compatibility.md`
- `docs/specs/cli-top5-priority-options.md`
- `docs/manual-validation-gate.md`

# harite watch 最小仕様

最終更新: 2026-04-11

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

- `harite watch --input <dir> --interval-sec <int> [--mode sequential|random] [--dry-run|--do-it] [--iterations <int>]`

オプション意味（最小）:

- `--input`: 画像ディレクトリ（必須）。
- `--interval-sec`: サイクル間隔秒（必須、1以上）。
- `--mode`: 列挙戦略。既定は `sequential`。
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
  - 直前と同一画像の連続選択は許容（最小仕様）。

### 実行制御

- `--iterations` 指定時は回数到達で正常終了。
- Ctrl+C 受信時は終了メッセージを表示して正常終了扱いにする。
- 1サイクル失敗時は失敗内容を表示し、次サイクルへ継続する。

### 適用モード

- `--dry-run`:
  - 選択画像と適用先情報を表示し、システム設定は変更しない。
- `--do-it`:
  - 既存 apply 経路で実適用する。
  - 失敗時はエラーを表示し、watch は継続する。

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

## オープン事項（オーナー確認）

- `random` で同一画像連続選択を初期段階で禁止するか。
- `--do-it` の失敗時に即終了するか継続するか（初期値）。
- 無限実行時のログ出力頻度をどこまで標準化するか。

## 関連仕様

- `docs/specs/cli-compatibility.md`
- `docs/specs/cli-top5-priority-options.md`
- `docs/manual-validation-gate.md`

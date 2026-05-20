# MainWindow State Model（Phase 3 UIバインド向け / 履歴資料）

最終更新: 2026-04-18

## 位置づけ

- この文書は Phase 3 時点の UI バインド前提で整理した MainWindow 状態モデルの履歴資料である。
- current runtime の状態設計をそのまま表す正本文書ではない。
- 後続フェーズでは、当時どの state を UI 要素へ結び付けようとしていたかの証跡として参照する。

## 目的

- `MainWindow` が保持する状態を UI バインド観点で明文化する。
- adapter 実装時に、どの状態をどのUI要素へ反映するかを固定する。

## 状態一覧

### 1. 実行制御状態

- `can_optimize: bool`
  - 意味: optimize 実行可能かどうか
  - 主な更新契機: `on_change_input_text`
  - UI反映: Optimize ボタンの enable/disable

- `closed: bool`
  - 意味: ウィンドウが終了処理済みか
  - 主な更新契機: `on_close`
  - UI反映: adapter 側の終了シーケンス制御

### 2. エラー状態

- `last_error: str`
  - 意味: 直近エラー（空文字はエラーなし）
  - 主な更新契機: 入力検証失敗、optimize/apply失敗、dialog close
  - UI反映: エラーバナー/ステータスラベル/ダイアログ

### 3. ログ状態

- `logs: list[str]`
  - 意味: 操作イベントと結果の時系列ログ
  - 主な更新契機: ほぼ全ハンドラ (`_log` 経由)
  - UI反映: ログペイン

### 4. プラグイン状態

- `available_plugins: tuple[str, ...]`
  - 意味: 選択可能 plugin 一覧
  - 主な更新契機: 初期化時
  - UI反映: plugin ドロップダウン候補

- `plugin_name: str`
  - 意味: 現在選択中 plugin
  - 主な更新契機: `_default_plugin_name`、`on_change_plugin`
  - UI反映: plugin ドロップダウン現在値

### 5. 実行結果状態

- `last_saved_files: list[Path]`
  - 意味: 直近 optimize の出力ファイル群
  - 主な更新契機: `on_optimize`
  - UI反映: 出力ファイル一覧、apply 対象候補

### 6. フォーム状態

- `form_state: OptimizeFormState`
  - 意味: optimize 実行入力の集約状態
  - 主なフィールド:
    - 入力: `input_value`、`resolution`、`output_dir`
    - 配置/品質: `scaling`、`align`、`valign`、`quality`
    - two-screen: `two_screen`、`margins`、`l_display`、`r_display`
    - margin text: `embed_info`、`embed_text`、`embed_position`、`embed_max_lines`
  - UI反映: 各入力コンポーネント

## 状態遷移（主要フロー）

1. 入力更新

- `on_change_input_text` -> `form_state.input_value` 更新
- `can_optimize` を再計算
- 不正時は `last_error` に反映

1. optimize 実行

- `on_optimize` 成功:
  - `last_saved_files` 更新
  - `last_error` クリア
  - `logs` に保存結果追記
- `on_optimize` 失敗:
  - `last_error` 更新
  - `logs` に失敗理由追記

1. apply 実行

- `_apply_latest` 成功:
  - `last_error` クリア
  - `logs` に適用ログ追記
- `_apply_latest` 失敗:
  - `last_error` 更新
  - `logs` に失敗ログ追記

1. dialog close

- `on_close_error_dialog`: `last_error` クリア
- その他 dialog close: `logs` のみ更新

## UI バインド要件（Phase 3）

- `can_optimize` の変更時に optimize ボタン状態を即時反映する。
- `last_error` が非空のときエラー表示を有効化し、空時は非表示化する。
- `logs` の追加は append-only として UI 側で末尾追従表示する。
- `last_saved_files` が空の間は apply ボタンを無効化する。
- `plugin_name` の変更は `available_plugins` の候補内に制約する。

## テスト観点への接続

- 既存: `tests/gui/test_main_window_signals.py` で state 更新と失敗パスを検証済み。
- Phase 3 以降: adapter 層で「signal -> state 更新 -> UI反映」の接続テストを追加する。

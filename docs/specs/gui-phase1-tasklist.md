# GUI Phase 1 タスクリスト（最初の3 signal）

最終更新: 2026-03-21

## 目的

- MVP 先行の 3 signal 実装を、短いサイクルで確実に終わらせる。

## 対象 signal

1. `on_entPath_insert_text` -> `MainWindow.on_change_input_text`
2. `on_btnSave_clicked` -> `MainWindow.on_optimize`
3. `on_WallPosit_MainWindow_delete_event` -> `MainWindow.on_close`

## 実装タスク

1. MainWindow に入力欄状態と実行可否フラグを追加
- DoD: 入力が空なら実行不可、入力ありで実行可

2. `on_change_input_text` を実装
- DoD: 入力変更時にバリデーションが走り、ログまたは状態表示が更新される

3. `on_optimize` を実装
- DoD: `OptimizeController.run_optimize` 呼び出しで成功時に出力パス、失敗時に例外メッセージを表示

4. `on_close` を実装
- DoD: 常駐プロセスを残さず終了する

5. 最小テストを追加
- DoD: controller 単体で validate と run_optimize の正常/異常ケースを確認

## 完了判定

- 3 signal が `docs/specs/gui-signal-mapping.md` で `implemented` に更新されている
- `python -m pytest -q` が成功
- `python -m harite.gui.app` で起動後、操作フローを手動確認できる

## 実装状況（2026-03-21）

- [x] `on_change_input_text` 実装
- [x] `on_optimize` 実装
- [x] `on_close` 実装
- [x] 最小テスト追加（`tests/gui/test_main_window_signals.py`）

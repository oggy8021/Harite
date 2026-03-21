# GUI Integration Test Matrix（Phase 3 最小セット）

最終更新: 2026-03-21

## 目的

- Phase 3 の実UI統合で必要な最小テストセットを固定する。
- headless CI を維持しつつ、signal 接続と安全導線の回帰を検出する。

## テストレイヤ

1. Headless Smoke
- 目的: GUI backend 未導入環境でも import/run が壊れないことを保証
- 対象:
  - `tests/gui/test_app_entrypoint.py`
- 合格条件:
  - `harite.gui.app` の import が成功
  - `run()` が `MainWindow.show()` まで到達

2. Signal-to-Handler Contract
- 目的: signal 相当イベントから `MainWindow` state 更新が壊れていないことを保証
- 対象:
  - `tests/gui/test_main_window_signals.py`
- 重点ケース:
  - 入力更新時の `can_optimize` / `last_error`
  - margins 更新の正常/異常
  - plugin 選択の正常/異常
  - dialog close ログ反映

3. Optimize/Apply Safety
- 目的: optimize と apply の失敗パスを安全に扱えることを保証
- 対象:
  - `tests/gui/test_main_window_signals.py`
  - `tests/gui/test_optimize_controller.py`
- 重点ケース:
  - optimize 前提不足（入力なし）
  - plugin 未登録/false return/例外
  - margins/display パース異常

4. Mapper Consistency
- 目的: GUI state から CLI 引数への変換が壊れていないことを保証
- 対象:
  - `tests/gui/test_cli_mapper.py`
- 合格条件:
  - 必須引数が常に出力される
  - optional 引数は設定時のみ出力される

## 推奨 pytest 実行セット

- 最小セット（CI常時）
  - `pytest -q tests/gui/test_app_entrypoint.py tests/gui/test_main_window_signals.py tests/gui/test_optimize_controller.py tests/gui/test_cli_mapper.py`

- 拡張セット（実UI adapter 導入後）
  - `tests/gui/integration/` を新設し、backend 依存テストを分離
  - backend 未導入環境は `pytest.importorskip` で skip

## 失敗時の切り分けガイド

- app entrypoint 失敗:
  - `src/harite/gui/app.py` の import 経路・fallback を確認
- signal contract 失敗:
  - `src/harite/gui/views/main_window.py` の state 更新順序を確認
- optimize/apply 安全系失敗:
  - `src/harite/gui/controllers/optimize_controller.py` と plugin 例外処理を確認
- mapper 失敗:
  - `src/harite/gui/services/cli_mapper.py` の optional flag 条件分岐を確認

## Phase 3 での運用ルール

- 実UI adapter 追加時は、まず headless smoke が通ることを優先する。
- backend 依存の統合テストは常時必須にせず、別ジョブまたは条件付きで運用する。
- `MainWindow` の state contract を壊す変更は、対応する signal テストを同PRで更新する。

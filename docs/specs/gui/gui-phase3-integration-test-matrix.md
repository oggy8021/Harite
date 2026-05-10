# GUI Integration Test Matrix（Phase 3 最小セット / 履歴資料）

最終更新: 2026-04-18

## 位置づけ

- この文書は Phase 3 時点で想定していた最小 GUI テストセットの履歴資料である。
- current runtime の最新テスト戦略や受け入れ基準を定義する文書ではない。
- 後続フェーズでは、当時の回帰観点と signal-to-handler 契約の棚卸し資料として参照する。

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

1. Signal-to-Handler Contract

- 目的: signal 相当イベントから `MainWindow` state 更新が壊れていないことを保証
- 対象:
  - `tests/gui/test_main_window_signals.py`
- 重点ケース:
  - 入力更新時の `can_optimize` / `last_error`
  - margins 更新の正常/異常
  - plugin 選択の正常/異常
  - dialog close ログ反映

1. Optimize/Apply Safety

- 目的: optimize と apply の失敗パスを安全に扱えることを保証
- 対象:
  - `tests/gui/test_main_window_signals.py`
  - `tests/gui/test_optimize_controller.py`
- 重点ケース:
  - optimize 前提不足（入力なし）
  - plugin 未登録/false return/例外
  - margins/display パース異常

1. Mapper Consistency

- 目的: GUI state から CLI 引数への変換が壊れていないことを保証
- 対象:
  - `tests/gui/test_cli_mapper.py`
- 合格条件:
  - 必須引数が常に出力される
  - optional 引数は設定時のみ出力される

1. Runtime Fallback UI Contract

- 目的: GTK runtime fallback の主要表示/導線が MainWindow ハンドラ契約と整合することを保証
- 対象:
  - `tests/gui/test_gtk_runtime_backend.py`
- 重点ケース:
  - Main/Optimize/Apply セクションのオブジェクト公開
  - 入力更新 -> Optimize有効化 -> Apply有効化の状態遷移
  - 実行中/成功/失敗/handler-missing のメッセージ規約
  - `on_btnSave_clicked` / `on_btnSetWall_clicked` の signal-to-handler 経路

## 推奨 pytest 実行セット

- 最小セット（CI常時）
  - `pytest -q tests/gui/test_app_entrypoint.py tests/gui/test_main_window_signals.py tests/gui/test_optimize_controller.py tests/gui/test_cli_mapper.py`
  - `pytest -q tests/gui/test_gtk_runtime_backend.py`

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

## CI smoke と manual gate の責務分離

| 項目 | CI smoke の責務 | manual gate の責務 |
| --- | --- | --- |
| 目的 | import/run と state contract の回帰検出 | 実機依存挙動と運用証跡の確認 |
| 実行環境 | headless（backend 非依存） | 実機（Windows/XFCE/macOS 利用可能環境） |
| 主対象 | `tests/gui/*` と `scripts/gui_layout_smoke.py --simulate --validate` | `scripts/gui_layout_smoke.py --auto-artifacts` または `--strict-manual` |
| 成功基準 | pytest green, GUI smoke pass | Result matrix 記録と PR 添付証跡の整合 |
| 失敗時対応 | 同PR内で修正必須 | 原因記録後に修正PRを先行 |

運用メモ:

- GUI プレースホルダ期間は `--auto-artifacts` を既定とし、スクリーンショットは `not-available` を許容する。
- 実ウィンドウ表示が可能になったら `--strict-manual` を既定へ切り替える。
- runtime fallback で UI 契約を検証した場合も、本UI（正式配置）で Step1-5 と 3画面添付を再実施して最終判定する。

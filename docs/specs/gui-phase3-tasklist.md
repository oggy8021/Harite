# GUI Phase 3 タスクリスト（実UI統合の準備）

最終更新: 2026-03-22

## 目的

- Phase 1/2 で整えたロジックとテスト基盤を活かし、実UI統合へ進む前提を固定する。
- 実装リスクを先に分解し、小PRで段階的に進めるための実行順を定義する。

## スコープ

- docs/specs/gui-standalone-design.md
- docs/specs/gui-signal-mapping.md
- src/harite/gui/app.py
- src/harite/gui/views/main_window.py
- tests/gui/

## 方針

- 常駐機能（tray/indicator/daemon）は引き続き非対象。
- 実UI導入時も headless CI で import/run が壊れない構成を維持する。
- View 層の追加は adapter 増設で行い、既存の MainWindow ロジックとテストを再利用する。

## タスク

- [x] Step 1: 実UI導入の境界を固定（framework依存を adapter 層に閉じ込める設計メモ作成）
- [x] Step 2: signal mapping の "dropped" 項目を Phase 3 対象/非対象に再分類
- [x] Step 3: MainWindow の状態モデルを UI バインド向けに明文化（入力・エラー・ログ・出力）
- [x] Step 4: GUI統合テスト最小セットを定義（headless smoke / signal-to-handler / apply safety）
- [x] Step 5: 実UIの最小読み込みプロトタイプ（読み込みのみ、操作は未接続）を別PRで追加

## 現在地（管理用）

- Phase 3 の初期計画（Step 1-5）は完了。
- 追加で、実機検証運用を回しやすくする補助実装を完了。
  - `src/harite/gui/adapters/ui_adapter.py`（最小バインド）
  - `src/harite/gui/adapters/fake_adapter.py`（headless検証向け）
  - `scripts/gui_layout_smoke.py`（validate / markdown / PRコメント出力）
  - `tests/scripts/test_gui_layout_smoke.py`（運用オプションの回帰テスト）
  - `docs/manual-validation-gate.md`（実機確認フロー更新）

## 進行管理ルール（この先）

- このドキュメントは「完了済みタスク表」ではなく、現在地と次マイルストーンの管理に使う。
- 小PR単位で進め、各PRは 1 目的に限定する。
- 更新ルール:
  - 新しい管理対象を始める時: `次マイルストーン` に項目追加。
  - PR merge 時: 該当項目を `進捗ログ` に移し、状態を更新。
  - 実機確認が必要な変更時: `docs/manual-validation-gate.md` のテンプレート記録を必須化。

## 進捗ログ（2026-03-22時点）

- 完了: Phase 3 Step 1-5（設計固定、mapping再分類、状態モデル、統合テスト観点、UI loader試作）
- 完了: 実機検証補助の強化（smoke validate、markdown出力、失敗チェック表示、PRコメントテンプレート）
- 完了: `.pyc` 追跡解除と再発防止（`__pycache__/`, `*.pyc` ignore）
- 完了: M1-1（glade signal handler 抽出 + `MainWindow` への mapping 検証）
- 完了: M1-2（adapter dispatch API 追加 + bind metadata へ接続ハンドラ記録）
- 完了: M1-3（backend signal connect 実装: `connect_signals(mapping)` / `connect(name, callback)` を adapter で吸収）
- 完了: M2-1（OS別実機確認マトリクスと成果物命名ルールを `manual-validation-gate` に追加）
- 完了: M2-2（GUI実機確認レポートテンプレートを `docs/templates/gui-manual-validation-report.md` として追加）
- 完了: M2-3準備（`gui_layout_smoke.py` に統合レポート出力 `--report-out` / `--print-report` を追加）
- 完了: M3-1準備（`gui_layout_smoke.py` に `--auto-artifacts` を追加し、PR添付用成果物を1コマンド出力）
- 完了: M3-2準備（手動結果ステータスを `pass/fail/not-available` に正規化し、旧表記を互換吸収）
- 完了: M3-3準備（`--require-screenshots` で添付漏れを検出し、レポート運用を強制可能化）
- 完了: M3-4準備（`--verify-screenshot-files` で添付パス実体の存在確認を追加）
- 完了: M3-5準備（`--strict-manual` で必須チェックと成果物出力を一括有効化）
- 完了: 暫定運用実績（XFCEで `--auto-artifacts` を実行し、`pr-146-xfce-pr-comment.md` を生成。GUIプレースホルダのためスクリーンショットは未実施）
- 完了: M4（`gui-integration-test-matrix` に CI smoke と manual gate の責務分離を明文化）
- 完了: M1-4（`app.run` から optional backend signal 接続導線を追加し、GTK backend 利用時の bind 実行を可能化）
- 完了: M1-5（`app.run` に optional 実ウィンドウ表示導線を追加し、GTK 利用時は placeholder 出力から表示フローへ遷移可能化）
- 完了: M1（実UI本バインド導入の最小要件を満たし、signal接続から window presentation までの導線を確立）

## 次マイルストーン（Phase 3 後半）

- [x] M1: 実UIウィジェットへの本バインド導入（adapterで signal -> `MainWindow` 接続を実装）
- [ ] M2: 主要画面の配置/表示の実機確認（Windows/XFCE/macOSのうち利用可能環境）
- [ ] M3: 実機確認結果を PR コメントに標準フォーマットで記録（スクリーンショット付き）
- [x] M4: 実UI導入後の最小回帰セットを固定（CI smoke + manual gate の責務分離）

## M1 詳細進捗

- [x] M1-1: glade の handler 抽出と legacy handler -> `MainWindow` メソッドの妥当性検証
- [x] M1-2: present handler 向け dispatch table を生成し、bind 時に `_adapter_signal_dispatch` と metadata へ保持
- [x] M1-3: 実UI backend 側で dispatch table を使った connect 実装（backend依存は adapter 内に限定）
- [x] M1-4: `app.run` に optional backend signal binding（`HARITE_GUI_BIND_SIGNALS` / `bind_ui_backend`）を導入
- [x] M1-5: `app.run` に optional window presentation（`HARITE_GUI_PRESENT_WINDOW` / `present_ui_window`）を導入

## M2 詳細進捗

- [x] M2-1: OS別の実機確認マトリクスを定義（pass/fail/not-available）
- [x] M2-2: 実機確認成果物の命名規則を定義（json/md/screenshot）
- [x] M2-3a: 手動検証結果を1ファイルへ束ねるレポート出力を smoke script に追加
- [ ] M2-3b: 1環境以上でテンプレート運用実績を作成し、PRコメントに添付（スクリーンショット付きは実ウィンドウ実装後）

## M3 詳細進捗

- [x] M3-1: PRコメント用成果物（json/report/pr-comment/smoke-md）の自動出力を追加
- [x] M3-2a: 手動結果ステータス入力の正規化（pass/fail/not-available）
- [x] M3-3a: スクリーンショット必須モード（`--require-screenshots`）を追加
- [x] M3-4a: スクリーンショット実ファイル存在チェック（`--verify-screenshot-files`）を追加
- [x] M3-5a: 厳格運用モード（`--strict-manual`）を追加
- [ ] M3-2b: 実機確認1件分を `pr-comment` へ添付して標準フォーマット運用を確定（スクリーンショット付きは実ウィンドウ実装後）

## 小PR分割（推奨）

1. docs(gui): define phase3 adapter boundaries
2. docs(gui): reclassify signal mapping for phase3
3. test(gui): define integration smoke matrix
4. feat(gui): add UI loader prototype behind safe entrypoint

## 成果物

- Step 1: `docs/specs/gui-phase3-adapter-boundary.md`
- Step 2: `docs/specs/gui-signal-mapping.md`（Phase 3 での再分類表）
- Step 3: `docs/specs/gui-mainwindow-state-model.md`
- Step 4: `docs/specs/gui-integration-test-matrix.md`
- Step 5: `src/harite/gui/adapters/ui_loader.py`, `src/harite/gui/app.py`, `tests/gui/test_ui_loader_prototype.py`

## DoD

- Phase 3 の実装順が docs 上で固定され、各PRの目的が明確になっている。
- signal mapping の Phase 3 対象が明示され、MVP非対象との混同がない。
- headless CI 継続条件（import/run可能）がテスト観点として明文化されている。

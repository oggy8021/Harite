# GUI Phase 5 タスクリスト（見た目・レイアウト再現）

最終更新: 2026-04-13

## 目的

- Glade 版の見た目とレイアウト意図を、現行 GUI に段階的に再現する。
- Phase4 で未達だった「画面構造（A）」を解消し、視覚的な差分を明確に縮小する。

## スコープ

- `src/harite/gui/views/`
- `src/harite/gui/presentation/`
- `tests/gui/`
- `docs/specs/gui/`
- `docs/manual-validation-gate.md`

## Phase5 方針

- 1ブランチ = 1PR を厳守する。
- 主要機能が通っている前提で、見た目再現のための大胆なレイアウト変更を許容する。
- 各PRでユーザーが体感できる視覚差分を必ず1つ以上入れる。
- 変更ごとにスクリーンショット比較（MainWindow / Optimize / Apply）を残す。
- 実装変更は回帰テストと実機証跡を同時提出する。

## 受け入れ基準（固定）

- 画面構造: 配置、余白、グルーピング、視線導線が Phase4 より改善している。
- 画面差別化: Optimize と Apply が視覚的に区別できる。
- 一貫性: タイトル、サブタイトル、セクション見出し、主要ボタンのスタイルが統一される。
- 体験差分: 各PRで before/after 比較により差分が説明できる。
- 品質運用: `tests/gui/` 回帰 + XFCE 実機証跡を継続提出する。

## 現在の進捗スナップショット（2026-04-13）

- P5-2 はクローズ済み（`[x]`）。
- 実装済み:
  - `src/harite/gui/views/main_window.py` に Phase5 レイアウトメタデータ（`layout_version`, `layout_sections`）を反映。
  - `src/harite/gui/adapters/gtk_backend.py` を Glade近似の縦5段/中央3列構成へ再編。
  - Window 方針を `resizable=True` に確定。
- ドキュメント済み:
  - Glade再現基準: `docs/specs/gui/gui-glade-layout-reconstruction.md`
  - P5-2判定基準: `docs/specs/gui/gui-phase5-p5-2-layout-checklist.md`
  - 手動検証メモ: `out/manual-validation/gui-phase5-pr2-memo.md`
- 未完了:
  - PR5-2 メモで上がった後続項目の分配（P5-3 / P5-4 / 将来拡張）

## タスク（1タスク=1PR）

- [x] P5-2 feat(gui): MainWindow の大胆レイアウト再構成
  - Glade基準配置: `docs/specs/gui/gui-glade-layout-reconstruction.md`
  - 上流解析参照: `docs/specs/upstream-full-analysis.md`
  - チェックリスト: `docs/specs/gui/gui-phase5-p5-2-layout-checklist.md`
  - 対象: セクション再配置、余白設計の再調整、視線導線の再設計、Windowポリシー（例: `resizable`）見直し
  - 完了条件: before/after で構造差分が明確で、P5-1 の MainWindow 観点が pass、上流由来のUI制約の採否理由が記録される

- [x] P5-3 feat(gui): Optimize / Apply のレイアウト分離強化
  - 仕様メモ: `docs/specs/gui/gui-phase5-p5-3-flow-policy.md`
  - 回帰必須: `Apply` は Optimize 未実行時に非活性、`Apply dry-run` 既定を維持
  - 対象: 情報階層、操作ブロック、見出し体系、アクション位置の差別化
  - 進捗: `on_btnSave_clicked` は `on_save_legacy` に分離し、旧Save導線を保持したまま `Optimize (provisional)` を Save 近傍に仮置き
  - 進捗: SaveDialog confirm で保存先を受けた場合、入力準備済みなら旧Save導線（選択+生成）を連続実行
  - 進捗: `on_btnOpenSave_clicked` は clicked引数だけでなく `SaveWallpaperDialog` から `get_filename()` を解決可能（実Glade経路の保存先取得を補強）
  - 進捗: GTK fallback で SaveDialog プロキシの open/hide 状態遷移（Saveでopen、confirm/cancelでhide）を実装
  - 進捗: SaveDialog の `btnOpenSave` / `btnCancelSave` は open 中のみ活性、closed では非活性に復帰
  - 進捗: GTK fallback で `btnSave` は dialog open 専用に分離し、生成継続は confirm 経由へ統一
  - 進捗: MainWindow の `on_save_dialog_confirm` でも保存先必須を適用し、空confirmを失敗（`save path is required`）として統一
  - 進捗: MainWindow の confirm は既存 `save_path` を再利用可能（引数なしconfirmの再試行導線を確保）
  - 進捗: MainWindow でも closed 状態の confirm/cancel は `save dialog ignored (closed)` として無視（backendと意味統一）
  - 進捗: MainWindow の `on_save_legacy` は dialog open 専用へ変更し、生成は confirm（`on_save_dialog_confirm -> on_optimize`）へ統一
  - 進捗: SaveDialog closed 状態での confirm/cancel 呼び出しは `ignored-closed` として無視（誤発火ガード）
  - 進捗: 入力クリア時は SaveDialog を自動で closed へ戻し、confirm/cancel を非活性化（状態整合）
  - 進捗: MainWindow でも入力クリア時に SaveDialog 状態を closed へ戻す（fallbackとの意味統一）
  - 進捗: dialog open 中でも保存先未選択なら confirm を非活性化し、選択後のみ活性化（誤確定防止）
  - 進捗: GTK fallback で `btnSave`（legacy）と `btnOptimize`（modern優先/未接続時fallback）の結線を分離
  - 進捗: `watch planned`（start/stop/interval）と `save_dialog_confirm/cancel` の正規結線を実装済み
  - 完了記録: 固定回帰コマンド `python.exe -m pytest -q tests/gui/test_ui_adapter_dispatch.py tests/gui/test_ui_adapter_mapping_validation.py tests/gui/test_main_window_signals.py tests/gui/test_gtk_runtime_backend.py` が継続して pass（2026-04-13）
  - 完了記録: Save/Optimize 分離、SaveDialog 状態遷移、confirm/cancel ガード、MainWindow/GTK fallback の意味統一を達成
  - 完了条件（新規成果）: 一目で画面意図の違いが分かり、優先順位ルール（`fixed > margin > toggles`）が Notes/ヘルプで確認でき、P5-1 の Optimize/Apply 区別観点が pass

- [ ] P5-8 refactor(gui): 旧互換シグナル/Glade依存の段階撤去（P5-3完了後）
  - 前提: P5-3 が `done` へ遷移し、Save/Optimize/Apply/SaveDialog の新導線が回帰で安定していること
  - 対象: legacy handler名への過剰フォールバック、旧Glade互換前提の分岐、互換専用テストの整理
  - 完了条件: 現行導線のみで回帰が通り、互換維持のためだけの分岐が削減される

- [ ] P5-4 feat(gui): レトロフィット + 現代化のスタイル統一
  - 対象: 旧デザイン意図の復元と、読みやすさ向上の同時達成
  - 完了条件: 同種要素の見た目ゆれがなく、旧版らしさが説明可能

- [ ] P5-1 docs: 見た目再現チェックリスト定義
  - 成果物: `docs/specs/gui/gui-phase5-visual-checklist.md`
  - 完了条件: MainWindow/Optimize/Apply の比較観点がチェック可能な形で記述される

- [ ] P5-5 test(gui): 視覚回帰テストとスモーク補強
  - 対象: `tests/gui/` に Phase5 観点を追加
  - 完了条件: CI で再現可能な形で回帰検知できる

- [ ] P5-6 docs/ops: manual gate の Phase5 同期
  - 対象: `docs/manual-validation-gate.md` の観点更新
  - 完了条件: docs / tests / 実機記録の判定項目が一致

- [ ] P5-7 validate: XFCE 実機で最終判定
  - 成果物: JSON / Report / PR Comment / 3画面スクリーンショット
  - 完了条件: P5-1 チェックリスト必須項目がすべて pass

## 推奨着手順

1. P5-2（MainWindow 大胆再構成）
2. P5-3（Optimize/Apply 分離強化）
3. P5-8（旧互換シグナル/Glade依存の段階撤去）
4. P5-4（レトロフィット + 現代化）
5. P5-1（チェックリスト固定）
6. P5-5（回帰テスト）
7. P5-6（manual gate 同期）
8. P5-7（実機最終判定）

## ブランチ命名（例）

1. P5-2: `feature/gui-phase5-mainwindow-radical-layout-20260413`
2. P5-3: `feature/gui-phase5-optimize-apply-layout-separation-20260413`
3. P5-4: `feature/gui-phase5-retrofit-modernized-style-20260413`
4. P5-1: `docs/gui-phase5-visual-checklist-20260413`
5. P5-5: `test/gui-phase5-visual-regression-20260413`
6. P5-6: `docs/gui-phase5-manual-gate-sync-20260413`
7. P5-7: `chore/gui-phase5-xfce-validation-20260413`

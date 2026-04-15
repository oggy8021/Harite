# GUI Phase 5 タスクリスト（見た目・レイアウト再現）

最終更新: 2026-04-15

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
  - `src/harite/gui/adapters/gtk_backend.py` を Glade近似の縦5段/中央十字配置を軸に再編（列/行増減を許容）。
  - Window 方針を `resizable=True` に確定。
- ドキュメント済み:
  - Glade再現基準: `docs/specs/gui/gui-glade-layout-reconstruction.md`
  - P5-2判定基準: `docs/specs/gui/gui-phase5-p5-2-layout-checklist.md`
  - 手動検証メモ: `out/manual-validation/gui-phase5-pr2-memo.md`
- 未完了:
  - PR5-2 メモで上がった後続項目の分配（P5-3 / P5-4 / 将来拡張）

方針決定ログ（2026-04-14）:

- 中央レイアウトは「3列固定」より「十字配置再現 + 実装しやすさ」を優先し、列/行増減を許容する。

## タスク（1タスク=1PR）

### P5-8以降の共通ゲート（必須）

- 対象: P5-8 / P5-9 / P5-10 / P5-11 の全PR。
- 参照正本: `docs/specs/gui/gui-phase5-upstream-traceability-checklist.md`
- 着手条件:
  - 母体プログラム（`wallpaperoptimizer`）の該当機能を読解し、対応関係を文書化する。
  - `docs/specs/gui/gui-phase5-upstream-traceability-checklist.md` をPR単位で作成し、差分・非対応・保留理由を明記する。
  - 実装前レビューで合意（Approve）を得る。
- 停止条件:
  - 上記チェック未充足のPRは `Draft` 維持、`merge禁止` とする。
- 実装条件:
  - 合意済みドキュメントにない挙動を先行実装しない。
  - MainWindow暫定ロジックへの寄せ集めを避け、Dialog/責務分割方針に沿う。
- 完了条件:
  - 実機結果（pass/warn/fail）と上流対応表の整合が取れている。
  - レビューコメントで「上流対応OK」または「差分を合意済み」と明示されている。

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
  - 進捗: `on_btnSave_clicked` は `on_save` に分離し、旧Save導線を保持したまま `Optimize (provisional)` を Save 近傍に仮置き
  - 進捗: SaveDialog confirm で保存先を受けた場合、入力準備済みなら旧Save導線（選択+生成）を連続実行
  - 進捗: `on_btnOpenSave_clicked` は clicked引数だけでなく `SaveWallpaperDialog` から `get_filename()` を解決可能（実Glade経路の保存先取得を補強）
  - 進捗: GTK fallback で SaveDialog プロキシの open/hide 状態遷移（Saveでopen、confirm/cancelでhide）を実装
  - 進捗: SaveDialog の `btnOpenSave` / `btnCancelSave` は open 中のみ活性、closed では非活性に復帰
  - 進捗: GTK fallback で `btnSave` は dialog open 専用に分離し、生成継続は confirm 経由へ統一
  - 進捗: MainWindow の `on_save_dialog_confirm` でも保存先必須を適用し、空confirmを失敗（`save path is required`）として統一
  - 進捗: MainWindow の confirm は既存 `save_path` を再利用可能（引数なしconfirmの再試行導線を確保）
  - 進捗: MainWindow でも closed 状態の confirm/cancel は `save dialog ignored (closed)` として無視（backendと意味統一）
  - 進捗: MainWindow の `on_save` は dialog open 専用へ変更し、生成は confirm（`on_save_dialog_confirm -> on_optimize`）へ統一
  - 進捗: SaveDialog closed 状態での confirm/cancel 呼び出しは `ignored-closed` として無視（誤発火ガード）
  - 進捗: 入力クリア時は SaveDialog を自動で closed へ戻し、confirm/cancel を非活性化（状態整合）
  - 進捗: MainWindow でも入力クリア時に SaveDialog 状態を closed へ戻す（fallbackとの意味統一）
  - 進捗: dialog open 中でも保存先未選択なら confirm を非活性化し、選択後のみ活性化（誤確定防止）
  - 進捗: GTK fallback で `btnSave`（legacy）と `btnOptimize`（modern優先/未接続時fallback）の結線を分離
  - 進捗: `watch planned`（start/stop/interval）と `save_dialog_confirm/cancel` の正規結線を実装済み
  - 完了記録: 固定回帰コマンド `python.exe -m pytest -q tests/gui/test_ui_adapter_dispatch.py tests/gui/test_ui_adapter_mapping_validation.py tests/gui/test_main_window_signals.py tests/gui/test_gtk_runtime_backend.py` が継続して pass（2026-04-13）
  - 完了記録: Save/Optimize 分離、SaveDialog 状態遷移、confirm/cancel ガード、MainWindow/GTK fallback の意味統一を達成
  - 完了条件（新規成果）: 一目で画面意図の違いが分かり、優先順位ルール（`fixed > margin > toggles`）が Notes/ヘルプで確認でき、P5-1 の Optimize/Apply 区別観点が pass

- [x] P5-8 refactor(gui): 旧互換シグナル/Glade依存の段階撤去（P5-3完了後）
  - 前提: P5-3 が `done` へ遷移し、Save/Optimize/Apply/SaveDialog の新導線が回帰で安定していること
  - 対象: legacy handler名への過剰フォールバック、旧Glade互換前提の分岐、互換専用テストの整理
  - 進捗: `gtk_backend` の `btnOptimize -> on_btnSave_clicked` fallback を削除し、Optimize は `on_btnOptimize_clicked` のみを受け付けるよう統一（2026-04-13）
  - 進捗: `ui_adapter` の `on_btnSave_clicked` マップ先を `on_save` へ変更し、`MainWindow` も `on_save` を正規エンドポイントへ統一（2026-04-13）
  - 進捗: `MainWindow` の signal docstring を `Signal endpoint` 表記へ統一し、互換中心の注記を最小化（2026-04-13）
  - 進捗: `on_save_legacy` と `legacy save flow` の実参照を撤去し、コード/テスト/仕様文書の表記を `on_save` へ一本化（2026-04-13）
  - 完了記録: Owner 実行の固定回帰コマンド `python.exe -m pytest -q tests/gui/test_ui_adapter_dispatch.py tests/gui/test_ui_adapter_mapping_validation.py tests/gui/test_main_window_signals.py tests/gui/test_gtk_runtime_backend.py` が 100% pass（2026-04-13）
  - 完了記録: Optimize の旧 fallback 撤去、Save confirm の過剰委譲撤去、`on_save` 正規化で互換維持専用分岐を段階削減
  - 完了条件: 現行導線のみで回帰が通り、互換維持のためだけの分岐が削減される

- [x] P5-4 feat(gui): レトロフィット + 現代化のスタイル統一
  - 仕様メモ: `docs/specs/gui/gui-phase5-p5-4-retrofit-modernize.md`
  - 対象: 旧デザイン意図の復元と、読みやすさ向上の同時達成
  - 進捗: P5-8 完了を受けて P5-4 着手（2026-04-13）
  - 初手スコープ: MainWindow / Optimize / Apply の見出し・主要ボタン・補助ボタンで visual token を統一
  - 初手スコープ: `gtk_backend` の button/label face を「主操作・副操作・planned」の3階層で再定義
  - 初手スコープ: before/after の体感差分を残すため、command bar と status 表示の視認性を優先改善
  - 進捗: `gtk_backend` に `tglPush*` / `tglLower*` を追加し、MainWindow の配置トグルIDを Glade 準拠で取得可能化（2026-04-13）
  - 進捗: `test_gtk_runtime_backend` に toggle/open ボタン存在チェックを追加し、欠落の再発を回帰固定（2026-04-13）
  - 完了記録（部分）: Owner 実行の固定回帰コマンドが 100% pass（2026-04-13）
  - 進捗: `Open-L/Open-R` を fallback backend で結線し、入力欄値を `on_btnGetImg_clicked` へ渡す最小導線を実装（2026-04-13）
  - 進捗: `ui_adapter` に `on_btnGetImg_clicked` の path解決（clicked引数/`entPathL`）を追加し、clicked引数依存の誤動作を抑制（2026-04-13）
  - 進捗: runtime backend / dispatch テストへ Open-L/Open-R の状態遷移・コールバック経路を追加（2026-04-13）
  - 完了記録（部分）: Open-L/Open-R 導線追加後も Owner 実行の固定回帰コマンドが 100% pass（2026-04-13）
  - 進捗: fallback UI に `Style cues` / `Commands` / `Flow` ラベルを追加し、`About/Help (secondary)` と `planned` の視認軸を明示（2026-04-13, 2026-04-14更新）
  - 進捗: `About/Help` のみ secondary 表記を維持し、`Save/Optimize/Apply/Prefs` からは primary/secondary 区別語彙を除去（2026-04-14）
  - 進捗: `test_gtk_runtime_backend` / `test_phase5_visual_regression` に新語彙（`Style cues`, `Commands`, ボタンラベル簡素化）の回帰チェックを反映（2026-04-14）
  - 完了記録（部分）: visual tier 整備後も Owner 実行の固定回帰コマンドが 100% pass（2026-04-13）
  - 進捗: `Save/Optimize/Apply` は機能名中心の簡潔ラベルへ移行し、`About/Help` 以外の secondary/primary 表記ノイズを削減（2026-04-14）
  - 進捗: `tgl` 系ボタンの語彙を `Top/Bottom/Left/Right` へ統一し、左右対称の見た目ルールを固定（2026-04-13）
  - 進捗: `test_gtk_runtime_backend` に `tgl` ラベル語彙の回帰チェックを追加（2026-04-13）
  - 完了記録（部分）: `tgl` 語彙統一後も Owner 実行の固定回帰コマンドが 100% pass（2026-04-13）
  - 完了記録: fallback UI の style tier（primary/secondary/planned）と flow 表示を整備し、旧版らしさの説明軸を仕様化（2026-04-13）
  - 完了記録: Owner 実行の固定回帰コマンド `python.exe -m pytest -q tests/gui/test_ui_adapter_dispatch.py tests/gui/test_ui_adapter_mapping_validation.py tests/gui/test_main_window_signals.py tests/gui/test_gtk_runtime_backend.py` が継続して 100% pass（2026-04-13）
  - 完了条件: 同種要素の見た目ゆれがなく、旧版らしさが説明可能

- [x] P5-1 docs: 見た目再現チェックリスト定義
  - 成果物: `docs/specs/gui/gui-phase5-visual-checklist.md`
  - 進捗: P5-4 完了を受けて P5-1 着手（2026-04-13）
  - 完了記録: `docs/specs/gui/gui-phase5-visual-checklist.md` を作成し、MainWindow/Optimize/Apply の比較観点と判定テンプレートを固定（2026-04-13）
  - 完了条件: MainWindow/Optimize/Apply の比較観点がチェック可能な形で記述される

- [x] P5-5 test(gui): 視覚回帰テストとスモーク補強
  - 対象: `tests/gui/` に Phase5 観点を追加
  - 進捗: `tests/gui/test_phase5_visual_regression.py` を追加し、Main/Optimize/Apply の視覚トークン固定と optimize->apply スモーク導線を回帰化（2026-04-13）
  - 進捗: MainWindow の `layout_version` / sections / primary flow を Phase5 観点で検証するスモークを追加（2026-04-13）
  - 進捗: 固定回帰コマンドに `tests/gui/test_phase5_visual_regression.py` を加えた実行がローカルで pass（2026-04-13）
  - 完了記録: Phase5 の視覚トークン固定・主要導線スモーク・MainWindow 青写真検証が CI で再現可能な形で回帰化された（2026-04-13）
  - 完了条件: CI で再現可能な形で回帰検知できる

- [x] P5-6 docs/ops: manual gate の Phase5 同期
  - 対象: `docs/manual-validation-gate.md` の観点更新
  - 進捗: `docs/manual-validation-gate.md` に `Phase 5 manual gate 同期（P5-6）` を追加し、P5-1 視覚チェックリスト観点（Main/Optimize/Apply/Style）の判定ルールを固定（2026-04-13）
  - 進捗: 固定回帰コマンドへ `tests/gui/test_phase5_visual_regression.py` を含めた Owner 実行手順を manual gate に同期（2026-04-13）
  - 完了記録: docs / tests / 実機記録（3画面 + 判定テンプレート + PRコメント）の突合ルールを manual gate 上で統一（2026-04-13）
  - 完了条件: docs / tests / 実機記録の判定項目が一致

- [ ] P5-7 validate: XFCE 実機で最終判定
  - 成果物: JSON / Report / PR Comment / 3画面スクリーンショット
  - 進捗: XFCE 実機判定用テンプレート `docs/specs/gui/gui-phase5-p5-7-xfce-validation-template.md` を追加（2026-04-13）
  - 進捗: P5-1 観点（MainWindow/Optimize/Apply/Style）の `pass/warn/fail` 記録欄と PR 貼り付け用コメント雛形を用意（2026-04-13）
  - 進捗: Owner 実行の固定回帰コマンドが 100% pass（2026-04-13）
  - 進捗: `docs/specs/gui/gui-glade-layout-reconstruction.md` に `docs/legacy-ui/wallpositapplet.glade` / `docs/legacy-ui/Glade.py` を一次根拠として明記（2026-04-14）
  - 進捗: `gtk_backend` で `entPathR` を実体化し、`Open-R -> entPathR` の入力反映導線を復旧（2026-04-14）
  - 進捗: `ui_adapter.bind_mainwindow` で `on_btnOptimize_clicked -> on_optimize` の補完接続を追加し、runtime fallback の handler-missing を抑制（2026-04-14）
  - 進捗: Owner 実行の固定回帰コマンドが 100% pass（2026-04-14）
  - 完了条件: P5-1 チェックリスト必須項目がすべて pass

- [ ] P5-8 feat(gui): トグル排他と margin 反映の実装確定
  - 対象: 同一side内の `Top/Bottom`、`Left/Right` の同時成立矛盾を排除する
  - 例示: `tglUpperL` がONのとき `tglLowerL` を押すと `tglUpperL` が落ちて切り替わる
  - 例示: `tglUpperL` がONでも `tglUpperR` は押せるままにする
  - 例示: `tglPushLeftR` がONのとき `tglPushRightR` を押すと `tglPushLeftR` が落ちて切り替わる
  - 要件: margin +/- 操作の反映を可視化し、優先順位ルール（fixed > margin > toggles）と整合
  - 進捗: runtime fallback を母体 `WindowBase.py` の `pressed / toggled / released` semantics へ寄せ、same-side の切替と both-off 復帰の土台を再現（2026-04-15）
  - 進捗: margin spin は changed された widget を起点に現在値を更新できるよう整理し、母体の単項目更新に寄せる方向を確定（2026-04-15）
  - 進捗: margin の `- / +` は独立ボタンではなく `GtkSpinButton` 内蔵ステッパと判明。fallback 側へ upstream 相当の range/increment 設定を補完し、実機の不発要因を是正（2026-04-15）
  - 進捗: `Current state` パネルを追加し、`fixed / margins / align / valign` の採用中値を fallback UI 上で常時確認可能にした（2026-04-15）
  - 進捗: `tests/gui/test_gtk_runtime_backend.py` と `tests/gui/test_phase5_visual_regression.py` を含む GUI 回帰が 100% pass（2026-04-15, owner実行）
  - 進捗: XFCE 実機で toggle 挙動と見た目の再現を確認済み。次の焦点は margin の扱い整理（2026-04-15, owner確認）
  - 追加条件: 旧 `WindowBase` のトグル相互排他（押下/復帰）仕様の対応表を提出し、実装前レビュー合意を得る
  - 完了条件: トグル排他・margin反映・優先順位の挙動が回帰テストと実機メモで一致

- [ ] P5-9 feat(gui): Open 導線を Dialog 主体へ復元（ImgOpenDialog 相当）
  - 対象: `Open-L` / `Open-R` 押下でファイル選択ダイアログを開き、選択結果を `entPathL` / `entPathR` へ反映
  - 要件: 直入力前提の承認UXではなく、旧導線準拠の「選択結果を表示」へ戻す
  - 要件: 拡張子制限など旧 `ImgOpenDialog` 相当の制御を段階導入
  - 追加条件: 旧 `Widget/ImgOpenDialog.py` の挙動対応表（選択/キャンセル/拡張子制限）を提出し、実装前レビュー合意を得る
  - 完了条件: Open 押下が `planned` 表示で終わらず、選択/キャンセルの状態遷移がUIで確認できる

- [ ] P5-10 feat(gui): watch 導線の実処理導入（srcdirL/srcdirR）
  - 対象: watch start/stop/interval の planned 導線を実処理へ昇格
  - 要件: watch 用の左右画像向けパスは `srcdirL`, `srcdirR` で指定可能、未指定も許容
  - 補足: MainWindow の `entPathL` / `entPathR` とは責務を分離（watch 用入力と通常入力を混同しない）
  - 進捗: `spnInterval` も upstream では `GtkSpinButton` の adjustment (`60 1 86400 1 10 0`) で駆動されると確認。fallback 側へ同等の range/increment/初期値を補完し、margin と同種のステッパ不発を予防（2026-04-15）
  - 追加条件: 旧 `SettingDialog` / `SrcdirDialog` の導線対応表を提出し、実装前レビュー合意を得る
  - 完了条件: watch 実行時に `srcdirL` / `srcdirR` の有無に応じた分岐が回帰テストで固定される

- [ ] P5-11 chore(gui): Save 体験改善（低優先 / SaveWallpaperDialog 相当）
  - 対象: 保存先・保存名の明示、confirm/cancel の排他制御、完了後の保存先表示
  - 優先度方針: `Optimize / Apply / do-it` の導線安定化より後に着手する
  - 背景: 保存場所選定を除く本体処理は `Optimize` と重なるため、緊急課題とは切り分ける
  - 要件: `Save Cancel` が `cancel-failed` とならない導線を保証
  - 要件: どこに何という名前で保存されたかを MainWindow 側で追跡可能にする
  - 追加条件: 旧 `Widget/SaveWallpaperDialog.py` の挙動対応表（保存先確定/キャンセル/表示）を提出し、実装前レビュー合意を得る
  - 完了条件: Save 体験が「行き先不明」にならず、保存先情報が実機で確認できる

## 推奨着手順

1. P5-2（MainWindow 大胆再構成）
2. P5-3（Optimize/Apply 分離強化）
3. P5-8（旧互換シグナル/Glade依存の段階撤去）
4. P5-4（レトロフィット + 現代化）
5. P5-1（チェックリスト固定）
6. P5-5（回帰テスト）
7. P5-6（manual gate 同期）
8. P5-7（実機最終判定）
9. P5-8（トグル排他 + margin 反映）
10. P5-9（Open Dialog 導線復元）
11. P5-10（watch 導線実処理）
12. P5-11（Save 体験改善・低優先）

## ブランチ命名（例）

1. P5-2: `feature/gui-phase5-mainwindow-radical-layout-20260413`
2. P5-3: `feature/gui-phase5-optimize-apply-layout-separation-20260413`
3. P5-4: `feature/gui-phase5-retrofit-modernized-style-20260413`
4. P5-1: `docs/gui-phase5-visual-checklist-20260413`
5. P5-5: `test/gui-phase5-visual-regression-20260413`
6. P5-6: `docs/gui-phase5-manual-gate-sync-20260413`
7. P5-7: `chore/gui-phase5-xfce-validation-20260413`
8. P5-8: `feature/gui-phase5-p5-8-toggle-exclusion-margin-sync-20260414`
9. P5-9: `feature/gui-phase5-p5-9-open-dialog-restore-20260414`
10. P5-10: `feature/gui-phase5-p5-10-watch-flow-srcdir-20260414`
11. P5-11: `chore/gui-phase5-p5-11-save-ux-improvement-20260414`

## P5-8以降のPR運用（明示）

- P5-8
  - PRタイトル案: `feat(gui): enforce toggle exclusivity and margin sync (P5-8)`
  - PRTXT short: `P5-8で同一side内のトグル排他とmargin反映を実装。tglUpperL/tglLowerL、tglPushLeftR/tglPushRightR などの矛盾を防ぎつつ、反対sideは独立維持、fixed>margin>toggles優先順位に整合。`
- P5-9
  - PRタイトル案: `feat(gui): restore Open-L/Open-R dialog flow (P5-9)`
  - PRTXT short: `P5-9でOpen-L/Open-RをDialog主体へ復元。選択結果をentPathL/Rへ反映し、直入力前提の暫定導線を置換。`
- P5-10
  - PRタイトル案: `feat(gui): implement watch flow with srcdirL/srcdirR (P5-10)`
  - PRTXT short: `P5-10でwatch導線を実処理化。srcdirL/srcdirR指定（未指定許容）を導入し、MainWindow入力責務と分離。`
- P5-11
  - PRタイトル案: `chore(gui): improve save UX and dialog clarity (P5-11)`
  - PRTXT short: `P5-11でSave体験を低優先で改善。保存先/保存名の可視化とconfirm/cancel整合を強化し、行き先不明を解消。`

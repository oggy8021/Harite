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

- P5-2 は実装進行中（`[-]`）。
- 実装済み:
  - `src/harite/gui/views/main_window.py` に Phase5 レイアウトメタデータ（`layout_version`, `layout_sections`）を反映。
  - `src/harite/gui/adapters/gtk_backend.py` を Glade近似の縦5段/中央3列構成へ再編。
  - Window 方針を `resizable=True` に確定。
- ドキュメント済み:
  - Glade再現基準: `docs/specs/gui/gui-glade-layout-reconstruction.md`
  - P5-2判定基準: `docs/specs/gui/gui-phase5-p5-2-layout-checklist.md`
- 未完了:
  - before/after 最終判定記録
  - P5-2 チェックリスト A〜E の最終 `pass` 確定
  - PR本文最終化

## タスク（1タスク=1PR）

- [-] P5-2 feat(gui): MainWindow の大胆レイアウト再構成
  - Glade基準配置: `docs/specs/gui/gui-glade-layout-reconstruction.md`
  - 上流解析参照: `docs/specs/upstream-full-analysis.md`
  - チェックリスト: `docs/specs/gui/gui-phase5-p5-2-layout-checklist.md`
  - 対象: セクション再配置、余白設計の再調整、視線導線の再設計、Windowポリシー（例: `resizable`）見直し
  - 完了条件: before/after で構造差分が明確で、P5-1 の MainWindow 観点が pass、上流由来のUI制約の採否理由が記録される

- [ ] P5-3 feat(gui): Optimize / Apply のレイアウト分離強化
  - 対象: 情報階層、操作ブロック、見出し体系、アクション位置の差別化
  - 完了条件: 一目で画面意図の違いが分かり、P5-1 の Optimize/Apply 区別観点が pass

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
3. P5-4（レトロフィット + 現代化）
4. P5-1（チェックリスト固定）
5. P5-5（回帰テスト）
6. P5-6（manual gate 同期）
7. P5-7（実機最終判定）

## ブランチ命名（例）

1. P5-2: `feature/gui-phase5-mainwindow-radical-layout-20260413`
2. P5-3: `feature/gui-phase5-optimize-apply-layout-separation-20260413`
3. P5-4: `feature/gui-phase5-retrofit-modernized-style-20260413`
4. P5-1: `docs/gui-phase5-visual-checklist-20260413`
5. P5-5: `test/gui-phase5-visual-regression-20260413`
6. P5-6: `docs/gui-phase5-manual-gate-sync-20260413`
7. P5-7: `chore/gui-phase5-xfce-validation-20260413`

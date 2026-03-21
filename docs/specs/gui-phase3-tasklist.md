# GUI Phase 3 タスクリスト（実UI統合の準備）

最終更新: 2026-03-21

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
- [ ] Step 3: MainWindow の状態モデルを UI バインド向けに明文化（入力・エラー・ログ・出力）
- [ ] Step 4: GUI統合テスト最小セットを定義（headless smoke / signal-to-handler / apply safety）
- [ ] Step 5: 実UIの最小読み込みプロトタイプ（読み込みのみ、操作は未接続）を別PRで追加

## 小PR分割（推奨）

1. docs(gui): define phase3 adapter boundaries
2. docs(gui): reclassify signal mapping for phase3
3. test(gui): define integration smoke matrix
4. feat(gui): add UI loader prototype behind safe entrypoint

## 成果物

- Step 1: `docs/specs/gui-phase3-adapter-boundary.md`
- Step 2: `docs/specs/gui-signal-mapping.md`（Phase 3 での再分類表）

## DoD

- Phase 3 の実装順が docs 上で固定され、各PRの目的が明確になっている。
- signal mapping の Phase 3 対象が明示され、MVP非対象との混同がない。
- headless CI 継続条件（import/run可能）がテスト観点として明文化されている。

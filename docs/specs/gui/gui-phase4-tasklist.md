# GUI Phase 4 タスクリスト（UI再現・体験改善）

最終更新: 2026-04-12

## 目的

- 旧画面との差分を可視化し、Glade移行後の UI ギャップを段階的に解消する。
- 操作効率と状態表示を改善し、実機運用で迷いなく使えるUIへ収束する。

## スコープ

- `src/harite/gui/`
- `tests/gui/`
- `docs/manual-validation-gate.md`
- `docs/specs/gui/`

## Phase4 方針

- 1ブランチ = 1PR を厳守する。
- 受け入れ基準は「旧画面との差分チェックリスト」を先に定義してから実装する。
- 既存の test/docs/manual gate を維持する。
- UI変更ごとに「回帰テスト + XFCE実機証跡」を残す。

## 受け入れ基準（固定）

- 画面構造: 主要ボタン配置、余白、グルーピング、視線導線がチェックリストで合格。
- 状態表示: 実行中/成功/失敗の表示が一貫し、判定可能。
- 操作効率: 主要アクション到達のクリック数と迷いが削減される。
- 品質運用: 回帰テストと XFCE 実機証跡の提出が継続される。

## タスク（1タスク=1PR）

- [ ] P4-1 docs: 旧画面との差分チェックリストを定義
  - 成果物: `docs/specs/gui/gui-phase4-diff-checklist.md`
  - 完了条件: 画面構造/状態表示/操作効率の観点がチェック可能な形で記述されている

- [ ] P4-2 feat(gui): MainWindow のレイアウト/導線調整
  - 対象: 主要ボタン配置、入力欄グルーピング、余白の統一
  - 完了条件: P4-1 の該当項目が pass

- [ ] P4-3 feat(gui): Optimize/Apply 領域の操作導線改善
  - 対象: 主要アクションまでのクリック数削減、導線の視認性改善
  - 完了条件: 主要シナリオで操作迷いが低減（チェックリストで pass）

- [ ] P4-4 feat(gui): 状態表示の一元化
  - 対象: 実行中/成功/失敗の表示ルールを統一
  - 完了条件: 表示揺れがなく、失敗時に原因が追える

- [ ] P4-5 test(gui): 回帰テスト強化
  - 対象: `tests/gui/` の既存回帰に Phase4 観点を追加
  - 完了条件: 追加観点がCIで再現可能

- [ ] P4-6 docs/ops: manual gate の同期更新
  - 対象: `docs/manual-validation-gate.md` に Phase4 観点を反映
  - 完了条件: docs と tests の判定項目が一致

- [ ] P4-7 validate: XFCE 実機証跡で最終判定
  - 成果物: JSON / Report / PR Comment / 画面証跡
  - 完了条件: P4-1チェックリスト全項目が pass

## 推奨着手順

1. P4-1（チェックリスト固定）
2. P4-2（MainWindow）
3. P4-3（Optimize/Apply）
4. P4-4（状態表示）
5. P4-5（テスト）
6. P4-6（manual gate）
7. P4-7（実機最終判定）

## ブランチ命名（例）

1. P4-1: `docs/gui-phase4-diff-checklist-20260412`
2. P4-2: `feature/gui-phase4-mainwindow-layout-20260412`
3. P4-3: `feature/gui-phase4-optimize-apply-flow-20260412`
4. P4-4: `feature/gui-phase4-status-feedback-20260412`
5. P4-5: `test/gui-phase4-regression-20260412`
6. P4-6: `docs/gui-phase4-manual-gate-sync-20260412`
7. P4-7: `chore/gui-phase4-xfce-validation-20260412`

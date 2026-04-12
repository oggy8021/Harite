# GUI Phase4 Final Validation Record (2026-04-13)

最終更新: 2026-04-13
対象: Phase4 P4-7 validate

## 判定サマリ

- 判定: deferred (Phase5へ移管)
- 理由: 実機検証と証跡収集は完了したが、Glade再現観点で Optimize/Apply の視覚差分が薄く、A（画面構造）の受け入れ基準を満たせなかったため。見た目/レイアウト再現要求は Phase5 で継続する。
- 対象環境: XFCE

## 前提（P4-1〜P4-6）

- P4-1: 差分チェックリスト定義（完了）
- P4-2: MainWindow レイアウト/導線調整（完了）
- P4-3: Optimize/Apply 導線改善（完了）
- P4-4: 状態表示の一元化（完了）
- P4-5: Phase4 回帰テスト追加（完了）
- P4-6: manual gate 同期更新（完了）

回帰テスト（owner実行）:

- `pytest -q tests/gui/test_phase4_regression.py tests/gui/test_main_window_signals.py`
- 結果: pass

## 最終受け入れ基準（固定）

以下を満たした時点で Phase4 を完了とする。

1. Phase4 UI Diff Checklist の A〜D 必須項目がすべて pass
2. MainWindow / Optimize / Apply の3画面スクリーンショット添付
3. PRコメントに Phase4 テンプレートで記録

## A〜D 実施記録

| 区分 | 内容 | 結果 | Notes |
| --- | --- | --- | --- |
| A | 画面構造（配置、余白、グルーピング、視線導線） | fail | MainWindow は改善したが、Optimize/Apply のレイアウト差分が小さく、旧画面再現の観点で未達。Phase5へ移管。 |
| B | 状態表示（running/success/error の一貫性） | pass | Phase4 で導入した `status_level/status_phase/status_message` で表示揺れなし。 |
| C | 操作効率（入力 -> optimize -> apply dry-run の導線） | pass | 主要シナリオの導線は確認済み。 |
| D | 品質運用（回帰テスト + 実機証跡） | pass | 回帰テスト pass、実機検証ログと成果物フォーマットを確認済み。 |

## 当日実施手順（XFCE）

1. 最新 main を取得し作業ディレクトリ確認
2. GUI 起動して主要シナリオ実施（入力更新 -> optimize -> apply dry-run）
3. 3画面を保存し、`out/manual-validation/` に成果物を集約
4. PRコメントテンプレートを埋めて添付

実行コマンド（XFCE）:

```bash
python -m harite.gui.app --load-ui-prototype --bind-ui-backend --present-ui-window
python scripts/gui_layout_smoke.py --simulate --validate --auto-artifacts --artifact-dir out/manual-validation --pr-number <PR番号> --scope xfce/gui --operator owner --optimize-result pass --apply-dry-run-result pass --apply-do-it-result not-available
```

スクリーンショット保存先（XFCE）:

- `out/manual-validation/pr-<PR番号>-xfce-mainwindow.png`
- `out/manual-validation/pr-<PR番号>-xfce-optimize.png`
- `out/manual-validation/pr-<PR番号>-xfce-apply.png`

## 成果物パス（P4-7）

- JSON: `out/manual-validation/pr-<PR番号>-<os>.json`
- Report: `out/manual-validation/pr-<PR番号>-<os>.md`
- PR Comment: `out/manual-validation/pr-<PR番号>-<os>-pr-comment.md`
- Screenshot MainWindow: `out/manual-validation/pr-<PR番号>-<os>-mainwindow.png`
- Screenshot Optimize: `out/manual-validation/pr-<PR番号>-<os>-optimize.png`
- Screenshot Apply: `out/manual-validation/pr-<PR番号>-<os>-apply.png`

## PRコメント貼付用（Phase4）

```md
### Phase4 UI Diff Checklist
- Scope: [OS/desktop]
- A. 画面構造: pass/fail/not-available
- B. 状態表示: pass/fail/not-available
- C. 操作効率: pass/fail/not-available
- D. 品質運用: pass/fail/not-available
- Notes: [差分・課題・再現手順]

### Manual device validation screenshots
- OS: [Windows|XFCE|macOS]
- MainWindow: attached
- Optimize form: attached
- Apply area: attached
- Notes: [observations]
```

## クローズ条件

- [x] 実機検証と証跡フォーマット確認を完了
- [x] 未達項目（A）を明文化し、Phase5移管方針を確定
- [x] 本ファイルの「判定サマリ」を `deferred (Phase5へ移管)` に更新

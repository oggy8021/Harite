# GUI Phase3 Final Validation Record (2026-04-12)

最終更新: 2026-04-12
対象: Phase3 P7 validate

## 判定サマリ

- 判定: pass (Phase3 P7 完了)
- 理由: 本UI（正式部品配置）で Step1-5 を再実施し、XFCE で pass を確認。JSON/Report/PR Comment と 3 画面スクリーンショットを取得し、最終受け入れ基準 3 点セットを満たした。
- 対象環境: XFCE のみ（Windows は今回対象外）

## 前提（P6までの完了確認）

- P1-P6 は完了。
- GUI回帰観点の test/docs 同期は反映済み。
- 回帰テスト（owner実行）:
  - `pytest -q tests/gui/test_gtk_runtime_backend.py tests/gui/test_main_window_signals.py`
  - 結果: pass (Exit Code: 0)

## 最終受け入れ基準（固定）

以下 3 点セットを満たした時点で Phase3 を完了とする。

1. 本UI（正式部品配置）で Step1-5 がすべて pass
2. MainWindow / Optimize / Apply の3画面スクリーンショット添付
3. PRコメントに標準フォーマットで記録

## Step1-5 実施記録（本UI）

| Step | 内容 | 結果 | Notes |
| --- | --- | --- | --- |
| 1 | `--load-ui-prototype --bind-ui-backend --present-ui-window` で実ウィンドウ表示 | pass | 本UI表示を確認 |
| 2 | MainWindow入力欄編集と値反映 | pass | 入力更新を確認 |
| 3 | Optimize実行（例外なし） | pass | `Traceback` / `Exception` なし |
| 4 | Apply dry-run 実行成功 | pass | dry-run 成功 |
| 5 | MainWindow/Optimize/Apply の3画面取得とPR添付 | pass | `pr-xxx-xfce-mainwindow.png` / `pr-xxx-xfce-optimize.png` / `pr-xxx-xfce-apply.png` |

## 当日実施手順（XFCE）

1. 最新 main（P6まで反映済み）で作業ディレクトリを確認
2. GUI本UIを起動し、Step1-5を順に実施
3. 3画面を保存し、`out/manual-validation/` に成果物を集約
4. PRコメント用テンプレートを埋めて添付

実行コマンド（XFCE）:

```bash
python -m harite.gui.app --load-ui-prototype --bind-ui-backend --present-ui-window
python scripts/gui_layout_smoke.py --simulate --validate --auto-artifacts --artifact-dir out/manual-validation --pr-number <PR番号> --scope xfce/gui --operator owner --optimize-result pass --apply-dry-run-result pass --apply-do-it-result not-available
```

スクリーンショット保存先（XFCE）:

- `out/manual-validation/pr-<PR番号>-xfce-mainwindow.png`
- `out/manual-validation/pr-<PR番号>-xfce-optimize.png`
- `out/manual-validation/pr-<PR番号>-xfce-apply.png`

## 参考実績（fallback 経路）

- 実施日: 2026-04-12
- 環境: XFCE
- 結果: Step1-5 pass
- 位置づけ: 暫定合格（継続運用確認）
- 補足: 本UI最終判定の代替にはしない

## 成果物パス（P7）

- JSON: `out/manual-validation/pr-<PR番号>-<os>.json`
- Report: `out/manual-validation/pr-<PR番号>-<os>.md`
- PR Comment: `out/manual-validation/pr-<PR番号>-<os>-pr-comment.md`
- Screenshot MainWindow: `out/manual-validation/pr-<PR番号>-<os>-mainwindow.png`
- Screenshot Optimize: `out/manual-validation/pr-<PR番号>-<os>-optimize.png`
- Screenshot Apply: `out/manual-validation/pr-<PR番号>-<os>-apply.png`

## PRコメント貼付用（最終版テンプレート）

```md
### Manual device validation
- Scope: [OS/desktop/plugin]
- optimize: pass/fail/not-available
- apply dry-run: pass/fail/not-available
- apply do-it: pass/fail/not-available
- GUI smoke: pass/fail/not-available
- Notes: [error or observation]

### Manual device validation screenshots
- OS: [Windows|XFCE|macOS]
- MainWindow: attached
- Optimize form: attached
- Apply area: attached
- Notes: [observations]
```

## クローズ条件

- [x] 本UI Step1-5 を pass に更新
- [x] 3画面添付を確認
- [x] 本ファイルの「判定サマリ」を `pass` に更新

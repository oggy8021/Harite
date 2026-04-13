# GUI Phase5 P5-7 XFCE Validation Template

最終更新: 2026-04-13
対象: P5-7 validate

## 目的

- XFCE 実機で Phase5 の最終判定を行い、PR 添付物を揃える。
- P5-1 観点（MainWindow / Optimize / Apply / Style）を `pass/warn/fail` で記録する。

## 成果物チェック

- [ ] JSON: `out/manual-validation/pr-<PR番号>-xfce.json`
- [ ] Report: `out/manual-validation/pr-<PR番号>-xfce.md`
- [ ] PR Comment: `out/manual-validation/pr-<PR番号>-xfce-pr-comment.md`
- [ ] Screenshot: `out/manual-validation/pr-<PR番号>-xfce-mainwindow.png`
- [ ] Screenshot: `out/manual-validation/pr-<PR番号>-xfce-optimize.png`
- [ ] Screenshot: `out/manual-validation/pr-<PR番号>-xfce-apply.png`

## Owner 実行コマンド

```bash
python.exe -m pytest -q tests/gui/test_ui_adapter_dispatch.py tests/gui/test_ui_adapter_mapping_validation.py tests/gui/test_main_window_signals.py tests/gui/test_gtk_runtime_backend.py tests/gui/test_phase5_visual_regression.py
```

```bash
python scripts/gui_layout_smoke.py --simulate --validate --auto-artifacts --artifact-dir out/manual-validation --pr-number <PR番号> --scope xfce/gui --operator owner --optimize-result pass --apply-dry-run-result pass --apply-do-it-result not-available
```

## 判定テンプレート

- 対象PR:
- 評価日:
- 評価者: owner
- MainWindow: pass / warn / fail
- Optimize: pass / warn / fail
- Apply: pass / warn / fail
- Style consistency: pass / warn / fail
- Overall: pass / fail
- Notes:

## PR コメント貼り付けテンプレート

```md
### Phase5 visual/manual gate (XFCE)
- MainWindow: pass/warn/fail
- Optimize: pass/warn/fail
- Apply: pass/warn/fail
- Style consistency: pass/warn/fail
- Overall: pass/fail
- Notes: [warn/fail reason and next action]

### Screenshots
- MainWindow: attached (`pr-<PR番号>-xfce-mainwindow.png`)
- Optimize: attached (`pr-<PR番号>-xfce-optimize.png`)
- Apply: attached (`pr-<PR番号>-xfce-apply.png`)
```

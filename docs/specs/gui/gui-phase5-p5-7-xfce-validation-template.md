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

```PowerShell
python.exe -m pytest -q tests/gui/test_ui_adapter_dispatch.py tests/gui/test_ui_adapter_mapping_validation.py tests/gui/test_main_window_signals.py tests/gui/test_gtk_runtime_backend.py tests/gui/test_phase5_visual_regression.py
```

```PowerShell
python scripts/gui_layout_smoke.py --simulate --validate --auto-artifacts --artifact-dir out/manual-validation --pr-number <PR番号> --scope xfce/gui --operator owner --optimize-result pass --apply-dry-run-result pass --apply-do-it-result not-available
```

## 判定テンプレート

- 対象PR: yyy
- 評価日: 2026/4/13-14
- 評価者: owner

### 判定結果

- MainWindow: warn
- Optimize: fail
- Apply: fail
- Style consistency: warn
- Overall: fail

### 詳細メモ

- MainWindow
  - 配置が十字形状になっていません。grid や hbox 相当でボタン類配置を旧 WallpaperOptimizer に寄せてください。
  - 将来アイコン化を踏まえても並び順は維持してください。
  - 下方 `中央2列目イメージ` に記述します。
  - glade のように grid 化できない場合は、きれいに並べる代替手法を提案してください。
  - GUI 版は本来、パスを入力させるフォームは不要です。ファイル選択ダイアログでパス指定する想定です。
  - 仮配置の場合は、レイアウト確認の外に置いてください。
  - `entPathL`, `entPathR` は `OpenL`, `OpenR` で取得した画像パスを表示する想定だったことを再確認しました。
  - 母体プログラムを explain し、確認してください。
  - 最終的に Core などに渡す際に 1 つへまとめることは問題ありません。
  - watch 用の左右画像向けパスは `srcdirL`, `srcdirR` で指定します。未指定も許容します。
  - 実施先PR: P5-9 `feat(gui): watch 導線の実処理導入（srcdirL/srcdirR）`

- Optimize
  - `Optimize result: handler-missing`
  - ステータスエリアも `handler-missing`。
  - エラーメッセージは `Error:handler not connected`。

- Apply
  - Optimize が fail のため実行不可。

- Style consistency
  - ボタン群の配置意図が旧版ルールと不一致で、視覚ルール説明が弱い。

### 中央2列目イメージ

|  　　　　    [tglUpperL]               |                 [tglUpperR]              |
|  [tglPushLeftL][openL][tglPushRightL] |     [tglPushLeftR][openR][tglPushRightR]   |
|             [tglLowerL]               |                 [tglLowerR]              |
|          [entPathL][clrL]             |              [entPathR][clrR]            |
|                             (radFixed) (radNoFixed)                              |

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

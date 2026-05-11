# GUI Phase6 Final Validation Record Template

最終更新: 2026-04-18
対象: Phase6 closeout validate

## 位置づけ

- 本書は Phase6 を閉じるための実施記録テンプレートである。
- [docs/manual-validation-gate.md](docs/manual-validation-gate.md) の運用ルールに従い、XFCE 実機確認結果、固定 GUI 回帰結果、観察メモを 1 つへまとめる。
- ルール本文は [docs/manual-validation-gate.md](docs/manual-validation-gate.md) を正本とし、本書はその実施結果だけを記録する。

## 判定サマリ

- 判定: pass/fail/deferred
- 理由: [Phase6 を閉じる判断理由]
- 対象環境: XFCE / Windows / macOS / not-available
- 対象PRまたはブランチ: [number or branch]

## 前提（Phase6 完了確認）

- [docs/specs/gui/gui-phase6-planning.md](docs/specs/gui/gui-phase6-planning.md) の出口条件を確認した。
- [docs/specs/gui/gui-phase7-product-alignment-planning.md](docs/specs/gui/gui-phase7-product-alignment-planning.md) を次フェーズ準備成果物として確認した。
- current runtime は glade prototype 前提を撤去済みである。
- `Save` は `Save As` chooser 主体、`Apply` は即時実行、`Save confirm` / `Save cancel` は常設しない前提である。

固定 GUI 回帰:

- コマンド:
  - `python.exe -m pytest -q tests/gui/test_main_window_signals.py tests/gui/test_gtk_runtime_backend.py tests/gui/test_phase5_visual_regression.py tests/gui/test_ui_adapter_backend_connect.py tests/gui/test_app_entrypoint.py`
- 結果: pass/fail

## 最終受け入れ基準（Phase6）

以下を満たした時点で Phase6 を close とする。

1. XFCE 実機で current GUI を起動し、MainWindow / Save As or Optimize / Apply immediate の主要導線を確認している。
2. 固定 GUI 回帰が pass している。
3. MainWindow / Optimize / Apply の 3 画面スクリーンショットが揃っている。
4. MainWindow の初見印象と、Phase6 を閉じてよいかの判断理由が記録されている。
5. Phase7 を product alignment フェーズとして開始してよい前提が確認されている。

## 実施記録（Phase6 closeout）

| Step | 内容 | 結果 | Notes |
| --- | --- | --- | --- |
| 1 | 固定 GUI 回帰実行 | pass/fail/not-available | [pytest 結果] |
| 2 | `python -m harite.gui.app --bind-ui-backend --present-ui-window` で実ウィンドウ表示 | pass/fail/not-available | [起動可否、display 条件] |
| 3 | MainWindow 入力欄編集と状態更新 | pass/fail/not-available | [反映状況] |
| 4 | `Save As` または `Optimize` 導線 | pass/fail/not-available | [`Traceback` / `Exception` の有無] |
| 5 | `Apply` 即時実行導線 | pass/fail/not-available | [実機変更有無、理由] |
| 6 | watch 導線確認（変更時のみ） | pass/fail/not-available | [srcdir / interval / start-stop] |
| 7 | MainWindow / Optimize / Apply スクリーンショット取得 | pass/fail/not-available | [添付パス] |

## MainWindow 初見印象

- 第一印象: [見た目、配置、違和感、良い点]
- 操作感: [入力 -> Save As or Optimize -> Apply の流れ]
- 「間に合わせではない」判断: pass/fail/deferred
- 理由: [Phase6 の出口として許容できるか]

## 当日実施手順（XFCE）

1. 作業ツリーと対象ブランチを確認する。
2. 固定 GUI 回帰を実行し、結果を記録する。
3. `python -m harite.gui.app --bind-ui-backend --present-ui-window` を起動する。
4. MainWindow 入力更新 -> `Save As` または `Optimize` -> `Apply` の順で確認する。
5. MainWindow / Optimize / Apply の 3 画面を保存する。
6. 必要なら `scripts/gui_layout_smoke.py` で成果物を生成し、PR コメントまたはメモへ転記する。

実行コマンド（XFCE）:

```bash
python.exe -m pytest -q tests/gui/test_main_window_signals.py tests/gui/test_gtk_runtime_backend.py tests/gui/test_phase5_visual_regression.py tests/gui/test_ui_adapter_backend_connect.py tests/gui/test_app_entrypoint.py
python -m harite.gui.app --bind-ui-backend --present-ui-window
python scripts/gui_layout_smoke.py --simulate --validate --auto-artifacts --artifact-dir out/manual-validation --pr-number <PR番号> --scope xfce/gui --operator owner --optimize-result pass --apply-result pass
```

## スクリーンショット保存先

- `out/manual-validation/pr-<PR番号>-xfce-mainwindow.png`
- `out/manual-validation/pr-<PR番号>-xfce-optimize.png`
- `out/manual-validation/pr-<PR番号>-xfce-apply.png`

## 成果物パス

- JSON: `out/manual-validation/pr-<PR番号>-<os>.json`
- Report: `out/manual-validation/pr-<PR番号>-<os>.md`
- PR Comment: `out/manual-validation/pr-<PR番号>-<os>-pr-comment.md`
- Screenshot MainWindow: `out/manual-validation/pr-<PR番号>-<os>-mainwindow.png`
- Screenshot Optimize: `out/manual-validation/pr-<PR番号>-<os>-optimize.png`
- Screenshot Apply: `out/manual-validation/pr-<PR番号>-<os>-apply.png`

## PRコメント貼付用（Phase6 closeout）

```md
### Manual device validation
- Scope: xfce/gui
- optimize: pass/fail/not-available
- apply: pass/fail/not-available
- GUI smoke: pass/fail/not-available
- Notes: [MainWindow impression, error, or observation]

### Manual device validation screenshots
- OS: XFCE
- MainWindow: attached
- Optimize form: attached
- Apply area: attached
- Notes: [observations]
```

## クローズ条件

- [ ] 固定 GUI 回帰を記録した
- [ ] 実ウィンドウ起動結果を記録した
- [ ] MainWindow 初見印象を記録した
- [ ] 3 画面スクリーンショットを確認した
- [ ] 本ファイルの「判定サマリ」を更新した
- [ ] Phase7 開始可否の判断を追記した

# 実機検証ゲート（軽量運用）

最終更新: 2026-04-18

## 目的

- CI だけでは拾いにくい実機依存の挙動を、毎サイクルで最小コストに確認する。
- 「小PR -> CI通過 -> 実機確認 -> squash merge」の順序を固定化する。

## 運用タイミング

- 対象: 壁紙適用、GUI操作、表示環境依存（XFCE/Windows/macOS）に触れる PR。
- 実施者: オーナー（実機保持者）。
- 実施時点: CI green 後、merge 前。

## 対象OSマトリクス（M2運用）

各PRで利用可能な環境のみ実施し、未実施環境は `not-available` を明示する。

| OS/環境 | optimize | apply dry-run | apply do-it | GUI表示確認 | 備考 |
| --- | --- | --- | --- | --- | --- |
| Windows | 必須 | 必須 | 任意 | GUI変更時は必須 | 既定確認環境 |
| XFCE/Linux | 利用可能時必須 | 利用可能時必須 | 任意 | GUI変更時は推奨 | display server依存 |
| macOS | 利用可能時必須 | 利用可能時必須 | 任意 | GUI変更時は推奨 | plugin導入状況に依存 |

結果記録ルール:

- `pass` / `fail` / `not-available` の3値で記録する。
- `fail` は再現手順を Notes に1行以上で残す。
- `not-available` は理由（端末なし、plugin未導入など）を Notes に残す。
- `GUI Manual Validation Report` の Result matrix では、`optimize` / `apply dry-run` / `apply do-it` の Notes 列は `manual declaration` として出力される（手動記録であることを明示）。

## 最小ゲート（3分）

1. optimize の正常系

- コマンド例:

```bash
harite optimize --input ./imgs --resolution 1920x1080 --output ./out
```

- 期待:

  - 出力画像が生成される。
  - エラー終了しない。

1. apply dry-run の安全確認

- コマンド例:

```bash
harite apply --plugin windows --file ./out/wallpaper_001.jpg
```

- 期待:

  - dry-run として成功する。
  - 実機設定は変更されない。

1. apply do-it の実機確認（必要時のみ）

- コマンド例:

```bash
harite apply --plugin windows --file ./out/wallpaper_001.jpg --do-it
```

- 期待:

  - 壁紙が実際に切り替わる。
  - 失敗時はロールバック手順を実施する。

## GUI 変更が入る場合の追加確認（2分）

注記:

- current GUI の実機確認は XFCE 実ウィンドウを正本とする。
- `--load-ui-prototype` 前提は撤去済みであり、GUI 起動は current runtime backend に一本化されている。
- GUI の `Save` は `Save As` chooser 主体、`Apply` は即時実行であり、`Save confirm` / `Save cancel` の常設 UI は存在しない。

実ウィンドウ起動（GTK 利用可能環境）:

```bash
python -m harite.gui.app --bind-ui-backend --present-ui-window
```

- 上記でウィンドウ表示できる環境では、スクリーンショット 3 枚取得運用へ進む。
- GTK / display が使えない環境では GUI 実ウィンドウ確認を `not-available` とし、固定 GUI 回帰と smoke 補助コマンドで代替確認する。
- headless 補助は owner の XFCE 実機承認の代替ではない。

### GUI 最小実施セット（current）

1. `python -m harite.gui.app --bind-ui-backend --present-ui-window` を起動し、実ウィンドウが表示されることを確認する。
2. MainWindow で入力欄を編集し、状態更新が反映されることを確認する。
3. `Save As` または `Optimize` 導線を実行し、`Traceback` / `Exception` が残らないことを確認する。
4. `Apply` を実行し、即時適用として完了することを確認する。実機変更を避ける場合は `not-available` とし、Notes に理由を残す。
5. MainWindow / Optimize / Apply の 3 画面スクリーンショットを PR コメントへ添付する。

補足:

- watch 導線に変更がある PR では、srcdir 選択、interval 更新、start/stop まで追加で確認する。
- 実機起動できない場合でも、固定 GUI 回帰が green であることは merge 前提として残す。

### 補助コマンド

headless smoke（current runtime の direct simulation）:

```bash
python scripts/gui_layout_smoke.py --simulate --validate --scope windows/gui --out-file ./out/gui-layout.json --markdown-out ./out/gui-layout.md --print-markdown
```

- 期待:
  - 終了コード `0`（検証成功）
  - `./out/gui-layout.json` に `validation.ok: true` が記録される
  - `./out/gui-layout.md` の `Failed checks` が `none` になる

成果物一式を自動生成する場合:

```bash
python scripts/gui_layout_smoke.py --simulate --validate --auto-artifacts --artifact-dir out/manual-validation --pr-number 146 --scope xfce/gui --operator owner --optimize-result pass --apply-result pass
```

スクリーンショット添付を必須化する場合:

```bash
python scripts/gui_layout_smoke.py --simulate --validate --auto-artifacts --artifact-dir out/manual-validation --pr-number 146 --scope xfce/gui --report-out out/manual-validation/pr-146-xfce.md --require-screenshots --screenshot-mainwindow out/manual-validation/pr-146-xfce-mainwindow.png --screenshot-optimize out/manual-validation/pr-146-xfce-optimize.png --screenshot-apply out/manual-validation/pr-146-xfce-apply.png
```

厳格モード:

```bash
python scripts/gui_layout_smoke.py --simulate --validate --strict-manual --artifact-dir out/manual-validation --pr-number 146 --scope xfce/gui --optimize-result pass --apply-result pass
```

### ウィンドウ別チェックリスト（実機確認、推奨 2 分）

- **MainWindow（メイン）**: タイトルが表示されること、主要ボタン（Optimize、Apply）が存在すること、入力欄が表示され値が編集可能であること。スクリーンショットを1枚取得。
- **Optimize フォーム**: 入力パス欄、解像度、出力先、プラグイン選択が表示され、`Save As` / `Optimize` が例外なく進むことを確認する。
- **Apply 領域**: 最新の保存ファイルがリストされ、`Apply` が即時実行として成功することを確認する。
- **エラーダイアログ / ログ表示**: エラー発生時にダイアログが閉じられること、`last_error` がクリアされることを手動で確認。

手順:

1. `python -m harite.gui.app --bind-ui-backend --present-ui-window` を起動し、上記ウィンドウを目視で確認してスクリーンショットを取る。
2. 入力変更 -> `Save As` または `Optimize` 実行 -> `Apply` 実行の順で確認する。
3. 実行ログに `Traceback` や `Exception` が残らないことを確認し、スクリーンショットを PR コメントに添付する。

- `--optimize-result` / `--apply-result` は `pass|fail|not-available` を使う。
- `--strict-manual` は `--auto-artifacts` + `--require-screenshots` + `--verify-screenshot-files` をまとめて有効化する。

スクリーンショット添付フォーマット（PR コメント貼り付け用）:

```md
### Manual device validation screenshots
- OS: [Windows|XFCE|macOS]
- MainWindow: attached
- Optimize form: attached
- Apply area: attached
- Notes: [observations]
```

## 成果物の保存ルール（M2/M3共通）

PRごとに以下の命名で保存する。

- JSON: `out/manual-validation/pr-<PR番号>-<os>.json`
- Markdown: `out/manual-validation/pr-<PR番号>-<os>.md`
- Screenshot: `out/manual-validation/pr-<PR番号>-<os>-<view>.png`

`<view>` は `mainwindow` / `optimize` / `apply` を使う。

## CLI 0.1.1 宿題チェック（オーナー用）

- [ ] wheel からのインストールで `harite optimize --help` が動く
- [ ] wheel からのインストールで `harite apply --help` が動く
- [ ] dry-run が既定であることを再確認した
- [ ] 実機で `--do-it` を1回だけ確認した（必要な環境のみ）
- [ ] 問題があれば再現手順を Issue に記録した

## 記録テンプレート（PRコメント貼り付け用）

```md
### Manual device validation
- Scope: [OS/desktop/plugin]
- optimize: pass/fail
- apply: pass/fail/not-available
- GUI smoke (if changed): pass/fail
- Notes: [error or observation]
```

## XFCE 実施メモ雛形（current）

owner が XFCE 実機確認を行うときは、次をそのままメモまたは PR コメント下書きとして使ってよい。

```md
### XFCE GUI validation memo
- Date: [YYYY-MM-DD]
- Operator: owner
- Scope: xfce/gui
- PR: [number]
- Fixed regression:
  - `python.exe -m pytest -q tests/gui/test_main_window_signals.py tests/gui/test_gtk_runtime_backend.py tests/gui/test_phase5_visual_regression.py tests/gui/test_ui_adapter_backend_connect.py tests/gui/test_app_entrypoint.py`
  - Result: pass/fail
- Window launch:
  - `python -m harite.gui.app --bind-ui-backend --present-ui-window`
  - Result: pass/fail/not-available
- MainWindow input update: pass/fail
- Save As or Optimize flow: pass/fail
- Apply immediate flow: pass/fail/not-available
- Watch flow (if changed): pass/fail/not-available
- Screenshots:
  - MainWindow: [attached/path]
  - Optimize: [attached/path]
  - Apply: [attached/path]
- Notes: [observations, repro, not-available reason]
```

短い PR コメントへ落とす場合:

```md
### Manual device validation
- Scope: xfce/gui
- optimize: pass/fail
- apply: pass/fail/not-available
- GUI smoke: pass/fail
- Notes: [observations]
```

## merge 判定

- 実機対象のPRは、上記テンプレートの `pass` 記録がある場合に merge 可。
- `fail` の場合は merge 保留。修正PRを先行する。

## 現行 GUI 回帰（P6）

current runtime の固定 GUI 回帰は、少なくとも次を green に保つ。

- `tests/gui/test_main_window_signals.py`
- `tests/gui/test_gtk_runtime_backend.py`
- `tests/gui/test_phase5_visual_regression.py`
- `tests/gui/test_ui_adapter_backend_connect.py`
- `tests/gui/test_app_entrypoint.py`

Owner 実行コマンド（固定回帰）:

```bash
python.exe -m pytest -q tests/gui/test_main_window_signals.py tests/gui/test_gtk_runtime_backend.py tests/gui/test_phase5_visual_regression.py tests/gui/test_ui_adapter_backend_connect.py tests/gui/test_app_entrypoint.py
```

受け入れ基準:

- runtime fallback でのラベル規約（Status/Error/Optimize result/Apply target/Watch）が固定されている。
- current handler 名での dispatch / bind が維持され、legacy signal 名へ戻っていない。
- handler 未接続時に `handler-missing` が表示され、例外クラッシュしない。
- 本項目の確認結果が PR 本文またはコメントに記録されている。

## 履歴参照

以下は current gate ではなく、履歴確認や差分読解のための参照先として扱う。

- `docs/specs/gui/gui-phase4-diff-checklist.md`
- `docs/specs/gui/gui-phase5-visual-checklist.md`
- `docs/specs/gui/gui-phase6-planning.md`
- `docs/gui-phase3-final-validation-record-20260412.md`
- `docs/gui-phase4-final-validation-record-20260413.md`

## 参照

- docs/release-readiness-checklist.md
- docs/release-delivery.md
- README.md

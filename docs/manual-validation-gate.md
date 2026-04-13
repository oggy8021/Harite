# 実機検証ゲート（軽量運用）

最終更新: 2026-04-13

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

- 現状の GUI はプレースホルダ実装のため、起動時はウィンドウ表示ではなくコンソールに状態を表示する。

実ウィンドウ起動（GTK 利用可能環境）:

```bash
python -m harite.gui.app --load-ui-prototype --bind-ui-backend --present-ui-window
```

- 上記でウィンドウ表示できる環境では、スクリーンショット 3 枚取得運用へ進む。
- 表示できない場合は従来どおり暫定運用（`--auto-artifacts` + Notes 記録）を適用する。

補足（2026-04-12 運用更新）:

- legacy glade（`<glade-interface>`）を runtime で直接読めない環境では、GTK runtime fallback window を使用して Step1-5 を実施してよい。
- fallback window での Step2-4 判定は、入力更新・Optimize・Apply(dry-run) のステータス表示で行う。
- 本UI（正式部品配置）へ移行後は、同じ 5 操作を本UI上で再確認する。
- fallback window での pass は暫定合格として扱い、Phase 3 最終完了判定は本UI（正式部品配置）での実施結果を優先する。

補足（2026-04-13, P5-3 反映）:

- fallback window では Save/Optimize を分離運用する。
- `Save` は SaveDialog を開く操作であり、生成は `Save confirm`（`on_btnOpenSave_clicked`）経由で続行する。
- SaveDialog の confirm は保存先選択後のみ活性化され、未選択時は `path-required` として確定を拒否する。
- SaveDialog の confirm/cancel は dialog open 中のみ有効で、closed 状態呼び出しは `ignored-closed` として無視する。

### Phase 3 完了判定の最小操作セット（固定）

以下 5 操作を 1 セッションで実施し、すべて `pass` であることを Phase 3 の実機受け入れ基準とする。

1. GUI を `--load-ui-prototype --bind-ui-backend --present-ui-window` で起動し、実ウィンドウが表示される。
2. MainWindow で入力欄を編集し、値更新が反映される（空入力ではない）。
3. Optimize 操作を実行し、例外なく完了する（`Traceback` / `Exception` が残らない）。
4. Apply 領域で dry-run を実行し、成功する。
5. MainWindow / Optimize / Apply の 3 画面スクリーンショットを保存し、PR コメントへ添付する。

補足:

- 実行環境はオーナーの Linux Mint (Xfce) 現行環境を基準とする。
- 実ウィンドウが出せない時期は暫定運用を適用し、Phase 3 完了判定には使わない。

### Phase 3 UI品質収束の判定ルール（2026-04-12 確定）

- M2/M3 の運用面（成果物生成・PR添付）が達成済みでも、`M2-ui` / `M3-ui` が未達の間は Phase 3 を未完了として扱う。
- 最終完了条件は本UI（正式部品配置）での Step1-5 pass + 3画面添付 + PR記録の3点セット。
- fallback window は継続運用の補助手段として扱い、最終完了判定の代替にはしない。

### 暫定運用（GUIプレースホルダ期間）

- `python -m harite.gui.app` で実ウィンドウが表示されない間は、3枚スクリーンショット取得を `not-available` として扱う。
- この期間は `--strict-manual` を既定手順にしない（`--require-screenshots` / `--verify-screenshot-files` が有効になり失敗するため）。
- 代わりに `--auto-artifacts` で JSON/Markdown/PRコメント成果物を生成し、Notes に「GUI はプレースホルダ実装のため画面取得未実施」を明記する。

暫定コマンド例（XFCE）:

```bash
python scripts/gui_layout_smoke.py --simulate --validate --auto-artifacts --artifact-dir out/manual-validation --pr-number 146 --scope xfce/gui --operator owner --optimize-result pass --apply-dry-run-result pass --apply-do-it-result not-available
```

- 実ウィンドウ実装後に `--strict-manual` 運用へ戻す。

### ウィンドウ別チェックリスト（実機確認、推奨 2 分）

- **MainWindow（メイン）**: タイトルが表示されること、主要ボタン（Optimize、Apply）が存在すること、入力欄が表示され値が編集可能であること。スクリーンショットを1枚取得。
- **Optimize フォーム**: 入力パス欄、解像度、出力先、プラグイン選択が表示され、`optimize` を実行できる（dry-run 環境で成功すること）。実行ログに例外や Traceback が含まれていないことを確認。
- **Apply 領域**: 最新の保存ファイルがリストされる、`apply dry-run` が成功すること。必要なら `apply --do-it` を一度だけ実行して挙動を確認（実機でのみ）。
- **エラーダイアログ / ログ表示**: エラー発生時にダイアログが閉じられること、`last_error` がクリアされることを手動で確認。

手順:

1. `python -m harite.gui.app --load-ui-prototype --bind-ui-backend --present-ui-window` を起動し、上記ウィンドウを目視で確認してスクリーンショットを取る。
2. 入力変更 -> `harite optimize` 実行（あるいは GUI 経由の optimize）-> `harite apply --plugin <os> --file <file>` の dry-run を確認。
3. 実行ログに `Traceback` や `Exception` が残らないことを確認し、スクリーンショットを PR コメントに添付する。

補助（推奨, headless 検証）:

```bash
python scripts/gui_layout_smoke.py --simulate --validate --scope windows/gui --out-file ./out/gui-layout.json --markdown-out ./out/gui-layout.md --print-markdown
```

- 期待:
  - 終了コード `0`（検証成功）
  - `./out/gui-layout.json` に `validation.ok: true` が記録される
  - `./out/gui-layout.md` の `Failed checks` が `none` になる

  補助（推奨, 実機結果の成果物一式を自動生成）:

  ```bash
  python scripts/gui_layout_smoke.py --simulate --validate --auto-artifacts --artifact-dir out/manual-validation --pr-number 140 --scope windows/gui --operator owner --optimize-result pass --apply-dry-run-result pass --apply-do-it-result not-available
  ```

  実機確認でスクリーンショット添付を必須化する場合:

  ```bash
  python scripts/gui_layout_smoke.py --simulate --validate --auto-artifacts --artifact-dir out/manual-validation --pr-number 140 --scope windows/gui --report-out out/manual-validation/pr-140-windows.md --require-screenshots --screenshot-mainwindow out/manual-validation/pr-140-windows-mainwindow.png --screenshot-optimize out/manual-validation/pr-140-windows-optimize.png --screenshot-apply out/manual-validation/pr-140-windows-apply.png
  ```

  - いずれかのスクリーンショットパスが未指定の場合は終了コード `3` で失敗する。
  - `--verify-screenshot-files` を付けると、指定パスの実ファイルが存在しない場合は終了コード `4` で失敗する。
  - スクリーンショットパスを指定した場合、`pr-<PR>-<os>-pr-comment.md` にも `### Screenshots` セクションが自動で出力される。
  - `--require-screenshots` / `--verify-screenshot-files` は report 出力だけでなく pr-comment 出力時にも同様に適用される。

  厳格モード（推奨、運用確定時）:

  ```bash
  python scripts/gui_layout_smoke.py --simulate --validate --strict-manual --artifact-dir out/manual-validation --pr-number 140 --scope windows/gui --optimize-result pass --apply-dry-run-result pass --apply-do-it-result not-available
  ```

  - `--strict-manual` は `--auto-artifacts` + `--require-screenshots` + `--verify-screenshot-files` をまとめて有効化する。
  - 実ウィンドウが表示される実装フェーズで有効化する（プレースホルダ期間は暫定運用を優先）。

  - `--optimize-result` / `--apply-dry-run-result` / `--apply-do-it-result` は `pass|fail|not-available` を使う。
  - 旧表記 `n/a`, `na`, `n/a (manual)`, `n/a (if executed)` は `not-available` として扱われる。

  - 生成されるファイル:
    - `out/manual-validation/pr-140-windows.json`
    - `out/manual-validation/pr-140-windows.md`
    - `out/manual-validation/pr-140-windows-pr-comment.md`
    - `out/manual-validation/pr-140-windows-smoke.md`

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
- apply dry-run: pass/fail
- apply do-it: pass/fail (if executed)
- GUI smoke (if changed): pass/fail
- Notes: [error or observation]
```

## merge 判定

- 実機対象のPRは、上記テンプレートの `pass` 記録がある場合に merge 可。
- `fail` の場合は merge 保留。修正PRを先行する。

## Phase 3 再開時の完了条件（M2-3b / M3-2b）

- 1環境以上で、次の3成果物を同じ `PR番号` と `os` で生成する。
  - `out/manual-validation/pr-<PR番号>-<os>.json`
  - `out/manual-validation/pr-<PR番号>-<os>.md`
  - `out/manual-validation/pr-<PR番号>-<os>-pr-comment.md`
- PR本文またはコメントに `pr-comment.md` の内容を添付する。
- `not-available` を使った項目は Notes に理由を明記する。
- `docs/specs/gui-phase3-tasklist.md` の `M2-3b` / `M3-2b` を `[x]` に更新する。

## 実施実績（2026-04-12, XFCE）

- Step1: pass（実ウィンドウ表示）
- Step2: pass（入力更新で `Input updated`）
- Step3: pass（`Optimize ok`）
- Step4: pass（`Apply dry-run ok`）
- Step5: pass（MainWindow/Optimize/Apply の3画面を添付）
- Notes: GTK runtime fallback window で実施。`Traceback` / `Exception` は未発生。

## P6 同期チェック（test/docs）

Phase 3 P6 では、GUI の表示品質だけでなく signal-to-handler 経路の回帰観点を docs と tests で同期する。

- signal 再監査対象:
  - `on_entPath_insert_text`（入力変更時の状態更新）
  - `on_btnSave_clicked`（SaveDialog open 操作、生成は直接実行しない）
  - `on_btnOpenSave_clicked` / `on_btnCancelSave_clicked`（SaveDialog confirm/cancel の open/close とガード）
  - `on_btnOptimize_clicked`（Optimize 実行時の running/ok/failed/error）
  - `on_btnSetWall_clicked`（Apply 実行時の running/dry-run-ok/dry-run-failed/error）
- ローカル検証コマンド:

```bash
python.exe -m pytest -q tests/gui/test_ui_adapter_dispatch.py tests/gui/test_ui_adapter_mapping_validation.py tests/gui/test_main_window_signals.py tests/gui/test_gtk_runtime_backend.py
```

- 受け入れ基準:
  - runtime fallback でのラベル規約（Status/Error/Optimize result/Apply target）が固定されている。
  - handler 未接続時に `handler-missing` が表示され、例外クラッシュしない。
  - 本項目の確認結果が PR 本文またはコメントに記録されている。

## Phase 5 manual gate 同期（P5-6）

対象:

- `docs/specs/gui/gui-phase5-visual-checklist.md`
- `tests/gui/test_phase5_visual_regression.py`
- `tests/gui/test_ui_adapter_dispatch.py`
- `tests/gui/test_ui_adapter_mapping_validation.py`
- `tests/gui/test_main_window_signals.py`
- `tests/gui/test_gtk_runtime_backend.py`

判定ルール:

- MainWindow / Optimize / Apply / スタイル統一を `pass/warn/fail` で記録する。
- 総合判定は 4 観点すべて `pass` のときのみ `pass`。
- `warn` は理由と次アクション（P5-7 で確認する項目）を Notes に残す。
- `fail` が 1 つでもある場合は merge 保留とする。

Owner 実行コマンド（固定回帰 + P5-5）:

```bash
python.exe -m pytest -q tests/gui/test_ui_adapter_dispatch.py tests/gui/test_ui_adapter_mapping_validation.py tests/gui/test_main_window_signals.py tests/gui/test_gtk_runtime_backend.py tests/gui/test_phase5_visual_regression.py
```

実機証跡（P5-7 へ引き継ぐ最小セット）:

- MainWindow / Optimize / Apply の 3 画面スクリーンショット
- 判定テンプレート記入済みメモ（`pass/warn/fail` と備考）
- PR コメントに判定結果と差分要点を記録

PRコメント追記テンプレート（Phase5）:

```md
### Phase5 visual/manual gate
- MainWindow: pass/warn/fail
- Optimize: pass/warn/fail
- Apply: pass/warn/fail
- Style consistency: pass/warn/fail
- Overall: pass/fail
- Notes: [warn/fail reason and next action]
```

## 参照

- docs/release-readiness-checklist.md
- docs/release-delivery.md
- README.md

## Phase 4 UI差分判定ゲート（P4-6 同期）

対象:

- `docs/specs/gui/gui-phase4-diff-checklist.md` の A〜D 必須項目
- `tests/gui/test_phase4_regression.py`（Phase4 回帰）

判定ルール:

- A〜D は `pass/fail/not-available` で記録する。
- 最終受け入れは A〜D の必須項目がすべて `pass`。
- `fail` は再現手順を Notes に 1 行以上記録する。
- `not-available` は理由を Notes に明記する。

Phase4 の最小実施セット（手動）:

1. GUI起動（実ウィンドウ表示または runtime fallback）
2. 入力更新 -> Optimize 実行
3. Apply dry-run 実行
4. 状態表示（running/success/error）を確認
5. 画面証跡（MainWindow/Optimize/Apply）を添付

推奨テスト（オーナー実行）:

```bash
pytest -q tests/gui/test_phase4_regression.py tests/gui/test_main_window_signals.py
```

PRコメント追記テンプレート（Phase4）:

```md
### Phase4 UI Diff Checklist
- Scope: [OS/desktop]
- A. 画面構造: pass/fail/not-available
- B. 状態表示: pass/fail/not-available
- C. 操作効率: pass/fail/not-available
- D. 品質運用: pass/fail/not-available
- Notes: [差分・課題・再現手順]
```

備考:

- Phase4 では UI調整PRごとに上記テンプレートを添付する。
- `docs/specs/gui/gui-phase4-diff-checklist.md` と本セクションの項目差分が出た場合は、先に docs を同期してから実装を進める。

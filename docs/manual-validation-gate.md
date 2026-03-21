# 実機検証ゲート（軽量運用）

最終更新: 2026-03-21

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

### ウィンドウ別チェックリスト（実機確認、推奨 2 分）

- **MainWindow（メイン）**: タイトルが表示されること、主要ボタン（Optimize、Apply）が存在すること、入力欄が表示され値が編集可能であること。スクリーンショットを1枚取得。
- **Optimize フォーム**: 入力パス欄、解像度、出力先、プラグイン選択が表示され、`optimize` を実行できる（dry-run 環境で成功すること）。実行ログに例外や Traceback が含まれていないことを確認。
- **Apply 領域**: 最新の保存ファイルがリストされる、`apply dry-run` が成功すること。必要なら `apply --do-it` を一度だけ実行して挙動を確認（実機でのみ）。
- **エラーダイアログ / ログ表示**: エラー発生時にダイアログが閉じられること、`last_error` がクリアされることを手動で確認。

手順:

1. `python -m harite.gui.app` を起動し、上記ウィンドウを目視で確認してスクリーンショットを取る。
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

## 参照

- docs/release-readiness-checklist.md
- docs/release-delivery.md
- README.md

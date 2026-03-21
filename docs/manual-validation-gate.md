# 実機検証ゲート（軽量運用）

最終更新: 2026-03-21

## 目的

- CI だけでは拾いにくい実機依存の挙動を、毎サイクルで最小コストに確認する。
- 「小PR -> CI通過 -> 実機確認 -> squash merge」の順序を固定化する。

## 運用タイミング

- 対象: 壁紙適用、GUI操作、表示環境依存（XFCE/Windows/macOS）に触れる PR。
- 実施者: オーナー（実機保持者）。
- 実施時点: CI green 後、merge 前。

## 最小ゲート（3分）

1. optimize の正常系
- コマンド例:
```bash
harite optimize --input ./imgs --resolution 1920x1080 --output ./out
```
- 期待:
  - 出力画像が生成される。
  - エラー終了しない。

2. apply dry-run の安全確認
- コマンド例:
```bash
harite apply --plugin windows --file ./out/wallpaper_001.jpg
```
- 期待:
  - dry-run として成功する。
  - 実機設定は変更されない。

3. apply do-it の実機確認（必要時のみ）
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

1. GUI起動
```bash
python -m harite.gui.app
```
2. 入力変更 -> optimize 実行 -> apply dry-run
3. 実行ログに失敗メッセージが残っていないこと
4. 併せて `pytest -q tests/test_gui_phase1.py` が成功すること

## CLI 0.1.1 宿題チェック（オーナー用）

- [ ] wheel からのインストールで `harite optimize --help` が動く
- [ ] wheel からのインストールで `harite apply --help` が動く
- [ ] dry-run が既定であることを再確認した
- [ ] 実機で `--do-it` を1回だけ確認した（必要な環境のみ）
- [ ] 問題があれば再現手順を Issue に記録した

## 記録テンプレート（PRコメント貼り付け用）

```md
### Manual device validation
- Scope: <OS/desktop/plugin>
- optimize: pass/fail
- apply dry-run: pass/fail
- apply do-it: pass/fail (if executed)
- GUI smoke (if changed): pass/fail
- Notes: <error or observation>
```

## merge 判定

- 実機対象のPRは、上記テンプレートの `pass` 記録がある場合に merge 可。
- `fail` の場合は merge 保留。修正PRを先行する。

## 参照

- docs/release-readiness-checklist.md
- docs/release-delivery.md
- README.md

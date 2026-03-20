# XFCE 切り戻し手順（Playbook）

最終更新: 2026-03-20

## 目的

- `harite apply --do-it` 実行後に想定外の表示になった場合、既知の良い画像へ安全に戻す。
- ログ取得と復帰確認を同時に行い、再発時の調査情報を残す。

## 前提

- XFCE 環境で `xfconf-query` が利用可能。
- 既知の良い画像（絶対パス）が 1 つ以上ある。
- `harite` を実行できる Python 環境が有効。

## 事前準備

1. 既知の良い画像の絶対パスを確認する。
2. 現在の XFCE プロパティを退避する。

```bash
xfconf-query -c xfce4-desktop -l > xfconf-props-before.txt
xfconf-query -c xfce4-desktop -l -v > xfconf-values-before.txt
```

## 切り戻し手順

1. まず dry-run で適用対象コマンドを確認する。

```bash
python -m harite.cli apply --plugin linux --file /abs/path/to/known-good.jpg
```

1. 問題なければ実適用を実行する。

```bash
python -m harite.cli apply --plugin linux --file /abs/path/to/known-good.jpg --do-it
```

1. 適用後の XFCE プロパティを取得する。

```bash
xfconf-query -c xfce4-desktop -l -v > xfconf-values-after.txt
```

1. 目視で壁紙が復帰したことを確認する。

補助スクリプト（推奨）

手動実行をまとめたい場合は、以下で切り戻し確認 + 短時間 smoke を一括実行できます。

```bash
scripts/run_xfce_followup.sh \
  --known-good /abs/path/to/known-good.jpg \
  --smoke-input /abs/path/to/wallpapers \
  --smoke-iterations 5
```

出力先ディレクトリには `summary.md` と `xfconf-values-before/after`、`smoke.log` が保存されます。

## 確認ポイント

- `last-image` 系プロパティが絶対パスになっている。
- 黒背景や無画像状態が解消している。
- 複数ディスプレイ環境では、左右ともに期待画像が反映される。

絶対パス確認は次の補助コマンドで機械判定できます。

```bash
python scripts/check_xfce_last_image_paths.py --file xfce-followup-YYYYmmdd-HHMMSS/xfconf-values-after.txt
```

## 失敗時の追加対応

1. `xfdesktop --replace` を実行して再読込する。
2. それでも復帰しない場合はログアウト/ログイン後に再確認する。
3. `xfconf-values-before.txt` と `xfconf-values-after.txt` の差分を添えて記録する。

## 記録テンプレ

- 実施日:
- 実施者:
- known-good 画像:
- 復帰結果（成功/失敗）:
- 補足（画面構成、再現条件など）:

## 実施記録（2026-03-20）

- 実施日: 2026-03-20
- 実施者: katsu
- known-good 画像: `/home/katsu/Develop/Repos/Harite/tests/data/img_wide.jpg`
- 復帰結果（成功/失敗）: 成功（壁紙復帰を確認）
- 出力ディレクトリ: `xfce-followup-20260320-131829`
- 補足:
  - summary.md 上はチェック未記入のため、`last-image` 絶対パス確認と黒背景再発有無は継続確認とする。

- 追加確認コマンド:
  - `python scripts/check_xfce_last_image_paths.py --file xfce-followup-20260320-131829/xfconf-values-after.txt`

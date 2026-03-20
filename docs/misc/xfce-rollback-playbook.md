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

## 確認ポイント

- `last-image` 系プロパティが絶対パスになっている。
- 黒背景や無画像状態が解消している。
- 複数ディスプレイ環境では、左右ともに期待画像が反映される。

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

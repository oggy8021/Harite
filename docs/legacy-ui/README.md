# Legacy UI Asset Staging

このディレクトリは、外部 clone に存在する旧母体の glade/ui 資産を
「参照専用」で保管するためのステージング場所です。

## 目的

- 旧 UI の構造と signal 名を失わず記録する
- 実装用抽出（src/harite/gui/resources）と原本保管を分離する

## 取り込みルール

1. 原本はこの配下へコピーする（移動ではなくコピー）
2. 原本ファイル名は維持する
3. 原本を直接編集しない
4. 変更が必要な場合は resources 側へ抽出して調整する

## 期待する主なファイル

- *.glade
- *.ui
- 関連画像や icon（必要な場合のみ）

## 次の作業

- `docs/specs/gui-signal-mapping.md` に signal 対応を記載
- 必要な UI だけ `src/harite/gui/resources/` へ抽出

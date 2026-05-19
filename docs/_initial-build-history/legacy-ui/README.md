# Legacy UI Asset Staging

このディレクトリは、外部 clone に存在する旧母体の glade/ui 資産を
「参照専用」で保管するためのステージング場所です。

## 目的

- 旧 UI の構造と signal 名を失わず記録する
- current runtime から切り離した履歴資産として原本を保管する

## 取り込みルール

1. 原本はこの配下へコピーする（移動ではなくコピー）
2. 原本ファイル名は維持する
3. 原本を直接編集しない
4. 変更が必要な場合も、この配下の原本は編集せず docs 側の補助文書で追跡する

## 期待する主なファイル

- *.glade
- *.ui
- 関連画像や icon（必要な場合のみ）

## 参照先

- `docs/specs/gui/gui-signal-mapping.md` は旧 glade signal 対応の履歴証跡
- current runtime の判断は `docs/specs/gui/gui-phase6-planning.md` と `docs/specs/gui/gui-phase6-glade-adapter-judgement.md` を参照

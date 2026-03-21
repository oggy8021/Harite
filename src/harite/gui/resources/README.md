# GUI Resource Staging

このディレクトリは、実装で使用する UI リソース（.ui/.glade 等）の配置先です。

## 使い分け

- 原本保管: docs/legacy-ui/
- 実装利用: src/harite/gui/resources/

## 取り込み方針

1. まず原本を docs/legacy-ui に置く
2. MVP に必要な画面だけ resources へコピー
3. 変更履歴は docs/specs/gui-signal-mapping.md で管理

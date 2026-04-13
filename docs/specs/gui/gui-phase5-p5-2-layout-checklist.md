# GUI Phase5 P5-2 MainWindow 大胆再構成チェックリスト

最終更新: 2026-04-13
対象: P5-2 feat(gui)

## 目的

- MainWindow の情報構造を再設計し、第一印象で主操作が分かる状態にする。
- Glade 時代のレイアウト意図を保ちながら、現行の可読性を引き上げる。

## 判定ルール

- 各項目は `pass` / `fail` / `not-available` で判定する。
- `fail` は 1 行以上の再現メモを残す。
- 受け入れは必須項目がすべて `pass` であること。

## A. 構造再設計（必須）

- [ ] A-1 主操作（Optimize / Apply）が画面上で最初に視認できる
- [ ] A-2 入力群（input/resolution/output）が機能単位でまとまっている
- [ ] A-3 情報の主従（見出し/補助説明/入力）が視覚的に区別できる
- [ ] A-4 旧版で重要だった操作ブロックが欠落していない

## B. 余白と視線導線（必須）

- [ ] B-1 セクション間余白が統一され、詰まり/空き過ぎがない
- [ ] B-2 ラベル、入力、主要ボタンの整列軸が揃っている
- [ ] B-3 視線が左上から主要操作へ自然に流れる
- [ ] B-4 誤操作を誘発する近接配置がない

## C. 体験差分の可視化（必須）

- [ ] C-1 before/after 画像で構造差分が一目で分かる
- [ ] C-2 変更理由を 3 行以内で説明できる
- [ ] C-3 変更により「次に押す場所」が迷いにくくなっている

## D. 品質運用（必須）

- [ ] D-1 関連 GUI テスト結果が記録されている
- [ ] D-2 XFCE 実機で MainWindow スクリーンショットを取得している
- [ ] D-3 PR本文に判定結果と差分説明を貼り付けている

## 証跡テンプレート（PR貼り付け用）

```md
### P5-2 MainWindow Layout Delta
- Scope: [OS/desktop]
- A. 構造再設計: pass/fail/not-available
- B. 余白と視線導線: pass/fail/not-available
- C. 体験差分の可視化: pass/fail/not-available
- D. 品質運用: pass/fail/not-available
- Before/After: attached
- Notes: [差分要点・再現メモ]
```

## Exit Criteria

- [ ] A〜D 必須項目がすべて `pass`
- [ ] MainWindow before/after 添付済み
- [ ] PR本文にテンプレート記録済み

# Issue #353

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/353>
- opened: 2026-05-31
- title: `左右画像選択後、入れ替えられるボタンがあるとよいかも。`

## 事象

- Main タブの左右画像 path、Slideshow タブの左右 srcdir を入れ替える操作がない。
- テストや条件変更付き Optimize の繰り返しで、手動で path を付け替えるのが手間。

## 分類

- polish / UX improvement

## 関連

- feature-overview: [P-01](../working/20260518-2047-feature-overview.md)（近端 polish）
- gui-spec: Main タブ path 行、Slideshow タブ srcdir 行
- [#358](issue-358.md)（Slideshow srcdir クリア — 同タブ周辺 UX）

## 取り込み方針

- **第2波（着手順序）**。F-01 完了後。P-02 と Slideshow 面をまとめて design slice → gui-spec。
- Main / Slideshow の **左右入れ替え**（`◁▷` 等）を 1 設計でまとめ、`.cursorrules` §9 に従い widget slice で合意してから gui-spec へ。
- スコープ: path / srcdir の値 swap のみ（ファイル移動や registry 変更は含めない）。

## 調査メモ

- memo（オーナー）: テスト実施から着想。画面中央部に swap ボタンがあると Optimize 条件変更が楽。

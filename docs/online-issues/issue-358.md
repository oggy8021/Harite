# Issue #358

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/358>
- opened: 2026-05-31
- title: `スライドショーについて、Srcdir-L,R をクリアする仕組みがない`

## 事象

- Slideshow タブで Srcdir-L / Srcdir-R を一度に空にする UI がない。
- Qt 版テスト時、左右 srcdir を揃えた状態からテストをやり直すのが手間。

## 分類

- polish / UX improvement

## 関連

- feature-overview: [P-02](../working/20260518-2047-feature-overview.md)
- [#353](issue-353.md)（同タブ周辺 — swap と合わせて design slice 検討可）
- gui-spec: Slideshow タブ srcdir 行

## 取り込み方針

- **近端着手候補**（P-01 とまとめて Slideshow 面の widget slice 合意がよい）。
- 要決定: 左右 **同時クリア** のみか、個別 clear も要るか（初期案は simultaneous がテスト用途に足りる）。
- GUI 版 slideshow は両 srcdir 必須のまま — clear 後は Start 不可になる挙動は現行 spec どおり。

## 調査メモ

- memo（オーナー）: 左右同時クリアか等は要検討だが、懸案として記録。

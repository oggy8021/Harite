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

- **第2波（着手順序）**。F-01 完了後。P-01 とまとめて Slideshow 面の widget slice 合意。
- **採用（2026-06-01 design slice）**: **個別 clear**（Clear-L / Clear-R）。Main タブ Clear-L/R と同配置（各 side panel 右下）。Clear both は不採用。
- GUI 版 slideshow は両 srcdir 必須のまま — 片方または両方空 → Start 不可（現行 spec どおり）。

## 調査メモ

- memo（オーナー）: 間違えた side だけ空にしたい。Clear both は UX が悪い。
- design: [20260601-p01-p02-lr-swap-clear-slice.html](../working/design/20260601-p01-p02-lr-swap-clear-slice.html)

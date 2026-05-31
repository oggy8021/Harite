# Issue #341

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/341>
- opened: 2026-05-31
- title: `Windows) スライドショーを実行しようとLRパス指定し、Startすると dual-source slideshow requires linux plugin となる`

## 事象

- Srcdir-L / Srcdir-R を指定して Start すると `dual-source slideshow requires linux plugin` となる
- **仕様として問題なし**（想定どおり）。dual-source slideshow は Linux plugin 前提
- Srcdir-L のみの指定では Start できない（これも仕様どおり）

## 分類

- **spec-as-designed** → **planning**（Qt 化により Windows ユーザーにも UI が見えるようになり、方針再検討が必要）

## 関連

- backlog: [docs/working/20260531-1200-windows-qt-validation-backlog.md](../working/20260531-1200-windows-qt-validation-backlog.md)（W-02）
- 横断: [#343](issue-343.md)（Apply / 壁紙 / 解像度）、two-screen、auto-split
- 正本: [harite-slideshow-spec.md](../specs/slideshow/harite-slideshow-spec.md)、[harite-plugin-spec.md](../specs/plugins/harite-plugin-spec.md) §4.1

## 取り込み方針

| 項目 | 判断 |
| --- | --- |
| 即時 bugfix | **不要**（現行 spec 通り） |
| 設計判断 | **保留**。W-03 とセットで決める |
| 選択肢（たたき台） | (1) Windows では slideshow 非提供を GUI で明示 (2) 単一 srcdir + 単一画像 apply のみ許可 (3) 将来 Windows per-monitor 対応 |
| 次アクション | W-03 方針確定後、slideshow-spec / gui-spec に Windows 向け注記を追記する spec PR |

## 論点メモ

- Linux 向けに設計された dual-source / per-monitor 経路を Windows にそのまま持ち込むかは未決
- Qt 移行の副産物として「できない」が目に付くようになった。UX 上の説明（disabled 理由・ヘルプ）も W-02 スコープに含めうる

# Issue #359

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/359>
- opened: 2026-05-31
- title: `ディスプレイが1接続しかないときは、右側操作パネルを全部無効化する？`

## 事象

- 物理 1 ディスプレイ環境で、右パネル（-R 側の path / srcdir / direction 等）をどう扱うか未整理。
- 単 display の再現が難しい（信号切替では 1 枚再現不可、ケーブル抜きは未試験）。

## 分類

- polish / investigation（edge case UX）

## 関連

- feature-overview: [P-03](../working/20260518-2047-feature-overview.md) — [planning draft](../working/20260606-p03-single-display-ux-planning-draft.md)（**display / monitor まわり UX の入口**。旧 K-01 の monitor 縁はここ。K-01 は [H-08](../working/20260518-2047-feature-overview.md#3-破棄候補--保留延長) 破棄）
- gui-spec: Main / Slideshow の dual-display 前提、monitor 検出

## 取り込み方針

- **planning draft 起票**（2026-06-06）— [20260606-p03-single-display-ux-planning-draft.md](../working/20260606-p03-single-display-ux-planning-draft.md)。採用条件未充足のため impl は未着手。
- ストレートな案は「検出 1 枚なら -R 側 widget 一式を disabled」だが、実装・テストコストが高く、再現手段も未確立。
- **採用条件**: (1) 単 display 再現手順の確立、(2) disabled 範囲の spec ストーリー（何を gray out するか）の合意、(3) GTK/Qt 両 backend でのテスト方針。
- C-02 / monitor policy 強化と競合しうるため、大 feature より後でもよい。

## 調査メモ

- memo（オーナー）: UX はストレートだが手間あり。HDMI 電源 off では枚数維持される等、再現が難しい。

# Issue #359

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/359>
- opened: 2026-05-31
- **closed: 2026-06-06**（P-03 完了 — #420 merge）
- title: `ディスプレイが1接続しかないときは、右側操作パネルを全部無効化する？`

## 事象

- 物理 1 ディスプレイ環境で、右パネル（-R 側の path / srcdir / direction 等）をどう扱うか未整理。
- 単 display の再現が難しい（信号切替では 1 枚再現不可、ケーブル抜きは未試験）。

## 分類

- polish / investigation（edge case UX）→ **resolved**

## 関連

- feature-overview: [P-03](../../working/20260518-2047-feature-overview.md) — [planning](../../working/finished/20260606-p03-single-display-ux-planning.md)（**display / monitor まわり UX の入口**。旧 K-01 の monitor 縁はここ。K-01 は [H-08](../../working/20260518-2047-feature-overview.md#3-破棄候補--保留延長) 破棄）
- gui-spec: [§4.3 単 display](../../specs/gui/harite-gui-spec.md)、[§6 slideshow start](../../specs/gui/harite-gui-spec.md)
- audit: [20260606-p03-3layer-audit.md](../../working/finished/20260606-p03-3layer-audit.md)

## 取り込み方針

- **完了（P-03）。** `len(detect_displays()) < 2` のとき第二スロット（R）UI を disabled。Slideshow は L-only start + single-file apply。
- **採用:** handler ブロック + GTK/Qt `dual_display_ui` 同期、opacity による視覚（Qt）。Margins Position 4 角は **有効**（埋め込み角 ≠ モニタ R）。
- **据え置き:** profile combo / Drawer、GTK C-02 slideshow widget（Qt-only layout）は既知 backlog。

## 調査メモ

- memo（オーナー）: UX はストレートだが手間あり。HDMI 電源 off では枚数維持される等、再現が難しい。
- 実機（2026-06-06）: Windows W2′ `len==1`、Normal Optimize、Margins embed、Slideshow L-only を確認。

## 3 層 audit（事後・2026-06-06）

| 層 | 内容 | PR / 根拠 |
| --- | --- | --- |
| **planning** | 第二スロット定義、disabled 範囲、L-only slideshow | [planning](../../working/finished/20260606-p03-single-display-ux-planning.md) |
| **spec** | gui-spec §4.3 / §6 L427–428 | #420 |
| **tests** | `test_p03_*`, `test_apply_surface`, CI conftest 隔離 | #420 |
| **impl（Qt/GTK）** | `dual_display_ui`, `MainWindow` guards, opacity | #420 |

## resolution

- **closed:** 2026-06-06
- **正本:** [gui-spec §4.3](../../specs/gui/harite-gui-spec.md)
- **PR:** #420（impl + gui-spec + tests）
- **手元確認:** Windows 単 display — R UI disabled、Slideshow L-only、Margins embed（Position Right 列は有効）

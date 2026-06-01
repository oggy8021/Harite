# Issue #353

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/353>
- opened: 2026-05-31
- **closed: 2026-06-01**（P-01 完了 — オーナー実機確認）
- title: `左右画像選択後、入れ替えられるボタンがあるとよいかも。`

## 事象

- Main タブの左右画像 path、Slideshow タブの左右 srcdir を入れ替える操作がない。
- テストや条件変更付き Optimize の繰り返しで、手動で path を付け替えるのが手間。

## 分類

- polish / UX improvement → **resolved**

## 関連

- feature-overview: [P-01](../../working/20260518-2047-feature-overview.md)
- [#358](issue-358.md)（同第2波 — Slideshow clear）
- design: [20260601-p01-p02-lr-swap-clear-slice.html](../../working/design/20260601-p01-p02-lr-swap-clear-slice.html)
- 正本: [harite-gui-spec.md §3 Main / §4.1](../../specs/gui/harite-gui-spec.md)

## 取り込み方針

- **完了（P-01 / 第2波）。** design slice → gui-spec → tests → impl を段階停止で実施。
- Main / Slideshow の **左右入れ替え**（`arrow-left-right`）を 1 設計でまとめた。
- スコープ: path / srcdir の値 swap のみ（ファイル移動・registry 変更なし）。
- Main の Swap は direction grid **中段**（Left-L … Right-L と同高）に配置（design 合意後の layout 調整含む）。

## 調査メモ

- memo（オーナー）: 画面中央部に swap があると Optimize 条件変更が楽。
- **2026-06-01:** Swap 初版は center 列下方で気づきにくい → 十字配置中段へ移動。オーナー「意味論がたしか」で OK。
- **2026-06-01:** 入替動作 OK（オーナー）。

## 3 層 audit（事後・2026-06-01）

| 層 | 内容 | PR / 根拠 |
| --- | --- | --- |
| **design** | Main 中央 Swap、Slideshow 中央 Swap；widget slice 合意 | #369 |
| **spec** | §3 レイアウト、§4.1 handlers、`arrow-left-right.svg`；Main Swap **中段**配置 | #370、本 PR |
| **tests** | `on_swap_input_paths` / `on_swap_slideshow_srcdirs`、RUNTIME_HANDLER_MAP、Qt wiring | #371 — `tests/gui/test_p01_p02_lr_swap_clear.py` |
| **impl（Qt）** | `MainWindow` swap handlers、`qt_tab_main` / `qt_tab_slideshow`、signal wiring | #371 |
| **impl（GTK）** | spec 上 parity 対象だが **未着手**（maintenance mode・第2波 Qt 先行） | — |

**プロセスメモ:** 第2波は F-01 教訓どおり design → spec → tests → impl で段階停止。branch protection により tests-only PR は CI 不通過のため tests+impl を #371 に統合。

## resolution

- **closed:** 2026-06-01
- **正本:** [gui-spec §4.1](../../specs/gui/harite-gui-spec.md)
- **PR:** #369（design）、#370（spec）、#371（tests + Qt impl）、本 PR（close + gui-spec 中段配置）
- **手元確認:** Main / Slideshow swap 動作、Main Swap 中段配置（オーナー）

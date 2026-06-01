# design

GUI の見た目合意形成用 artifact を置く（spec 正本の前段）。

## 位置づけ

| 種別 | 用途 | 例 |
| --- | --- | --- |
| **icon board** | Lucide 選定・icon+label・tone 比較 | [gui-phase10-icon-mock.html](gui-phase10-icon-mock.html) |
| **widget slice**（将来） | 新 widget 1 塊の配置・ラベル合意 | `YYYYMMDD-HHMM-*-slice.html` |
| **評価メモ** | mock の pass/warn/fail 記録 | [gui-phase10-icon-mock-memo.md](gui-phase10-icon-mock-memo.md) |

- HTML mock はブラウザで開いて比較する。CI 対象外。
- 振る舞いの正本は [docs/specs/gui/](../../specs/gui/)。mock は合意用の補助資料。
- icon board は **icon 専用**。ウィンドウ全体のレイアウト正本にはしない。

## 現在のファイル

| ファイル | 内容 |
| --- | --- |
| [gui-phase10-icon-mock.html](gui-phase10-icon-mock.html) | Main / Watch icon 合意 board（Phase10 由来） |
| [gui-phase10-icon-mock-memo.md](gui-phase10-icon-mock-memo.md) | 上記 mock の目的・評価観点・手順 |

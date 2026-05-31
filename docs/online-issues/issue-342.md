# Issue #342

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/342>
- opened: 2026-05-31
- title: `Qt) Windows) Optimize, Applyまわりがレイアウト崩れになっている`

## 事象

- Web UI に貼り付けのスナップショットを `out/online-issues/issue-342補足画像.png` として保存した（リポジトリ追跡は不要）
- Optimize ラベルと Apply ラベルの高さが揃っていない
- ボタンフェイスとして **アイコン + 文字列** は守る（icon-only 化は revert 済み）
- Optimize / Apply のユーザー補助メッセージ（例: `Optimize result: not-run`, `Apply target: not-ready`）は GTK 版ではボタン右横。Qt 版では **下段配置でも可**
- Apply における `Auto-Split` / `No Split` 選択とそれ以降の補助メッセージは、現行の残り領域への並べ方のままでよい

## 分類

- **UI polish**（不具合というより Qt 版の整列・可読性）

## 関連

- backlog: [docs/working/20260531-1200-windows-qt-validation-backlog.md](../working/20260531-1200-windows-qt-validation-backlog.md)（W-01）
- 実装: `src/harite/gui/adapters_qt/qt_tab_main.py`（action cluster）
- 正本: [docs/specs/gui/harite-gui-spec.md](../specs/gui/harite-gui-spec.md) § Main tab action cluster

## 取り込み方針

| 項目 | 判断 |
| --- | --- |
| 着手 | **完了** — PR #346 マージ・Windows 実機確認済 |
| spec 改訂 | [gui-spec](../specs/gui/harite-gui-spec.md) § Main tab action cluster（2026-05-31） |
| 実装 | `qt_tab_main.py` — 上端揃え、補助ラベルをボタン直下 |
| 次アクション | GitHub Issue #342 を close |

## resolution

- **2026-05-31**: PR [#346](https://github.com/oggy8021/Harite/pull/346) マージ。Windows `harite-qt` 実機で Optimize / Apply 見出しおよび補助ラベル配置を確認。
- 正本: [harite-gui-spec.md](../specs/gui/harite-gui-spec.md) § Main tab（action cluster 上端揃え、Qt 補助ラベル直下配置）。

## 補足

- Phase 8 監査 PR で試した icon-only action cluster は一貫性のため revert 済み。本 Issue は **ラベル高さ・補助テキスト配置** にスコープを限定する。

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
- 実装: `src/harite/gui/adapters_qt/qt_layout_builders.py`（action cluster）
- 正本（将来）: [docs/specs/gui/harite-gui-spec.md](../specs/gui/harite-gui-spec.md) Main tab レイアウト節

## 取り込み方針

| 項目 | 判断 |
| --- | --- |
| 着手 | **実施中** — [gui-spec](../../specs/gui/harite-gui-spec.md) § Main tab action cluster 改訂済 |
| spec 改訂 | 最小。補助ラベルの配置（横 / 下）を gui-spec に 1 段落追記すれば足りる |
| 実装 | Qt layout builder のみ。GTK 版は現状維持でよい |
| 次アクション | gui-spec ドラフト → テスト（レイアウト smoke）→ Qt layout 修正 PR |

## 補足

- Phase 8 監査 PR で試した icon-only action cluster は一貫性のため revert 済み。本 Issue は **ラベル高さ・補助テキスト配置** にスコープを限定する。

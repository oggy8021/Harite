# Windows Qt 検証 backlog（post Phase 8）

作成: 2026-05-31  
起点: `harite-qt` の Windows 実機検証と Phase 8 監査 PR マージ後の残論点

## 位置づけ

- [docs/working/20260518-2047-feature-overview.md](20260518-2047-feature-overview.md) の C-xx（post-1.0.0 機能 inventory）とは **別軸**。
- Qt 移行完了直後に表面化した **現行 surface の polish / プラットフォームギャップ** を束ねる。
- 仕様正本（`docs/specs/`）へ昇格する前の planning 入口。詳細観測は [docs/online-issues/](../online-issues/README.md) へ。

## 一覧

| ID | 項目 | 分類 | Issue | 優先感 | 現判断 |
| --- | --- | --- | --- | --- | --- |
| W-01 | Main タブ action cluster レイアウト | UI polish | [#342](../online-issues/issue-342.md) | 高（見た目・可読性） | **完了**（#346, 2026-05-31） |
| W-02 | Windows スライドショー方針 | planning | [#341](../online-issues/issue-341.md) | 中（設計判断） | **保留**。W-03 / two-screen / auto-split とセットで決める |
| W-03 | Windows Apply / 壁紙表示 / 解像度検出 | investigation | [#343](../online-issues/issue-343.md) | 中（Apply 品質） | **C 先行着手** → 完了後に A/B を判断 |

## 依存関係

```mermaid
flowchart LR
  W03[W-03 Apply / 壁紙 / 解像度]
  W02[W-02 Windows slideshow]
  W01[W-01 action cluster UI]

  W03 --> W02
  W03 -->|"two-screen / auto-split 前提"| SpecPlugin[plugin-spec / core-spec]
  W01 --> SpecGUI[gui-spec レイアウト節]
```

- **W-01** は W-02 / W-03 と独立。Qt layout builder のみで完結可能。
- **W-02** と **W-03** は「Windows で per-monitor / dual-source をどこまで約束するか」が共通テーマ。
- 現行正本: Windows plugin は **単一画像 apply のみ**（[plugin-spec §4.1](../specs/plugins/harite-plugin-spec.md)）。Linux plugin 必須の dual-source slideshow は **仕様どおり**。

## 推奨着手順（2026-05-31 更新）

1. ~~**W-01（#342）**~~ — 完了（PR #346）。
2. **W-03-C（#343 解像度検出）** — GTK/Linux 実装（`detect_displays` / `display_context`）を参考に Windows 強化。**可能なら先行実施**。正本ライティング時に plugin 層のディスプレイ名補完の表現範囲を相談。
3. **W-03-A / W-03-B（#343 Apply / 壁紙）** — C 実施後に判断（レジストリ Fit/Fill、背景色など）。
4. **W-02（#341）** — W-03 全体の方針確定後、slideshow を spec 化。

## W-03 方針候補と実施順

| 順 | 案 | 内容 | 状態 |
| --- | --- | --- | --- |
| 1 | **C. 解像度検出強化** | マルチモニタ bounds / 仮想解像度 / two-screen context を Windows でも `detect_displays` 経由で供給 | **着手予定** |
| 2 | A. 最小（現行維持） | `SystemParametersInfoW` のみ。OS Fit/Fill・背景色はユーザー任せ | C 後に判断 |
| 2 | B. 表示方式同期 | レジストリ `WallpaperStyle` / `TileWallpaper` | C 後に判断 |

背景色の重畳問題は **案 A ならノータッチ** で整理可能（#343 本文参照）。

## W-03-C 実装メモ（spec ドラフト用）

### 現状（Linux vs Windows）

| 項目 | Linux（GTK 参考） | Windows（現行） |
| --- | --- | --- |
| 検出入口 | `workspace.detect_displays()` → `xrandr --query` | 同入口 → `_detect_windows()` |
| ディスプレイ名 | `HDMI-1`, `DP-1` 等 | **空文字**（primary のみ） |
| ジオメトリ | width / height / x_offset / y_offset / primary | primary 1 枚の width / height のみ |
| 下流 | `display_context.build_two_screen_optimize_context()` → GUI two-screen / auto 解像度 | 2 枚検出不可 → two-screen 不可 |

### 強化の当たり所（コード）

- **主:** `src/harite/workspace.py` の `_detect_windows()` — `EnumDisplayMonitors` + `MONITORINFOEX` で `DeviceName`（`\\.\DISPLAYn`）、bounds（width/height/x/y）、primary を返す（`Screen.AllScreens` 相当。PowerShell は使わない）。
- **再利用:** `display_context.order_displays` / `derive_virtual_resolution` / `build_two_screen_optimize_context` — Linux と同じ経路。
- **既存:** `optimize_settings.resolve_optimize_display_settings` — primary 1 枚 fallback は Phase 8 で追加済み。C 完了で dual-input + two-screen も Windows 上で解決可能に。

### 正本ライティングで相談すること

- ~~Windows の `Display.name` に何を載せるか~~ → **オーナー判断: `\\.\DISPLAYn`（Screen.DeviceName 相当）をベース**（2026-05-31 実機確認）。
- **plugin 層**でディスプレイ名補完をどこまで約束するか — WMI 製品名は **空間順序には使わない**。Auto-Split ファイル名の部分文字列候補としての利用は **予備検討**（Linux xfconf 的用途）。解像度検知とは独立。
- GUI two-screen / Auto-Split を Windows で **どこまで有効化**するか（optimize のみ vs apply まで）。two-screen / auto-split 自体は **難しければ廃案も残す**。

## spec 改訂が必要になるタイミング

| トリガ | 想定正本 |
| --- | --- |
| action cluster の補助ラベル配置（Qt 下段） | ~~`harite-gui-spec.md` § Main tab~~ **反映済**（#346） |
| Windows で slideshow を新たに約束する | `harite-slideshow-spec.md`, `harite-plugin-spec.md` |
| Windows Apply で Fit/Fill 等を Harite が制御する | `harite-plugin-spec.md` §4.1 |
| 解像度 auto 検出の Windows 経路を追加 | `harite-core-spec.md`, `workspace.py`, `optimize_settings` 関連 — **W-03-C 着手予定** |

## 完了条件（この backlog 文書として）

- [x] W-01 が Issue クローズまたは spec + 実装 PR に分解された（#346, 2026-05-31）
- [ ] W-03-C（解像度検出）が spec + 実装 PR に分解された
- [ ] W-03-A / W-03-B が C 完了後にオーナー判断で固定された
- [ ] W-02 の Windows slideshow 方針が spec または Issue resolution に記録された
- [ ] 確定事項は online-issues の `resolution` 節と specs 正本へ反映された

## 関連

- Qt 移行計画: [20260530-2201-pyqt6-migration-plan.md](20260530-2201-pyqt6-migration-plan.md)
- Phase 8 監査: [20260531-0843-qt-phase8-3layer-audit.md](20260531-0843-qt-phase8-3layer-audit.md)
- Feature inventory（C-xx）: [20260518-2047-feature-overview.md](20260518-2047-feature-overview.md)

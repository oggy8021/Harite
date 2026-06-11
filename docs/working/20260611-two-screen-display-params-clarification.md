# two-screen / resolution / l-display / r-display — 整理メモ

最終更新: 2026-06-11  
**従属文書** — 親 planning: [20260611-1200-cli-v2-roadmap.md](20260611-1200-cli-v2-roadmap.md)（MAT-21 の設計入力）  
文脈: v2.0.0 前の整理ブランチ（`docs/pre-bump-v2.0.0-planning`）上で、CLI 総点検中にオーナー（原作者）と整理した内容。  
正本: [harite-core-spec.md §3](../specs/core/harite-core-spec.md#3-入力解決と表示コンテキスト)、[harite-cli-spec.md §4](../specs/cli/harite-cli-spec.md)

**ステータス: 記録のみ・実装は先送り。** §6 の母体寄せは **MAT-21**（親 roadmap）で横断着手。単体では core 変更に入らない。

---

## 1. 一行結論

**母体では WorkSpace 検出が幾何の正で、2枚入力＝dual は暗黙。** Harite は同じ情報を `two_screen` / `resolution` / `l_display` / `r_display` に **分解して CLI に露出**したため、原作者モデルから見ると **重複した混乱要素** になっている。CLI 総点検では **これらのフラグは通常スキップ** でよい（検出と入力枚数だけ見る）。

---

## 2. 母体（wallpaperoptimizer）のモデル

| 概念 | 母体での扱い |
| --- | --- |
| **WorkSpace** | マシン上のモニタ幾何を検出する **唯一の正** |
| **lScreen / rScreen** | WorkSpace から得た左右モニタ矩形（配置・収納判定・merge の基準） |
| **合成全体** | WorkSpace + 2枚バインドから **暗黙**（`_mergeWallpaper`、右画像は `lScreen.width` オフセット） |
| **2画面か否か** | **ユーザーが選ばない**。L/R に画像2枚 → dual 一択に近い |
| **CLI 相当** | `--two-screen` / `--l-display` / `--r-display` のような **独立ノブは無い** |

参照: [MAT-01b ドラフト](design/20260609-mat-01b-native-placement-repair-draft.md)、[MAT-15 監査](finished/20260609-mat-15-core-geometry-audit.md) §1.1（母体 `Core.py` 再読）

---

## 3. Harite のモデル（分解と露出）

Harite は再実装時に内部で必要だった分解を、そのまま設定・CLI 面に載せた。

| 母体（暗黙） | Harite（明示） | 主な実装 |
| --- | --- | --- |
| WorkSpace → lScreen / rScreen | `l_display` / `r_display` | `workspace.detect_displays()` → `build_two_screen_optimize_context()` |
| WorkSpace からの合成面 | `resolution` | `derive_virtual_resolution()`（two-screen 時は仮想デスクトップ外接矩形） |
| 2枚＝dual | `two_screen`（`auto` / on / off） | `resolve_optimize_display_settings()` |
| 検出モジュール名 | `src/harite/workspace.py` | **検出のみ**。母体の WorkSpace 全体（バインド・合成）ではない |

### 3.1 各パラメータの実態（用語の注意）

| パラメータ | Harite での意味 | **ではない** もの |
| --- | --- | --- |
| **`resolution`** | optimize が描く **合成キャンバス全体のピクセルサイズ**（出力 JPEG の作業解像度） | Windows 設定の「論理解像度」、タスクバー除きの利用可能領域 |
| **`l_display` / `r_display`** | 各モニタの **いま有効なピクセル寸法**（分割比率・スロット高さの根拠） | 「論理最大解像度」。パネル最大対応解像度一覧でもない |
| **`two_screen`** | 上記幾何モードを使うかの **明示フラグ**（未指定時は auto） | 母体にあった独立オプションではない |

**OS 別の検出:**

- **Windows:** `EnumDisplayMonitors` の `rcMonitor` = **physical pixel**（150% DPI 設定でも物理解像度）。`scale_percent` は取るが **resolution / l/r 解決には使わない**（core-spec §3.3）。
- **Linux:** `xrandr --query` の `connected` 行の **現在モード**（例 `1920x1080+1920+0`）。

### 3.2 two-screen ON 時の3つの関係（自動補完）

例: 左 1920×1080、右 1920×1080、横並び

- `l_display` = `1920x1080`
- `r_display` = `1920x1080`
- `resolution` = `3840x1080`（仮想デスクトップ外接）

`core.py` の `_resolve_display_slots` は `left_w : right_w` で `split_x` を決め、L margins `(ml,0,mt,mb)` / R `(0,mr,mt,mb)` を使う。

---

## 4. 混乱の本体（オーナー観点）

### 4.1 `two_screen` フラグ

- **母体:** 画像枚数（L/R の埋まり）で実質決まる。
- **Harite:** 2枚でも `two_screen=OFF` 可能 → **1キャンバスを半分ずつ** の第3経路。
- **オーナー判断:** この経路は **余計・嫌**（意図したユースケースではない）。2枚なら dual に寄せたい。

`two_screen=OFF` + 2枚になり得る状況:

1. Settings / 設定 JSON で `two_screen: false`（または off）を明示
2. CLI で `--no-two-screen`
3. **auto** だがモニタ検出が2台未満（context `None` → OFF に戻る → 半分ずつ）

### 4.2 `resolution` と `l/r-display` の三重露出

母体では **WorkSpace 一括** だった幾何が、Harite では **3〜4 個の名前** で重複表示されている。`workspace.py` という名前も母体 WorkSpace の **一部（検出だけ）** を指し、責務分割と名前の残りがさらに紛らわしい。

### 4.3 関連だが別レイヤの概念

- **Apply** の Span / Auto-Split / No Split（`apply_surface.margin_settings_split_label`）は **壁紙の貼り方**。optimize の `two_screen` とは別。
- **Slideshow dual-source** は `build_two_screen_optimize_context()` 必須（検出2台）。

---

## 5. CLI 総点検 — 実務ガイド

### 5.1 通常は触らない

| フラグ | 総点検での扱い |
| --- | --- |
| `--two-screen` / `--no-two-screen` | **スキップ可**（未指定 = auto） |
| `--l-display` / `--r-display` | **スキップ可**（検出に任せる） |
| `--resolution` / `-r` | **スキップ可**（検出 or 設定ファイル） |

確認すべきは **入力枚数** と **検出が効いているか**（出力の分割比率、`posit` が left/right か、ログ）。

### 5.2 設定ファイルだけ注意

`--settings-file` に `"two_screen": false` や `"off"` が入っていると、2枚でも明示 OFF になる。GUI 保存 JSON を CLI に流用している場合は要確認。

### 5.3 CLI と spec の既知ギャップ（参考）

[specs-checking](finished/20260530-1509-specs-checking-from-cursor.md) CLI1: Typer の `--two-screen` デフォルト `False` と、未指定時 auto 扱いの説明が読み手を混乱させやすい。実動は `resolve_bool_or_auto_option` が CLI 未指定なら `None`（auto）を返す経路。

---

## 6. 将来整理の方向（候補メモ・未着手）

オーナー・原作者モデルに寄せる **方向性のメモ**。§6 全体は **後日・他話題と合わせて** 設計・実装する（本稿単体では core 変更に入らない）。

| 候補 | 触る層（例） |
| --- | --- |
| 2枚入力 → two-screen 必須（半分ずつ1キャンバス廃止） | `core`, `optimize_settings`, GUI/CLI |
| `two_screen` を UI/CLI から隠す（枚数 + WorkSpace） | `cli`, settings, gui-spec |
| `resolution` / `l/r-display` を上級者 override に格下げ | `cli`, `display_context`, harite-core-spec |
| Settings TwoScreen Off 縮小 or 廃止 | `settings`, Qt settings dialog |
| 用語整理（合成キャンバス / 各モニタ実ピクセル） | spec 正本 |

**いまやらない:** 上記のコード変更、Apply Span / per-monitor plugin、Slideshow CLI 実機、CHANGELOG / 版 bump。

**横断着手の入口:** [20260611-1200-cli-v2-roadmap.md](20260611-1200-cli-v2-roadmap.md)（MAT-21）。

---

## 7. コード・正本への索引

|  topic | 場所 |
| --- | --- |
| 表示解決 | `src/harite/optimize_settings.py` — `resolve_optimize_display_settings` |
| two-screen context | `src/harite/display_context.py` — `build_two_screen_optimize_context` |
| 検出 | `src/harite/workspace.py` — `detect_displays` |
| スロット分割 | `src/harite/core.py` — `_resolve_display_slots` |
| CLI 入口 | `src/harite/cli.py` — `optimize` の `--two-screen`, `--l-display`, `--r-display`, `--resolution` |
| GUI 自動同期 | `src/harite/gui/views/main_window.py` — `_sync_two_screen_state` |
| Settings 三値 | `src/harite/settings.py` — `two_screen_mode`（auto/on/off） |

---

## 8. 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-11 | 初版（CLI 総点検中のオーナー対応を markdown 化） |
| 2026-06-11 | ステータス追記 — core 等の基底変更は先送り、他話題と横断整理予定 |
| 2026-06-11 | 親 roadmap リンク — MAT-21 設計入力として従属化 |

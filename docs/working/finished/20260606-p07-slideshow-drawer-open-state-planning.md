# P-07 — Slideshow options Drawer 開閉の視認性（計画正本）

最終更新: 2026-06-06  
ステータス: **完了**（#417 merge、#412 close、オーナー実機 OK）

## 位置づけ

| 文書 | 役割 |
| --- | --- |
| [feature-overview §P-07](../20260518-2047-feature-overview.md) | inventory 入口 |
| **本書** | Slideshow options Drawer の **開いている／閉じている** 視認性 — 計画正本（完了記録） |
| [C-04 計画正本](20260604-c04-gui-surface-planning-draft.md) | Drawer 導入（Wave b） |
| [surface slice-memo](../design/20260604-c04-slideshow-margins-surface-slice-memo.md) | S2–S5 合意（Manage / Mode は Drawer 内） |
| GitHub [#412](https://github.com/oggy8021/Harite/issues/412) | 起票（online-issues への md 転記は **不要**、クローズ済み） |

**きっかけ:** Drawer 伸長の開閉が分かりにくい。現状はラベル反転（`More…` ↔ `Fewer…`）と固定 chevron のみ。

**オーナー方針（2026-06-06 確定）:**

- **背景ずらし + 縁取り** を採用（固定 `#F0F0F0` 系だが **ダークモード相性は懸念** → palette 参照を優先）
- **chevron 回転**、開時トリガの軽い pressed 感を **セット**で OK
- 専用 online-issues md は作らない（#412 のみ）

---

## 1. 問題

- `More slideshow options…` で開く補助面（Mode / Manage / current・output）が、閉じた正面と **同一白背景**のまま伸びる。
- ラベル反転だけでは「どこまでが Drawer か」「今開いているか」が弱い。
- C-04 slice mock は紫系 panel + 枠だったが、本番は未適用。

---

## 2. 目標（v1 — 合意済み・実装反映）

| 要素 | 内容 |
| --- | --- |
| **Drawer 面板** | 開時のみ: 背景を base より一段ずらす。**実装:** `QPalette.Window` に theme chrome tint（`Window` と `WindowText` を 6% 混合）+ `autoFillBackground`。子 widget へ QSS を当てない |
| **上辺ボーダー** | drawer 直上に 1px `QFrame` — `palette(mid)` |
| **内側 inset** | 左右 `8px` 前後 padding |
| **トリガ chevron** | 閉 = down、開 = up（`arrow-down.svg` / `arrow-up.svg` 切替） |
| **トリガ状態** | 開時: chrome tint 背景 + 上・左・右 1px 枠（scoped QSS、下辺なし） |
| **既存** | `More…` / `Fewer…` ラベル反転は **維持**（`slideshow_options_drawer.py`） |

**スコープ v1:** **Slideshow** `slideshow_options_drawer` のみ。Margins 側 Drawer が将来同型なら **同スタイルを再利用**。

---

## 3. スコープ / スコープ外

| 含む（v1） | 含まない |
| --- | --- |
| Qt Slideshow drawer 開閉スタイル | 開閉アニメーション（高さ tween） |
| GTK parity（`slideshow_options_drawer` 共通 toggle） | Margins drawer（未実装なら別波） |
| palette ベース色（ダークモード耐性） | 固定 hex のみで完結する実装 |
| chevron 回転 + 上辺線 + 背景 | Drawer 内コンテンツの再配置 |
| | online-issues への md 新規転記 |

---

## 4. 着手 gate checklist

| # | 論点 | 提案 | オーナー |
| --- | --- | --- | --- |
| P7-1 | 背景 | theme chrome tint（palette 混合） | **pass** |
| P7-2 | 縁取り | drawer 上辺 1px `mid` 系 | **pass** |
| P7-3 | chevron | 開 = up / 閉 = down | **pass** |
| P7-4 | トリガ pressed | 開時のみ chrome 背景 + 枠 | **pass** |
| P7-5 | ダークモード | 固定 hex 単独は不可。palette フォールバック必須 | **pass** |

---

## 5. 実装フェーズ（完了）

| 段 | 内容 |
| --- | --- |
| 0 | 本書（方針確定） |
| 1 | `slideshow_options_drawer.py` — toggle 時に drawer / trigger スタイル適用 |
| 2 | Qt `qt_tab_slideshow` — drawer widget + top border `QFrame` |
| 3 | GTK `gtk_tab_builders` — 同等 CSS / widget class |
| 4 | gui-spec §3 Drawer 追記、実機確認、#412 クローズ |

**入口:** `toggle_slideshow_options_drawer` / `apply_slideshow_options_drawer_open_state` が正本。

**実装メモ（Qt）:** 初版で drawer 親への QSS が子を黒塗りにしたため、面板は palette のみ。トリガ QSS は閉じ括弧 typo と `AlternateBase` 直指定を修正し chrome tint に統一（#417 追補）。

---

## 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-06 | 初版 — #412 由来。背景+縁取り+chevron。ダークモードは palette 優先 |
| 2026-06-06 | Qt/GTK impl — `slideshow_options_drawer` 開閉スタイル、chevron 切替 |
| 2026-06-06 | #417 merge — palette/chrome tint 修正、#412 close、本書を finished へ |

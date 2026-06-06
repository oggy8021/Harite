# P-07 — Slideshow options Drawer 開閉の視認性（計画 draft）

最終更新: 2026-06-06  
ステータス: **planning draft**（方針確定・gate 前）

## 位置づけ

| 文書 | 役割 |
| --- | --- |
| [feature-overview §P-07](20260518-2047-feature-overview.md) | inventory 入口 |
| **本書** | Slideshow options Drawer の **開いている／閉じている** 視認性 — 計画正本 |
| [C-04 計画正本](20260604-c04-gui-surface-planning-draft.md) | Drawer 導入（Wave b） |
| [surface slice-memo](design/20260604-c04-slideshow-margins-surface-slice-memo.md) | S2–S5 合意（Manage / Mode は Drawer 内） |
| GitHub [#412](https://github.com/oggy8021/Harite/issues/412) | 起票（online-issues への md 転記は **不要**） |

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

## 2. 目標（v1 案 — 合意済み）

| 要素 | 内容 |
| --- | --- |
| **Drawer 面板** | 開時のみ: 背景を base より一段ずらす（ライト目安 `#F0F0F0`、**実装は `QPalette.ColorRole.AlternateBase` / GTK 同等**） |
| **上辺ボーダー** | drawer 直上に 1px — `palette(mid)` または `#D0D0D0` 相当。白との境界を明示 |
| **内側 inset** | 左右 `8px` 前後 padding（任意・コスト低ければ同梱） |
| **トリガ chevron** | 閉 = down、開 = up（180° 回転）。`arrow-down.svg` を回転または up アイコン切替 |
| **トリガ状態** | 開時: 軽い sunken / 面板と同系の背景で「引き出し一体」感（過度な 3D は避ける） |
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

## 4. 着手 gate checklist（未記入）

| # | 論点 | 提案 | オーナー |
| --- | --- | --- | --- |
| P7-1 | 背景 | `AlternateBase` 優先。ライト実機で `#F0F0F0` 相当か確認 | **pass**（方針） |
| P7-2 | 縁取り | drawer 上辺 1px `mid` 系 | **pass** |
| P7-3 | chevron | 開 = up / 閉 = down | **pass** |
| P7-4 | トリガ pressed | 開時のみ軽い sunken または同系背景 | **pass** |
| P7-5 | ダークモード | 固定 hex 単独は不可。palette フォールバック必須 | **pass**（懸念として明記） |

**gate 通過条件:** P7-1–P7-5 を実機（ライト + 可能ならダーク）で pass → gui-spec §3 Slideshow 1 行追記 → impl。

---

## 5. 実装フェーズ案

| 段 | 内容 |
| --- | --- |
| 0 | 本書（方針確定） |
| 1 | `slideshow_options_drawer.py` — toggle 時に drawer / trigger スタイル適用 |
| 2 | Qt `qt_tab_slideshow` — drawer widget に objectName / 初期スタイルフック |
| 3 | GTK `gtk_tab_builders` — 同等 CSS / widget class |
| 4 | gui-spec §3 Drawer 追記、実機確認、#412 クローズ |

**入口:** `toggle_slideshow_options_drawer` が正本。開閉とスタイルを **一箇所**に集約。

---

## 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-06 | 初版 — #412 由来。背景+縁取り+chevron。ダークモードは palette 優先 |

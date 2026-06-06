# P-06 — Slideshow CODH キーワード read-only 露出（計画 draft）

最終更新: 2026-06-06  
ステータス: **impl 完了**（Qt — gate pass、gui-spec 改訂済み）

## 位置づけ

| 文書 | 役割 |
| --- | --- |
| [feature-overview §P-06](20260518-2047-feature-overview.md) | inventory 入口 |
| **本書** | Slideshow タブ内の CODH キーワード **読み取り専用**露出 — 計画正本 |
| [C-01-E-KW 完了](finished/20260605-c01-e-kw-codh-keyword-planning.md) | 編集は Manage `keyword(CODH)` |
| [P-05 planning](20260606-p05-manage-sources-panel-planning-draft.md) | Manage 内の編集面整理（本書とは別） |

**きっかけ（2026-06-06）:** キーワード preset 運用中に「いま何で回しているか」を見るには Manage が遠い。編集は Manage のまま、**確認だけ Slideshow タブ**に置く。

**オーナー方針（確定）:**

- **Slideshow タブのみ**でよい（他タブ・Footer には出さない）
- 配置は **タブ内容の右上角** — muted label / チップ
- **read-only**（編集・ショートカットで Manage を開く等は v1 不要）
- P-05（Manage 面板）とは **別 Polish**

---

## 1. 問題

- `codh_keyword` は `harite-settings.json` にあり、編集 UI は Manage dialog のみ。
- Slideshow 運用中に L/R が keyword preset でも、**正面から現在のキーワードが読めない**。
- Footer `Slideshow summary` へ足す案は、目線が届きにくいため **不採用**。

---

## 2. 目標

| 方針 | 内容 |
| --- | --- |
| **露出面** | **Slideshow タブ内容の右上角**に read-only 表示 |
| **表示条件** | L または R の saved source が `codh-edo-spots-keyword` / `codh-edo-shops-keyword` のとき **表示**；それ以外は **非表示**（空・hidden） |
| **文言（案）** | `CODH: {keyword}` または `keyword(CODH): {keyword}` — gate で 1 つに固定 |
| **データ** | `harite-settings.json` の `codh_keyword`（Manage Close / Refresh 後と同期） |
| **編集** | **行わない** — 変更は従来どおり Manage（将来 P-05 preset 面板） |

C-04 の Slideshow 正面ミニマル（profile → srcdir → interval/start/stop）を崩さない。**右上角は補助ステータス**として扱う。

---

## 3. スコープ / スコープ外

| 含む（v1 案） | 含まない |
| --- | --- |
| Qt Slideshow tab 右上角 read-only label | Footer / Main / Margins への露出 |
| L/R combo 変更・Manage Close 後の表示更新 | クリックで Manage 起動 |
| keyword preset 非選択時の非表示 | キーワードのインライン編集 |
| muted スタイル（C-04 footer muted と同系） | GTK parity（Qt 先行） |
| | L/R で別 KW（C-01-E-KW で共通 1 語のまま） |
| | Notebook タブラベルへの動的文言 |

---

## 4. 着手 gate checklist（未記入）

| # | 論点 | 提案 | オーナー |
| --- | --- | --- | --- |
| P6-1 | 配置 | タブ内容 **右上角**、profile 行と縦に競合しない | **pass**（方針確定 2026-06-06） |
| P6-2 | 露出範囲 | **Slideshow のみ**。Footer 等は出さない | **pass** |
| P6-3 | ラベル文言 | `CODH: {kw}`（短い） | **pass** |
| P6-4 | 表示条件 | L/R いずれかが keyword preset のとき表示 | **pass** |
| P6-5 | 更新タイミング | profile / source combo 変更、Manage Close、`sync_slideshow_state_from_owner` | **pass** |

**gate 通過条件:** P6-3–P6-5 を含め pass。次: widget slice（任意）→ gui-spec §3 Slideshow 追記 → impl。

---

## 5. 実装フェーズ案

| 段 | 内容 |
| --- | --- |
| 0 | 本書（方針確定） |
| 1 | gui-spec §3 Slideshow tab 追記 |
| 2 | Qt layout（右上角 label）+ 表示条件配線 |
| 3 | テスト（combo 変更で show/hide、keyword 文字列） |

**着手順序:** P-05 と **独立**。小粒のため P-05 前後どちらでも可。

---

## 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-06 | 初版 — オーナー: Slideshow 右上角 read-only、Footer 不採用、P-05 と分離 |
| 2026-06-06 | Qt impl — `slideshow_codh_keyword_chip` + tab 右上角 label |

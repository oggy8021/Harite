# C-01-E-KW — CODH キーワード検索のユーザー指定（計画正本）

最終更新: 2026-06-06  
ステータス: **完了**（#413 merge、オーナー実機 OK）

## 位置づけ

| 文書 | 役割 |
| --- | --- |
| [feature-overview §C-01-E-KW](../20260518-2047-feature-overview.md) | inventory 入口（1 行） |
| **本書** | CODH キーワード UI — 計画正本（完了記録） |
| [CODH inventory](20260603-c01-e-codh-icp-inventory.md) | API・メタデータ棚卸 |
| [C-01-F planning](../20260604-c01-f-remote-sync-on-tick-planning-draft.md) | **据え置き** — tick sync（CODH 負荷懸念含む） |
| [P-05 planning](../20260606-p05-manage-sources-panel-planning-draft.md) | keyword 行の理想配置（面板分割） |
| [harite-source-spec §15.7](../../specs/source/harite-source-spec.md) | provider 正本 |
| [harite-gui-spec §4.2](../../specs/gui/harite-gui-spec.md) | Manage dialog 契約 |

**前提（完了済み）:** C-01-E provider、C-04 Drawer / Manage 導線。

---

## 9. 完了記録（2026-06-06）

| 項目 | 内容 |
| --- | --- |
| PR | [#413](https://github.com/oggy8021/Harite/pull/413) — `feature/c01-e-kw-codh-keyword` |
| preset | `codh-edo-spots-keyword` / `codh-edo-shops-keyword`（`codh-edo-spots-sakura` 廃止） |
| 保存 | `harite-settings.json` の `codh_keyword`（観光・買物 **共通 1 語** — 分離は見送り） |
| 検索 | `where={kw}` 部分一致（`where_metadata_*` 完全一致は地名で 0 件になりうるため不採用） |
| 設定ファイル責務 | preset JSON / `harite-sources.json` の `notes` に KW・interval 機械行は **書かない** |
| エラー | `remote sync failed (L\|R — {source名}): …`（Start 時）。0 件はエラーのみ（K4） |
| オーナー判断 | 機能 **一旦 OK**。KW 共有のまま。CODH 負荷のため **C-01-F は据え置き** |
| 残課題 | Manage 暫定配置 → [P-05](../20260606-p05-manage-sources-panel-planning-draft.md)。運用中の read-only 露出 → [P-06](../20260606-p06-slideshow-codh-keyword-chip-planning-draft.md) |

---

## 1. 問題

- `codh-edo-spots-sakura` の **「桜」はコード固定** — ユーザーが梅・花火・地名などに変えられない。
- 同梱 preset を 104 ファセット分増やすのは非現実的。
- C-04 後、KW 入力の置き場は **Manage sources and profiles…** 内に合意済み。

---

## 2. 目標

**CODH 江戸観光・江戸買物の両 indexer で、ユーザーが 1 語指定して slideshow remote source として使えるようにする。**

| 方針 | 内容（§7 確定 + impl 改訂） |
| --- | --- |
| **indexer** | `edo-spots` + `edo-shops` — **同一** `codh_keyword` |
| **preset** | `codh-edo-spots-keyword` / `codh-edo-shops-keyword`。`codh-edo-spots-sakura` 廃止 |
| **検索 API** | `where={kw}`（部分一致）。[inventory §2](20260603-c01-e-codh-icp-inventory.md) |
| **保存** | `harite-settings.json` の `codh_keyword` |
| **UI** | Manage dialog `keyword(CODH)` 行（暫定: Refresh 直上） |
| **多様性** | 疑似ランダム（`total` → `start`） |

---

## 3. `codh_keyword` 契約

**保存先:** `harite-settings.json` トップレベル `codh_keyword`。

| 項目 | 契約 |
| --- | --- |
| キー | `codh_keyword` |
| 値 | UTF-8、strip、空は無効。最大 **16** 文字（`len()`） |
| preset JSON / source `notes` | **書かない** |
| 初期値 | `桜` |

---

## 4. GUI

**slice:** [20260605-c01-e-kw-manage-keyword-slice.html](../design/20260605-c01-e-kw-manage-keyword-slice.html) + [memo](../design/20260605-c01-e-kw-manage-keyword-slice-memo.md)

暫定: Refresh 直上・常設・対象 preset 時のみ enabled。理想配置は **P-05**。

---

## 5. sync 挙動

```
_codh_sync (keyword preset)
  1. settings から codh_keyword（default 桜）
  2. where={kw}
  3. total → random start → limit=1
  4. canvasThumbnail → /max/ → latest.*
```

**注意:** 買物 DB に無い語（例: 飛鳥山）は R 側のみ 0 件エラーになりうる。

---

## 7. 着手 gate checklist

K1–K6 すべて **pass**（2026-06-05）。[slice-memo](../design/20260605-c01-e-kw-manage-keyword-slice-memo.md) 参照。

---

## 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-05 | 初版 planning draft |
| 2026-06-05 | §7 gate 通過 |
| 2026-06-06 | **完了** — #413。`where` 検索・設定ファイル責務分離・L/R エラー。`finished/` へ移動 |

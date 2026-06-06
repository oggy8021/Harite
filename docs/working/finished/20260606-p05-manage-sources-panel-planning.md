# P-05 — Manage sources リスト整理（計画正本）

最終更新: 2026-06-06  
ステータス: **完了**（Qt — gate pass、gui-spec 改訂済み）

## 位置づけ


| 文書                                                                          | 役割                                    |
| --------------------------------------------------------------------------- | ------------------------------------- |
| [feature-overview §P-05](../20260518-2047-feature-overview.md)                 | inventory 入口                          |
| **本書**                                                                      | Manage dialog の source 一覧・面板分割 — 計画正本 |
| [C-01-E-KW 完了](finished/20260605-c01-e-kw-codh-keyword-planning.md)         | `keyword(CODH)` 暫定行の移設先               |
| [keyword slice-memo](../design/20260605-c01-e-kw-manage-keyword-slice-memo.md) | 暫定 vs 理想の合意                           |


**きっかけ:** C-01-E-KW で Refresh 直上に keyword 行を暫定配置。理想は **local / preset 二面板**。

---

## 1. 問題

- Manage dialog の source 一覧が **local + preset 混在**で長く、操作の所属が分かりにくい。
- Refresh / keyword(CODH) は **preset 専用**だが、source リストと一体表示のまま。
- 自動ソート・グループ見出しが無く、追加 preset が増えると探索コストが上がる。

---

## 2. 目標


| 方針            | 内容                                                         |
| ------------- | ---------------------------------------------------------- |
| **面板**        | **ALL タブなし**。**local 面板** と **preset 面板** に分離              |
| **local 面板**  | Delete、name、path、Browse、Add local                          |
| **preset 面板** | source 一覧（preset/remote）、Refresh、**keyword(CODH)**         |
| **ソート**       | 自動ソート + グループ見出し（manual 並べ替え・schema 変更は対象外）                 |
| **schema**    | `harite-sources.json` の catalog schema version は **変更しない** |


---

## 3. スコープ / スコープ外


| 含む（v1 案）                | 含まない                  |
| ----------------------- | --------------------- |
| Qt Manage dialog 面板分割   | GTK parity（Qt 先行後に最小） |
| keyword 行の preset 側への移設 | Slideshow read-only 露出 — **[P-06](20260606-p06-slideshow-codh-keyword-chip-planning.md)** |
| 自動ソート・見出し               | ユーザー手動並べ替え            |
| C-01-E-KW 暫定行の撤去        | profile 編集 UI の大幅変更   |


---

## 4. 着手 gate checklist


| #    | 論点        | 提案                                   | オーナー |
| ---- | --------- | ------------------------------------ | ---- |
| P5-1 | 面板切替      | タブ vs 縦積み二面板                         | **pass**（タブ） |
| P5-2 | preset 一覧 | `harite-preset:` マーカーでグループ / 自動ソート順  | **pass** |
| P5-3 | keyword 行 | keyword preset 選択時のみ enabled           | **pass**（現行踏襲） |
| P5-4 | local 操作  | 現行 Add local 行を local 面板へ集約          | **pass** |


**gate 通過条件:** P5-1–P5-4 **pass**（2026-06-06）。

---

## 5. 実装フェーズ案


| 段   | 内容                                  |
| --- | ----------------------------------- |
| 0   | 本書 + widget slice 合意                |
| 1   | gui-spec §4.2 改訂                    |
| 2   | Qt `qt_source_registry_dialog` 面板分割 |
| 3   | keyword 行移設・テスト                     |


---

## 変更履歴


| 日付         | 内容                          |
| ---------- | --------------------------- |
| 2026-06-06 | 初版 — C-01-E-KW 完了後の次着手として起票 |
| 2026-06-06 | Qt impl — `qt_source_registry_dialog` Local/Presets タブ、グループ見出し、keyword 移設 |



# C-04 Slideshow / Margins surface slice — 評価メモ

最終更新: 2026-06-04（オーナー checklist 記入 → 合意確定）  
mock: [20260604-c04-slideshow-margins-surface-slice.html](20260604-c04-slideshow-margins-surface-slice.html)  
計画正本: [20260604-c04-gui-surface-planning-draft.md](../finished/20260604-c04-gui-surface-planning-draft.md) §4–§5

## 目的

- §4（Slideshow）と §5（Margins）の **将来配置**をブラウザ mock で合意する。
- impl 前に「何をタブ正面に残すか / Drawer に移すか / 削除するか」を固定する。

## 使い方

1. HTML をブラウザで開く（ローカル file:// で可）。
2. 各 slice の **左=現行 / 右=提案**（案 B は単 panel）を見比べる。
3. 下記 checklist に pass / revise / reject を記入（オーナー）。

## §4 Slideshow — 合意 checklist


| #   | 論点                                    | 提案                         | オーナー                              |
| --- | ------------------------------------- | -------------------------- | --------------------------------- |
| S1  | Profile row から `Applies L/R` 常設文を外す   | tooltip 可                  | **pass**                          |
| S2  | Manage は正面 1 ボタン vs Drawer 内のみ        | Drawer 内推奨（最薄）             | **pass**（Drawer 内）                |
| S3  | Mode + help は Drawer                  | 正面は Interval+Start/Stop のみ | **pass**                          |
| S4  | current/output は Drawer または footer 要約 | detail row 削除              | **pass**（Drawer；footer 要約は実装時に決定） |
| S5  | 「More slideshow options…」ラベルでよいか      | 要 rename 可                 | **pass**（rename 可）                |
| S6  | KW 余地は Manage dialog 内（Drawer 経由）でよいか | C-01-E-KW 前提               | **pass**                          |


## 案 B — 「減る」のか「mock の省略」か（2026-06-04 補足）

**結論:** いまの HTML 案 B は **操作系を統廃合した設計図ではなく、ほぼ省略した概念図**。実装する案 B を採る場合も、**spin 個数・設定項目の削除は案 A と同じ範囲**に留め、**載せ場所だけ** Main 外周 + Drawer に変える想定。


| 区分                                                   | 現行（Margins tab） | 案 B での扱い                                                 |
| ---------------------------------------------------- | --------------- | -------------------------------------------------------- |
| 4 辺 margin spin（top/left/right/bottom）               | cross-grid 外周   | **削除しない** — Main の compose を囲む位置へ **移設**                 |
| embed pattern（4 radio）                               | center          | **Drawer 内**（折りたたみ時は非表示）                                 |
| margin text notebook（Settings/Text + max lines spin） | center          | **Drawer 内**                                             |
| Position L/R Top/Bottom                              | center          | **Drawer 内**（Main の direction 十字とは **別物のまま** — 自動統合はしない） |
| `align=...` summary・3 行 notes                        | center          | **削除**（案 A と共通 — tooltip 化）                              |
| Main: L/R direction・Open・Preview・Optimize・Apply      | Main tab        | **維持**（mock では「既存」と一行のみ）                                 |


**mock で減って見える理由:** Drawer 折りたたみ・Preview 群・spin の実体・notebook タブを **描いていない**ため。

**案 B 固有の UX リスク:** Drawer を開かないと margin 数値以外が見えない → **機能削減ではなく discoverability の問題**。常時 4 spin を Main に見せるか、Drawer を半開きにするかは別決定。

---

## §5 Margins — 合意 checklist


| #   | 論点                        | 案 A（専用 tab スリム）  | 案 B（Main Drawer） | オーナー                                |
| --- | ------------------------- | ---------------- | ---------------- | ----------------------------------- |
| M1  | `align=...` 長文 summary 削除 | 採用               | 採用               | **pass**                            |
| M2  | 3 行 notes → tooltip       | 採用               | 採用               | **pass**                            |
| M3  | spin 十字を主役                | 採用               | Main 外周に spin    | **pass**（A 先行）                      |
| M4  | embed/position/text の載せ方  | tab 内 sub-panel  | Drawer 内         | **pass**（A: tab 内 / B: 将来 Drawer）   |
| M5  | Margins 専用 tab            | **維持**           | **廃止 or 空**      | **pass** — **Wave a は A（維持）**。B は保留 |
| M6  | 先行実装                      | Wave a で A のみでも可 | B は slice 合意後    | **pass**                            |


**推奨順序（エージェント）:** 案 **A を先**（差分が小さい）→ 余裕があれば B を spec オプションとして比較。

## footer（参考 slice）


| #   | 論点                | 判断           | オーナー |
| --- | ----------------- | ------------ | --- |
| F1  | `Phase: state` 廃止 | 採用（§3.2）     | **pass** |
| F2  | Error 赤系          | Wave 0（P-04） | **pass** |


## 合意確定サマリ（2026-06-04）


| 波      | 内容                                                                                                 |
| ------ | -------------------------------------------------------------------------------------------------- |
| **0**  | footer Error 視覚分離 + `Phase: state` 廃止                                                              |
| **b**  | Slideshow: 正面 = profile + L/R source + interval + Start/Stop；**More…** Drawer に Mode/Manage/output |
| **a**  | Margins **専用 tab 維持**・スリム化（summary/notes 削除、spin 十字主役）                                             |
| **将来** | 案 B（Main+Margins Drawer）— 操作削減なし・載せ替えのみ                                                            |


## 合意後の出口

1. ~~checklist~~ → **完了**。計画正本 §4.2 / §5 確定版へ反映済み。
2. gui-spec §3 Slideshow / Margins に落とす design→spec PR。
3. Wave 0 → Wave b（Slideshow）→ Wave a（Margins）の順で可。

## 変更履歴


| 日付         | 内容                          |
| ---------- | --------------------------- |
| 2026-06-04 | 初版 — HTML slice + checklist |
| 2026-06-04 | オーナー記入 — 全項目 pass。計画正本へ反映   |
| 2026-06-04 | 保存後確認 — エージェント仮記入と一致（差分なし） |



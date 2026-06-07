# P-08 — Main + Margins Drawer（C-04 案 B）（計画 draft）

最終更新: 2026-06-08  
ステータス: **gate 通過**（#432 merge。gui-spec §3 改訂 → テスト → impl）

## 位置づけ


| 文書                                                                             | 役割                                                           |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------ |
| [feature-overview §P-08](20260518-2047-feature-overview.md)                    | inventory 入口                                                 |
| **本書**                                                                         | C-04 §7.2 **案 B** — Margins 専用 tab 廃止、Main 正面 + Drawer へ載せ替え |
| [C-04 計画正本](finished/20260604-c04-gui-surface-planning-draft.md)               | §5 Margins 面・§7.2 A12 改訂（案 B は保留→本波で着手）                      |
| [C-04 slice-memo](design/20260604-c04-slideshow-margins-surface-slice-memo.md) | 案 B の操作削減なし・載せ替えのみ（M1–M4 pass 済み）                            |
| [P-08 slice-memo](design/20260608-p08-main-margins-drawer-slice-memo.md)       | 本波の配置・gate checklist（§9）                                     |
| [P-07 完了記録](finished/20260606-p07-slideshow-drawer-open-state-planning.md)     | Drawer 開閉視認性 — **本波でスタイル再利用**                                |
| [harite-gui-spec.md](../specs/gui/harite-gui-spec.md)                          | 実装正本（合意後に §3 を 2-tab + Main Drawer へ改訂）                      |


**きっかけ:** P-04 で Main action cluster を整理済み。Slideshow は正面 + Drawer 化済み（C-04b / P-07）だが、**Margins だけ専用 notebook tab が残り非対称**。

**採用案:** **全面 tab 統合はしない**。Main 正面に margin 十字（4 spin）を常時見せ、embed / margin text / position は **Drawer** 内（C-04 案 B）。

---

## 1. 現状


| 面               | 構成                                                                                    |
| --------------- | ------------------------------------------------------------------------------------- |
| **notebook**    | 3 tab — `Main` / `Margins (for each display)` / `Slideshow`                           |
| **Margins tab** | cross-grid（4 spin + center stack: embed / notebook / position）。Wave a で冗長 label は削除済み |
| **Main tab**    | compose grid + action cluster（P-04 済み）                                                |
| **Slideshow**   | 正面中核 + `More slideshow options…` Drawer（P-07 開閉スタイル）                                  |


実装入口: Qt `qt_tab_margins.py` / `qt_layout_builders.py`、GTK `gtk_tab_builders.build_margins_tab_section`。

---

## 2. 目標（案 B — 操作は維持・載せ替えのみ）

### 2.1 notebook

- tab は **`Main`** と **`Slideshow (...)` の 2 枚**にする。
- `Margins (for each display)` **page を廃止**（widget は Main へ移設）。

### 2.2 Main tab 正面（上から）

1. **margin cross-grid の外周 4 spin**（top / left / right / bottom）— compose grid を囲む配置（C-04 slice 案 B）。
2. **compose grid**（現行どおり — L/R direction・Open・path・Swap）。
3. **action cluster**（P-04 済み — Preview / Optimize / Apply）。
4. （任意 spacer）
5. **Drawer トリガ** — 提案: `More margin options…`（rename 可。Slideshow の `More slideshow options…` と対称）。

**常時見せる意図:** Drawer を開かなくても **4 辺 margin 数値**は編集可能（discoverability）。embed / text / position は補助面。

### 2.3 Main tab — Margins Drawer 内

現 Margins tab の **center stack** をそのまま移す（削除・統合しない）:


| ブロック                 | 内容                                                            |
| -------------------- | ------------------------------------------------------------- |
| embed pattern        | `Off` / `Settings` / `Text only` / `Both` radio               |
| margin text notebook | `Settings` + `Text` page、max-lines spin                       |
| position selector    | L/R × Top/Bottom radio（Main direction 十字とは **別 widget 群**のまま） |


tooltip 契約は現 gui-spec §3 Margins と **同一**（line limits / Rule / Current behavior）。

### 2.4 Drawer 開閉視認性

- **P-07 と同型** — chrome tint 背景、上辺 1px `mid`、chevron up/down、トリガ pressed 枠。
- 実装は `slideshow_options_drawer` のパターンを **共通化または margins 用モジュールで再利用**（palette ベース、固定 hex 単独不可）。

---

## 3. 非採択（再確認）


| 案                                          | 理由                                     |
| ------------------------------------------ | -------------------------------------- |
| Main 1 tab に margin 操作を **すべて**戻す（全面統合）    | C-04 §7.2 / glade 解釈 — 密度・parity 悪化    |
| margin spin を Drawer 内だけにする                | 案 B でも 4 spin は正面常設（slice-memo §案 B 表） |
| Main direction 十字と position selector の自動統合 | 意味論が異なる — 別 widget のまま                 |


---

## 4. spec 改訂タッチポイント（合意後）


| 正本                      | 変更                                                                   |
| ----------------------- | -------------------------------------------------------------------- |
| gui-spec §3 layout      | notebook **2 tab**；Margins tab 節を **Main tab + Margins Drawer** へ再構成 |
| gui-spec §3 補助説明面一覧     | Margins tab tooltip → Main margin widget / Drawer 内へ                 |
| gui-spec §8 margin text | 挙動不変。載せ場所のみ Main Drawer                                              |
| （参照）slideshow-spec      | 変更なし                                                                 |


---

## 5. 実装タッチポイント（草案）


| 層            | 内容                                                                                       |
| ------------ | ---------------------------------------------------------------------------------------- |
| **views**    | `margins_options_drawer.py`（新規）または drawer スタイル共通化                                        |
| **Qt**       | `qt_tab_main.py` — margin cross-grid + drawer；`qt_layout_builders.py` — Margins tab 登録削除 |
| **GTK**      | `gtk_tab_builders.py` — Main へ margin 部品移設；`gtk_backend.py` — tab 数 2                    |
| **registry** | `marginsTab` 等の object key — 移設先に合わせて更新（後方互換は不要、テスト同期）                                   |
| **tests**    | `tests/gui/` — tab 数・widget パス期待値                                                        |


**widget 名:** 可能な限り既存 logical name（`spinMarginTop` 等）を **維持**し、signal wiring の差分を抑える。

---

## 6. スコープ / スコープ外


| 含む                                         | 含まない                           |
| ------------------------------------------ | ------------------------------ |
| 案 B 載せ替え（2 tab + Main Drawer）              | margin 算法・preflight 規則の変更      |
| 4 spin + Drawer 内 center stack の **全機能維持** | plugin capability パネル（C-03 縮小） |
| Qt + GTK parity                            | Drawer 開閉アニメーション（高さ tween）     |
| P-07 同等の Drawer 視認性                        | Slideshow Drawer の再設計          |


---

## 7. 着手 gate checklist（§9 — オーナー記入）

詳細配置は [P-08 slice-memo](design/20260608-p08-main-margins-drawer-slice-memo.md)。視覚参照: [C-04 slice HTML](design/20260604-c04-slideshow-margins-surface-slice.html) §5 右（案 B）。


| #    | 論点                                     | 提案           | オーナー |
| ---- | -------------------------------------- | ------------ | ---- |
| P8-1 | notebook 2 tab（Main + Slideshow）       | 採用           | **pass** |
| P8-2 | 4 margin spin を Main 正面常設（compose 外周）  | 採用           | **pass** |
| P8-3 | embed / notebook / position は Drawer 内 | 採用           | **pass** |
| P8-4 | トリガ label `More margin options…`       | 採用（rename 可） | **pass** |
| P8-5 | Drawer 開閉 = P-07 同型スタイル                | 採用           | **pass** |
| P8-6 | position selector は Main 十字と統合しない      | 維持           | **pass** |
| P8-7 | margin tooltip 3 件                      | 現 gui-spec 表のまま載せ替え | **pass** |


**gate 通過:** P8-1〜P8-7 すべて **pass**（2026-06-08。C-04 案 B 先行合意を含む）。

**次:** gui-spec §3 改訂 PR → テスト → impl（GTK/Qt）。

---

## 8. 実装フェーズ案


| 段   | 内容                                                                          |
| --- | --------------------------------------------------------------------------- |
| 0   | 本書 + [slice-memo](design/20260608-p08-main-margins-drawer-slice-memo.md) 合意 |
| 1   | gui-spec §3 改訂（docs PR）                                                     |
| 2   | drawer モジュール + Qt Main レイアウト移設                                              |
| 3   | GTK parity + object registry 更新                                             |
| 4   | `tests/gui/` 期待値更新                                                          |


---

## 9. 関連 ID


| ID        | 関係                          |
| --------- | --------------------------- |
| C-04 §7.2 | 本波は保留だった案 B の実装             |
| P-04      | Main 正面が整理済み — Drawer 追加の前提 |
| P-07      | Drawer 視認性の再利用元             |
| C-03      | 着手しない（構想保持のまま）              |



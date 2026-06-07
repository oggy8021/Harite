# P-08 3層比較（spec / tests / impl）

実施日: 2026-05-31（マージ後）  
対象: PR #436 — Main + Margins Drawer（C-04 案 B）+ options drawer 枠伸縮（Option B）  
照合源: `docs/specs/gui/harite-gui-spec.md` §3 / `tests/gui/test_p08_main_margins_drawer.py` 他 / `src/harite/gui/{views,adapters_qt,adapters}/`

## 参照 spec

| 文書 | 要点 |
|------|------|
| `docs/specs/gui/harite-gui-spec.md` | §3 — 2 tab notebook、Main margin cross-grid + Margins Drawer、Slideshow 正面 + Drawer |
| `docs/working/finished/20260608-p08-main-margins-drawer-planning-draft.md` | P8-1〜P8-7 gate、案 B 載せ替えのみ |
| `docs/working/design/20260608-p08-main-margins-drawer-slice-memo.md` | 配置・registry 維持 |

## 凡例

| 記号 | 意味 |
|------|------|
| OK | 仕様・テスト・実装が整合 |
| INTENTIONAL | 仕様文言と表現は異なるが、意図どおりの実装 |
| SPEC-STALE | 実装・試験済み事実と gui-spec 記述が不一致（正本要更新） |
| ⚠️ | テスト薄い／GTK 既知 backlog |
| BACKLOG | スコープ外または別 ID で追跡 |

---

## 1. Notebook（P8-1）

| 層 | 内容 | 判定 |
|----|------|------|
| 仕様 §3 L95 | tab 順 `Main` → `Slideshow (...)` の **2 枚** | — |
| Qt tests | `test_command_tabs_has_two_pages`, `test_no_margins_notebook_tab`, `test_center_body_builds_two_tabs_without_margins_page` | OK |
| Qt impl | `qt_layout_builders.build_center_body_section` — 2 `addTab` のみ | OK |
| GTK tests | `test_runtime_backend_adds_main_margins_drawer_and_syncs_owner_state` — `len(notebook.pages)==2` | OK |
| GTK impl | `gtk_backend` — Main + Slideshow `append_page` のみ | OK |

**判定: OK**

---

## 2. Main tab 正面（P8-2, P8-4）

| 要件 | gui-spec | tests | impl | 判定 |
|------|----------|-------|------|------|
| 4 margin spin 常設 | §3 L128–129 | `test_margin_spins_visible_on_main_face` | `build_margin_cross_grid` on `main_col` | OK |
| compose grid | §3 L130–134 | `test_margin_cross_grid_wraps_compose_grid` | spin 外周が `compose_grid` を包含 | INTENTIONAL（§3 は「cross-grid → compose」と列挙するが、物理配置は 1 widget 入れ子） |
| action cluster 順 | §3 L128 | `test_main_tab_vertical_order_margin_action_drawer` | cross → action → trigger → drawer | OK |
| トリガ label | §3 L154 `More margin options…` | `test_margins_drawer_hidden_by_default` | `margins_options_drawer.MORE_LABEL` | OK |
| registry 論理名維持 | planning §5 | `test_margin_widgets_remain_in_registry` | `qt_object_registry` / GTK registry | OK |

**判定: OK**（compose 入れ子は INTENTIONAL）

---

## 3. Margins Drawer 内容（P8-3, P8-6）

| 要件 | gui-spec | tests | impl | 判定 |
|------|----------|-------|------|------|
| embed / notebook / position は Drawer 内 | §3 L155–158 | `test_embed_and_position_widgets_live_in_drawer` | `build_margins_options_drawer` | OK |
| direction 十字と position 独立 | §3 L158, §8 L578 | registry に両系統 widget 共存 | 別 widget 群のまま | OK |
| Drawer 初期非表示 | §3 | `test_margins_drawer_hidden_by_default` | `setVisible(False)` / Gtk revealer | OK |
| 常設 notes block なし（C-04a） | §3 L159 | 正面・Drawer face に label 行なしを builder 単体で確認 | Qt: tooltip のみ。GTK: `lblPriorityRule` 等は **registry/sync 用**で tab 面未配置 | OK |

**判定: OK**

---

## 4. Drawer 開閉視認性（P8-5）

| 層 | 内容 | 判定 |
|----|------|------|
| 仕様 §3 L171 | P-07 同型 — chrome tint、1px 上辺、chevron、More/Fewer | — |
| Qt tests | `test_margins_drawer_toggle_applies_p07_open_state_styles` | OK |
| Qt impl | `margins_options_drawer.apply_margins_options_drawer_open_state` | OK |
| GTK impl | Gtk CSS class + `toggle_margins_options_drawer` | OK（⚠️ Qt ほど細かい自動テストなし） |

**判定: OK**（GTK スタイルは ⚠️ 手動／既存 revealer テストのみ）

---

## 5. Margin tooltip（P8-7）

| 載せ先 | gui-spec §3 L160–168 | Qt impl | tests | 判定 |
|--------|----------------------|---------|-------|------|
| embed mode label | line limits 文 | `MARGIN_TEXT_LINE_LIMITS_TOOLTIP` | — | ⚠️ 専用 assert なし |
| text entry | 同上 | 同上 | — | ⚠️ |
| position selector | Rule 文 | `MARGIN_PRIORITY_RULE_TOOLTIP` | — | ⚠️ |
| cross-grid / 辺 label | behavior 文 | `MARGIN_BEHAVIOR_TOOLTIP` | — | ⚠️ |
| center stack（任意） | 3 文連結 | `MARGIN_CROSS_GRID_TOOLTIP` on stack | — | ⚠️ |

**判定: OK（impl）/ ⚠️（P-08 専用 tooltip テスト未追加）** — C-04 既存 `margins_surface` 契約を流用。

---

## 6. Options Drawer — 枠伸縮（Option B）

マージ後の実装事実。**旧 gui-spec 未記載**（#436 で Main + Slideshow 両方に適用）。

| 層 | 内容 | 判定 |
|----|------|------|
| 期待挙動（試験・オーナー確認） | 開く: タブ中核の Y 位置を維持し **top-level window の高さのみ増加**。閉じる: **開く前の window 高さに復元** | — |
| 共有 module | `drawer_window_resize.py` — `grow_window_after_drawer_expand` / `shrink_window_after_drawer_collapse` | OK |
| Main 配線 | `margins_options_drawer._sync_margins_drawer_window_frame`, `tab_attr=main_col` | OK |
| Slideshow 配線 | `slideshow_options_drawer._sync_slideshow_drawer_window_frame`, `tab_attr=slideshow_tab_box` | OK |
| Qt tests | `test_drawer_window_resize.py`, `test_margins_options_drawer` / `test_slideshow_options_drawer` toggle 復元、`test_slideshow_drawer_grows_window_without_shifting_core` | OK |
| GTK | 同一 toggle 経由で `drawer_window_resize` 呼び出し | OK（⚠️ 枠伸縮の GTK 統合テストなし） |
| Slideshow 旧挙動 | §3 L175 の top/bottom spacer による上寄せシフト | **廃止**（SPEC-STALE） |

**判定: OK（impl）— gui-spec §3 に追記済み（本 audit 反映 PR）**

---

## 7. Slideshow tab 正面（P-08 波及 + 既存 spec）

| 要件 | gui-spec（改訂前 L175） | tests | impl（#436 後） | 判定 |
|------|-------------------------|-------|-----------------|------|
| 正面構成 | chip + **top spacer** + profile + … + **bottom spacer** | `test_slideshow_tab_has_no_vertical_stretch_spacers` | expanding stretch **削除** | SPEC-STALE → 正本更新 |
| profile row | §3 L177 Qt | Qt `slideshow_profile_row` | GTK **未実装** | OK Qt / BACKLOG GTK（P-03 audit 既知） |
| Drawer 枠伸縮 | 未記載 | `test_slideshow_drawer_grows_window_without_shifting_core` | Option B 適用 | SPEC-STALE → 正本更新 |
| Drawer 視認性 P-07 | §3 L187 | 既存 slideshow open-state tests | 維持 + 枠伸縮追加 | OK |

**判定: SPEC-STALE 2 件は gui-spec 改訂で解消**

---

## 8. Widget 棚卸し（主要 registry）

| 論理名 | gui-spec 意図 | Qt | GTK | 判定 |
|--------|---------------|----|----|------|
| `btnMarginsOptionsMore` | Drawer トリガ | OK | OK | OK |
| `marginsOptionsDrawer` | Drawer 面板 | OK | OK（revealer 可） | OK |
| `spinMargin*` / `top_margin_spin` | Main 正面 4 spin | OK | OK | OK |
| `radMarginTextMode*` / embed | Drawer 内 | OK | OK | OK |
| `txtMarginText` / `margin_text_entry` | Drawer Text page | OK | OK | OK |
| `radMarginTextPosition*` | Drawer position | OK | OK | OK |
| `lblCurrentMargins` 等 | sync 用（面非常設） | registry のみ | registry のみ | INTENTIONAL |

---

## 9. 検出ギャップと対応

### 本 audit で正本へ反映した事項

| 項目 | 対応 |
|------|------|
| Slideshow §3 の top/bottom spacer 記述 | gui-spec §3 — spacer 削除、正面縦積みを実装順に合わせる |
| Drawer 枠伸縮 Option B | gui-spec §3 — Main / Slideshow 共通節として追記 |
| compose grid の入れ子 | gui-spec §3 L128 — cross-grid 内包と明記 |

### 意図的に残す項目（follow-up）

| 項目 | 理由 |
|------|------|
| P-08 専用 margin tooltip テスト | impl は `margins_surface` 既存契約。回帰は phase4/5 + 手動で足りる |
| GTK Drawer 枠伸縮の自動テスト | Qt で frame resize ロジック検証済み。GTK は `resize` / `set_default_size` 分岐のみ |
| `build_margins_tab` レガシー builder（Qt/GTK） | 未配線 dead code。削除は別 cleanup |
| GTK `combo_slideshow_profile` | C-02 / P-03 audit 既知 backlog |

---

## 10. 実機試験（オーナー確認・2026-05-31）

| 項目 | 結果 |
|------|------|
| Main More/Fewer、手動リサイズなし | クロスグリッド固定、枠のみ伸縮、閉じて復元 |
| Slideshow More/Fewer | 上寄せシフト解消、枠伸縮、閉じて復元 |
| 違和感 | **解消**（マージ前フィードバック反映済み） |

---

## 結論

**P-08 の spec 契約（2 tab・Main 正面 4 spin・Drawer 載せ替え・P-07 視認性）は tests/impl と一致。**  
**#436 追加の Option B 枠伸縮**は旧 gui-spec 未記載だったため、本 audit に基づき **gui-spec §3 を事実ベースで更新**する。

**P-08 完了** — PR #436 マージ済み。planning / 本 audit の working コピーを `finished/` へ移動。

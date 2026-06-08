# MAT-01b 改修方針ドラフト — 原寸配置・align 座標系の母体回帰

最終更新: 2026-06-09  
親ログ: [maturation-20260609-qt-common.md](../../online-issues/maturation-20260609-qt-common.md#mat-01b--optimize-が小画像を拡大し-align-座標系が母体と乖離)  
母体: `C:\Users\oggy_\Develop\Repos\wallpaperoptimizer`（`WallpaperOptimizer/Core.py`）

**一行結論:** Harite の `optimize` 幾何は reformation 以降 **母体から逸脱**している（無条件 fit + upscale、margin-inner cell への align）。**母体の基底ロジックと貼り方は変えない** — `contains` → 必要時のみ `_downsizeImg` → display 矩形への `_allocateImg` → `_mergeWallpaper` へ **回帰**する。

---

## 1. 背景

- 熟成運転 MAT-01（xxAlign が効かない）の調査で、Qt handler 不具合（#442）に加え **core の upscale** が余白を潰し align を無効化していることが判明。
- 母体 `wallpaperoptimizer` を洗った結果、オーナー記憶（**原寸志向・Optimize に拡大は含めない**）は **正しい**。記憶違いではない。
- `scaling` 設定の無効性は **合意済み**。本件の焦点は settings キーではなく **配置パイプラインの回帰修正**。

---

## 2. オーナー方針（不変）

| 項目 | 方針 |
| --- | --- |
| 基底ロジック | **母体と同型を維持**（変更しない） |
| 貼り方 | `_mergeWallpaper` 型（右画像は `lScreen.width` オフセットして paste） |
| Optimize の意味 | 配置・必要なら縮小。**小画像の無理な拡大は含めない** |
| align | **原寸（または縮小後）** の画像を、各 L/R **display 矩形**の中で限界まで寄せる |
| margins | **収納判定と縮小上限**（L: `(L,0,T,B)` / R: `(0,R,T,B)`）。align の座標原点を margin-inner にしない |
| `scaling` 設定 | 引き続き optimize に影響させない（復活しない） |

---

## 3. 母体照合（wallpaperoptimizer）

### 3.1 計算優先度

```
_bindingImgToScreen
  → per-side margins（非対称）
  → _checkContain（containsPlusMergin）
  → _downsizeImg（収まらないときのみ・縮小のみ）
  → _allocateCenter
  → _allocateImg（align / valign）
  → _mergeWallpaper（paste）
```

### 3.2 拡大なし

- `containsPlusMergin`: 画像 + margins が各 `lScreen` / `rScreen` に収まれば **原寸のまま**次へ。
- `_downsizeImg`: `Img.Size > (screen - margins)` のときだけ二段 proportional shrink。**`scale > 1` 経路なし**。

参照: `WallpaperOptimizer/Core.py` — `_checkContain`, `_downsizeImg`, `_optimizeWallpapers`

### 3.3 align 座標系

- 初期 `(0,0)` = left / top（display 矩形の原点）。
- `center` / `right` / `middle` / `bottom` は **各 display の全矩形**（`tmpScreen.start`〜`end`）に対するオフセット。
- margins は paste 座標の `+= ml` ではなく、**contains / downsize の制約**として効く。

---

## 4. Harite 現行との diff

| 観点 | 母体 | Harite 現行 (`src/harite/core.py`) |
| --- | --- | --- |
| 小画像 | 原寸維持 | `_scale_to_fit` で **常にリサイズ・拡大あり** |
| resize 条件 | `contains` 失敗時のみ | **毎回** cell へ fit |
| scale 式 | 実質 `≤ 1`（down-only） | `min(max_w/w, max_h/h)`（**> 1 可**） |
| align 面 | 各 `lScreen` / `rScreen` 全矩形 | margins 差引き後 **cell 内余白** |
| margins（two-screen） | L: `(L,0,T,B)` / R: `(0,R,T,B)` | 左右とも `(ml,mr,mt,mb)` を cell 計算に使用 |
| 右画像 paste | `x += lScreen.width` 後 paste | split_x + cell 内 offset |
| テスト | （母体側） | `test_upscale_when_target_larger` が upscale を **期待** |

Harite GUI 注釈 `Rule: margins define area; align/valign act inside it` は **現行 core 実装の説明**であり、**母体の優先度ではない**。MAT-01b 完了時に gui-spec / 注釈も母体整合へ更新する。

---

## 5. 改修方針（実装ドラフト）

### 5.1 core — 配置パイプライン差し替え

**目標:** `optimize_wallpapers` の幾何部分を母体パイプラインに寄せる。公開 API（引数名・戻り値型）は維持。

| ステップ | 改修内容 |
| --- | --- |
| A | `_scale_to_fit` の無条件適用をやめる |
| B | 母体相当の `_image_fits_with_margins(img, screen_w, screen_h, margins_tuple) -> bool` を導入 |
| C | 収まらないときのみ母体相当 `_downsize_to_fit_margins(...)`（二段 shrink・down-only） |
| D | align / valign は **display 矩形**（single: 全面、two-screen: 各半分）に対して適用。初期 left/top、toggle で center/right・top/bottom |
| E | paste: 右スロットは `x_offset = left_display_width`（母体 `_mergeWallpaper` 同型） |
| F | `PlacementResult.scale` は down-only 時 `≤ 1`、原寸時 `1.0` |

**非スコープ（今回やらない）:**

- `scaling` 設定の有効化、`fill` / `crop` user-facing 露出
- embed 描画ロジックの全面書き換え（margin region 規則は別途。配置との整合は確認する）
- GTK / Qt UI の toggle 配線（MAT-01 / #442 で対応済み）

### 5.2 positioning / GUI 層

- `form_state.align` / `valign` の L/R ペア表現は **維持**（母体の per-side option と同型）。
- `refresh_current_state_labels` / priority rule 文言を **母体優先度**に合わせて更新。
- Preview 経路（`main_window_preview.py`）も同じ幾何を共有すること。

### 5.3 spec 更新

| 文書 | 更新内容 |
| --- | --- |
| [harite-core-spec.md §4.1](../../specs/core/harite-core-spec.md) | down-only、display 矩形 align、非対称 margins、paste 規則を正本化 |
| [harite-gui-spec.md §3 Main](../../specs/gui/harite-gui-spec.md) | priority rule 文言・toggle 期待動作 |
| maturation MAT-01 / MAT-01b | 完了条件・検証手順 |

### 5.4 テスト更新

| 現状 | 改修後 |
| --- | --- |
| `test_upscale_when_target_larger`（upscale 期待） | **削除または反転** — 小画像は原寸・scale=1.0 |
| `test_compute_placement_upscales_if_allowed` | 同上 |
| single/dual smoke | 大画像縮小・小画像原寸・align で x/y が変わるケースを追加 |
| 母体 parity | 代表サイズ（小画像 + margins + L/R align）の golden placement 座標 |

---

## 6. MAT-01 との関係

| ID | 層 | 状態 |
| --- | --- | --- |
| MAT-01 | Qt `on_toggle_position` 配線 | #442 着手済み |
| MAT-01b | `core.optimize_wallpapers` 幾何 | **本ドラフト** |

#442 だけでは Optimize 出力の x 寄せ体感は直りきらない。**MAT-01 マージ後も MAT-01b は改修系で継続必須**。

---

## 7. 着手順・PR 分割案

1. **#442** — MAT-01 handler（マージ待ち）
2. **MAT-01b PR-1** — core 幾何回帰 + spec §4.1 更新 + テスト反転（GTK/Qt 共通）
3. **MAT-01b PR-2**（必要なら）— GUI priority 文言・preview 同期・回帰確認メモ

実装ブランチ名案: `fix/mat-01b-native-placement`

---

## 8. 完了条件（実機）

- [ ] 小画像（例: 400×300）を 1920×1080 + margins=0 で Optimize → **拡大されない**（原寸 paste）
- [ ] 同上で Left-* / Right-* / Top-* / Bottom-* toggle → **出力画像で位置が変わる**
- [ ] 大画像（cell を超える）→ **縮小のみ**（母体と同様はみ出し防止）
- [ ] two-screen: L/R 非対称 margins で左右それぞれ独立に寄せ・収納
- [ ] `scaling` 設定を変えても結果不変（合意済み）

---

## 9. 参照コード（母体）

| ファイル | 関数 |
| --- | --- |
| `WallpaperOptimizer/Core.py` | `_optimizeWallpapers`, `_checkContain`, `_downsizeImg`, `_allocateImg`, `_mergeWallpaper` |
| `WallpaperOptimizer/Imaging/Rectangle.py` | `containsPlusMergin` |
| Harite 現行 | `src/harite/core.py` — `_scale_to_fit`, `optimize_wallpapers`（差し替え対象） |

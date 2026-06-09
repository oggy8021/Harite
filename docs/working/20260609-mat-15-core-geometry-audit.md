# MAT-15 — core 幾何総点検（align / margin / MAT-14 scale）

最終更新: 2026-06-09  
親: [maturation-20260609-qt-common.md §MAT-15](../online-issues/maturation-20260609-qt-common.md#mat-15--align--margin--ストレッチの-core-幾何総点検)  
正本: [harite-core-spec.md §4.1](../specs/core/harite-core-spec.md)、[harite-gui-spec.md §3](../specs/gui/harite-gui-spec.md)

## 一行結論

**core 配置パイプラインは MAT-01b 母体回帰後も整合している。** ユーザー誤解の主因は GUI 注釈「margins define area; align/valign act inside it」が **旧実装・誤解を助長**していたこと。MAT-14 は **元画像サイズ決定の前段**として正しく挿入されている。`scaling` 設定は幾何に未使用（合意どおり）。

---

## 1. 点検スコープ

| 要素 | 点検対象 |
| --- | --- |
| display slot | `_resolve_display_slots`（single / two-screen / 非対称 margins） |
| 画像サイズ | `_resolve_intentional_image_dimensions`（100% = MAT-01b、125–200% = MAT-14） |
| align / valign | `_allocate_on_display`（スロット全面） |
| paste | `origin + inner` |
| `scaling` 設定 | `optimize_wallpapers` / `compute_placement` 引数の無効性 |
| GUI 注釈 | priority rule / margins drawer tooltip |
| Preview / CLI | `main_window_preview`（配置幾何は共有せず、apply 向け表示のみ） |

---

## 2. 計算優先度（現行・母体準拠）

```
per input image:
  1. display slot  (origin_x/y, screen_w/h, side_margins)
  2. image size    MAT-14 % → native / intentional upscale / down-only
                   margins → 収納判定 + 縮小上限のみ
  3. align/valign  スロット全面 (0,0)–(screen_w, screen_h)
  4. paste         composite 上へ origin + inner
```

**margins は align の「内側セル」を切らない。** 収まる最大画像サイズを `screen - margins` で制限し、align は残ったスロット内で `(nw, nh)` を寄せる。

---

## 3. MAT-14 との接続

| 段 | 挙動 |
| --- | --- |
| 100% | `_resolve_native_dimensions`（原寸 or down-only） |
| 125–200% | 元画像 × 係数 → 収納判定 → 収まらなければ `ValueError` |
| align 後 | upscale 後の `(nw, nh)` に対して `_allocate_on_display` |

キャンバス解像度（`target_resolution`）は **MAT-14 では変更しない**（#459 実機確認済み）。

---

## 4. 発見事項

### 4.1 修正済み（本 PR）

| ID | 内容 | 対応 |
| --- | --- | --- |
| G-01 | GUI priority rule が margin-inner align を示唆 | 文言を core-spec 整合へ更新（Qt/GTK/spec） |
| S-01 | core-spec §4.1 に MAT-14 計算順・`scaling` 無効の明記不足 | §4.1 追記 |

### 4.2 仕様どおり（改修不要）

| ID | 内容 |
| --- | --- |
| C-01 | `scaling=fit` / `fill` で配置結果は同一（テスト追加） |
| C-02 | two-screen 非対称 margins `L:(ml,0,mt,mb)` / `R:(0,mr,mt,mb)` |
| C-03 | left/top align はスロット原点 `(0,0)` — 小画像は margin 帯に重なることがある（母体同型） |
| C-04 | `PlacementResult.scale` — 100% 時 `≤ 1.0`、MAT-14 upscale 時 `> 1` |

### 4.3 follow-up（別 PR 可）

| ID | 内容 | 提案 |
| --- | --- | --- |
| F-01 | CLI preview / `OptimizeRequest` に `l_display_scale` 未反映 | GUI-only 機能として doc 注記。CLI 露出時に mapper 拡張 |
| F-02 | `compute_placement` は margins / MAT-14 非対応（単純中央・zero margins） | CLI 補助 API として現状維持。必要なら doc のみ |

---

## 5. テスト追加

- `tests/core/test_mat15_geometry_audit.py` — scaling 無効、margin 優先度、MAT-14 + align 合成

---

## 6. 検証コマンド

```bash
python -m pytest tests/core/test_mat15_geometry_audit.py tests/core/test_align_valign.py tests/test_display_scale.py -q
```

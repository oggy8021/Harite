# P-01 / P-02 widget slice — 評価メモ

- mock: [20260601-p01-p02-lr-swap-clear-slice.html](20260601-p01-p02-lr-swap-clear-slice.html)
- 第2波（feature-overview）: P-01 (#353) + P-02 (#358)
- 段階: **design slice 合意** → gui-spec → tests → impl（各段階でマージ許可）

## 目的

1. **P-01**: Main / Slideshow の L/R 値をワンクリックで入れ替え（path / srcdir の swap のみ）。
2. **P-02**: Slideshow の Srcdir-L/R を **同時に** クリア（テストや条件変更のやり直し用）。

## 配置案（本 mock の提案）

| タブ | 位置 | 新 widget |
| --- | --- | --- |
| Main | compose grid **中央列**（`pick_state_label` の下） | Swap L/R（icon + tooltip） |
| Slideshow | srcdir 行 L/R ブロック **の間** | Swap L/R + Clear both（縦積み） |

### 採用理由

- issue #353 メモ「画面中央部に swap」→ Main は既存 center 列を拡張（新列追加なし）。
- Slideshow は `_build_srcdir_row()` が L | gap | R 構造のため、gap にまとめると P-01/P-02 を 1 塊で合意できる。
- Main の per-side Clear-L/R は既存のまま（P-02 は Slideshow のみ）。

## Icon / ラベル案

| 操作 | Lucide | ラベル | 備考 |
| --- | --- | --- | --- |
| Swap | `arrow-left-right` | tooltip `Swap L/R` | リポジトリ未同梱 → impl 時に SVG 追加 |
| Clear both | `folder-x`（既存） | tooltip `Clear both` | Main Clear-L/R と同系。icon-only + tooltip |

- ボタンは **icon-only**（Main の Clear-L/R と同 tone）。Slideshow 中央は縦 2 ボタン。
- 代替案: Slideshow Clear both に短いテキストラベル — 中央幅が狭い場合は要再検討。

## 振る舞い（spec 化予定の要点）

### Swap（Main）

- Owner: `input_path_l` ↔ `input_path_r` を swap。
- `input_display_l` / `input_display_r` を `format_input_display()` で再描画。
- direction toggle・pick state・apply 状態は触らない。
- ファイル移動・registry 更新なし。

### Swap（Slideshow）

- Owner: `slideshow_srcdir_l` ↔ `slideshow_srcdir_r` を swap。
- srcdir ラベル（`L:` / `R:` 行）を更新。
- 実行中 slideshow への影響は gui-spec 既存ルールに従う（spec 段階で明記）。

### Clear both（Slideshow）

- 両 srcdir を `""` に。個別 clear ボタンは **第2波では作らない**。
- 両方空 → Start 不可（現行 spec 維持）。

### Handler 名（spec 草案 — 合意後に gui-spec へ）

| Handler | 用途 |
| --- | --- |
| `on_swap_input_paths()` | Main L/R path swap |
| `on_swap_slideshow_srcdirs()` | Slideshow L/R srcdir swap |
| `on_clear_slideshow_srcdirs()` | Slideshow 両方 clear |

## 評価チェックリスト（オーナー）

ブラウザで HTML を開き、以下を確認:

- [ ] Main: center 列の Swap が L/R パネル間の視覚的「中央」に見えるか
- [ ] Main: pick state ラベルと Swap の縦バランス
- [ ] Slideshow: L/R srcdir ブロック間の Swap + Clear both が窮屈でないか
- [ ] icon-only + tooltip で Main Clear-L/R とトーンが揃うか
- [ ] Clear both を simultaneous のみで足りるか（個別 clear は defer でよいか）

## 合意後の次ステップ

1. 本 design PR マージ（オーナー許可後）
2. `docs/specs/gui/harite-gui-spec.md` に widget / handler / 起動時 sync 追記
3. tests → impl（Qt のみ第2波; GTK は既存 parity 方針に従い spec で明示）

## スコープ外（第2波）

- P-03 (#359) 単一ディスプレイ無効化
- Slideshow 個別 srcdir clear
- path / srcdir swap 時の undo や確認ダイアログ

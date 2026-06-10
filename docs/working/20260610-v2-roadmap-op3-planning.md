# v2.0.0 ロードマップ固め — op3 観測後（2026-06-10）

親: [maturation §v2.0.0](../online-issues/maturation-20260609-qt-common.md)  
前提: [op3 観測](20260610-mat-08-viper3-slideshow-op3-observation.md)、main `0672e7d`（#464 + #465）

## オーナー判断（2026-06-10）

| 判断 | 内容 |
| --- | --- |
| **MAT-02b** | op3 で **勝ち筋確定**（NDL tick + outcome + apply 一連）。残課題は timer 方針・長時間 CODH のみ |
| **MAT-10** | **後回し解除 → 実施 backlog に載せる**（Q-01 後に調査・実装着手） |
| **MAT-18（新規）** | NDL `searchbytext` + キーワード UI（CODH 同型）。facet ランダムは書簡・文書スキャン寄りで品質不足 |
| **MAT-14b（新規）** | 小画像向け **auto 倍率**（≠ fit/fill、≠ MAT-14 手動 %） |

---

## おおよその着手順（更新）

| 順 | ID | 状態 | 備考 |
| --- | --- | --- | --- |
| 1 | ~~MAT-17~~ | **完了** #463 | CLI slideshow + settings |
| 2 | ~~MAT-02b 主戦場~~ | **op3 完了** #462–#465 | 残: apply 失敗時 timer |
| 3 | **Q-01** | 未着手 | v2.0.0 骨格（GTK メンテ対象外） |
| 4 | **MAT-10** | **実施に載せる** | 江戸切絵図 / edo-maps 雰囲気 source |
| 5 | **MAT-18** | planning | NDL テキスト類似検索 preset（試験優先） |
| 6 | **MAT-14b** | planning | auto 倍率（Main + Slideshow） |

**並行可:** MAT-18 の API 試験は Q-01 / MAT-10 と独立。MAT-14b は core + settings 浸透のため MAT-10 より先に着手してもよい（オーナー判断待ち）。

---

## MAT-18 — NDL `searchbytext` キーワード preset

### 背景（op3）

- `randomwithfacet` は **技術的には成功**（tick 毎取得・上書き・apply 一連）。
- 実機品質: **書簡・文書スキャンばかり**で「絵図」期待に届かないケースが多い。
- 既存調査（[C-01-E NDL](../working/finished/20260603-c01-e-ndl-tsugidigi-inventory.md)）では `searchbytext` を **対象外**としていた（キーワード UI なし）。**op3 後に方針転換。**

### API（試験 URL）

```
GET https://lab.ndl.go.jp/dl/api/illustration/searchbytext?keyword2vec={keyword}
```

例: `keyword2vec=ペンギン`（オーナー試験例）

### 取り込み方針（ドラフト）

| 項目 | 案 |
| --- | --- |
| preset 形 | 新 preset `ndl-search-keyword`（仮）または既存 facet preset に **モード切替** — **試験後に決定** |
| キーワード UI | **CODH 同型** — Manage Presets の `keyword(CODH)` に隣接または `keyword(NDL)` 専用行。`harite-settings.json` に `ndl_keyword`（仮） |
| sync / tick | 層 A 入口を `randomwithfacet` → `searchbytext` に差し替え。IIIF 以降は §15.3 と同型 |
| op log | `NDL_META_URL` の url に `searchbytext` を記録（既存ステップ流用可） |
| ゲート | 返却 0 件・IIIF 404 再試行（既存 5 回契約）。利用規約は §15.3 帰属と同型 |

### 試験計画（実装前）

1. `curl` / 手動で `searchbytext?keyword2vec=ペンギン` → Illustration 1 件 + IIIF GET
2. 書簡寄り facet（例: `graphic_illust`）と品質比較
3. キーワード複数（動物・風景・挿絵）で op log 付き viper3 短時間観測

---

## MAT-14b — auto 倍率（≠ fit / fill、≠ MAT-14 手動 %）

### 背景（op3）

- MAT-01b 原寸 + MAT-14 手動 % で小画像は中央にポツンしうる。
- NDL 切り出し図版は **短辺が display 解像度に対して小さい**ことが多い。
- **ユーザーが毎回 125%/150% を選ぶ前に**、閾値ベースで自動 upscale したい（product 判断。MAT-01b の「誤 upscale 禁止」とは別軸の **明示的 auto**）。

### ルール（オーナー案）

対象: **割り当て対象 display の解像度**（optimize 時の per-monitor slot）。比較軸は **短辺**（主に height 想定）。

| 条件 | auto 倍率（案） |
| --- | --- |
| 短辺 ≤ 割当解像度の **1/2** | **1.25x または 1.5x**（アスペクト比維持） |
| 短辺 ≤ 割当解像度の **1/4** | **1.5x または 2x**（アスペクト比維持） |

- **fit / fill ではない** — MAT-14 と同様、元画像サイズ決定段階での意図的拡大。
- MAT-14 手動 % との合成順・優先は **設計時に確定**（例: auto 適用後に手動 %、または排他トグル）。

### UX

| 項目 | 案 |
| --- | --- |
| 配置 | Compose **Surface** 行 — **倍率 combo（MAT-14）の左**に L/R 各 auto トグルまたは小コンボ |
| 設定 | `harite-settings.json` — Main Optimize **と** Slideshow Optimize **両方**に浸透（MAT-11 経路） |
| エラー | 拡大後が display 矩形（margins 込み）に収まらなければ MAT-14 同型 `ValueError` |

### 関連

- MAT-14（#459 — 手動 100/125/150/200%）
- MAT-01b（原寸デフォルト）
- MAT-11（Slideshow も Optimize 経路）
- core-spec §4.1 計算順への追記が必要

### 未確定（設計ゲート）

- 1.25 vs 1.5、1.5 vs 2x の **デフォルト係数**
- width 主導の横長画像の扱い（height 以外の short edge 定義）
- auto ON 時の MAT-14 手動 % との関係

---

## MAT-10 — 実施載せ（変更点のみ）

- 区分: `機能要望・後回し` → **`実施 backlog`**
- 位置づけ: Q-01（GTK 整理）**の後**に調査・試験着手。完全新規 source のためライセンスゲートは維持。
- op3 との関係: MAT-18 が NDL 品質を改善、MAT-10 は **雰囲気絵の別経路**（edo-maps / 切絵図）。**補完関係**。

---

## ドキュメント更新先

| ファイル | 更新内容 |
| --- | --- |
| `maturation-20260609-qt-common.md` | ロードマップ表、MAT-02b 完了、MAT-10/18/14b 節 |
| `online-issues/README.md` | 索引棚卸 |
| `20260609-1200-feature-overview.md` | 次の流れ 1 行 |
| `20260603-c01-e-ndl-tsugidigi-inventory.md` | §1 searchbytext を「MAT-18 候補」へ注記（任意・軽量） |

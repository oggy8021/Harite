# JMA 天気図 list.json — 提供カタログ（inventory）

最終更新: 2026-06-03

## 位置づけ

- 親: [feature-overview §C-01-J](20260518-2047-feature-overview.md)（別フェーズ）
- 用途: `https://www.jma.go.jp/bosai/weather_map/data/list.json` から **何が取れるか** を日本語で整理し、Harite の **preset 選定ストーリー** の材料とする
- 正本 spec ではない（気象庁による list.json の公式 schema 文書は **未公開**）

## 参照 URL

| 種別 | URL |
| --- | --- |
| 一覧 API | https://www.jma.go.jp/bosai/weather_map/data/list.json |
| 画像 | `https://www.jma.go.jp/bosai/weather_map/data/png/{filename}` |
| 利用規約 | https://www.jma.go.jp/jma/kishou/info/coment.html |

## list.json 構造（観測）

ルートは **4 カテゴリ** × 各 **3 時間軸**（配列または 1 要素）。

### カテゴリ × 時間軸（日本語名）

| ルート key | 日本語名 | 時間軸 key | 日本語名 | 配列の意味 | Harite C-01 第1弾 |
| --- | --- | --- | --- | --- | --- |
| `near` | 日本付近域（カラー） | `now` | 実況（時系列） | 過去〜最新の実況天気図ファイル名 | **採用** — preset `jma-near-color`（`now` の最新 1 枚） |
| `near` | 同上 | `ft24` | 24 時間予報 | 予報 1 件 | 対象外 |
| `near` | 同上 | `ft48` | 48 時間予報 | 予報 1 件 | 対象外 |
| `near_monochrome` | 日本付近域（モノクロ） | `now` / `ft24` / `ft48` | 同上 | 同上（モノクロ） | 対象外 |
| `asia` | アジア域（カラー） | `now` | 実況（時系列） | 同上 | **採用** — preset `jma-asia-color`（`now` の最新 1 枚） |
| `asia` | 同上 | `ft24` / `ft48` | 24h / 48h 予報 | 予報 | 対象外 |
| `asia_monochrome` | アジア域（モノクロ） | `now` / `ft24` / `ft48` | 同上 | モノクロ | 対象外 |

### ファイル名の目安（カラー実況 `now`）

- カラー: ファイル名に **`JRcolor`** を含む
- モノクロ: **`JRjmahp`** 等（Harite 第1弾では採用しない）
- 最新 1 枚: 配列の **最終要素**

## Harite 第1弾（開発用 preset）

| 表示名（combo `*…`） | `preset_id` | list.json |
| --- | --- | --- |
| 気象庁（日本付近） | `jma-near-color` | `near.now` 最新 |
| 気象庁（アジア域） | `jma-asia-color` | `asia.now` 最新 |
| 気象庁 L/R | `jma-dual-lr` | L/R = 上記 2 source |

契約: [harite-source-spec §15](../specs/source/harite-source-spec.md)

## 別フェーズで検討する拡張

- `ft24` / `ft48` を別 preset として提供するか
- モノクロ系列の要否
- カテゴリ追加時の preset 命名・provider 分岐
- 他外部 source（NDL / CODH 等）の探索 — [feature-overview §C-01-E](20260518-2047-feature-overview.md)

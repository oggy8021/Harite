# C-01-J: JMA 天気図 list.json — 調査報告（inventory）

最終更新: 2026-06-03（**C-01-J クローズ** — オーナー実機確認済）

## 位置づけ

| 項目 | 内容 |
| --- | --- |
| 親 | [feature-overview §C-01-J](20260518-2047-feature-overview.md) |
| ステータス | **完了**（2026-06-03） |
| 目的 | 気象庁 `list.json` の棚卸と **採用 preset の確定**（カラー実況 2 + モノクロ実況 2） |
| スコープ外（見送り確定） | `ft24`/`ft48`、12 葉ギャラリー / 検索 UI、風温湿度など別 API |
| 正本性 | 調査・完了記録（気象庁 list.json 公式 schema は **未公開**） |
| 実装正本 | [harite-source-spec §15](../specs/source/harite-source-spec.md) + [同梱 preset](../../src/harite/gui/resources/source_presets/harite-source-presets.json) |

## 調査方法

1. `GET https://www.jma.go.jp/bosai/weather_map/data/list.json`（UTF-8 JSON、認証なし）
2. ルート 4 カテゴリ × 各 3 時間軸の配列長・先頭/末尾ファイル名・`JRcolor` / `JRjmahp` タグを集計
3. 現行 `sources_remote._JMA_PRESET_LIST_KEYS` / `_jma_pick_filename`（`JRcolor` 最終要素）と照合

**観測日時:** 2026-06-03（調査実行時点の live 応答。配列長・末尾ファイル名は **日々変わる**）

## 参照 URL

| 種別 | URL |
| --- | --- |
| 一覧 API | https://www.jma.go.jp/bosai/weather_map/data/list.json |
| 画像 | `https://www.jma.go.jp/bosai/weather_map/data/png/{filename}` |
| 利用・出典 | https://www.jma.go.jp/jma/kishou/info/coment.html（公共データ利用規約 第1.0版、出典記載例あり） |
| 天気図コメント（人向け説明） | https://www.jma.go.jp/jma/kishou/info/coment.html ほか bosai 天気図 UI |

Harite 同梱 preset の `notes` は「出典：気象庁ホームページ」系（§15 / preset JSON）。

---

## 1. list.json トポロジ（確定）

```
list.json
├── near              … 日本付近域（カラー）
├── near_monochrome   … 日本付近域（モノクロ）
├── asia              … アジア域（カラー）
└── asia_monochrome   … アジア域（モノクロ）
    各カテゴリ:
    ├── now   … 実況（**時系列・複数ファイル名**）
    ├── ft24  … 24 時間予報（**常に 1 要素**）
    └── ft48  … 48 時間予報（**常に 1 要素**）
```

- ルートに **他キーは観測されず**（2026-06-03）。将来キー追加は schema 未公開のため **実行時エラー or 無視** の設計が必要。
- 各葉は **文字列の配列**（オブジェクトではない）。

---

## 2. 全パス棚卸（2026-06-03 live）

| list パス | 日本語（inventory 用） | 配列長 | ファイル名タグ（全要素） | Harite C-01 第1弾 |
| --- | --- | ---: | --- | --- |
| `near.now` | 日本付近・カラー・実況 | 22 | `JRcolor` | **採用** → `jma-near-color` |
| `near.ft24` | 日本付近・カラー・24h 予報 | 1 | `JRcolor` | 対象外 |
| `near.ft48` | 日本付近・カラー・48h 予報 | 1 | `JRcolor` | 対象外 |
| `near_monochrome.now` | 日本付近・モノクロ・実況 | 22 | `JRjmahp`（22/22） | **採用** → `jma-near-monochrome` |
| `near_monochrome.ft24` | 日本付近・モノクロ・24h | 1 | **`JRcolor`/`JRjmahp` なし**（`Tjmahp` のみ） | 対象外 |
| `near_monochrome.ft48` | 日本付近・モノクロ・48h | 1 | 同上 | 対象外 |
| `asia.now` | アジア域・カラー・実況 | 13 | `JRcolor` | **採用** → `jma-asia-color` |
| `asia.ft24` | アジア域・カラー・24h | 1 | `JRcolor` | 対象外 |
| `asia.ft48` | アジア域・カラー・48h | 1 | `JRcolor` | 対象外 |
| `asia_monochrome.now` | アジア域・モノクロ・実況 | 13 | `JRjmahp` | **採用** → `jma-asia-monochrome` |
| `asia_monochrome.ft24` | アジア域・モノクロ・24h | 1 | `JRjmahp` | 対象外 |
| `asia_monochrome.ft48` | アジア域・モノクロ・48h | 1 | `JRjmahp` | 対象外 |

**計 12 葉**（4×3）。Sync 対象は **4 葉**（カラー・モノクロ各 `now` の最新 1 枚）。`ft24` / `ft48` は対象外。

### 2.1 時間軸の意味（運用上）

| key | 意味 | 配列の扱い |
| --- | --- | --- |
| `now` | 実況の時系列 | 過去〜最新の PNG 名が並ぶ。**最新 = 末尾**（第1弾の契約） |
| `ft24` | 24 時間予報 | 単一スナップショット。先頭=末尾 |
| `ft48` | 48 時間予報 | 同上 |

live 例（末尾の先頭 14 桁 = ファイル側タイムスタンプ）:

| パス | 先頭 → 末尾（lead ts） | 末尾の MET 内時刻例 | 製品トークン例（末尾） |
| --- | --- | --- | --- |
| `near.now` | `20260531110031` → `20260603111031` | `20260603090000` | `JCIspas` |
| `asia.now` | `20260531082730` → `20260603083731` | `20260603060000` | `JCIasas` |
| `near.ft24` | 単一 `20260603052400` | `20260603000000` | `JCIfsas24` |
| `near.ft48` | 単一 `20260603074331` | `20260603000000` | `JCIfsas48` |

`now` の配列長は **固定ではない**（調査日: near 22、asia 13）。実装は常に **末尾選択** でよい。

### 2.2 ファイル名の目安（実装フィルタ）

| 系列 | 識別子 | 第1弾 |
| --- | --- | --- |
| カラー実況・予報 | 部分文字列 **`JRcolor`** | `_jma_pick_filename` がこれのみ採用 |
| モノクロ実況 | **`JRjmahp`** | 非採用 |
| モノクロ一部予報 | `JRjmahp` 無し、`Tjmahp` のみ | 非採用（フィルタに掛からない） |

ファイル名は 1 文字列にメタデータが埋め込まれた長い PNG 名（例: `20260603111031_0_Z__C_010000_20260603090000_MET_CHT_JCIspas_JCP600x581_JRcolor_Tjmahp_image.png`）。**公式フィールド定義はなし** — パースは Harite では行わず、list 要素をそのまま PNG URL に渡す。

解像度の目安: 日本付近 `JCP600x581`、アジア `JCP600x512`（ファイル名中のトークン。変更されうる）。

---

## 3. 現行 Harite との対応

### 3.1 同梱 preset（第1弾）

| combo 表示 | `preset_id` | list パス | profile |
| --- | --- | --- | --- |
| `*気象庁（日本付近）` | `jma-near-color` | `near.now` | — |
| `*気象庁（アジア域）` | `jma-asia-color` | `asia.now` | — |
| `*気象庁（日本付近・モノクロ）` | `jma-near-monochrome` | `near_monochrome.now` | — |
| `*気象庁（アジア域・モノクロ）` | `jma-asia-monochrome` | `asia_monochrome.now` | — |
| `*気象庁 L/R` | `jma-dual-lr` | L/R = 上記 2 source | `members.L/R` |

Interval 下限 **600 s**: preset `min_slideshow_interval_seconds`（気象庁更新頻度と product 方針）。

### 3.2 コード上の分岐

- `sources_remote._JMA_PRESET_LIST_KEYS` + `_JMA_PRESET_FILENAME_TAG`: カラー 2 + モノクロ 2
- Sync: list GET → パス配列 → **タグ付き要素の最後**（`JRcolor` / `JRjmahp`）→ PNG GET → `latest.png`
- 未対応 `preset_id` は `ValueError`（拡張時はキー追加 + spec §15 更新）

### 3.3 C-01 完了時点で **意図的に無い** もの（audit）

- list 全種の **GUI カタログ**（検索・ギャラリー・プレビュー）
- `ft24` / `ft48` / モノクロの preset
- 配列中間要素の選択（履歴スライドショー）

---

## 4. preset 拡張候補（調査結論）

| 候補 | list パス | 推奨 | 理由 |
| --- | --- | --- | --- |
| A. 現状維持（実況カラー 2 種 + dual） | `near.now`, `asia.now` | **既定** | 第1弾目的（壁紙・L/R）を満たす。運用単純 |
| B. 24h / 48h 予報カラー | `*.ft24`, `*.ft48` | 任意・低優先 | 各 1 枚で実装は容易。slideshow は **単一静止画** のため Interval 意味が薄い。別 preset 4 本増 |
| C. モノクロ実況 `now` | `near_monochrome.now`, `asia_monochrome.now` | **採用済**（2026-06） | オーナー: デスクトップを邪魔しにくい。Interval 600・最新 1 枚はカラーと同型 |
| C′. モノクロ `ft24`/`ft48` | 予報モノクロ | **非推奨** | タグ例外あり。今回スコープ外 |
| D. `now` 履歴スライド | `now` 配列全体 | **非推奨** | 気象「最新」用途とずれる。別 product（アニメーション） |
| E. 動的カタログ UI | 全 12 葉 | **C-01-J 本体** | ユーザーが path を選ぶなら `_JMA_PRESET_LIST_KEYS` 固定を超える。spec + GUI 設計が要る |

**調査時の推奨:** 追加 preset を増やすなら **B（ft24/ft48）を先に検討**、モノクロは見送り。UI カタログは **E** として planning でスコープ分割（「JSON だけ増やす」vs「combo 検索・説明付き一覧」）。

---

## 5. C-01-J → planning への入力

| 論点 | 調査結果 |
| --- | --- |
| 公式 schema | なし。破壊的変更は **実行時検証** のみ |
| カタログの正 | 本 inventory + live 再取得手順（§調査方法） |
| 最小追加実装 | preset JSON + `_JMA_PRESET_LIST_KEYS` 行追加（UI なし） |
| フル C-01-J | 12 葉の日本語ラベル表 + 選定 UI + `harite-preset` / list パス契約の一般化 |
| ライセンス | 出典記載（既存 notes）。加工時は気象庁 coment ページの加工表記例に従う |
| 他 provider | [C-01-E](20260518-2047-feature-overview.md)（本調査の対象外） |

### 5.1 クローズ時の決定（2026-06-03）

| 論点 | 決定 |
| --- | --- |
| 追加 preset | モノクロ実況 2 種のみ（`jma-near-monochrome` / `jma-asia-monochrome`） |
| 運用 | カラーと同型 — Interval 下限 600、`now` 最新 1 枚、Start 直前 Sync |
| ft24 / ft48 / 予報 | **見送り** |
| カタログ UI | **見送り**（combo の `*preset` で十分） |
| 実機確認 | **OK** — C-01-J 以上でクローズ |

**follow-up（任意）:** ルートキー増減・配列空・タグ不在は実行時 `ValueError` と live 再取得（§6）で対応。

---

## 6. live 取得の再現（開発者向け）

```bash
python -c "import json; from urllib.request import urlopen; d=json.load(urlopen('https://www.jma.go.jp/bosai/weather_map/data/list.json')); print(sorted(d)); print('near.now', len(d['near']['now']), d['near']['now'][-1][:40])"
```

---

## 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-03 | 初版 inventory（4 カテゴリ × 3 軸、第1弾 2 preset） |
| 2026-06-03 | **C-01-J 調査完了** — live 全パス棚卸、ファイル名・拡張候補・planning 論点を追記 |
| 2026-06-03 | **モノクロ実況 2 preset 実装** — `jma-near-monochrome` / `jma-asia-monochrome`（§15 / 同梱 JSON） |
| 2026-06-03 | **C-01-J クローズ** — オーナー実機確認 OK。ギャラリー UI・ft24/48 は見送り確定 |

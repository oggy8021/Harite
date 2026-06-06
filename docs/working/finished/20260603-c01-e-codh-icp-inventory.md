# C-01-E: CODH IIIF Curation Platform（江戸観光・買物）— 調査報告（inventory）

最終更新: 2026-06-03（**調査記録** — 実装・preset 未着手）

## 位置づけ

| 項目 | 内容 |
| --- | --- |
| 親 | [feature-overview §C-01-E](20260518-2047-feature-overview.md) |
| 関連 | [C-01 planning](20260603-1400-c01-external-wallpaper-source-planning.md) / [NDL inventory](20260603-c01-e-ndl-tsugidigi-inventory.md) |
| ステータス | **調査記録**（実装完了 — 契約正本は [harite-source-spec §15.7](../../specs/source/harite-source-spec.md)） |
| 目的 | オーナー関心の **江戸観光案内・江戸買物案内** を、Harite の interval sync で載せられるか整理する |
| スコープ外（オーナー方針） | **江戸マップ**（緯度経度・GIS・地図タイル連携）、位置情報の採取・利用 |
| 正本性 | 本 inventory + Canvas Indexer API live 検証（2026-06-03） |

**観測日時:** 2026-06-03

---

## 参照 URL（オーナー入口 + 調査で確定した正本）

| 種別 | URL |
| --- | --- |
| Curation API 仕様 | https://codh.rois.ac.jp/iiif/curation/ |
| IIIF Curation Platform (ICP) | http://codh.rois.ac.jp/icp/ |
| IIIF Curation Finder（検索 UI） | http://codh.rois.ac.jp/software/iiif-curation-finder/ |
| Canvas Indexer（検索エンジン） | http://codh.rois.ac.jp/software/canvas-indexer/ |
| **江戸観光案内** | http://codh.rois.ac.jp/edo-spots/ |
| **江戸買物案内** | http://codh.rois.ac.jp/edo-shops/ |
| 江戸マップ（今回パス） | http://codh.rois.ac.jp/edo-maps/ |
| 利用ポリシー（総合） | https://codh.rois.ac.jp/policy/ |
| Canvas Indexer API 仕様（GitHub） | https://github.com/IllDepence/Canvas-Indexer |

---

## 1. 画像は「Curation API だけ」では取れない

オーナー仮説: 画像取得は https://codh.rois.ac.jp/iiif/curation/ 経由か？

| 層 | 役割 |
| --- | --- |
| **[Curation API](https://codh.rois.ac.jp/iiif/curation/)** | `cr:Curation` JSON の **データモデル**（`selections` → 複数 Manifest 横断の Canvas / `#xywh=` 矩形）。**検索 API ではない** |
| **JSONkeeper** | キュレーション JSON の保存 |
| **Canvas Indexer** | JSONkeeper / Activity Stream をクロールし **検索・ファセット API** を提供 |
| **IIIF Curation Finder** | 上記 API を呼ぶ **ブラウザ UI**（江戸サイトに埋め込み） |

Harite が叩くのは実質 **Canvas Indexer の search / facets**（ICFinder と同じバックエンド）。返却の `canvasThumbnail` が **既に IIIF Image API の切り出し URL** になっている。

Curation JSON を自前でパースする経路もある（`selections[].canvases[]` + `within`）が、江戸 DB は **Indexer 経由の方が単純**。

---

## 2. 検索 API（実装の正本）

江戸観光・買物は **サービス別エンドポイント**（顔貌コレクションの `api/face/` と同型）。

| データセット | search | facets | キャンバス総数（2026-06-03） |
| --- | --- | --- | ---: |
| 江戸観光案内 | `https://mp.ex.nii.ac.jp/api/edo-spots/search` | `.../edo-spots/facets` | **1309** |
| 江戸買物案内 | `https://mp.ex.nii.ac.jp/api/edo-shops/search` | `.../edo-shops/facets` | **2489** |

仕様は [Canvas-Indexer README](https://github.com/IllDepence/Canvas-Indexer) に準拠。Harite で使うパラメータの例:

| パラメータ | 例 | 用途 |
| --- | --- | --- |
| `select` | `canvas` | キャンバス単位で返す |
| `from` | `canvas,curation` | 検索対象メタデータ |
| `where` | `桜` | キーワード部分一致 |
| `where_metadata_label` + `where_metadata_value` | `キーワード` / `桜` | **メタデータ完全一致**（preset に向く） |
| `start` + `limit` | `302` / `1` | ページング・**疑似ランダム** |
| `where_agent` | （省略可） | `human` / `machine` フィルタ |

応答の主要フィールド（`results[]` 1 件）:

| フィールド | 用途 |
| --- | --- |
| `canvasThumbnail` | **PNG/JPEG 取得用**（IIIF Image API、矩形込み） |
| `fragment` | `xywh=...`（Thumbnail と対応） |
| `canvasId` | Presentation `@id` |
| `manifestUrl` / `manifestLabel` | 出典・書誌 |
| `metadata[]` | `{label, value}` — `notes` 生成に使う |

---

## 3. 画像 URL の作り方（2 通り）

### 3.1 推奨: `canvasThumbnail` の size を上げる

Finder のサムネイルは幅 **200px** 指定（URL 中の `/200,/`）。

```text
# 例（観光・桜検索 1 件目）
https://kokusho.nijl.ac.jp/api/iiif/.../848,837,2464,3208/200,/0/default.jpg
# Harite 用: /200,/ → /max/ または /1200,/
https://kokusho.nijl.ac.jp/api/iiif/.../848,837,2464,3208/max/0/default.jpg
```

- **ホストは資料ごとに異なる**（例: `kokusho.nijl.ac.jp`, `codh.rois.ac.jp/pmjt/...`）。Harite は URL を **そのまま GET** すればよい。
- 原資料の IIIF 利用規約は **ホスト機関側**（国文学研・NDL 等）も確認が必要。

### 3.2 代替: Curation API JSON から組み立て

[Curation API 例](https://codh.rois.ac.jp/iiif/curation/)どおり、`canvas#xywh=` フラグメント + 元 Manifest の Image API。Indexer を使わない場合の低レベル経路。**江戸 DB では不要**。

---

## 4. メタデータ棚卸（＝検索軸の現実）

### 4.1 オーナー案 vs データの有無

| 検索軸（オーナー案） | 江戸観光 | 江戸買物 | コメント |
| --- | --- | --- | --- |
| **日付** | ✗ | ✗ | 刊行年は「出典」出版物単位程度。キャンバス単位の暦日なし |
| **季節** | △ | ✗ | **キーワード**代理（例: 桜・梅・雪）のみ |
| **昼 / 夜** | ✗ | ✗ | タグ・メタデータに未整備 |
| **時刻** | ✗ | ✗ | 同上 |
| **緯度経度・場所** | △（ID のみ） | △（ID のみ） | **江戸マップID**・歴史地名ID はあるが **Harite では用いない**（方針） |
| **キーワード** | ◎ | △ | 観光: 104 ファセット値。買物: 「備考」中心 |
| **地名・名所** | ◎ | ◎ | 統一地名 / 原本表記 / 居所 |
| **職種・商人** | ✗ | ◎ | 買物: 職種・商人名・仲間・版面サイズ |

**結論:** 「日付・季節・昼夜・時刻」で機械的に検索するフィールドは **ない**。実現するなら **キーワード／地名／職種の preset 固定** + 必要なら **疑似ランダム**（§5.2）。

### 4.2 江戸観光案内 — ファセット（Canvas Indexer `facets`）

| メタデータ label | 値の個数（約） | Harite preset 向き |
| --- | ---: | --- |
| 出典 | 8 | 出版物固定（6 点+追加資料） |
| **キーワード** | 104 | **◎** 季節・題材の代理（桜・松・花火…） |
| 名所（統一地名） | 774 | ○ 地名固定 |
| 名所（原本表記） | 1543 | △ 表記ゆれ大 |
| 歴史地名データID | 409 | 見送り（GIS 連携） |
| 江戸マップID | 212 | **見送り** |
| 江戸観光ID | 786 | 内部 ID（ユーザー向けでない） |

公式のメタデータ方針: [edo-spots ページ](http://codh.rois.ac.jp/edo-spots/) の表を正本とする。

### 4.3 江戸買物案内 — ファセット

| メタデータ label | 値の個数（約） | Harite preset 向き |
| --- | ---: | --- |
| 出典 | 4 | 飲食の部 / 問屋の部 |
| 仲間 | 15 | ○ 業種グループ |
| 版面サイズ | 15 | ○ 見開き等 |
| 商人名 | 2057 | △ 多すぎ |
| 職種（原本表記） | 628 | **◎** |
| 居所（原本表記） | 1048 | ○ |
| 居所（歴史地名大系） | 497 | ○ |
| 江戸マップID | 465 | **見送り** |
| 備考 | 2589 | △ 全文検索向き |
| 江戸買物ID | 2157 | 内部 ID |

---

## 5. Harite との適合性

| 観点 | 評価 | メモ |
| --- | --- | --- |
| API キー | ◎ | 不要 |
| Interval sync | ○ | 検索 → 1 キャンバス → IIIF GET → `latest.png` |
| 「ランダム」 | ○ | **専用 random API なし**。`total` 取得 → `start=randint(0,total-1)` & `limit=1` |
| テーマ別 preset | ◎ | `where_metadata_label` + `where_metadata_value` で **再現可能** |
| 出典 `notes` | ○ | `manifestLabel` + `出典` + CODH ポリシー表記 |
| 複数 IIIF ホスト | △ | 障害・レートはホスト依存。リトライ設計が必要 |
| 江戸マップ連携 | **対象外** | GIS・緯度経度はオーナー判断でパス |
| 商用利用 | 要確認 | [policy](https://codh.rois.ac.jp/policy/) — CC と All Rights Reserved 混在。**画像ホストごと**に確認 |

### 5.1 想定 sync フロー（`remote-codh` 草案）

```
1. preset から indexer パス（edo-spots | edo-shops）と検索条件を読む
2. GET .../search?select=canvas&from=canvas,curation&...&limit=1
   （ランダム preset なら start を乱数）
3. results[0].canvasThumbnail の /200,/ → /max/ に置換して GET
4. cache/latest.png、notes に出典・名所/商人名等
```

### 5.2 実現性検証（推奨スパイク）

| # | 検証 | 合格基準 |
| --- | --- | --- |
| V1 | キーワード preset（観光・`桜`） | 200 OK、PNG 保存、縦横比が slideshow で許容 |
| V2 | 買物・職種 preset（例: `薬種`） | 同上 |
| V3 | 無条件 + random `start` | 1309/2489 から偏りなく取得できるか |
| V4 | ホスト混在 | `kokusho` / `codh` 両方で `/max/` GET が安定か |
| V5 | ライセンス | 壁紙用途・表示のみで policy + 原資料ホストに抵触しないか |

NDL の `random?size=1` より **クエリ設計の自由度は高い**が、**検索軸の設計が product 側の責務**になる。

---

## 6. preset たたき台（未決定）

| combo 案 | indexer | 検索条件 |
| --- | --- | --- |
| 江戸観光・おまかせ | edo-spots | 無条件 + random `start` |
| 江戸観光・桜 | edo-spots | `キーワード`=`桜`（または `where=桜`） |
| 江戸観光・花火 | edo-spots | `キーワード`=`花火` |
| 江戸買物・おまかせ | edo-shops | random `start` |
| 江戸買物・薬種 | edo-shops | `職種（原本表記）` 含む検索（要 live 表記確認） |

**見送り:** 江戸マップ preset、緯度経度連動、GIS タイル背景。

---

## 7. NDL との比較（C-01-E 選定用）

| | NDL 次世代 DL | CODH 江戸 ICP |
| --- | --- | --- |
| 取得 | `illustration/random?size=1` | Canvas Indexer **search** |
| 画像 | `dl.ndl.go.jp` IIIF 組み立て | 返却 `canvasThumbnail` を拡大 |
| テーマ | `randomwithfacet` タグ | **メタデータ label/value** |
| 時刻・季節 | ✗ | ✗（キーワード代理のみ） |
| 位置 | ✗ | メタデータに ID あり（**Harite では不用**） |

---

## 8. live 再現（開発者向け）

**ブラウザで JSON が見えるなら API は正常**です。NDL inventory と同様、Windows `curl` だけが Schannel の失効確認で失敗することがあります → [NDL inventory §6.1–6.3](20260603-c01-e-ndl-tsugidigi-inventory.md) を共通手順として参照。

### 8.1 Windows 向け（要 `--ssl-no-revoke` + URL 全体をクォート）

```powershell
curl.exe --ssl-no-revoke -sS "https://mp.ex.nii.ac.jp/api/edo-spots/facets"

curl.exe --ssl-no-revoke -sS "https://mp.ex.nii.ac.jp/api/edo-spots/search?select=canvas&from=canvas,curation&where_metadata_label=%E3%82%AD%E3%83%BC%E3%83%AF%E3%83%BC%E3%83%89&where_metadata_value=%E6%A1%9C&limit=1"

curl.exe --ssl-no-revoke -sS "https://mp.ex.nii.ac.jp/api/edo-spots/search?select=canvas&from=canvas,curation&start=302&limit=1"
```

```powershell
# curl を使わない例
$r = Invoke-RestMethod -Uri "https://mp.ex.nii.ac.jp/api/edo-spots/search?select=canvas&from=canvas,curation&limit=1"
$r.results[0].canvasThumbnail
```

**注意:** `?select=canvas&from=...` の **`&` を PowerShell でクォートしない**と、`from=...` 以降が別コマンド扱いになり、`--ssl-no-revoke` 後に「別のエラー」に見えやすい。bash 向けの `| head` / `| python` も PowerShell では **パイプライン構文**になり、そのままでは動かない（NDL inventory §6.1 参照）。

### 8.2 bash（参考）

```bash
curl -sS "https://mp.ex.nii.ac.jp/api/edo-spots/facets" | head -c 400
curl -sS "https://mp.ex.nii.ac.jp/api/edo-spots/search?select=canvas&from=canvas,curation&limit=1"
```

---

## 9. 実装前の未決論点

| 論点 | メモ |
| --- | --- |
| preset 本数 | 観光キーワード何本か / 買物職種 / おまかせ random |
| 検索ヒット 0 件 | キーワード表記ゆれ — フォールバック方針 |
| Thumbnail 解像度 | `/max/` vs 固定幅 `1200,` — 帯域と slideshow 品質 |
| 出典 notes 定型 | CODH + 各 `manifestLabel` + ホスト機関 |
| 江戸マップ | **スコープ外**（オーナー確認済み方針として記録） |

---

## 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-03 | 初版 — ICP 構成、Indexer API、メタデータ棚卸、画像 URL、Harite 適合性・スパイク項目 |
| 2026-06-03 | §8 — Windows curl / PowerShell 向け追記（NDL §6 と相互参照） |
| 2026-06-03 | **実機:** random 用 probe は `limit=1` 必須（未指定で全件 JSON ≈3MB・UI フリーズ） |


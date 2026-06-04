# C-01-E: 次世代デジタルライブラリー（NDL）図版 API — 調査報告（inventory）

最終更新: 2026-06-03（**調査記録** — 実装・preset 未着手）

## 位置づけ

| 項目 | 内容 |
| --- | --- |
| 親 | [feature-overview §C-01-E](20260518-2047-feature-overview.md) |
| 関連 planning | [C-01 外部壁紙 planning](20260603-1400-c01-external-wallpaper-source-planning.md) |
| ステータス | **調査のみ**（Harite `remote-ndl` / 同梱 preset は未実装） |
| 目的 | 次世代デジタルライブラリー API（図版・ランダム取得・IIIF）の棚卸と **Harite 採用可否**の整理 |
| スコープ外（現時点） | Book / Page 全文検索、OCR ダウンロード、ギャラリー UI、`searchbytext` キーワード探索 |
| 正本性 | 本 inventory + OpenAPI live 検証（**公式タグ enum は Swagger に無い**） |
| 実装正本（将来） | [harite-source-spec §15](../specs/source/harite-source-spec.md) + 同梱 `harite-source-presets.json` |

**観測日時:** 2026-06-03（`lab.ndl.go.jp` / `dl.ndl.go.jp` への live 呼び出し）

---

## 参照 URL（オーナー入口 + 調査で確定した正本）

| 種別 | URL |
| --- | --- |
| デジタルコレクション（ポータル） | https://dl.ndl.go.jp/ |
| 次世代 DL サービス・利用規約 | https://lab.ndl.go.jp/service/tsugidigi/ |
| **API 人向け解説** | https://lab.ndl.go.jp/service/tsugidigi/apiinfo/ |
| **Swagger UI** | https://lab.ndl.go.jp/dl/swagger-ui/index.html |
| **OpenAPI JSON** | https://lab.ndl.go.jp/dl/v3/api-docs |
| API 公開ニュース（2023-09） | https://lab.ndl.go.jp/news/2023/2023-09-19/ |
| 図版タグ（NDL-ImageLabel） | https://github.com/ndl-lab/imagetagdataset |
| タグ推定・`randomwithfacet` 例 | https://github.com/ndl-lab/tagestimatemodel |

### ドキュメントの読み分け

| 読む場所 | 分かること | 分からないこと |
| --- | --- | --- |
| [apiinfo](https://lab.ndl.go.jp/service/tsugidigi/apiinfo/) | Book / Page / Illustration の概要、**IIIF で画像を取る手順（§4）**、Swagger の見方 | **ランダム図版 API**（Swagger のみ） |
| Swagger / OpenAPI | 全エンドポイント、必須パラメータ、返却 JSON 型 | タグ名の意味（enum なし） |
| NDL-ImageLabel / tagestimatemodel | `tagname` の定義・facet クエリ例 | Harite 製品利用の法的最終判断 |

**注意:** `https://lab.ndl.go.jp/dl/api/swagger-ui/` や `.../dl/api/v3/api-docs` は SPA に吸われ **HTML が返る**。Swagger の正しい入口は **`/dl/swagger-ui/`**（`/dl/api/` ではない）。

**ホスト分担:**

| ホスト | 役割 |
| --- | --- |
| `lab.ndl.go.jp/dl/api/...` | 次世代 DL **実験 API**（JSON メタデータ・検索） |
| `dl.ndl.go.jp/api/iiif/...` | デジタルコレクション **IIIF 画像配信**（切り出し PNG/JPEG） |

---

## 1. Illustration API 棚卸（OpenAPI `illust-controller`）

ベース: `https://lab.ndl.go.jp/dl/api`

| パス | 概要 | 主なクエリ | Harite 第1弾 |
| --- | --- | --- | --- |
| `GET /illustration/random` | 図版をランダム取得 | **`size` 必須**（未指定 → 400） | **採用候補**（`size=1`） |
| `GET /illustration/randomwithfacet` | タグ facet で絞ってランダム | `query` マップ（下記 §3） | **採用候補**（preset 分類） |
| `GET /illustration/{id}` | 図版 ID 指定メタデータ | path `id` = `{pid}_{page}_{n}` | 補助（ID は random 返却から） |
| `GET /illustration/multi-get` | 複数 ID 一括 | `ids` カンマ区切り | 対象外 |
| `GET /illustration/searchbytext` | テキスト類似図版検索 | **`keyword2vec` 必須** | 対象外（キーワード UI なし） |
| `GET /illustration/searchbyid` | ID 検索 | `id` | 対象外 |

`apiinfo` §3 に明記されているのは **図版メタデータ取得** と **テキスト類似検索** のみ。**ランダム系は Swagger / OpenAPI のみ**（2026-06-03 時点）。

### 1.1 `random` 契約

```
GET https://lab.ndl.go.jp/dl/api/illustration/random?size=1
```

| 項目 | 内容 |
| --- | --- |
| 認証 | 不要（API キーなし） |
| 返却 | `Illustration[]`（0 件以上） |
| Harite sync | **1 回の取得で 1 枚** → JMA `now` 最新 1 枚と同型 |

### 1.2 `Illustration` オブジェクト（実装で使うフィールド）

| フィールド | 用途 |
| --- | --- |
| `id` | `{pid}_{page}_{通し番号}`（例: `1114728_187_0`） |
| `pid`, `page` | IIIF URL 組み立て |
| `x`, `y`, `w`, `h` | ページ画像上の **百分率** 矩形（0–100） |
| `graphictags[]` | `tagname` + `confidence`（facet 結果の確認用） |
| `feature`, `feature_txt2vec` | 機械学習用ベクトル — **ダウンロード・保存不要**（JSON が巨大） |
| `title` | あれば `notes` 出典補助に使える |

---

## 2. 画像取得（IIIF）— apiinfo §4 + live 検証

流れは **常に 2 段**:

1. Illustration API でメタデータ（座標）を得る  
2. デジタルコレクション IIIF で切り出し画像を GET

### 2.1 URL テンプレート（確定）

```text
https://dl.ndl.go.jp/api/iiif/{pid}/{page}/pct:{x},{y},{w},{h}/max/0/default.jpg
```

- `{x},{y},{w},{h}` は API 返却値を **そのまま** `pct:` に載せる（apiinfo 図1・PID `2558316` 例と同型）
- `max/0/default.jpg` は調査時点で **200 OK** を確認（他 size/quality は未棚卸）

### 2.2 実装時の注意

| 論点 | 内容 |
| --- | --- |
| 縦横比 | 切り出し矩形依存（壁紙向けに letterbox / crop は Harite 側ポリシー次第） |
| 極小矩形 | `w`/`h` が数 % の図版あり（スタンプ等）— 壁紙として見づらい可能性 |
| PID 不在 | 収録同期のずれで IIIF 404 の可能性（apiinfo「PID リストと DL 提供の不一致」注記と同種） |

---

## 3. `randomwithfacet` と図版タグ（facet）

### 3.1 Swagger が言っていること

| 項目 | 内容 |
| --- | --- |
| パラメータ名 | `query` のみ（型: `MultiValueMapStringString`） |
| `tagname` の enum | **なし** |
| 説明文 | 「図版タグや ID を指定して同種の図版を絞り込める」（要約） |

### 3.2 実際のクエリキー（OpenAPI 外・live + 公式 GitHub 例）

| キー | 必須性 | 説明 |
| --- | --- | --- |
| `size` | 推奨 **必ず指定** | 件数。省略時は **大量返却** になり得る（実測: `stamp` 絞りのみで ~130KB 級 JSON） |
| `f-graphictags.tagname` | 絞り込み時 | facet フィルタ（[tagestimatemodel README](https://github.com/ndl-lab/tagestimatemodel) の curl 例） |

**効かない例（2026-06-03）:** `graphictag=...`、`f-graphictag=...` 単体では意図どおり絞れない。

公式例:

```bash
curl "https://lab.ndl.go.jp/dl/api/illustration/randomwithfacet?size=10&f-graphictags.tagname=graphic_map"
```

Harite 向け:

```bash
curl "https://lab.ndl.go.jp/dl/api/illustration/randomwithfacet?size=1&f-graphictags.tagname=graphic_map"
```

### 3.3 `f-graphictags.tagname` に渡せる値（全件 live OK）

Swagger に enum は無い。下表は **NDL-ImageLabel 公開ラベル + モデル拡張** を `size=1` で呼び、**非空 JSON** が返ったもの（2026-06-03）。

| `tagname` | 意味（NDL-ImageLabel 説明要約） | 階層 | データセット |
| --- | --- | --- | --- |
| `graphic` | グラフィック上位 | 単独フィルタ可 | 学習ラベル体系 |
| `graphic_map` | 地図・図面 | `graphic` 系 | 公開 |
| `graphic_graph` | グラフ・表 | `graphic` 系 | 公開 |
| `graphic_illustcolor` | 着色イラスト | `graphic` 系 | 公開 |
| `graphic_illust` | 地図/グラフ/着色以外のイラスト | `graphic` 系 | 公開 |
| `picture` | 写真上位 | 単独フィルタ可 | 学習ラベル体系 |
| `picture_landmark` | 写真（建物・景観） | `picture` 系 | 公開 |
| `picture_outdoor` | 写真（屋外） | `picture` 系 | 公開 |
| `picture_indoor` | 写真（屋内） | `picture` 系 | 公開 |
| `picture_object` | 写真（物体） | `picture` 系 | 公開 |
| `picture_person` | 写真（人物） | `picture` 系 | **公開 DS 外**、API では利用可 |
| `stamp` | 印・スタンプ | 単独 | 公開 |

**応答の `graphictags`:** 1 図版に複数タグ＋信頼度が付く。facet で `graphic_map` を指定しても、返却に `graphic_illust` 等が **併記** されることがある（多ラベル推定）。

### 3.4 preset 分類のたたき台（未決定）

| Harite combo 案（例） | facet `f-graphictags.tagname` |
| --- | --- |
| おまかせランダム | （なし）→ `/random?size=1` |
| 地図 | `graphic_map` |
| グラフ・表 | `graphic_graph` |
| イラスト | `graphic_illust` |
| 着色挿絵 | `graphic_illustcolor` |
| 写真（屋外） | `picture_outdoor` |
| 印影 | `stamp` |

オーナー判断待ち: **単一 preset のみ** vs **タグ別複数 preset** vs **上位タグ `graphic` / `picture` のみ**.

---

## 4. Harite C-01 適合性

| 観点 | 評価 | メモ |
| --- | --- | --- |
| API キー | ◎ | C-01 方針と一致 |
| Interval sync（600s 等） | ◎ | `size=1` + IIIF 1 枚 cache |
| 出典 `notes` | ○ | [利用規約](https://lab.ndl.go.jp/service/tsugidigi/) — 二次利用可の表記保持・加工明示 |
| 実験サービス | △ | 予告なく変更・削除あり（apiinfo / サービスページ） |
| 応答サイズ | △ | `feature*` を無視しても JSON は大きめ。保存は PNG のみ |
| 壁紙品質 | △ | 縦横・解像度バラバラ。極小切り出しあり |
| 商用・製品配布 | 要確認 | 規約上はオープン資料の二次利用想定だが **実験 API 依存** は product リスクとして別途 |

### 4.1 想定 provider フロー（実装メモ）

```
sync_remote_source (remote-ndl)
  1. GET .../illustration/random?size=1
     または .../randomwithfacet?size=1&f-graphictags.tagname={tag}
  2. Illustration から IIIF URL を組み立て
  3. GET IIIF → cache/latest.png（1 枚上書き）
  4. harite-sources.json の notes に出典（§15.4 — 画像への埋め込みではない）
```

---

## 5. 見送り・別 API（混同防止）

| API / サイト | 関係 |
| --- | --- |
| NDL Search / OpenSearch / SRU | **別系統**（書誌・サムネ ISBN 等） |
| `dl.ndl.go.jp` ポータル UI | 人間閲覧。Harite は **lab API + IIIF** |
| Book API 資料検索 | 全文・書誌 — 壁紙用途では優先度低 |
| NASA APOD 等 | C-01 planning で見送り済（API キー） |

---

## 6. live 取得の再現（開発者向け）

**ブラウザで URL を開いて JSON が見えるなら API は正常**です。Harite 実装も Python 等の TLS スタックを使うため、Windows `curl` だけが失敗する場合があります。

### 6.1 Windows + curl（Schannel）でよくあること

| 現象 | 原因 | 対処 |
| --- | --- | --- |
| `curl: (35) schannel: ... CRYPT_E_NO_REVOCATION_CHECK (0x80092012)` | Windows 付属 curl が **証明書失効リスト（CRL/OCSP）を確認できない**（プロキシ・社内 CA・オフライン等） | 下記 §6.2 |
| `--ssl-no-revoke` のあと別エラー | **PowerShell で URL の `&` がコマンド区切り**と解釈され、URL が途中で切れることが多い | URL を **全体をダブルクォート**、`curl.exe` を明示（§6.2） |
| `curl ... \| head` / `\| python` が動かない | PowerShell の `\|` は **パイプライン**（オブジェクト渡し）。`head` コマンドも無い | 出力をファイルにリダイレクトするか、`Invoke-RestMethod` / Python ワンライナー（§6.3） |
| ブラウザは OK / curl だけ NG | 上記の組み合わせ | `Invoke-RestMethod` または Python（§6.3） |

inventory 執筆環境（Windows 11・`C:\Windows\System32\curl.exe` 8.19）では、**`--ssl-no-revoke` + クォート済み URL** で NDL は **HTTP 200** を確認済み（2026-06-03）。

### 6.2 Windows 向け curl 例

**PowerShell** — エイリアスではなく `curl.exe`、URL は必ず引用符で囲む:

```powershell
curl.exe --ssl-no-revoke -sS "https://lab.ndl.go.jp/dl/api/illustration/random?size=1"

curl.exe --ssl-no-revoke -sS "https://lab.ndl.go.jp/dl/api/illustration/randomwithfacet?size=1&f-graphictags.tagname=graphic_map"

curl.exe --ssl-no-revoke -sS "https://lab.ndl.go.jp/dl/v3/api-docs" | python -c "import json,sys; s=json.load(sys.stdin); print(*[p for p in sorted(s['paths']) if 'illustration' in p], sep='\n')"
```

**cmd.exe** — 同様にダブルクォート必須:

```bat
curl --ssl-no-revoke -sS "https://lab.ndl.go.jp/dl/api/illustration/random?size=1"
```

毎回付けたくない場合はユーザホームに `_curlrc`（1 行 `ssl-no-revoke`）でもよい（開発マシンのみ推奨）。

**Git Bash / WSL** の curl は OpenSSL 由来のことが多く、`(35)` が出ない場合あり。

### 6.3 curl を避ける例（PowerShell / Python）

```powershell
# ランダム 1 件 — 先頭要素の id
(Invoke-RestMethod -Uri "https://lab.ndl.go.jp/dl/api/illustration/random?size=1")[0].id
```

```powershell
python -c "import json,urllib.request; print(json.load(urllib.request.urlopen('https://lab.ndl.go.jp/dl/api/illustration/random?size=1'))[0]['id'])"
```

### 6.4 bash（参考・Linux / macOS / Git Bash）

```bash
curl -sS "https://lab.ndl.go.jp/dl/api/illustration/random?size=1" | head -c 500
curl -sS "https://lab.ndl.go.jp/dl/api/illustration/randomwithfacet?size=1&f-graphictags.tagname=graphic_map"
```

IIIF（`pid`/`page`/`x,y,w,h` は直前の JSON から差し替え）— **画像はブラウザで URL を開いてもよい**:

```text
https://dl.ndl.go.jp/api/iiif/{pid}/{page}/pct:{x},{y},{w},{h}/max/0/default.jpg
```

---

## 7. C-01-E 実装前の未決論点

| 論点 | 調査結果 / 推奨 |
| --- | --- |
| preset 本数 | 単一 `ndl-random` vs §3.4 タグ別 — **オーナー決定** |
| `notes` 文言 | 「国立国会図書館デジタルコレクション」「次世代デジタルライブラリー」等の定型 — §15.4 に合わせて確定 |
| 画像後処理 | 極小 crop の最小サイズ閾値を入れるか |
| 失敗時 | 400（`random` で `size` 忘れ）、404 IIIF — `ValueError` / sync ログ方針は JMA と揃える |
| CODH 江戸 ICP | [別 inventory](20260603-c01-e-codh-icp-inventory.md) |

---

## 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-03 | 初版 — 入口 URL、Swagger 正本、random / randomwithfacet / IIIF、タグ一覧 live 検証、Harite 適合性 |
| 2026-06-03 | §6 — Windows curl `(35)` / `--ssl-no-revoke` / PowerShell の `&` 注意、代替コマンド |

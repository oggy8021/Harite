# C-01-E: 外部 provider 調査 — 統合索引

最終更新: 2026-06-04（**完了** — #400 merge、`finished/` へ移動）

## 位置づけ

| 項目 | 内容 |
| --- | --- |
| 親 | [feature-overview §C-01-E](20260518-2047-feature-overview.md) |
| 実装 | ブランチ `feature/c01-e-ndl-codh` — `remote-ndl-tsugidigi` / `remote-codh-edo` + 同梱 preset |
| spec | [harite-source-spec §15.6–15.7](../specs/source/harite-source-spec.md) |
| 状態 | **完了**（#400）— 本書 §実現性検証。[軽量 audit](20260603-c01-e-3layer-audit.md) |

## 調査ドキュメント

| Provider | inventory | 要点 |
| --- | --- | --- |
| **NDL** 次世代 DL | [20260603-c01-e-ndl-tsugidigi-inventory.md](20260603-c01-e-ndl-tsugidigi-inventory.md) | `random?size=1` / `randomwithfacet` → IIIF 切り出し |
| **CODH** 江戸 ICP | [20260603-c01-e-codh-icp-inventory.md](20260603-c01-e-codh-icp-inventory.md) | Canvas Indexer search → `canvasThumbnail` |

## 第 1 実装で採用した preset（2026-06-03）

| `preset_id` | 表示名 | `kind` |
| --- | --- | --- |
| `ndl-random-map` | NDL 図版（地図） | `remote-ndl-tsugidigi` |
| `ndl-random-illust` | NDL 図版（イラスト） | `remote-ndl-tsugidigi` |
| `ndl-random-illustcolor` | NDL 図版（着色挿絵） | `remote-ndl-tsugidigi` |
| `ndl-random-indoor` | NDL 図版（写真・屋内） | `remote-ndl-tsugidigi` |
| `ndl-random-landmark` | NDL 図版（写真・ランドマーク） | `remote-ndl-tsugidigi` |
| `ndl-random-outdoor` | NDL 図版（写真・屋外） | `remote-ndl-tsugidigi` |
| `codh-edo-spots-sakura` | 江戸観光（桜） | `remote-codh-edo` |
| `codh-edo-spots-random` | 江戸観光（おまかせ） | `remote-codh-edo` |
| `codh-edo-shops-random` | 江戸買物（おまかせ） | `remote-codh-edo` |

Interval 下限 **600 s**（JMA と同型）。江戸マップ・座標連携は **見送り**。

**起動時:** `load_source_catalog` は preset 追加のみ（**ネットワーク sync なし**）。画像取得は Manage の **Refresh** または Slideshow **Start** 直前。

**実機（2026-06）:** NDL facet preset OK（2026-06-04 より同梱 6 種、`ndl-random` 廃止）。CODH「おまかせ」Start 無応答 → random の search が `limit` 無しで全 1309 件取得していたため修正。手動 Sync は **Manage sources and profiles…** 内 **Refresh** のみ（Slideshow タブに Sync ボタンなし）。`remote-cache` 内 UUID フォルダの手動削除後は Saved source 選択で空フォルダが再作成され、画像は Start/Refresh で再取得（[source-spec §12.3](../specs/source/harite-source-spec.md)）。

**remote-cache 掃除（C-01 追補）:** catalog materialize 時に、catalog に無い UUID subdirectory を自動削除（`prune_orphan_remote_cache_dirs`）。ユーザー向け GUI ボタンは置かない。

## 実現性検証（2026-06・クローズ）

オーナー実機で **本フェーズの確認は十分** とし、追加の探索実装は行わない。

| 確認 | 結果 |
| --- | --- |
| NDL おまかせ / 地図を L/R Saved source | OK（名称表示、sync → `latest.jpg`、壁紙） |
| 地図 facet の見た目 | タグは ML 絞り込みのため地図以外もありうる（既知） |
| CODH 桜 / おまかせ | 選択・cache UUID 作成 OK。おまかせは `limit` 無し bug 修正後 Start で画像取得 |
| cache UUID 手動削除 | 選択で空フォルダ再作成。Start/Refresh で画像再取得 |
| 孤児 UUID フォルダ | materialize 時自動削除（§12.3） |

**第 4 波 C-01（JMA）audit** は [20260603-c01-3layer-audit.md](20260603-c01-3layer-audit.md) で完了済み。C-01-E は [20260603-c01-e-3layer-audit.md](20260603-c01-e-3layer-audit.md) で差分確認。

## 見送り（調査済み・preset 未実装）

| 項目 | 理由 |
| --- | --- |
| NDL タグ別 preset 大量追加 | まず 2 種で検証。`randomwithfacet` 拡張は任意 |
| CODH キーワード・職種の網羅 | 桜 + おまかせ random のみ。季節・昼夜メタデータなし |
| CODH キーワードのユーザー指定 | **先送り** — [feature-overview §2 C-01-E-KW](20260518-2047-feature-overview.md)。当面は同梱 preset 追加で代替 |
| 江戸マップ / GIS | オーナー方針でパス |
| 日付・時刻・緯度経度検索 | データ側にフィールドなし |

## Windows 開発者向け

curl の Schannel `(35)` / PowerShell の `&` `|` — [NDL inventory §6](20260603-c01-e-ndl-tsugidigi-inventory.md)。

## 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-03 | 統合索引 + 実装 preset 一覧 |
| 2026-06-03 | 実現性検証クローズ + 開発プロセス続き（PR / 軽量 audit） |
| 2026-06-04 | #400 merge、[軽量 audit](20260603-c01-e-3layer-audit.md)、`finished/` へ移動 |

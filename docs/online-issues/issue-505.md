# Issue #505

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/505>
- opened: 2026-06-14
- title: `harite-sources.json について 0byte 空ファイルとして起動したら、json.decoder.JSONDecodeError`
- labels: `enhancement`
- 報告: 実機（catalog 手動リセット試行）

## 事象

`harite-sources.json` を **0 バイト空ファイル**にして `harite-qt` 起動すると、`load_sources_json` → `JSONDecodeError: Expecting value` で **起動不能**。

ユーザー意図は catalog 内容のリセット。不存在時は空 catalog として扱われるが、**空ファイルは存在扱い**のため parse 失敗していた。

## 期待

- 0 バイト / 空白のみの `harite-sources.json` は **空 catalog** として load する（§6.1 と同型）。
- 起動時 `materialize_source_catalog_at_path` が preset bootstrap し、有効 JSON を書き戻す。
- 中身ありの **不正 JSON** は従来どおり `ValueError`（破損検知を維持）。

## 分類

- `bug` / `enhancement` — 手動リセット手順の耐障害性

## 関連

- 正本: [harite-source-spec.md §6.1](../specs/source/harite-source-spec.md)
- 実装: `harite.sources_file.load_sources_json`, `harite.sources.load_catalog`
- 起動経路: `qt_source_catalog.materialize_source_catalog_at_path`

## 取り込み方針

- `load_sources_json`: `raw.strip()` が空なら `empty_sources_json_payload()` を返す。
- spec §6.1 / API 表に 0 バイト契約を追記。
- テスト: `tests/test_sources_file.py`

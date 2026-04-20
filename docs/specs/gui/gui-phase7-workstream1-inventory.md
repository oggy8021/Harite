# GUI Phase 7 Workstream 1: 機能棚卸し

最終更新: 2026-04-20

## 位置づけ

- 本書は Phase7 product alignment における Workstream 1 の詳細メモである。
- 目的は、CLI / GUI / core の差分を `意図差` / `接続済み` / `未接続` / `CLI 専用` / `Phase8 候補` の観点で棚卸しすることにある。
- index は [docs/specs/gui/gui-phase7-product-alignment-planning.md](docs/specs/gui/gui-phase7-product-alignment-planning.md) を参照する。

## 分類メモ

- `意図差`: product 上その差を残す前提
- `接続済み`: GUI / CLI / core の責務整理と実接続まで完了
- `未接続`: 土台はあるが GUI / CLI / core の接続が未完
- `CLI 専用`: GUI 主導線へ持ち込まない前提
- `Phase8 候補`: 将来 backlog として送る候補

## 機能棚卸し表

| 項目 | core | CLI | GUI | 現時点の分類 | 現時点メモ | 次に詰めること |
| --- | --- | --- | --- | --- | --- | --- |
| `optimize` / `two_screen` 合成 | 実装済み | 実装済み | 2入力 + 2画面検出時に自動投入 | 意図差 | optimize 側の主導線として最も揃っている。apply 側の monitor-aware 挙動とは別レイヤー。 | この理解を棚卸し表の基準線として固定する |
| `Apply` の基本責務 | plugin apply は可能 | dry-run 既定 + `--do-it` | 即時実行 | 意図差 | CLI と GUI で実行ポリシーが異なるが、語彙差を除けば同じ plugin apply を指している。 | この差を残すか、将来さらに寄せるかを別途判断する |
| `Default` / `single-file` apply | `single-file` 経路あり | 既定 apply は `single-file` | visible には `Default` 相当で露出 | 意図差 | 現在の理解では `Default` は monitor-aware 既定ではなく、追加分割なしの通常 apply 経路を指す。 | GUI 表示語を `分割せず適用` 系へ寄せる整理を維持する |
| `Auto-split` | split / monitor-aware apply の土台あり | 実装済み | apply mode として露出済み | 意図差 | Harite 独自価値として `Apply` の主導線に置く判断まで到達した。 | GUI 上でどの程度前面に出すかを UI/文言へ落とす |
| explicit mapping (`--left-file` / `--right-file`) | mapping を受ける土台あり | 実装済み | 未露出 | CLI 専用 | CLI 側の低露出 escape hatch として残す。Harite の主導線とは扱わない。 | GUI 非対象のまま固定するかを棚卸し結果として明記する |
| `watch` 継続ループ | watch runner あり | 実装済み | srcdir / interval / start-stop、timer event 駆動、状態表示、apply 接続あり | 接続済み | GUI は same-process の watch front-end として接続済みであり、`run_watch_cycle()` を刻んで反復 apply を扱う。 | close 判定用の manual validation と文言調整へ進む |
| watch failure-continue / 実切替 | plugin apply と組み合わせ可能 | 実装済み | 既定挙動として継承、詳細 option は未露出 | 意図差 | GUI は CLI と同じ詳細 option 群を広く露出せず、watch 実切替の front-end として必要最小限の責務に留める。 | GUI 非露出のまま維持する語彙境界を確定する |
| `Prefs` / 設定同期 | config / dataclass 基盤あり | config 読み込みあり | dialog 開閉、適用、保存、読込あり | 未接続 | Phase6 で入口と同期基盤は復旧した。内容 grouping と main 画面との責務分担はまだ再設計対象。 | Workstream 4 で main と settings の境界を再整理する |
| `embed-text` / margin info | 実装済み | 実装済み | form / preferences には入るが主導線では未露出 | Phase8 候補 | core / CLI では既に使える一方、GUI では制作機能としてまだ立ち上げきっていない。 | GUI へ送る価値と露出方法を Workstream 4 で判断する |
| per-monitor apply / auto-split の GUI 露出 | 実装済み | 実装済み | `Auto-split` のみ露出、explicit は未露出 | 意図差 | `Auto-split` を主導線、explicit mapping を非主導線とする方向で整理済み。 | GUI に出す apply mode の最終語彙を固める |
| visual preview / assist | 画像 preview の専用基盤は未成熟 | なし | CLI preview 文字列はあるが画像 preview は未成熟 | Phase8 候補 | GUI には optimize CLI preview 相当はあるが、制作支援としての visual preview はまだ候補段階。 | Workstream 4 で backlog 化するか判断する |
| `Color` | core 根拠なし | なし | deferred のまま | Phase8 候補 | 現状は `phase7 deferred` を示すプレースホルダに留まり、正本機能ではない。 | 維持 / 削除 / Phase8 候補のいずれに置くか決める |
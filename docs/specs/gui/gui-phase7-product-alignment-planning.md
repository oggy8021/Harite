# GUI Phase 7 計画（プロダクト整合性の再設計フェーズ）

最終更新: 2026-04-21

## 位置づけ

- 本書は Phase6 の成果物として作成する、次フェーズ準備用の index 文書である。
- 新しい Phase7 は、GUI / CLI / core の機能差分と操作語彙を棚卸しし、プロダクトとしての整合性を再設計するフェーズとする。
- 新機能の実装フェーズは Phase8 へ後ろ倒しし、Phase7 で承認された項目だけを送る。
- 詳細メモは workstream 単位の個別文書へ分離する。

## 目的

- CLI / GUI / core の機能差分を、偶発的な抜け漏れと意図的なチャネル差に分離する。
- `optimize` / `apply` / `dry-run` / `do-it` / `watch` の語彙と責務境界を再設計する。
- CLI に先行して存在する機能のうち、GUI にもたらすべきものと CLI 専用に残すものを分類する。
- GUI にだけ残る planned / deferred 項目について、維持 / 落とす / Phase8 候補へ送る、のいずれに置くかを判断する。
- `Prefs` の内容 grouping、初期値埋め込み、auto-detect の露出方針、main 画面との責務分担を整理する。
- Phase8 に送る新機能バックログを、整合性判断済みの状態で作る。

## 非目的

- Phase7 中に新機能をまとめて実装すること。
- GUI の全面 redesign を再度始めること。
- ラベルだけを先に変えて責務整理を後回しにすること。
- `do-it` の是非を感覚だけで決め、plugin apply や実機運用との関係を見ないこと。

## Phase6 から受け取る前提

- GUI current runtime は glade prototype 前提を外し、`Apply` を即時実行の正本へ戻している。
- save path chooser、watch tab 分離、adapter/runtime 名寄せなどの構造整理は Phase6 で進んだ。
- `Prefs` は Phase6 で必要部品として復旧し、最低限の可視化と config 同期の入口が戻っている。
- `Apply` 結果の疑義は、見た目未達ではなく product alignment 上の整合性論点として Phase7 へ引き継いでいる。
- core / CLI には margin 情報埋め込みや monitor split など、GUI 未露出の機能が既に存在する。
- watch は CLI が loop / apply / failure-continue を持ち、GUI 側も same-process front-end として接続が進んでいる。

## 一次参照

- [docs/specs/gui/gui-phase6-planning.md](docs/specs/gui/gui-phase6-planning.md)
- [docs/specs/gui/gui-phase6-baseline-recheck.md](docs/specs/gui/gui-phase6-baseline-recheck.md)
- [docs/specs/gui/gui-phase6-cli-reference-check.md](docs/specs/gui/gui-phase6-cli-reference-check.md)
- [docs/specs/core/margin-info-embedding.md](docs/specs/core/margin-info-embedding.md)
- [docs/specs/core/monitor-split-design.md](docs/specs/core/monitor-split-design.md)
- [docs/specs/watch/harite-watch-minimum-spec.md](docs/specs/watch/harite-watch-minimum-spec.md)
- [docs/manual-validation-gate.md](docs/manual-validation-gate.md)
- [docs/meta/do-it.md](docs/meta/do-it.md)
- [src/harite/cli.py](src/harite/cli.py)
- [src/harite/core.py](src/harite/core.py)
- [src/harite/plugins.py](src/harite/plugins.py)

## 文書構成

- index / 入口:
  - [docs/specs/gui/gui-phase7-product-alignment-planning.md](docs/specs/gui/gui-phase7-product-alignment-planning.md)
- Workstream 1: 機能棚卸し
  - [docs/specs/gui/gui-phase7-workstream1-inventory.md](docs/specs/gui/gui-phase7-workstream1-inventory.md)
- Workstream 2: 操作語彙の再設計
  - [docs/specs/gui/gui-phase7-workstream2-operation-semantics.md](docs/specs/gui/gui-phase7-workstream2-operation-semantics.md)
- Workstream 3: watch の責務再定義
  - [docs/specs/gui/gui-phase7-workstream3-watch-responsibility.md](docs/specs/gui/gui-phase7-workstream3-watch-responsibility.md)
- Workstream 4: GUI 候補機能の再読
  - [docs/specs/gui/gui-phase7-workstream4-gui-candidate-recheck.md](docs/specs/gui/gui-phase7-workstream4-gui-candidate-recheck.md)

## Workstream 一覧

| Workstream | 主題 | 現在地 | 詳細 |
| --- | --- | --- | --- |
| 1 | 機能棚卸し | 初版作成済み | [docs/specs/gui/gui-phase7-workstream1-inventory.md](docs/specs/gui/gui-phase7-workstream1-inventory.md) |
| 2 | 操作語彙の再設計 | 主要論点の棚卸しと暫定方針は一巡済み。`align/valign` の左右別 semantics も母体踏襲で close | [docs/specs/gui/gui-phase7-workstream2-operation-semantics.md](docs/specs/gui/gui-phase7-workstream2-operation-semantics.md) |
| 3 | watch の責務再定義 | 接続方針と責務整理は完了、close 前の文言整理と manual validation を残す | [docs/specs/gui/gui-phase7-workstream3-watch-responsibility.md](docs/specs/gui/gui-phase7-workstream3-watch-responsibility.md) |
| 4 | GUI 候補機能の再読 | 第1巡の比較メモに加え、explicit mapping の GUI 非対象境界まで実装反映済み | [docs/specs/gui/gui-phase7-workstream4-gui-candidate-recheck.md](docs/specs/gui/gui-phase7-workstream4-gui-candidate-recheck.md) |

## 現時点の主要判断

- `Default` は current 実装上 `single-file` として読み、将来的には `分割せず適用` 系の非曖昧語へ寄せる。
- `Auto-split` は Harite 独自価値として `Apply` の主導線に置く。
- explicit mapping (`--left-file` / `--right-file`) は CLI 専用の低露出 escape hatch として残す。
- explicit mapping は GUI に露出しない一方、既存 config / prefs 経路で unsupported mode を破壊しないところまで Phase7 で閉じる。
- `align` / `valign` は Harite 独自の single 値類推を捨て、母体どおり左右別 pair を正本として扱う。
- GUI watch は CLI watch / watch runner を利用する same-process front-end として扱う。
- `Prefs` は残し、既定値とその場の作業状態を分ける方向で整理する。
- `embed-text` / margin info、preview / visual assist、`Color` は Phase8 候補として扱い、Phase7 主導線へは無理に上げない。

## Workstream 4 の現時点成果物

- `Prefs` と main/settings 境界の整理メモ
- `Apply` visible 語彙と補助文言の整理メモ
- `embed-text` / margin info embedding の GUI 露出判断メモ
- preview / visual assist の現在地メモ
- `Color` など deferred 項目の扱いメモ
- GUI 候補機能リスト（初版）
- Phase8 backlog 素案

## PR 区切りの考え方

- `Prefs` と main/settings 境界、および比較観点が一巡した時点を最初の区切りとする。
- `embed-text` / preview / deferred 項目まで含めて候補機能リストが揃った時点を次の区切りとする。
- 重要な変更や区切りでは、その都度 PR を促す。

## 完了条件

- CLI / GUI / core の差分が、`意図差` / `抜け漏れ` / `削除候補` / `Phase8 候補` に分類されている。
- `optimize` / `apply` / `dry-run` / `do-it` / `watch` の語彙と責務境界について、owner 判断に必要な材料が揃っている。
- GUI に入れる候補機能が、単なる思いつきではなく Phase8 backlog として列挙されている。
- Phase8 に送る新機能と、Phase7 内で閉じる設計整理が分離されている。
- 少なくとも `do-it` の扱いについて、維持 / 改名 / 廃止の比較が文書化されている。

## 判断メモ

- `do-it` は単なるオプション名ではなく、CLI の安全設計と GUI の即時実行ポリシーの衝突点である。
- したがって `do-it` の再整理は、CLI UX だけでなく manual gate / docs / plugin apply の説明にも波及する。
- `watch` の不足補完は新機能追加に見えるが、実際には CLI 先行機能との整合性整理でもある。
- `embed-text` のような margin 利用機能は、GUI に持ち込むと制作画面としての意味が増すため、Phase8 候補として価値が高い。
- `Auto-split` は、現時点では `Apply` の主導線に最も近い Harite 独自機能として扱うのが自然である。
- `per-monitor-explicit` は残すとしても、`auto-split` より前面に出すのではなく CLI 側の低露出な escape hatch に留める。
- 逆に、GUI に理由なく CLI 専用機能をそのまま移植すると、Phase6 で落とした暫定 UI の複雑さを戻す危険がある。

## 初動タスク

### T7-1. 機能棚卸し表の作成

- CLI / GUI / core の機能差分を 1 表へまとめる。

### T7-2. 操作語彙比較メモの作成

- `optimize` / `apply` / `dry-run` / `do-it` / `watch` の意味を並べ、候補案を比較する。

### T7-3. watch responsibility memo の作成

- GUI watch を CLI watch の front-end として扱うかを中心に、責務境界を再定義する。

### T7-4. GUI 候補機能バックログの作成

- `embed-text`、per-monitor apply、preview、deferred 項目などを Phase8 候補として整理する。

## Phase8 の位置づけ

- Phase8 は、Phase7 で承認された候補機能だけを実装するフェーズとする。
- Phase8 は探索フェーズではなく、仕様化済み backlog の実装フェーズとして扱う。
- Phase7 で整合性整理が終わらない限り、Phase8 の着手条件は満たさない。

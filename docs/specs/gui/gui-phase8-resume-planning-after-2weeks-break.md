# GUI Phase 8 Resume Planning After 2 Weeks Break

最終更新: 2026-05-09

## 目的

- 本書は、2026-04-21 から 2026-04-23 に起こした Phase8 planning / backlog / repair-plan を、2026-05-09 時点の実装・実機確認結果に重ねて読み直すための再開用 index である。
- 既存の Phase8 文書を歴史ごと書き換えるのではなく、どの文書が今も正本で、どこが既に消化済みで、どこが未了かを短く固定する。
- 次ブランチで `gui-phase8-traceability-followup-memo.md` を着手対象に入れるべきか、それとも repair-plan 未了項目を先に閉じるべきかを判断できる状態を作る。

## 文書の役割と現在地

### 1. planning

- [docs/specs/gui/gui-phase8-planning.md](docs/specs/gui/gui-phase8-planning.md) は、Phase8 を preview / embed 系 GUI 昇格 / deferred legacy の 3 group で整理した初期 index として読む。
- 現在の main では、group 2 の一部が先行実装されており、group 順そのままの「未着手一覧」としては読まない。

### 2. backlog

- [docs/specs/gui/gui-phase8-backlog.md](docs/specs/gui/gui-phase8-backlog.md) は、P8-2A / P8-2B の意図と wording 議論を残す設計メモとしてまだ有効である。
- ただし `Embed` から `Margins` / `Margin text` への visible rename とレイアウト再配置は、backlog 上の候補ではなく一度実装・実機確認済みの扱いへ進んだ。

### 3. precedence audit

- [docs/specs/gui/gui-phase8-precedence-audit-memo.md](docs/specs/gui/gui-phase8-precedence-audit-memo.md) は、optimize / apply / GUI wording の責務境界を読むための正本として維持する。
- 次に semantics 修復を進めるときは、本メモを再読してからブランチ責務を切る。

### 4. repair plan

- [docs/specs/gui/gui-phase8-repair-plan.md](docs/specs/gui/gui-phase8-repair-plan.md) は、branch order の正本として使い続ける。
- ただし本文の「現時点の実行順」は 2026-04-23 時点の前提なので、そのまま現在地とはみなさない。
- 現在地の overlay は本書で扱う。

### 5. margins contract

- [docs/specs/gui/gui-margin-tab-grid-re-layout-contract.md](docs/specs/gui/gui-margin-tab-grid-re-layout-contract.md) は、`feature/margin-tab-grid-re-layout` のローカル contract として役目を果たした。
- 表示性・機能性・Optimize / Apply を含む確認が済んだため、この contract は「閉じたブランチの正本」として参照し、次ブランチの入口文書にはしない。

### 6. traceability follow-up memo

- [docs/specs/gui/gui-phase8-traceability-followup-memo.md](docs/specs/gui/gui-phase8-traceability-followup-memo.md) は、Margins branch 完了後に見えた GUI traceability debt を次の専用ブランチへ送る短い設計メモである。
- これは Phase8 の全体順を置き換える文書ではなく、repair-plan の途中または後段に差し込む GUI 専用メモとして扱う。

## 2026-05-09 時点の実装観測

### 完了として扱ってよいもの

- `Margins` / `Margin text` への visible rename と GUI 配置変更
- 5 行 text area 化と入力ガード
- `Margins (for each display)` を含む手動調整
- MainWindow 側 alignment sign を残す補助表示
- 関連 GUI テスト通過、および owner による表示性・機能性・Optimize / Apply 確認

### docs と実装がまだずれているもの

- repair-plan 上は `phase8-gui-margins-tab` が「これから実施」に見えるが、実態は完了済み
- [docs/specs/gui/gui-margin-tab-grid-re-layout-contract.md](docs/specs/gui/gui-margin-tab-grid-re-layout-contract.md) の固定 visible layout 冒頭には `Margins` のままとある一方、Grid contract と実装・実機確認では `Margins (for each display)` へ進んでいる

### 未了として扱うべきもの

- `padding` / `mosaic` の整理は未完了
  - 2026-05-09 時点確認で [src/harite/core.py](src/harite/core.py) に `padding` 処理が残っている
  - 同日時点確認で [tests/core/test_core.py](tests/core/test_core.py)、[tests/core/test_core_twoscreen.py](tests/core/test_core_twoscreen.py)、[tests/regression/test_regression_parity.py](tests/regression/test_regression_parity.py) などに `padding` / `mosaic` 前提テストが残っている
- `Margins` 4 値の意味論修復は未着手
  - 母体は左右 display 双方へ同じ margin 値を適用する前提だが、Harite 現状は `global outer margins` として先に canvas 全体へ効かせている
  - この差は wording 調整ではなく core/CLI semantics の修復として扱う
- `margin text` display-target は未着手
- preview / visual assist、`Color`、`About` は backlog 上の別群として残っている

## 再計画

### 判断 1. follow-up memo は「次で必ず着手」ではない

- [docs/specs/gui/gui-phase8-traceability-followup-memo.md](docs/specs/gui/gui-phase8-traceability-followup-memo.md) の課題は妥当だが、性質は GUI traceability 改善であり、意味論修復の代替ではない。
- したがって repair-plan の未了項目が残っている限り、常に最優先とまでは置かない。

### 判断 2. 次ブランチの第一候補は `padding` / `mosaic` 整理

- repair-plan の順を尊重するなら、次に消すべき未了の太い項目は `phase8-drop-padding-mosaic` である。
- 理由は、GUI wording より下層の core / regression surface にまだ残っており、Phase8 の semantics 修復列がそこで止まっているためである。

### 判断 3. `Margins` 4 値の見直しは `padding` / `mosaic` の直後に置く

- `global outer margins` を母体準拠の screen-bound margin semantics へ寄せる修復は、次の独立ブランチとして扱う。
- この段では、`Margins` 4 値を左右 display 双方へ同じ値として適用する前提へ戻し、`global outer margins` 前提の説明や計算順を縮退させる。
- これは GUI wording の微修正ではなく、optimize 側の拘束順と margin 解釈を直す semantics 修復として切り出す。

### 判断 4. traceability follow-up の着手タイミング

- 第一候補: `Margins` 4 値の意味論修復完了直後
- 条件付き前倒し候補: 今回の 2 週間 break 後にまず変更追跡性を上げてから次の semantics 修復へ入りたい場合
- ただし前倒しする場合も、「repair-plan の順から一時的に外す」という判断を PR 本文と本書に明記する

## 推奨の次アクション

1. この docs ブランチでは、本書を resume index として追加し、既存 Phase8 docs からの導線だけを足す
2. 実装ブランチの第一候補は `phase8-drop-padding-mosaic` とする
3. その次に、`Margins` 4 値を母体準拠へ戻す semantics 修復ブランチを切る
4. `gui-phase8-traceability-followup-memo.md` は、その後に `phase8-gui-traceability-followup` 相当の専用ブランチで扱う
5. もし break 明けの再始動コストを下げることを優先するなら、4 を 2 より前へ送ってよいが、その場合は「semantics 修復より traceability 改善を先に置く理由」を明文化する

## この文書を読んだあとの進み方

- semantics を直すブランチへ進むなら [docs/specs/gui/gui-phase8-precedence-audit-memo.md](docs/specs/gui/gui-phase8-precedence-audit-memo.md) と [docs/specs/gui/gui-phase8-repair-plan.md](docs/specs/gui/gui-phase8-repair-plan.md) を再読する
- GUI traceability ブランチへ進むなら [docs/specs/gui/gui-phase8-traceability-followup-memo.md](docs/specs/gui/gui-phase8-traceability-followup-memo.md) を正本として使う
- 完了済み Margins レイアウトの確認結果を辿るときだけ [docs/specs/gui/gui-margin-tab-grid-re-layout-contract.md](docs/specs/gui/gui-margin-tab-grid-re-layout-contract.md) を参照する

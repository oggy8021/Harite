# GUI Phase 8 Resume Planning After 2 Weeks Break

最終更新: 2026-05-10

## 目的

- 本書は、2026-04-21 から 2026-04-23 に起こした Phase8 planning / backlog / repair-plan を、2026-05-10 時点の実装・実機確認結果に重ねて読み直すための再開用 index である。
- 既存の Phase8 文書を歴史ごと書き換えるのではなく、どの文書が今も正本で、どこが既に消化済みで、どこが未了かを短く固定する。
- `phase8-drop-padding-mosaic` と `phase8-fix-margin-semantics` を取り込んだ後の現在地を固定し、次に `gui-phase8-traceability-followup-memo.md` をどう扱うかを判断できる状態を作る。

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

- [docs/specs/gui/gui-phase8-margin-tab-grid-re-layout-contract.md](docs/specs/gui/gui-phase8-margin-tab-grid-re-layout-contract.md) は、`feature/margin-tab-grid-re-layout` のローカル contract として役目を果たした。
- 表示性・機能性・Optimize / Apply を含む確認が済んだため、この contract は「閉じたブランチの正本」として参照し、次ブランチの入口文書にはしない。

### 6. traceability follow-up memo

- [docs/specs/gui/gui-phase8-traceability-followup-memo.md](docs/specs/gui/gui-phase8-traceability-followup-memo.md) は、Margins branch 完了後に見えた GUI traceability debt を次の専用ブランチへ送る短い設計メモである。
- これは Phase8 の全体順を置き換える文書ではなく、repair-plan の途中または後段に差し込む GUI 専用メモとして扱う。

## 2026-05-10 時点の実装観測

### 完了として扱ってよいもの

- optimize 後 / apply 前の生成済みファイル preview
  - MainWindow / runtime backend 上で、左右 2 面の縮小 preview、preview source、assignment、assist summary、result note まで確認できる
- preview / visual assist の最小セット
  - `single-file` の同一画像適用、`Auto-split` の pseudo split result、配置要約と左右割当の可視化まで実装済みとして扱ってよい
- `Margins` / `Margin text` への visible rename と GUI 配置変更
- 5 行 text area 化と入力ガード
- `Margins (for each display)` を含む手動調整
- MainWindow 側 alignment sign を残す補助表示
- `padding` / `mosaic` 残骸の整理
- `Margins` 4 値の意味論修復
  - explicit two-screen / implicit two-screen の双方で、margin を canvas 全体ではなく各 display slice に対して適用するよう修復済み
  - 同一 display を並べ、同一画像を Auto-split で Optimize したときに同じ壁紙配置が得られることを確認済み
- margin text / preflight / GTK runtime backend の display-slice 整合
- GUI traceability debt のうち、Settings / Save As / margin canonical 化と audit inventory 作成
  - canonical 名の整理結果は [docs/specs/gui/gui-phase8-traceability-followup-memo.md](docs/specs/gui/gui-phase8-traceability-followup-memo.md) と [docs/specs/gui/gui-phase8-traceability-audit-inventory.md](docs/specs/gui/gui-phase8-traceability-audit-inventory.md) を正本として扱う
- 関連 GUI テスト通過、および owner による表示性・機能性・Optimize / Apply 確認

### docs と実装がまだずれているもの

- repair-plan 上は `phase8-gui-margins-tab` が「これから実施」に見えるが、実態は完了済み
- [docs/specs/gui/gui-phase8-margin-tab-grid-re-layout-contract.md](docs/specs/gui/gui-phase8-margin-tab-grid-re-layout-contract.md) の固定 visible layout 冒頭には `Margins` のままとある一方、Grid contract と実装・実機確認では `Margins (for each display)` へ進んでいる
- repair-plan / overlay 上では traceability follow-up が未着手候補に読める箇所が残るが、memo / inventory / code 実態は整理済みである

### 未了として扱うべきもの

- Phase8 の主対象としては、現時点で未了と扱うべき太い項目はない。
- close 判定の正本は [docs/specs/gui/gui-phase8-closing.md](docs/specs/gui/gui-phase8-closing.md) として扱う。

### 現行判定として補足するもの

- `margin text` display-target は、branch 7 の独立 feature としては現時点では起こさない。
- 理由は、[docs/specs/gui/gui-phase8-margin-tab-grid-re-layout-contract.md](docs/specs/gui/gui-phase8-margin-tab-grid-re-layout-contract.md) の `Position:` が既に `Left/Right x Top/Bottom` の 4 候補を user-facing に持ち、visible requirement としては実質充足済みだからである。
- 今後これを再起動する場合は、visible requirement の不足ではなく、内部 state 分離や schema 再設計の別責務として扱う。

## 再計画

### 判断 1. traceability follow-up は整理済みとして扱う

- [docs/specs/gui/gui-phase8-traceability-followup-memo.md](docs/specs/gui/gui-phase8-traceability-followup-memo.md) の課題は、`padding` / `mosaic` 整理と `Margins` 4 値意味論修復の後段で扱う前提だった。
- その前提は満たされ、canonical 名整理と inventory 化まで実施済みである。

### 判断 2. Group 3 まで到達済みとして close 判定へ進める

- traceability 系は、現時点では新規専用ブランチ候補というより、完了済み整理結果の参照先として維持する段に入った。
- preview / visual assist は、backlog 上の Group 1 定義に対して実装がかなり先行しており、現時点では未了の主題としては扱わない。
- `Color` と `About` はともに placeholder 段を抜け、Group 3 の主対象は到達済みとして扱ってよい。
- したがって、Phase8 は次の feature 実装へ進む前に close 判定を行う段に入った。

### 判断 3. `Margins` 4 値修復は通過済みとして扱う

- `global outer margins` を前提にした主要経路は、optimize / preflight / runtime backend を含めて修復済みと扱う。
- 今後この話題が再浮上する場合は、新規 semantics 修復ではなく residual difference の確認として扱う。

### 判断 4. pre-closing では stale な現在地記述だけを整える

- 実装の追加要求をここで起こすのではなく、既に整理済みの traceability memo / inventory と overlay の現在地を一致させる。
- pre-closing の docs ブランチでは、追加 feature を混ぜずに stale な導線と現在地記述の修正だけを扱えばよい。

## 推奨の次アクション

1. この docs ブランチでは、本書を resume index として追加し、既存 Phase8 docs からの導線だけを足す
2. この follow-up では、`padding` / `mosaic` 整理と `Margins` 4 値意味論修復が通過済みであることを本書に反映する
3. traceability の正本は [docs/specs/gui/gui-phase8-traceability-followup-memo.md](docs/specs/gui/gui-phase8-traceability-followup-memo.md) と [docs/specs/gui/gui-phase8-traceability-audit-inventory.md](docs/specs/gui/gui-phase8-traceability-audit-inventory.md) とする
4. close 判定の正本は [docs/specs/gui/gui-phase8-closing.md](docs/specs/gui/gui-phase8-closing.md) へ集約する
5. post-Phase8 の追加 polish は別ブランチへ分けて扱う

## 現時点の close 判定

- preview / visual assist、traceability、margin text display-target 判断は先行整理済みである。
- `Color` / `About` を含む Group 3 まで到達済みになったため、Phase8 は現時点で close 可能と判断してよい。
- close 判定の要約と residual scope は [docs/specs/gui/gui-phase8-closing.md](docs/specs/gui/gui-phase8-closing.md) を参照する。

## この文書を読んだあとの進み方

- repair-plan の順と現在地 overlay の差を再確認したいときは [docs/specs/gui/gui-phase8-repair-plan.md](docs/specs/gui/gui-phase8-repair-plan.md) を参照する
- GUI traceability ブランチへ進むなら [docs/specs/gui/gui-phase8-traceability-followup-memo.md](docs/specs/gui/gui-phase8-traceability-followup-memo.md) を正本として使う
- 完了済み Margins レイアウトの確認結果を辿るときだけ [docs/specs/gui/gui-phase8-margin-tab-grid-re-layout-contract.md](docs/specs/gui/gui-phase8-margin-tab-grid-re-layout-contract.md) を参照する

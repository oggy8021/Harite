# Harite Project Initial Build Reformation

最終更新: 2026-05-16

## 位置づけ

- 本書は [docs/specs/gui/gui-phase11-closing.md](docs/specs/gui/gui-phase11-closing.md) の次に置く親文書である。
- Phase9-11 で達成したのは、10年前遺産を current GUI と OS integration を含む現代的な形へ更新することだった。
- したがって次段では、GUI をさらに作り込むことより、製品として閉じるための整理、packaging、文書体系再編、仕様書整備を主題に置く。
- 本書は `spec` そのものではなく、初期製造を閉じて `1.0.0` へ向かうための再編計画の親文書として扱う。

## 現在地

- GUI 本体、tray icon、application icon family、XFCE 実機確認まで含めて、Phase11 は close 扱いへ進めてよい状態にある。[docs/specs/gui/gui-phase11-closing.md](docs/specs/gui/gui-phase11-closing.md)
- ただし現時点では、docs 群は planning / 履歴 / 検証記録が厚く、運用と後続機能追加を受ける常設文書体系としてはまだ重い。
- packaging、sdist、release judgement も未整理であり、「完成した Harite をどう出荷するか」はまだ閉じていない。
- 起動時メッセージや周辺の掃除も、初期製造の仕上げとして残っている。

## 基本判断

- `0.2.0` はここでは採らない。
- release judgement は、GUI 単体の完成ではなく、製品として閉じる条件で判断する。
- したがって `1.0.0` の gate は、少なくとも本書の Workstream 1-3 が揃うことに置く。
- Workstream 4 は `1.0.0` 条件ではなく、post-1.0.0 の新運用入口として扱う。

## Workstream 構成

### Workstream 1. 仕上げ・掃除・packaging・release 準備

主題:

- 大掃除
- 起動時メッセージの削除または非表示化
- packaging 整備
- sdist 作成
- `1.0.0` release judgement

この stream で扱うこと:

- current GUI / tray / application icon 実装を前提に、出荷時に不要なログ、起動ノイズ、暫定説明、余剰導線を整理する。
- `pyproject.toml`、package data、entrypoint、配布物構成を点検し、sdist / 配布観点で破綻しない状態へ寄せる。
- release notes、CHANGELOG、version judgement の最小整理を行う。

この stream で扱わないこと:

- 新機能追加
- docs 全面再編の設計論そのもの
- 将来構想の棚卸し

想定成果物:

- release / packaging 方針メモ
- 起動時メッセージ整理の判断メモ
- `1.0.0` 出荷可否を判断できる最小証跡

### Workstream 2. docs 再編と大構想資料の点検

主題:

- 大憲章、大きな構想資料、重い履歴 docs の点検
- docs の再フォーメーション
- 初期製造ベースから、運用 / 後続新機能追加を受けられる形への再構成

この stream で扱うこと:

- 現在の docs 群を、planning、closing、validation record、常設仕様、運用 docs、将来構想 docs に分けて整理する。
- GUI とその履歴に寄りすぎた重い流れを見直し、日常参照する文書と履歴保存文書を分ける。
- 大憲章や大型構想資料について、現行 Harite と整合しない記述、役割が曖昧な文書、重複した parent 文書を点検する。

この stream で扱わないこと:

- 詳細仕様本文の全面執筆そのもの
- 新機能の優先順位決定

想定成果物:

- docs map / 情報設計メモ
- 常設 docs と履歴 docs の切り分け方針
- 保持、縮退、統合、アーカイブ候補の一覧

### Workstream 3. 真の読みものとしての仕様書

主題:

- 調整履歴や planning の集積ではなく、現行 Harite を読むための仕様書を作る

この stream で扱うこと:

- Harite の目的、対象利用者、主要環境、主要導線、用語、設定、watch、tray、GUI / CLI 関係、保存 / 適用の基本動作を、履歴依存なしに読める形で書き下ろす。
- 「どう決まったか」より「今どうなっているか」を正本にする。
- Workstream 2 の docs 再編結果を受け、常設文書として読む順序を固定する。

この stream で扱わないこと:

- planning 履歴の再要約
- 過去論争の保存
- post-1.0.0 機能構想の詳細化

想定成果物:

- 仕様書正本の親文書
- 必要なら surface ごとの下位仕様
- README と矛盾しない常設仕様導線

### Workstream 4. post-1.0.0 の新運用と後続機能棚卸し

主題:

- 後続新機能の棚卸し
- overview 作成
- 外部壁紙サイト連携などの将来構想の受け皿作り

この stream の位置づけ:

- この stream は `1.0.0` gate ではない。
- `1.0.0` 後の新運用で扱う入口であり、製品を閉じた後に開く backlog / overview 層として扱う。

この stream で扱うこと:

- 断片的に存在する構想、妄想、保留アイデアを inventory 化する。
- 「すぐ作る」「構想として残す」「捨てる」を粗く切り分ける。
- 外部壁紙サイト連携のような将来テーマを、単発メモではなく overview として受ける。

想定成果物:

- feature inventory
- post-1.0.0 overview
- 次期 planning の入口メモ

## stream 間の順序

1. Workstream 1 と Workstream 2 を初動として始める。
2. Workstream 3 は Workstream 2 の docs map を受けながら進める。
3. `1.0.0` judgement は Workstream 1-3 が揃った時点で行う。
4. Workstream 4 は `1.0.0` 後の運用に送る。

## 1.0.0 の暫定 gate

- packaging / sdist / release judgement が説明可能になっている。
- 出荷時に不要な起動時メッセージや暫定ノイズを整理済みである。
- docs 体系が、planning 履歴中心ではなく、運用と保守が可能な形へ再編されている。
- 現行 Harite を読むための常設仕様書が存在する。
- GUI 完成を理由とした中間版 `0.2.0` はここでは採らず、製品として閉じる版を `1.0.0` に置く。

## 初手の子文書名案

- `docs/reformation/harite-project-initial-build-reformation-ws1-release-prep.md`
- `docs/reformation/harite-project-initial-build-reformation-ws2-docs-reformation.md`
- `docs/reformation/harite-project-initial-build-reformation-ws3-spec-authoring.md`
- `docs/reformation/harite-project-initial-build-reformation-ws4-feature-overview.md`

## 非目的

- Phase11 を reopen して tray / icon / GUI polish を続けること。
- `1.0.0` 前に後続新機能の実装へ流れ込むこと。
- docs をまた履歴増築で重くすること。

## 完了条件

- reformation 全体の親文書として、Workstream 1-4 の境界が説明可能になっている。
- `1.0.0` 条件が Workstream 1-3 にあることが説明可能になっている。
- Workstream 4 が post-1.0.0 の新運用入口であることが説明可能になっている。
- Phase9-11 の closing 後に、次段の整理がどこから始まるか説明可能になっている。

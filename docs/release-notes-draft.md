# Harite リリースノート草案

最終更新: 2026-05-16
対象バージョン: v1.0.0 draft

## 概要

この草案は、Harite を `1.0.0` として初期製造へ寄せるための release note 叩き台です。現時点では version bump 自体は未確定ですが、current GUI を含む現行成果、packaging / license 整理、release 前に残る確認点を 1 か所で読めるようにしています。

## 今回の主題

- current GUI を、GTK ベースの通常利用導線として整理した。
- tray / application icon、About / Settings 周辺、header icon を含む GUI runtime 資産を current 構成へ統合した。
- release build に向けて、通常 GUI 起動時の常設 stdout ノイズを削減した。
- license / third-party notice を配布物へ残す前提を整えた。

## 主な変更

### GUI / UX

- current GUI の visual operation view、header icon、settings/dialog semantics を実装・整理。
- Main / Margins / Watch tab の layout を再構成し、current GUI 前提の導線へ寄せた。
- About dialog と application / tray icon 周辺を整理し、XFCE first target の runtime 実装へ統合した。

### Runtime / Packaging

- `harite-gui` を含む GUI 起動導線を current runtime 前提で整理。
- `src/harite/gui/resources/` 配下の runtime asset を package data として配布対象に維持。
- [LICENSE](LICENSE) に加え、vendor した Lucide icon 用 notice を [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) として配布物へ残す構成を追加。

### Release Prep

- 通常 GUI 起動時の `ready` / `skipped` / skeleton 系 stdout 出力を削除し、release build 前提の常設ノイズを解消。
- release 判定は大部 checklist ではなく、WS1 で管理する少数 gate へ縮退。

## 既知の制約

- Linux の壁紙設定はデスクトップ環境依存です。XFCE 以外では環境差分により挙動が異なる場合があります。
- tray / indicator 系は XFCE first target の runtime 実装であり、desktop 環境差分は別途残ります。
- `1.0.0` として何を最終同梱範囲にするか、version bump と最終 release judgement は未確定です。

## 検証サマリー

- owner 実行の GUI テスト:
  - `c:/Users/oggy_/Develop/Repos/Harite/.venv/Scripts/python.exe -m pytest .\tests\gui` 成功
- current GUI / tray / application icon については、これまでの WS / planning / closing 文書と owner 実機確認を前提に整理済み。
- packaging / build / clean install の最終確認は、WS1 Gate 2-4 の残作業として継続中。

## 配布物案

- `harite-<version>-py3-none-any.whl`
- `harite-<version>.tar.gz`

## 未確定事項

- 最終 version を `1.0.0` に上げるタイミング
- release note 本文へ残す「今回の売り」を GUI 中心で寄せるか、CLI 継続面も併記するか
- build / install / manual validation の最終証跡をどこまで本文へ埋め込むか

## 参照

- [docs/reformation/harite-project-initial-build-reformation-ws1-release-prep.md](docs/reformation/harite-project-initial-build-reformation-ws1-release-prep.md)
- [docs/release-delivery.md](docs/release-delivery.md)
- [CHANGELOG.md](CHANGELOG.md)

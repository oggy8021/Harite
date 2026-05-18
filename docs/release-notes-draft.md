# Harite リリースノート草案

最終更新: 2026-05-18
対象バージョン: v1.0.0 draft

## 概要

Harite は、マルチディスプレイ環境で壁紙画像を生成・配置・適用するためのツールです。複数の入力画像から壁紙を作成し、画面ごとの配置、余白、固定配置、単画面利用を扱えます。

この草案は `1.0.0` リリース本文の叩き台であり、現時点では version bump 自体は未確定です。ここでは、今回の版で外向けに何を出すか、利用者にとって何が変わるか、既知の制約は何かを整理します。

## 今回の要点

- GTK ベースの GUI を通常利用向けの構成として整備しました。
- GUI の icon / dialog / watch 周辺を見直しました。
- release build に向けて、通常 GUI 起動時の不要な常設ノイズを削減しました。
- 配布物へ含める license / third-party notice の前提を整理しました。

## 主な内容

### GUI / UX

- GUI を通常利用向けの構成として整理しました。
- Main / Margins / Watch tab の構成を見直し、日常利用で迷いにくい導線へ寄せました。
- Settings / Color / About dialog の役割を整理し、操作上の意味づけを明確化しました。
- application icon と header icon を含む GUI 資産を整理しました。

### Runtime / Packaging

- `harite-gui` を GUI の起動導線として提供します。
- `src/harite/gui/resources/` 配下の GUI 資産を package data として配布対象に含めます。
- [LICENSE](LICENSE) に加え、vendor した Lucide icon 用 notice を [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) として同梱する前提を整えています。

### 安定化 / 整理

- 通常 GUI 起動時の `ready` / `skipped` / skeleton 系 stdout 出力を削減しました。
- watch 周辺の安定化を進め、一時的な display 検出崩れに対する pause / resume の扱いを改善しました。
- dialog / feedback / icon 周辺の細部を継続的に調整しました。

## 既知の制約

- Linux の壁紙設定はデスクトップ環境依存です。XFCE 以外では環境差分により挙動が異なる場合があります。
- GUI / packaging の最終確認と version bump は継続中であり、本文は確定前の draft です。

## 検証サマリー

- owner 実行の GUI テスト:
  - `python.exe -m pytest .\tests\gui` 成功
- GUI / application icon については、owner 実機確認を含めて継続的に調整しています。
- packaging / build / clean install の最終確認は、`1.0.0` 確定前に別途詰めます。

## 配布物

- `harite-<version>-py3-none-any.whl`
- `harite-<version>.tar.gz`

## 未確定事項

- 最終 version を `1.0.0` に上げるタイミング
- release 本文で GUI 中心に寄せる範囲と、CLI 継続面をどこまで併記するか
- build / install / 実機確認の最終証跡をどこまで release 本文へ反映するか

## 参照

- [docs/release-delivery.md](docs/release-delivery.md)
- [CHANGELOG.md](CHANGELOG.md)

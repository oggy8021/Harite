# Harite リリースノート

最終更新: 2026-03-21
対象バージョン: v0.1.1

## 概要

このリリースでは、実運用フィードバックを反映し、2画面分割の堅牢性と余白活用の改善を行いました。特に、低解像度合成画像でも破綻しにくい auto-split の改善と、余白への情報埋め込み（MVP）を追加しています。

## 主な変更

- optimize UX/仕様整理:
  - `--input` 複数指定と `--two-screen` の実効仕様を `--help` と仕様書に反映
  - パラメータの効きの強弱を明文化
- auto-split 改善:
  - 仮想デスクトップ座標を比率マッピングするクロップへ変更
  - 低解像度合成でも左右分割が破綻しにくい挙動へ改善
  - 回帰テストを追加
- 余白情報埋め込み（MVP）:
  - `--embed-info` (`none|params|free|combo`) を追加
  - `--embed-text` / `--embed-position` / `--embed-max-lines` を追加
  - 余白不足時は安全にスキップし、画像本体には重ね描画しない

## 既知の制約

- Linux の壁紙設定はデスクトップ環境依存です。XFCE 以外では環境差分により挙動が異なる場合があります。
- 余白情報埋め込みは余白量に依存します。余白不足時は意図的に描画をスキップします。

## 検証サマリー

- ローカルテスト: `pytest` 全件成功
- CI: 必須チェック成功
- 配布検証:
  - `python -m build --sdist --wheel` 成功
  - クリーン環境への wheel インストール成功
  - `.venv` 非依存で `harite optimize --help` / `harite apply --help` 実行成功

## 配布物

- `harite-0.1.1-py3-none-any.whl`
- `harite-0.1.1.tar.gz`

## 参照

- `docs/release-readiness-checklist.md`
- `docs/release-delivery.md`
- `docs/misc/xfce-followup-log.md`
- `docs/misc/xfce-rollback-playbook.md`

# Harite リリースノート

最終更新: 2026-04-12
対象バージョン: v0.1.2

## 概要

このリリースでは、`embed-text` の日本語描画改善（Issue #158）とライセンス整備（MIT）を中心に、配布品質を更新しました。`watch` を含む既存CLI機能への回帰確認も実施対象としています。

## 主な変更

- Issue #158 対応（embed-text 日本語/CJK）:
  - 描画フォントを固定の `ImageFont.load_default()` から改善
  - 既定でシステムの CJK フォント候補を自動探索
  - 必要時のみ `--embed-font` で明示指定可能
- テスト追加:
  - CLI: `--embed-font` 受け渡しテスト
  - Core: 明示フォントパス優先ロードテスト
- 配布整備:
  - `LICENSE`（MIT）追加
  - `pyproject.toml` に license metadata を追記

## 既知の制約

- Linux の壁紙設定はデスクトップ環境依存です。XFCE 以外では環境差分により挙動が異なる場合があります。
- CJK フォントが環境に存在しない場合、埋め込みテキストはデフォルトフォントにフォールバックするため、文字集合によっては表示制限があります。

## 検証サマリー

- ローカルテスト:
  - `c:/Users/oggy_/Develop/Repos/Harite/.venv/Scripts/python.exe -m pytest tests/core/test_core_features.py tests/cli/test_cli_validation.py -q` 成功
- 回帰確認:
  - `watch` 関連テストを含む既存チェックをリリース前に再実施
- CI: 必須チェック成功
- 配布検証:
  - `python -m build --sdist --wheel` 成功
  - クリーン環境への wheel インストール成功
  - `.venv` 非依存で `harite optimize --help` / `harite apply --help` 実行成功

## 配布物

- `harite-0.1.2-py3-none-any.whl`
- `harite-0.1.2.tar.gz`

## 参照

- `docs/release-readiness-checklist.md`
- `docs/release-delivery.md`
- `docs/misc/xfce-followup-log.md`
- `docs/misc/xfce-rollback-playbook.md`

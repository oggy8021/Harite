# Harite リリースノート草案

最終更新: 2026-03-20
対象バージョン: TBD（第7章で確定）

## 概要

このリリースでは、Linux/XFCE の壁紙適用安定性を中心に、テスト・CI・運用ドキュメントを段階的に整備しました。特に、相対パス起因の不安定挙動に対して、実装・テスト・実機検証ログを一体で改善しています。

## 主な変更

- XFCE 向け改善:
  - `last-image` 適用時の絶対パス化を強化
  - 実機フォローアップ（dry-run / `--do-it`）で再発確認を継続
  - 切り戻し手順を playbook 化
- テスト改善:
  - Linux マッピングの回帰テストを調整し、クロスプラットフォームで安定化
- CI 改善:
  - `sdist` / `wheel` ビルドジョブを追加
  - PR チェック運用を維持し、docs 変更も含めて品質ゲートを通過
- ドキュメント整備:
  - リリース準備チェックリストを更新
  - `.venv` 非依存での配布・実行手順を追加（`docs/release-delivery.md`）

## 既知の制約

- Linux の壁紙設定はデスクトップ環境依存です。XFCE 以外では環境差分により挙動が異なる場合があります。
- 実適用（`--do-it`）はシステム設定を書き換えるため、事前に dry-run で確認してください。

## 検証サマリー

- ローカルテスト: `pytest` 全件成功
- CI: 必須チェック成功
- 配布検証:
  - `python -m build --sdist --wheel` 成功
  - クリーン環境への wheel インストール成功
  - `.venv` 非依存で `harite optimize --help` / `harite apply --help` 実行成功

## 配布物

- `harite-<version>-py3-none-any.whl`
- `harite-<version>.tar.gz`

## 参照

- `docs/release-readiness-checklist.md`
- `docs/release-delivery.md`
- `docs/misc/xfce-followup-log.md`
- `docs/misc/xfce-rollback-playbook.md`

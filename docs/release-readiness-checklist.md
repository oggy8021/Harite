# Harite リリース準備チェックリスト

最終更新: 2026-03-20

## 使い方

- このチェックリストは「リリース候補（RC）確定」から「タグ作成」までの抜け漏れ防止を目的とする。
- 各項目は、実施後に PR コメントまたはリリースノート草案へ証跡（コマンド結果・スクリーンショット・ログ要約）を残す。
- ブロッカーが 1 つでもある場合は、リリースを延期し、原因と再開条件を記録する。

## 点検サマリー（2026-03-20）

- 判定（XFCE 向け 1st build）: 機能面は完了扱いで進めてよい。
- 判定（リリース準備）: 第1-6章は完了。第7章（バージョン確定・タグ作成・リリース公開）のみ未実施。
- 解消済み: `pytest` は全件成功（2026-03-20 再実行）。
- 解消済み: `python -m build --sdist --wheel` で `sdist/wheel` 生成成功。
- 解消済み: `.venv` 非依存のクリーン環境で CLI 実行確認成功。
- 追加: リリースノート草案を `docs/release-notes-draft.md` に作成。
- 確定: リリースバージョンを `v0.1.0` に決定。

## 1. コード・ブランチ状態

- [x] `main` が `origin/main` と同期している。
- [x] オープン PR のうち、当該リリースに含める/含めないを明示できている。（open PR なし）
- [x] ブランチ保護ルール（必須チェック・レビュー要件）が有効である。
- [x] 直近でマージした高リスク変更（壁紙適用ロジックなど）を一覧化できている。

## 2. テストと品質ゲート

- [x] ローカルで `pytest` が成功している。
- [x] GitHub Actions の必須 CI が成功している。
- [x] 失敗中または不安定（flake）なテストがない。
- [x] 新規テスト（今回の変更に対応）が追加済み、または不要理由を説明できる。

## 3. 実行確認（CLI）

- [x] `harite optimize --help` の表示を確認した。
- [x] `harite apply --help` の表示を確認した。
- [x] `apply` は dry-run が既定であることを再確認した。
- [ ] `--do-it` 実行時の注意事項を README と整合させた。

## 4. Linux/XFCE 向け最終確認

- [x] `xfconf-query` が利用可能な環境で dry-run を再実行した。
- [x] XFCE 実機で `--do-it` を使ったとき、壁紙が実際に切り替わることを確認した。
- [x] 相対パスではなく絶対パスで適用されることをログまたは設定値で確認した。
- [x] 問題発生時の切り戻し手順（既知の良い画像へ再設定）を確認した。

## 5. ドキュメント・運用

- [x] README の操作例が現行 CLI と一致している。
- [x] `docs/TODOs_jp.md` の進捗が最新化されている。
- [x] 変更に対応するドキュメント（PR フロー、運用ルール等）が更新済み。
- [x] 次タスク（CI で sdist/wheel build）への引き継ぎ事項を記録した。

## 6. 実行環境（.venv 非依存）とデリバリー

証跡: `docs/release-delivery.md`

- [x] クリーン環境で `pip install dist/*.whl` または `pipx install dist/*.whl` が成功することを確認した。
- [x] `.venv` を有効化しない状態で `harite optimize --help` / `harite apply --help` が実行できることを確認した。
- [x] 配布対象（`sdist` / `wheel`）と配布経路（GitHub Releases、社内配布先など）を確定した。
- [x] インストール手順とアンインストール手順（ロールバック手順を含む）を記録した。

## 7. リリース実施（最終）

- [x] バージョン番号を確定した。（`v0.1.0`）
- [x] リリースノート草案（変更概要、注意点、既知の制約）を作成した。
- [ ] リリースタグ作成手順を実行し、参照コミットを確認した。
- [ ] リリース後の監視ポイント（不具合受付窓口、初期フィードバック確認日）を決めた。

## 付録: 最低限の実行コマンド例

```bash
pytest
python -m harite.cli optimize --help
python -m harite.cli apply --help
python -m build --sdist --wheel
# .venv を使わない実行確認の例（別環境）
pipx install dist/*.whl
harite optimize --help
python scripts/xfce_smoke_runner.py --input /abs/path/to/wallpapers --iterations 5
```

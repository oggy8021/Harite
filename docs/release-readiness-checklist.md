# Harite リリース準備チェックリスト

最終更新: 2026-05-25

## 使い方

- このチェックリストは「リリース候補（RC）確定」から「タグ作成」までの抜け漏れ防止を目的とする。
- 各項目は、実施後に PR コメントまたはリリースノート草案へ証跡（コマンド結果・スクリーンショット・ログ要約）を残す。
- ブロッカーが 1 つでもある場合は、リリースを延期し、原因と再開条件を記録する。
- 本書は current release 用の運用チェックリストであり、旧 `v0.1.0` 実施履歴の保管場所としては使わない。旧版の実施経緯は git history を参照する。

## 点検サマリー（2026-05-25）

- 対象リリースは `v1.0.0` を想定する。
- 解消済み: ローカル `python -m pytest -q tests` は成功している。
- 解消済み: リリースノート草案は [docs/release-notes-draft.md](docs/release-notes-draft.md) にある。
- 解消済み: [CHANGELOG.md](CHANGELOG.md) に `1.0.0 (2026-05-25)` 節を作成済みである。
- 解消済み: [pyproject.toml](pyproject.toml) の version は `1.0.0` へ更新済みである。
- 解消済み: `sdist` / `wheel` の current release 候補ビルドは成功している。
- 未確定: XFCE 実機でのクリーン install、タグ作成、GitHub Release 公開は未実施である。

## 1. コード・ブランチ状態

- [ ] リリース対象ブランチと `main` の差分範囲を固定できている。
- [ ] オープン PR のうち、当該リリースに含める/含めないを明示できている。
- [ ] ブランチ保護ルール（必須チェック・レビュー要件）を current 運用として再確認した。
- [ ] 直近でマージした高リスク変更（壁紙適用、GUI runtime、watch、packaging）を一覧化できている。

## 2. テストと品質ゲート

- [x] ローカルで `python -m pytest -q tests` が成功している。
- [ ] GitHub Actions の必須 CI が release 候補コミットで成功している。
- [ ] 失敗中または不安定（flake）なテストがない。
- [ ] current release 範囲の変更に対応するテストが追加済み、または不要理由を説明できる。
- [x] `python -m build --sdist --wheel` が release 候補コミットで成功している。

## 3. 実行確認（CLI）

- [ ] `harite optimize --help` の表示を current CLI surface として確認した。
- [ ] `harite apply --help` の表示を current CLI surface として確認した。
- [ ] `harite slideshow --help` の表示を current CLI surface として確認した。
- [ ] README の CLI 例が current CLI surface と一致している。
- [ ] `apply` が direct apply command であり、旧 `dry-run` / `--do-it` 前提の説明が release 文書から除去されている。

## 4. Linux/XFCE 向け最終確認

- [ ] `xfconf-query` が利用可能な環境で current apply を再実行した。
- [ ] XFCE 実機で current apply により壁紙が実際に切り替わることを確認した。
- [ ] 相対パスではなく絶対パスで適用されることをログまたは設定値で確認した。
- [ ] 問題発生時の切り戻し手順（既知の良い画像へ再設定）を current 手順として確認した。

## 5. ドキュメント・運用

- [ ] README の操作例が現行 CLI / GUI surface と一致している。
- [ ] [docs/release-notes-draft.md](docs/release-notes-draft.md) と [CHANGELOG.md](CHANGELOG.md) の要点が一致している。
- [ ] [docs/release-delivery.md](docs/release-delivery.md) の配布物・install/uninstall 手順が current release 前提に更新されている。
- [ ] 変更に対応するドキュメント（release 手順、運用ルール、validation 記録）が更新済みである。
- [ ] stale な旧 release 前提（`v0.1.0`, `--do-it`, 旧 dry-run 説明）が current release 文書から除去または切り分け済みである。

## 6. 実行環境（.venv 非依存）とデリバリー

証跡: `docs/release-delivery.md`

- [ ] XFCE 実機のクリーン環境で `pip install dist/*.whl` または `pipx install dist/*.whl` が成功することを確認した。
- [ ] XFCE 実機で `.venv` を有効化しない状態の `harite optimize --help` / `harite apply --help` / `harite slideshow --help` / `harite-gui` の入口確認を行った。
- [ ] 配布対象（`sdist` / `wheel`）と配布経路（GitHub Releases など）を current release として確定した。
- [ ] インストール手順とアンインストール手順（ロールバック手順を含む）を current release 前提で記録した。

## 7. リリース実施（最終）

- [x] バージョン番号を `v1.0.0` として確定し、[pyproject.toml](pyproject.toml) へ反映した。
- [x] リリースノート草案（変更概要、注意点、既知の制約）を作成した。
- [ ] リリースタグ作成手順を実行し、参照コミットを確認した。（`v1.0.0` / target: `main`）
- [ ] リリース後の監視ポイント（不具合受付窓口、初期フィードバック確認日）を決めた。

監視ポイント（v1.0.0）

- 不具合受付窓口: GitHub Issues
- 初期フィードバック確認日: TBD

軽量運用版（3項目）

- [ ] GitHub Issues に v1.0.0 関連の新規不具合報告がないことを確認した。
- [ ] インストール/起動（wheel 配布、CLI 実行）で詰まり報告がないことを確認した。
- [ ] XFCE 壁紙適用で再発報告がないことを確認した。

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

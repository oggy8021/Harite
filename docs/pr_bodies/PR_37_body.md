概要
- XFCE 用のディスプレイマッピングに解像度ベースのフォールバックを追加しました。

やったこと
- `src/harite/plugins.py` に解像度ベースの候補選択ロジックを追加。
  - xfconf のプロパティ名に含まれる解像度トークン（例: `2048x1280`）を解析して、`workspace.detect_displays()` で検出したディスプレイ解像度と照合します。
  - 既存の正規化・インデックスベースのマッチングに続く、最終的なフォールバックとして機能します。
- 解像度ベースのマッピングを検証するユニットテスト `tests/test_plugins_xfconf_resolution_mapping.py` を追加。

動作確認
- ローカルで該当テストを実行し、パスすることを確認しました：
  - `pytest -q tests/test_plugins_xfconf_resolution_mapping.py`
- 既存の XFCE 関連テスト群もグリーンであることを確認済み。

テスト
- 新規テストを追加済み（`tests/test_plugins_xfconf_resolution_mapping.py`）。
- 既存テスト（index ベースなど）もすべてローカルで成功しています。

注意事項
- PR 作成時に CI が "PR body が空" を要求するチェックがあるため、この本文を PR に設定してください。

関連PR
- #36: index ベースのフォールバック（マージ済）

レビューのお願い
- ロジックの妥当性（解像度トークンの抽出とマッチング）とテストのカバレッジを確認してください。

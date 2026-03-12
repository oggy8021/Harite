# CHANGELOG

## Unreleased (2026-03-13)

### Added
- Monitor-split 機能: ワークスペース検出に基づくモニタ別分割と個別適用フローを追加しました。
  - CLI フラグ: `--per-monitor`, `--left-file`, `--right-file`, `--auto-split` を実装。
  - コア: `split_composite_for_displays()` を追加し、合成画像をディスプレイ単位で切り出します。
  - ワークスペース検出: `detect_displays()` を追加、`Display` データクラスで構造化された情報を返します。

- Linux/XFCE プラグインの改善:
  - `xfconf-query` の候補を列挙し、dry-run で詳細ログを出力するようにしました。
  - モニタ名→プロパティのマッピングを受け取り、複数モニタへ個別に適用する機能を追加しました。
  - dry-run を実行時に存在するファイルで成功を返す互換性改善を行いました（CI 親和性向上）。

- CLI: `apply` コマンドの挙動を拡張し、auto-split のワイヤリングとプラグインマッピングを実装しました。

- CI / 開発体験:
  - GitHub Actions ワークフローを追加し、Linux/macOS/Windows 上でテストと lint を実行するようにしました。
  - pip キャッシュパスの OS 別確保とワークフローの修正でキャッシュ警告を低減しました。

### Fixed
- `src/harite/cli.py` で未定義だった `path_str` の参照を修正しました。
- Linux プラグインの dry-run 処理で起きていた UnboundLocalError を修正しました。
- テストの未使用 import を削除して linter（ruff）エラーを解消しました。

### Tests
- ユニットテストを追加／調整:
  - workspace 検出、画像分割、Linux プラグインのマッピング・dry-run に関するテストを追加。
  - 現在テストスイートはローカルで 29 tests passed を確認済み。

### Docs
- モニタ分割設計ドキュメントを `docs/specs/monitor-split-design.md` に追加。

---
PR: https://github.com/oggy8021/Harite/pull/4

次のステップ（候補）:
- CHANGELOG を確定してバージョン番号を `pyproject.toml` に反映
- sdist/wheel を作成して動作確認
- Git タグ & GitHub Release の作成

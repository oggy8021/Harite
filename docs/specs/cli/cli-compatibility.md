# CLI 互換マッピング（旧: WallpaperOptimizer → 現行: Harite）

目的

- 旧 `wallpaperoptimizer`（母体） の CLI オプション／機能と、現行 `Harite` CLI の対応関係を明示し、優先復元候補と移植手順を示す。

概要

- 旧実装は `Options.py`/`OptionsBase.py` により多くの細かなオプションを提供し、`Core.py` により合成〜適用までを一括で実行していた。
- 現行は `src/harite/cli.py`（`typer`）で主要コマンドを `optimize`, `compute-placement`, `apply` として提供しており、機能は概ねカバー済みだが一部細目とデーモン機能が未移植。

対応表（代表）

- 基本操作
  - 旧: `wallpaperoptimizer --input DIR --resolution 1920x1080 --layout mosaic`  
    → 現行: `harite optimize --input DIR --resolution 1920x1080 --layout mosaic`

- 出力フォーマット
  - 旧: （標準出力/ログ）  
    → 現行: `--format json` または text（`--format`）

- 2画面／左右指定
  - 旧: `--two-screen` / `--left`/`--right` オプション（Config 経由含む）  
    → 現行: `--two-screen/--no-two-screen`（`optimize`）、`apply` の `--left-file`/`--right-file`、および `--auto-split`

- 自動分割／適用
  - 旧: Core が内部で分割・適用を実行  
    → 現行: `split_composite_for_displays()` + `apply --auto-split` フロー（明示的に分離）

- 設定ファイル
  - 旧: `.walloptrc`（`Config.py`）を読み込む  
    → 現行: 自動探索読込は非採用。`--config` 明示指定で設定を読み込む。

- デーモン／Applet（常駐）
  - 旧: `Starter` / `Applet` / `AppIndicator` による常駐モード  
    → 現行: 未実装（今回の優先度は低）。別プロセス/サービス化で段階的に検討。

- 監視・切替（ChangerDir）
  - 旧: 指定ディレクトリからランダム／順次で壁紙を切替する長時間実行モード  
    → 現行: 未実装。将来的に `harite watch` のようなサブコマンドで実装可能。

- 細かなオプション（align/valign 等）
  - 旧: optparse で多数の細かい配置オプションを提供  
    → 現行: 一部は core の API で賄えるが、CLI 名称での 1:1 対応は乏しい。

- fixed 指定
  - 旧: fixed 相当の入力順固定運用（左右割り当て）  
    → 現行: `fixed` は廃止。2画面時の左右順は常に入力順に従う

優先復元項目（推奨順）

1. `ChangerDir` 相当（ランダム/順次列挙） — `harite watch` サブコマンドで限定的に実装。  
2. 旧 CLI の代表的細オプション（`align`/`valign`） — 需要が高ければ `optimize` に追加。  
3. デーモン/Applet（低優先） — GUI/常駐の要件が出た段階で設計。

完了済み項目（2026-04-11時点）

- `--config` 優先順位（CLI > config > default）を実装・テスト固定済み。
- `--two-screen` の config 連携を実装・テスト固定済み。
- `--no-two-screen` を導入し、CLI から明示 false 指定を可能化。
- `fixed` は撤去し、2画面時の左右順は入力順へ一本化した。
- `optimize --input` は file-only に制限し、directory 指定は受け付けない実装へ更新した。
- `--two-screen` + `--l-display` + `--r-display` + `--margins` の組み合わせケースを CLI テストで固定済み。

移植手順（短期）

1. `docs/specs/cli-compatibility.md` をレビュー・承認（済）。  
2. `tests/compat/` に旧 CLI の代表コマンドライン事例を YAML/JSON で追加（期待出力を記述）。  
3. `ChangerDir` 軽量実装を `src/harite/watch.py`（`harite watch`）として追加し、単体テストを用意。  
4. 必要に応じて既存 `core` API を拡張して `align` 等を透過的にサポート。

検証

- 各移植ステップごとに unit test を追加し、CI が通ること。  
- `tests/compat/` の代表ケースがローカルで再現できること。

次のアクション

- `.walloptrc` 自動探索読込は現時点で非採用を維持し、`--config` 明示指定運用を継続する。
- 次の実装候補は `harite watch`（`ChangerDir` 相当）の最小導入。

作成日: 2026-03-17
作成者: 作業エージェント

補足: 上位5オプションの確定仕様は `docs/specs/cli-top5-priority-options.md` を参照。

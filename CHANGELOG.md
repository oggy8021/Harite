# CHANGELOG

## Unreleased

- なし

## 2.0.0 (2026-06-13)

**メジャー版。** CLI v2・Qt 一本化・canvas-scale 意味論の確定。`v1.9.0` 熟成運転からの製品線再定義。

### Breaking — CLI `optimize`

- **`--resolution` / `-r` を削除。** 作業解像度はワークスペース検出と入力枚数から自動決定。出力 JPEG の縮小は **`--canvas-scale`（1–100、既定 100）** のみ。配置は常に 100% 幾何で計算し、縮小は保存ファイルのサイズ目的に限定。
- **`--two-screen` / `--no-two-screen` を削除。** 2 枚入力時は検出成功でデュアル、失敗時はエラー（半分ずつフォールバック廃止）。`--l-display` / `--r-display` も public surface から削除。
- **`--scaling` を削除。** fit 系は内部計算のみ。
- **`--embed-info=none` を削除。** 埋め込みなしはオプション省略。`none` 指定時はエラー。
- **`--embed-info=params` を `--embed-info=settings` に改名。** 互換 alias なし（旧値指定時はエラーメッセージで案内）。
- **margins / align の説明を仕様に合わせて整理。** margins は fit 制約のみ。align / valign は display スロット全面で効く。

### Breaking — CLI `apply`

- **`--plugin` を削除。** プラグインは `--settings-file` / `-c` の `plugin` キーまたは OS 既定。
- **`--apply-mode` / `--windows-apply-span` 等の apply 専用 CLI フラグを削除。** `apply_mode` / `windows_apply_span` は settings JSON 経由。
- 直前の `optimize` 実行を `.harite-last-optimize.json` で追跡。`--file` 省略時はそこから合成画像パスを解決。

### Changed — GUI / 配布

- **Qt 6 を唯一の GUI runtime。** `harite-gui` / `harite-qt` はいずれも `app_qt` を起動。GTK バックエンド・`harite-gtk` バイナリは提供しない。
- **システムトレイ:** Windows はライト/ダーク表面検出、Linux/XFCE はラスター pixmap + 明ストローク既定アイコン（`HARITE_TRAY_LIGHT_SURFACE=1` で上書き可）。
- **embed-info:** 重畳ガード、文字色自動、`canvas=` / `L=` / `R=` 行、GUI プレビュー同期。
- **仕様正本（`docs/specs/`）から開発チケット番号（MAT-xx）を除去。** 挙動・廃止事項は仕様本文に維持。

### Added

- `scripts/rinji.py` — XFCE / Qt トレイ診断。
- `requirements-linux-qt.txt`、`scripts/verify_linux_qt_env.py` — Linux Qt 環境再現。
- Windows 向け PyInstaller `onedir` ビルド手順（`packaging/windows/`）。

### Fixed

- canvas-scale がメモリ上のキャンバスまで縮小していた問題を修正（ポストダウンスケールのみ）。
- XFCE パネルでトレイアイコンが表示されない問題（SVG→pixmap、ステータストレイ前提）。

## 1.9.0 (2026-06-09)

開発マイルストーン。**PyPI / GitHub Release は公開しない**（`v1.0.0` 期間の区切りとタグ付けのみ）。

### Changed

- Qt 6 GUI を主 runtime とし、post-`1.0.0` inventory（C-xx / P-xx 一次波）を完了。
- feature overview を第2期 inventory（`20260609`）へ分割。熟成運転期間を開始。

### Fixed

- GTK: options drawer 開閉、Slideshow tab レイアウト、srcdir path 省略（#439）。

## 1.0.0 (2026-05-25)

### Added

- GTK ベースの GUI を通常利用向けの構成として整備。
- GUI で利用する icon 資産を追加。
- `harite-gui` を GUI の起動導線として提供。

### Changed

- Main / Margins / Slideshow tab の構成を見直し、GUI の視認性と操作導線を改善。
- Settings / Color / About dialog の役割を整理し、操作の意味づけを明確化。
- README、release note、配布物の説明を現行の利用形態に合わせて整理。

### Fixed

- GUI preview の画像・ファイルパス判定のずれを修正。
- Slideshow tab の layout ずれを抑制。
- 一時的な display 検出崩れに対する watch の安定性を改善。

## 0.1.3 (2026-05-16)

### Added (0.1.3)

- GTK ベースの GUI を通常利用向けの構成として整備。
- GUI で利用する Lucide icon 資産を追加。

### Changed (0.1.3)

- Main / Margins / Slideshow tab の構成を見直し、GUI の視認性と操作導線を改善。
- Settings / Color / About dialog の役割を整理し、操作の意味づけを明確化。
- header command bar を icon ベースに整理。

### Fixed (0.1.3)

- GUI preview の画像・ファイルパス判定のずれを修正。
- Slideshow tab の layout ずれを抑制。

## 0.1.2 (2026-04-12)

### Added (0.1.2)

- `--embed-font`（任意）を追加。余白埋め込みテキスト描画でフォントを明示指定可能。
- `LICENSE`（MIT）を追加。

### Changed (0.1.2)

- `embed-text` 描画時のフォント選択を改善。
  - 既定では CJK を含むシステムフォント候補を自動探索。
  - 候補未検出時のみ Pillow デフォルトフォントへフォールバック。

### Fixed (0.1.2)

- 日本語文字列を `--embed-text` で指定した場合に文字化けしやすい問題を改善。

## 0.1.1 (2026-03-21)

### Added (0.1.1)

- 余白情報埋め込み（MVP）を追加。
  - `--embed-info` (`none|params|free|combo`)
  - `--embed-text`, `--embed-position`, `--embed-max-lines`
- `harite apply` コマンドを追加（プラグイン経由で壁紙適用）。
- `harite slideshow` コマンドを追加（ディレクトリからのローテーション適用）。
- Windows 向け PowerShell プラグイン（レジストリ Span 設定）のスタブを整備。

### Changed (0.1.1)

- CLI の設定ファイル読み込みと option 優先順位を整理。
- 複数入力画像のパス正規化（カンマ区切り / 繰り返し `--input`）を統一。

### Fixed (0.1.1)

- 一部環境でのディスプレイ検出・配置計算の端数処理を改善。

## 0.1.0 (2026-03-20)

### Added (0.1.0)

- Harite 初回リリース（wallpaperoptimizer からのリファクタリング）。
- `harite optimize` CLI（マルチディスプレイ壁紙合成）。
- コア配置ロジック、プラグインレジストリ、設定ファイル基盤。

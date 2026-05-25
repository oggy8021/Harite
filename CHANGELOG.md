# CHANGELOG

## Unreleased

- なし

## 1.0.0 (2026-05-25)

### Added

- GTK ベースの GUI を通常利用向けの構成として整備。
- GUI で利用する icon 資産を追加。
- `harite-gui` を GUI の起動導線として提供。

### Changed

- Main / Margins / Watch tab の構成を見直し、GUI の視認性と操作導線を改善。
- Settings / Color / About dialog の役割を整理し、操作の意味づけを明確化。
- README、release note、配布物の説明を現行の利用形態に合わせて整理。

### Fixed

- GUI preview の画像・ファイルパス判定のずれを修正。
- Watch tab の layout ずれを抑制。
- 一時的な display 検出崩れに対する watch の安定性を改善。

## 0.1.3 (2026-05-16)

### Added (0.1.3)

- GTK ベースの GUI を通常利用向けの構成として整備。
- GUI で利用する Lucide icon 資産を追加。

### Changed (0.1.3)

- Main / Margins / Watch tab の構成を見直し、GUI の視認性と操作導線を改善。
- Settings / Color / About dialog の役割を整理し、操作の意味づけを明確化。
- header command bar を icon ベースに整理。

### Fixed (0.1.3)

- GUI preview の画像・ファイルパス判定のずれを修正。
- Watch tab の layout ずれを抑制。

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
- スタンドアロン GUI のブートストラップを追加。
  - `harite-gui` エントリポイント
  - GUI 骨格 (`src/harite/gui/*`)
  - 旧 glade 資産の取り込みと signal 対応表

### Changed (0.1.1)

- auto-split の分割クロップを仮想デスクトップ比率ベースへ改善。
- `optimize --help` と仕様書を実運用フィードバックに合わせて更新。

### Fixed (0.1.1)

- 低解像度合成画像でも左右分割が破綻しにくいように補正。
- 余白不足時の情報埋め込みは安全にスキップするように改善。

## 0.1.0 (2026-03-20)

### Added (0.1.0)

- Linux/XFCE の適用安定化と monitor-split 系機能を導入。
- `apply` の `--per-monitor`, `--left-file`, `--right-file`, `--auto-split` を導入。

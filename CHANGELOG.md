# CHANGELOG

## Unreleased

- なし

## 0.1.1 (2026-03-21)

### Added

- 余白情報埋め込み（MVP）を追加。
  - `--embed-info` (`none|params|free|combo`)
  - `--embed-text`, `--embed-position`, `--embed-max-lines`
- スタンドアロン GUI のブートストラップを追加。
  - `harite-gui` エントリポイント
  - GUI 骨格 (`src/harite/gui/*`)
  - 旧 glade 資産の取り込みと signal 対応表

### Changed

- auto-split の分割クロップを仮想デスクトップ比率ベースへ改善。
- `optimize --help` と仕様書を実運用フィードバックに合わせて更新。

### Fixed

- 低解像度合成画像でも左右分割が破綻しにくいように補正。
- 余白不足時の情報埋め込みは安全にスキップするように改善。

### Tests

- 分割合成（比率マッピング）回帰テストを追加。
- 埋め込みオプションのバリデーションと描画テストを追加。

## 0.1.0 (2026-03-20)

### Added

- Linux/XFCE の適用安定化と monitor-split 系機能を導入。
- `apply` の `--per-monitor`, `--left-file`, `--right-file`, `--auto-split` を導入。
- CI（lint/test/build）とリリース運用ドキュメントを整備。

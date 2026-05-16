# CHANGELOG

## Unreleased

- なし

## 0.1.3 (2026-05-16)

### Added (0.1.3)

- GTK ベース current GUI の visual operation view、header icon、settings/dialog semantics に関する実装と設計資産を追加。
- Lucide 系 icon 資産と、それを current GUI へ適用するための runtime 側基盤を追加。
- Phase10 close 判断と、Phase11 の tray / indicator 常駐導線に関する初手 planning 文書を追加。

### Changed (0.1.3)

- GTK runtime backend の責務を、layout builder、tab builder、dialog builder、signal wiring、object registry などへ分割し、追跡しやすい構成へ整理。
- Main / Margins / Watch tab の layout を契約駆動で再構成し、XFCE 上の current GUI を前提に視認性と操作導線を改善。
- Settings / Color / About 周辺の dialog semantics を整理し、`OK=Apply` と `Save=永続化` の役割分担を current GUI 側へ明確化。
- header command bar を icon ベースに再構成し、Help 導線を削除した上で Color / Settings / About の現行構成へ整理。
- Phase10 close と Phase11 planning の関係を docs 上で整理し、XFCE first target、`AyatanaAppIndicator3` / `AppIndicator3` runtime detection、watch state 追随、settings JSON 永続化反映の方針を明文化。

### Fixed (0.1.3)

- preview widget と fake GTK runtime の期待差分を調整し、GUI runtime test の image/file path 判定ずれを修正。
- watch tab の spacer / row 構成と parent container の責務を見直し、tab ごとの layout drift を抑制。
- docs 自動置換の未適用分を反映し、docs diff size check CI に再度通る状態へ整理。

### Tests (0.1.3)

- GTK runtime backend、signal dispatch、main window signal、visual regression 周辺の GUI テストを current GUI 構成に合わせて更新。
- Phase10 / Phase11 の文書整理に合わせ、GUI planning と close 判断の参照関係を点検可能な状態へ更新。

## 0.1.2 (2026-04-12)

### Added (0.1.2)

- `--embed-font`（任意）を追加。余白埋め込みテキスト描画でフォントを明示指定可能。
- `LICENSE`（MIT）を追加。

### Changed (0.1.2)

- `embed-text` 描画時のフォント選択を改善。
  - 既定では CJK を含むシステムフォント候補を自動探索。
  - 候補未検出時のみ Pillow デフォルトフォントへフォールバック。
- README に日本語テキスト埋め込みの利用例とフォント挙動を追記。

### Fixed (0.1.2)

- 日本語文字列を `--embed-text` で指定した場合に文字化けしやすい問題を改善。

### Tests (0.1.2)

- `--embed-font` の CLI 受け渡しテストを追加。
- 明示フォントパス優先ロードのコアテストを追加。
- `watch` CLI の既存回帰観点（`--help` / dry-run 既定 / `--do-it` 動作）を再確認。

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

### Tests (0.1.1)

- 分割合成（比率マッピング）回帰テストを追加。
- 埋め込みオプションのバリデーションと描画テストを追加。

## 0.1.0 (2026-03-20)

### Added (0.1.0)

- Linux/XFCE の適用安定化と monitor-split 系機能を導入。
- `apply` の `--per-monitor`, `--left-file`, `--right-file`, `--auto-split` を導入。
- CI（lint/test/build）とリリース運用ドキュメントを整備。

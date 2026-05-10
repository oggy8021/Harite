# Phase8 Margin Text Placement Note

最終更新: 2026-05-10

## 目的

- Phase8 の `margin text` 配置について、現行の visible requirement と既存実装を短く固定する。
- `phase8-margin-text-display-target` を独立ブランチとして継続すべきかどうかの判断根拠を残す。

## 現行の仕様判断

- visible requirement は、[docs/specs/gui/gui-phase8-margin-tab-grid-re-layout-contract.md](docs/specs/gui/gui-phase8-margin-tab-grid-re-layout-contract.md) の `Position:` で既に表現されている。
- 同 contract では、`Left: Top/Bottom` と `Right: Top/Bottom` の 4 候補から 1 つを選ぶ。
- これは user-facing には「margin text を左右どちらの display に出すか」を既に含んでいる。
- したがって、Phase8 で追加の visible control や別 state を導入しなくても、margin text の配置場所は合理的に指定済みと扱える。

## 現行実装の整理

- GUI runtime の選択 UI は 4 象限 radio のままとする。
- object 名は `radMarginTextPositionLeftTop`, `radMarginTextPositionLeftBottom`, `radMarginTextPositionRightTop`, `radMarginTextPositionRightBottom` を使う。
- GUI state と config/CLI/core の橋渡しは、単一の `embed_position` 値で行う。
- `embed_position` の現行対応は次の 4 値である。
  - `top` = left top
  - `left` = left bottom
  - `right` = right top
  - `bottom` = right bottom
- visible label 化は [src/harite/core.py](src/harite/core.py#L13) と [src/harite/core.py](src/harite/core.py#L163) の対応表を正本とする。
- margin 領域の解決は [src/harite/core.py](src/harite/core.py#L169) の `resolve_embed_margin_region()` に従う。
- MainWindow 側は `embed_position` をそのまま保持し、preflight/status 表示でも同 4 値を前提に扱う。実装の起点は [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py#L321) と [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py#L648) である。
- GTK backend 側も同じ 4 値を radio selection に直結している。実装の起点は [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py#L1900) と [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py#L2640) である。

## これを合理的とみなす理由

- user は `Left/Right` と `Top/Bottom` の組で配置先を選べる。
- margin 数値 4 項目との一体感を崩さず、`Margins` tab の visible complexity を増やさない。
- 既存の `embed_position` をそのまま使うため、GUI, prefs, CLI preview, core の境界を広く触らずに済む。
- branch 6 のレイアウト contract と実装が一致しており、別 branch で追加 UI を起こす必要が薄い。

## 非対象

- `embed_position` を `display target + vertical position` へ内部的に分離すること。
- config schema や CLI option を再設計すること。
- `Margins` の意味論を display-local へ変更すること。

## branch 7 の扱い

- `phase8-margin-text-display-target` は、visible requirement の不足を埋める branch としては再開しない。
- 将来もし branch 7 を再起動するなら、理由は visible requirement ではなく、内部 state 分離や schema 再設計の必要性として明示する。

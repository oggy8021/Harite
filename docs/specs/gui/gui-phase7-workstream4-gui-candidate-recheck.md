# GUI Phase 7 Workstream 4: GUI 候補機能の再読

最終更新: 2026-04-20

## 位置づけ

- 本書は Phase7 product alignment における Workstream 4 の詳細メモである。
- 目的は、main 画面、settings、CLI 専用機能、Phase8 候補の境界を docs-first で整理することにある。
- index は [docs/specs/gui/gui-phase7-product-alignment-planning.md](docs/specs/gui/gui-phase7-product-alignment-planning.md) を参照する。

## Workstream 4 の比較観点

- current GUI 上の入口は何か。
- current GUI での責務は何か。
- 母体プログラムでは何が相当機能だったか、または相当機能が存在しなかったか。
- `Harite v0.1.2` ではどう露出していたか。
- current 実装やこれまでの改修で、何が揃い、何が意図差として残ったか。
- 実機確認や過去の不具合修正から見えている制約は何か。
- Phase7 の判断として、main に残す / settings へ寄せる / CLI 専用のまま残す / Phase8 候補へ送る / 落とす、のどれに置くか。

## `Prefs` と main/settings 境界

- current `Prefs` は optimize・apply・watch の一部既定値を保存し、dialog から apply / load / save できる入口として成立している。
- `Prefs` に入っていない代表値:
  - current input path L/R
  - `output_dir`
  - `save_path`
  - watch source dir L/R
  - watch current 表示や watch 実行状態
- `Prefs` は「何でも入る箱」ではなく、「既定値」と「今この作業だけの状態」を分ける入口として読む。
- settings dialog に寄せるもの:
  - optimize の既定値
  - plugin / apply mode の既定値
  - watch interval の既定値
  - 将来的な `output_dir` 既定値候補
- main 画面に残すもの:
  - input path L/R
  - watch source dir L/R
  - watch start / stop と current 状態表示
  - save 実行直前の保存先選択
  - `Apply` / `Optimize` の即時操作
- watch interval は、`Prefs` 上の既定値と watch tab 上の runtime override の二重性を許す。

## `embed-text` / margin info embedding

- core / CLI ではすでに正本機能として成立している。
- GUI では state と `Prefs` 保存対象には入っているが、main 画面の主導線 widget にはなっていない。
- core spec の基本方針は「余白のみ」「デフォルト無効」「可読性優先」「壊れにくさ優先」である。
- `params` / `free` / `combo` は、装飾機能というより、生成物へ最小限の付加情報を残す機能として読む。
- Phase7 の暫定判断:
  - main 主導線へ今すぐ昇格させず、Phase8 候補として扱う。
  - ただし current state / prefs までは接続済みであることを明文化しておく。
  - main 画面に常設 controls を増やすより、将来の制作支援機能群としてまとめて再設計する。

## preview / visual assist

- current GUI には `CLI preview` 文字列はある。
- `last_saved_files` によって optimize 結果ファイル群は保持され、apply 対象候補として再利用できる。
- しかし専用の preview pane / preview window / preview service は current 実装には見当たらない。
- current GUI が持っているのは「CLI preview 文字列」と「生成後ファイルの保持」であり、「生成前後の見た目確認」はまだ弱い。
- Phase5 系 docs でも中央プレビューは現状無しと整理済みで、preview は後続タスクとして扱われていた。
- Phase7 の暫定判断:
  - Phase7 主導線へ無理に入れず、Phase8 候補として扱う。
  - 単なる wishlist にせず、preview 不在がどの判断に影響しているかを比較可能な形で残す。

## `Color` など deferred 項目

- `MainWindow.on_set_color()` は `color picker is deferred to phase7` を status に出すだけのプレースホルダである。
- GUI test も、その deferred status を確認している。
- GTK runtime backend 側でも `Color` ボタン押下は `Color: deferred` 表示へ落ちるだけで、実処理には接続されていない。
- core / CLI 側にも GUI の color picker に対応する正本機能は見当たらない。
- Phase6 の整理どおり、`Color` は main 主導線へ戻さない。
- Phase7 では、`Color` を理由に main 画面構成や controls grouping を揺らさない。

## GUI 候補機能リスト（初版）

- Phase7 の main 主導線に残すもの:
  - `Optimize`
  - `Apply`
  - `Auto-split` を含む apply mode の整理
  - watch front-end
  - 入力 path / save path / current output のような作業中 state
- settings dialog (`Prefs`) に寄せるもの:
  - optimize 既定値
  - plugin / apply mode 既定値
  - watch interval 既定値
  - 将来的な `output_dir` 既定値候補
- GUI に残すが主導線へは上げないもの:
  - embed 系の既定値保持
  - `CLI preview` 文字列による最低限の可視化
- CLI 専用のまま残すもの:
  - explicit mapping (`--left-file` / `--right-file`)
  - 実画面解像度と意図的にずらした素材生成を前提にした expert workflow
- Phase8 候補として送るもの:
  - `embed-text` / margin info embedding の GUI 制作支援化
  - visual preview / assist
  - `Color` の再定義または close

## feature group ごとの暫定分類

| feature group | 現時点の置き場 | 理由 |
| --- | --- | --- |
| main workflow (`Optimize` / `Apply` / watch) | Phase7 主導線 | current product の中心責務であり、すでに実接続または責務整理済み |
| settings / defaults (`Prefs`) | Phase7 再整理対象 | current 実装はあるが、main との境界整理が必要 |
| apply wording / helper text | Phase7 再整理対象 | semantics は固まりつつあり、visible 語彙の整理が残る |
| embed / margin info | Phase8 候補 | core / CLI では成立済みだが、GUI 主導線での見せ方は未設計 |
| visual preview / assist | Phase8 候補 | CLI preview はあるが、専用の visual 基盤は未成熟 |
| `Color` / deferred legacy items | Phase8 候補または削除候補 | legacy 痕跡はあるが、正本機能としては未成立 |
| explicit per-monitor mapping | CLI 専用 | Harite の主導線ではなく、低露出 escape hatch として扱う |

## Phase8 候補バックログ素案

### P8-A. 制作支援の最小セット

- 目的:
  - current GUI の「作れるが見えにくい」を改善する。
- 候補:
  - optimize 結果の生成後 preview
  - embed 系結果の見え方確認
  - two-screen 合成結果の確認
- 優先理由:
  - current Phase7 で最も不足が明確で、embed 系を主導線へ上げるかどうかの判断材料にも直結する。

### P8-B. preview / visual assist の拡張

- 目的:
  - 生成前後の見た目確認を GUI 内で閉じる。
- 候補:
  - 生成前 preview と生成後 preview の責務分離
  - 配置要約表示
  - 将来的な auto-split 結果確認
- 優先理由:
  - single-screen / two-screen / embed / auto-split の複数論点を横断して支える基盤になり得る。

### P8-C. embed 系の GUI 昇格再設計

- 目的:
  - `Prefs` 内の隠れ設定を、必要なら制作機能として再設計する。
- 候補:
  - 常設 controls ではなく advanced section / dialog への分離
  - `embed_info` mode の user 向け語彙再設計
  - 既定値と作業ごとの埋め込み内容の分離
- 優先理由:
  - current state / prefs 接続はあるため、設計が決まれば進めやすい。

### P8-D. deferred 項目の close 判断

- 目的:
  - legacy 痕跡だけで残っている項目を backlog として残すか閉じるかを決める。
- 候補:
  - `Color` の再定義
  - close するなら close 条件と文言の明文化
- 優先理由:
  - 未完 UI の印象だけを残さないため、Phase8 では「作る」だけでなく「閉じる」判断も必要である。

## Phase8 の優先順メモ

- 第1群:
  - P8-A 制作支援の最小セット
  - P8-B preview / visual assist の拡張
- 第2群:
  - P8-C embed 系の GUI 昇格再設計
- 第3群:
  - P8-D deferred 項目の close 判断

- 理由:
  - preview / assist が弱いまま embed 系や deferred 項目を先に動かすと、結果確認の弱さを抱えたまま controls だけ増えやすい。
  - 先に制作支援の土台を置いた方が、embed 系を上げるか据え置くか、`Color` を残すか閉じるかの判断もしやすい。
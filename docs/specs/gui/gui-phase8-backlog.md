# GUI Phase 8 バックログ素案

最終更新: 2026-04-21

## 位置づけ

- 本書は [docs/specs/gui/gui-phase8-planning.md](docs/specs/gui/gui-phase8-planning.md) の feature group を、実装前提の backlog 粒度へ落とすための初版である。
- ここでは詳細 UI mock や wording を確定せず、目的、入口、依存、除外事項を先に固定する。

## Group 1: preview / visual assist

### P8-1A. 最小 preview

- 目的:
  - optimize 実行後の生成結果を GUI 内で確認できるようにする。
- 最小スコープ:
  - 生成済み結果ファイルの縮小表示のみ
  - 直近 optimize 結果の表示
  - 保存済み結果との対応が分かる最低限の表示
- 先に決めること:
  - MainWindow 内に、左右ディスプレイ相当の 2 面縮小表示を置く
  - watch は対象外とし、optimize / apply 主導線の補助として扱う
  - `single-file` では同一画像が左右ディスプレイへ出ることを事前に伝える
  - `Auto-split` では分割後の見え方を疑似表示の対象に含める
  - preview サイズは Window 全体比ではなく、preview 親領域の割当幅に対する比率で決める
  - preview は起動直後は空、optimize 成功で初期化、apply mode 切替で再描画、input clear で破棄、optimize failure 時は前回成功 preview を維持する
- 除外:
  - 生成前 preview
  - `Color` や embed controls との同時実装

### P8-1B. visual assist の拡張

- 目的:
  - preview を単なる画像表示で終わらせず、配置理解の補助まで広げる。
- 候補:
  - 第1段: 配置要約表示
  - 第2段: 左右割当の見える化
  - 第3段: auto-split 結果確認
- 第1段の最小実装:
  - preview 直下に配置要約ラベルを 1 本置き、`single-file` は同一画像を左右へ適用すること、`Auto-split` は左右表示幅に沿って分割適用することを文で補足する
- 第2段の最小実装:
  - 左右 preview pane ごとに割当ラベルを置き、どの入力画像が L / R display に対応するかを basename 単位で見えるようにする
- 第3段の最小実装:
  - 左右 preview pane ごとに result note を置き、`single-file` では full optimized image、`Auto-split` では left crop / right crop を明示して pseudo split preview を結果確認として読めるようにする
- 依存:
  - P8-1A が先

## Group 2: embed 系 GUI 昇格

### P8-2A. MainWindow 入口の再配置

- 目的:
  - `embed-text` / margin info を `Prefs` 既定値保持だけで終わらせず、MainWindow の制作機能として扱う。
- 最小スコープ:
  - MainWindow の watch より手前の tab として embed 系入口を置く
  - `embed_info` の visible 語彙を user 向けに整理する
- P8-2A の最小実装:
  - watch より手前に `Embed` tab を追加し、`embed_info` は `Off / Params / Text / Both` の visible 語彙で切り替えられるようにする
  - `embed_text` / `embed_position` / `embed_max_lines` は MainWindow から直接更新できる入口までを用意する
- `Params` 表示内容の整理メモ:
  - 合成後画像上では `Params` という見出しは置かず、内容だけを直接出す方針とする
  - `resolution` は `res` へ省略せず、そのまま `resolution` と明記する
  - `margins` は短縮形を採用し、`L,R,U,B` ベースで出す
  - `align` は現状 wording を維持する
  - `pad` は意味が伝わりにくいため、`Params` 表示には含めない
  - `inputs` も `Params` 表示には含めない
  - `two-screen=1` のような flag 的露出は避け、split の有無はラベルなしで `Auto-Split` / `No Split` として見せる
  - `Max lines` の初期値は固定せず、上記 wording を並べた案と `position` の整理後に再評価する
- `Position` 整理メモ:
  - user が選べる候補は current implementation に合わせて `Top margin` / `Bottom margin` / `Left margin` / `Right margin` の 4 つに絞る
  - `auto` は P8-2A で廃止し、初期値は `Bottom margin` とする
  - `Left display` / `Right display` / `Both displays` は今回の scope に入れない
  - 画像本体との重畳は行わず、margin 領域のみを配置対象とする
  - embed tab では preflight 判定を行い、選択された margin 領域が current resolution / margins で不足する場合は `Status` / `Error` に出す
- 実機確認メモ:
  - margin がないと embed は当然ほぼ確認できず、単独機能として誤読されやすい
  - `position=auto` は実機では左上に置かれた。CLI 側が暫定実装だった前提も含め、意味付けの再確認が要る
  - `Position` は `auto` 以外に何が書けるかが user から分かりにくく、CLI literal をそのまま出すより「マージンのどの領域に置くか」という user-facing な言い方へ整理する議論が要る
  - 1 行程度の text は taskbar との干渉で視認性を失う場合がある
  - `Params` は何の parameter か直感しづらく、実機確認では「こちらの設定組み合わせ」を出す意味だと再把握した。user-facing wording としては再検討が要る
  - `Text` が 1 行入力のため、`Max lines` の意味付けは現状まだ弱い。初期値はおおよそ 5-6 行を目標に再評価する
  - tab 内の `Embed: ...` state 表示は Main tab に戻ると見えず価値が薄いため、P8-2A では置かない方針にした
- 前提:
  - current state / prefs 接続までは既にある
- 割り込み条件:
  - P8-2B へ進む前に、`margins` / `two_screen` / `align` / `valign` / `fixed` / `apply_mode` の precedence audit を 1 度挟む
  - 特に母体の screen-bound な幾何拘束と、Harite 現行の global outer margins 主導の意味論差を確認してから wording 強化や max-lines 再設計へ進む
- 依存:
  - preview 方針の固定後に扱う

### P8-2B. 作業単位編集と既定値の分離

- 目的:
  - embed 系を「保存される既定値」と「今回だけの編集値」に分ける。
- 再設計前提:
  - `Embed` という名称はやめ、tab 全体は `Margins` として扱う。
  - tab 内は少なくとも `Margins` と `Margin text` の 2 段に分ける。
  - 既存の margin 数値 4 項目は Main 側から `Margins` tab へ移し、margin 関連を一箇所で扱う。
  - margin 値は 4 つ 1 組で入力させ、左右で同じ margin として扱う前提を維持する。
  - ただしこの整理は「current 実装の global outer margins を肯定する」意味ではなく、母体差を抱えたまま margin 関連 UI を分散させないための再配置である。
  - `embed info` という名称はやめ、CLI/GUI ともに `Margin text` 系の語彙へ寄せる。
  - `Text` 入力は 1 行 entry ではなく 5 行 textbox 風の multiline control へ広げる。
  - `max lines` は user-facing control としては廃止する。
  - 行数上限は mode ごとの内部ルールで扱う。
  - `Params` 相当: 自然に決まる行数
  - `Text` 相当: 最大 5 行
  - `Both` 相当: 最大 8 行
  - 将来的には margin text の出力先 display を左右どちらかへ限定指定する余地を残す。
- 候補:
  - `embed_text` 「今回だけの編集値」
  - `embed_position` 「保存される既定値」
  - `embed_max_lines` 「保存される既定値」
- layout 正本: [docs/specs/gui/gui-phase8-margin-tab-grid-re-layout-contract.md](docs/specs/gui/gui-phase8-margin-tab-grid-re-layout-contract.md)

## Group 3: `Color` / deferred legacy

### P8-3A. `Color` の再定義

- 目的:
  - 背景色を user selectable な機能として GUI に実装する。
- 2026-05-10 補記:
  - `Color` は command bar の visible control として復帰し、background color の選択値が optimize state / settings JSON / CLI preview に浸透する形まで実装済み。
- 先に決めること:
  - `Color` はその場限りの即時指定ではなく、watch と同様に設定値として浸透させ、JSON に保存する
  - 置き場の第一案は `Color` `Prefs` `About` の並びとする
- 依存:
  - `Prefs` と並ぶ補助 control として扱うため、preview 方針とは切り分けて進められる

### P8-3B. `About` 実装と deferred 整理

- 目的:
  - `About` は軽量な情報ダイアログとして実装し、その他の legacy 痕跡は backlog に残すか close するかを決める。
- 対象候補:
  - `About` はアプリ名、アイコン、版数、短い説明、クレジット、ライセンス導線を持つ軽量ダイアログとして扱う
  - 構成は標準的な About ダイアログを参照してよいが、固有アイコンや文言を複製せず Harite 用に組み直す
  - `Help` はいったん Phase8 対象から外し、別系統の未完項目として将来あらためて判断する

## 初期優先順

1. P8-1A 最小 preview
2. P8-1B visual assist の拡張
3. P8-2A MainWindow 入口の再配置
4. P8-2B 作業単位編集と既定値の分離
5. P8-3A `Color` の再定義
6. P8-3B `About` 実装と deferred 整理

## PR 区切りのたたき台

- PR1: Phase8 docs と preview 最小要件の固定
- PR2: preview 入口と visual assist 最小セット
- PR3: embed 系 GUI 昇格の最小設計
- PR4: `Color` / `About` と deferred の扱い判断

## 修復計画への導線

- precedence audit 後の実装修復順は [docs/specs/gui/gui-phase8-repair-plan.md](docs/specs/gui/gui-phase8-repair-plan.md) を正本として扱う。
- 特に `fixed`、optimize input、`padding` / `mosaic`、`Margins` / `Margin text` 再配置は backlog の自然順だけで入れ替えず、修復計画の順に従う。

# GUI Phase 8 修復計画

最終更新: 2026-04-23

## 位置づけ

- 本書は、Phase8 の precedence audit を受けて、実装修復をどの順で進めるかを固定するための計画書である。
- exploratory な追加要求を積む文書ではなく、意味論の負債をどの順で減らすかを整理する文書として扱う。
- 実装ブランチは、本書の単位で責務を分ける。

## 一次参照

- [docs/specs/gui/gui-phase8-precedence-audit-memo.md](docs/specs/gui/gui-phase8-precedence-audit-memo.md)
- [docs/specs/gui/gui-phase8-backlog.md](docs/specs/gui/gui-phase8-backlog.md)
- [docs/specs/core/optimize-input-and-two-screen.md](docs/specs/core/optimize-input-and-two-screen.md)
- current status overlay: [docs/specs/gui/gui-phase8-resume-planning-after-2weeks-break.md](docs/specs/gui/gui-phase8-resume-planning-after-2weeks-break.md)

## 修復の基本方針

- 先に意味論の負債を消し、その後に visible wording と GUI 配置を直す。
- `watch` は directory 主導の別責務なので、`optimize` の修復と混ぜない。
- `fixed`、directory input、`padding` / `mosaic` のような Harite 固有 convenience は、互いに関係があっても 1 PR に詰め込まない。
- `Margins` / `Margin text` の再設計は、core/CLI の意味論修復後に扱う。
- 将来の display-targeted margin text は追加機能として最後に分離する。
- 2026-05-09 時点の現在地判断は本書へ追記せず、overlay として [docs/specs/gui/gui-phase8-resume-planning-after-2weeks-break.md](docs/specs/gui/gui-phase8-resume-planning-after-2weeks-break.md) で管理する。

## 修復順

### 1. 修復順の固定

- ブランチ名案: `docs/phase8-repair-plan`
- 目的:
  - 修復対象の順番、各ブランチの責務、完了条件を docs として固定する。
- 完了条件:
  - Phase8 の修復順が 1 本の文書で読める。
  - 各ブランチが何を含み、何を含まないかが明記されている。

### 2. `fixed` の撤去

- ブランチ名案: `phase8-drop-fixed`
- 目的:
  - 母体との差が最も大きい `fixed` 残骸を CLI/core/GUI/prefs/tests から除去する。
- 対象:
  - CLI option
  - core の未使用パラメータ
  - preferences / json
  - GUI widget / signal
  - tests / docs
- 完了条件:
  - `fixed` / `no-fixed` が user-facing 入口から消えている。
  - 2 画面時の左右順は input 順で説明できる。

### 3. optimize input の拘束強化

- ブランチ名案: `phase8-optimize-input-files-only`
- 目的:
  - `harite optimize` の `--input` を画像ファイル限定へ修復する。
- 対象:
  - CLI help
  - core input parser
  - optimize tests
  - docs
- 非対象:
  - `watch` の directory input
- 完了条件:
  - optimize は directory を受け付けない。
  - watch は従来どおり directory を受け付ける。

### 4. `padding` / `mosaic` 系の整理

- ブランチ名案: `phase8-drop-padding-mosaic`
- 目的:
  - Harite 固有 convenience になっている通常分割系の余剰パラメータを縮退または撤去する。
- 対象:
  - `--padding`
  - `layout=mosaic`
  - 関連 docs / tests / prefs 残骸
- 完了条件:
  - 母体非準拠の tile convenience が整理されている。
  - `Params` / `Margin text` に内部語彙として残す値が縮小されている。

### 5. `Margins` 4 値の意味論修復

- ブランチ名案: `phase8-fix-margin-semantics`
- 目的:
  - Harite 独自の `global outer margins` 前提を縮退し、母体準拠の screen-bound margin semantics へ寄せる。
- 対象:
  - optimize 側の margin 解釈順
  - `Margins` 4 値がどの領域へ効くかの core 実装
  - CLI / docs / tests に残る `global outer margins` 前提の説明
  - 必要な場合の prefs 正規化と migration 方針
- 非対象:
  - `Margins` tab の再レイアウトや wording 再調整
  - margin text の display-target 追加
  - watch 系の別責務整理
- 完了条件:
  - `Margins` 4 値は左右 display 双方へ同じ値として効くと説明できる。
  - `global outer margins` を前提にした optimize 計算順または説明が主要経路から消えている。
  - 母体との差分が残る場合は、意図差分として docs に明記されている。

### 6. `Margins` / `Margin text` への再配置

- ブランチ名案: `phase8-gui-margins-tab`
- 目的:
  - `Embed` をやめ、GUI/CLI の visible wording を `Margins` / `Margin text` へ寄せる。
- 対象:
  - MainWindow の tab 名と section 名
  - margin 数値 4 項目の配置移動
  - 5 行 textbox
  - `max lines` の user-facing 廃止
  - CLI wording の追従
- 完了条件:
  - `Embed` という表示語が消えている。
  - margin 関連の入口が一箇所にまとまっている。

### 7. margin text の display 指定

- ブランチ名案: `phase8-margin-text-display-target`
- 目的:
  - margin text の出力先を display 単位で選べる余地を追加する。
- 前提:
  - 先行ブランチで `Margins` / `Margin text` の語彙と UI が安定していること。
- 完了条件:
  - 左右どちらへ出すかを user-facing に指定できる。
  - 最高位要求である margin 入力一体性を壊していない。

## PR の切り方

- 1 PR で複数段をまたがない。
- docs-only の修復順固定は、本書だけで閉じてよい。
- core/CLI 修復と GUI wording 修復は分離する。
- 追加機能は、意味論修復の後ろへ送る。

## 現時点の実行順

1. `docs/phase8-repair-plan`
2. `phase8-drop-fixed`
3. `phase8-optimize-input-files-only`
4. `phase8-drop-padding-mosaic`
5. `phase8-fix-margin-semantics`
6. `phase8-gui-margins-tab`
7. `phase8-margin-text-display-target`

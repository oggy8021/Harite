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
- 依存:
  - P8-1A が先

## Group 2: embed 系 GUI 昇格

### P8-2A. MainWindow 入口の再配置

- 目的:
  - `embed-text` / margin info を `Prefs` 既定値保持だけで終わらせず、MainWindow の制作機能として扱う。
- 最小スコープ:
  - MainWindow の第3タブとして embed 系入口を置く
  - `embed_info` の visible 語彙を user 向けに整理する
- 前提:
  - current state / prefs 接続までは既にある
- 依存:
  - preview 方針の固定後に扱う

### P8-2B. 作業単位編集と既定値の分離

- 目的:
  - embed 系を「保存される既定値」と「今回だけの編集値」に分ける。
- 候補:
  - `embed_text` 「今回だけの編集値」
  - `embed_position` 「保存される既定値」
  - `embed_max_lines` 「保存される既定値」

## Group 3: `Color` / deferred legacy

### P8-3A. `Color` の再定義

- 目的:
  - 背景色を user selectable な機能として GUI に実装する。
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

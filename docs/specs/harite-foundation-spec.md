# Harite 基本仕様 (Foundation Spec)

最終更新: 2026-06-01 (F-01 settings path 参照)

## 1. 文書の目的と適用範囲

- 本書は Harite の常設仕様書群の入口である。
- 主題は、現行 Harite が何を目的とし、どの環境で、どの操作面を持ち、どの分冊へ読むべきかを示すことにある。
- planning 履歴、過去判断の時系列、没案の説明は対象外とする。

本書の読み方:

- Harite 全体の位置づけ、対象利用者、運用前提を知りたい場合は本書を最初に読む。
- 各操作面の具体仕様を知りたい場合は、本書末尾の分冊導線から core / CLI / GUI / スライドショー へ進む。
- 実装変更時に参照する場合も、まず本書で責務境界を確認してから個別分冊へ降りる。

## 2. Harite の目的

- Harite は、壁紙画像の最適化と適用を、GUI と CLI の両面から扱うためのツールである。
- 主な責務は、入力画像の解決、表示条件に応じた最適化、OS / desktop plugin を通じた適用、継続運用としてのスライドショー機能にある。
- 特に GUI では、compose -> optimize -> apply の流れを日常操作として扱えることを重視する。

目的をもう少し具体化すると、Harite は次の 3 面を一続きの体験として扱う。

1. 入力画像と表示条件から、適切な壁紙出力を作る。
2. 作られた出力を、現在の OS / desktop 環境へ適用する。
3. 単発操作だけでなく、スライドショー機能により継続的な更新運用を行う。

そのため Harite は、単なる画像変換ツールでも、単なる壁紙 setter でもなく、最適化と適用の間をつなぐアプリケーションとして位置づけられる。

## 3. 想定利用者

- 日常的に壁紙最適化と適用を行う owner
- 将来の保守者
- 新しい仕様変更や実装変更の前提確認をしたい contributor

想定していない読み手:

- 画像処理アルゴリズムだけを独立利用したい利用者
- packaging / release 運用だけを知りたい利用者
- planning 履歴や過去議論の経緯を主目的に追いたい利用者

## 4. 対象環境と前提依存

- Python ベースのアプリケーションとして動作する。
- CLI は cross-platform を志向するが、plugin 実装により適用面は OS ごとに差分を持つ。
- GUI は GTK backend（`harite-gtk`）と Qt backend（`harite-qt`）の 2 系統を持つデュアルバックエンド構成を採る。
- Linux / XFCE では per-monitor apply, スライドショー, tray, desktop entry まわりの説明比重が高い。

環境前提の整理:

- 画像の最適化自体は OS 依存を最小化するが、実適用は plugin 実装に依存する。
- Windows plugin と macOS plugin は単一画像適用を基本とする。
- Linux plugin は desktop 環境ごとの差分を吸収しつつ、per-monitor apply と XFCE 系の説明比重が高い。
- GUI は GTK backend と Qt backend の 2 系統を持つ。GTK backend（`harite-gtk`）は Linux / XFCE 向けにネイティブ感を重視し、Qt backend（`harite-qt`）は Windows / クロスプラットフォーム向けの開発フォーカスとする。
- GTK backend は maintenance mode（バグ修正のみ）、Qt backend は development focus として扱う。
- headless 環境では CLI が主操作面になる。

## 5. 全体アーキテクチャ概要

Harite の主な面は以下の 6 つである。

1. 基本仕様 (foundation): 全体像と分冊導線
2. コア仕様 (core): 最適化、設定、適用条件の基底仕様
3. CLI 仕様 (CLI): command surface
4. GUI 仕様 (GUI): 画面、操作、状態、tray
5. スライドショー仕様: 継続実行、pause / retry、観測面
6. plugin 仕様 (plugin): OS / desktop 環境ごとの適用実行

この 6 面は、責務を分離するための文書分冊であって、実装が完全に独立していることを意味しない。実装上は core, plugin, GUI state, slideshow state が相互に接続しているため、本書は「どこからどこまでをどの分冊で説明するか」の境界線として機能する。

## 6. GUI / CLI / スライドショー / tray の関係

```mermaid
flowchart TD
    User[User] --> GUI[GUI surface]
    User --> CLI[CLI surface]
    GUI --> Core[core logic]
    CLI --> Core
    GUI --> Slideshow[GUI slideshow]
    CLI --> Slideshow[CLI slideshow]
    GUI --> Tray[task tray]
    Slideshow --> Plugin[OS plugin apply]
    Core --> Plugin
```

- GUI と CLI は別の操作面だが、基底挙動は core に寄せる。
  - スライドショー機能は CLI 専用ではなく、GUI 側にも長時間運用の責務を持つ。
- tray は GUI の補助操作面であり、スライドショーの開始停止と可視状態制御に関与する。

操作面ごとの基本役割:

- GUI は日常操作と状態可視化を担う。
- CLI は明示的な command 実行と再現性の高い呼び出しを担う。
- スライドショー機能は単発操作を継続運用へ拡張する。
- tray は GUI 常駐時の補助導線であり、独立した業務面ではない。

### 6.1 横断責務マトリクス

主要な境界を 1 つの表でまとめると次のとおりである。

| 論点 | 主責務 | 補助責務 / 呼び出し側 | 非主責務 |
| --- | --- | --- | --- |
| 入力検証 | CLI / GUI | core は受け取った値の基底正規化を行う（不正値に対して例外ではなくフォールバック値を返す場合がある。例: `background_color` 不正 → `#1E1E1E`、margins 変換失敗 → `(0,0,0,0)`） | plugin |
| optimize 条件解決 | core | CLI / GUI は入力採用値を決めて渡す | plugin |
| 設定ファイル path 解決と JSON 入出力 | settings_file | CLI / GUI は load/save の契機を持つ | plugin |
| apply target 解決 | core | CLI / GUI / slideshow は apply_mode と file 条件を渡す | plugin |
| plugin 名の選択 | CLI / GUI / 設定 | plugin registry は解決を補助する | core |
| plugin registry 解決 | plugins registry | CLI / GUI が名前を与える | core |
| target 種類の受理可否 | plugin 契約 | CLI / GUI は事前判定してよい | core |
| OS / desktop への実適用 | plugin | CLI / GUI / slideshow は結果を観測する | core |
| スライドショーの画像選択と cycle state | slideshow helper | GUI / CLI は実行面を被せる | plugin |
| GUI status / history / tab state 更新 | GUI views + adapters | plugin logger は補助観測面 | core |
| CLI 終了コードと実行メッセージ | CLI | plugin / core の失敗を分類して表示する | GUI |
| tray からの start/stop / 可視制御 | tray adapter | GUI state が業務状態を保持する | core / plugin |

この表は「実装がどの module にあるか」の一覧ではなく、「仕様上どの層が主語になるか」の一覧である。実装上は 1 回の操作で複数層が連続して呼ばれるが、どの判断をどこで説明するかはこの表を基準に分冊へ振り分ける。

## 7. 設定 (settings) / save / apply の責務分担

- 設定 (settings) は論理設定モデルとして保持され、物理保存は 設定ファイル (harite-settings.json) を使う。
- 既定 path の解決規則は [core-spec §6.1](core/harite-core-spec.md) が正本（Linux: XDG config 配下、Windows: `%APPDATA%\harite\`）。
- save は optimize 結果の出力先決定と書き出しを扱う。
- apply は最終適用対象を解決したうえで plugin へ委譲する。
- apply では、target 解決を core、plugin 名の選択と実行可否を呼び出し側 / plugin 側へ分けて扱う。
- GUI では、設定保存と画像保存を別 surface として扱う。settings dialog の `Save Settings` は設定ファイルを保存し、main window の `Export Image` は今回の optimize 結果画像の書き出し先を扱う。

責務を混同しないための整理:

- 設定は「次回以降も使いたい既定値や運用値」を保持する。
- save は「今回の optimize 結果をどこへ書くか」を扱う。
- apply は「生成済みまたは既存の画像を、環境へどう反映するか」を扱う。

この 3 面は GUI 上では近く見えるが、仕様上は別責務として扱う。

plugin 分冊:

- plugin 実装の正本は [docs/specs/plugins/harite-plugin-spec.md](docs/specs/plugins/harite-plugin-spec.md)

## 8. README と仕様書の役割分担

- README は導入、インストール、最小の使用導線を扱う。
- 仕様書は、現行挙動、責務分担、状態、失敗時挙動を扱う。
- README に長い仕様説明や履歴説明を戻さない。

README に残すもの:

- 何のツールか
- どうインストールするか
- どう最短で起動するか
- 主要 command の最小例

仕様書へ寄せるもの:

- 各操作面の責務
- 設定ファイルの意味
- スライドショーと apply の条件分岐
- GUI / CLI / plugin / tray の境界
- 失敗時挙動と観測面

## 9. ソースディレクトリ構成と責務境界

```text
src/harite/
  cli.py                  CLI entrypoint と command surface
  settings_file.py        設定ファイル (harite-settings.json) の path 解決と JSON load/save
  settings.py             設定モデルと JSON との相互変換
  core.py                 optimize の基底ロジック（配置計算・embed・auto-split）
  optimize_settings.py    display 設定の解決（入力値と two-screen context から optimize パラメータを確定）
  display_context.py      接続中 display 群の検出と two-screen context の生成
  apply_settings.py       apply 対象の解決
  slideshow.py            スライドショー実行の選択ループとサイクル state
  plugins.py              OS / desktop plugin registry と apply 実装
  linux_xdg_launcher.py   Linux/XDG launcher 生成
  gui/
    app.py                GTK backend entrypoint（harite-gtk）
    app_qt.py             Qt backend entrypoint（harite-qt）
    views/                framework-neutral な状態モデル
    controllers/          GUI から core への接続制御
    adapters/             GTK runtime, dialog, tray, signal wiring（maintenance mode）
    adapters_qt/          Qt runtime, dialog, tray, signal wiring（development focus）
    services/             GUI 補助サービス
    resources/            icon などの同梱リソース
```

### GUI 配下の詳細分類

```text
src/harite/gui/
  app.py
    GTK backend 起動入口（harite-gtk）。MainWindow 生成、GTK backend load、tasktray 初期化、window present を束ねる。
  app_qt.py
    Qt backend 起動入口（harite-qt）。MainWindow 生成、Qt backend load、window present を束ねる。
  views/
    main_window.py
      主状態モデル。framework-neutral。status, history, 設定, optimize/apply/slideshow の業務状態を持つ。
    main_window_preview.py
      preview 表示専用の補助計算を持つ。
  controllers/
    optimize_controller.py
      GUI form state を core.optimize 実行へ橋渡しする。
  services/
    cli_mapper.py
      GUI state を CLI 相当の引数列へ写像する。
  adapters/                         ← GTK backend（maintenance mode）
    gtk_backend.py
      GTK runtime 統合窓口。
    ui_adapter.py
      runtime signal と MainWindow method の対応表を持つ（両 backend 共用）。
    tasktray_adapter.py
      GTK tray / indicator の生成と menu action を持つ。
    gtk_layout_builders.py / gtk_tab_builders.py / gtk_dialog_builders.py
      widget 構築責務を分割する。
    gtk_runtime_* modules
      signal, sync, dialog, slideshow, helper などの細粒度 runtime 責務を持つ。
  adapters_qt/                      ← Qt backend（development focus）
    qt_backend.py
      Qt runtime 統合窓口。QApplication と QMainWindow の管理を担う。
    qt_layout_builders.py
      Qt レイアウト骨格（3 層 + タブ）の構築を担う。
    （以降のモジュールは Phase 3–9 で順次追加する）
```

### 9.1 GUI 内部層の配置規則

GUI 配下の file / module を読むときは、次の配置規則を前提にする。

- views は framework-neutral な owner state を持つ。widget instance, GTK 型, Qt 型, tray 実体, signal 名の知識は持ち込まない。
- controllers は GUI form state を core や helper 呼び出しへ橋渡しする。業務判断の本体を新設せず、views と core の間で値を整える役に留める。
- services は GUI から見た補助変換や補助計算を置く。runtime 固有物や user interaction の進行管理は持たない。
- `adapters/` は GTK runtime, dialog, tray, signal wiring など外界との接続面を持つ（GTK backend 専用）。
- `adapters_qt/` は Qt runtime, dialog, tray, signal wiring など外界との接続面を持つ（Qt backend 専用）。
- `adapters/ui_adapter.py` の `RUNTIME_HANDLER_MAP` は両 backend が共用する。handler 名と `MainWindow` メソッド名の対応表として機能し、runtime 固有の接続実装はそれぞれの adapters 側で行う。
- `app.py` / `app_qt.py` は起動順制御の入口であり、継続的な業務状態は持たない。
- 複数層にまたがる処理は、まず owner state がどこにあるかで置き場所を決める。状態の主語が GUI 業務状態なら views、GTK 実体なら `adapters/`、Qt 実体なら `adapters_qt/`、core 業務規則なら core を優先する。
- したがって「GUI から呼ばれるから controllers / adapters に置く」とは考えず、状態主語と runtime 依存の有無で切り分ける。

## 10. エントリーポイント一覧

| コマンド | モジュール | 役割 |
|---|---|---|
| `harite` | `harite.cli` | CLI entrypoint（optimize / apply / slideshow） |
| `harite-gtk` | `harite.gui.app` | GTK backend GUI（maintenance mode） |
| `harite-qt` | `harite.gui.app_qt` | Qt backend GUI（development focus） |

- `harite-gtk` は旧 `harite-gui` エントリーポイントの後継であり、GTK backend に対応する。
- `harite-qt` は Qt backend の新エントリーポイントであり、Qt migration の実装が完了した段階で `pyproject.toml` に追加する。

## 11. 分冊導線

- core 詳細は [docs/specs/core/harite-core-spec.md](docs/specs/core/harite-core-spec.md)
- CLI 詳細は [docs/specs/cli/harite-cli-spec.md](docs/specs/cli/harite-cli-spec.md)
- GUI 詳細は [docs/specs/gui/harite-gui-spec.md](docs/specs/gui/harite-gui-spec.md)
- スライドショー詳細は [docs/specs/slideshow/harite-slideshow-spec.md](docs/specs/slideshow/harite-slideshow-spec.md)

推奨読順:

1. 本書で全体像と責務境界を掴む。
2. core で最適化、設定ファイル、適用条件の基底仕様を読む。
3. その後、必要に応じて CLI / GUI / スライドショー の各分冊へ進む。

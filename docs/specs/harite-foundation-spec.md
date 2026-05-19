# Harite 基本仕様 (Foundation Spec)

最終更新: 2026-05-19

## 1. 文書の目的と適用範囲

- 本書は Harite の常設仕様書群の入口である。
- 主題は、現行 Harite が何を目的とし、どの環境で、どの操作面を持ち、どの分冊へ読むべきかを示すことにある。
- planning 履歴、過去判断の時系列、没案の説明は対象外とする。

## 2. Harite の目的

- Harite は、壁紙画像の最適化と適用を、GUI と CLI の両面から扱うためのツールである。
- 主な責務は、入力画像の解決、表示条件に応じた最適化、OS / desktop plugin を通じた適用、継続運用としての watch にある。
- 特に GUI では、compose -> optimize -> apply の流れを日常操作として扱えることを重視する。

## 3. 想定利用者

- 日常的に壁紙最適化と適用を行う owner
- 将来の保守者
- 新しい仕様変更や実装変更の前提確認をしたい contributor

## 4. 対象環境と前提依存

- Python ベースのアプリケーションとして動作する。
- CLI は cross-platform を志向するが、plugin 実装により適用面は OS ごとに差分を持つ。
- GUI は GTK / PyGObject が利用可能な環境を前提とする。
- Linux / XFCE では per-monitor apply, watch, tray, desktop entry まわりの説明比重が高い。

## 5. 全体アーキテクチャ概要

Harite の主な面は以下の 5 つである。

1. 基本仕様 (foundation): 全体像と分冊導線
2. コア仕様 (core): 最適化、設定、適用条件の基底仕様
3. CLI 仕様 (CLI): command surface
4. GUI 仕様 (GUI): 画面、操作、状態、tray
5. watch 仕様 (watch): 継続実行、pause / retry、観測面

## 6. GUI / CLI / watch / tray の関係

```mermaid
flowchart TD
    User[User] --> GUI[GUI surface]
    User --> CLI[CLI surface]
    GUI --> Core[core logic]
    CLI --> Core
    GUI --> Watch[GUI watch]
    CLI --> Watch[CLI watch]
    GUI --> Tray[task tray]
    Watch --> Plugin[OS plugin apply]
    Core --> Plugin
```

- GUI と CLI は別の操作面だが、基底挙動は core に寄せる。
- watch は CLI 専用ではなく、GUI 側にも長時間運用の責務を持つ。
- tray は GUI の補助操作面であり、watch の開始停止と可視状態制御に関与する。

## 7. 設定 (settings) / save / apply の責務分担

- 設定 (settings) は論理設定モデルとして保持され、物理保存は 設定ファイル (harite-preferences.json) を使う。
- save は optimize 結果の出力先決定と書き出しを扱う。
- apply は effective target を解決したうえで plugin へ委譲する。

## 8. README と仕様書の役割分担

- README は導入、インストール、最小の使用導線を扱う。
- 仕様書は、現行挙動、責務分担、状態、失敗時挙動を扱う。
- README に長い仕様説明や履歴説明を戻さない。

## 9. ソースディレクトリ構成と責務境界

```text
src/harite/
  cli.py                  CLI entrypoint と command surface
  config.py               設定ファイル (harite-preferences.json) の path 解決と JSON load/save
  preferences.py          設定モデルと JSON との相互変換
  core.py                 optimize の基底ロジック
  apply_settings.py       apply 対象の解決
  watch.py                watch の選択ループと cycle state
  plugins.py              OS / desktop plugin registry と apply 実装
  linux_xdg_launcher.py   Linux/XDG launcher 生成
  gui/
    app.py                GUI entrypoint
    views/                framework-neutral な状態モデル
    controllers/          GUI から core への接続制御
    adapters/             GTK runtime, dialog, tray, signal wiring
    services/             GUI 補助サービス
    resources/            icon などの同梱リソース
```

### GUI 配下の詳細分類

```text
src/harite/gui/
  app.py
    起動入口。MainWindow 生成、GTK backend load、tasktray 初期化、window present を束ねる。
  views/
    main_window.py
      主状態モデル。status, logs, 設定, optimize/apply/watch の業務状態を持つ。
    main_window_preview.py
      preview 表示専用の補助計算を持つ。
  controllers/
    optimize_controller.py
      GUI form state を core.optimize 実行へ橋渡しする。
  services/
    cli_mapper.py
      GUI state を CLI 相当の引数列へ写像する。
  adapters/
    gtk_backend.py
      GTK runtime 統合窓口。
    ui_adapter.py
      runtime signal と MainWindow method の対応表を持つ。
    tasktray_adapter.py
      tray / indicator の生成と menu action を持つ。
    gtk_layout_builders.py / gtk_tab_builders.py / gtk_dialog_builders.py
      widget 構築責務を分割する。
    gtk_runtime_* modules
      signal, sync, dialog, watch, helper などの細粒度 runtime 責務を持つ。
```

## 10. 分冊導線

- core 詳細は [docs/specs/core/harite-core-spec.md](docs/specs/core/harite-core-spec.md)
- CLI 詳細は [docs/specs/cli/harite-cli-spec.md](docs/specs/cli/harite-cli-spec.md)
- GUI 詳細は [docs/specs/gui/harite-gui-spec.md](docs/specs/gui/harite-gui-spec.md)
- watch 詳細は [docs/specs/watch/harite-watch-spec.md](docs/specs/watch/harite-watch-spec.md)

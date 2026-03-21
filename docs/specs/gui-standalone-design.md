# GUI スタンドアロン設計（Glade資産取り込み前提）

最終更新: 2026-03-21

## 目的

- 旧母体の Glade/GTK 系仕様を参照しつつ、Harite の現行 CLI/コアを呼び出すスタンドアロン GUI を設計する。
- 当面は常駐機能（インジケーター、トレイ、デーモン）を実装しない。
- 実運用で使える最小 GUI（MVP）を先に成立させる。

## 前提

- 既存 Harite は CLI 中心で、コア処理は `src/harite/core.py`、入口は `src/harite/cli.py`。
- 旧母体に存在した `Starter` / `Applet` / `AppIndicator` / `Glade` は、現リポジトリでは実装コードとしては保持していない。
- 旧 GUI の知見は分析ドキュメント（`docs/specs/upstream-full-analysis.md` など）に要約されている。

## 調査結果（現時点）

### 現リポジトリ内の実体

- `.glade` / `.ui` ファイルは未格納。
- 常駐 UI 実装（indicator/tray）の現行コードは未実装。
- そのため、現時点で直接移植できるのは「分析済み仕様」であり、実体 XML は別途回収が必要。

### 外部 clone からの取り込み前提

- 旧母体の `.glade` / `.ui` は外部ディレクトリの clone 側に存在する前提で進める。
- 取り込み元（現時点）: `C:/Users/oggy_/Develop/Repos/wallpaperoptimizer`
- Harite 本体には次の手順で取り込む。
  1. 参照専用として `docs/legacy-ui/` に原本コピー（編集しない）
  2. 実装用に `src/harite/gui/resources/` へ必要分を抽出
  3. signal 名対応表を `docs/specs/gui-signal-mapping.md` に記録
- 取り込みガイド:
  - `docs/legacy-ui/README.md`
  - `src/harite/gui/resources/README.md`

### 取得済み資産

- `docs/legacy-ui/wallpositapplet.glade`
- `docs/legacy-ui/Glade.py`
- `src/harite/gui/resources/wallpositapplet.glade`

### 参照可能な上流仕様知見

- 旧設計は GTK/Glade ベースで GUI イベントハンドラが多い。
- 旧常駐系は古い依存（pygtk/xdg/appindicator）前提で、そのまま再利用は不可。
- コア計算ロジックは CLI/ライブラリ側で再実装済みなので、GUI は「入力収集」「プレビュー」「実行制御」に集中できる。

## スコープ

### MVP（今回の設計対象）

- 単体ウィンドウのスタンドアロン GUI。
- 画像入力、主要オプション設定、プレビュー、生成実行、結果表示。
- `optimize` と `apply` の安全な導線（dry-run 優先）。
- 余白情報埋め込み（`none|params|free|combo`）の設定 UI。

### 非目標（MVP）

- インジケーター常駐。
- トレイ常駐。
- 定期実行デーモン。
- 旧 Glade の 1:1 再現（レイアウトや見た目の完全互換）。

## 技術方針（案）

- 第一候補: PyGObject (GTK4) + GtkBuilder (`.ui`)。
  - 理由: Glade由来の構造に寄せやすく、Linux/XFCE と親和性が高い。
- 代替候補: Qt 系（PySide6）。
  - 理由: クロスプラットフォーム性は高いが、Glade資産との親和は低い。

設計決定（現時点）:
- MVP は GTK 系前提で仕様を記述する。
- 実装前に依存導入可否（配布難易度、CI負荷）を再確認する。

## フレームワーク最新化と選択

### 結論

- 第一選択: **PyGObject + GTK4 (GtkBuilder)**
- 第二選択: **PySide6 (Qt6)**

### 選定理由

- Linux/XFCE 親和性と旧 Glade 資産の継承を優先すると GTK 系が最短。
- 旧 pygtk/appindicator は採用せず、GTK4 + 非常駐で構成を簡素化できる。
- Qt6 はクロスプラットフォーム性に強いが、旧 Glade 資産の再利用効率が下がる。

### 最新化ポリシー

- 禁止: pygtk, appindicator, Python2 時代 API
- 推奨: GTK4 + Builder XML + controller 分離
- 将来の常駐機能は別モジュールに分離し、MVP には入れない

## 画面構成（MVP）

1. MainWindow
- 入力画像/ディレクトリ選択
- 出力先選択
- 解像度、レイアウト、スケーリング、品質、padding
- two-screen 設定（チェック、左右解像度、margins、fixed）
- 余白情報埋め込み設定（embed 系）
- 実行ボタン（Preview / Optimize / Apply dry-run / Apply do-it）

2. PreviewPane
- 生成予定画像のサムネイル表示
- 配置情報（矩形、スケール、左右割当）の要約表示

3. LogPane
- 実行ログ
- 失敗時の原因表示（入力不足、解像度不正、plugin 不一致等）

## UX 原則

- デフォルト安全: `apply` は dry-run を既定にする。
- 失敗を早く出す: 入力不足や数値異常は実行前にバリデーション。
- CLI 対応の見える化: GUI 操作に対応する CLI 引数のプレビュー表示を用意する。

## CLI マッピング（MVP）

- 入力: `--input`
- 出力先: `--output`
- 解像度: `--resolution`
- 基本設定: `--layout`, `--scaling`, `--quality`, `--padding`
- two-screen: `--two-screen`, `--l-display`, `--r-display`, `--margins`, `--fixed`
- 配置: `--align`, `--valign`
- 埋め込み: `--embed-info`, `--embed-text`, `--embed-position`, `--embed-max-lines`
- 適用: `apply --plugin ... --file ... [--do-it]`

## モジュール分割案

- `src/harite/gui/app.py`
  - エントリポイント、アプリ起動
- `src/harite/gui/views/main_window.py`
  - メインウィンドウ定義（GtkBuilder 読み込み）
- `src/harite/gui/controllers/optimize_controller.py`
  - 入力収集、バリデーション、core 呼び出し
- `src/harite/gui/services/cli_mapper.py`
  - GUI状態 -> CLI引数 変換
- `src/harite/gui/services/preview_service.py`
  - 画像プレビュー生成、メタ情報整形

## 旧 Glade 資産の取り込み方

1. 旧母体から `.glade` / `.ui` / signal 定義を回収
2. 画面要素を次の3種に分類
- 再利用（概念維持）: 入力、設定、プレビュー、実行
- 改変（現行CLI準拠）: two-screen、embed、apply dry-run
- 廃止（MVP非対象）: indicator/tray/daemon
3. 旧 signal 名と新 controller メソッドの対応表を作る
4. 1:1 再現ではなく「操作意図」を優先して UI を再設計

## 受け入れ基準（MVP）

- GUI だけで `optimize` の主要機能を実行できる。
- 実行結果画像と配置情報を GUI 上で確認できる。
- `apply` は dry-run を標準で実行でき、`do-it` は明示操作のみ。
- two-screen と embed 設定が GUI から操作できる。
- indicator/tray なしで単体アプリとして起動・終了できる。

## リスク

- GTK 依存導入時の環境差（特に Windows 開発環境）。
- 旧 Glade 実体が未回収の場合、再現精度が下がる。
- GUI 実装が先行しすぎると CLI 仕様変化に追従コストが増える。

## 実装順（推奨）

1. 設計固定（本書）
2. 画面遷移なしの単一ウィンドウ雛形
3. 入力バリデーション + optimize 実行
4. プレビューとログ表示
5. apply(dry-run) 導線
6. do-it 明示導線

## 次アクション

- A. 旧母体の Glade 実体ファイル回収（可能なら最優先）
- B. `gui` サブパッケージ骨格の追加（実装ゼロの起動確認まで）
- C. MainWindow の項目定義を UI ID 一覧として別紙化

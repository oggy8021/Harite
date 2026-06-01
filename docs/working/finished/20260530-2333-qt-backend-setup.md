# Harite Qt backend セットアップ手順書

最終更新: 2026-05-31（XFCE 実機: `libxcb-cursor0` 追記）

## 概要

本書は GTK backend（`harite-gtk`）と Qt backend（`harite-qt`）を同一環境で並べて動かすための手順書である。  
Qt backend は Phase 1（空ウィンドウ）から始まり、フェーズごとに機能を追加していく。

---

## 1. 前提環境

| 環境 | 必要なもの |
|---|---|
| Windows 11 | Python 3.12+、Git |
| Linux Mint XFCE | Python 3.12+、Git、GTK 3 / python3-gi（GTK backend 用）、**`libxcb-cursor0`**（Qt backend GUI 用・下記 §2.1） |
| 共通 | `pip install PyQt6` が動作するネットワーク環境 |

---

## 2. インストール手順

### 2.1 通常インストール（pip）

```bash
# Qt backend を含めてインストール
pip install -e ".[gui-qt]"
```

Linux（X11 / XFCE）で `harite-qt` のウィンドウを出す場合、pip だけでは不足する。Qt 6.5+ の xcb platform plugin は **`libxcb-cursor0`** を要求する（システム Qt SDK は不要）。

```bash
# Debian / Ubuntu / Linux Mint 系（XFCE 実機で確認済み）
sudo apt install libxcb-cursor0
```

これで以下のエントリーポイントが使えるようになる。

| コマンド | 内容 |
|---|---|
| `harite` | CLI（optimize / apply / slideshow） |
| `harite-gtk` | GTK backend GUI（旧 `harite-gui`） |
| `harite-qt` | Qt backend GUI（Phase 1 以降） |
| `harite-gui` | GTK backend GUI（後方互換エイリアス） |

### 2.2 pipx を使う場合

GTK backend は `--system-site-packages` が必要（python3-gi がシステム提供のため）。  
Qt backend の **Python パッケージ**は pip で完結するが、Linux GUI 表示には §2.1 の `libxcb-cursor0` が別途必要。

```bash
# Qt backend のみ使う場合
pipx install -e ".[gui-qt]"

# GTK backend も使う場合（Linux のみ）
pipx install --system-site-packages -e ".[gui-qt]"
```

---

## 3. 起動方法

### 3.1 Qt backend（harite-qt）を起動する

```bash
harite-qt
```

Phase 1 では「Harite」タイトルの空ウィンドウが表示される（900×640px）。

```bash
# ウィンドウ表示なしで import のみ確認したい場合
harite-qt --no-present-ui-window
```

### 3.2 GTK backend（harite-gtk）を起動する

```bash
# Linux / XFCE 環境で GTK が利用できる場合
harite-gtk
```

### 3.3 ヘッドレス環境（CI / SSH 接続先など）

```bash
# QT_QPA_PLATFORM=offscreen を設定することで画面なしで Qt が動作する
QT_QPA_PLATFORM=offscreen harite-qt --no-present-ui-window
```

---

## 4. 両 backend を並べて確認する

同一マシンで GTK と Qt を同時に起動できる（互いに影響しない）。

```bash
# ターミナル 1
harite-gtk &

# ターミナル 2
harite-qt &
```

どちらも `MainWindow` の同じ owner state を生成するため、設定ファイルは共通（`~/.config/harite/harite-settings.json`）。

---

## 5. テスト実行

### 5.1 Qt backend テストのみ実行する

```bash
QT_QPA_PLATFORM=offscreen pytest tests/gui/test_app_qt_entrypoint.py -v
```

### 5.2 全テストを実行する

```bash
QT_QPA_PLATFORM=offscreen pytest -q
```

### 5.3 PyQt6 がインストールされていない場合

Qt 固有テスト（`pytest.importorskip("PyQt6")` を含むもの）は自動的に skip される。  
PyQt6 なしの環境でも既存の GTK backend テストには影響しない。

---

## 6. トラブルシューティング

| 症状 | 対処 |
|---|---|
| `Harite Qt backend is unavailable` | `pip install PyQt6` を実行する |
| `Could not load the Qt platform plugin "xcb"` / `libxcb-cursor0 is needed` | `sudo apt install libxcb-cursor0`（§2.1）。pip 側は既に OK のことが多い |
| `QT_QPA_PLATFORM` 未設定でヘッドレス環境クラッシュ | `export QT_QPA_PLATFORM=offscreen` を追加する |
| `harite-qt` コマンドが見つからない | `pip install -e ".[gui-qt]"` を再実行する |
| Qt ウィンドウがアイコンなしで表示される | `PyQt6-Qt6` の SVG サポートが不足している可能性（`pip install PyQt6` 再インストール） |
| Windows で XFCE 用 plugin が動かない | 想定内の動作。Windows plugin が適用に使われる |

---

## 7. Phase 進捗と対応 PR

| Phase | 内容 | 状態 |
|---|---|---|
| Phase 0 | 依存関係・CI 準備（`PyQt6` optional extra、CI 更新） | 完了 |
| Phase 1 | 空ウィンドウ（`qt_backend.py`、`app_qt.py`） | 完了 |
| Phase 2 | レイアウト骨格（3 層 + タブ） | 未着手 |
| Phase 3 | Main タブ | 未着手 |
| Phase 4 | Margins タブ | 未着手 |
| Phase 5 | Slideshow タブ | 未着手 |
| Phase 6 | Dialogs | 未着手 |
| Phase 7 | System Tray | 未着手 |
| Phase 8 | Signal wiring・状態同期 | 未着手 |
| Phase 9 | リソース・スタイリング | 未着手 |
| Phase 10 | 旧 GTK 除去・クリーンアップ | 未着手 |

# Harite PyQt6 移植ロードマップ（仕様書修正後版）

最終更新: 2026-05-30

## 位置づけ

- 本書は v1.0.0 後の次期 planning 入口として、GTK 3 / PyGObject から PyQt6 への移植を具体化した計画文書である。
- [docs/working/20260520-feature-overview.md](20260520-feature-overview.md) の C-04（GUI 利用導線の再設計）と密接に関連する。
- 仕様書は 2026-05-30 時点のリファクタ後正本（`docs/specs/`）を参照基準とする。

---

## 1. 現行アーキテクチャの整理

### 1.1 レイヤー構成と主要ファイル

```text
src/harite/gui/
  app.py                        # エントリーポイント（GTK backend のロード seam）
  resource_access.py            # リソースパス解決（GTK 非依存）
  views/
    main_window.py              # framework-neutral owner state（1,447 行）
    main_window_preview.py      # preview 補助計算（138 行）
  controllers/
    optimize_controller.py      # GUI → core bridge（165 行）
  services/
    cli_mapper.py               # GUI state → CLI args（71 行）
  adapters/                     # ← GTK 固有。全面置き換え対象
    gtk_backend.py              # GTK runtime 統合窓口（1,222 行）
    gtk_tab_builders.py         # タブ widget 構築（838 行）
    gtk_runtime_dialogs.py      # dialog ロジック（995 行）
    gtk_runtime_settings_dialogs.py  # settings dialogs（472 行）
    gtk_runtime_file_dialog_flow.py  # ファイルダイアログ（334 行）
    gtk_runtime_object_registry.py   # widget registry（217 行）
    gtk_dialog_builders.py      # dialog 骨格（245 行）
    gtk_layout_builders.py      # レイアウト骨格（194 行）
    gtk_runtime_sync.py         # 状態同期（184 行）
    gtk_runtime_preview.py      # preview widget（173 行）
    tasktray_adapter.py         # system tray（280 行）
    gtk_runtime_signal_wiring.py # signal 接続（135 行）
    gtk_runtime_slideshow_ui.py  # slideshow UI（125 行）
    gtk_runtime_slideshow.py     # slideshow ロジック（112 行）
    gtk_runtime_widget_access.py # widget アクセス（121 行）
    gtk_runtime_state_labels.py  # state label 同期（51 行）
    gtk_runtime_save_path_access.py  # 保存パス（51 行）
    gtk_runtime_owner_sync.py    # owner state 同期（48 行）
    gtk_runtime_margin_text_gtk.py   # margin text GTK 固有（46 行）
    gtk_runtime_margin_text.py   # margin text ロジック（32 行）
    gtk_runtime_builders.py      # 共通 builder（32 行）
    ui_adapter.py               # signal dispatch table（99 行）
```

### 1.2 移行対象・非対象の分類

| 分類 | ファイル群 | 行数合計 | 対応 |
|---|---|---|---|
| **維持** | views/、controllers/、services/ | ~1,821 行 | そのまま |
| **維持** | core.py、plugins.py、cli.py、slideshow.py 等 | 非 GUI 全体 | 無関係 |
| **置き換え** | adapters/gtk_*.py、tasktray_adapter.py | ~7,500 行 | Qt 版を新設 |
| **改修** | app.py | 159 行 | ローダー seam を切り替え |
| **改修** | ui_adapter.py | 99 行 | ハンドラマップは維持、dispatch 実装を調整 |
| **改修** | resource_access.py | 24 行 | `importlib.resources` ベースのため最小変更 |

### 1.3 移行の有利な点

- **`ui_adapter.py` の `RUNTIME_HANDLER_MAP`** が `MainWindow` メソッドと GTK signal の対応を既に宣言している。Qt 移行では同じマップを Qt signal の接続に再利用できる。
- **`app.py` の `_load_ui_signal_backend()`** が GTK backend のロード唯一の seam になっている。ここを Qt 版に差し替えるだけで既存テストは壊れない。
- **`views/main_window.py` に GTK import なし**。framework-neutral であることが仕様書（gui-spec §1）通りに実装されている。
- **SVG アイコンリソースが既に分離**済み（`resources/icons/`）で `QIcon` / `QSvgRenderer` でそのまま使える。

---

## 2. 移行方針

### 2.1 方式の選択肢

| 方式 | 内容 | リスク |
|---|---|---|
| Big Bang | adapters/ を一括で Qt に書き換える | 動作確認できない中間状態が長期続く |
| Incremental（サブシステム単位） | タブ 1 枚ずつ差し替える | 2 フレームワーク混在が複雑 |
| **New adapter directory（採用）** | `adapters_qt/` を新設し段階的に実装、最後に seam を切り替える | 最も安全。旧 GTK は削除前まで動き続ける |

### 2.2 採用方針の概要（確定: デュアルバックエンド非対称運用）

オーナーの常用環境（Windows 11 + Linux Mint XFCE）を踏まえた結論として、**デュアルバックエンドの非対称運用**を採用する。

```text
harite-gtk  ← 現行 harite-gui をリネーム。XFCE ネイティブ。maintenance mode（バグ修正のみ）
harite-qt   ← 新規開発。Windows 日常使用が主目的。XFCE でも動作する
```

エントリーポイントの変遷:

```text
[現在]          [移行中]                        [完了後]
harite-gui      harite-gtk  ← 現行のリネーム    harite-gtk  （maintenance mode）
                harite-qt   ← 段階的に実装      harite-qt   （development focus）
```

実装の進め方:
- `adapters_qt/` を新ディレクトリとして作成し、Qt 版のファイルを順次実装する。
- `app.py` に環境変数 `HARITE_GUI_BACKEND=qt` のフラグを追加し、早期から切り替えテストできるようにする。
- 各 Phase が完了したら GTK 版との動作を比較し、`MainWindow` の振る舞いが一致することを確認する。
- Qt 版が安定したら GTK 版を deprecated とし、将来的に除去する。除去タイミングは別途判断。

---

## 3. フェーズ計画

### Phase 0: 依存関係・CI 準備

**目標**: `import PyQt6.QtWidgets` が CI で通る状態にする。

| 作業 | 詳細 |
|---|---|
| `pyproject.toml` に `PyQt6>=6.4` を追加 | optional extras か本体依存かは §6 判断待ち |
| CI workflow に PyQt6 インストールを追加 | `pip install PyQt6` / ヘッドレス用 `QT_QPA_PLATFORM=offscreen` |
| `adapters_qt/` ディレクトリを作成 | `__init__.py` のみ |
| `app.py` に `--backend gtk\|qt` フラグを追加 | 既存動作に影響しない形で追加 |

**成果物**: `adapters_qt/__init__.py`、CI 設定更新

---

### Phase 1: Qt 基盤（空ウィンドウ）

**目標**: `QMainWindow` が起動し、ウィンドウタイトル・アイコンが表示される状態。

| 作業 | 対応する GTK ファイル |
|---|---|
| `adapters_qt/qt_backend.py` 新設（`QApplication` + `QMainWindow` の最小構成） | `gtk_backend.py` の骨格 |
| `adapters_qt/qt_app.py` 新設（Qt 版 `_load_qt_signal_backend`） | `app.py` の GTK ローダー部分 |
| `resource_access.py` を Qt で使えるか確認（`importlib.resources` ベースのため基本 OK） | `resource_access.py` |
| `QIcon` で `harite_app.svg` を表示 | `tasktray_adapter.py` の icon 初期化 |

**確認**: `python -m harite.gui.app --backend qt` で空ウィンドウが表示される。

---

### Phase 2: レイアウト骨格（3 層 + タブ）

**目標**: header / center-body / footer の 3 層と Main / Margins / Slideshow タブが空で存在する。

GUI spec §3 に対応。

| 作業 | 対応する GTK ファイル |
|---|---|
| `adapters_qt/qt_layout_builders.py` 新設 | `gtk_layout_builders.py` |
| `QVBoxLayout` で header / notebook / footer を組む | 同上 |
| `QTabWidget` で 3 タブを作成（中身は空） | `gtk_tab_builders.py` の骨格 |
| header: title label + command bar（Color / Settings / About ボタン） | `gtk_layout_builders.py` |
| footer: Status + Slideshow summary / Error の 2 行構成 | 同上 |

---

### Phase 3: Main タブ

**目標**: 画像入力・方向 toggle・Optimize / Apply ボタンが動作する状態。

GUI spec §3 Main tab / §4 メイン操作フロー に対応。

| 作業 | 対応する GTK ファイル |
|---|---|
| `adapters_qt/qt_tab_main.py` 新設 | `gtk_tab_builders.py` の Main tab 部分 |
| compose grid: Left panel / center panel / Right panel | 同上 |
| 方向 toggle 群（QToolButton × 8 per side） | `gtk_runtime_signal_wiring.py` の direction widgets |
| Open-L / Open-R / Clear-L / Clear-R ボタン | 同上 |
| action cluster: Preview / Optimize / Apply ボタン | `gtk_runtime_signal_wiring.py` の action widgets |
| apply mode radio（No Split / Auto-Split） | 同上 |
| preview box（QLabel + QPixmap） | `gtk_runtime_preview.py` |
| `MainWindow` の signal dispatch を Qt signal に接続 | `ui_adapter.py` |

**技術メモ**: GTK の `widget.connect("clicked", handler)` → Qt の `button.clicked.connect(handler)` に対応する。`RUNTIME_HANDLER_MAP` を使えば dispatch table をほぼそのまま引き継げる。

---

### Phase 4: Margins タブ

**目標**: margin 値変更・embed pattern 選択・position selector が動作する状態。

GUI spec §3 Margins tab に対応。

| 作業 | 対応する GTK ファイル |
|---|---|
| `adapters_qt/qt_tab_margins.py` 新設 | `gtk_tab_builders.py` の Margins tab 部分 |
| cross-grid editor（4 方向 QSpinBox + 中央 stack） | `gtk_tab_builders.py` |
| embed pattern radio 4 択（Off / Settings / Text only / Both） | 同上 |
| margin text entry（`QPlainTextEdit`） | 同上 |
| position selector（Left/Right × Top/Bottom `QRadioButton`） | 同上 |
| margin text preflight 結果 → status 反映 | `gtk_runtime_margin_text.py`、`gtk_runtime_margin_text_gtk.py` |

---

### Phase 5: Slideshow タブ

**目標**: srcdir 選択・mode 選択・Start / Stop が動作する状態。

GUI spec §3 Slideshow tab / §6 slideshow との接続 に対応。

| 作業 | 対応する GTK ファイル |
|---|---|
| `adapters_qt/qt_tab_slideshow.py` 新設 | `gtk_tab_builders.py` の Slideshow tab 部分 |
| Srcdir-L / Srcdir-R 選択ボタン + パス表示 | `gtk_runtime_slideshow_ui.py` |
| mode radio（sequential / random） + mode help label | 同上 |
| interval spin + Start / Stop ボタン | 同上 |
| slideshow timer: `QTimer` で `interval_ms` を設定 | `gtk_runtime_slideshow.py` の `GLib.timeout_add` 部分 |
| slideshow output display label の更新 | `gtk_runtime_state_labels.py` |

**技術メモ**: GTK の `GLib.timeout_add(interval_ms, callback)` → `QTimer.singleShot` または `QTimer` の繰り返しモードに置き換える。`callback` が `False` を返したら `timer.stop()` する点は同じロジックで実装できる。

---

### Phase 6: Dialogs

**目標**: Settings / Color / About / Export Image の各 dialog が開閉できる状態。

GUI spec §3 Dialogs に対応。

| 作業 | 対応する GTK ファイル | Qt の対応 |
|---|---|---|
| Settings dialog | `gtk_runtime_settings_dialogs.py`（472 行） | `QDialog` + フォーム layout |
| Color dialog（背景色ピッカー） | `gtk_runtime_dialogs.py` 内 | `QColorDialog` で代替可能 |
| About dialog | `gtk_runtime_dialogs.py` 内 | `QDialog` |
| Export Image dialog（保存先選択） | `gtk_runtime_file_dialog_flow.py`（334 行） | `QFileDialog.getSaveFileName` |
| ファイル選択 dialog（Open-L/R / Srcdir-L/R） | `gtk_runtime_file_dialog_flow.py` | `QFileDialog.getOpenFileName` / `getExistingDirectory` |
| `adapters_qt/qt_dialogs.py` 新設 | 上記 GTK dialog ファイル群 | — |

**技術メモ**: GTK の `Gtk.FileChooserDialog` は複数ステップの状態機械だったが、Qt の `QFileDialog` は単一呼び出しで結果を返す。`gtk_runtime_file_dialog_flow.py` の 334 行の多くはこの state management なので、Qt 版は大幅に短くなる見込み。

---

### Phase 7: System Tray

**目標**: tray icon が表示され、Visible toggle / Start / Stop が動作する状態。

GUI spec §7 tray / indicator / app icon surface に対応。

| 作業 | 対応する GTK ファイル | Qt の対応 |
|---|---|---|
| `adapters_qt/qt_tray_adapter.py` 新設 | `tasktray_adapter.py`（280 行） | `QSystemTrayIcon` + `QMenu` |
| icon の slideshow 状態切り替え | `tasktray_adapter.py` | `QIcon` の切り替え |
| tray menu（Visible / Start / Stop / Settings / Color / About / Quit） | `tasktray_adapter.py` | `QAction` |

**技術メモ**: 現行は `AyatanaAppIndicator3`（Ubuntu AppIndicator）→ `AppIndicator3` のフォールバック順。Qt の `QSystemTrayIcon` はクロスプラットフォームで動作し、Linux / Windows / macOS すべてで同一コードになる。これは GTK 版より**大幅にシンプル**になる。ただし AppIndicator が必須の環境（Ubuntu Unity 等）では見た目が変わる可能性がある。

---

### Phase 8: Signal Wiring と状態同期の仕上げ

**目標**: 全ての `RUNTIME_HANDLER_MAP` エントリが動作し、状態同期に漏れがない状態。

| 作業 | 対応する GTK ファイル |
|---|---|
| `adapters_qt/qt_signal_wiring.py` 新設（Phase 3–7 の signal を統合） | `gtk_runtime_signal_wiring.py` |
| owner state → Qt widget への逆同期（`MainWindow` → widget 表示） | `gtk_runtime_sync.py`（184 行）、`gtk_runtime_owner_sync.py`（48 行） |
| widget registry（widget 名 → Qt object の解決） | `gtk_runtime_object_registry.py`（217 行） |
| footer status label / error label の更新 | `gtk_runtime_state_labels.py` |
| スレッド安全な UI 更新（optimize は別スレッド実行） | `gtk_backend.py` の `GLib.idle_add` 部分 → `QMetaObject.invokeMethod` またはシグナル経由 |

**技術メモ**: GTK の `GLib.idle_add(callback)` は UI スレッドへの安全な委譲。Qt では `QMetaObject.invokeMethod(..., Qt.QueuedConnection)` またはカスタムシグナルで同等を実現する。`optimize_wallpapers` を `QThread` / `concurrent.futures` で実行する設計も検討。

---

### Phase 9: リソース・アイコン・スタイリング

**目標**: アイコン・SVG・スタイルが仕様どおりに表示される状態。

| 作業 | 詳細 |
|---|---|
| `resource_access.py` の Qt 版確認 | `importlib.resources` ベースのためほぼそのまま使える |
| `QIcon` / `QSvgRenderer` で Lucide SVG を表示 | `resources/icons/lucide/*.svg` |
| product icon の `QIcon` 設定 | `harite_app.svg` / `harite.svg` / `harite_off.svg` |
| Qt stylesheet で基本スタイルを設定（GTK CSS の Qt 版） | `gtk_layout_builders.py` の `style` 設定部分 |

---

### Phase 10: 旧 GTK 除去・クリーンアップ *(永続ペンディング – 実施しない)*

> **2026-05-31 決定**: デュアルバックエンド戦略（`harite-gtk` を XFCE 向けにメンテナンス継続、`harite-qt` を Windows 向け新規開発）を採択したため、GTK の完全除去は行わない。本 Phase の内容は対象外とする。

~~**目標**: GTK 依存を完全に除去し、`pyproject.toml` からも削除。~~

| 作業 | 詳細 | 状態 |
|---|---|---|
| `adapters/gtk_*.py` 一式を削除 | 計 21 ファイル | 実施しない |
| `adapters/tasktray_adapter.py`（旧 GTK 版）を削除 | `adapters_qt/qt_tray_adapter.py` に置き換え済み | 実施しない |
| `app.py` の GTK ローダー分岐を削除（Qt 版のみに） | | 実施しない |
| `pyproject.toml` の GTK 系 extras / PyGObject 記述を削除または optional 化 | | 実施しない |
| CI workflow の PyGObject セットアップを削除 | | 実施しない |
| README の「GTK 3 / PyGObject が必要」記述を更新 | | 実施しない |
| 全テストが Qt backend で通ることを確認 | | 実施しない |

---

## 4. 主要な技術的チャレンジ

| 課題 | GTK 現行 | Qt 対応 | 難易度 |
|---|---|---|---|
| タイマー（slideshow） | `GLib.timeout_add(ms, cb)` → `False` で停止 | `QTimer` + `timeout` signal | 低 |
| スレッド安全 UI 更新 | `GLib.idle_add(cb)` | カスタム signal または `invokeMethod` | 中 |
| ファイルダイアログ | state machine（334 行） | `QFileDialog` 単一呼び出し | 低（簡素化） |
| system tray | `AyatanaAppIndicator3` / `AppIndicator3` フォールバック | `QSystemTrayIcon`（クロスプラットフォーム） | 低（簡素化） |
| preview 描画 | `GdkPixbuf` / GTK widget | `QPixmap.load(path)` + `QLabel.setPixmap` | 低 |
| CSS スタイリング | GTK CSS（`widget.get_style_context().add_class`） | Qt stylesheet | 中 |
| direction toggle の toggled/pressed/released | GTK toggle button 3 signal | `QPushButton` + `checkable` + 3 signal | 中 |
| widget registry | `gtk_runtime_object_registry.py` の GTK widget 名解決 | dict で `{name: QWidget}` を管理 | 低 |

---

## 5. C-04（GUI 利用導線の再設計）との関係

feature-overview の C-04 は「optimize / apply / slideshow を利用目的ベースで再構成する」提案だが、**現時点では構想保持**に分類されている。

**Qt 移植フェーズ（Phase 0–10）の目標は現行仕様書どおりの構成を再現すること**とし、C-04 の UX 変更は扱わない。

理由:
- 「利用目的ベース」の具体的な画面遷移案がまだ存在しない。
- 移植と UX 変更を同時に進めると検証の基準が定まらない。
- 現行 GUI spec（2026-05-30 正本）が「移植後の正解」として機能する。

**C-04 の採用条件**（feature-overview より）:
- 既存レイアウトの骨格を維持しつつ、世の標準傾向や UX トレンドを引用した「主要導線がより良くなる」ストーリーが組めたとき。
- この条件が整った場合のみ、Qt 版で Phase 11 以降として着手する。

**参考**: C-04 rough ideas（Qt との親和性）

| C-04 rough idea | Qt での展開可能性（参考） |
|---|---|
| task ベース（「作る」「適用する」「回す」） | QStackedWidget でタスクビューを差し込みやすい |
| progressive disclosure | `QGroupBox` collapsible / `QSplitter` で段階的開示が実装しやすい |
| scenario ベース入口 | `QWizard` で welcome wizard として実装できる |

---

## 6. 工数の粗見積り

| フェーズ | 主な作業内容 | 目安 |
|---|---|---|
| Phase 0 | 依存関係・CI 準備 | 0.5–1 日 |
| Phase 1 | Qt 基盤（空ウィンドウ） | 0.5–1 日 |
| Phase 2 | レイアウト骨格 | 1–2 日 |
| Phase 3 | Main タブ | 2–3 日 |
| Phase 4 | Margins タブ | 1–2 日 |
| Phase 5 | Slideshow タブ | 1–2 日 |
| Phase 6 | Dialogs（4 種） | 2–3 日 |
| Phase 7 | System Tray | 0.5–1 日 |
| Phase 8 | Signal wiring 仕上げ・状態同期 | 2–3 日 |
| Phase 9 | リソース・スタイリング | 0.5–1 日 |
| Phase 10 | 旧 GTK 除去・クリーンアップ | 1–2 日 |
| **合計** | | **12–21 日（2.5–4 週間）** |

前提: spec ドリブンで 1 フェーズずつ spec 検証しながら進める場合。各フェーズに spec との照合・テスト更新を含む。

---

## 7. 残課題・判断待ち

### 確定済み

| ID | 課題 | 決定内容 |
|---|---|---|
| J-05 | C-04 の優先度 | Qt 移植を先行。C-04 は構想保持（採用条件付き） |

### 判断待ち

| ID | 課題 | 判断内容 |
|---|---|---|
| J-01 | PyQt6 の依存関係扱い | `[project.dependencies]` に必須で追加するか、`[project.optional-dependencies]` の `gui-qt` extra にするか |
| J-02 | PyGObject / GTK backend の長期扱い | `harite-gtk` が maintenance mode に移行後、いつ deprecated → 除去するか。`gui-gtk` extra として残すか |
| J-03 | `fake_adapter.py` の扱い | テスト用 fake adapter を Qt 版でも維持するか（現行 `fake_adapter.py` は GTK import なしの可能性が高い） |
| J-04 | `--system-site-packages` 不要化 | PyQt6 は `pip install PyQt6` で動作するため、`pipx install` 時の `--system-site-packages` が不要になる可能性。install 手順の変更範囲を確認 |
| J-06 | Windows / macOS での tray 動作確認 | `QSystemTrayIcon` は XFCE 以外でも動く。Windows での tray 表示が副産物として得られる |

### Mac サポート方針（確定）

- Mac コードはリポジトリに残す。
- `README` および `docs/` に「community-maintained、オーナー未検証」として明記する。
- 不具合報告は受け付けるが、オーナー側で再現・修正する義務は持たない。

---

## 付録: 参照仕様・文書

- GUI 仕様: [docs/specs/gui/harite-gui-spec.md](../specs/gui/harite-gui-spec.md)
- Foundation 仕様: [docs/specs/harite-foundation-spec.md](../specs/harite-foundation-spec.md)
- Feature overview: [docs/working/20260520-feature-overview.md](20260520-feature-overview.md)
- Release readiness: [docs/release-readiness-checklist.md](../release-readiness-checklist.md)

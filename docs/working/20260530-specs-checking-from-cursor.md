# 仕様書 vs 実装 ギャップ分析レポート

作成日: 2026-05-30  
調査対象ブランチ: `main`（`c4d7e46`）  
調査範囲: `src/`, `tests/`, `docs/specs/`

---

## 凡例

| カテゴリ記号 | 意味 |
|---|---|
| **矛盾** | 仕様と実装が食い違う |
| **仕様漏れ** | 実装に挙動があるが仕様に記載がない |
| **エッジケース未記載** | 仕様は主要パスのみ記載、境界・例外動作が未記載 |
| **テストのみ** | テストコードにのみ存在し仕様・実装コメントに未反映 |
| **仕様内矛盾** | 同一仕様書内で記述が食い違う |

---

## 1. Foundation / 横断

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| F1 | Foundation §9 ディレクトリ図 | `src/harite/core/` パッケージは存在しない。`optimize_settings.py`, `apply_settings.py`, `display_context.py` 等が `src/harite/` 直下に散在 | `core/` 配下にまとまるように記載 | **矛盾** |
| F2 | Foundation §6.1 責務表 | `core.py` 内で margins・background_color のフォールバックが発生（値不正でも処理続行）。CLI/GUI は先に厳格検証 | core は「基底正規化」、検証は CLI/GUI 主責務 | **矛盾**（厳格さの層が逆転するケースがある） |

---

## 2. Core（`core.py` 他）

### A. 入力・表示コンテキスト

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| A1 | core §3, §7 | `normalize_optimize_input_paths` はディレクトリのみ `ValueError`。存在しないファイル・非画像は検証しない（core は後で黙ってスキップ） | ディレクトリ拒否と代表的失敗例のみ記載 | **エッジケース未記載** |
| A2 | core §3.1 | `optimize_wallpapers` は3枚以上の画像も処理可能（N 枚横分割）。CLI は先頭2件に切るが GUI/Controller は切らない | public surface は先頭2件採用 | **矛盾**（core 直呼びと public 面の乖離） |
| A3 | core §3.1 | `resolve_optimize_display_settings` は resolution 文字列の形式を検証しない。`WxH` 検証は CLI/GUI 側の `parse_resolution` が担当 | 仕様上の検証責務の所在が不明瞭 | **仕様漏れ** |
| A4 | core §3.1 | `build_two_screen_optimize_context` は **先頭2台の display のみ**から virtual resolution を算出 | 「検出 display 群」から virtual を作ると読める | **エッジケース未記載**（3画面以上環境） |
| A5 | 未記載 | `closest_display_for_offset`, `get_display_at_index` 等のヘルパ関数が `display_context.py` に存在 | core spec 未掲載 | **仕様漏れ** |

### B. 最適化・配置

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| B1 | core §6.3 settings | `OptimizeSettings.scaling` は保存・GUI で保持されるが optimize 結果に影響しない（常に `fit`） | settings key 一覧に `scaling` なし | **仕様漏れ**（設定キーの存在と無効性） |
| B2 | core §4.1 | 読み込み失敗画像は `continue` で黙ってスキップ。全画像失敗でも JPEG 出力（背景のみ）が発生しうる | 入力不正の代表例のみ | **エッジケース未記載** |
| B3 | core §4.1 | 0×0 画像は `_scale_to_fit` が `(1,1,1.0)` を返す | 未記載 | **エッジケース未記載** |
| B4 | core §4.1 | `align`/`valign` はインデックス 0/1 のみペア適用。3枚目以降はインデックス 0 側を再利用 | single-screen 各画像 `i` に align | **矛盾**（3枚以上時の align 挙動） |
| B5 | core §4.1 | リサイズは `Image.LANCZOS`、内部は RGB フラット化（RGBA→RGB） | アルゴリズム・アルファ処理が未記載 | **仕様漏れ** |
| B6 | テスト | `test_three_images_split`（regression）は3入力分割を期待動作として固定 | public 2件制限との関係が不明 | **テストのみ** |

### C. margins / background

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| C1 | CLI spec §optimize | `cli.py` の `parse_margins` docstring は `left,top,right,bottom` と誤記（実装は `left,right,top,bottom`） | CLI spec は `l,r,top,bottom` | **矛盾**（コード内 doc vs CLI spec） |
| C2 | core §7 | `optimize_wallpapers` 内で margins の int 変換失敗時 `(0,0,0,0)` に黙ってフォールバック | CLI/GUI は事前に検証して失敗 | **矛盾**（CLI/GUI との厳格さの不一致） |
| C3 | core §4.2 | core の `normalize_background_color` は不正時 `#1E1E1E` にフォールバック。CLI/GUI は `is_background_color_literal` で拒否 | 層によって挙動が異なる | **矛盾** |

### D. embed テキスト

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| D1 | core §4.3 | 行数超過時の切り詰め記号は `" ..."` （スペース+三点）| 末尾 `...` のみ | **矛盾**（細部） |
| D2 | core §4.3 | 描画色は固定 `(235,235,235)` | 色が未記載 | **仕様漏れ** |
| D3 | core §4.3 | `_load_preferred_font` が OS 別 CJK フォント候補を探索。`embed_font` 明示時は存在チェックなしで試行 | `embed_font` 受け取りは記載、探索規則なし | **仕様漏れ** |
| D4 | core §4.3 | 無効 `embed_position` は `resolve_embed_margin_region` が `None` → 描画なし | 4値以外は正規入力外とのみ記載 | **エッジケース未記載** |

### E. 出力・品質

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| E1 | 未記載 | 出力は常に JPEG。`output_path` に拡張子がない場合 `.jpg` を付与 | 出力形式の記載なし | **仕様漏れ** |
| E2 | 未記載 | デフォルトファイル名 `harite_output_{NNNN}.jpg`（連番スキップ方式） | 未記載 | **仕様漏れ** |
| E3 | core §5.2 | `split_composite_for_displays` の save は quality=90 固定（optimize の `quality` パラメータを受けない） | fit 再配置は記載、quality 連動なし | **仕様漏れ** / **矛盾** |
| E4 | core §5.2 | auto-split 呼び出しは `background_color` を渡さない（常に内部デフォルト `#1E1E1E` 系） | optimize と split の背景色が非連動 | **エッジケース未記載** |
| E5 | core §5.2 | split 出力のファイル名は `{composite_stem}_{display_name}.jpg`（例: `harite_slideshow_composite_HDMI-1.jpg`） | Slideshow spec §6.2 は `harite_slideshow_{display_name_safe}.jpg` と規定 | **矛盾**（core 実装 vs slideshow 仕様） |

### F. display.name 空文字

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| F3 | core §5.2 | display 名が空のとき split ファイル名は `display_{x_offset}` だが、mapping の dict キーは空文字 `""` になりうる | `display.name` をキーと記載 | **エッジケース未記載** / 実装バグの可能性 |

---

## 3. CLI（`cli.py`）

### CLI - optimize

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| CLI1 | CLI §4 `two_screen` auto | Typer デフォルト `False` → `resolve_bool_or_auto_option` は CLI 未指定時 `False`（`None` にならない）。`auto` は設定 JSON の `"auto"` 文字列のみ有効 | 未指定 = `auto`、2枚入力+display 情報あり → 自動 two-screen | **矛盾** |
| CLI2 | CLI §4 | `--input` / `-i`、`--settings-file` / `-c`、`--output` / `-o` などの短縮形が存在する | 長形式オプションのみ記載 | **仕様漏れ** |
| CLI3 | CLI §4 | `--output` デフォルトは `Path(".")`。`--background-color` デフォルトは `#1E1E1E`。`--quality` デフォルトは `90` | デフォルト値の記載なし | **仕様漏れ** |
| CLI4 | CLI §4 | 設定ファイルの bool 値は `true/false/1/0/yes/no/on/off` 等を `parse_config_bool` が受理 | bool 解釈規則の記載なし | **仕様漏れ** |
| CLI5 | CLI §4 | `parse_margins` / `parse_display` の失敗が try 外のため Typer デフォルト exit `1`（仕様は `2`）になりうる | 不正パラメータは exit `2` | **矛盾** |
| CLI6 | CLI §4 | 入力3件目が不正（例:存在しないディレクトリ）でも無視して exit 0 | 先頭2件のみ採用とのみ記載 | **エッジケース未記載** |
| CLI7 | CLI §4 | 存在しないファイル指定は CLI では検証なし。core 側が黙ってスキップ → exit 0 になりうる | 入力不正は失敗扱い | **矛盾** |

### CLI - apply

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| CLI8 | CLI §5 | apply 成功メッセージは `Plugin '{plugin}' applied wallpaper: {path}` 形式 | `applied wallpaper` のみ記載 | **矛盾**（詳細フォーマット） |
| CLI9 | CLI §5 | `--auto-split` と `--left-file` 併用時は auto-split が優先（明示ファイルは無視） | 未記載 | **エッジケース未記載** |
| CLI10 | CLI §5 | 未知 plugin 時のメッセージ: `Unknown plugin:` + 利用可能プラグイン一覧 | メッセージ詳細なし | **仕様漏れ** |
| CLI11 | CLI §5 | apply 失敗 exit `3`。CLI テストに apply 失敗ケースがない | exit `3` は記載済みだがテストなし | **テストのみ**（網羅なし） |

### CLI - slideshow

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| CLI12 | CLI §6 | plugin 解決は `Slideshow start:` 出力**後**に実行。未知 plugin でも start 行が出力される | command 開始時に plugin 解決 | **矛盾** |
| CLI13 | CLI §6 | `Slideshow start: input=... images=... interval_sec=... mode=... plugin=...` の詳細フィールド | `Slideshow start` とのみ記載 | **仕様漏れ** |
| CLI14 | CLI §6 | `run_slideshow_cycles` は `while True` の無限ループ。`Slideshow completed` には本番運用で到達しない | bounded run を想定した `Slideshow completed` が仕様にある | **矛盾** |
| CLI15 | CLI §6 | slideshow の apply 失敗は常に exit `0`（`apply` コマンドの exit `3` とは別） | slideshow 失敗時の exit code 未記載 | **仕様漏れ** |
| CLI16 | 未記載 | 画像は直下ファイルのみ対象、拡張子 `.jpg/.jpeg/.png/.bmp`、ソート順で列挙 | 未記載 | **仕様漏れ** |
| CLI17 | CLI §6 | `--mode` 不正時: `--mode must be one of: sequential, random` exit `2` | エラーメッセージ未記載 | **仕様漏れ** |
| CLI18 | CLI §6 | 空ディレクトリ: `no image files found in --input directory` exit `2` | 空ディレクトリのエラー未記載 | **仕様漏れ** |

### CLI - install-desktop-entry

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| CLI19 | CLI §7 | `--output` で任意出力パスが指定可能 | デフォルトパスのみ記載 | **仕様漏れ** |

### CLI - 共通

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| CLI20 | CLI §8 | `--plugin` のデフォルト: `win32→windows`, `darwin→macos`, 他→`linux`、次に registry 先頭、最後 `windows` | plugin デフォルト決定規則の記載なし | **仕様漏れ** |
| CLI21 | CLI §8 | `--version`・subcommand 未指定の動作テストが存在しない | exit `0` と記載あり | **テストのみ**（網羅なし） |

---

## 4. GUI（`main_window.py`, `optimize_controller.py`）

### GUI - スライドショー開始条件

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| GUI1 | GUI §6 | `_can_start_slideshow_now()` は L・R **両方** の srcdir が非空のときのみ `True`。ボタンが無効化される | シングルソースでの start は有効（片側のみで `on_slideshow_start()` 成功） | **矛盾**（UI ゲートが過剰制限） |
| GUI2 | GUI §6 | `_prepare_slideshow_apply()` は plugin のみ検証。`apply_mode` の検証なし | start 時に srcdir/plugin/apply_mode/dual-source を検証すると記載 | **矛盾** |
| GUI3 | GUI §6 | デュアルソース時は `apply_mode` 設定値に関わらず常に `per-monitor-auto-split` で処理 | GUI の apply_mode 設定が slideshow に反映されることを示唆 | **仕様漏れ** |
| GUI4 | 未記載 | `on_slideshow_start()` / `on_slideshow_stop()` は `SlideshowCycleState` L/R をリセットしない。再起動時に sequential インデックスが継続 | 未記載 | **エッジケース未記載** |

### GUI - slideshow 出力表示

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| GUI5 | Slideshow §6.1 GUI surface | `MainWindow.slideshow_output_display` はワークディレクトリを表示（実装済み） | ワークディレクトリ表示 | 一致 |
| GUI6 | Slideshow §6.1 GUI surface | `gtk_runtime_slideshow_ui.py` の `refresh_slideshow_output_label` は `form_state.output_dir`（手動 optimize ディレクトリ）を表示している | ワークディレクトリを表示すべき | **矛盾**（MainWindow モデル vs GTK レイヤー） |
| GUI7 | 未記載 | 初期値 `slideshow_output_display = "Slideshow output: ."` が `_update_slideshow_output_display()` 呼び出し前に一時的に表示されうる | 未記載 | **エッジケース未記載** |

### GUI - R1–R5 実装とスロット名

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| GUI8 | Slideshow §6.2 R2 | `split_composite_for_displays`（core）が生成するファイル名は `{composite_stem}_{name}.jpg`（例: `harite_slideshow_composite_HDMI-1.jpg`） | per-monitor スロットは `harite_slideshow_{display_name_safe}.jpg` | **矛盾**（core 実装 vs spec のスロット名） |
| GUI9 | Slideshow §6.2 R1 | `_cleanup_work_dir_orphans` は `harite_output_*.jpg` のみ対象。`harite_slideshow_*.jpg` のスロット外ファイルは対象外 | R1 は `harite_output_*` とスロット外 `harite_slideshow_*` 両方を対象 | **矛盾** |
| GUI10 | Slideshow §6.2 | R1 クリーンアップはデュアルソース apply 成功時のみ実行。pause 時・失敗時は実行なし | tick 終了ごとに実行 | **矛盾** |
| GUI11 | Slideshow §6.2 | シングルソース成功時、`_set_slideshow_active_generated_files(())` は**以前のトラッキングファイルのみ**削除（ワークディレクトリのグロブなし） | シングルソース成功時はワークディレクトリのスロットファイルを削除 | **矛盾** |
| GUI12 | Slideshow §6.2 | stop 後に `_slideshow_active_generated_files = ()` が設定されるため、次回シングルソース起動時に前のスロットファイルが残存しうる | stop→single-source で残存ファイルが削除されるべき | **矛盾** |
| GUI13 | Slideshow §6.2, §6.3 | 仕様内に「R1–R5 対応する」と「現行実装は過渡状態」という記述が混在 | — | **仕様内矛盾** |

### GUI - デフォルト値・未記載挙動

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| GUI14 | 未記載 | `_default_apply_mode()`: XFCE セッション検出時 → `per-monitor-auto-split`、それ以外 → `single-file` | 未記載 | **仕様漏れ** |
| GUI15 | 未記載 | `_default_plugin_name()`: プラットフォームマップ（`linux`/`windows`/`macos`） | 未記載 | **仕様漏れ** |
| GUI16 | 未記載 | `slideshow_interval_seconds` デフォルト `60` 秒 | 未記載 | **仕様漏れ** |
| GUI17 | 未記載 | インターバル変更はモデルのみ更新（GTK タイマーは再起動しない） | 未記載 | **エッジケース未記載** |
| GUI18 | 未記載 | `_apply_slideshow_selection` で L・R 両方が `"-"` の場合 `(True, None)` を返して apply なし | 未記載 | **エッジケース未記載** |
| GUI19 | 未記載 | `on_slideshow_tick()` を `slideshow_running=False` 時に呼ぶと `False` を返してログのみ | 未記載 | **エッジケース未記載** |

### GUI - embed / マージン

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| GUI20 | GUI §8 | `embed_info` 内部値（`none`/`params`/`free`/`combo`）と UI ラベル（Off / Settings / Text only / Both）のマッピングが未記載 | 内部値の記載なし | **仕様漏れ** |
| GUI21 | GUI §8 | preflight の `status_message` 文言: `margin text does not fit current margin area` | `last_error` 文言のみ記載 | **仕様漏れ** |
| GUI22 | 未記載 | `on_settings_dialog_open` は両方の input path が設定されている場合のみ two-screen を同期 | 片側のみの場合の挙動が未記載 | **エッジケース未記載** |

---

## 5. Plugin（`plugins.py`）

### Plugin - 契約・レジストリ

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| PL1 | plugin §3 | `PluginProtocol.apply(self, path: str)` と型注釈。実行時は `dict` も受け付ける（Linux のみ） | 公開契約は `apply(path_or_map) -> bool` | **矛盾**（Protocol 型定義と実動作） |
| PL2 | plugin §2 | 未知名の `registry.get` は `KeyError("No such plugin: {name}")` | 「registry 解決失敗」のみ記載、例外型・メッセージ未規定 | **仕様漏れ** |
| PL3 | plugin §2 | 登録順は `windows` → `macos` → `linux` | 列挙順の記載なし | **仕様漏れ** |
| PL4 | 未記載 | 各プラグインクラスに `name = "windows"` 等の属性 | 未記載 | **仕様漏れ** |

### Plugin - Windows / macOS

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| PL5 | plugin §4.1 | `SystemParametersInfoW(20, 0, str(p), 3)` の第4引数 `3` = `SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE` | API 名と戻り値の真偽のみ | **仕様漏れ** |
| PL6 | plugin §4.1–4.2 | Windows/macOS とも `Path(path)` の存在確認のみ（`expanduser`/`resolve` なし） | Linux のみ path 正規化を詳述 | **エッジケース未記載**（`~` や相対 path） |
| PL7 | plugin §4.2 | `osascript -e` でパスをダブルクォートに直接埋め込み（`"` や `\` をエスケープしない） | AppleScript 文字列のみ記載 | **エッジケース未記載**（特殊文字を含むパス） |
| PL8 | plugin §4.2 | macOS 非ゼロ終了コードは `False`（ログなし） | 失敗時ログ方針の記載なし | **仕様漏れ** |

### Plugin - Linux xfconf

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| PL9 | plugin §4.3 | `shutil.which("xfconf-query")` が真なら XFCE 経路。PATH 上の存在 = 「利用可能」と同義かは環境依存 | 「利用可能なら」のみ | **エッジケース未記載** |
| PL10 | plugin §4.3 | xfconf 列挙失敗（returncode≠0）→ 候補 `[]` → 単一は後段 fallback、map は即 `False` | 列挙失敗時の挙動未記載 | **仕様漏れ** |
| PL11 | plugin §4.3 | xfconf 単一: 候補全 prop に対して `-s` を実行し、**いずれか1つでも** returncode 0 なら `True`（成功後もループ継続 → 複数 prop 更新しうる） | 成功が出た時点で `True` という記載はあるが、ループ継続は未記載 | **仕様漏れ** |
| PL12 | 未記載 | `gsettings set org.gnome.desktop.background picture-uri file://{path}` の具体コマンド | `gsettings` とのみ記載 | **仕様漏れ** |
| PL13 | 未記載 | `feh --bg-scale {path}` の具体コマンド | `feh` とのみ記載 | **仕様漏れ** |
| PL14 | 未記載 | setter なし時のエラーログ: `"No known wallpaper setter found on PATH"` | エラー返却のみ記載 | **仕様漏れ** |

### Plugin - Linux per-monitor

| # | 仕様節 | 実装の実際 | 仕様の記載 | 区分 |
|---|--------|-----------|-----------|------|
| PL15 | plugin §4.3 | `_name_variants` による略称・展開に加え、`mon_name in prop` の**部分一致**も使用 | 正規化・バリアント中心の説明 | **仕様漏れ** |
| PL16 | 未記載 | 同一解像度の display が複数ある場合、`size_map` は後勝ち | 未記載 | **エッジケース未記載** |
| PL17 | plugin §4.3 map | mapping の**全 key について** xfconf 成功が必要。1台でも失敗すると `False` | 全モニタ成功の要件が未記載 | **テストのみ** |
| PL18 | 未記載 | 1 monitor につき複数の filtered prop を順に試し、最初の成功でその monitor 成功扱い | 未記載 | **仕様漏れ** |
| PL19 | 未記載 | 空 dict `{}` は `success_all = bool({})` で即 `False` | 未記載 | **エッジケース未記載** |
| PL20 | plugin §4.3 | 負のオフセット（例: `-512+0`）を `_extract_position` が受理 | `+X+Y` 形式中心の記載 | **エッジケース未記載**（テスト: `test_plugins_xfconf_position_edgecases.py` で補強） |

---

## 6. 優先度サマリー

### 🔴 高優先度（矛盾・動作不正の可能性）

| # | 内容 | 関連ファイル |
|---|------|-------------|
| 1 | **split ファイル名**: core は `{composite_stem}_{name}.jpg`、Slideshow spec は `harite_slideshow_{name}.jpg` | `core.py`, `harite-slideshow-spec.md` |
| 2 | **GTK `Slideshow output` ラベル**が手動 optimize dir を表示（MainWindow モデルはワークディレクトリを正しく保持） | `gtk_runtime_slideshow_ui.py`, `harite-slideshow-spec.md` |
| 3 | **`can_start_slideshow`** が L・R 両方必須のためシングルソースは UI から起動不可 | `main_window.py`, `harite-gui-spec.md` |
| 4 | **`PluginProtocol` 型**: `str` のみで `dict` を受け付けない | `plugins.py`, `harite-plugin-spec.md` |
| 5 | **CLI `two_screen` auto**: CLI 未指定は `False`（設定の `"auto"` のみ有効）| `cli.py`, `harite-cli-spec.md` |
| 6 | **R1 クリーンアップ範囲**: `harite_output_*` のみ。pause/fail 時実行なし | `main_window.py`, `harite-slideshow-spec.md` |
| 7 | **stop 後→シングルソース起動**でスロットファイルが残存する可能性 | `main_window.py`, `harite-slideshow-spec.md` |

### 🟡 中優先度（仕様漏れ・動作は正しいが文書化が不足）

| # | 内容 |
|---|------|
| 8 | `scaling` 設定キーが効かない（settings モデルに残存） |
| 9 | `_default_apply_mode()` / `_default_plugin_name()` のデフォルト決定規則 |
| 10 | `Slideshow completed` が本番では到達不能 |
| 11 | CLI slideshow `apply` 失敗時の exit code（常に `0`） |
| 12 | embed 描画色 `(235,235,235)` / フォント探索規則 |
| 13 | auto-split quality/background_color が optimize 設定と非連動 |
| 14 | `gsettings` / `feh` の具体コマンド形式 |

### 🟢 低優先度（エッジケース・テスト補強）

| # | 内容 |
|---|------|
| 15 | 0×0 画像・全画像読込失敗時の core 動作 |
| 16 | macOS AppleScript での特殊文字パス |
| 17 | 同一解像度 display 複数時の size_map 後勝ち |
| 18 | `on_slideshow_tick()` を停止中に呼んだ場合の挙動 |
| 19 | `SlideshowCycleState` が再起動時にリセットされない |

---

## 7. 参照ファイル一覧

| 役割 | パス |
|------|------|
| Foundation spec | `docs/specs/harite-foundation-spec.md` |
| Core spec | `docs/specs/core/harite-core-spec.md` |
| CLI spec | `docs/specs/cli/harite-cli-spec.md` |
| GUI spec | `docs/specs/gui/harite-gui-spec.md` |
| Slideshow spec | `docs/specs/slideshow/harite-slideshow-spec.md` |
| Plugin spec | `docs/specs/plugins/harite-plugin-spec.md` |
| MainWindow | `src/harite/gui/views/main_window.py` |
| OptimizeController | `src/harite/gui/controllers/optimize_controller.py` |
| core | `src/harite/core.py` |
| plugins | `src/harite/plugins.py` |
| CLI | `src/harite/cli.py` |
| GTK slideshow UI | `src/harite/gui/adapters/gtk_runtime_slideshow_ui.py` |

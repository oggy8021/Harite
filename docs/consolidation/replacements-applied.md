# Replacements applied

## docs\docs-consolidation-replacements-applied.md

```diff
--- docs\docs-consolidation-replacements-applied.md
+++ docs\docs-consolidation-replacements-applied.md (modified)
@@ -516,8 +516,8 @@
  
  次の手順
  --
--1. 上記手順を実行のうえ結果を共有してください（成功なら次に PR マージの調整を進めます）。
--2. 追加で自動化したい項目（例: `xfconf-query` のプロパティ自動検出、複数モニタの優先設定など）があれば教えてください。必要に応じて tests/ に追加のインテグレーションスクリプトを作成します。
+-1。上記手順を実行のうえ結果を共有してください（成功なら次に PR マージの調整を進めます）。
+-2。追加で自動化したい項目（例: `xfconf-query` のプロパティ自動検出、複数モニタの優先設定など）があれば教えてください。必要に応じて tests/ に追加のインテグレーションスクリプトを作成します。
 +1。上記手順を実行のうえ結果を共有してください（成功なら次に PR マージの調整を進めます）。
 +2。追加で自動化したい項目（例: `xfconf-query` のプロパティ自動検出、複数モニタの優先設定など）があれば教えてください。必要に応じて tests/ に追加のインテグレーションスクリプトを作成します。
  
@@ -534,7 +534,7 @@
  
  ## 例2: デュアルモニタ（左右分割）
  - 入力: `inputs = ['samples/left.jpg', 'samples/right.jpg']`
--- target_resolution: `(3840, 1080)`  # 左:1920x1080, 右:1920x1080
+-- target_resolution: `(3840, 1080)`  # 左:1920x1080、右:1920x1080
 +- target_resolution: `(3840, 1080)`  # 左:1920x1080、右:1920x1080
  - layout: `mosaic`
  - scaling: `fit`
@@ -543,7 +543,7 @@
  
  ## 例3: マージン指定と再現性
  - 入力: ディレクトリ `samples/` を指定して複数画像をランダム選出
--- オプション: `padding=10`, `random_seed=42`
+-- オプション: `padding=10`、`random_seed=42`
 +- オプション: `padding=10`、`random_seed=42`
  - 期待出力:
    - `random_seed=42` による `layout_metadata` は再現可能
@@ -551,23 +551,13 @@
  
  ## メタデータ JSON 例
  {
--  "optimized_files": ["/home/user/.local/share/harite/wallopt20260312-120101.jpg"],
--  "layout_metadata": [
+-  "optimized_files": ["/home/user/.local/share/harite/wallopt20260312-120101.jpg"]、-  "layout_metadata": [
 +  "optimized_files": ["/home/user/.local/share/harite/wallopt20260312-120101.jpg"]、"layout_metadata": [
      {
--      "image_path": "samples/left.jpg",
--      "x": 0,
--      "y": 0,
--      "width": 1920,
--      "height": 1080,
--      "rotation": 0.0,
--      "scale": 1.0,
--      "score": 0.95,
--      "posit": "left"
+-      "image_path": "samples/left.jpg"、-      "x": 0、-      "y": 0、-      "width": 1920、-      "height": 1080、-      "rotation": 0.0、-      "scale": 1.0、-      "score": 0.95、-      "posit": "left"
 +      "image_path": "samples/left.jpg"、"x": 0、"y": 0、"width": 1920、"height": 1080、"rotation": 0.0、"scale": 1.0、"score": 0.95、"posit": "left"
      }
--  ],
--  "summary": {"processing_time_s": 0.42}
+-  ]、-  "summary": {"processing_time_s": 0.42}
 +  ]、"summary": {"processing_time_s": 0.42}
  }
  
@@ -584,9 +574,9 @@
  
  ## 入力（パラメータ）
  - inputs: `list[str | Path]` — 入力画像ファイルのパス一覧、もしくは画像を列挙するディレクトリパス
--- target_resolution: `tuple[int, int]` — 出力画面解像度（幅, 高さ）
--- layout: `str` — レイアウトモード（例: `single`, `grid`, `mosaic`, `cover`）
--- scaling: `str` — リサイズモード（例: `fit`, `fill`, `crop`）
+-- target_resolution: `tuple[int, int]` — 出力画面解像度（幅、高さ）
+-- layout: `str` — レイアウトモード（例: `single`、`grid`、`mosaic`、`cover`）
+-- scaling: `str` — リサイズモード（例: `fit`、`fill`、`crop`）
 +- target_resolution: `tuple[int, int]` — 出力画面解像度（幅、高さ）
 +- layout: `str` — レイアウトモード（例: `single`、`grid`、`mosaic`、`cover`）
 +- scaling: `str` — リサイズモード（例: `fit`、`fill`、`crop`）
@@ -597,9 +587,9 @@
  - 入出力のフォーマットテスト（JSON）を用意する。
  
  ## 次のアクション
--1. 母体プログラムの該当ソース（`wallpaperoptimizer`）を解析し、代表的な入力/出力例を収集する。
--2. 本ファイルを基に `tests/test_core.py` のサンプルケースを作成する。
--3. オーナーに本草案のレビューを依頼し、許容差やレイアウトモードの細部を決定する。
+-1。母体プログラムの該当ソース（`wallpaperoptimizer`）を解析し、代表的な入力/出力例を収集する。
+-2。本ファイルを基に `tests/test_core.py` のサンプルケースを作成する。
+-3。オーナーに本草案のレビューを依頼し、許容差やレイアウトモードの細部を決定する。
 +1。母体プログラムの該当ソース（`wallpaperoptimizer`）を解析し、代表的な入力/出力例を収集する。
 +2。本ファイルを基に `tests/test_core.py` のサンプルケースを作成する。
 +3。オーナーに本草案のレビューを依頼し、許容差やレイアウトモードの細部を決定する。
@@ -618,23 +608,23 @@
  
  - Bounds
    - クラス: `Bounds`
--  - 属性: `start: Point`, `end: Point`, `center: Point`
--  - メソッド: `get_width() -> int`, `get_height() -> int`, `set_width(w: int)`, `set_height(h: int)`, `calc_center()`
+-  - 属性: `start: Point`、`end: Point`、`center: Point`
+-  - メソッド: `get_width() -> int`、`get_height() -> int`、`set_width(w: int)`、`set_height(h: int)`、`calc_center()`
 +  - 属性: `start: Point`、`end: Point`、`center: Point`
 +  - メソッド: `get_width() -> int`、`get_height() -> int`、`set_width(w: int)`、`set_height(h: int)`、`calc_center()`
  
  - Rectangle (Bounds 拡張)
    - クラス: `Rectangle(Bounds)`
    - 属性: `size: Tuple[int,int]`（幅・高さ）
--  - メソッド: `set_size(w:int,h:int)`, `is_square() -> bool`, `is_wide() -> bool`, `is_dual() -> bool`, `contains(other: Rectangle) -> bool`, `contains_plus_margin(other: Rectangle, margin: Tuple[int,int,int,int]) -> bool`
+-  - メソッド: `set_size(w:int,h:int)`、`is_square() -> bool`、`is_wide() -> bool`、`is_dual() -> bool`、`contains(other: Rectangle) -> bool`、`contains_plus_margin(other: Rectangle, margin: Tuple[int,int,int,int]) -> bool`
 +  - メソッド: `set_size(w:int,h:int)`、`is_square() -> bool`、`is_wide() -> bool`、`is_dual() -> bool`、`contains(other: Rectangle) -> bool`、`contains_plus_margin(other: Rectangle, margin: Tuple[int,int,int,int]) -> bool`
    - アスペクト判定は許容誤差を設けつつ整数比で判定する（上流と互換を持たせるため floor ベースの既存ロジックを参照する）。
  
  - ImgFile
    - クラス: `ImgFile`
    - 内部: `image: PIL.Image.Image`（委譲）
--  - メソッド: `from_path(path: str|Path) -> ImgFile`, `create_blank(w:int,h:int,color:str) -> ImgFile`, `resize(w:int,h:int)`, `paste(other: ImgFile, box: Tuple[int,int,int,int])`, `save(path: Path)`
--  - プロパティ: `width`, `height`, `size`
+-  - メソッド: `from_path(path: str|Path) -> ImgFile`、`create_blank(w:int,h:int,color:str) -> ImgFile`、`resize(w:int,h:int)`、`paste(other: ImgFile, box: Tuple[int,int,int,int])`、`save(path: Path)`
+-  - プロパティ: `width`、`height`、`size`
 +  - メソッド: `from_path(path: str|Path) -> ImgFile`、`create_blank(w:int,h:int,color:str) -> ImgFile`、`resize(w:int,h:int)`、`paste(other: ImgFile, box: Tuple[int,int,int,int])`、`save(path: Path)`
 +  - プロパティ: `width`、`height`、`size`
  
@@ -642,15 +632,15 @@
    - クラス: `WorkSpace`
    - 目的: 複数スクリーン（少なくとも左/右）に関するサイズ・中心情報を扱う。
    - コンストラクタ: `WorkSpace.from_sizes(total_w:int,total_h:int, l_display:Optional[Tuple[int,int]]=None, r_display:Optional[Tuple[int,int]]=None)`
--  - 属性: `l_screen: Rectangle`, `r_screen: Rectangle`, `separate: bool`
--  - メソッド: `set_screen_size(l_display:Tuple[int,int], r_display:Tuple[int,int])`, `compare_to_screen() -> bool`, `set_attr_screen_type()`
+-  - 属性: `l_screen: Rectangle`、`r_screen: Rectangle`、`separate: bool`
+-  - メソッド: `set_screen_size(l_display:Tuple[int,int], r_display:Tuple[int,int])`、`compare_to_screen() -> bool`、`set_attr_screen_type()`
 +  - 属性: `l_screen: Rectangle`、`r_screen: Rectangle`、`separate: bool`
 +  - メソッド: `set_screen_size(l_display:Tuple[int,int], r_display:Tuple[int,int])`、`compare_to_screen() -> bool`、`set_attr_screen_type()`
    - 注意: `xdpyinfo` 等の外部コマンド依存は廃し、明示的なサイズ引数を基本とする。
  
  - ChangerDir
    - クラス: `ChangerDir`
--  - メソッド: `from_dir(path: Path)`, `get_imgfile_seq() -> Path`, `get_imgfile_rand() -> Path`
+-  - メソッド: `from_dir(path: Path)`、`get_imgfile_seq() -> Path`、`get_imgfile_rand() -> Path`
 +  - メソッド: `from_dir(path: Path)`、`get_imgfile_seq() -> Path`、`get_imgfile_rand() -> Path`
    - エラー: ディレクトリに画像がなければ `FileCountZeroError` を投げる。
  
@@ -659,8 +649,8 @@
    - 期待: `fit` の場合幅または高さがターゲット内に収まり、`fill` の場合少なくともターゲットを覆う（nw>=target_w or nh>=target_h）
  
  - Two-screen 合成:
--  - 入力: 2 つのダミー画像 (e.g., left.jpg 800x600, right.jpg 600x800)
--  - パラメータ: two_screen=True, l_display=(1920,1080), r_display=(1920,1080), margins=(10,10,5,5), scaling='fit'
+-  - 入力: 2 つのダミー画像 (e.g.、left.jpg 800x600、right.jpg 600x800)
+-  - パラメータ: two_screen=True、l_display=(1920,1080)、r_display=(1920,1080)、margins=(10,10,5,5)、scaling='fit'
 +  - 入力: 2 つのダミー画像 (e.g.、left.jpg 800x600、right.jpg 600x800)
 +  - パラメータ: two_screen=True、l_display=(1920,1080)、r_display=(1920,1080)、margins=(10,10,5,5)、scaling='fit'
    - 期待: `optimize_wallpapers` は 1 つの出力ファイルを生成し、`placements` に length=2、`posit` が `left`/`right`、各 `width`/`height` がそれぞれのスクリーンの有効領域以下であること。
@@ -670,9 +660,9 @@
  - 既存の `src/harite/core.py` の two_screen パッチと合わせる形で API を整備する。まずは仕様にある最小限の振る舞いを満たし、テストを追加してからより複雑な割当ロジックを段階的に追加する。
  
  次の手順
--1. この仕様に基づき `tests/test_core_twoscreen.py` を追加してユニットテストを実装する。  
--2. `src/harite` に `workspace.py`/`imgfile.py`/`changerdir.py` の骨格を追加（必要なら単体ファイルで実装）。  
--3. CI 上でテストを実行し、挙動を確認して実装を調整する。
+-1。この仕様に基づき `tests/test_core_twoscreen.py` を追加してユニットテストを実装する。  
+-2。`src/harite` に `workspace.py`/`imgfile.py`/`changerdir.py` の骨格を追加（必要なら単体ファイルで実装）。  
+-3。CI 上でテストを実行し、挙動を確認して実装を調整する。
 +1。この仕様に基づき `tests/test_core_twoscreen.py` を追加してユニットテストを実装する。  
 +2。`src/harite` に `workspace.py`/`imgfile.py`/`changerdir.py` の骨格を追加（必要なら単体ファイルで実装）。  
 +3。CI 上でテストを実行し、挙動を確認して実装を調整する。
@@ -688,7 +678,7 @@
  - 互換性: 既存の単一 `--file`（従来の合成画像）ワークフローはそのまま動作すること。
  
  用語
--- Display: name (例: "DP-1"), width, height, x_offset, primary: bool
+-- Display: name (例: "DP-1")、width、height、x_offset、primary: bool
 +- Display: name (例: "DP-1")、width、height、x_offset、primary: bool
  - monitor-prop: XFCE のプロパティ名に含まれる monitor 候補（例: `/backdrop/screen0/monitorDP-1/...`）
  
@@ -697,16 +687,16 @@
    - `apply(path_or_map, *, dry_run=True)` を受け、`path_or_map` が dict のときはキーをモニタ識別子（xrandr の `name`）として扱う。
    - 文字列のときは従来の全体適用。
  - XFCE プロパティの割当アルゴリズム
--  1. `xrandr` で得た `Display.name`（例: `DP-1`）をモニタ候補表示名として使用。候補として `monitor{NAME}`（例: `monitorDP-1`）をプロパティ名にマッチさせる。
--  2. `xfconf-query -c xfce4-desktop -l` の出力からプロパティリストを得る（既存処理）。
--  3. 優先ルール:
+-  1。`xrandr` で得た `Display.name`（例: `DP-1`）をモニタ候補表示名として使用。候補として `monitor{NAME}`（例: `monitorDP-1`）をプロパティ名にマッチさせる。
+-  2。`xfconf-query -c xfce4-desktop -l` の出力からプロパティリストを得る（既存処理）。
+-  3。優先ルール:
 +  1。`xrandr` で得た `Display.name`（例: `DP-1`）をモニタ候補表示名として使用。候補として `monitor{NAME}`（例: `monitorDP-1`）をプロパティ名にマッチさせる。
 +  2。`xfconf-query -c xfce4-desktop -l` の出力からプロパティリストを得る（既存処理）。
 +  3。優先ルール:
       - monitor 固有 (/monitor.../) にマッチするプロパティへまず書き込む。
       - 次に workspace ベースの `.../workspaceX/last-image` へ書き込む（各ワークスペースに対して同じファイルを設定）。
       - どのプロパティも見つからない場合は `last-image` / `last-single-image` の一般エントリへフォールバック。
--  4. 書き込み実行:
+-  4。書き込み実行:
 +  4。書き込み実行:
       - `dry_run=True` の場合は実行予定コマンドをログに残すのみ。
       - `dry_run=False` の場合は、モニタ別に見つかったすべてのプロパティに対して `xfconf-query -p <prop> -s <path>` を実行し、個別の成功/失敗をログに残す。最終的には一つでも成功すれば True を返すが、個別失敗は debug/info ログで確認できるようにする。
@@ -715,7 +705,7 @@
  
  テスト設計
  - ユニットテスト
--  - `tests/test_workspace_detect.py` : `xrandr` 出力サンプルをパースし `Display` リストが期待通りであることを確かめる（primary, offsets を含む）。
+-  - `tests/test_workspace_detect.py` : `xrandr` 出力サンプルをパースし `Display` リストが期待通りであることを確かめる（primary、offsets を含む）。
 +  - `tests/test_workspace_detect.py` : `xrandr` 出力サンプルをパースし `Display` リストが期待通りであることを確かめる（primary、offsets を含む）。
    - `tests/test_split_image.py` : ダミー合成画像（左右異なる色）を作成し `auto_split` が左右を正しく切り出すことを検証する。
    - `tests/test_plugins_linux_mapping.py` : モック subprocess の出力を用いて XFCE プロパティを解析、与えたモニタ名に対して正しい `xfconf-query` コマンドが実行されることを検証する（dry-run でコマンド列を確認）。
@@ -724,11 +714,11 @@
  - `apply --per-monitor`（または `apply --file <composite> --auto-split --do-it`）で、linux/xfc e プラグインがモニタ別に `xfconf-query` を呼び出し、両方の画面に意図した画像が設定される（dry-run および実行時ログで確認可能）。
  
  移行計画 / 実装順序（推奨）
--1. `workspace.detect_displays()` の堅牢化（xrandr パースユニットテストを追加）
--2. 画像分割ユーティリティ実装（`harite.core.split_composite_for_displays()`）とテスト
--3. CLI フラグの追加（`apply` に `--auto-split` / `--per-monitor` / `--left-file` / `--right-file`）
--4. Linux プラグインの `apply` 拡張（dict 受け取り対応）とモックベースのテスト
--5. 実機検証（ユーザ）と docs 更新
+-1。`workspace.detect_displays()` の堅牢化（xrandr パースユニットテストを追加）
+-2。画像分割ユーティリティ実装（`harite.core.split_composite_for_displays()`）とテスト
+-3。CLI フラグの追加（`apply` に `--auto-split` / `--per-monitor` / `--left-file` / `--right-file`）
+-4。Linux プラグインの `apply` 拡張（dict 受け取り対応）とモックベースのテスト
+-5。実機検証（ユーザ）と docs 更新
 +1。`workspace.detect_displays()` の堅牢化（xrandr パースユニットテストを追加）
 +2。画像分割ユーティリティ実装（`harite.core.split_composite_for_displays()`）とテスト
 +3。CLI フラグの追加（`apply` に `--auto-split` / `--per-monitor` / `--left-file` / `--right-file`）
@@ -749,7 +739,7 @@
  
  代表的振る舞い（例）
  - Two-screen モード例:
--  - target_resolution=(3840,1080), l_display=(1920,1080), r_display=(1920,1080), margins=(10,10,5,5)
+-  - target_resolution=(3840,1080)、l_display=(1920,1080)、r_display=(1920,1080)、margins=(10,10,5,5)
 +  - target_resolution=(3840,1080)、l_display=(1920,1080)、r_display=(1920,1080)、margins=(10,10,5,5)
    - 左画像は利用可能領域 (1920-10-10,1080-5-5) に合わせて `fit`/`fill` でリサイズされ、左領域の中央付近に配置される。
    - 右画像は右領域に同様に配置され、保存ファイルは 1 枚に合成される。
@@ -758,9 +748,9 @@
  - margins が与えられた場合に貼付け位置が margin を反映していること（単純数値比較）。
  
  次の作業（優先順）
--1. `tests/test_core.py` に Two-screen のユニットテストを追加して CI を通す。テストケースは小さなダミー画像を使用する。  
--2. CLI 側で `--two-screen` / `--margins` オプションを受け取れるよう `src/harite/cli.py` を調整する。  
--3. より詳細な割当ロジック（アスペクト優先、画面タイプ照合）を仕様化し、追加テストを作成する。
+-1。`tests/test_core.py` に Two-screen のユニットテストを追加して CI を通す。テストケースは小さなダミー画像を使用する。  
+-2。CLI 側で `--two-screen` / `--margins` オプションを受け取れるよう `src/harite/cli.py` を調整する。  
+-3。より詳細な割当ロジック（アスペクト優先、画面タイプ照合）を仕様化し、追加テストを作成する。
 +1。`tests/test_core.py` に Two-screen のユニットテストを追加して CI を通す。テストケースは小さなダミー画像を使用する。  
 +2。CLI 側で `--two-screen` / `--margins` オプションを受け取れるよう `src/harite/cli.py` を調整する。  
 +3。より詳細な割当ロジック（アスペクト優先、画面タイプ照合）を仕様化し、追加テストを作成する。
@@ -779,7 +769,7 @@
  - 解析対象ディレクトリ: `wallpaperoptimizer/WallpaperOptimizer`
  
  概要サマリ
--- コードは Python 2 時代に書かれており (print 文, except 構文等)、X11/Xfce/GNOME 環境に深く依存したデスクトップユーティリティ設計である。
+-- コードは Python 2 時代に書かれており (print 文、except 構文等)、X11/Xfce/GNOME 環境に深く依存したデスクトップユーティリティ設計である。
 +- コードは Python 2 時代に書かれており (print 文、except 構文等)、X11/Xfce/GNOME 環境に深く依存したデスクトップユーティリティ設計である。
  - 基盤は `Imaging`（`Bounds`/`Rectangle`/`ImgFile`）と `WorkSpace` で、これらが Core の画像配置ロジックの土台となっている。
  - UI/起動は `Starter`/`StarterFactory`/`Applet`/`AppIndicator`/`Glade` 等が担い、`Command` サブパッケージがデスクトップ環境ごとの壁紙適用を抽象化する。
@@ -788,12 +778,12 @@
    - 問題点: 型チェック・浮動小数の扱いが弱いが単純なユーティリティ。
  
  - `Imaging/Rectangle.py`
--  - `Bounds` を拡張しサイズ管理、アスペクト比判定 (`isWide`, `isSquare`, `isDual`) を提供。
+-  - `Bounds` を拡張しサイズ管理、アスペクト比判定 (`isWide`、`isSquare`、`isDual`) を提供。
 +  - `Bounds` を拡張しサイズ管理、アスペクト比判定 (`isWide`、`isSquare`、`isDual`) を提供。
    - アスペクト判定は床関数と分割で決める古典的ロジック（柔軟性は低い）。
  
  - `Imaging/ImgFile.py`
--  - PIL (`Image`) を内部委譲する `_img` を持ち、`Rectangle` と組み合わせて `reSize`, `paste`, `save` を提供。
+-  - PIL (`Image`) を内部委譲する `_img` を持ち、`Rectangle` と組み合わせて `reSize`、`paste`、`save` を提供。
 +  - PIL (`Image`) を内部委譲する `_img` を持ち、`Rectangle` と組み合わせて `reSize`、`paste`、`save` を提供。
    - 設計上は委譲に見えるが `class ImgFile(Rectangle, Image.Image)` と継承している点が混乱を招く。
  
@@ -802,7 +792,7 @@
    - Option パーサは optparse ベースで拡張アクションを定義しており、GUI/CLI 両対応。
  
  - `Command/*`
--  - 各 WM (xfce, gnome, lxde) に対する壁紙設定コマンドのラッパーを提供。`CommandFactory` で選択。
+-  - 各 WM (xfce、gnome、lxde) に対する壁紙設定コマンドのラッパーを提供。`CommandFactory` で選択。
 +  - 各 WM (xfce、gnome、lxde) に対する壁紙設定コマンドのラッパーを提供。`CommandFactory` で選択。
    - 副作用（実際の壁紙変更）を行う層であり、Harite では CLI あるいはプラグイン的に分離すべき。
  
@@ -810,28 +800,28 @@
    - 画像判定、マージン処理、リサイズ順序、左右バインド、合成、保存、壁紙反映まで一連を担うモノリシック実装。
    - 例外クラス `CoreRuntimeError` を使用し、オプションに応じて daemon/foreground 動作を切り替える。
  
--- UI 周り (`WindowBase`, `Applet`, `AppIndicator`, `Widget/*`, `Glade`)
+-- UI 周り (`WindowBase`、`Applet`、`AppIndicator`、`Widget/*`、`Glade`)
 +- UI 周り (`WindowBase`、`Applet`、`AppIndicator`、`Widget/*`、`Glade`)
    - GTK/Glade ベースの UI 実装。多数の GUI イベントハンドラとウィジェット連携を持つ。
    - Harite は CLI/ライブラリ優先のため UI 層は参照実装として扱い、直接継承は避ける。
  
--- `Starter*`, `StarterFactory`
+-- `Starter*`、`StarterFactory`
 +- `Starter*`、`StarterFactory`
    - 実行時に環境に応じた Starter (GNOME2/GNOME3) を選択して起動する。UI/daemon の入口点。
  
  設計意図と移植リスク
  - 既存設計は「当時のデスクトップ環境（X11/GNOME/Xfce）上でのフル機能実行」を前提としたため、次のリスクがある:
--  - Python2 構文・古い依存（pygtk, xdg, appindicator）で現代環境にそのまま導入不可。
+-  - Python2 構文・古い依存（pygtk、xdg、appindicator）で現代環境にそのまま導入不可。
 +  - Python2 構文・古い依存（pygtk、xdg、appindicator）で現代環境にそのまま導入不可。
    - X11 / WM コマンド依存が強く、クロスプラットフォーム互換性がない。
--  - 密結合（Core が WorkSpace, ChangerDir, Command を直接呼ぶ）によりライブラリ化が難しい。
+-  - 密結合（Core が WorkSpace、ChangerDir、Command を直接呼ぶ）によりライブラリ化が難しい。
 +  - 密結合（Core が WorkSpace、ChangerDir、Command を直接呼ぶ）によりライブラリ化が難しい。
  
  移植方針（推奨）
--1. 設計の抽象化: 上流のドメイン知識（スクリーン分割、アスペクト判定、余白ルール、配置順序）をインタフェースとして抽出する。
--2. 実装は現代的な Python3 + PIL（Pillow） + pure 関数／小クラスで再実装。副作用（壁紙セット等）は CLI プラグイン層に委譲する。
--3. `WorkSpace` は `xdpyinfo` に依存しない API を提供（例: 明示的にスクリーン解像度を渡せるようにする）。
--4. GUI コードは参考実装に留め、Harite 本体はライブラリとしてテスト可能に保つ。
+-1。設計の抽象化: 上流のドメイン知識（スクリーン分割、アスペクト判定、余白ルール、配置順序）をインタフェースとして抽出する。
+-2。実装は現代的な Python3 + PIL（Pillow） + pure 関数／小クラスで再実装。副作用（壁紙セット等）は CLI プラグイン層に委譲する。
+-3。`WorkSpace` は `xdpyinfo` に依存しない API を提供（例: 明示的にスクリーン解像度を渡せるようにする）。
+-4。GUI コードは参考実装に留め、Harite 本体はライブラリとしてテスト可能に保つ。
 +1。設計の抽象化: 上流のドメイン知識（スクリーン分割、アスペクト判定、余白ルール、配置順序）をインタフェースとして抽出する。
 +2。実装は現代的な Python3 + PIL（Pillow） + pure 関数／小クラスで再実装。副作用（壁紙セット等）は CLI プラグイン層に委譲する。
 +3。`WorkSpace` は `xdpyinfo` に依存しない API を提供（例: 明示的にスクリーン解像度を渡せるようにする）。
@@ -842,9 +832,9 @@
  - 副作用（壁紙変更）は明示的オプションで有効化でき、デフォルトでは副作用がないこと。
  
  次の具体作業（A→B→C の流れ）
--1. A (完了): 上流の全主要モジュールを解析しレポート化（本ファイル）。
--2. B (これから): Harite 側で再実装すべき基盤 API（WorkSpace/ImgFile/Bounds/Config/ChangerDir）を仕様化し、テストケースを設計する。
--3. C (後続): 仕様に基づき Harite に実装を追加、ユニットテストと CI を通じて検証する。
+-1。A (完了): 上流の全主要モジュールを解析しレポート化（本ファイル）。
+-2。B (これから): Harite 側で再実装すべき基盤 API（WorkSpace/ImgFile/Bounds/Config/ChangerDir）を仕様化し、テストケースを設計する。
+-3。C (後続): 仕様に基づき Harite に実装を追加、ユニットテストと CI を通じて検証する。
 +1。A (完了): 上流の全主要モジュールを解析しレポート化（本ファイル）。
 +2。B (これから): Harite 側で再実装すべき基盤 API（WorkSpace/ImgFile/Bounds/Config/ChangerDir）を仕様化し、テストケースを設計する。
 +3。C (後続): 仕様に基づき Harite に実装を追加、ユニットテストと CI を通じて検証する。

```

## docs\TODOs_jp.md

```diff
--- docs\TODOs_jp.md
+++ docs\TODOs_jp.md (modified)
@@ -17,19 +17,19 @@
    - コンフリクトはローカルで解消し、チャット内で合意を得てからコミット→push→PR の順で反映する運用とします。
 
 合意済み作業項目（優先度順）
-1. ✅ 完了 — ドキュメント整理（Docs consolidation） — `docs/` の重複・表記ゆれの統合。小さな PR に分割。
-2. ✅ 完了 — `docs` 統合用 PR の作成（レビュー用）。
-3. バックアップとブランチ運用ポリシーのドキュメント化。
-4. ワーキングツリー中心のチャットレビュー運用の導入 — PRは最終合意時のみ作成。チャット内でドラフトをレビューし、確定後にコミット→push→PRを行う運用を標準とする。
-5. `Improve XFCE heuristics` の調査開始（実装は別ブランチ `feature/`）。
-6. テスト強化（Docs 作成→優先ケース追加 → CI 組合せ）
+1。✅ 完了 — ドキュメント整理（Docs consolidation） — `docs/` の重複・表記ゆれの統合。小さな PR に分割。
+2。✅ 完了 — `docs` 統合用 PR の作成（レビュー用）。
+3。バックアップとブランチ運用ポリシーのドキュメント化。
+4。ワーキングツリー中心のチャットレビュー運用の導入 — PRは最終合意時のみ作成。チャット内でドラフトをレビューし、確定後にコミット→push→PRを行う運用を標準とする。
+5。`Improve XFCE heuristics` の調査開始（実装は別ブランチ `feature/`）。
+6。テスト強化（Docs 作成→優先ケース追加 → CI 組合せ）
    - `docs/tests-overview.md` を作成して現状と未カバー領域を明示。
    - 優先ケースに対し parametrize した `pytest` を追加。
    - 必要なら限定的な CI ジョブを追加。
-7. CI: sdist/wheel ビルド job の追加。
-8. リリース準備チェックリスト作成。
-9. ブランチ保護・PR フローのペアセッション（スケジュール）。
-10. 定期的なブランチクリーンアップ（運用ルール化）。
+7。CI: sdist/wheel ビルド job の追加。
+8。リリース準備チェックリスト作成。
+9。ブランチ保護・PR フローのペアセッション（スケジュール）。
+10。定期的なブランチクリーンアップ（運用ルール化）。
 
 短い作業フロー提案
 1.この `docs/TODOs_jp.md` を基点に `docs` の小タスクを洗い出す。

```

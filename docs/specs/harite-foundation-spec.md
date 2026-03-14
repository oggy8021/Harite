# Harite 基盤 API 仕様（WorkSpace / ImgFile / Bounds / ChangerDir）

最終更新: 2026-03-12

目的
- `wallpaperoptimizer` の基盤概念（スクリーン、矩形、画像ラッパ、画像ソース列挙）を Harite 側で安全かつテスト可能に再実装するための仕様。C（実装）段階の設計図となる。

設計方針
- Python 3 (3.11+) を前提とする。Pillow を画像処理に使用する。
- 副作用は最小にし、ライブラリ呼び出しは出力を返すだけとする。壁紙への反映は CLI レイヤで行う。
- 上流の振る舞いは API とテストで再現する（左右スクリーン、マージン、アスペクト判定、2 画像合成）。

型およびクラス設計

- Bounds
  - クラス: `Bounds`
  - 属性: `start: Point`、`end: Point`、`center: Point`
  - メソッド: `get_width() -> int`、`get_height() -> int`、`set_width(w: int)`、`set_height(h: int)`、`calc_center()`

- Rectangle (Bounds 拡張)
  - クラス: `Rectangle(Bounds)`
  - 属性: `size: Tuple[int,int]`（幅・高さ）
  - メソッド: `set_size(w:int,h:int)`、`is_square() -> bool`、`is_wide() -> bool`、`is_dual() -> bool`、`contains(other: Rectangle) -> bool`、`contains_plus_margin(other: Rectangle, margin: Tuple[int,int,int,int]) -> bool`
  - アスペクト判定は許容誤差を設けつつ整数比で判定する（上流と互換を持たせるため floor ベースの既存ロジックを参照する）。

- ImgFile
  - クラス: `ImgFile`
  - 内部: `image: PIL.Image.Image`（委譲）
  - メソッド: `from_path(path: str|Path) -> ImgFile`、`create_blank(w:int,h:int,color:str) -> ImgFile`、`resize(w:int,h:int)`、`paste(other: ImgFile, box: Tuple[int,int,int,int])`、`save(path: Path)`
  - プロパティ: `width`、`height`、`size`

- WorkSpace
  - クラス: `WorkSpace`
  - 目的: 複数スクリーン（少なくとも左/右）に関するサイズ・中心情報を扱う。
  - コンストラクタ: `WorkSpace.from_sizes(total_w:int,total_h:int, l_display:Optional[Tuple[int,int]]=None, r_display:Optional[Tuple[int,int]]=None)`
  - 属性: `l_screen: Rectangle`、`r_screen: Rectangle`、`separate: bool`
  - メソッド: `set_screen_size(l_display:Tuple[int,int], r_display:Tuple[int,int])`、`compare_to_screen() -> bool`、`set_attr_screen_type()`
  - 注意: `xdpyinfo` 等の外部コマンド依存は廃し、明示的なサイズ引数を基本とする。

- ChangerDir
  - クラス: `ChangerDir`
  - メソッド: `from_dir(path: Path)`、`get_imgfile_seq() -> Path`、`get_imgfile_rand() -> Path`
  - エラー: ディレクトリに画像がなければ `FileCountZeroError` を投げる。

拡張オプション（Harite API 用）
- `optimize_wallpapers(..., two_screen: bool=False, l_display:Optional[Tuple[int,int]]=None, r_display:Optional[Tuple[int,int]]=None, margins: Tuple[int,int,int,int]=(0,0,0,0), fixed: bool=False)`
  - two_screen=True の場合、左/右割当を行い `PlacementResult.posit` を `left`/`right` とする。`fixed` が True なら入力順序で固定する。

テストケース設計（必須）
- compute_placement `fit`/`fill`:
  - 入力: 小さな画像（例 200x100）、ターゲット (1920,1080)
  - 期待: `fit` の場合幅または高さがターゲット内に収まり、`fill` の場合少なくともターゲットを覆う（nw>=target_w or nh>=target_h）

- Two-screen 合成:
  - 入力: 2 つのダミー画像 (e.g.、left.jpg 800x600、right.jpg 600x800)
  - パラメータ: two_screen=True、l_display=(1920,1080)、r_display=(1920,1080)、margins=(10,10,5,5)、scaling='fit'
  - 期待: `optimize_wallpapers` は 1 つの出力ファイルを生成し、`placements` に length=2、`posit` が `left`/`right`、各 `width`/`height` がそれぞれのスクリーンの有効領域以下であること。

- ChangerDir:
  - 入力: テスト用ディレクトリに 3 つの小画像を用意
  - 期待: `get_imgfile_seq()` が順次同じ画像をループで返す、`get_imgfile_rand()` がディレクトリの範囲内を返す。

実装ノート
- 既存の `src/harite/core.py` の two_screen パッチと合わせる形で API を整備する。まずは仕様にある最小限の振る舞いを満たし、テストを追加してからより複雑な割当ロジックを段階的に追加する。

次の手順
1.この仕様に基づき `tests/test_core_twoscreen.py` を追加してユニットテストを実装する。  
2.`src/harite` に `workspace.py`/`imgfile.py`/`changerdir.py` の骨格を追加（必要なら単体ファイルで実装）。  
3.CI 上でテストを実行し、挙動を確認して実装を調整する。

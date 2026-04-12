# Monitor-split / WorkSpace 自動検出 設計

最終更新: 2026-03-12

目的

- デュアル／マルチモニタ環境で左右別壁紙を安全に適用するため、Harite 側での自動検出とモニタ分割（monitor-split）機能の設計を確定する。
- 現行 `optimize_wallpapers` の `two_screen` ワークフローと CLI/プラグインを連携させ、`--do-it` 実行時にモニタ単位で適切な設定が行われること。

設計上の原則

- 画像のアスペクト比尊重を最優先とする。無理な引き伸ばしや比率変更は原則行わない。
- 単一作品を断片化して左右両画面へ貼る自動分割はオプション機能とし、ユーザが明示的に選択した場合のみ実行する（`--auto-split` を有効にした時点で意図的選択とみなす）。
- デフォルトの動作は、各モニタに対して個別に最適化された画像を生成して適用する `per_monitor` ワークフローを推奨する。

要件（高レベル）

- ディスプレイ検出: X11 環境で `xrandr` などを用いてモニタ名（例: `DP-1`）、解像度、オフセットを取得する。
- 出力分割: `two_screen` モードまたはユーザ指定により、合成済み画像を左右それぞれのモニタサイズに切り出すか、`optimize_wallpapers` によって最初から左右別ファイルを生成できる。
- プラグイン適用: Linux/XFCE プラグインはモニタ単位でのファイルパス割当を受け取り、対応する `xfconf-query` プロパティへ書き込む。
- 互換性: 既存の単一 `--file`（従来の合成画像）ワークフローはそのまま動作すること。

用語

- Display: name (例: "DP-1")、width、height、x_offset、primary: bool
- monitor-prop: XFCE のプロパティ名に含まれる monitor 候補（例: `/backdrop/screen0/monitorDP-1/...`）

設計（API / データ構造）

- 新規/変更 API
  - `harite.workspace.detect_displays() -> list[Display]`
    - 実行環境を検出し、Display オブジェクトのリストを返す。Linux では `xrandr --verbose` を主に使用し、fallback に `xfconf-query -c xfce4-desktop -l` の解析を行う。
  - `optimize_wallpapers(..., two_screen: bool = False, per_monitor: bool = False) -> tuple[list[Path], list[PlacementResult], Optional[dict[str, Path]]]`
    - 戻り値にオプションで `per_monitor_paths`（モニタ識別子 -> Path）を追加可能にする。`per_monitor=True` の場合、左右それぞれに対応するファイルを返す。
    - 既存の呼び出しとは互換性を保つため、デフォルトは None を返す。
  - `PluginProtocol.apply(self, path_or_map: Union[str, dict], *, dry_run: bool = True) -> bool`
    - 既存の `apply(path: str, *, dry_run: bool)` を拡張して、値が `dict` の場合はモニタ別割当として扱う。
    - 破壊的変更を避けるため、文字列が来た場合は従来通りの単一適用を行う。

CLI 仕様

- 新フラグ（互換性を配慮）
  - `--per-monitor` / `-m` : `apply` コマンドに追加。`--per-monitor` 使用時はプラグインにモニタ別割当を渡す。
  - `--left-file` / `--right-file`: 明示的に左右個別ファイルを指定する（`two_screen` の出力を使わないケース）。
  - `--auto-split` : 単一合成ファイルを自動で左右サイズにスライスして適用する（内部的に `optimize_wallpapers(..., per_monitor=True)` を呼ぶか、単一ファイルから切り出す）。
- 既存 `--do-it` の意味はそのまま（dry-run でない実行）。

プラグイン実装 (Linux/XFCE)

- 入力受け取り
  - `apply(path_or_map, *, dry_run=True)` を受け、`path_or_map` が dict のときはキーをモニタ識別子（xrandr の `name`）として扱う。
  - 文字列のときは従来の全体適用。
- XFCE プロパティの割当アルゴリズム
  1.`xrandr` で得た `Display.name`（例: `DP-1`）をモニタ候補表示名として使用。候補として `monitor{NAME}`（例: `monitorDP-1`）をプロパティ名にマッチさせる。
  2.`xfconf-query -c xfce4-desktop -l` の出力からプロパティリストを得る（既存処理）。
  3.優先ルール:
  - monitor 固有 (/monitor.../) にマッチするプロパティへまず書き込む。
  - 次に workspace ベースの `.../workspaceX/last-image` へ書き込む（各ワークスペースに対して同じファイルを設定）。
  - どのプロパティも見つからない場合は `last-image` / `last-single-image` の一般エントリへフォールバック。
  4.書き込み実行:
  - `dry_run=True` の場合は実行予定コマンドをログに残すのみ。
  - `dry_run=False` の場合は、モニタ別に見つかったすべてのプロパティに対して `xfconf-query -p <prop> -s <path>` を実行し、個別の成功/失敗をログに残す。最終的には一つでも成功すれば True を返すが、個別失敗は debug/info ログで確認できるようにする。

モニタ分割アルゴリズム

- 前提: 2 モニタ（左右）を仮定するが、N モニタ拡張を考慮する。
- 入力:
  - 単一合成画像（幅 = sum(widths)、高さ = max(heights)）または `per_monitor` により別々に生成されたファイル。
- 動作:
  - 自動分割 (`--auto-split`) の場合、`detect_displays()` の順序（x_offset による左→右）で各モニタ解像度分を切り出す。切り出し処理は Pillow を使用し、各モニタ幅・高さに合わせてリサイズ/トリミングする。
  - `two_screen` が `True` かつ `optimize_wallpapers` が左右合成を生成している場合は、合成の左右それぞれを切り出して保存する（命名規則: `out/harite_{hash}_left.jpg` / `..._right.jpg`）。

テスト設計

- ユニットテスト
  - `tests/workspace/test_workspace_detect.py` : `xrandr` 出力サンプルをパースし `Display` リストが期待通りであることを確かめる（primary、offsets を含む）。
  - `tests/core/test_split_image.py` : ダミー合成画像（左右異なる色）を作成し `auto_split` が左右を正しく切り出すことを検証する。
  - `tests/plugins/test_plugins_linux_mapping.py` : モック subprocess の出力を用いて XFCE プロパティを解析、与えたモニタ名に対して正しい `xfconf-query` コマンドが実行されることを検証する（dry-run でコマンド列を確認）。
- 結合テスト（手動）
  - 実機で `--do-it` を指定して左右別ファイルがそれぞれのモニタに反映されることを確認する（ユーザによる検証手順を docs に記載する）。

受け入れ基準

- `detect_displays()` が主要な xrandr 出力パターンを解析できる。
- `--auto-split` による自動分割が左右モニタの解像度に合わせたファイルを生成する。
- `apply --per-monitor`（または `apply --file <composite> --auto-split --do-it`）で、linux/xfc e プラグインがモニタ別に `xfconf-query` を呼び出し、両方の画面に意図した画像が設定される（dry-run および実行時ログで確認可能）。

移行計画 / 実装順序（推奨）
1.`workspace.detect_displays()` の堅牢化（xrandr パースユニットテストを追加）
2.画像分割ユーティリティ実装（`harite.core.split_composite_for_displays()`）とテスト
3.CLI フラグの追加（`apply` に `--auto-split` / `--per-monitor` / `--left-file` / `--right-file`）
4.Linux プラグインの `apply` 拡張（dict 受け取り対応）とモックベースのテスト
5.実機検証（ユーザ）と docs 更新

セキュリティと安全性

- `--do-it` は明示的に指定しない限り何もしない（dry-run）。
- 実行時に外部コマンド（`xfconf-query` 等）を直接実行するため、引数は適切にエスケープし、ログにフルパスを出力して監査可能にする。

ドキュメント

- `docs/xfce-testing.md` を拡張して `--auto-split` / `--per-monitor` の手順と実機検証ガイドを追加する。

---

次のアクション候補

- (A) この設計に基づき実装を開始する
- (B) 設計の不明点を議論・微調整する

設計に問題なければ実装へ移ります。

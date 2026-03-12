# Upstream 完全解析レポート

最終更新: 2026-03-12

目的
- `wallpaperoptimizer/WallpaperOptimizer` 配下の全主要モジュールを解析し、各モジュールの責務・公開 API・設計意図・移植リスクを明確化する。

対象
- 解析対象ディレクトリ: `wallpaperoptimizer/WallpaperOptimizer`

概要サマリ
- コードは Python 2 時代に書かれており (print 文, except 構文等)、X11/Xfce/GNOME 環境に深く依存したデスクトップユーティリティ設計である。
- 基盤は `Imaging`（`Bounds`/`Rectangle`/`ImgFile`）と `WorkSpace` で、これらが Core の画像配置ロジックの土台となっている。
- UI/起動は `Starter`/`StarterFactory`/`Applet`/`AppIndicator`/`Glade` 等が担い、`Command` サブパッケージがデスクトップ環境ごとの壁紙適用を抽象化する。

モジュール別解析（要点）
- `Imaging/Bounds.py`
  - 軽量な Point/Bounds 実装。座標差分、中心計算を提供。
  - 問題点: 型チェック・浮動小数の扱いが弱いが単純なユーティリティ。

- `Imaging/Rectangle.py`
  - `Bounds` を拡張しサイズ管理、アスペクト比判定 (`isWide`, `isSquare`, `isDual`) を提供。
  - アスペクト判定は床関数と分割で決める古典的ロジック（柔軟性は低い）。

- `Imaging/ImgFile.py`
  - PIL (`Image`) を内部委譲する `_img` を持ち、`Rectangle` と組み合わせて `reSize`, `paste`, `save` を提供。
  - 設計上は委譲に見えるが `class ImgFile(Rectangle, Image.Image)` と継承している点が混乱を招く。

- `WorkSpace.py`
  - `xdpyinfo` を呼び出してスクリーン一覧・深度を取得し `lScreen`/`rScreen` を構築。
  - `separate` フラグにより single/dual monitor を判定。スクリーンごとに `displayType` を決める。
  - 問題点: X11 固有、テスト困難。代替として明示的引数でスクリーンを与える API を推奨。

- `Config.py`
  - `.walloptrc` から左右 display 設定・srcdir を読み込む単純パーサ。

- `ChangerDir.py`
  - 指定ディレクトリ内の画像列挙・ランダム/順次取得を提供。IO エラーは例外で報告。

- `OptionsBase.py` / `Options.py`
  - コマンドラインオプションのパースとアクセサ。`margin`（注:綴りは margin）や align/valign を扱う。
  - Option パーサは optparse ベースで拡張アクションを定義しており、GUI/CLI 両対応。

- `Command/*`
  - 各 WM (xfce, gnome, lxde) に対する壁紙設定コマンドのラッパーを提供。`CommandFactory` で選択。
  - 副作用（実際の壁紙変更）を行う層であり、Harite では CLI あるいはプラグイン的に分離すべき。

- `Core.py`
  - 画像判定、マージン処理、リサイズ順序、左右バインド、合成、保存、壁紙反映まで一連を担うモノリシック実装。
  - 例外クラス `CoreRuntimeError` を使用し、オプションに応じて daemon/foreground 動作を切り替える。

- UI 周り (`WindowBase`, `Applet`, `AppIndicator`, `Widget/*`, `Glade`)
  - GTK/Glade ベースの UI 実装。多数の GUI イベントハンドラとウィジェット連携を持つ。
  - Harite は CLI/ライブラリ優先のため UI 層は参照実装として扱い、直接継承は避ける。

- `Starter*`, `StarterFactory`
  - 実行時に環境に応じた Starter (GNOME2/GNOME3) を選択して起動する。UI/daemon の入口点。

設計意図と移植リスク
- 既存設計は「当時のデスクトップ環境（X11/GNOME/Xfce）上でのフル機能実行」を前提としたため、次のリスクがある:
  - Python2 構文・古い依存（pygtk, xdg, appindicator）で現代環境にそのまま導入不可。
  - X11 / WM コマンド依存が強く、クロスプラットフォーム互換性がない。
  - 密結合（Core が WorkSpace, ChangerDir, Command を直接呼ぶ）によりライブラリ化が難しい。

移植方針（推奨）
1. 設計の抽象化: 上流のドメイン知識（スクリーン分割、アスペクト判定、余白ルール、配置順序）をインタフェースとして抽出する。
2. 実装は現代的な Python3 + PIL（Pillow） + pure 関数／小クラスで再実装。副作用（壁紙セット等）は CLI プラグイン層に委譲する。
3. `WorkSpace` は `xdpyinfo` に依存しない API を提供（例: 明示的にスクリーン解像度を渡せるようにする）。
4. GUI コードは参考実装に留め、Harite 本体はライブラリとしてテスト可能に保つ。

受け入れ基準（移植の成功判定）
- Harite の再実装が母体の代表ケース（左右 2 画面、マージンあり、fixed オプションなど）で期待値（配置矩形）とスケールが許容差内で一致すること。
- 副作用（壁紙変更）は明示的オプションで有効化でき、デフォルトでは副作用がないこと。

次の具体作業（A→B→C の流れ）
1. A (完了): 上流の全主要モジュールを解析しレポート化（本ファイル）。
2. B (これから): Harite 側で再実装すべき基盤 API（WorkSpace/ImgFile/Bounds/Config/ChangerDir）を仕様化し、テストケースを設計する。
3. C (後続): 仕様に基づき Harite に実装を追加、ユニットテストと CI を通じて検証する。

付記
- 解析はソース読取ベースでの静的解析です。実行時の挙動（例: xprop の出力バリエーションや外部コマンドの挙動）は実環境での確認を推奨します。

---

作成者: Copilot（解析担当）

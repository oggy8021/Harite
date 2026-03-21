# Upstream Core 機能マッピング

最終更新: 2026-03-12

目的
- 古い母体プログラム `WallpaperOptimizer::Core`（`WallpaperOptimizer/Core.py`）に実装されている主要な機能・振る舞いを解析し、
  Harite 側へどのように移植するかを明文化する。設計意図と受け入れ基準を明示して、実装（パッチ）とテストにつなげる。

対象ファイル
- 母体: `wallpaperoptimizer/WallpaperOptimizer/Core.py`
- Harite: `src/harite/core.py`

要約（高レベル）
- 母体はモノリシックな `Core` クラスで、`WorkSpace`（左右スクリーン情報）、`ImgFile`（画像抽象）、設定ファイル・デーモン運用・壁紙反映コマンド等と密に結びつく。
- Harite はライブラリ/テスト重視の関数ベース実装で副作用を最小化している。現状では母体の細かい配置ルール（左右バインド／余白／優先度など）を再現していない。

母体の重要機能（抜粋）
- マルチスクリーン: `WorkSpace` により `lScreen`/`rScreen` を管理し、左右別の解像度や中心座標で配置を行う。
- 画像タイプ判定: アスペクト比から `wide`/`square`/`dual`/`other` を判定し、表示タイプに応じて左/右優先で割り当てる。
- マージン処理: `LMargin`/`RMargin`/`TopMargin`/`BottomMargin` を用いて、リサイズ許容領域を決定する。
- サイズ調整順序: 幅・高さそれぞれの閾で `setSize`→`reSize` として段階的に縮小し、Screen に収める。
- アライメント: `getLAlign`/`getLValign` に従い、center/right/bottom 等で位置を微調整する。
- 2 画像合成パス: ` _optimizeWallpapers` で左右 2 画像を合成して一枚の壁紙を作る（paste＋左画面オフセット）。
- 壁紙設定: 生成ファイルを保存後、`CommandFactory` を通してデスクトップ環境に反映し古いファイルをクリーンアップする。

Harite 側へのマッピング（設計決定）
- WorkSpace / Two-screen
  - Harite の `optimize_wallpapers` に `two_screen: bool` を追加し、`True` の場合は最初の 2 画像を左/右に割り当てる簡易ワークフローを提供する。
  - オプションで `l_display`/`r_display`（各スクリーンの解像度）を受け取り、母体同様の左右別処理を可能にする。
- マージン
  - `margins` パラメータを導入（`(l,r,top,btm)`）して利用可能領域を計算する。縮小は `scaling` モードに従う。
- 画像タイプ判定とバインド
  - 簡易な `img_type` 判定関数を追加し、`fixed` フラグが有効な場合は入力順序で左右を固定する。より複雑な割当ロジックは後続で追加可能。
- 合成と出力
  - Harite は副作用を抑え、出力ファイルパスと `PlacementResult` を返す。CLI 層で壁紙反映（母体の `_setWall` 相当）をオプションとして実装する。

代表的振る舞い（例）
- Two-screen モード例:
  - target_resolution=(3840,1080)、l_display=(1920,1080)、r_display=(1920,1080)、margins=(10,10,5,5)
  - 左画像は利用可能領域 (1920-10-10,1080-5-5) に合わせて `fit`/`fill` でリサイズされ、左領域の中央付近に配置される。
  - 右画像は右領域に同様に配置され、保存ファイルは 1 枚に合成される。

受け入れ基準（テスト可能に記述）
- `compute_placement()` に `scaling=='fill'`/`'fit'` のケースを追加し、期待幅/高さが ±2 px、scale が ±0.02 以内であることを確認するユニットテストを作成する。
- Two-screen 結果について、左/右の `PlacementResult` が返り、それぞれ `posit` が `left`/`right` であること。
- margins が与えられた場合に貼付け位置が margin を反映していること（単純数値比較）。

次の作業（優先順）
1.`tests/core/test_core.py` に Two-screen のユニットテストを追加して CI を通す。テストケースは小さなダミー画像を使用する。  
2.CLI 側で `--two-screen` / `--margins` オプションを受け取れるよう `src/harite/cli.py` を調整する。  
3.より詳細な割当ロジック（アスペクト優先、画面タイプ照合）を仕様化し、追加テストを作成する。

参照: 母体の実装は `wallpaperoptimizer/WallpaperOptimizer/Core.py` を参照のこと。

---

このファイルはレビュー用ドラフトです。次はユニットテスト追加を行います。

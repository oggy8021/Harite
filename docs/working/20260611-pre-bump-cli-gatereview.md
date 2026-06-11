
# 2026/6/10 - 2026/6/11 CLI再再考メモ

**従属文書** — 親 planning: [20260611-1200-cli-v2-roadmap.md](20260611-1200-cli-v2-roadmap.md)（MAT-19〜24・改修順序の正）

## オープニング

- .venv環境は、削除して作り直した上で実施した
- Q-01営みにより、たしかに `harite-gtk.exe` が提供されなくなったことを確認
- `harite-gui`, `harite-qt` いずれからも起動できた

## 仕様書を再点検

- MAT-14 などといった 開発番号 が居並ぶ。一部書き換えたが大量であるため、網羅的にメンテナンスを事実記載としては不要なはず
- CLI optimize におけるターミナルへの出力 “Placement: ” ついて何を出力しているかの説明がない。harite-cli-spec.md:70 あたりを補強する形がよい。
- 以下の内容らから発生する「仕様書の総点検」

## CLI共通

### harite --help

- `--install-completion`, `--show-completion` の説明がない。何をするコマンドで、標準的に備えるべきインターフェースか、要確認。整理如何によっては廃止する

### optimize --help

- “ `margins` はまず有効領域を決め、その内側で `align` / `valign` が効きます。” 記載について
  - 【MAT-15】にて解析結果がアップデートされたので同記載はずれた、marginsは align系に作用しない認識である。 `margins よりも align/valign が優先されます。` との記載となるか。
- “  `two-screen` は `--l-display` / `--r-display` 併用時に効きが強くなります。”
  - “効きが強くなる” が曖昧。何を言っているのか分からない。削除する。
  - `two-screen` の意味するところが不安定であるため、オプションパラメータとしては廃止 or 見直し方向
    - two-screenの記載説明が、仕様書にない
    - 自動検出下では、ほぼ域内
  - `docs/working/20260611-two-screen-display-params-clarification.md` の整理と合わせて扱う
- `--embed-info=none` は、CLIでは不要。none つまり本オプションを指定しないことであり、わざわざ none と指定するのはおかしいため改める。
- `--embed-info=params` は、`--embed-info=settings` に変更する
  - 意図的拡大 or auto倍率の指定があれば `auto` も出力に加える。表記は `input=x` の後ろに足す。

## CLI / Windows / PowerShell

### Optimize

- Optimizeにてディレクトリを指定 → NOP = No Problem

    ```powershell
    > harite optimize --input ~\OneDrive\画像 -r 7680x2160
    optimize --input does not accept directories: C:\Users\oggy_\OneDrive\画像
    ```

- 出力先指定なしOptimize → NOP

    ```powershell
    > harite optimize --input C:\Users\oggy_\OneDrive\画像\1-140316135950.jpg, C:\Users\oggy_\OneDrive\画像\1-140316140041.jpg -r 7680x2160
    Usage: harite optimize [OPTIONS]
    Try 'harite optimize --help' for help.
    ╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ Got unexpected extra argument(s) (C:\Users\oggy_\OneDrive\画像\1-140316140041.jpg)                                   │
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
    ```

- 出力先指定なしOptimize → OK（二重引用符が必要）

    ```powershell
    > harite optimize --input "C:\Users\oggy_\OneDrive\画像\1-140316135950.jpg, C:\Users\oggy_\OneDrive\画像\1-140316140041.jpg" -r 7680x2160
    Saved: [WindowsPath('harite_output_0001.jpg')]
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316135950.jpg'), x=960, y=540, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='left')
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316140041.jpg'), x=4800, y=540, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='right')
    ```

- 出力先指定あり

    ```powershell
    > harite optimize --input "C:\Users\oggy_\OneDrive\画像\1-140316135950.jpg, C:\Users\oggy_\OneDrive\画像\1-140316140041.jpg" -r 7680x2160 --output C:\Users\oggy_\OneDrive\画像
    Saved: [WindowsPath('C:/Users/oggy_/OneDrive/画像/harite_output_0001.jpg')]
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316135950.jpg'), x=960, y=540, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='left')
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316140041.jpg'), x=4800, y=540, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='right')
    ```

- 解像度変更 半分にする

    ```powershell
    > harite optimize --input "C:\Users\oggy_\OneDrive\画像\1-140316135950.jpg, C:\Users\oggy_\OneDrive\画像\1-140316140041.jpg" -r 7680x2160 --output C:\Users\oggy_\OneDrive\画像
    Saved: [WindowsPath('C:/Users/oggy_/OneDrive/画像/harite_output_0001.jpg')]
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316135950.jpg'), x=960, y=540, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='left')
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316140041.jpg'), x=4800, y=540, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='right')
    ```

- 解像度 1/4にする

    ```powershell
    > harite optimize --input "C:\Users\oggy_\OneDrive\画像\1-140316135950.jpg, C:\Users\oggy_\OneDrive\画像\1-140316140041.jpg" -r 7680x2160 --output C:\Users\oggy_\OneDrive\画像
    Saved: [WindowsPath('C:/Users/oggy_/OneDrive/画像/harite_output_0001.jpg')]
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316135950.jpg'), x=960, y=540, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='left')
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316140041.jpg'), x=4800, y=540, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='right')
    ```

- marginsを設定

    ```powershell
    > harite optimize --input "C:\Users\oggy_\OneDrive\画像\1-140316135950.jpg, C:\Users\oggy_\OneDrive\画像\1-140316140041.jpg" -r 7680x2160 --output C:\Users\oggy_\OneDrive\画像 --margins=200,200,100,100
    Saved: [WindowsPath('C:/Users/oggy_/OneDrive/画像/harite_output_0004.jpg')]
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316135950.jpg'), x=960, y=540, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='left')
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316140041.jpg'), x=4800, y=540, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='right')
    ```

  - Placement の読み方はどこかにあるか。x, y は何の座標？（画像の中心座標か・・Placementのダンプ全般について、具体的仕様書記載がない可能性）

- 単独 align/valign

    ```powershell
    > harite optimize --input "C:\Users\oggy_\OneDrive\画像\1-140316135950.jpg, C:\Users\oggy_\OneDrive\画像\1-140316140041.jpg" -r 7680x2160 --output C:\Users\oggy_\OneDrive\画像 --align right,left  --valign top,top
    Saved: [WindowsPath('C:/Users/oggy_/OneDrive/画像/harite_output_0005.jpg')]
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316135950.jpg'), x=1920, y=0, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='left')
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316140041.jpg'), x=3840, y=0, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='right')
    
    > harite optimize --input "C:\Users\oggy_\OneDrive\画像\1-140316135950.jpg, C:\Users\oggy_\OneDrive\画像\1-140316140041.jpg" -r 7680x2160 --output C:\Users\oggy_\OneDrive\画像 --align right,left  --valign top,bottom
    Saved: [WindowsPath('C:/Users/oggy_/OneDrive/画像/harite_output_0006.jpg')]
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316135950.jpg'), x=1920, y=0, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='left')
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316140041.jpg'), x=3840, y=1080, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='right')
    ```

- margins, align, valign 同時指定

    ```powershell
    > harite optimize --input "C:\Users\oggy_\OneDrive\画像\1-140316135950.jpg, C:\Users\oggy_\OneDrive\画像\1-140316140041.jpg" -r 7680x2160 --output C:\Users\oggy_\OneDrive\画像 --align right,left  --valign top,bottom --margins=100,100,200,200
    Saved: [WindowsPath('C:/Users/oggy_/OneDrive/画像/harite_output_0007.jpg')]
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316135950.jpg'), x=1920, y=0, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='left')
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316140041.jpg'), x=3840, y=1080, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='right')
    ```

- 背景色

    ```powershell
    > harite optimize --input "C:\Users\oggy_\OneDrive\画像\1-140316135950.jpg, C:\Users\oggy_\OneDrive\画像\1-140316140041.jpg" -r 7680x2160 --output C:\Users\oggy_\OneDrive\画像 --align right,left  --valign top,bottom --margins=100,100,200,200 --background-color E0E0E0
    Saved: [WindowsPath('C:/Users/oggy_/OneDrive/画像/harite_output_0008.jpg')]
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316135950.jpg'), x=1920, y=0, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='left')
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316140041.jpg'), x=3840, y=1080, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='right')
    ```

- 埋め込み情報(設定値)

    ```powershell
    > harite optimize --input "C:\Users\oggy_\OneDrive\画像\1-140316135950.jpg, C:\Users\oggy_\OneDrive\画像\1-140316140041.jpg" -r 7680x2160 --output C:\Users\oggy_\OneDrive\画像 --align right,left  --valign top,bottom --margins=100,100,200,200 --background-color E0E0E0 --embed-info params
    Saved: [WindowsPath('C:/Users/oggy_/OneDrive/画像/harite_output_0009.jpg')]
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316135950.jpg'), x=1920, y=0, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='left')
    Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316140041.jpg'), x=3840, y=1080, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='right')
    ```

  - bug: 【MAT-15】結果的にマージンが無いところへ「埋め込み情報」を書けてしまった。画像上に合成してしまっている。 `right-bottom` を指定しているときに、同箇所に重畳する可能性があるときは計算ガードが必要。

    - center,center,center,centerにして実施してみる

        ```powershell
        > harite optimize --input "C:\Users\oggy_\OneDrive\画像\1-140316135950.jpg, C:\Users\oggy_\OneDrive\画像\1-140316140041.jpg" -r 7680x2160 --output C:\Users\oggy_\OneDrive\画像 --align center,center  --valign center,center --margins=100,100,200,200 --background-color E0E0E0 --embed-info params
        Saved: [WindowsPath('C:/Users/oggy_/OneDrive/画像/harite_output_0010.jpg')]
        Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316135950.jpg'), x=960, y=540, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='left')
        Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316140041.jpg'), x=4800, y=540, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='right')
        
        > harite optimize --input "C:\Users\oggy_\OneDrive\画像\1-140316135950.jpg, C:\Users\oggy_\OneDrive\画像\1-140316140041.jpg" -r 7680x2160 --output C:\Users\oggy_\OneDrive\画像 --align center,center  --valign center,center --margins=100,100,200,200 --background-color E0E0E0 --embed-info params
        Saved: [WindowsPath('C:/Users/oggy_/OneDrive/画像/harite_output_0010.jpg')]
        Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316135950.jpg'), x=960, y=540, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='left')
        Placement: PlacementResult(image_path=WindowsPath('C:/Users/oggy_/OneDrive/画像/1-140316140041.jpg'), x=4800, y=540, width=1920, height=1080, rotation=0.0, scale=1.0, score=1.0, posit='right')
        ```

    - 以下のロジックを導入したい

      - W3C基準の輝度計算（最も実用的で、文字が確実に見える手法）

        背景色の上に「黒文字」と「白文字」のどちらを置くべきかを判定する、Webの国際標準（W3C）が定めた最もポピュラーなアルゴリズムです。人間の目は「緑」を最も明るく感じ、「青」を暗く感じるという特性（視覚感受性）を反映した数式を使います。

      - 計算式

        カラーコード（RGB）の各要素を 0∼255 の範囲で取得し、以下のウェイトで乗算して「相対輝度（Y）」を割り出します。
        Y=0.299×R+0.587×G+0.114×B

      - **判定ルール**: 導き出した Y の値が **`128`（中間値）以上** であれば「明るい背景（文字は黒にする）」、**`128` 未満** であれば「暗い背景（文字は白にする）」と自動判定します。

- l-display, r-display
  - こちらも `docs/working/20260611-two-screen-display-params-clarification.md` の導出となったメモ
  - resolutionは、仮想。l/r-displayも仮想じゃね？
    - resolutionは利用解像度。l/r-displayは論理最大解像度
  - two-screenは、wallpaperoptimizerには無い
    - 2枚 + OFF → 1枚の壁紙キャンバスを半分ずつ使うイメージ
    - 2枚 + ON → **デュアルモニタのジオメトリ** に合わせて合成・配置するイメージ
- two-screen
  - --two-screen / --no-two-screen を surface から外す（または非推奨）
    2枚入力 → two-screen 必須（検出失敗はエラー or --l-display/--r-display 必須、半分ずつフォールバック廃止）
    Settings の Off も縮小 or 廃止

### Apply

- Optimize, Applyを統合する。以降、根拠を列挙する。
  - `--plugin` 廃止
    - 自動判定を前提とする。
  - `--file`
    - optimizeで事前生成しているファイルを今一度入力させるのはおかしい。GUIもファイル名の管理は Surface化しておらず、SlideshowもOptimize・Applyの分断もなく動かせている。
  - `left-file, right-file`
    - fileに同じく、さらに分けて入力させる手間を強いるのはナンセンス
    - two-screen, l/r-displayの整理と合わせて余計な手間
  - `auto-split`
    - two-screen, l/r-displayの整理と合わせて余計な手間

### Slideshow

- `--plugin` 廃止
  - 自動判定を前提とする。

- ふつうにSlideshow

    ```powershell
    > harite slideshow --input "G:\マイドライブ\Wallpaper\1920,G:\マイドライブ\Wallpaper\1280" --interval-sec 5
    Slideshow start: input=G:\マイドライブ\Wallpaper\1920,G:\マイドライブ\Wallpaper\1280 images=93 sources=dual interval_sec=5 mode=sequential plugin=windows optimize=yes work_dir=C:\Users\oggy_\OneDrive\画像\Harite\slideshow
    ```

- random

    ```powershell
    > harite slideshow --input "G:\マイドライブ\Wallpaper\1920,G:\マイドライブ\Wallpaper\1280" --interval-sec 5 --mode=random
    Slideshow start: input=G:\マイドライブ\Wallpaper\1920,G:\マイドライブ\Wallpaper\1280 images=93 sources=dual interval_sec=5 mode=random plugin=windows optimize=yes work_dir=C:\Users\oggy_\OneDrive\画像\Harite\slideshow
    ```

- 設定ファイルを読む

    ```powershell
    > harite slideshow --input "G:\マイドライブ\Wallpaper\1920,G:\マイドライブ\Wallpaper\1280" --interval-sec 5 -c "C:\Users\oggy_\AppData\Roaming\harite\harite-settings.json"
    Slideshow start: input=G:\マイドライブ\Wallpaper\1920,G:\マイドライブ\Wallpaper\1280 images=93 sources=dual interval_sec=5 mode=random plugin=windows optimize=yes work_dir=C:\Users\oggy_\OneDrive\画像\Harite\slideshow
    Slideshow interrupted by user
    
    > harite slideshow --input "G:\マイドライブ\Wallpaper\1920,G:\マイドライブ\Wallpaper\1280" -c "C:\Users\oggy_\AppData\Roaming\harite\harite-settings.json"
    Slideshow start: input=G:\マイドライブ\Wallpaper\1920,G:\マイドライブ\Wallpaper\1280 images=93 sources=dual interval_sec=10 mode=random plugin=windows optimize=yes work_dir=C:\Users\oggy_\OneDrive\画像\Harite\slideshow
    Slideshow interrupted by user
    
    e> harite slideshow -c "C:\Users\oggy_\AppData\Roaming\harite\harite-settings.json"
    Slideshow start: input=G:\マイドライブ\Wallpaper\1024,G:\マイドライブ\Wallpaper\1024 images=38 sources=dual interval_sec=10 mode=random plugin=windows optimize=yes work_dir=C:\Users\oggy_\OneDrive\画像\Harite\slideshow
    ```

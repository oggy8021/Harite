# GUI Phase11 2nd Planning

最終更新: 2026-05-16

## 位置づけ

- 本書は [docs/specs/gui/gui-phase11-1st-planning.md](docs/specs/gui/gui-phase11-1st-planning.md) を補う、blocker 起点の補助メモである。
- Phase11 初手実装により tray / indicator 自体は XFCE 実機で成立したが、tray icon の見え方と意匠が暫定のままで、panel 上の視認性に課題が残った。
- したがって本書では、tray icon の asset / motif / state 表現だけを 2nd planning として切り出す。

## 実装到達点

- XFCE 実機で tray 自体は出る。
- `Visible/Invisible` は main window の hide / present を行える。
- `Settings` / `BaseColor` / `About` は main window を強制再表示せず既存 dialog を開ける。
- settings JSON に保存済みの watch srcdir は起動時に current GUI 側へ戻せる。
- `Quit` は成立している。

## 今回見えた問題

- tray icon が panel 上で色的に埋もれやすい。
- 現行実装は `wallpaper.svg` / `pause.svg` を暫定 icon として使っており、planning で決めた `wallopt.png` / `wallopt_off.png` の正本設計と一致していない。
- 「app icon をそのまま流用する」読みでは、XFCE panel 上の 16px / 22px 相当で潰れやすい。
- 暫定 icon の説明が事前共有されておらず、実機確認時に「出ていない」のか「埋もれている」のかの切り分けが遅れた。

## ここで固定すること

### 1. tray icon は app icon の完全流用を正本にしない

- 1st planning では「tray icon は application icon を兼ねてよい」としたが、これは「必ず同一意匠に固定する」という意味ではない。
- XFCE panel 上の視認性を優先し、tray icon には tray 専用の簡略化意匠を許容する。
- したがって app icon と tray icon は、同じ motif family に属していてよいが、同一絵柄である必要はない。

### 2. tray icon は小サイズ専用の単純記号に寄せる

- 16px / 22px 相当で読めることを first target の必須条件に置く。
- 立体感、多色、細線過多、文字依存は避ける。
- panel 背景に埋もれにくい、単色寄りのシルエットを優先する。
- icon 全周には最小限の余白を持たせ、隣接 icon と詰まりすぎないようにする。

### 3. running / stopped の差は色ではなく形でも読めるようにする

- state 差分を色だけに依存しない。
- enabled / running 側は通常シンボル、disabled / stopped 側は欠け、停止記号、slash など形差分で読む。
- したがって `wallopt.png` / `wallopt_off.png` は、単なる色違いではなく形でも区別可能な 2 状態 asset とする。

### 4. source of truth は tray 向け vector design でよい

- Linux/XFCE 初手では、tray 専用意匠の source を SVG で持つ考え方は妥当である。
- ただし runtime で最終的に何形式を使うかは実装基盤事情に従ってよく、Phase11 初手では source SVG と runtime asset 名を混同しない。
- したがって `wallopt` / `wallopt_off` は最終 runtime asset 名として維持しつつ、元デザインは SVG で起こしてよい。

## tray icon の設計原則

### 1. motif

- Harite の tray icon は、「壁紙」「画面」「余白」「切替」のいずれかが極小サイズでも読める motif に寄せる。
- 複雑なロゴ再現より、1 記号で Harite の道具性を示すことを優先する。

### 2. contrast

- dark/light panel の両方で見失いにくいことを優先する。
- 実機で埋もれる場合、最初に見直すのは hue ではなく silhouette と余白である。

### 3. packaging

- tray 用の product icon は [src/harite/gui/resources/README.md](src/harite/gui/resources/README.md) の方針どおり package resource として保持する。
- docs/mock asset 側とは混線させない。

## 初手候補

### 候補 A: frame motif

- 角丸の画面フレームを基本とし、中に 1 本だけ余白や壁紙の区切りを示す。
- off 側は右下欠け、または斜線を足す。
- 長所は「壁紙ツール」らしさが最も素直に伝わること。

### 候補 B: margin motif

- 外枠と内側の余白帯で構成し、「margin / fitting」らしさを出す。
- off 側は帯の一部を落とすか、停止線を加える。
- 長所は Harite 固有の機能性に寄せやすいこと。

### 候補 C: H motif

- `H` を幾何学的に簡略化し、tray 専用の symbol として使う。
- off 側は片側を切るか、中央線を stop 記号に寄せる。
- 長所は単純で潰れにくいことだが、壁紙ツールらしさは弱い。

## 現時点の判断

- Phase11 初手の tray icon は、app icon そのものより「tray 専用簡略版」を正本に置く。
- state 差分は色差だけでなく shape 差分でも読む。
- motif の第一候補は frame motif、次点は margin motif とする。
- `wallopt.png` / `wallopt_off.png` の名前は維持しつつ、source design は SVG で起こしてよい。
- したがって次の作業は、tray icon 2 状態の SVG 案を少数作成し、XFCE 実機で見比べることに置く。

## 次アクション

1. tray 専用 icon の source SVG を 2 状態 2 案程度作る。
2. `wallopt` / `wallopt_off` として package resource に配置する。
3. [src/harite/gui/adapters/tasktray_adapter.py](src/harite/gui/adapters/tasktray_adapter.py) の暫定 `wallpaper.svg` / `pause.svg` 参照を差し替える。
4. XFCE 実機で 16px / 22px 相当の視認性を再確認する。

## 完了条件

- tray icon が「出る」だけでなく、XFCE panel 上で見失いにくいことが説明可能になっている。
- `wallopt` / `wallopt_off` の 2 状態差分が shape でも読める。
- app icon と tray icon の関係が「同 motif family だが tray 専用簡略版を許容する」と説明可能になっている。
- source SVG と runtime asset の関係が整理されている。

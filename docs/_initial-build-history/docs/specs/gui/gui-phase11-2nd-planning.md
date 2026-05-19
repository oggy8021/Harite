# GUI Phase11 2nd Planning

最終更新: 2026-05-16

## 位置づけ

- 本書は [docs/specs/gui/gui-phase11-1st-planning.md](docs/specs/gui/gui-phase11-1st-planning.md) を補う、blocker 起点の補助メモである。
- Phase11 初手実装により tray / indicator 自体は XFCE 実機で成立したが、tray icon の見え方と意匠が暫定のままで、panel 上の視認性に課題が残った。
- したがって本書では、tray icon の asset / motif / state 表現だけを 2nd planning として切り出す。
- application / taskbar / about / main window 側の icon surface は [docs/specs/gui/gui-phase11-3rd-planning.md](docs/specs/gui/gui-phase11-3rd-planning.md) に切り出す。

## 実装到達点

- XFCE 実機で tray 自体は出る。
- `Visible/Invisible` は main window の hide / present を行える。
- `Settings` / `BaseColor` / `About` は main window を強制再表示せず既存 dialog を開ける。
- settings JSON に保存済みの watch srcdir は起動時に current GUI 側へ戻せる。
- `Quit` は成立している。

## 今回見えた問題

- tray icon が panel 上で色的に埋もれやすい。
- 現行実装は `wallpaper.svg` / `pause.svg` を暫定 icon として使っており、今回採る `harite.svg` / `harite_off.svg` の正本設計と一致していない。
- 過去の `wallopt.png` 自体は application icon 候補としては辛うじて残せるが、そのまま正本に据えるには意匠面が弱い。
- 「app icon をそのまま流用する」読みでは、XFCE panel 上の 16px / 22px 相当で潰れやすい。
- 暫定 icon の説明が事前共有されておらず、実機確認時に「出ていない」のか「埋もれている」のかの切り分けが遅れた。

## ここで固定すること

### 1. tray icon は app icon の完全流用を正本にしない

- 1st planning では「tray icon は application icon を兼ねてよい」としたが、これは「必ず同一意匠に固定する」という意味ではない。
- 過去の `wallopt.png` は application icon 候補として保留してよいが、tray icon の正本判断まで拘束しない。
- XFCE panel 上の視認性を優先し、tray icon には tray 専用の簡略化意匠を許容する。
- したがって app icon と tray icon は、同じ motif family に属していてよいが、同一絵柄である必要はない。

### 2. tray icon は小サイズ専用の単純記号に寄せる

- 16px / 22px 相当で読めることを first target の必須条件に置く。
- 立体感、多色、細線過多、文字依存は避ける。
- panel 背景に埋もれにくい、単色寄りのシルエットを優先する。
- icon 全周には最小限の余白を持たせ、隣接 icon と詰まりすぎないようにする。

### 3. running / stopped の差は色ではなく形でも読めるようにする

- state 差分を色だけに依存しない。
- enabled / running 側は base motif のみで読み、disabled / stopped 側は大きい斜線で停止状態を読む。
- 再生 / 一時停止記号の重畳は、単色 small icon では情報量が重くなりやすいため採らない。
- したがって `off` 側は大斜線の shape 差分を primary cue に置く。
- したがって `harite.svg` / `harite_off.svg` は、単なる色違いではなく形でも区別可能な 2 状態 asset とする。

### 4. source of truth は tray 向け vector design でよい

- Linux/XFCE 初手では、tray 専用意匠の source を SVG で持つ考え方は妥当である。
- application icon 候補として残す側も、見た目の古さを引きずらないため SVG への再設計を優先してよい。
- ただし runtime で最終的に何形式を使うかは実装基盤事情に従ってよく、Phase11 初手では source SVG と runtime asset 名を混同しない。
- したがって `harite.svg` / `harite_off.svg` を最終 runtime asset 名に置き、元デザインは SVG で起こしてよい。

## tray icon の設計原則

### 0. 旧 wallopt icon の意味は捨てない

- out 直下の旧 `wallopt.png` / `wallopt_off.png` には、過去の Harite の意図がすでに入っている。
- 2 つの display に対して貼ること、両 corner のめくれで「貼る」感を出すこと、display size が違っても収まる貼り方を提供すること、が元の意味である。
- display size 差を含めたのは、過去に同サイズ display を一度に揃えにくく、順次 replacement していく実利用を反映していたためである。
- したがって SVG 再設計では、旧 png の見た目をそのままなぞる必要はないが、「2 画面」「貼る」「異サイズ混在でも収める」という意味核は落とさない。

### 1. motif

- Harite の tray icon は、「壁紙」「画面」「余白」「切替」のいずれかが極小サイズでも読める motif に寄せる。
- 複雑なロゴ再現より、1 記号で Harite の道具性を示すことを優先する。
- 旧 wallopt icon の由来を踏まえ、tray 側でも 2 画面性や貼り込みのニュアンスを完全には捨てず、極小サイズで読める形に圧縮する。

### 2. contrast

- dark/light panel の両方で見失いにくいことを優先する。
- 実機で埋もれる場合、最初に見直すのは hue ではなく silhouette と余白である。

### 3. packaging

- tray 用の product icon は [src/harite/gui/resources/README.md](src/harite/gui/resources/README.md) の方針どおり package resource として保持する。
- docs/mock asset 側とは混線させない。

## 採用案

### A: frame motif

- 角丸の画面フレームを基本とし、中に 1 本だけ余白や壁紙の区切りを示す。
- 旧 wallopt の 2 display 構図は、大小 2 枠または主副 2 面の差で簡略表現できる。
- on 側は 2 面の重なりを素直に読み、後ろ面の短いバーは左上、手前面の短いバーは右下に置く。
- 手前面が奥面を隠す構図を採り、重なり順を明確にする。
- off 側は大きい斜線を重ね、停止状態を shape 差分で読む。
- 実験 SVG として [out/harite_candidate_a.svg](out/harite_candidate_a.svg) と [out/harite_candidate_a_off.svg](out/harite_candidate_a_off.svg) を採用候補の現在形とする。

## 非採用案

### B: margin motif

- 外枠と内側の余白帯で構成し、「margin / fitting」らしさを出す案として検討した。
- display size が違っても収める、という旧意図との相性はよい。
- ただし 2 面の重なり感そのものは A より弱く、今回の tray icon 正本には採らない。

## 現時点の判断

- Phase11 初手の tray icon は、app icon そのものより「tray 専用簡略版」を正本に置く。
- 過去の `wallopt.png` は application icon 候補としては残すが、tray icon の最終 asset 名は `harite.svg` / `harite_off.svg` へ切り替える。
- state 差分は色差だけでなく shape 差分でも読む。
- on/off は大斜線の有無で区別し、再生 / 一時停止の重畳は入れない。
- 採用 motif は frame motif とする。
- 旧 wallopt icon の「2 画面」「角めくれの貼り込み感」「異サイズ display でも収める」という意味は、SVG 再設計後も motif の判断根拠として継承する。
- `harite.svg` / `harite_off.svg` の名前で source design を SVG から起こしてよい。
- したがって次の作業は、A 採用案を symbolic 風の本命 asset として package resource へ移すことに置く。

## 次アクション

1. A 採用案を白基調の symbolic 風 SVG に整える。
2. `harite.svg` / `harite_off.svg` として package resource に配置する。
3. [src/harite/gui/adapters/tasktray_adapter.py](src/harite/gui/adapters/tasktray_adapter.py) の暫定 `wallpaper.svg` / `pause.svg` 参照を差し替える。
4. XFCE 実機で 16px / 22px 相当の視認性を再確認する。

## 完了条件

- tray icon が「出る」だけでなく、XFCE panel 上で見失いにくいことが説明可能になっている。
- `harite.svg` / `harite_off.svg` の 2 状態差分が shape でも読める。
- on/off の差分が大斜線だけで自然に読める。
- app icon と tray icon の関係が「同 motif family だが tray 専用簡略版を許容する」と説明可能になっている。
- source SVG と runtime asset の関係が整理されている。

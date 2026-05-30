# Harite Plugin 仕様 (Plugin Spec)

最終更新: 2026-05-20

## 1. plugin の責務

- plugin は、core / CLI / GUI から渡された最終適用対象を、各 OS / desktop 環境の壁紙設定へ反映する。
- plugin は、target 解決そのものではなく、受け取った target の適用実行を担当する。
- plugin 名の選択と registry 解決は呼び出し側が行い、plugin は選ばれた後の target 実行面を担う。

plugin が直接の主責務としないもの:

- CLI の option surface
- GUI の状態管理や widget 更新
- apply mode の決定
- monitor map の構成

## 2. registry と plugin 名

- plugin は `plugins.py` 内の registry に登録される。
- 現行の登録名は `windows`, `macos`, `linux` である。
- CLI / GUI は plugin 名から registry を引き、plugin instance を得て `apply(...)` を呼ぶ。

registry の扱い:

- 未知 plugin 名は registry 解決失敗として扱う。
- registry は factory を保持し、`get(name)` のたびに plugin instance を生成する。
- registry の列挙結果は CLI の plugin 候補表示にも使われる。
- registry は plugin instance を共有せず、毎回新しい instance を返す。

## 3. 共通契約

- plugin は `apply(path_or_map) -> bool` の形で呼ばれる。
- 成功時は `True`、失敗時は `False` を返す。
- plugin 例外は呼び出し側で failure / exception 面として扱われる。
- `PluginProtocol` の Python 静的型注釈では `apply(path: str) -> bool` としているが、実行時に Linux plugin は `dict[str, Path]`（monitor map）も受け付ける。この型注釈と実行時契約の乖離は既知であり、注釈の改善は今後の課題とする。

target の種類:

- `single-file` apply では単一画像 path を受け取る。
- per-monitor apply では `{display.name: output_path}` 形式の monitor map を受け取りうる。
- monitor map を受け付けるのは現行では Linux plugin のみである。

target 境界の考え方:

- core は `apply_mode` と display 条件から target を解決するが、その target 種類を各 plugin が受け付けるかは plugin 契約側で決まる。
- したがって `single-file` / `monitor map` のどちらになるかと、Windows / macOS / Linux のどれがその target を実行できるかは別の論点として扱う。
- 呼び出し側は必要に応じて選択済み plugin の capability を事前に見て止めてよいが、最終的な受理境界は `plugin.apply(...)` の契約にある。

monitor map interface:

- per-monitor apply の interface で plugin が受け取る主語は、画像ファイル名そのものではなく `{display.name: output_path}` の key/value 対である。
- key の `display.name` は display 検出で得た論理名であり、Linux では `xrandr --query` 由来の `HDMI-1`, `DP-1`, `eDP-1` などを取りうる。
- value の `output_path` は auto-split で生成された各 display 向け画像 path である。
- plugin 側の per-monitor apply は monitor map の key を基準に候補対応付けを行い、ファイル名文字列そのものを主たる判定根拠にはしない。

## 4. OS ごとの実装差分

### 4.1 Windows plugin

- 単一画像 apply のみを扱う。
- monitor map が渡された場合は失敗する。
- 実適用では `SystemParametersInfoW` を使う。
- 実適用の戻り値は `SystemParametersInfoW(...)` の真偽値をそのまま成功判定に使う。

### 4.2 macOS plugin

- 単一画像 apply のみを扱う。
- monitor map が渡された場合は失敗する。
- 実適用では `osascript` による AppleScript 呼び出しを使う。
- 実適用では `tell application "System Events" to set picture of every desktop to "..."` を組み立てて `osascript -e` へ渡し、終了コード `0` を成功とみなす。

### 4.3 Linux plugin

- 単一画像 apply と monitor map apply の両方を扱う。
- monitor map apply を受け付けること自体が Linux plugin の capability であり、core 側の target 解決規則とは別面である。
- per-monitor apply では、XFCE 系の `xfconf-query` 候補列挙と monitor 名対応付けを使う。
- single-file 実行前には `Path(path).expanduser().resolve()` で path を正規化してから存在確認する。
- この正規化は `~` 展開と絶対 path 化までであり、誤った file 名の補完や推測は行わない。正規化後 path が存在しなければ失敗を返す。
- per-monitor mapping では、各 value を `Path(mon_path).expanduser().resolve()` で正規化してから使う。
- 現行 Linux plugin は per-monitor mapping value の存在確認を事前には行わず、setter 実行系にそのまま渡す。

display 自動検出と候補対応付け:

- Linux の display 検出は `xrandr --query` を解析して行い、`Display(name, width, height, x_offset, y_offset, primary)` の列へ正規化する。
- per-monitor apply では、検出した display 列を `x_offset`, `y_offset`, `name` の順で安定化して扱う。
- auto-split で生成する出力ファイル名は、合成画像の stem に `_{display.name}.jpg` を付ける形が基本であり、`HDMI-1`, `DP-1` などがファイル名へ入る根拠はここにある。
- `display.name` が空なら、出力ファイル名側では `display_{x_offset}` を代替名に使う。
- `xfconf-query -c xfce4-desktop -l` で列挙した候補から、workspace 系、monitor image 系、last-image 系、last-single-image 系の property を抽出する。
- monitor map と `xfconf-query` 候補の対応付けでは、monitor 名の正規化バリアント、monitor index、解像度、位置オフセットを使う。
- 位置対応付けでは、候補 property に含まれる geometry / offset と、検出 display の `x_offset`, `y_offset` の距離を比較して最も近い display を使う。
- 単一の monitor map しかない場合は、上記で決まらないときに monitor property を 1 件だけ拾う pragmatic fallback を持つ。

候補対応付けの計算規則:

- monitor 名の正規化は `_normalize_identifier(...)` で行い、`lower()` したうえで英数字以外を除去する。したがって `HDMI-1` と `hdmi1` は同一視される。
- `_name_variants(...)` はこの正規化名に加え、`displayport -> dp`, `display -> dp`, `edp -> edp` の略称・展開形を足した集合を作る。
- 位置抽出は、まず `WIDTHxHEIGHT+X+Y` 形から `(X, Y)` を読み、見つからなければ `+X+Y` 形を試す。
- 位置対応付けの距離は `dx = display.x_offset - x`, `dy = display.y_offset - y` に対するマンハッタン距離 `abs(dx) + abs(dy)` である。
- この距離が `POS_MATCH_THRESHOLD = 200` 以下の display だけを位置一致候補とみなし、その中で最も近い display を使う。
- `_match_candidates_for_mapping(...)` の探索順は、名前一致、複合 token 一致、index 一致、解像度一致、位置一致、単一 mapping 用 fallback の順である。workspace-level 候補への後退は行わない。
- 単一 mapping fallback では、monitor index を持つ候補を優先し、それも決まらない場合だけ monitor property を 1 件拾う。ただし位置が取れるときは距離が 200px 以下の候補だけを残す。

Linux plugin の適用順:

1. `xfconf-query` が利用可能なら XFCE 候補を試す。
2. 単一画像 apply では `gsettings` を次候補として試す。
3. 単一画像 apply では `feh` を次候補として試す。
4. 既知の setter が見つからなければ失敗する。

- この fallback 順は Linux plugin の実行面に属し、core の apply target 解決規則には含めない。

適用フローの細部:

- Linux plugin は `xfconf-query` を最初に試し、そこで成功が出た時点で `True` を返す。したがって XFCE 候補で成功した場合、後段の `gsettings` / `feh` へは進まない。
- monitor map apply では `gsettings` と `feh` へは進まず、XFCE 候補が成立しない場合はそのまま失敗する。

補足:

- `gsettings` と `feh` は単一画像 apply の fallback 候補であり、monitor map apply には使わない。
- `xfconf-query` の候補対応付けは monitor 名、index、resolution、position のヒューリスティックを使う。
- `xrandr` による display 検出に失敗した場合、Linux plugin の per-monitor apply は候補対応付け根拠を弱めた状態になる。
- Linux plugin は desktop 環境差分を完全抽象化するものではなく、現行では XFCE 系の説明比重が高い。

## 5. 失敗と観測面

- 入力 file が存在しない場合、plugin は失敗を返す。
- 未対応 target 種類が渡された場合、plugin は失敗を返す。
- 外部コマンド失敗や OS API 失敗は、plugin 内で error / exception として記録されうる。

観測面の分離:

- CLI は終了コードと stdout message を主表示とする。
- GUI は status / summary / last_error を主表示とする。
- plugin logger は外部 command や apply failure の補助観測面になる。
- plugin の補助 message は Python logging 側へ流れるため、表示されるかどうかや出力先は logging 設定に依存する。

## 6. 他分冊との境界

- apply target の解決は [docs/specs/core/harite-core-spec.md](docs/specs/core/harite-core-spec.md) が扱う。
- CLI の plugin option と終了コードは [docs/specs/cli/harite-cli-spec.md](docs/specs/cli/harite-cli-spec.md) が扱う。
- GUI からの apply / slideshow 起動導線は [docs/specs/gui/harite-gui-spec.md](docs/specs/gui/harite-gui-spec.md) が扱う。
- slideshow 中の plugin 呼び出しと失敗集計は [docs/specs/slideshow/harite-slideshow-spec.md](docs/specs/slideshow/harite-slideshow-spec.md) が扱う。

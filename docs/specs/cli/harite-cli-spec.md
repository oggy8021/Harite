# Harite CLI 仕様 (CLI Spec)

最終更新: 2026-05-20

## 1. CLI の責務

- Harite の command surface を提供する。
- command ごとの入力検証、設定ファイル読み込み、core / plugin 呼び出し、終了コード決定を行う。

CLI は GUI と異なり、1 回の command 実行を明示的に完結させる操作面である。そのため本分冊では、各 command がどの入力を受け、どの層へ委譲し、どの終了コードで返るかを主に扱う。

## 2. command 一覧

- `optimize`
- `apply`
- `slideshow`
- `install-desktop-entry`

位置づけの違い:

- `optimize` は画像生成を担う主 command である。
- `apply` は既存または生成済み画像の適用を担う。
- `slideshow` は単発 command を継続実行へ拡張する。
- `install-desktop-entry` は Linux/XDG 向け補助 command である。

## 3. CLI シーケンス図 (CLI sequence)

```mermaid
sequenceDiagram
    actor User
    participant CLI as cli.py
    participant SettingsFile as settings_file.py
    participant Core as core/apply/slideshow
    participant Plugin as plugins.py

    User->>CLI: command + options
    CLI->>SettingsFile: 設定ファイルを読む
    SettingsFile-->>CLI: 設定値 dict / error
    CLI->>CLI: 入力値を検証し、最終採用値を解決

    alt optimize
        CLI->>Core: optimize_wallpapers(...)
        Core-->>CLI: saved_files, placements
        CLI-->>User: Saved / Placement messages
    else apply
        CLI->>Core: resolve_apply_settings(...)
        Core-->>CLI: 最終適用対象
        CLI->>Plugin: apply(target, dry_run)
        Plugin-->>CLI: success / failure
        CLI-->>User: apply result
    else slideshow
        CLI->>Core: collect_slideshow_input_images(...)
        CLI->>Core: run_slideshow_cycles(...)
        loop each cycle
            Core-->>CLI: selected image
            CLI->>Plugin: apply(...)
            Plugin-->>CLI: success / failure / exception
            CLI-->>User: Slideshow cycle/result
        end
    end
```

## 4. `optimize`

- 入力画像、表示条件、scaling、margins、align、background_color、embed 系を受け取る。
- `--settings-file` が与えられた場合は設定ファイルを読み、CLI 引数を優先して上書きする。
- 成功時は `Saved:` と `Placement:` を出力する。

主要な流れ:

1. `--settings-file` があれば設定ファイル JSON を読み込む。
2. CLI 引数と設定ファイル値から、各オプションの最終採用値を解決する。
3. `--input` を画像ファイル列として正規化する。
4. display 条件を解決し、最終的な `resolution` を確定する。
5. `optimize_wallpapers(...)` を呼び、出力ファイル一覧と配置結果一覧を得る。
6. 結果を stdout に出力する。

入力値の優先順位と最終採用値:

- ここでいう最終採用値とは、CLI 引数、設定ファイル値、option default を優先順位で重ねたあとに、実際に `optimize_wallpapers(...)` へ渡す値を指す。
- 優先順位は CLI 引数 > 設定ファイル値 > option default である。
- `--input` 未指定時は設定ファイル側の `input` を使えるが、最終的に入力列が空なら終了コード `2` で止める。
- `optimize` の `--input` は画像ファイル列のみを受け付け、directory が渡された場合は明示エラーで終了する。
- `quality`, `embed_info`, `embed_position`, `embed_max_lines`, `background_color` は CLI 側で先に妥当性検証する。

display / two-screen 解決:

- `two_screen` は CLI / 設定ファイルで明示されなければ `auto` 扱いになり、入力画像が 2 枚以上あり、two-screen 用の表示情報を取得できる場合だけ有効化される。
- `resolution`, `l_display`, `r_display` は CLI 引数 > 設定ファイル値 > two-screen 用表示情報から導いた自動値 の順で解決する。
- `two_screen` が自動判定のままで two-screen 用の表示情報を取得できない場合、最終的な two-screen 判定は `False` に戻る。
- `--l-display` / `--r-display` は個別指定できるが、未指定時は two-screen 用表示情報から導いた display size を使う。
- `--margins` は `l,r,top,bottom` の 4 要素文字列として解釈し、省略時は `(0, 0, 0, 0)` を使う。

計算規則の補足:

- `resolve_optimize_display_settings(...)` は、まず空文字を除いた入力列 `cleaned_inputs` を作り、`len(cleaned_inputs) >= 2` のときだけ two-screen 用表示情報取得を試みる。
- `two_screen` が CLI / 設定ファイルで未指定なら `auto` と見なし、最終値は `effective_two_screen = context is not None` で始まる。明示指定がある場合はその bool 値をそのまま使う。
- `resolution`, `l_display`, `r_display` は、値が `None` または `auto` のときだけ未確定扱いに戻し、context が得られていて `effective_two_screen=True` の場合に限って自動補完する。
- 自動補完で使う値は `resolution = "{virtual_w}x{virtual_h}"`, `l_display = "{left_w}x{left_h}"`, `r_display = "{right_w}x{right_h}"` である。
- `two_screen` が自動判定のまま context を得られなかった場合だけ、最後に `effective_two_screen=False` へ戻す。`resolution` が最後まで未確定なら CLI はエラー終了する。

主な失敗条件:

- 設定ファイル読み込み失敗
- 画像入力不正
- resolution / display 条件不正
- background color や embed 系 option 不正

## 5. `apply`

- plugin を解決し、`single-file` または per-monitor target を適用する。
- CLI では dry-run を既定とし、実適用したい場合だけ --do-it を指定する。
- CLI は最終的に plugin へ `dry_run=not --do-it` を渡す。

補足:

- GUI には `--do-it` / `dry-run` という同名オプションは存在しない。そのため GUI の apply / slideshow は、CLI とは別の操作面として説明する。
- dry-run 時の「副作用を起こさないこと」は plugin 側の契約でもある。plugin は `dry_run=True` のとき外部コマンドや OS 設定変更を実行しない。

apply mode の決定順:

1. `--auto-split` があれば `per-monitor-auto-split`
2. `--left-file` または `--right-file` があれば `per-monitor-explicit`
3. それ以外は `single-file`

補足:

- `--per-monitor` 単独では実行できず、`--left-file` / `--right-file` か `--auto-split` を伴う必要がある。
- plugin 解決は command 先頭で行い、未知 plugin は終了コード `2` で止める。
- `resolve_apply_settings(...)` により最終適用対象を構成してから plugin へ渡す。
- plugin が `False` を返した場合は終了コード `3` で扱う。
- CLI 実装は `resolve_apply_settings(...)` に `output_dir=Path(".")` を渡しているため、`--auto-split` 時の split 出力先既定値は current working directory である。

## 6. `slideshow`

- command 名も `slideshow` とし、public surface の機能名と揃える。
- 入力 directory を監視ではなくスライドショー実行対象として扱う。
- `mode`, `interval_sec`, `plugin`, `dry_run` を扱う。

slideshow command の意味:

- filesystem event を待つ監視ではなく、入力 directory から画像一覧を集め、一定間隔で次画像を選んで apply する。
- `dry_run` では plugin を解決せず、サイクルの進行だけを確認できる。
- `--do-it` 時だけ plugin 解決と実 apply を行う。

CLI surface の整理方針:

- `mode` は CLI / helper だけの概念に留めず、GUI 側にも user-visible な選択面を持つ前提で扱う。
- `log_level` は option 名と実体のずれが大きいため、public surface から外し、固定の実行メッセージ方針へ寄せる。

`mode` と実行メッセージ:

- `mode=sequential` は index を進めながら順番に選ぶ。
- `mode=random` は可能なら直前画像を避けて選ぶ。
- `log_level` option は持たず、CLI は固定の実行メッセージ方針を採る。
- 固定方針は旧 `normal` 相当とし、失敗がない間は `Slideshow start` と `Slideshow completed` を中心に出す。
- `Slideshow cycle=...` は常時出さず、実 apply 中に `apply_failed` または `apply_error` が発生したサイクルでだけ出す。
- したがって dry-run や成功のみの実 apply では cycle 行を出さない。

slideshow helper の計算規則:

- `select_next_image(...)` の `sequential` は `selected_index = index % len(images)` で選び、次 state の `index` は `index + 1` になる。
- `random` では、候補数が 2 件以上かつ `previous_selected` が現在候補に含まれている場合だけ、`candidates = [img for img in images if img != previous_selected]` を作ってその中から 1 件選ぶ。
- `random` では `index` を進めず、そのまま保持する。したがって現行 random の状態更新で効いているのは `previous_selected` と `completed` である。
- `run_slideshow_cycle(...)` は、選ばれた画像を `previous_selected` に入れ、`completed = state.completed + 1` とした新 state を返す。
- `run_slideshow_cycles(...)` は各サイクル後に `on_cycle(selected, state.completed - 1)` を呼ぶため、callback 側へ渡る cycle 番号は 0 始まりである。
- sleep は継続実行を続ける場合にだけ `sleep_fn(interval_sec)` を呼ぶ。
- ただし CLI の user-facing `Slideshow cycle=` 表示は callback 値をそのまま出さず、`cycle_index + 1` を使う。したがって内部 callback は 0 始まり、stdout 表示は 1 始まりである。
- dry-run の各サイクルでは `dry_run_cycles` を 1 件増やすが、固定方針では `Slideshow cycle=...` は出さない。
- 実 apply では `apply_ok` は成功時だけ、`apply_failed` は plugin が `False` を返したときだけ、`apply_error` は plugin 例外時だけ増える。`apply_failed_total = apply_failed + apply_error` は completed 行でだけ計算する。

出力先:

- 実行メッセージの出力先は CLI の `typer.echo(...)` による標準出力 (stdout) である。
- 現行 CLI `slideshow` command には専用保存先や履歴ファイル出力はない。
- plugin 側の logger は別系統であり、CLI の固定実行メッセージ方針とは分けて考える。

## 7. `install-desktop-entry`

- Linux/XDG 限定 command とする。
- user-local の `.desktop` launcher を生成する。

launcher 生成の実際:

- 既定の出力先は XDG data home 配下の `applications/harite.desktop` である。
- `Exec` は実行中 Python を使った `-m harite.gui.app` 形式で書かれる。
- `Icon` は package resource の product icon から解決し、優先順は `harite_app.svg`、`harite.svg`、最後に icon theme 名 `harite` である。

Windows / macOS ではサポート外であり、終了コード `2` で終了する。Linux でも既存ファイル衝突は `--force` の有無で扱いが変わる。

## 8. 共通オプションと終了コード

- 主な終了コード:
  - `0`: 正常終了
    - `2`: 入力不正、設定ファイル不正、plugin 解決失敗、サポート外
  - `3`: apply 失敗

共通的な振る舞い:

- `--version` は callback で処理し、値表示後に正常終了する。
- subcommand 未指定時は簡易ヘルプ文言を出して正常終了する。
- Typer / Click の parse error は framework 側の終了に委ねるが、業務上の入力不正は Harite 側で `2` に寄せる。

## 9. メッセージと重要度

- `info`: 実行開始、完了、dry-run summary
- `error`: validation error, unknown plugin, apply failed
- Harite 固有の stdout 実行メッセージは、言語に応じた自然な user-facing 表現を使う。
- 英語表記では通常の文やラベルとして読める形を優先し、全部大文字の強い prefix は使わない。
- slideshow では `Slideshow start`, `Slideshow cycle`, `Slideshow completed` を中心に実行メッセージを出す

command ごとの代表メッセージ:

- `optimize`: `Saved:` と `Placement:`
- `apply`: `applied wallpaper` または `failed to apply wallpaper`
- `slideshow`: `Slideshow start`, `Slideshow interrupted by user`, `Slideshow completed`
- `install-desktop-entry`: `Installed desktop entry:`

`slideshow` の `Slideshow completed` では、dry-run 時は `dry_run_cycles`、実 apply 時は `apply_ok`, `apply_failed`, `apply_error`, `apply_failed_total` を出してサイクルごとの結果を要約する。

重要度の見方:

- 明示的な prefix を持たない message もあるが、終了コードと併せて判断する。
- slideshow の詳細行は通常の info 相当、plugin 例外や apply failure は error 相当として読む。
- plugin logger の出力有無や出力先は Python logging 側の設定に依存するため、CLI `slideshow` command の stdout 実行メッセージとは分けて考える。

## 10. core / GUI / packaging との境界

- core 挙動の正本は [docs/specs/core/harite-core-spec.md](docs/specs/core/harite-core-spec.md)
- GUI 側の状態や tray は [docs/specs/gui/harite-gui-spec.md](docs/specs/gui/harite-gui-spec.md)

境界整理:

- CLI は option surface と終了コードを決めるが、最適化や apply target 解決の業務規則自体は core に置く。
- `slideshow` command は CLI 面の実行メッセージと plugin 呼び出しを持つが、最小ループの挙動は slideshow helper に委譲する。
- desktop entry 生成は packaging / launcher 面にまたがるが、CLI からの起動導線としてここに置く。

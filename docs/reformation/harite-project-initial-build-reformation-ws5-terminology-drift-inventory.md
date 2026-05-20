# Harite Project Initial Build Reformation WS5 Terminology Drift Inventory

最終更新: 2026-05-20

## 位置づけ

- 本書は [docs/reformation/harite-project-initial-build-reformation-ws5-internal-issues-overview.md](docs/reformation/harite-project-initial-build-reformation-ws5-internal-issues-overview.md) を受ける WS5 の子文書である。
- 対象は canonical spec だけに限らず、README、現行 docs、src 実装、tests を含む現行 repo 全域の用語ぶれである。
- ここでは、現状の表現差、責務境界による説明差、未整理の呼び方を横断一覧として固定する。
- WS4 側では、この一覧の元になる抽出と事実記載までを扱い、ここで見えた論点に対して「直す / 直さない」を決める working は WS5 で扱う。
- 優先度付け、rename 方針、実働の着手順は本書では確定せず、WS5 planning で扱う。

## 調査範囲

- canonical spec: [docs/specs/harite-foundation-spec.md](docs/specs/harite-foundation-spec.md) を起点とする harite-xxx-spec.md 群
- README: [README.md](README.md), [README_en.md](README_en.md)
- 現行 docs: reformation, tests overview, release / dev 補助文書を含む docs 配下
- source: [src/harite/config.py](src/harite/config.py), [src/harite/preferences.py](src/harite/preferences.py), [src/harite/watch.py](src/harite/watch.py), [src/harite/apply_settings.py](src/harite/apply_settings.py), [src/harite/cli.py](src/harite/cli.py), [src/harite/plugins.py](src/harite/plugins.py), [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) など
- tests: CLI / watch / plugins / GUI / core の現行テスト群
- ただし履歴証跡は補助参照に留め、正系語の判定根拠には現行面を優先する

## canonical spec 対象分冊

- [docs/specs/harite-foundation-spec.md](docs/specs/harite-foundation-spec.md)
- [docs/specs/core/harite-core-spec.md](docs/specs/core/harite-core-spec.md)
- [docs/specs/cli/harite-cli-spec.md](docs/specs/cli/harite-cli-spec.md)
- [docs/specs/watch/harite-watch-spec.md](docs/specs/watch/harite-watch-spec.md)
- [docs/specs/plugins/harite-plugin-spec.md](docs/specs/plugins/harite-plugin-spec.md)
- [docs/specs/gui/harite-gui-spec.md](docs/specs/gui/harite-gui-spec.md)

## 読み方

- 現在の表現: 現行 spec 群に現れている語をそのまま並べる。
- ずれの型: 単なる言い換えなのか、surface ごとの責務差を含むのか、命名自体に違和感があるのかを分ける。
- 扱い候補: いま決め打ちせず、次の planning で何を判定すべきかを示す。

## WS4 / WS5 の境界

- WS4 は、現行 repo を読み、用語ぶれや責務ずれを抽出し、事実として記述するところまでを担当する。
- WS4 では、抽出した論点を見てその場で rename や wording 修正へ進まない。
- WS5 は、本書を input にして、どの論点を直すか、併存を許容するか、rename まで踏み込むかを working として扱う。
- したがって本書は、修正文案の置き場ではなく、後続 working の判断材料を過不足なく残すための inventory として使う。

## 一覧

| ID | 論点 | 現在の表現 | 主な出現箇所 | ずれの型 | 扱い候補 |
| --- | --- | --- | --- | --- | --- |
| T01 | 設定系の呼称 | 設定, 設定ファイル, settings, settings file, config, preferences, harite-preferences.json | [foundation](docs/specs/harite-foundation-spec.md#L98), [foundation](docs/specs/harite-foundation-spec.md#L140), [core](docs/specs/core/harite-core-spec.md#L201), [core](docs/specs/core/harite-core-spec.md#L257), [cli](docs/specs/cli/harite-cli-spec.md#L68), [gui](docs/specs/gui/harite-gui-spec.md#L76) | 日本語用語, CLI/module 名, 物理ファイル名が混在している | 文書上の正系語と媒体名を分離して整理する。特に config と 設定 を同義扱いで残すかを判定対象にする |
| T02 | watch の実体名 | watch, 周期実行, 周期的に選択, 選択ループ, changer 的継続実行 | [foundation](docs/specs/harite-foundation-spec.md#L94), [cli](docs/specs/cli/harite-cli-spec.md#L149), [watch](docs/specs/watch/harite-watch-spec.md#L55), [core](docs/specs/core/harite-core-spec.md#L36) | command 名と実際の挙動説明がずれている | rename 論点として維持しつつ、正本側では「filesystem watch ではない」を共通注記に寄せる |
| T03 | 時間間隔と 1 回分処理の単位 | interval, interval_sec, interval_seconds, 周期, cycle, サイクル | [core](docs/specs/core/harite-core-spec.md#L36), [cli](docs/specs/cli/harite-cli-spec.md#L150), [cli](docs/specs/cli/harite-cli-spec.md#L175), [watch](docs/specs/watch/harite-watch-spec.md#L66), [watch](docs/specs/watch/harite-watch-spec.md#L163) | 時間と回数の単位語が同じ段落内で交差している | 時間は interval 系、1 回分処理は サイクル など、軸ごとの固定語を次段で決める |
| T04 | watch 出力と logging の呼称 | log_level, stdout message, WATCH summary, plugin logger, logging, status, message history | [cli](docs/specs/cli/harite-cli-spec.md#L164), [cli](docs/specs/cli/harite-cli-spec.md#L181), [watch](docs/specs/watch/harite-watch-spec.md#L140), [gui](docs/specs/gui/harite-gui-spec.md#L228), [plugins](docs/specs/plugins/harite-plugin-spec.md#L138), [core](docs/specs/core/harite-core-spec.md#L271) | 同じ log 系語で別観測面を指している | 観測面ごとに語彙を固定する。CLI は stdout summary、GUI は status と message history、plugin は logger を正候補として比較する |
| T05 | apply 側の対象名 | apply target, 最終適用対象, target, monitor map, per-monitor mapping | [foundation](docs/specs/harite-foundation-spec.md#L100), [core](docs/specs/core/harite-core-spec.md#L156), [cli](docs/specs/cli/harite-cli-spec.md#L143), [plugins](docs/specs/plugins/harite-plugin-spec.md#L40), [plugins](docs/specs/plugins/harite-plugin-spec.md#L143) | 上位概念と Linux plugin 固有の受け口名が混在している | 上位概念を final apply target などで固定し、 monitor map は Linux per-monitor 受け口の下位語として分離する |
| T06 | GUI watch 表示名 | watch current, output display, watch summary, status, last_error, message history | [gui](docs/specs/gui/harite-gui-spec.md#L225), [watch](docs/specs/watch/harite-watch-spec.md#L107), [watch](docs/specs/watch/harite-watch-spec.md#L142), [gui](docs/specs/gui/harite-gui-spec.md#L235) | GUI 面の user-facing 表示名と内部状態名が混在している | user-facing label と内部 state key を分けて一覧化する。用語統一だけでなく表示責務も整理対象にする |
| T07 | 設定保存と画像保存の語 | settings save, load, apply, save, optimize 結果の出力先 | [foundation](docs/specs/harite-foundation-spec.md#L98), [foundation](docs/specs/harite-foundation-spec.md#L103), [gui](docs/specs/gui/harite-gui-spec.md#L77), [cli](docs/specs/cli/harite-cli-spec.md#L78) | save が設定保存と画像書き出しの両方に使われうる | 設定保存は settings save、画像書き出しは output save など責務境界で言い分ける候補として維持する |
| T08 | preferences 系クラス名と文書語 | OptimizePreferences, ApplyPreferences, WatchPreferences, AppPreferences, 設定モデル, preferences | [core](docs/specs/core/harite-core-spec.md#L30), [foundation](docs/specs/harite-foundation-spec.md#L141), [gui](docs/specs/gui/harite-gui-spec.md#L89) | 実装クラス名が preference 系、本文は設定系で説明している | クラス名はそのまま残し、本文では設定モデルを主語にするかを判定対象にする |
| T09 | source の settings / config / preferences 三層 | resolve_apply_settings, load_config, save_config, AppPreferences, on_apply_settings, on_load_settings_file | [config.py](src/harite/config.py#L17), [preferences.py](src/harite/preferences.py#L125), [apply_settings.py](src/harite/apply_settings.py#L18), [main_window.py](src/harite/gui/views/main_window.py#L788), [main_window.py](src/harite/gui/views/main_window.py#L909) | module 名、関数名、GUI handler 名がそれぞれ別語を主語にしている | spec だけでなく source 命名も棚卸対象に入れる。文書語だけ揃えて済むのか、命名整理まで踏み込むのかを WS5 で判定する |
| T10 | source / tests の watch 単位語 | WatchCycleState, run_watch_cycle, run_watch_cycles, interval_sec, interval_seconds, cycle_phase | [watch.py](src/harite/watch.py#L15), [watch.py](src/harite/watch.py#L88), [cli.py](src/harite/cli.py#L471), [preferences.py](src/harite/preferences.py#L104), [main_window.py](src/harite/gui/views/main_window.py#L1117), [test_watch_runner.py](tests/watch/test_watch_runner.py#L119) | source は cycle 系が強く、GUI state では phase や interval_seconds も混ざる | doc 側の統一だけでは不十分で、source 上の境界語も追跡対象として保持する |
| T11 | source / spec / tests の観測面語 | logger, logging, log_level, status_message, last_error, WATCH ..., message history | [plugins.py](src/harite/plugins.py#L16), [cli.py](src/harite/cli.py#L504), [main_window.py](src/harite/gui/views/main_window.py#L501), [test_phase4_regression.py](tests/gui/test_phase4_regression.py#L48), [test_plugins_linux_mapping.py](tests/plugins/test_plugins_linux_mapping.py#L8) | source は logger と status field、CLI は WATCH 行、tests は caplog や status assert で観測している | 実働では UI 表示語と内部観測語の分離方針を先に決め、その後 rename 範囲を見積もる |
| T12 | mapping / monitor map の実装語 | mapping, per-monitor mapping, EffectiveApplySettings, resolve_apply_settings, plugin.apply(mapping, ...) | [apply_settings.py](src/harite/apply_settings.py#L18), [cli.py](src/harite/cli.py#L437), [plugins.py](src/harite/plugins.py#L375), [test_apply_settings.py](tests/test_apply_settings.py#L23), [test_plugins_xfconf.py](tests/plugins/test_plugins_xfconf.py#L41) | spec は apply target / monitor map、source と tests は mapping が優勢 | Linux plugin 層の実装語を monitor map に寄せるのか、上位 spec を mapping まで許容するのかを WS5 判定対象にする |

## spec 外 surface の補足

- source では GUI handler 名に settings が強く、永続化 I/O には config、論理モデルには preferences が残っている。
- tests でも `plugin.apply(mapping, ...)` や `test_run_watch_cycles_*` のように、実装語をそのまま主語にした命名が広く使われている。
- README 現行面は語彙の密度が薄く、現時点では大きな用語ぶれの主戦場ではない。

## 途中所見

### 1. 強い不一致として先に扱う候補

- T01 設定系の呼称
- T03 時間間隔と 1 回分処理の単位
- T04 watch 出力と logging の呼称
- T05 apply 側の対象名

これらは単なる言い換えに留まらず、help、実装 module 名、user-facing 表示、分冊間責務の境界にまたがっている。

- 全域に広げると、T01, T03, T04, T05 に加えて T09, T10, T11, T12 も source / tests 側の実働論点として無視できない。

### 2. 責務境界での併存を認めうる候補

- T06 GUI watch 表示名
- T07 設定保存と画像保存の語
- T08 preferences 系クラス名と文書語

これらは完全統一よりも、内部名と user-facing 名の分離で説明した方が自然な可能性がある。

### 3. rename 論点と密接な候補

- T02 watch の実体名
- T04 watch 出力と logging の呼称

この 2 件は用語ぶれ一覧に留まらず、WS5 の rename / cleanup planning と直結する。

### 4. 全域調査として見えた境界

- spec は説明責務の違いから意図的併存の余地がある。
- source は module 名と handler 名の履歴が残っており、settings / config / preferences の三層が共存している。
- tests は実装語を強く反映するため、将来 rename するなら追従コストの見積もり対象になる。

## 次段で決めること

1. 文書の正系語を日本語中心で置くのか、config など実装寄り語を立てるのか。
2. watch 系では「時間間隔」と「1 回分処理」の語をどう固定するか。
3. log 系では観測面ごとに何を主語として残すか。
4. apply target と monitor map の上下関係をどこまで本文で固定するか。
5. source / tests の命名まで rename 対象に含めるのか、文書語の整理に留めるのか。

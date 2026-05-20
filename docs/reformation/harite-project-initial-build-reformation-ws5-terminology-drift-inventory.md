# Harite Project Initial Build Reformation WS5 Terminology Drift Inventory

最終更新: 2026-05-20

## 位置づけ

- 本書は [docs/reformation/harite-project-initial-build-reformation-ws5-internal-issues-overview.md](docs/reformation/harite-project-initial-build-reformation-ws5-internal-issues-overview.md) を受ける WS5 の子文書である。
- 対象は canonical spec だけに限らず、README、現行 docs、src 実装、tests を含む現行 repo 全域の用語ぶれである。
- ここでは、現状の表現差、責務境界による説明差、未整理の呼び方を横断一覧として固定する。
- WS4 側では、この一覧の元になる抽出と事実記載までを扱い、ここで見えた論点をどう直すか、どこまで直すかを決める working は WS5 で扱う。
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
- 正系語の判定: repo 内の都合や履歴だけで閉じず、公開アプリとして一般的に通じる語彙と観念を優先する。
- 提供者判断の前提: 時間とコストを掛ければ直せる論点は「直せないから放置する」とは扱わず、維持・rename・削除縮退のいずれかを能動判断する。

## WS4 / WS5 の境界

- WS4 は、現行 repo を読み、用語ぶれや責務ずれを抽出し、事実として記述するところまでを担当する。
- WS4 では、抽出した論点を見てその場で rename や wording 修正へ進まない。
- WS5 は、本書を input にして、どの論点を直すか、併存を許容するか、rename まで踏み込むかを working として扱う。
- したがって本書は、修正文案の置き場ではなく、後続 working の判断材料を過不足なく残すための inventory として使う。

## 一覧

| ID | 論点 | 現在の表現 | 主な出現箇所 | ずれの型 | 扱い候補 | 位置候補 |
| --- | --- | --- | --- | --- | --- | --- |
| T01 | 設定系の呼称 | 設定, 設定ファイル, settings, settings file, config, preferences, harite-preferences.json | [foundation](docs/specs/harite-foundation-spec.md#L98), [foundation](docs/specs/harite-foundation-spec.md#L140), [core](docs/specs/core/harite-core-spec.md#L201), [core](docs/specs/core/harite-core-spec.md#L257), [cli](docs/specs/cli/harite-cli-spec.md#L68), [gui](docs/specs/gui/harite-gui-spec.md#L76) | 日本語用語, CLI/module 名, 物理ファイル名が混在している | 文書上の正系語と媒体名を分離して整理する。特に config と 設定 を同義扱いで残すかを判定対象にする | rename・cleanup 第一候補 |
| T02 | watch の実体名 | watch, 周期実行, 周期的に選択, 選択ループ, changer 的継続実行 | [foundation](docs/specs/harite-foundation-spec.md#L94), [cli](docs/specs/cli/harite-cli-spec.md#L149), [watch](docs/specs/watch/harite-watch-spec.md#L55), [core](docs/specs/core/harite-core-spec.md#L36) | command 名と実際の挙動説明がずれている | rename 論点として維持しつつ、`周期実行` は使わず、`サイクル実行` または `スライドショーの実行` へ読み替える。正本側では `filesystem watch ではない` を共通注記に寄せる。 | rename・cleanup 第一候補 |
| T03 | 時間間隔と 1 回分処理の単位 | interval, interval_sec, interval_seconds, 周期, cycle, サイクル | [core](docs/specs/core/harite-core-spec.md#L36), [cli](docs/specs/cli/harite-cli-spec.md#L150), [cli](docs/specs/cli/harite-cli-spec.md#L175), [watch](docs/specs/watch/harite-watch-spec.md#L66), [watch](docs/specs/watch/harite-watch-spec.md#L163) | 時間と回数の単位語が同じ段落内で交差している | 時間は interval 系、1 回分処理は サイクル など、軸ごとの固定語を次段で決める | rename・cleanup 第一候補 |
| T04 | watch 出力と logging の呼称 | log_level, stdout message, WATCH summary, plugin logger, logging, status, message history | [cli](docs/specs/cli/harite-cli-spec.md#L164), [cli](docs/specs/cli/harite-cli-spec.md#L181), [watch](docs/specs/watch/harite-watch-spec.md#L140), [gui](docs/specs/gui/harite-gui-spec.md#L228), [plugins](docs/specs/plugins/harite-plugin-spec.md#L138), [core](docs/specs/core/harite-core-spec.md#L271) | 同じ log 系語で別観測面を指している | 観測面ごとに語彙を固定する。CLI は実行メッセージ、GUI はステータスとメッセージ履歴、plugin はロガーとし、`log` は総称にしない。 | rename・cleanup 第一候補 |
| T05 | apply 側の対象名 | apply target, 最終適用対象, target, monitor map, per-monitor mapping | [foundation](docs/specs/harite-foundation-spec.md#L100), [core](docs/specs/core/harite-core-spec.md#L156), [cli](docs/specs/cli/harite-cli-spec.md#L143), [plugins](docs/specs/plugins/harite-plugin-spec.md#L40), [plugins](docs/specs/plugins/harite-plugin-spec.md#L143) | 上位概念と Linux plugin 固有の受け口名が混在している | 上位概念を final apply target などで固定し、 monitor map は Linux per-monitor 受け口の下位語として分離する | rename・cleanup 第一候補 |
| T06 | GUI watch 表示名 | watch current, output display, watch summary, status, last_error, message history | [gui](docs/specs/gui/harite-gui-spec.md#L225), [watch](docs/specs/watch/harite-watch-spec.md#L107), [watch](docs/specs/watch/harite-watch-spec.md#L142), [gui](docs/specs/gui/harite-gui-spec.md#L235) | GUI 面の user-facing 表示名と内部状態名が混在している | user-facing label と内部 state key を分けて一覧化する。用語統一だけでなく表示責務も整理対象にする | rename・cleanup 第一候補 |
| T07 | 設定保存と画像保存の語 | settings save, load, apply, save, optimize 結果の出力先 | [foundation](docs/specs/harite-foundation-spec.md#L98), [foundation](docs/specs/harite-foundation-spec.md#L103), [gui](docs/specs/gui/harite-gui-spec.md#L77), [cli](docs/specs/cli/harite-cli-spec.md#L78) | save が設定保存と画像書き出しの両方に使われうる | 設定保存は settings save、画像書き出しは output save など責務境界で言い分ける候補として維持する | rename・cleanup 第一候補 |
| T08 | preferences 系クラス名と文書語 | OptimizePreferences, ApplyPreferences, WatchPreferences, AppPreferences, 設定モデル, preferences | [core](docs/specs/core/harite-core-spec.md#L30), [foundation](docs/specs/harite-foundation-spec.md#L141), [gui](docs/specs/gui/harite-gui-spec.md#L89) | 実装クラス名が preference 系、本文は設定系で説明している | T01 の整理結果に引かれる前提で、クラス名と本文語の不一致も rename・cleanup 対象として扱う。局所維持で浮かせない。 | rename・cleanup 第一候補 |
| T09 | source の settings / config / preferences 三層 | resolve_apply_settings, load_config, save_config, AppPreferences, on_apply_settings, on_load_settings_file | [config.py](src/harite/config.py#L17), [preferences.py](src/harite/preferences.py#L125), [apply_settings.py](src/harite/apply_settings.py#L18), [main_window.py](src/harite/gui/views/main_window.py#L788), [main_window.py](src/harite/gui/views/main_window.py#L909) | module 名、関数名、GUI handler 名がそれぞれ別語を主語にしている | spec だけでなく source 命名も棚卸対象に入れる。文書語だけ揃えて済むのか、命名整理まで踏み込むのかを WS5 で判定する | rename・cleanup 第一候補 |
| T10 | source / tests の watch 単位語 | WatchCycleState, run_watch_cycle, run_watch_cycles, interval_sec, interval_seconds, cycle_phase | [watch.py](src/harite/watch.py#L15), [watch.py](src/harite/watch.py#L88), [cli.py](src/harite/cli.py#L471), [preferences.py](src/harite/preferences.py#L104), [main_window.py](src/harite/gui/views/main_window.py#L1117), [test_watch_runner.py](tests/watch/test_watch_runner.py#L119) | source は cycle 系が強く、GUI state では phase や interval_seconds も混ざる | doc 側の統一だけでは不十分で、source 上の境界語も追跡対象として保持する | rename・cleanup 第一候補 |
| T11 | source / spec / tests の観測面語 | logger, logging, log_level, status_message, last_error, WATCH ..., message history | [plugins.py](src/harite/plugins.py#L16), [cli.py](src/harite/cli.py#L504), [main_window.py](src/harite/gui/views/main_window.py#L501), [test_phase4_regression.py](tests/gui/test_phase4_regression.py#L48), [test_plugins_linux_mapping.py](tests/plugins/test_plugins_linux_mapping.py#L8) | source は logger と status field、CLI は WATCH 行、tests は caplog や status assert で観測している | source / spec / tests を跨いで、CLI は実行メッセージ、GUI はステータスとメッセージ履歴、plugin はロガーへ固定する。観測面をまたぐ `log` 総称は避ける。 | rename・cleanup 第一候補 |
| T12 | mapping / monitor map の実装語 | mapping, per-monitor mapping, EffectiveApplySettings, resolve_apply_settings, plugin.apply(mapping, ...) | [apply_settings.py](src/harite/apply_settings.py#L18), [cli.py](src/harite/cli.py#L437), [plugins.py](src/harite/plugins.py#L375), [test_apply_settings.py](tests/test_apply_settings.py#L23), [test_plugins_xfconf.py](tests/plugins/test_plugins_xfconf.py#L41) | spec は apply target / monitor map、source と tests は mapping が優勢 | Linux plugin 層の実装語を monitor map に寄せるのか、上位 spec を mapping まで許容するのかを WS5 判定対象にする | rename・cleanup 第一候補 |

- 現時点では、T01-T12 は terminology drift inventory として整理しているため、右端の位置候補に `削除・縮退候補` の第一候補はまだ置かない。

## 固定化の決定事項

- 以下は、T01-T12 について現時点で固定した決定事項である。
- 文書では日本語を正系語に置き、user-facing surface では対応する英語語彙を使う前提で運用する。
- 1 つの ID の中に上下位語が混じる場合は、主語になる語を先に固定し、下位語は補足に回す。

| ID | 日本語の決定語 | 英語の決定語 | 補足 |
| --- | --- | --- | --- |
| T01 | 設定 | Settings | `config` は設定ファイルや設定入出力の補助語に下げ、主語には置かない。`preferences` は残さない方向で扱う。 |
| T02 | スライドショー | Slideshow | `watch` は実装由来の旧語として扱い、公開面の主語には置かない。実行を説明する場合は `サイクル実行` または `スライドショーの実行` とし、`周期実行` は使わない。 |
| T03 | 切替間隔 / 切替サイクル | Interval / Cycle | 時間量と 1 回分処理を分離して固定する。`周期` は極力使わず、必要時も補助説明に留める。 |
| T04 | 実行メッセージ / ステータス / メッセージ履歴 / ロガー | Run Messages / Status / Message History / Logger | CLI 出力、GUI 表示、plugin 内部観測を分離して固定する。`log` は総称にしない。 |
| T05 | 適用先 | Apply Target | 上位概念はこれに固定し、Linux plugin 側の monitor mapping は下位語として扱う。 |
| T06 | 状態表示 / 履歴 | Status / History | GUI の user-facing label は簡潔な表示語へ寄せ、内部 state 名とは切り分ける。 |
| T07 | 設定を保存 / 画像を書き出す | Save Settings / Export Image | `save` を 1 語で兼用せず、設定保存と画像出力を責務で分離する。`Export Image` を採用し、icon など周辺 surface も追随対象に含める。 |
| T08 | 設定モデル | Settings Model | classes も `Preferences` 系からの rename を第一候補に置き、T01 と浮かないようにする。 |
| T09 | 設定 | Settings | source 上の主語もこれに寄せる。`config` はファイル I/O や形式名に用途限定する。 |
| T10 | 切替間隔 / 切替サイクル | Interval / Cycle | source / tests 側も T03 と同じ軸で固定し、`周期` は極力使わず、`phase` は補助的な内部語へ下げる。 |
| T11 | 実行メッセージ / ステータス / メッセージ履歴 / ロガー | Run Messages / Status / Message History / Logger | CLI 行出力、GUI 表示、plugin logger を同じ `log` に畳まず、tests の観測語もこれに追随させる。 |
| T12 | モニター割当 | Monitor Mapping | apply target の下位に置く実装語として固定し、`mapping` 単独語は避ける。 |

## spec 外 surface の補足

- source では GUI handler 名に settings が強く、永続化 I/O には config、論理モデルには preferences が残っている。
- tests でも `plugin.apply(mapping, ...)` や `test_run_watch_cycles_*` のように、実装語をそのまま主語にした命名が広く使われている。
- README 現行面は語彙の密度が薄く、現時点では大きな用語ぶれの主戦場ではない。

## 補足所見

- ここまでの抽出過程では、強い不一致候補、責務境界での併存候補、rename と密接な候補、全域調査で見えた境界なども見えている。
- ただし、これらの所見整理は WS4 側の抽出過程で生じた揺らぎを含むため、現時点では owner が直接扱う WS5 対象としては数えない。
- したがって本書では、所見の優先順位づけや束ね直しよりも、上の一覧と下の判断を優先して参照する。
- 必要になった場合だけ、各論 task の中で該当 ID を見直して再評価する。

## 現時点の判断

1. T01-T12 の強い概念・観念は、公開アプリとして一般的に通じる標準的な語彙へ寄せる。
   - repo 内だけで通じる語や、実装都合だけで残った語は、正系語の根拠にしない。
   - user が初見で意味を推測しやすく、既存のアプリケーション感覚から大きく外れないことを優先する。

2. 文書の正系語は日本語中心で置く。
   - ただし、アプリケーション表面は英語に揃えているため、user-facing surface では違和感のない英語語彙を別途用意する。

3. watch 系の「時間間隔」と「1 回分処理」は、本来的には同義のものとして扱う。
   - 母体プログラムでは時間間隔だけを持っていたが、後から有限回数実行を導入したことで語が割れた経緯を前提に整理する。
   - 日本語の正系語では `周期` を極力使わず、時間量は `間隔`、1 回分処理は `サイクル` を優先する。
   - 詳細な fixed wording と surface 反映は、該当する各論 task の中で詰める。

4. log 系の主語整理は、WS5 内で決め切るが、この段階ではまだ確定しない。
   - log 関連の working を一通り通してからでないと判断材料が不足するため、いったん保留する。
   - ただし、観測面をまたぐ `log` 総称は正系語にしない方針だけは先に固定し、CLI は `実行メッセージ`、GUI は `ステータス` と `メッセージ履歴`、plugin は `ロガー` を第一候補に置く。

5. apply target と monitor map の上下関係は、先にある現行事実を基準に固定する。
   - したがってここでの論点は「どこまで本文で固定するか」そのものではなく、現行事実をどう責務境界つきで記述し切るかに置く。

6. source / tests の命名まで rename 対象に含める。
   - 文書語だけに留めず、仕様書、tests、source を含む全生産物で高い一貫性を目指す。

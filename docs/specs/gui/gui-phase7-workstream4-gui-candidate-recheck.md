# GUI Phase 7 Workstream 4: GUI 候補機能の再読

最終更新: 2026-04-21

## 位置づけ

- 本書は Phase7 product alignment における Workstream 4 の詳細メモである。
- 目的は、main 画面、settings、CLI 専用機能、Phase8 候補の境界を docs-first で整理することにある。
- index は [docs/specs/gui/gui-phase7-product-alignment-planning.md](docs/specs/gui/gui-phase7-product-alignment-planning.md) を参照する。
- Phase8 planning へ送った後続骨子は [docs/specs/gui/gui-phase8-planning.md](docs/specs/gui/gui-phase8-planning.md) と [docs/specs/gui/gui-phase8-backlog.md](docs/specs/gui/gui-phase8-backlog.md) を参照する。

## Workstream 4 の比較観点

- current GUI 上の入口は何か。
- current GUI での責務は何か。
- 母体プログラムでは何が相当機能だったか、または相当機能が存在しなかったか。
- `Harite v0.1.2` ではどう露出していたか。
- current 実装やこれまでの改修で、何が揃い、何が意図差として残ったか。
- 実機確認や過去の不具合修正から見えている制約は何か。
- Phase7 の判断として、main に残す / settings へ寄せる / CLI 専用のまま残す / Phase8 候補へ送る / 落とす、のどれに置くか。

## Phase7 判断項目

- この section は「Phase8 の仕様化」ではなく、「Phase7 の境界整理として閉じた項目」を抜き出すためのものとする。
- ここで閉じたのは、実装詳細ではなく、置き場、露出方針、Phase8 送りの確定である。

| 論点 | Phase7 で閉じたこと | Phase7 の判断 |
| --- | --- | --- |
| `Prefs` と main の境界 | `output_dir` を Phase7 時点で `Prefs` 正式対象へ上げるか | `Prefs` 正式対象へは上げず、runtime state として扱う。GUI の既定出力先は OS が解決する Pictures directory 直下とし、CLI は `.` 維持で分ける |
| watch interval の二重性 | `Prefs` 既定値 + watch tab runtime override を正式方針として明文化するか | 二重性は採らない。watch tab を正とし、`SrcdirL/R` と `Interval` は設定として永続化するが、`Prefs` UI には watch 系の loading / editing を持ち込まない |
| `Apply` visible 語彙 | `Default` を Phase7 文書上どう確定表現するか | GUI から `Default` は外す。MainWindow は英語へ寄せ、mode は `Auto-split` / `No Split` を第一候補として扱う |
| `Apply` helper text | Phase7 で helper text の責務まで決めるか | 最低限の意味だけ固定し、最終 UI 文言調整は後段に残す |
| explicit mapping の扱い | GUI 非対象を Phase7 判断として閉じるか | GUI 非対象として Phase7 判断で閉じる。CLI 専用の低露出 escape hatch として残す |
| `embed-text` の置き場 | main 非昇格と Phase8 送りを Phase7 判断として閉じるか | Phase8 扱いで閉じる。ただし将来の入口は MainWindow 内、またはその配下 tab / section を第一候補とする |
| preview / visual assist | Phase7 非対象を明記して backlog 化するか | 要望としては最上位級だが、Phase7 対象にはしない。GUI の visual preview は現状ゼロ、母体にも無かったものとして、Phase8 候補へ送る |
| `Color` | Phase8 候補として残すか、削除候補寄りに置くか | 削除候補へは寄せず、Phase8 で再定義する候補として残す。main 主導線へは戻さない |

## 判断順の推奨

1. `Prefs` と main の境界を先に閉じる。
2. `Apply` visible 語彙と helper text の責務を閉じる。
3. explicit mapping の GUI 非対象を閉じる。
4. `embed-text` と preview を Phase8 送りとして閉じる。
5. `Color` を「Phase8 で再定義または close 判断」のどちら寄りかだけ決める。

## 今日決めなくてよいこと

- preview の UI 形状そのもの。
- `embed-text` の実際の controls 配置。
- `Color` を実装する場合の機能定義詳細。
- helper text の最終 wording 微調整。
- `output_dir` の既定出力先ポリシーを実装へ反映するタイミング。

## 最終棚卸

- Phase7 で決定済みの事項:
  - `output_dir` は `Prefs` に上げず runtime state とし、GUI の既定出力先は OS が解決する Pictures directory 直下、CLI は `.` 維持とする。
  - watch は tab 側を正とし、`SrcdirL/R` と `Interval` は設定ファイルへ永続化するが、`Prefs` UI には watch 系 loading / editing を持ち込まない。
  - `Apply` では GUI から `Default` を外し、MainWindow は英語へ寄せ、mode は `Auto-split` / `No Split` を第一候補とする。
  - helper text は MainWindow 内に残し、mode の意味差だけを短く案内する。
  - explicit mapping は GUI 非対象として閉じ、CLI 専用の低露出 escape hatch とする。
  - `embed-text` 系は Phase8 扱いとし、将来の入口は MainWindow 内またはその配下 tab / section を第一候補とする。
  - preview / visual assist は GUI visual preview 現状ゼロ、CLI 対象外、母体にも無かったものとして Phase8 制作支援へ送る。
  - `Color` は削除候補へ寄せず、Phase8 で再定義する候補として残す。

- なお未決定として残る事項:
  - `Prefs` 側にも `No Split` / `Auto-split` をそのまま持ち込むか。
  - preview は Phase8 の初手を「生成後 preview」から入るか、「生成前 preview + 配置要約」まで同時に扱うか。
  - preview の入口を MainWindow 内 pane / section、配下 tab、別 window のどこに置くか。
  - `Color` を Phase8 でどの場面に、どの粒度で user selectable にするか。

## `Prefs` と main/settings 境界

- ここでいう `output_dir` は、Save As / save path dialog で user が明示選択する保存先そのものではない。
- ここでいう `output_dir` は、少なくとも次のような「明示 save path が無い場面での生成物置き場」を指す。
  - `Optimize` 実行時の自動命名出力
  - watch 実行時の生成物出力
  - auto-split など apply 補助生成物の出力
- Save As 文脈では保存先は user 主導であり、user が選ばなければ保存しない、という前提を優先する。
- したがって `output_dir` 論点は、Save As の UX ではなく、「明示保存先がない生成系導線の既定出力先をどう扱うか」の論点として切り分ける。

- current `Prefs` は optimize・apply・watch の一部既定値を保存し、dialog から apply / load / save できる入口として成立している。
- `Prefs` に入っていない代表値:
  - current input path L/R
  - `output_dir`
  - `save_path`
  - watch source dir L/R
  - watch current 表示や watch 実行状態
- `Prefs` は「何でも入る箱」ではなく、「既定値」と「今この作業だけの状態」を分ける入口として読む。
- settings dialog に寄せるもの:
  - optimize の既定値
  - plugin / apply mode の既定値
- main 画面に残すもの:
  - input path L/R
  - `output_dir` 候補
  - watch source dir L/R
  - watch interval
  - watch start / stop と current 状態表示
  - save 実行直前の保存先選択
  - `Apply` / `Optimize` の即時操作
- watch 系は tab 側を正とし、`SrcdirL/R` と `Interval` は設定ファイルへ永続化するが、`Prefs` UI からは編集しない。

## watch と `Prefs` の境界

- 再読した根拠:
  - MainWindow に watch tab を持ち込んだことで、watch 系の操作と状態は一か所にまとまった。
  - watch を「さあ、チェンジャーを使うぞ」という単位で扱うなら、入口と編集点が tab 側に集約されている方が自然である。
  - 一方で `SrcdirL/R` と `Interval` は、一度決めたら頻繁には変えない値でもある。

- Phase7 で閉じる判断:
  - watch 系機能の loading / editing を `Prefs` UI に持ち込まない。
  - watch tab を watch 系設定の正面入口とする。
  - `SrcdirL/R` と `Interval` は起動時だけの揮発 state にせず、設定ファイルへ永続化する。
  - したがってここで閉じるのは、「`Prefs` で watch を触る」ではなく、「watch tab と設定ファイルを接続する」方針である。

- 理由:
  - watch tab を置いた以上、watch の導線を別 dialog に分散させる理由は弱い。
  - 変更頻度の低い値であっても、watch tab から自然に再利用できる方が運用に合う。
  - これにより `Prefs` は optimize / apply の既定値寄り、watch tab は watch の作業導線寄り、という責務分離が保ちやすい。

### Phase7 で閉じる判断

- 決めたこと:
  - `Prefs` の正式保存対象へは上げず、runtime state として扱う。
  - Phase7 では、未指定時の既定出力先ポリシーまで閉じる。

- この判断を読むときの前提:
  - この論点は Save As の保存先ではなく、明示 save path がない生成物置き場の話として扱う。
  - ここで閉じたのは、GUI / CLI で既定値ポリシーを分けることと、GUI 側の既定出力先の置き方である。

- current 実装では GUI / CLI とも `.` を使っており、VS Code から起動した場合は repo root や clone 直下が偶発的な保存先になり得る。
- 標準的なアプリケーション作法に照らすと、GUI の既定出力先として current working directory (`.`) を使い続ける理由は弱い。
  - 起動場所に依存し、clone directory や repo root へ偶発的に保存され得る。
  - GUI 利用者にとって「どこへ出たか」が読みにくく、生成物の発見性が低い。
- そのため GUI 側の既定出力先は、起動場所に依存しない user writable な固定先へ寄せることとする。
  - 性格としてはアプリ私有ディレクトリではなく、user が自分の生成物として見つけやすい user-visible な保存先を優先する。
  - 画像生成物であるため、Linux / Windows とも Pictures 系 user space がもっとも自然である。
- 参照性の担保は、英語名や固定文字列で directory 名を決め打ちすることではなく、OS が解決する Pictures directory を使うことで読む。
  - Linux では XDG user dirs により解決された Pictures 系 directory を前提にする。
  - Windows では Known Folder として解決された Pictures 系 directory を前提にする。
  - OneDrive 配下や多言語 directory 名であっても、OS が返す実パスをそのまま扱う限り論点にしなくてよい。
- Pictures 配下の置き方としては、Pictures 直下と Pictures/Harite 配下の両案があり得る。
  - Pictures/Harite 配下は整理された見え方になるが、Phase7 時点で専用 subdirectory を必須化するほどの要件はまだ薄い。
  - 生成ファイル名に `harite` が含まれるため、Pictures 直下でも発見性と識別性は確保しやすい。
  - Windows でもスクリーンショット等が Pictures 系へ集まる運用は一般的であり、ユーザにとって異物になりにくい。
  - ただし watch は短周期実行時に近傍連番内をサイクリックに回す挙動が実機観測されており、生成物の蓄積や混在が将来の再検討条件になり得る。
- Phase7 の判断:
  - GUI は OS が解決する Pictures directory 直下を既定出力先とする。
  - CLI は current working directory (`.`) 維持とする。
  - 将来、生成物の種類や量が増えて Pictures 直下での混在が問題化した場合に限り、Phase8 以降で Harite 専用 subdirectory を再検討する。

## `Apply` visible 語彙 / helper text

- 再読した根拠:
  - current 実装の main 画面では apply mode が `Default` / `Auto-split` で露出し、補助ラベルは `Default: normal apply` になっている。
  - current `Prefs` 画面では `Apply Default` / `Apply Auto-split` という、さらに技術寄りの語が残っている。
  - Workstream 2 での整理では、`Default` は current 実装上 `single-file` であり、「追加分割をせず 1 ファイルを plugin 実装部へそのまま渡す経路」と読むのがもっとも整合的である。
  - ambiguity の直接原因は、`Default` という visible 語が「通常 apply」「OS の既定動作」「Harite の標準経路」を混線させたことにある。

- Phase7 で閉じる判断:
  - MainWindow の visible 語彙は、margin を除き英語へ寄せる。
  - GUI から `Default` という語は完全に外す。
  - `Default` が指していた経路は `single-file` のままと読み、visible では別語へ置き換える。
  - helper text は当面 MainWindow 内に残し、mode の意味差だけを短く案内する。
  - `Prefs` の apply mode 表示は、Phase7 では固定対象にしない。
  - helper text の status / tooltip への退避や icon 導入は、Phase8 側の UI 整理で扱う。

- visible 語の決定:
  - `Apply` 見出しの下で mode を 2 ボタン化する案を採る。
  - `No Separate` は不採用とする。
  - Phase7 の第一候補は次とする。
    - `[Auto-split]` = `per-monitor-auto-split`
    - `[No Split]` = `single-file`
  - こう読むと、`Auto-split` 側は monitor 別 apply target を内部生成する動作、`No Split` 側は追加分割せず 1 ファイルをそのまま適用する動作として対置できる。

- helper text の責務:
  - `Auto-split`: split the optimized image and apply per display。- `No Split`: apply the optimized image as a single file。- Phase7 ではまだ固定しない点:
  - `Prefs` 側にも `No Split` / `Auto-split` をそのまま持ち込むか。

## explicit mapping の扱い

- Phase7 で閉じる判断:
  - explicit mapping (`--left-file` / `--right-file`) は GUI 非対象として閉じる。
  - CLI 専用の低露出 escape hatch として残し、MainWindow や `Prefs` の主導線には持ち込まない。
  - ただし config / prefs load-save-apply 経路では unsupported mode を破壊しない。

- 理由:
  - Harite の GUI 主導線は、`Optimize` で成果物を作る流れと、`Auto-split` による monitor 別適用の自動生成に置く。
  - explicit mapping は expert workflow としては有効だが、current GUI の中心責務ではない。
  - これを GUI へ前面露出すると、`Auto-split` 主導線と責務が競合し、Phase7 で閉じた apply 語彙の整理も再び曖昧になりやすい。

- 2026-04-21 実装反映:
  - `per-monitor-explicit` 自体の GUI 露出は追加しない。
  - `Prefs` の apply mode は GUI 対応の 2 択だけを編集面として維持する。
  - その一方で、既存 config に `per-monitor-explicit` が入っていても、load / save / apply 経路で `single-file` へ勝手に潰さない。
  - この論点では実機確認を要求せず、GUI tests 通過を close 根拠とする。

## `embed-text` / margin info embedding

- core / CLI ではすでに正本機能として成立している。
- GUI では state と `Prefs` 保存対象には入っているが、main 画面の主導線 widget にはなっていない。
- core spec の基本方針は「余白のみ」「デフォルト無効」「可読性優先」「壊れにくさ優先」である。
- `params` / `free` / `combo` は、装飾機能というより、生成物へ最小限の付加情報を残す機能として読む。
- Phase7 で閉じる判断:
  - `embed-text` とその兄弟機能は、話題ごと Phase8 扱いで閉じる。
  - 理由は、Phase7 改修を重くしすぎないためである。
  - ただし将来の GUI 入口は `Prefs` へ退避するのではなく、MainWindow 内、または MainWindow 配下の tab / section を第一候補として扱う。
  - したがって Phase8 で扱うのは、「GUI に置くかどうか」ではなく、「MainWindow のどこに、どの粒度で置くか」である。
  - current state / prefs までは接続済みであることは明文化しておく。

## preview / visual assist

- 再読した根拠:
  - current GUI に visual preview と呼べる専用 UI は存在しない。
  - `last_saved_files` によって optimize 結果ファイル群は保持されるが、これは preview そのものではない。
  - `CLI preview` 文字列はあるが、これは CLI 対応の見える化であり、visual preview ではない。
  - 旧資産の再読でも、MainWindow 中央に常設画像 preview があった根拠は見つかっていない。
  - 母体プログラム側にも、今回ここで欲している visual preview 相当の正本機能は見当たらない。
  - ただし standalone design には `PreviewPane` / `preview_service` の構想があり、preview 自体が完全な異物というわけではない。

- 現時点の読み:
  - GUI の visual preview は現状ゼロ、と言い切ってよい。
  - CLI は当然 visual preview の対象外であり、この論点に混ぜなくてよい。
  - 要望としての優先度は高いが、Phase7 で抱え込むと境界整理より実装膨張が先に立ちやすい。
  - したがって preview / visual assist は、既存主導線の仕上げではなく、Phase8 で追加設計すべき GUI 制作支援機能として読むのが自然である。

- 比較候補:
  - 最小の preview は、optimize 結果の生成後 preview である。
  - 次段の visual assist は、画像そのものの表示だけでなく、配置要約、左右割当、auto-split 結果確認のような説明補助を含み得る。
  - 入口の置き方としては、少なくとも次があり得る。
    - MainWindow 内の pane / section として置く。
    - MainWindow 配下の tab として分離する。
    - 別 preview window として切り出す。

- Phase7 で先に閉じてよいこと:
  - Phase7 主導線へ無理に入れず、Phase8 扱いとして送る。
  - 単なる wishlist にせず、preview 不在が `embed-text` や deferred 項目の判断にも影響していることを比較可能な形で残す。
  - current baseline は「GUI visual preview はゼロ、CLI は対象外」で固定する。
  - 母体プログラムにも無かったため、Phase7 の upstream 整合性を崩してまで先行導入しない。

- いま考えるべき問い:
  - Phase8 の初手は「生成後 preview」から入るか、それとも「生成前 preview + 配置要約」まで同時に扱うか。
  - preview は MainWindow 内の一部として育てるか、制作支援用 tab / window として独立度を上げるか。

## `Color` など deferred 項目

- `MainWindow.on_set_color()` は `color picker is deferred to phase7` を status に出すだけのプレースホルダである。
- GUI test も、その deferred status を確認している。
- GTK runtime backend 側でも `Color` ボタン押下は `Color: deferred` 表示へ落ちるだけで、実処理には接続されていない。
- core / CLI 側にも GUI の color picker に対応する正本機能は見当たらない。
- 母体でも背景色は実質的に黒寄りだったが、それをそのまま正解とみなす理由は薄い。
- 背景色は margins や x 寄せが入ったときに見えやすくなり、作品の見え方に実影響を持つ。
- 一方で通常の desktop 背景として自然な色は、採用 desktop / distro / Windows の運用差にも左右される。
- user の好みや、見やすさに関わる個人差も無視しにくい。

- Phase7 で閉じる判断:
  - `Color` は削除候補へは寄せず、Phase8 で再定義する候補として残す。
  - 発想の核は、黒を押し付けることではなく、背景色を user が選べるようにすることにある。
  - ただし Phase7 では main 主導線へ戻さず、これを理由に main 画面構成や controls grouping を揺らさない。
  - Phase8 で扱うべき論点は、「Color を残すか」ではなく、「どの場面で、どの粒度で user selectable にするか」である。

## GUI 候補機能リスト（初版）

- Phase7 の main 主導線に残すもの:
  - `Optimize`
  - `Apply`
  - `Auto-split` を含む apply mode の整理
  - watch front-end
  - 入力 path / save path / current output のような作業中 state
- settings dialog (`Prefs`) に寄せるもの:
  - optimize 既定値
  - plugin / apply mode 既定値
- GUI に残すが主導線へは上げないもの:
  - embed 系の既定値保持
  - `CLI preview` 文字列による最低限の可視化
- CLI 専用のまま残すもの:
  - explicit mapping (`--left-file` / `--right-file`)
  - 実画面解像度と意図的にずらした素材生成を前提にした expert workflow
- Phase8 候補として送るもの:
  - `embed-text` / margin info embedding の MainWindow 内再配置
  - visual preview / assist
  - `Color` の再定義または close

## feature group ごとの暫定分類

| feature group | 現時点の置き場 | 理由 |
| --- | --- | --- |
| main workflow (`Optimize` / `Apply` / watch) | Phase7 主導線 | current product の中心責務であり、すでに実接続または責務整理済み |
| settings / defaults (`Prefs`) | Phase7 再整理対象 | current 実装はあるが、main との境界整理が必要 |
| apply wording / helper text | Phase7 再整理対象 | semantics は固まりつつあり、visible 語彙の整理が残る |
| embed / margin info | Phase8 候補 | core / CLI では成立済み。Phase7 では重くしすぎないため送り、MainWindow 内または配下 tab / section での再配置を Phase8 で扱う |
| visual preview / assist | Phase8 候補 | 要望優先度は高いが、GUI visual preview は現状ゼロで、母体にも無い。Phase7 では抱え込まず、Phase8 の制作支援として扱う |
| `Color` / deferred legacy items | Phase8 候補 | legacy 痕跡はあるが、背景色を user selectable に再定義する余地があり、削除候補へは寄せない |
| explicit per-monitor mapping | CLI 専用 | Harite の主導線ではなく、低露出 escape hatch として扱う |

## Phase8 候補バックログ素案

### P8-A。制作支援の最小セット

- 目的:
  - current GUI の「作れるが見えにくい」を改善する。
- 候補:
  - optimize 結果の生成後 preview
  - embed 系結果の見え方確認
  - two-screen 合成結果の確認
- 優先理由:
  - current Phase7 で最も不足が明確で、embed 系を主導線へ上げるかどうかの判断材料にも直結する。
  - 要望としての優先度も高く、Phase8 に入った時点で最初に着手する候補として自然である。

### P8-B。preview / visual assist の拡張

- 目的:
  - 生成前後の見た目確認を GUI 内で閉じる。
- 候補:
  - 生成前 preview と生成後 preview の責務分離
  - 配置要約表示
  - 将来的な auto-split 結果確認
- 優先理由:
  - single-screen / two-screen / embed / auto-split の複数論点を横断して支える基盤になり得る。

### P8-C。embed 系の GUI 昇格再設計

- 目的:
  - current state / prefs 接続済みの embed 系を、MainWindow 内の制作機能として再設計する。
- 候補:
  - MainWindow 内の section または配下 tab への配置
  - `embed_info` mode の user 向け語彙再設計
  - 既定値と作業ごとの埋め込み内容の分離
- 優先理由:
  - current state / prefs 接続はあるため、設計が決まれば進めやすい。

### P8-D。deferred 項目の close 判断

- 目的:
  - legacy 痕跡だけで残っている項目を backlog として残すか閉じるかを決める。
- 候補:
  - `Color` の再定義
  - close するなら close 条件と文言の明文化
- 優先理由:
  - 未完 UI の印象だけを残さないため、Phase8 では「作る」だけでなく「閉じる」判断も必要である。

## Phase8 の優先順メモ

- 第1群:
  - P8-A 制作支援の最小セット
  - P8-B preview / visual assist の拡張
- 第2群:
  - P8-C embed 系の GUI 昇格再設計
- 第3群:
  - P8-D deferred 項目の close 判断

- 理由:
  - preview / assist が弱いまま embed 系や deferred 項目を先に動かすと、結果確認の弱さを抱えたまま controls だけ増えやすい。
  - 先に制作支援の土台を置いた方が、embed 系を上げるか据え置くか、`Color` を残すか閉じるかの判断もしやすい。

## handoff

- Phase7 側では、preview / visual assist を第1群、embed 系 GUI 昇格を第2群、`Color` / deferred legacy を第3群として送るところまでを close とする。
- 以後の仕様化と PR 粒度整理は [docs/specs/gui/gui-phase8-planning.md](docs/specs/gui/gui-phase8-planning.md) と [docs/specs/gui/gui-phase8-backlog.md](docs/specs/gui/gui-phase8-backlog.md) で扱う。

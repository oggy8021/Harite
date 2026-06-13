# online-issues

GitHub Issue の調査・観測・方針メモをリポジトリ内に残す置き場。

## 位置づけ

| レイヤ | 役割 | 例 |
| --- | --- | --- |
| **GitHub Issue** | 対外トラッカー・議論の入口 | #341, #342, #343 |
| **docs/online-issues/** | 進行中 Issue の観測ログ・調査メモ | 本ディレクトリ直下 |
| **docs/online-issues/closed/** | 解決済み Issue の観測ログ・resolution 記録 | [closed/README.md](closed/README.md) |
| **docs/working/** | 進行中の planning / gap analysis | `20260609-1200-feature-overview.md` 等 |
| **docs/working/finished/** | 完了した working メモのアーカイブ | [finished/README.md](../working/finished/README.md) |
| **docs/specs/** | 確定した振る舞いの正本 | `harite-gui-spec.md` 等 |

正本（specs）に昇格する前の「観測と判断材料」は online-issues / working に置く。

## ディレクトリ構成

```text
docs/online-issues/
  issue-xxx.md         ← 複製用テンプレート（索引対象外）
  issue-{番号}.md      ← 進行中
  closed/
    issue-{番号}.md    ← 解決済み（GitHub で close 後に git mv）
```

新規 Issue メモは `issue-xxx.md` を複製し、`issue-{番号}.md` にリネームしてから埋める。

## ファイル命名

```
issue-{番号}.md
```

GitHub Issue 番号と 1:1 で対応させる。場所（直下 vs `closed/`）で状態を区別する。

## 推奨テンプレート

各 `issue-*.md` は次の見出しを揃える（短い Issue でも **分類** と **取り込み方針** は書く）。

**コピー元:** [issue-xxx.md](issue-xxx.md)（プレースホルダ `#xxx` のまま索引には載せない）

```markdown
# Issue #{番号}

## 管理情報
- URL / opened / title

## 事象
（ユーザーが見たこと）

## 分類
- bug / spec-as-designed / polish / investigation / planning

## 関連
- 他 Issue、spec 節、working 文書へのリンク

## 取り込み方針
- 現時点の判断（着手 / 保留 / spec 改訂 / 破棄）
- 次に誰が何をするか

## 調査メモ
（任意。AI 調査結果はここに整理して貼る）

## resolution
（解決したら日付と正本への反映先を追記。closed/issue-317 / issue-318 参照）
```

## 正本への昇格フロー

```text
GitHub Issue 起票
    ↓
online-issues/issue-NNN.md に観測・調査を追記
    ↓
複数 Issue / 横断テーマ → docs/working/ に backlog 化
    ↓
振る舞い確定 → docs/specs/ 改訂 PR（.cursorrules 手順 2）
    ↓
resolution 節を追記 → git mv で closed/ へ移動
    ↓
working メモも完了なら docs/working/finished/ へ移動
```

- **docs のみ PR** は CI 通過・オーナー確認後に即マージ可（`.cursorrules` §4）。
- **コード変更 PR** は対応 spec PR のマージ後（§5）。

## 索引（closed）

| Issue | タイトル要約 | 分類 | 統合 backlog |
| --- | --- | --- | --- |
| [#317](closed/issue-317.md) | slideshow 出力純増 | 解決済み → spec 反映 | — |
| [#318](closed/issue-318.md) | ファイル名再利用の spec 欠落 | 解決済み → spec 反映 | — |
| [#341](closed/issue-341.md) | Windows slideshow / dual-source | **解決済** → spec + #356 | [working](../working/finished/20260531-1200-windows-qt-validation-backlog.md) |
| [#342](closed/issue-342.md) | Qt Main action cluster レイアウト | polish → **完了** | 同上 |
| [#343](closed/issue-343.md) | Windows Apply / 壁紙 / 解像度 | **解決済** → spec 反映 | 同上 |
| [#354](closed/issue-354.md) | Windows settings path（Roaming） | **解決済** → F-01 | [F-01](../working/finished/20260518-2047-feature-overview.md) |
| [#353](closed/issue-353.md) | L/R path・srcdir swap | **解決済** → P-01 | [P-01](../working/finished/20260518-2047-feature-overview.md) |
| [#358](closed/issue-358.md) | Slideshow srcdir 個別 clear | **解決済** → P-02 | [P-02](../working/finished/20260518-2047-feature-overview.md) |
| [#359](closed/issue-359.md) | 単 display / monitor まわり UX（-R 無効化等） | **解決済** → P-03 | [P-03](../working/finished/20260518-2047-feature-overview.md) |

## 索引（進行中）

| Issue | タイトル要約 | 分類 | overview ID |
| --- | --- | --- | --- |
| [#492](issue-492.md) | トレイから Settings/Color で Main Window も表示 | bug（tray 回帰） | v2.0.0 post-release |
| [#493](issue-493.md) | JMA tick: 更新なし時に slideshow 停止 | bug / investigation | v2.0.0 post-release |
| [#494](issue-494.md) | Tray と Main の slideshow 状態不一致 | bug（#493 後の desync） | v2.0.0 post-release |
| [#495](issue-495.md) | running 中の設定を次 tick に適用 | enhancement | v2.0.0 post-release |
| [#496](issue-496.md) | Settings Save で keyword が消える | bug（settings 上書き） | v2.0.0 post-release |
| [#497](issue-497.md) | 縦長 NDL + display scale で tick 停止 | bug（optimize fit） | v2.0.0 post-release |
| [#503](issue-503.md) | JMA 更新後に apply されない（pause + skip 隙間） | bug | v2.0.1 候補 |

**修正 planning（着手順・PR 分割）:** [20260613-v2-post-release-fix-planning.md](../working/20260613-v2-post-release-fix-planning.md)

| [maturation-20260609-qt-common](maturation-20260609-qt-common.md) | Qt/共通 MAT-01〜18 + Q-01（`v2.0.0` 目標） | bug / investigation / planning | **Q-01**（[棚卸](../working/finished/20260610-q01-gtk-deprecation-planning.md)） |

### maturation-20260609-qt-common — 棚卸（2026-06-10 · #470 後）

| 区分 | ID |
| --- | --- |
| 完了 | MAT-01, 01b, 02〜03, 05〜09, 11〜18, 14b, 10, 02b（#442〜#470） |
| 観測完了 | MAT-08 op3（[メモ](../working/finished/20260610-mat-08-viper3-slideshow-op3-observation.md)） |
| 実装中 | **Q-01**（GTK 削除 + rename → Qt 一本化 · v2.0.0） |

### 内訳

| ID | 要約 | 区分 |
| --- | --- | --- |
| MAT-01 | Main xxAlign / Top・Bottom Align が効かない（handler） | 改修 |
| MAT-01b | 小画像 upscale + align 座標系が母体と乖離（core 回帰） | 改修 |
| MAT-02 | Slideshow `(stopped)` vs footer `running` 不一致 | 改修 |
| MAT-03 | Optimize で Color が効かない | 改修 |
| MAT-05 | CODH キーワード: Close しないと確定されない | 改修 |
| MAT-06 | CODH キーワード: Xfce+Qt で IME 不可 | 改修 |
| MAT-07 | embed Text: 2・3 行目 Enter で先頭行へジャンプ | 改修 |
| MAT-08 | Preset 系 Slideshow 動作ログ（CODH/NDL 観測用） | 確かさ |
| MAT-12 | Preset 時 Optimize 有無・保存先（**完了** #451） | 確かさ |
| MAT-04 | 江戸買物案内 preset をやめる（**完了** #455） | 要望 |
| MAT-09 | Margin 一括変更・リセット（**完了** #456） | 要望 |
| MAT-10 | 江戸切絵図を雰囲気絵ソースに（**実施 backlog**） | 要望 |
| MAT-18 | NDL `searchbytext` + キーワード（op3 品質所見） | 要望 |
| MAT-14b | 小画像 auto 倍率（Main + Slideshow） | 要望 |
| MAT-11 | Slideshow でも Main と同型の Optimize（**完了** #452） | 要望 |
| MAT-02b | NDL/CODH slideshow 安定化（**完了** #462–#465） | 改修 |
| MAT-13 | エラーメッセージを赤色で表示（**完了** #458） | polish |
| MAT-14 | source image scale % プリセット・L/R（**完了** #459） | 要望 |
| MAT-15 | align / margin / ストレッチの core 幾何総点検（**完了** #460） | 確かさ |
| MAT-16 | 時刻をローカル TZ（JST）で統一（**完了** #461） | 確かさ |
| MAT-08 観測 | viper3 op1–op3（op3 で勝ち筋確定） | 確かさ |
| MAT-17 | CLI slideshow で settings 読込（**完了** #463） | CLI |

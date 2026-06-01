# online-issues

GitHub Issue の調査・観測・方針メモをリポジトリ内に残す置き場。

## 位置づけ

| レイヤ | 役割 | 例 |
| --- | --- | --- |
| **GitHub Issue** | 対外トラッカー・議論の入口 | #341, #342, #343 |
| **docs/online-issues/** | 進行中 Issue の観測ログ・調査メモ | 本ディレクトリ直下 |
| **docs/online-issues/closed/** | 解決済み Issue の観測ログ・resolution 記録 | [closed/README.md](closed/README.md) |
| **docs/working/** | 進行中の planning / gap analysis | `20260518-2047-feature-overview.md` 等 |
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
| [#354](closed/issue-354.md) | Windows settings path（Roaming） | **解決済** → F-01 | [F-01](../../working/20260518-2047-feature-overview.md) |

## 索引（進行中）

| Issue | タイトル要約 | 分類 | overview ID |
| --- | --- | --- | --- |
| [#353](issue-353.md) | L/R path・srcdir swap | polish | [P-01](../working/20260518-2047-feature-overview.md) |
| [#358](issue-358.md) | Slideshow srcdir clear | polish | [P-02](../working/20260518-2047-feature-overview.md) |
| [#359](issue-359.md) | 単 display で -R 無効化 | edge case UX | [P-03](../working/20260518-2047-feature-overview.md)（構想保持） |

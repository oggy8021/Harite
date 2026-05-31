# online-issues

GitHub Issue の調査・観測・方針メモをリポジトリ内に残す置き場。

## 位置づけ

| レイヤ | 役割 | 例 |
| --- | --- | --- |
| **GitHub Issue** | 対外トラッカー・議論の入口 | #341, #342, #343 |
| **docs/online-issues/** | Issue 本文を補う観測ログ・調査メモ・解決記録 | 本ディレクトリ |
| **docs/working/** | 複数 Issue を束ねた planning / backlog | `20260531-1200-windows-qt-validation-backlog.md` |
| **docs/specs/** | 確定した振る舞いの正本 | `harite-gui-spec.md` 等 |

正本（specs）に昇格する前の「観測と判断材料」は online-issues / working に置く。

## ファイル命名

```
issue-{番号}.md
```

GitHub Issue 番号と 1:1 で対応させる。

## 推奨テンプレート

各 `issue-*.md` は次の見出しを揃える（短い Issue でも **分類** と **取り込み方針** は書く）。

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
（解決したら日付と正本への反映先を追記。issue-317 / issue-318 参照）
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
online-issues に resolution 節を追記（issue-318 型）
```

- **docs のみ PR** は CI 通過・オーナー確認後に即マージ可（`.cursorrules` §4）。
- **コード変更 PR** は対応 spec PR のマージ後（§5）。

## 索引

| Issue | タイトル要約 | 分類 | 統合 backlog |
| --- | --- | --- | --- |
| [#317](issue-317.md) | slideshow 出力純増 | 解決済み → spec 反映 | — |
| [#318](issue-318.md) | ファイル名再利用の spec 欠落 | 解決済み → spec 反映 | — |
| [#341](issue-341.md) | Windows slideshow / dual-source | **解決済** → spec + #356 | [working](../working/20260531-1200-windows-qt-validation-backlog.md) |
| [#342](issue-342.md) | Qt Main action cluster レイアウト | polish | 同上 |
| [#343](issue-343.md) | Windows Apply / 壁紙 / 解像度 | **解決済** → spec 反映 | 同上 |

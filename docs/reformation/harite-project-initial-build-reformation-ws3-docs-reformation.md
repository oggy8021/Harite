# Harite Project Initial Build Reformation WS3 Docs Reformation

最終更新: 2026-05-19

## 位置づけ

- 本書は [docs/reformation/harite-project-initial-build-reformation.md](docs/reformation/harite-project-initial-build-reformation.md) の Workstream 3 を具体化する子文書である。
- 主題は、planning / closing / validation record / 常設文書 / 将来構想文書が混在した現状 docs を、運用可能な体系へ再編することである。
- 仕様書本文の執筆は Workstream 4 の主責務とし、本書ではその受け皿を整える。

## この stream で固定すること

- 何を常設文書として残すか。
- 何を履歴保存文書として残すか。
- 何を統合、縮退、アーカイブ候補とみなすか。

## 対象

- `docs/specs/` を正本受け皿として明け渡すための directory 単位移動
- `docs/_initial-build-history/` へ退避した初期開発履歴群
- 大憲章、大構想資料、親文書の重複
- docs の参照導線
- 常設文書と履歴文書の役割分担

## 非対象

- packaging 実務
- release version judgement
- 仕様書本文の詳細章立て
- post-1.0.0 機能棚卸し

## 現在の状態

- 2026-05-19 時点で、初期開発寄りの directory 群は `docs/_initial-build-history/` へ directory 単位で退避済みである。
- `docs/specs/core/` `cli/` `gui/` `watch/` は、Workstream 4 の仕様書正本を受けるための空ディレクトリとして再作成済みである。
- したがって WS3 の次段は、細かな再分類ではなく、移動結果を review しながら「何を履歴として残すか」「何をさらに縮退または破棄するか」を詰めることに置く。

## 粗分類 v0

### 常設候補

- `docs/manual-validation-gate.md`
- `docs/release-delivery.md`
- `docs/release-readiness-checklist.md`

理由:

- 現行 Harite の挙動、運用、出荷確認に直接つながる面であり、履歴を辿らずに読みたい文書群だから。

### WS4 受け皿候補

- `docs/specs/gui/` (暫定)
- `docs/specs/core/` (暫定)
- `docs/specs/cli/` (暫定)
- `docs/specs/watch/` (暫定)

理由:

- directory 名としては常設仕様を受ける場所として自然だが、現時点では仕様書正本そのものはまだ成立していない。
- 2026-05-19 時点で、これらのディレクトリは実際に空の受け皿として明け渡し済みである。
- 実際の常設仕様は Workstream 4 で正本を書いた後にここへ受けるか、別の親文書構成へ寄せるかを決める。
- つまりこの directory 構成自体も暫定であり、最終的な章立てしだいでは `core/` `cli/` `gui/` `watch/` の切り方を見直す可能性がある。

### 履歴保存候補

- `docs/_initial-build-history/specs/gui/`
- `docs/_initial-build-history/specs/core/`
- `docs/_initial-build-history/specs/cli/`
- `docs/_initial-build-history/specs/watch/`
- `docs/_initial-build-history/consolidation/`
- `docs/_initial-build-history/meta/`
- `docs/_initial-build-history/pr_bodies/`
- `docs/_initial-build-history/legacy-ui/`
- `docs/_initial-build-history/misc/`

理由:

- 価値はあるが、「今の Harite を読む入口」よりも「どうここへ来たか」の保存価値が主だから。
- 特に `docs/specs/` は Workstream 4 の正本受け皿として明け渡す前提なので、支障になる文書は `docs/_initial-build-history/` へ退避してよい。
- phase ごとに生成時の前提、迷い、非採用仕様の混ざり方が違うため、ここで無理に再分類せず、その時制のまま dirty に残す方が履歴として自然である。
- したがって履歴化は「見やすく再編する」より「常設面から退避して history 側へそのまま移す」を優先する。
- これらは常設参照面ではなく、正本成立後によほど必要な時だけ振り返る履歴寄りの文書群として扱う。

### 運用候補

- `docs/dev/`
- `docs/git-operation-help/`
- `docs/templates/`
- `docs/branch-policy/`
- `docs/premium-request-savings.md`

理由:

- 製品仕様そのものではないが、owner / contributor の運用時には参照価値があるため、履歴専用とは切り分けたいから。

### 保留候補

- `docs/reformation/`

理由:

- 現時点では Workstream 3 / Workstream 4 の整理と正本設計のために使うが、Workstream 4 完了と `1.0.0` リリース後は履歴化する前提でよい。

## 固定した前提

### 1. `docs/specs/` は Workstream 4 に向けて明け渡す

- `docs/specs/core/` `cli/` `gui/` `watch/` は、既存文書を守る場所ではなく、仕様書正本の受け皿として空ける前提で進める。
- 2026-05-19 時点で、既存内容は `docs/_initial-build-history/specs/` へ退避し、元の directory は空の受け皿として再作成済みである。

### 2. 履歴退避は history 側へそのまま移す

- 移動単位は file 群ではなく directory 単位とし、`docs/specs/gui/` のような面をシンプルに明け渡す。
- history 側の置き場名は `docs/_initial-build-history/` とする。先頭アンダーバーは Explorer 上でまとまりを見やすくするために維持する。
- つまり、運用系など明け渡し対象ではないものを除き、支障になる directory を `docs/_initial-build-history/` へそのまま移す整理でよい。
- phase ごとに生成モデルや検討の粗さが違い、後に残らなかった非採用仕様も多い。
- そのため、ここで整理し直すより、作られた時制のまま history 側へ移す方が履歴価値を保ちやすい。
- これらは正本の出来しだいでは通常参照しない前提であり、「残すが入口には置かない」文書群として扱う。

### 3. `docs/reformation/` は移行期文書として使い切る

- `docs/reformation/` は当面は整理用の親文書群として使う。
- ただし Workstream 4 と `1.0.0` リリースを越えた後は、常設運用ではなく履歴側へ寄せる前提でよい。

### 4. Workstream 4 の仕様書正本は分冊前提で考える

- 正本は軽い概要メモではなく、業務仕様書並みに分冊する前提で扱う。
- 具体的な章構成と分冊線引きは別途相談し、時間をかけて決める。
- したがって Workstream 3 時点では、最終章立てを先に固定し切るより、正本受け皿を空けて履歴文書を退避することを優先する。

### 役割終了寄り / WS5 論点抽出候補

- `docs/specs/upstream-core-mapping.md`
- `docs/specs/upstream-full-analysis.md`
- `docs/_initial-build-history/misc/`

理由:

- どちらも upstream 解析と初期移植判断のための文書であり、現行 Harite の常設仕様や日常運用の入口としては役割をほぼ終えている。
- いま残っている価値は「将来また upstream 由来の機能を見直す時の論点メモ」に近く、その場合は文書自体を常設保持するより、必要な論点だけ WS5 側へ子文書として移す方が扱いやすい。
- したがって WS3 では、保持前提ではなく「破棄候補 / WS5 内容移管候補」として扱うのが自然である。

`docs/_initial-build-history/misc/` について:

- 中身はいずれも 2026-03 から 2026-04 の初期設計 / 初期検討メモ寄りであり、現行の常設仕様を支える面ではない。
- OS 依存部を閉じ込めている補助価値はあるが、それも Workstream 4 の仕様書正本が成立した後は原文書として保持する必要は薄い。
- したがって `docs/_initial-build-history/misc/` は、仕様書正本成立後に破棄候補として扱うのが自然である。

## 現時点の論点

### 1. 常設文書と履歴文書の境界

- 現在の docs には、今読むべきものと歴史として残すべきものが混在している。
- 特に GUI 系は phase planning と validation record が厚く、入口が重い。

### 2. 親文書の数と責務

- roadmap、closing、planning、補助メモが段階的に増えており、親文書の責務が分散しやすい。
- 正本として読む文書と、補助として参照する文書を分ける必要がある。

### 3. 大型構想資料の扱い

- 今の Harite と整合するもの
- 歴史的には有用だが常設参照には重いもの
- 役割が薄くなったもの

### 4. docs 反映前に小さく実装を先行させる論点

- Linux / XFCE の launcher / autostart のように、常設仕様へ落とす前に最小実装で導線を確定した方がよいテーマがある。
- その種の論点は、WS3/WS4 の前段で短い implementation event として先行させ、docs は後から実装に寄せる方が自然である。

補助メモ:

- [docs/reformation/harite-project-initial-build-reformation-linux-xdg-launcher.md](docs/reformation/harite-project-initial-build-reformation-linux-xdg-launcher.md)

## 初動タスク

1. docs を「常設」「履歴」「運用」「将来構想」に仮分類する。
   - 2026-05-19 時点で directory / 文書群単位の粗分類 v0 まで着手済み。
2. `docs/specs/` の初期開発 directory 群を `docs/_initial-build-history/` へ directory 単位で退避し、受け皿を空ける。
   - 2026-05-19 時点で `gui` `core` `cli` `watch` と履歴系 directory の一括移動を実施済み。
3. 大憲章・大型構想資料の一覧を作り、常設参照面へ残すかどうかだけを整理する。
4. 再編後の docs map の最小案を作る。

## 次の焦点

- `docs/_initial-build-history/` へ移した directory 群は、追加選別せず履歴退避済みとして扱う。
- `docs/specs/core/` / `cli/` / `gui/` / `watch/` を、WS4 の正本受け皿としてどう使うかを固める。
- `docs/specs/upstream-*.md` を、補助履歴として残すのか、WS5 へ論点抽出して原本は破棄寄りにするのかを判断する。
- `docs/_initial-build-history/misc/` を、仕様書正本成立後の破棄候補として扱う前提でよいかを固める。
- 大型構想資料を、常設参照ではなく補助履歴へ寄せるかを判断する。
- Workstream 4 の分冊前提に対して、どの directory 名を最終受け皿として残すかを別途詰める。

## 完了条件

- docs の役割分類が説明可能になっている。
- 常設文書と履歴保存文書の境界が説明可能になっている。
- GUI 系 docs の重さをどこで減らすか説明可能になっている。
- Workstream 4 の仕様書正本をどこへ受けるか説明可能になっている。

# Harite Project Initial Build Reformation WS2 Packaging And Release

最終更新: 2026-05-18

## 位置づけ

- 本書は [docs/reformation/harite-project-initial-build-reformation.md](docs/reformation/harite-project-initial-build-reformation.md) の Workstream 2 を具体化する子文書である。
- 主題は、初期製造を `1.0.0` として出荷するための packaging / sdist / release evidence / version judgement を整理することである。
- 出荷前の起動ノイズ整理、code residue cleanup、owner 判定前整理は [docs/reformation/harite-project-initial-build-reformation-ws1-release-prep.md](docs/reformation/harite-project-initial-build-reformation-ws1-release-prep.md) の主責務とする。

## この stream で固定すること

- packaging と配布物の成立条件を明示する。
- `1.0.0` 判定に必要な release 証跡を定める。
- version、CHANGELOG、release notes、配布説明の整合境界を明示する。
- 別紙の大部 checklist を増やさず、この WS 文書と chat 上の判断記録で回せる形にする。

## 対象

- `pyproject.toml`
- package data
- entrypoint
- sdist / wheel / release 実務
- CHANGELOG / release notes / version judgement
- license / notices の配布物整合

## 非対象

- 起動時メッセージの整理
- 出荷前に不要な debug / 暫定表示の整理
- `1.0.0` 前に落とすべき code residue / skeleton / placeholder / legacy alias
- docs 全体の情報設計
- 常設仕様書の章立て設計
- post-1.0.0 機能棚卸し

## 現時点の論点

### 1. packaging の成立条件をどこまでに置くか

- sdist が作れること
- entrypoint が配布物でも自然に使えること
- GUI resource / icon resource が欠落しないこと
- README や release 文書と配布実態が矛盾しないこと

### 2. `1.0.0` judgement の最小証跡を何にするか

- 配布構成の確認
- バージョン表記と release notes の整合
- 必要最小限の回帰確認
- owner judgement をどこへ残すか

## 現時点の観測

### 1. packaging の現状

- [pyproject.toml](pyproject.toml) では project 名は `harite`、version は `0.1.3`、script entrypoint は `harite` / `harite-gui` になっている。
- package data は `"harite.gui" = ["resources/**/*"]` として GUI resource 一式を含める構成になっており、tray / application icon の packaging 方針とは整合している。
- したがって WS2 の主論点は「package data が未設定」ではなく、「`1.0.0` 出荷物として十分な資産が本当に全てこの定義で拾われるか」と「sdist/wheel 観点の最終確認をどこまで再実施するか」にある。

#### `sdist/wheel` で見る資産群

- Python package 本体:
  - `src/harite/*.py`
  - `src/harite/gui/**/*.py`
  - CLI / GUI entrypoint の実体である [src/harite/cli.py](src/harite/cli.py) と [src/harite/gui/app.py](src/harite/gui/app.py)
- GUI runtime resource:
  - [src/harite/gui/resources/README.md](src/harite/gui/resources/README.md)
  - `src/harite/gui/resources/icons/product/*.svg`
  - `src/harite/gui/resources/icons/lucide/*.svg`
- project metadata / 配布説明:
  - [pyproject.toml](pyproject.toml)
  - [README.md](README.md)
  - [LICENSE](LICENSE)
  - [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
  - 配布手順の現行ベースである [docs/release-delivery.md](docs/release-delivery.md)

#### 現時点の暫定資産一覧

- CLI 側の最低限確認対象:
  - `harite` entrypoint
  - core package (`core.py`, `plugins.py`, `watch.py`, `preferences.py`, `workspace.py` など)
- GUI 側の最低限確認対象:
  - `harite-gui` entrypoint
  - GTK runtime backend / adapter 群
  - tasktray adapter
  - application / tray icon を含む `resources/icons/product/`
  - header icon を含む `resources/icons/lucide/`

#### 暫定判断

- wheel では「entrypoint が起動できること」と「GUI resource が importlib.resources で欠落しないこと」を最優先に見る。
- sdist では、それに加えて「ビルド元として必要な source / metadata / resource が揃っていること」を見る。
- license 面では、Harite 本体の MIT を [LICENSE](LICENSE) で同梱し、vendor した Lucide icon の upstream notice を [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) で配布物へ残す。
- [src/harite/gui/resources/README.md](src/harite/gui/resources/README.md) の方針どおり、runtime で使う資産は `src/harite/gui/resources/` 配下に閉じているため、WS2 ではこの閉じ方が配布物でも維持されるかを確認対象にする。

### 2. release 実務文書の現状

- [docs/release-readiness-checklist.md](docs/release-readiness-checklist.md) は現時点で `v0.1.0` 前提のチェックリストであり、初回リリース時の証跡としては有用だが、そのまま `1.0.0` 判定の正本には使えない。
- 既存 checklist には `pytest`、`python -m build --sdist --wheel`、`.venv` 非依存実行確認、release notes 草案など、WS2 でも流用可能な確認項目が既にある。
- WS2 では、この既存 checklist を丸ごと再利用するのではなく、「`1.0.0` 判定へ流用する項目」「更新が必要な項目」「初回リリース固有で畳んでよい項目」を分ける必要がある。

#### 文書運用の暫定方針

- [docs/release-readiness-checklist.md](docs/release-readiness-checklist.md) は source material として読むに留める。
- `1.0.0` 向けには、再利用性の低い大部 checklist を育て直すのではなく、WS2 の論点に直結した軽量 release gate へ落とす方がよい。
- agent 作業上も必要なのは詳細な儀式一覧ではなく、「何が揃えば出せるか」の判定軸が少数で固定されていることである。
- 現運用では、WS / 事前文書で大半の論点が既に押さえられており、残差分は chat 欄の判断記録で十分追えるため、独立 checklist の常設価値は高くない。

### 3. version judgement の現状

- [pyproject.toml](pyproject.toml) の version はまだ `0.1.3` であり、`1.0.0` へ上げる判断そのものは未反映である。
- したがって WS2 では、version bump を先に行うのではなく、「何が揃ったら `1.0.0` に上げるか」を先に固定する。

### 4. release 面の整合状況

- [pyproject.toml](pyproject.toml) の version は `0.1.3`、[CHANGELOG.md](CHANGELOG.md) も `0.1.3 (2026-05-16)` まで更新されており、この 2 つは現時点で整合している。
- [docs/release-notes-draft.md](docs/release-notes-draft.md) は `v1.0.0 draft` として current 化済みであり、stale 状態は解消した。
- そのため Gate 3 の現時点の主な未充足は「最終 version をいつ `1.0.0` に上げるか」と「release note 上で何を最終同梱範囲として言い切るか」に寄っている。
- WS2 では、release note 草案を土台にしつつ、最終版で確定させる文言の境界を詰める。

## `1.0.0` 少数 gate

### Gate 2. packaging / resource / license 成立

- `harite` / `harite-gui` entrypoint が配布物観点で成立している。
- 本体 Python package と `src/harite/gui/resources/` 配下の runtime asset が配布物で欠落しない。
- [LICENSE](LICENSE) と [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) が配布物に残る。
- 証跡の置き場:
  - [pyproject.toml](pyproject.toml)
  - [README.md](README.md)
  - [docs/release-delivery.md](docs/release-delivery.md)
  - 本文中の packaging 判断

### Gate 3. release 面の整合

- version、CHANGELOG、release notes 草案、配布説明の間で大きな矛盾がない。
- `1.0.0` として何を出すか、何をまだ含めないかが説明できる。
- 証跡の置き場:
  - [pyproject.toml](pyproject.toml)
  - [CHANGELOG.md](CHANGELOG.md)
  - [docs/release-notes-draft.md](docs/release-notes-draft.md)
  - 本文中の version / release judgement

現時点の評価:

- [pyproject.toml](pyproject.toml) と [CHANGELOG.md](CHANGELOG.md) は `0.1.3` で整合している。
- [docs/release-notes-draft.md](docs/release-notes-draft.md) は `v1.0.0 draft` として更新済みであり、草案不在は解消した。
- ただし final release の version / scope はまだ未確定であり、Gate 3 は完全充足前の段階にある。

## WS2 の暫定判断

- packaging は resource 同梱方式そのものを作り直す段ではなく、既存 [pyproject.toml](pyproject.toml) を前提に `sdist/wheel` の最終確認条件を再定義する段として扱う。
- packaging の最小成立条件は、`harite` / `harite-gui` entrypoint、本体 Python package、`src/harite/gui/resources/` 配下の runtime asset が配布物で欠落しないことである。
- packaging の license 成立条件は、自前 MIT と vendored Lucide notice の両方が配布物に残ることである。
- release 判定文書は [docs/release-readiness-checklist.md](docs/release-readiness-checklist.md) を source material として参照しつつ、`1.0.0` 用には少数 gate の軽量正本へ縮退させる前提でよい。
- release 証跡は、必要最小限なら WS2 本文と関連文書、補足は chat 上の owner/agent 判断ログで足りる。
- Gate 3 については、release notes 草案の current 化は済んだため、現時点の主残論点は version bump と最終同梱範囲の確定である。

## 当初タスク

1. [pyproject.toml](pyproject.toml) の package data / entrypoint を前提に、`sdist/wheel` 最終確認で見る資産一覧を列挙する。
2. `1.0.0` 判定に必要な少数 gate を、この WS 文書内で説明可能な形へ絞る。
3. version bump 前に必要な gate と、その証跡の置き場を文書化する。
4. release notes / CHANGELOG / 配布説明の整合境界を整理する。

## 完了条件

- packaging / sdist の成立条件が説明可能になっている。
- `1.0.0` judgement に必要な最小証跡が説明可能になっている。
- version、CHANGELOG、release notes、配布説明の整合境界が説明可能になっている。
- その証跡が、不要な独立 checklist なしでも追える構成になっている。
- Workstream 1・3・4・5 に属する論点と混線していない。

# GUI Phase 8 計画（制作支援と deferred 項目の仕様化フェーズ）

最終更新: 2026-04-21

## 位置づけ

- 本書は、Phase7 で Phase8 候補へ送られた GUI 項目を実装前提の planning として束ねる index 文書である。
- Phase8 は exploratory な発散フェーズではなく、Phase7 で置き場と優先順を整理した候補を仕様化し、実装可能な backlog へ落とすフェーズとして扱う。
- Phase7 の product alignment で閉じた main workflow、apply wording、watch responsibility を崩さず、その上に制作支援と deferred 項目を段階追加する。

## 目的

- preview / visual assist を、GUI の制作支援機能として最初の feature group に固定する。
- `embed-text` / margin info embedding を、MainWindow 内の再配置対象として仕様化する。
- `Color` など deferred 項目を、実装候補として残すものと close 判断を伴うものに分ける。
- Phase8 の feature group 間依存を明文化し、controls だけが先に増える状態を避ける。

## 非目的

- Phase7 で閉じた apply semantics や watch responsibility をやり直すこと。
- preview の見た目だけを先に決め、責務や入口を曖昧なまま実装すること。
- `embed-text` や `Color` を個別要求として先行実装し、制作支援基盤との依存を無視すること。

## 一次参照

- [docs/specs/gui/gui-phase7-product-alignment-planning.md](docs/specs/gui/gui-phase7-product-alignment-planning.md)
- [docs/specs/gui/gui-phase7-workstream4-gui-candidate-recheck.md](docs/specs/gui/gui-phase7-workstream4-gui-candidate-recheck.md)
- [docs/specs/core/margin-info-embedding.md](docs/specs/core/margin-info-embedding.md)
- [docs/specs/core/monitor-split-design.md](docs/specs/core/monitor-split-design.md)
- [docs/specs/gui/gui-standalone-design.md](docs/specs/gui/gui-standalone-design.md)
- [docs/specs/gui/gui-glade-layout-reconstruction.md](docs/specs/gui/gui-glade-layout-reconstruction.md)

## 文書構成

- index / planning:
  - [docs/specs/gui/gui-phase8-planning.md](docs/specs/gui/gui-phase8-planning.md)
- backlog / feature group detail:
  - [docs/specs/gui/gui-phase8-backlog.md](docs/specs/gui/gui-phase8-backlog.md)
- repair sequence:
  - [docs/specs/gui/gui-phase8-repair-plan.md](docs/specs/gui/gui-phase8-repair-plan.md)
- current status / resume overlay:
  - [docs/specs/gui/gui-phase8-resume-planning-after-2weeks-break.md](docs/specs/gui/gui-phase8-resume-planning-after-2weeks-break.md)

## Phase7 から受け取る前提

- main workflow (`Optimize` / `Apply` / watch) は Phase7 で主導線を閉じている。
- `Apply` visible wording は `Auto-split` / `No Split` を第一候補として閉じている。
- explicit mapping は GUI 非対象であり、Phase8 でも主導線へ上げない。
- GUI visual preview は現状ゼロであり、母体にも相当の正本機能は無かった。
- `embed-text` 系は current state / prefs 接続までは揃っているが、MainWindow 主導線には昇格していない。
- `Color` は legacy 痕跡として残るが、Phase7 では削除候補へ寄せず Phase8 での再定義候補として保留した。

## feature group の優先順

| group | 主題 | 現時点の位置づけ | Phase8 で最初に決めること |
| --- | --- | --- | --- |
| 1 | preview / visual assist | 第1群 | 最小 preview を「生成後 preview」から入るか、配置要約まで同時に持つか |
| 2 | embed 系 GUI 昇格 | 第2群 | MainWindow 内の入口位置と、既定値 vs 作業単位編集の分離 |
| 3 | `Color` / deferred legacy | 第3群 | 再定義して残すか、close 条件付き backlog に落とすか |

## feature group 間依存

- preview / visual assist は、Phase8 の土台機能として先に置く。
- embed 系は preview 不在のまま controls だけ増やさないため、第1群の後ろに置く。
- `Color` は preview や embed と同列の制作支援候補ではなく、close 判断を含む低優先 group として扱う。

## Phase8 で先に固定する問い

1. preview の初手を「生成後 preview」に限定するか。
2. preview の入口を MainWindow 内 pane / section、配下 tab、別 window のどこに置くか。
3. visual assist に配置要約や auto-split 結果確認をどこまで含めるか。
4. `embed-text` を MainWindow に昇格する際、最小 controls をどこまで露出するか。
5. `Color` を user selectable な背景色機能として再定義するか、close 条件付き候補として扱うか。

## 完了条件

- preview / visual assist、embed 系、`Color` の 3 group が依存順付きで backlog 化されている。
- 第1群の最小着手単位が 1 PR に切れる粒度まで明文化されている。
- `Color` など deferred 項目が「残す」だけでなく、close 判断を含む形で整理されている。
- Phase7 文書から Phase8 planning へ自然に辿れる。

# GUI Phase10 1st Planning

最終更新: 2026-05-11

## 位置づけ

- 本書は [docs/specs/gui/gui-phase9-11-roadmap.md](docs/specs/gui/gui-phase9-11-roadmap.md) の Phase10 を、初手 planning として具体化する文書である。
- 初手では visual aid や icon 導入へ広げず、まず GUI の通常起動導線を利用者向けに整える。
- Phase9 で確定した前提として、XFCE は current GUI の正本運用環境であり、Phase10 で解消したい暫定は XFCE 対応そのものではなく option 依存 bootstrap である。

## 現在地

- [src/harite/gui/app.py](src/harite/gui/app.py) は `--bind-ui-backend` / `--present-ui-window` と環境変数前提の bootstrap を持つ skeleton 的 entrypoint である。
- 現在の実ウィンドウ起動は [docs/manual-validation-gate.md](docs/manual-validation-gate.md) などで `python -m harite.gui.app --bind-ui-backend --present-ui-window` を前提にしているが、この文書は現時点では強い制約として扱わない。
- [pyproject.toml](pyproject.toml) には既に `harite` と `harite-gui` の console script があり、CLI の正式名は `harite`、GUI 側の既存 script 名は `harite-gui` である。
- [src/harite/cli.py](src/harite/cli.py) は Typer ベースの command entrypoint であり、将来的に `harite gui` のような subcommand 導線を追加できる余地もある。
- Phase9 の compatibility 判断では、runtime fallback backend は維持しつつ、利用者向けには option 依存 bootstrap を見せ続けない方針を確定した。
- したがって Phase10 の初手は、「GTK runtime / fallback backend を消す」ことではなく、「利用者が追加 option なしで current GUI を起動できる既定導線を定義する」ことにある。

## 利用想定の前提

- CLI は、変わった使い方を含めても `harite` を叩いて使いこなす層が残る前提でよい。
- 一方で GUI standalone は、恒久的にターミナルから都度起動される主導線というより、初回起動・試用・設定導入時に触られる導線として考える。
- 開発者自身も 1 ユーザーであり、毎回コマンド履歴から `python -m harite.gui.app --bind-ui-backend --present-ui-window` を探して再実行する運用は避けたい。Phase10 では、この日常的な起動摩擦の解消も正当な要求として扱う。
- したがって GUI 側は、end user に `--bind-ui-backend` / `--present-ui-window` を露出させないことを優先し、常用導線としての taskbar / indicator / `.desktop` 常駐設計は Phase10 初手の必須論点にしない。
- 製品化後の launcher UX と、現時点の開発・配布前導線は切り分けて考えてよい。ただし「追加 option なしで GUI が開く」こと自体は、製品化前の Phase10 でも満たしておく。

## 目的

- owner の通常利用環境である XFCE で、current GUI を追加 option なしの既定導線から起動できるようにする。
- 開発用 bootstrap option と通常利用導線を分離し、まず README / 実装の説明を揃える。
- 開発者や継続利用者が、長い bootstrap コマンドを履歴から拾わずに current GUI を開ける状態にする。
- runtime fallback backend や non-fatal safety net の存在を内部実装へ押し戻し、利用者向け説明からは隠蔽する。

## 非目的

- Phase10 初手で visual aid / icon 方針まで同時に確定すること。
- Phase9 で整理済みの backend 境界を再び大きく掘り返すこと。
- OS integration や tray / indicator まで着手すること。

## 論点

### 1. 通常起動導線を何にするか

- 第一候補は `python -m harite.gui.app` を通常起動導線として成立させること。
- このとき `--bind-ui-backend` / `--present-ui-window` を既定で内包するのか、別の内部判定へ置き換えるのかを決める必要がある。
- 利用者向けには「XFCE で current GUI を開くコマンドは 1 つ」で説明できる形を優先する。
- 既存の script 定義と CLI 構造を踏まえると、Phase10 初手の実用候補は `harite-gui`、`python -m harite.gui.app` の no-option 化、`harite gui` の 3 系統である。
- ただし CLI 正式名 `harite` を GUI 専用コマンドへ直ちに振り替える前提は取らない。

### 初手評価

- 近距離の第一候補:
  - `harite-gui` と `python -m harite.gui.app` を追加 option なしで current GUI 起動可能にし、bootstrap option は内部既定または開発用補助へ押し戻す。
  - `harite gui` は比較候補として残すが、Phase10 初手の README 正本導線はまず `harite-gui` を優先候補として扱う。
- 理由:
  - [pyproject.toml](pyproject.toml) ですでに GUI script 名 `harite-gui` が存在するため、end user 向けに bootstrap option を隠す最短経路がある。
  - CLI 側の正式名 `harite` は既存の CUI 利用者向け導線として残っており、Phase10 初手で GUI と取り合いにしない方が混乱が少ない。
  - 一方で [src/harite/cli.py](src/harite/cli.py) の command 構造上、`harite gui` は導入不能ではなく、README 主導で誘導する前提なら十分実用候補になり得る。
  - 開発者自身も日常的に使う以上、「履歴から長い bootstrap コマンドを拾う」運用をやめられることに即効性がある。
  - GUI standalone は常時コンソール起動される主導線ではなく、将来は `.desktop` や launcher 側から隠蔽される可能性が高いため、まずは「no-option で起動できる実体コマンド」を整える方が筋が良い。
- 保留するもの:
  - `.desktop` / indicator / taskbar 常駐との結合設計。
  - `harite` という単一コマンド名へ GUI を寄せるかどうか。

## 現時点の採用方針

- Phase10 初手の README 上の正本 GUI 導線は、現時点では `harite-gui` を第一候補として採る。
- 理由は、美しさや CLI 体系の統一感よりも、既存 script 名としてすでに存在していること、Windows / macOS の浅めな利用者にも「GUI 用の実体コマンド」として認識しやすいこと、実装変更の最短経路であることを優先するためである。
- `harite gui` は将来の整理候補として残すが、Phase10 初手では正本導線にしない。
- したがって次の作業は「`harite-gui` と `python -m harite.gui.app` の no-option 起動化」と「README 上の正本導線を `harite-gui` 基準へ揃えること」である。

## `harite-gui` no-option 化の実装変更点

### 仮説

- 現状の起動摩擦の根因は、[src/harite/gui/app.py](src/harite/gui/app.py) の通常経路が `bind_ui_backend=None` / `present_ui_window=None` を受け取り、その解決先が `_should_bind_ui_backend()` / `_should_present_ui_window()` で env 既定 `0` に落ちることにある。
- したがって Phase10 初手では、runtime fallback backend 自体を消すのではなく、「通常起動で `bind` と `present` が既定で有効になる入口」を 1 本定義すればよい。

### 近距離の再設計案

1. [src/harite/gui/app.py](src/harite/gui/app.py) に「通常起動用既定値」と「開発用 override」を分離する。
2. `run()` は `harite-gui` / `python -m harite.gui.app` から呼ばれた通常経路では `bind=True` / `present=True` を既定にし、明示 override があるときだけそれを優先する。
3. 既存の `--bind-ui-backend` / `--present-ui-window` は直ちに消さず、開発用 override として後方互換で残す。
4. env 変数は「通常起動の既定値を決める入口」ではなく、「開発用 override / 特殊環境用 escape hatch」へ格下げする。

### 変更対象

- [src/harite/gui/app.py](src/harite/gui/app.py)
  - `run()` の既定解決を見直し、通常起動で bind / present が有効になる制御点を作る。
  - `main()` の引数解決を見直し、no-option 実行時に `run()` へ通常起動モードを渡せるようにする。
  - `--bind-ui-backend` / `--present-ui-window` の help は、通常利用用ではなく override 用の説明に寄せる。
- [pyproject.toml](pyproject.toml)
  - `harite-gui = "harite.gui.app:run"` は no-option 化後の挙動に合うか確認が必要である。
  - `run()` をそのまま console script の入口に使うなら、通常起動既定を `run()` 側へ持たせるのが最短である。
  - もし CLI 引数整理を `main()` に集約したいなら、`harite-gui` の entrypoint を `harite.gui.app:main` へ寄せる案も比較対象になる。
- [tests/gui/test_app_entrypoint.py](tests/gui/test_app_entrypoint.py)
  - 現在の `None` 既定や flag 依存を前提にしたテストを、通常起動既定が bind / present に倒れる仕様へ更新する必要がある。
  - 少なくとも「no-option で backend bind と window present を試みる」「GTK 不可時でも non-fatal に fallback する」の 2 点は固定回帰にしたい。

### 先に固定したい仕様

- `harite-gui` は no-option で current GUI 起動を試みる正本導線にする。
- `python -m harite.gui.app` も同じく no-option で current GUI 起動を試みる補助導線として揃える。
- GTK / display が不足する環境では、現行どおり non-fatal に `window.show()` 側へ落ちる。
- 開発用 option / env override は残してよいが、README 正本導線からは外す。

### この案を崩し得る安価な確認点

- [pyproject.toml](pyproject.toml) の `harite-gui` が `run()` を直接呼ぶため、`main()` だけ直しても console script 側の no-option 化には効かない。
- したがって最初の実装判断は、「通常起動既定を `run()` に持たせるか」「entrypoint を `main()` へ差し替えるか」の二択である。
- 初手の安価な確認としては、[tests/gui/test_app_entrypoint.py](tests/gui/test_app_entrypoint.py) の console entrypoint 前提を壊さずにどちらが小さく済むかを比較すれば足りる。

### 実装方針の決定

- Phase10 初手では、「通常起動既定を `run()` に持たせる」案を採る。
- 採用理由は、[pyproject.toml](pyproject.toml) の `harite-gui` がすでに `harite.gui.app:run` を直接呼んでおり、この制御点を変えずに no-option 化できるためである。
- [src/harite/gui/app.py](src/harite/gui/app.py) を `python -m harite.gui.app` で起動した場合も最終的には `main()` から `run()` へ到達するため、`run()` 側に通常既定を置けば `harite-gui` と module 起動の両方を 1 箇所で揃えられる。
- repo 内の `app.run()` 直接呼び出しは実質 [tests/gui/test_app_entrypoint.py](tests/gui/test_app_entrypoint.py) に限られており、外部呼び出し面の広い互換負債は見えていない。
- 逆に `main()` 側へ寄せる案は、`harite-gui` の entrypoint を `harite.gui.app:main` へ差し替える追加変更が必要で、`run()` と `main()` の通常既定が分離しやすい。
- したがって Phase10 初手では、entrypoint 差し替えよりも「`run()` を正本起動制御点に昇格させる」方が、変更範囲・説明コスト・ docs 整合のいずれも小さい。

### 採らない案の扱い

- `main()` 側へ通常既定を寄せる案は、将来 `run()` を内部 API へ縮退させたい場合の再検討候補として残してよい。
- ただし現時点では、console script と module 起動の双方に対して制御点を二重化するだけになりやすく、Phase10 初手の目的に対して利得が薄い。
- 環境変数既定の復活余地はこの判断では見込まない。env は残すとしても開発用 override / escape hatch に限る。

### 2. 開発用 option をどう残すか

- `--bind-ui-backend` / `--present-ui-window` は削除候補ではあるが、Phase10 初手では即削除を前提にしない。
- 通常起動導線が成立したあと、開発用 / 検証用 option として残すのか、内部既定へ吸収して CLI からは隠すのかを決める。
- 非 fatal な safety net は維持しつつ、利用者向け説明では開発用 option と通常導線を混ぜない。

### 3. docs と manual validation をどう揃えるか

- README / phase validation 文書がいまは技術寄り bootstrap を前提にしている。
- Phase10 初手では README の正本導線整理を優先し、manual validation は製品整理が進んだ段階で思い出す補助文書として後段に回してよい。
- docs 更新は実装変更の後追いではなく、通常導線の定義と同時に README / roadmap を先に揃える。

## 初手の判断方針

- 通常起動導線は 1 本に寄せる。
- XFCE 正本運用を弱める変更はしない。
- fallback backend と non-fatal safety net は内部都合として残し得るが、利用者向け導線では露出を減らす。
- CLI 正式名 `harite` は維持しつつ、GUI 側は `harite-gui` または `harite gui` の no-option 起動成立を優先する。
- visual aid / icon は別メモへ送り、この文書では起動導線だけに集中する。

## 現時点の絞り込み

- Phase10 初手の論点は、実質 `harite-gui` と `harite gui` のどちらを README 上の正本 GUI 導線にするかへ収束していたが、現時点では `harite-gui` を採用候補として前へ進める判断になった。
- どちらを選ぶ場合でも、`--bind-ui-backend` / `--present-ui-window` を end user へ露出させないこと、XFCE を含む current GUI を追加 option なしで起動できることは共通要件である。
- したがって次はコマンド名の再比較ではなく、`harite-gui` を各環境で無理なく成立させる実装と docs 整備へ進む。

## 初動タスク

1. [src/harite/gui/app.py](src/harite/gui/app.py) の `run()` を通常起動の正本制御点として再設計する。
2. [tests/gui/test_app_entrypoint.py](tests/gui/test_app_entrypoint.py) で固定すべき no-option 起動回帰を列挙する。
3. README / roadmap のどこを `harite-gui` 正本導線として更新するか、更新対象一覧を作る。
4. visual aid / icon は別メモへ分離し、本書では未着手のままにする。

## 完了条件

- 通常起動導線の第一候補が 1 本に絞られている。
- README 上の正本 GUI 導線として `harite-gui` を採る理由が整理されている。
- `--bind-ui-backend` / `--present-ui-window` の扱いが、通常導線か開発用導線かで整理されている。
- XFCE で追加 option なし起動を実現するために必要な実装変更点と README / roadmap 更新点が列挙されている。
- visual aid / icon 論点を、この文書の外へ切り分ける方針が明記されている。

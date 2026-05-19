# Harite Project Initial Build Reformation Linux XDG Launcher

最終更新: 2026-05-19

## 位置づけ

- 本書は reformation 配下に置く補助メモであり、Workstream 3 の docs 再編と Workstream 4 の常設仕様記述の前段にある実装判断メモとして扱う。
- 主題は、Linux / XFCE 前提の tray / indicator 常駐導線を、`harite-gui &` のような terminal 起動前提から、ユーザー負荷の低い XDG launcher / autostart 導線へ寄せることである。
- これは `1.0.0` 前の大設計書ではなく、`feature/linux-xdg-launcher` で先に小さく進める実装イベントの判断材料として残す。

## 背景

- 現状の tray / indicator 常駐は、AyatanaAppIndicator / AppIndicator 側の runtime 実装自体は存在する。
- しかし end user が常用するには、terminal で `harite-gui` を起動し、必要なら `&` を付けてバックグラウンド実行にしておく導線から始まる。
- これは GUI 常用導線として見た目が悪く、Linux desktop の現在の期待とも合いにくい。
- 過去には `.desktop` ファイルを用意していた時期もあるが、OS 依存面であることから、現行 reformation 文脈では正面から整理されないまま残っていた。

## 現時点の判断

### 1. `harite-gui &` を正規導線にしない

- terminal から `&` を付けて常駐させる手順は、開発者や owner の手元確認には使えても、end user の主導線にはしない。
- README や将来の常設仕様で、この導線を常用前提として強く押し出さない。

### 2. Linux / XFCE の常用導線は XDG launcher を正面で採る

- Linux desktop で GUI アプリを terminal なしに起動させる導線としては、`.desktop` launcher が最も自然である。
- tray / indicator 自体がすでに OS integration である以上、launcher / autostart だけ OS 依存を避けても整理は良くならない。
- したがって Linux / XFCE first target の範囲では、XDG launcher を正規導線として扱うのが妥当である。

### 3. autostart は opt-in にする

- 常駐開始を login 時に自動化する場合は、`~/.config/autostart/` への `.desktop` 配置を明示 opt-in として扱う。
- package install の副作用で自動配置することはしない。
- 初回 GUI 起動後の案内、または settings / CLI からの明示操作で作成・削除する方針がよい。

## 推奨する着地

### 段階 1. user-local launcher 生成

- まずは terminal を開かずに Harite GUI を起動できる user-local launcher を作れるようにする。
- 想定配置先は XDG 準拠の launcher 配置先とし、`Exec=harite-gui`、`Terminal=false`、適切な icon を含む最小 `.desktop` を生成する。
- この段階では autostart まで一気に抱え込まず、「GUI を自然に起動できる」ことだけを最小スコープにする。

### 段階 2. login 時常駐の opt-in

- 次に、必要なら `~/.config/autostart/harite.desktop` を作成・削除する仕組みを足す。
- UI としては `Start on login` のような設定項目が自然だが、初手では CLI あるいは限定 UI でもよい。
- tray / indicator 常駐と autostart は関連するが、launcher 導線と分けて段階的に載せる。

### 段階 3. docs 反映

- 実装が固まった後に README、常設仕様、WS3 docs map へ反映する。
- 先に大きな設計書を起こすより、user-local launcher の実体を先に作ってから docs を寄せる方が手戻りが少ない。

## 推奨しない着地

- `harite-gui &` を常用導線として README や仕様書へ残すこと。
- wheel / pip install の副作用で `.desktop` や autostart を自動配置すること。
- tray 常駐 UI と headless watch daemon を最初から同一問題としてまとめること。

## headless 常駐との切り分け

- GUI を表示せず watch だけを継続させたい要望は将来的にあり得る。
- ただしそれは tray / indicator 常駐とは別問題であり、必要になった時点で `systemd --user` 等の user service として別に扱う方が整理しやすい。
- 今回の論点は GUI 常用導線であり、headless daemon 設計をここで先回りして抱え込まない。

## branch / 実装イベントとしての扱い

- 本件は docs だけを先に厚くするより、短い implementation event として扱う方がよい。
- branch 種別としては `chore` より `feature` が自然であり、`feature/linux-xdg-launcher` は妥当な命名である。
- 初手の実装スコープは「launcher 生成のみ」または「launcher + autostart opt-in」のどちらかに絞る。

## WS3 / WS4 との関係

- Workstream 3 では、本件を「Linux / XFCE の OS integration をどう常設 docs に位置づけるか」の具体例として扱える。
- Workstream 4 では、実装確定後に「通常 GUI 起動」「login 時常駐」「watch 常用導線」の正本説明へ落とし込む。
- したがって本件は、WS3/WS4 の前に小さく実装イベントとして進め、その結果を docs 側へ反映する順序がよい。

## 現時点の結論

- Linux / XFCE first target で tray / indicator 常駐を見せるなら、XDG launcher を正規導線として扱う。
- autostart は user が明示的に有効化する opt-in にする。
- 先に full 設計書を書くより、`feature/linux-xdg-launcher` で launcher 生成の最小実装を先に固める。
- 現段階では、段階 1 の user-local launcher 生成までを先に採る。
- 段階 2 の autostart は、責務を広げすぎないため現時点では入れず、将来側の論点として送る。
- README / README_en には段階 1 の導線のみを最小追記し、常用導線は `harite-gui` を維持する。
- テストと実機確認は後続で行えばよく、本件は急いで autostart まで抱え込まない。

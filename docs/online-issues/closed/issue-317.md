# Issue #317

- URL
  <https://github.com/oggy8021/Harite/issues/317>
- opened
  2026/5/26
- title
  スライドショーについて、サイクルごとにファイルが純増する仕様に戻ってしまうことがある。

## 事象

`issue #318` にて仕様書正本に追記した内容に関連し、スライドショーの実行過程を追跡していたところ、 `interval_sec` ごとに生成される `Optimize` 後のファイル について、ファイル名を再クリックに使わずに純増する状態に戻ってしまう時間帯が発生した

```shell
-rw-rw-r-- 1 katsu katsu 757K  5月 26 01:57 harite_output_0001.jpg
-rw-rw-r-- 1 katsu katsu 733K  5月 26 02:57 harite_output_0002.jpg
-rw-rw-r-- 1 katsu katsu 791K  5月 26 03:57 harite_output_0003.jpg
-rw-rw-r-- 1 katsu katsu 757K  5月 26 04:57 harite_output_0004.jpg
-rw-rw-r-- 1 katsu katsu 791K  5月 26 05:58 harite_output_0005.jpg
-rw-rw-r-- 1 katsu katsu 613K  5月 26 06:57 harite_output_0006.jpg
-rw-rw-r-- 1 katsu katsu 741K  5月 26 07:58 harite_output_0007.jpg
-rw-rw-r-- 1 katsu katsu 663K  5月 26 13:57 harite_output_0009.jpg
-rw-rw-r-- 1 katsu katsu 371K  5月 26 13:58 harite_output_0009_DP-1.jpg
-rw-rw-r-- 1 katsu katsu 289K  5月 26 13:57 harite_output_0009_HDMI-1.jpg
```

ただし、lsを眺めると 8:00以降は問題ないようにも見える。引き続き観察を行ったところ、以下のファイルリスト挙動となった。

```shell
-rw-rw-r-- 1 katsu katsu 682K  5月 26 22:53 harite_output_0001.jpg
-rw-rw-r-- 1 katsu katsu 807K  5月 27 12:23 harite_output_0002.jpg
-rw-rw-r-- 1 katsu katsu 789K  5月 27 00:23 harite_output_0003.jpg
-rw-rw-r-- 1 katsu katsu 733K  5月 27 00:53 harite_output_0004.jpg
-rw-rw-r-- 1 katsu katsu 757K  5月 27 01:23 harite_output_0005.jpg
-rw-rw-r-- 1 katsu katsu 663K  5月 27 01:53 harite_output_0006.jpg
-rw-rw-r-- 1 katsu katsu 741K  5月 27 02:23 harite_output_0007.jpg
-rw-rw-r-- 1 katsu katsu 721K  5月 27 02:53 harite_output_0008.jpg
-rw-rw-r-- 1 katsu katsu 738K  5月 27 03:23 harite_output_0009.jpg
-rw-rw-r-- 1 katsu katsu 819K  5月 27 03:53 harite_output_0010.jpg
-rw-rw-r-- 1 katsu katsu 688K  5月 27 04:23 harite_output_0011.jpg
-rw-rw-r-- 1 katsu katsu 733K  5月 27 04:53 harite_output_0012.jpg
-rw-rw-r-- 1 katsu katsu 613K  5月 27 05:23 harite_output_0013.jpg
-rw-rw-r-- 1 katsu katsu 810K  5月 27 05:53 harite_output_0014.jpg
-rw-rw-r-- 1 katsu katsu 819K  5月 27 06:23 harite_output_0015.jpg
-rw-rw-r-- 1 katsu katsu 741K  5月 27 06:53 harite_output_0016.jpg
-rw-rw-r-- 1 katsu katsu 798K  5月 27 07:23 harite_output_0017.jpg
-rw-rw-r-- 1 katsu katsu 733K  5月 28 00:23 harite_output_0018.jpg
-rw-rw-r-- 1 katsu katsu 733K  5月 27 12:53 harite_output_0019.jpg
-rw-rw-r-- 1 katsu katsu 699K  5月 27 13:23 harite_output_0020.jpg
-rw-rw-r-- 1 katsu katsu 712K  5月 27 13:53 harite_output_0021.jpg
-rw-rw-r-- 1 katsu katsu 738K  5月 27 14:23 harite_output_0022.jpg
-rw-rw-r-- 1 katsu katsu 802K  5月 27 14:53 harite_output_0023.jpg
-rw-rw-r-- 1 katsu katsu 738K  5月 27 15:23 harite_output_0024.jpg
-rw-rw-r-- 1 katsu katsu 733K  5月 27 15:53 harite_output_0025.jpg
-rw-rw-r-- 1 katsu katsu 789K  5月 27 16:23 harite_output_0026.jpg
-rw-rw-r-- 1 katsu katsu 733K  5月 27 16:53 harite_output_0027.jpg
-rw-rw-r-- 1 katsu katsu 827K  5月 27 17:23 harite_output_0028.jpg
-rw-rw-r-- 1 katsu katsu 721K  5月 27 17:53 harite_output_0029.jpg
-rw-rw-r-- 1 katsu katsu 699K  5月 27 18:23 harite_output_0030.jpg
-rw-rw-r-- 1 katsu katsu 721K  5月 27 18:53 harite_output_0031.jpg
-rw-rw-r-- 1 katsu katsu 741K  5月 27 19:23 harite_output_0032.jpg
-rw-rw-r-- 1 katsu katsu 802K  5月 27 19:53 harite_output_0033.jpg
-rw-rw-r-- 1 katsu katsu 720K  5月 27 23:23 harite_output_0034.jpg
-rw-rw-r-- 1 katsu katsu 733K  5月 28 17:53 harite_output_0035.jpg
-rw-rw-r-- 1 katsu katsu 738K  5月 28 00:53 harite_output_0036.jpg
-rw-rw-r-- 1 katsu katsu 798K  5月 28 01:23 harite_output_0037.jpg
-rw-rw-r-- 1 katsu katsu 770K  5月 28 01:53 harite_output_0038.jpg
-rw-rw-r-- 1 katsu katsu 733K  5月 28 02:23 harite_output_0039.jpg
-rw-rw-r-- 1 katsu katsu 613K  5月 28 02:53 harite_output_0040.jpg
-rw-rw-r-- 1 katsu katsu 781K  5月 28 03:23 harite_output_0041.jpg
-rw-rw-r-- 1 katsu katsu 733K  5月 28 03:53 harite_output_0042.jpg
-rw-rw-r-- 1 katsu katsu 741K  5月 28 04:23 harite_output_0043.jpg
-rw-rw-r-- 1 katsu katsu 713K  5月 28 04:53 harite_output_0044.jpg
-rw-rw-r-- 1 katsu katsu 807K  5月 28 05:23 harite_output_0045.jpg
-rw-rw-r-- 1 katsu katsu 613K  5月 28 05:53 harite_output_0046.jpg
-rw-rw-r-- 1 katsu katsu 721K  5月 28 06:23 harite_output_0047.jpg
-rw-rw-r-- 1 katsu katsu 757K  5月 28 06:53 harite_output_0048.jpg
-rw-rw-r-- 1 katsu katsu 741K  5月 28 07:23 harite_output_0049.jpg
-rw-rw-r-- 1 katsu katsu 807K  5月 28 07:53 harite_output_0050.jpg
-rw-rw-r-- 1 katsu katsu 733K  5月 28 19:23 harite_output_0052.jpg
-rw-rw-r-- 1 katsu katsu 712K  5月 28 19:53 harite_output_0053.jpg
-rw-rw-r-- 1 katsu katsu 613K  5月 28 20:23 harite_output_0054.jpg
-rw-rw-r-- 1 katsu katsu 819K  5月 28 20:53 harite_output_0055.jpg
-rw-rw-r-- 1 katsu katsu 791K  5月 28 21:23 harite_output_0056.jpg
-rw-rw-r-- 1 katsu katsu 371K  5月 28 21:23 harite_output_0056_DP-1.jpg
-rw-rw-r-- 1 katsu katsu 418K  5月 28 21:23 harite_output_0056_HDMI-1.jpg
```

- 一度エクスプローラーにて生成後ファイルを削除して、`001` からとなるようにスライドショーを `3600s` 間隔で開始したが、何かの拍子にデフォルト値か設定値由来の `1800s` サイクルになってしまった。スライドショーが継続不可能となったときにおける再開機能において、設定値等の再利用がなされていないと考えられる。
- `two-screen`, `auto-split` 挙動を取るときと取らないときがある？都度、消しているから最新だけ残る？
  これは一部、 `issue #318` の対処時に明らかにしてもらったが、採番再利用の場面が限られることが影響していると分かった。
- resolution (2026-05-30, 仕様)
  - 純増の解析: pause tick・未追跡 orphan・手動 Optimize との採番競合 → `harite-slideshow-spec.md` §6.3。
  - 出力分離（R5）: 案 A 採用 — slideshow 作業は `{XDG_PICTURES_DIR}/Harite/slideshow/`。`XDG_CACHE_HOME` は不採用（xfconf 壁紙実体の非揮発性のため）。§6.1 / GUI spec §6 表を追記。
  - 対応方針: 要件 **R1–R5 はすべて実装する**。§6.2 に目標挙動（固定スロット・tick rollback・掃除）を記載。実装は未達。
  - R4 確定: stop 時はスロットファイルを削除しない。追跡 state のみクリア。

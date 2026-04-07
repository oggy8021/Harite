# Enumerator fixes applied

## docs\docs-consolidation-enumerator-fix.md

```diff
--- docs\docs-consolidation-enumerator-fix.md
+++ docs\docs-consolidation-enumerator-fix.md (fixed)
@@ -533,16 +533,16 @@
    - `apply(path_or_map, *, dry_run=True)` を受け、`path_or_map` が dict のときはキーをモニタ識別子（xrandr の `name`）として扱う。
    - 文字列のときは従来の全体適用。
  - XFCE プロパティの割当アルゴリズム
--  1。`xrandr` で得た `Display.name`（例: `DP-1`）をモニタ候補表示名として使用。候補として `monitor{NAME}`（例: `monitorDP-1`）をプロパティ名にマッチさせる。
--  2。`xfconf-query -c xfce4-desktop -l` の出力からプロパティリストを得る（既存処理）。
--  3。優先ルール:
+-  1.`xrandr` で得た `Display.name`（例: `DP-1`）をモニタ候補表示名として使用。候補として `monitor{NAME}`（例: `monitorDP-1`）をプロパティ名にマッチさせる。
+-  2.`xfconf-query -c xfce4-desktop -l` の出力からプロパティリストを得る（既存処理）。
+-  3.優先ルール:
 +  1.`xrandr` で得た `Display.name`（例: `DP-1`）をモニタ候補表示名として使用。候補として `monitor{NAME}`（例: `monitorDP-1`）をプロパティ名にマッチさせる。
 +  2.`xfconf-query -c xfce4-desktop -l` の出力からプロパティリストを得る（既存処理）。
 +  3.優先ルール:
       - monitor 固有 (/monitor.../) にマッチするプロパティへまず書き込む。
       - 次に workspace ベースの `.../workspaceX/last-image` へ書き込む（各ワークスペースに対して同じファイルを設定）。
       - どのプロパティも見つからない場合は `last-image` / `last-single-image` の一般エントリへフォールバック。
--  4。書き込み実行:
+-  4.書き込み実行:
 +  4.書き込み実行:
       - `dry_run=True` の場合は実行予定コマンドをログに残すのみ。
       - `dry_run=False` の場合は、モニタ別に見つかったすべてのプロパティに対して `xfconf-query -p <prop> -s <path>` を実行し、個別の成功/失敗をログに残す。最終的には一つでも成功すれば True を返すが、個別失敗は debug/info ログで確認できるようにする。

```

## docs\docs-consolidation-replacements-applied.md

```diff
--- docs\docs-consolidation-replacements-applied.md
+++ docs\docs-consolidation-replacements-applied.md (fixed)
@@ -687,17 +687,17 @@
    - `apply(path_or_map, *, dry_run=True)` を受け、`path_or_map` が dict のときはキーをモニタ識別子（xrandr の `name`）として扱う。
    - 文字列のときは従来の全体適用。
  - XFCE プロパティの割当アルゴリズム
--  1。`xrandr` で得た `Display.name`（例: `DP-1`）をモニタ候補表示名として使用。候補として `monitor{NAME}`（例: `monitorDP-1`）をプロパティ名にマッチさせる。
--  2。`xfconf-query -c xfce4-desktop -l` の出力からプロパティリストを得る（既存処理）。
--  3。優先ルール:
-+  1。`xrandr` で得た `Display.name`（例: `DP-1`）をモニタ候補表示名として使用。候補として `monitor{NAME}`（例: `monitorDP-1`）をプロパティ名にマッチさせる。
-+  2。`xfconf-query -c xfce4-desktop -l` の出力からプロパティリストを得る（既存処理）。
-+  3。優先ルール:
+-  1.`xrandr` で得た `Display.name`（例: `DP-1`）をモニタ候補表示名として使用。候補として `monitor{NAME}`（例: `monitorDP-1`）をプロパティ名にマッチさせる。
+-  2.`xfconf-query -c xfce4-desktop -l` の出力からプロパティリストを得る（既存処理）。
+-  3.優先ルール:
++  1.`xrandr` で得た `Display.name`（例: `DP-1`）をモニタ候補表示名として使用。候補として `monitor{NAME}`（例: `monitorDP-1`）をプロパティ名にマッチさせる。
++  2.`xfconf-query -c xfce4-desktop -l` の出力からプロパティリストを得る（既存処理）。
++  3.優先ルール:
       - monitor 固有 (/monitor.../) にマッチするプロパティへまず書き込む。
       - 次に workspace ベースの `.../workspaceX/last-image` へ書き込む（各ワークスペースに対して同じファイルを設定）。
       - どのプロパティも見つからない場合は `last-image` / `last-single-image` の一般エントリへフォールバック。
--  4。書き込み実行:
-+  4。書き込み実行:
+-  4.書き込み実行:
++  4.書き込み実行:
       - `dry_run=True` の場合は実行予定コマンドをログに残すのみ。
       - `dry_run=False` の場合は、モニタ別に見つかったすべてのプロパティに対して `xfconf-query -p <prop> -s <path>` を実行し、個別の成功/失敗をログに残す。最終的には一つでも成功すれば True を返すが、個別失敗は debug/info ログで確認できるようにする。
  

```

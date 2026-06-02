# GUI Resources

このディレクトリは current runtime が直接利用する GUI リソースの配置先です。

## 現状

- legacy glade 原本は docs/legacy-ui/ を参照する
- Phase6 では glade prototype 前提を撤去したため、wallpositapplet.glade の実装側コピーは保持しない

## 方針

1. legacy UI の証跡は docs/legacy-ui にのみ置く
2. current runtime で使う資産だけをこのディレクトリに置く
3. signal や layout の追跡は docs/specs/gui/ の文書で管理する
4. product icon のような runtime asset は package 内 resource としてここへ置く
5. runtime からは importlib.resources 経由で参照し、docs/mock asset とは混線させない
6. source preset は `source_presets/harite-source-presets.json`（[source-spec §15](../../../docs/specs/source/harite-source-spec.md)）

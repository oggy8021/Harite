**概要**

- このドキュメントは `tests/core/test_core_features.py` と `tests/core/test_core_edgecases.py` の目的と実行方法を説明します。

**目的**

- リポジトリのコア機能（壁紙最適化、画像配置、複合画像のディスプレイ分割）に対する代表的かつ詳細なユニットテストを提供します。
- 目的は「クラッシュや主要な回帰を早期に検出すること」です。UI や外部依存はモックするか小さなファイルで代替しています。

**含まれるテスト**

- `tests/core/test_core_features.py`
  - スモークおよび代表的な動作検証：`optimize_wallpapers`、`compute_placement`、`split_composite_for_displays` の基本動作。
- `tests/core/test_core_edgecases.py`
  - エッジケース検証：透過 PNG、非常に大きな画像、アップスケールの取り扱い、オフスクリーン（x_offset が合成画像範囲外）のディスプレイ処理。

**実行方法（ローカル）**

1. 仮想環境を有効化
   - Windows PowerShell:

```
& .venv\Scripts\Activate.ps1
```
1. 依存をインストール（未インストール時）

```
python -m pip install -r requirements-dev.txt
```
1. テスト実行

```
python -m pytest -q
```

**CI の注意点**

- 重い画像処理テストは最初は軽量（小さな画像）で書かれているため通常の CI で問題なく通る想定です。将来的に重い I/O を増やす場合は、`slow` マーカを付けて分離ジョブに移すことを推奨します。

**補足**

- 追加したテストは代表的シナリオとエッジケースをカバーしますが、アルゴリズムの完全な網羅を保証するものではありません。特定の回帰や環境差異が懸念される場合、該当機能に対して追加テストを段階的に追加してください。

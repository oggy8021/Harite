# Harite

Harite — 壁紙最適化ツール（リファクタリング版）

## 概要

Harite は、マルチディスプレイ環境で壁紙画像を生成・配置・適用するためのツールです。複数の入力画像から壁紙を作成し、画面ごとの配置、余白、固定配置、単画面利用を扱えます。

## CLI 例

基本的な使い方:

```bash
harite optimize --input left.jpg,right.jpg --resolution 3840x1080 \
 --two-screen --l-display 1920x1080 --r-display 1920x1080 \
 --margins 10,10,5,5 --fixed --output ./out
```

詳細オプションは `harite optimize --help` を参照してください。

## GUI 起動

```bash
harite-gui
```

`harite-gui` は host 環境側の GTK 3 / PyGObject runtime を前提にします。Linux / XFCE では少なくとも `python3-gi` と GTK 3 系ライブラリが利用可能であることを確認してください。

Linux / XFCE でアプリケーションメニューから起動したい場合は、user-local の launcher を生成できます。

```bash
harite install-desktop-entry
```

## 外部依存（システムツール）

Harite 本体は Python パッケージですが、XFCE での壁紙設定やディスプレイ検出では外部ツールを利用することがあります。

- 必須:
  - Python 3.12+（pyproject.toml に指定）
  - Python パッケージ: `typer`, `Pillow`（`pip install -e .` でインストール）

- XFCE 利用時:
  - `xrandr` — ディスプレイ情報の取得に使うことがあります。
  - `xfconf-query` — 壁紙設定に使うことがあります。
  - `python3-gi` と GTK 3 runtime — `harite-gui` の起動に必要です。

XFCE では、これらが利用可能であることを前提に考えてください。

## License

Harite 本体は MIT License です。配布物には [LICENSE](LICENSE) を含めます。

GUI で同梱している Lucide SVG icon については upstream notice を別途保持します。詳細は [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) を参照してください。

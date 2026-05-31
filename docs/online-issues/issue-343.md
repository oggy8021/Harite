# Issue #343

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/343>
- opened: 2026-05-31
- title: `Windows) Apply周辺にて、以下のOS機能群との関係精査が必要`

## 背景・論点

不具合というより、**Windows で Qt 環境が動くようになったこと**を契機に Apply / optimize まわりを再検討するテーマ。

### Windows の壁紙表示方式（OS 設定）

| UI 表示名（日本語） | 一般的な英名 | WallpaperStyle | TileWallpaper |
| --- | --- | --- | --- |
| ページ幅に合わせる | Fit | 6 | 0 |
| 画面のサイズに合わせる | Stretch | 2 | 0 |
| 拡大して表示 | Fill | 10 | 0 |
| 並べて表示 | Tile | 0 | 1 |
| 中央に表示 | Center | 0 | 0 |
| スパン | Span | 22 | 0 |

> **注意:** UI ラベルと `WallpaperStyle` 値の対応は Windows バージョンで表記が揺れる。Harite が触る前に **実機で regedit 確認** すること。

保存先: `HKEY_CURRENT_USER\Control Panel\Desktop` の `WallpaperStyle`, `TileWallpaper`。

### Harite 現状

- 過去から **OS 側の Fit/Fill 等はユーザー任せ**。Harite は Apply → plugin で画像 path を渡すまで（[plugin-spec §4.1](../specs/plugins/harite-plugin-spec.md)）。
- Windows plugin は `SystemParametersInfoW(SPI_SETDESKWALLPAPER, ...)` で **ファイル差し替えのみ**。
- OS が設定する **背景色** は Harite の壁紙と重畳しうる。

### 判断メモ（オーナー）

| 論点 | 有力案 |
| --- | --- |
| 背景色 | **ノータッチ**（最小案）。Harite 壁紙と独立 |
| Fit/Fill 等 | レジストリ変更まで手を伸ばすか **要判断**（工数・テスト・ユーザー期待） |
| 解像度検出 | **W-03-C 先行** — GTK/Linux の `detect_displays` 経路を参考に Windows 強化。完了後に A/B を判断 |

方針候補の整理は [working backlog W-03](../working/20260531-1200-windows-qt-validation-backlog.md) を参照。

## 分類

- **investigation** / **planning**（spec 改訂前）

## 関連

- backlog: [docs/working/20260531-1200-windows-qt-validation-backlog.md](../working/20260531-1200-windows-qt-validation-backlog.md)（W-03）
- [#341](issue-341.md) Windows slideshow
- 正本: [harite-plugin-spec.md](../specs/plugins/harite-plugin-spec.md) §4.1

## 取り込み方針

| 項目 | 判断 |
| --- | --- |
| 実施順 | **C → A/B**。C（解像度検出）を GTK 実装参考で可能なら先行。A/B（Apply / 壁紙 Fit/Fill 等）は C 後 |
| spec | 正本ライティング時に **plugin 層のディスプレイ名補完** の表現範囲を相談 |
| 次アクション | W-03-C: core-spec / workspace 契約のドラフト → テスト → `_detect_windows` 強化 PR |

---

## 調査メモ（外部・未検証）

以下は AI 調査の整理。Microsoft Learn 等へのリンク含む。**Harite 公式見解ではない。**

### 1. 壁紙ファイルの設定 — `SystemParametersInfoW`

- 公式: [SystemParametersInfoW (Microsoft Learn)](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-systemparametersinfow)
- 壁紙 path 設定: `SPI_SETDESKWALLPAPER` (= 20)

```c
SystemParametersInfoW(
    SPI_SETDESKWALLPAPER,
    0,
    L"C:\\wallpaper.jpg",
    SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE
);
```

| 設定項目 | SystemParametersInfoW |
| --- | --- |
| 壁紙ファイル | ○ |
| 壁紙の再読込 | ○ |
| Fit / Fill / Stretch / Tile / Center / Span | **×**（引数なし） |

→ 表示方式は **別経路（レジストリ等）** が必要。Harite Windows plugin の現行実装はここまで。

### 2. 表示方式 — レジストリ + 再適用

```powershell
Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name WallpaperStyle -Value "10"
Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name TileWallpaper -Value "0"
rundll32.exe user32.dll,UpdatePerUserSystemParameters
```

cmd 例:

```cmd
reg add "HKCU\Control Panel\Desktop" /v WallpaperStyle /t REG_SZ /d 10 /f
reg add "HKCU\Control Panel\Desktop" /v TileWallpaper /t REG_SZ /d 0 /f
```

典型的な Apply フロー（外部ツール一般）:

```text
レジストリで WallpaperStyle / TileWallpaper を設定
    ↓
SystemParametersInfoW(SPI_SETDESKWALLPAPER) または UpdatePerUserSystemParameters
```

GUI の「背景」設定変更も、利用者目線では上記キーに反映される（内部実装は OS 依存）。

### 3. 解像度・マルチモニタ検出

**プライマリ解像度（PowerShell）:**

```powershell
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Screen]::PrimaryScreen.Bounds
```

**全ディスプレイ:**

```powershell
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Screen]::AllScreens |
  Select-Object DeviceName,
    @{N="Width";E={$_.Bounds.Width}},
    @{N="Height";E={$_.Bounds.Height}},
    Primary
```

**WMIC（レガシー）:**

```cmd
wmic path Win32_VideoController get CurrentHorizontalResolution,CurrentVerticalResolution
```

**モニタ製品名（WMI）:**

```powershell
Get-CimInstance -Namespace root\wmi -Class WmiMonitorID
```

→ per-monitor apply や Span 自動判定の材料になりうる。Harite への取り込みは W-03 方針確定後。

### 5. オーナー実機確認（2026-05-31）

**`Screen.AllScreens`（2 枚構成）:**

```text
DeviceName   Width Height Primary
\\.\DISPLAY1  2560   1440    True
\\.\DISPLAY2  2560   1440   False
```

**WMI 製品名（参考）:**

```text
DELL S2721QS
DELL U2720QM
```

**判断（W-03-C ベースロジック）:**

| 方式 | 採用 | 理由 |
| --- | --- | --- |
| `DeviceName`（`\\.\DISPLAY1` 等）+ bounds + Primary | **ベース** | Linux の `HDMI-1` / `DP-1` と同様、論理デバイス名として汎用。`display_context.order_displays` は **x_offset / y_offset**（`Bounds.X` / `Bounds.Y`）で左右順を決められる |
| WMI `UserFriendlyName`（製品名） | **予備・別レイヤ** | Auto-Split 出力ファイル名の部分文字列候補（Linux xfconf 対応付けに近い用途）としては検討余地があるが、**左右・DISPLAY 対応は取れない**（類似製品名では特に不可） |
| two-screen / auto-split 全体 | **条件付き** | 検出強化後も apply 面（Windows plugin 単一画像）と切り離して判断。難しければ廃案も残す |

- **解像度検知（W-03-C）** と **製品名 WMI** は独立して設計する（同一 PowerShell スタックから得られても、Harite では別 concern）。
- 実装時は PowerShell ではなく **`workspace._detect_windows()` 内の Win32 API**（`EnumDisplayMonitors` / `MONITORINFOEX` 等、`Screen.AllScreens` と同等）を想定。core は Qt / PowerShell 非依存を維持。

### 4. Harite 実装との差分メモ

| 領域 | 現行 Harite | 調査で見える OS 能力 |
| --- | --- | --- |
| 壁紙 path | plugin が SPI 呼び出し | 一致 |
| Fit/Fill 等 | 未制御 | レジストリ + 再 Apply |
| マルチモニタ optimize | Linux 中心。Windows は単一 auto 解像度の強化あり | Screen API / WMI |
| 背景色 | 未制御 | OS 設定と独立管理が最小 |

---

## resolution

（未解決。方針確定後に追記）

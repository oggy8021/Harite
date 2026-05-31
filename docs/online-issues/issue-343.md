# Issue #343

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/343>
- opened: 2026-05-31
- **closed: 2026-05-31**（W-03 完了 — 背景色は Harite 管轄外として不問）
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

- ~~investigation / planning~~ → **resolved**（W-03 完了, 2026-05-31）

## 関連

- backlog: [docs/working/20260531-1200-windows-qt-validation-backlog.md](../working/20260531-1200-windows-qt-validation-backlog.md)（W-03）
- [#341](issue-341.md) Windows slideshow
- 正本: [harite-plugin-spec.md](../specs/plugins/harite-plugin-spec.md) §4.1

## 取り込み方針

| 項目 | 判断 |
| --- | --- |
| 実施順 | **C → B-lite 完了**。B-full（Fit/Fill 全面制御）は **不採用** |
| 背景色 | **Harite 管轄外（不問）** — OS 設定のまま。plugin は壁紙 file path のみ |
| spec | W-03-C / B-lite / W-02 は正本反映済 |
| 次アクション | **なし**（本 Issue クローズ） |

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

### W-03-C（完了）

- PR #349: `EnumDisplayMonitors`、物理解像度、`scale_percent`、Qt Optimize 結果ラベル修正。

### W-03-B-lite（オーナー採択 2026-05-31）

**目標:** Linux Auto-Split と **見え方は同じ**（左右意図どおり）。Windows 実現は **仮想解像度 1 枚 + OS Span**（per-monitor map は約束しない）。

**実機:** 7680×1280 合成 + OS **スパン** で意図どおり。**並べて表示（Tile）は非推奨**（片側だけ・無駄メモリ）。

| 項目 | 方針 |
| --- | --- |
| ベース | **A** — 既定は registry 非触 |
| opt-in | Settings **`windows_apply_span`** — 有効時のみ Apply で Span（22）設定 |
| Span 選択 | Main タブ **Span** ラベル（旧 Auto-Split）。2 枚以上で **Span 既定**。No Split も選択可 |
| Span 選択の意味 | Apply 時 Span 切替への **同意**（opt-in 時） |
| 復元 | **自動復元は見送り**（slideshow 中の復元で表示崩れ。異常終了も不可） |
| プレビュー | **B'** — 疑似クロップ + 「monitor region」文言（Linux 用語を出さない） |
| slideshow | wide composite + Span（opt-in 時は registry 維持）。**W-02 完了**（#355 + #356） |

**~~未着手（W-02）~~:** slideshow-spec / gui-spec §6 Windows dual-source 追記、`_prepare_slideshow_apply` ゲート解除 — **完了**（#355 + #356）。

### W-03-B-lite（完了 — PR #352）

**目標:** Linux Auto-Split と **見え方は同じ**（左右意図どおり）。Windows 実現は **仮想解像度 1 枚 + OS Span**（per-monitor map は約束しない）。

**実装:** `apply_surface`, `windows_wallpaper`, `resolve_apply_settings` Windows 分岐, GUI Span ラベル, Settings `windows_apply_span`, slideshow tick 内 Span 分岐。**slideshow start ゲート解除は W-02 #356。**

**追補（#352 マージ後）:** Qt preview pixmap 接続、Settings Save の `Path` 受け付け。

### 背景色（不問 — 2026-05-31 確定）

- Windows のデスクトップ **背景色**（「背景」設定）は OS が管理する。Harite の壁紙画像と視覚的に重畳しうるが、**Harite は制御しない**。
- plugin 契約は従来どおり **壁紙 file path の差し替え**（`SPI_SETDESKWALLPAPER`）まで。背景色 API / registry は対象外。
- 正本: [plugin-spec §4.1](../specs/plugins/harite-plugin-spec.md)。

### B-full（Fit/Fill / Stretch / Tile / Center 全面制御）— 不採用

- registry で `WallpaperStyle` / `TileWallpaper` を Harite が全面管理する案は **見送り**（B-lite の Span opt-in のみ採用）。
- ユーザーは OS の「背景」設定で Fit/Fill 等を選ぶ従来モデルを維持。

### Issue クローズ（2026-05-31）

| 論点 | 結果 |
| --- | --- |
| W-03-C 解像度検出 | **完了** #349 |
| W-03-B-lite Span Apply | **完了** #350 + #352 |
| W-02 slideshow Windows | **完了** #355 + #356（[#341](issue-341.md) 参照） |
| 背景色 | **不問**（上記） |
| B-full Fit/Fill 制御 | **不採用** |

**GitHub:** Issue #343 クローズ。Windows Qt 検証 backlog（W-03）完了。

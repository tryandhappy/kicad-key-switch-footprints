# Key Switches

[:globe_with_meridians:中文](/readme_zh-TW.md)

This is a [KiCad](https://www.kicad.org/) footprint library of mechanical keyboard switches, released under the [CERN-OHL-P v2](/LICENSE).

## ★ このフォーク限定: プレートのカット線（上流には無い。2026-08-29）

**33 個すべての `.kicad_mod` に、キーボードプレート加工用のカット線
（`fp_rect`、原点中心、線幅 0.05mm）を追加してある。** 各ファイルには
そのスイッチに該当するレイヤだけが入っている（`descr` フィールドにも同じ対応を記載）:

| レイヤ | 開口 | 対象スイッチ | 入っているファイル |
|---|---|---|---|
| `User.1` | **15.60mm 角** | 化粧カバー（スイッチを掴まない。全スイッチ共通） | 全 33 ファイル |
| `User.2` | **14.00mm 角** | **MX / MX Low Profile / Gateron Low Profile** | `SW_MX_*` `SW_Gateron_*`（21） |
| `User.3` | **13.95mm 角** | **Kailh Choc V2（PG1353）** | `*Choc_V2*` `*Choc_V1V2*`（9） |
| `User.4` | **13.80mm 角** | **Kailh Choc V1（PG1350）** | `*Choc_V1_*` `*Choc_V1V2*`（15） |

- **レイヤ＝プレート案の排他選択。** 書き出すレイヤを 1 つ選べばプレートの種類が決まる。
  ハイブリッド系のフットプリントには該当レイヤが複数入っているが、共存してよい
- **MX 系はすべて 14.00mm 角**（通常の Gateron は MX クローンで `SW_MX_*` を使う。
  低背 2 種も開口は同じだが、推奨プレート厚が違う: Gateron LP は 1.2mm）
- **★ 13.95 と 14.00 の差 0.05mm は JLCPCB のルーター公差（±0.2mm）より小さく、
  実物で区別できない可能性が高い。** 実物比較で差が出なければ V2 も 14.00 に寄せて
  `User.3` を廃止してよい（緩くなる側なので安全）。値の変更は各ファイル数字 1 か所
- **出典**: Choc V1=13.80 / V2=13.95 は
  [cyril279/keyboards revlp/41_1353](https://github.com/cyril279/keyboards/blob/main/revlp/41_1353/README.md)、
  Gateron LP の 14.00 は公式データシートの取付図
  （[KS-27](https://www.gateron.co/pages/gateron-low-profile-mechanical-switch-datasheet) /
  [KS-33](https://www.gateron.co/pages/gateron-ks-33-low-profile-2-0-mechanical-switch-datasheet)）、
  Cherry MX LP が 14×14 に入ることは
  [Deskthority wiki](https://deskthority.net/wiki/Cherry_MX_Low_Profile)
- **検証**: KiCad 10.0.5 の `kicad-cli fp export svg` で 33 ファイル全部のパースを確認済み。
  DXF 書き出しは 20° 回転を含む配置で `User.1/2/3` から 15.600 / 14.000 / 13.950mm が
  出ることを確認済み（線幅は書き出しに出ないので値は自由に変えてよい）
- `preview/` の画像もカット線入りで再生成してある
  （`kicad-cli fp export svg` + 黒背景化。ベースは上流コミット `b4afad5`）

以下は上流（siderakb/key-switches.pretty）の README のまま。

## Usage

It is recommended to use this library with [KiCAD KLE Placer](https://github.com/zykrah/kicad-kle-placer) or [kicad-kbplacer](https://github.com/adamws/kicad-kbplacer) for automatic switch placement.

If you're using Git, you can include this library as a [submodule](https://git-scm.com/docs/git-submodule) via `git submodule add https://github.com/siderakb/key-switches.pretty.git`

Keyboards created using this library: [ErgoSNM](https://github.com/siderakb/ergo-snm-keyboard), [Calcite](https://github.com/siderakb/calcite), [MS60](https://github.com/siderakb/ms60).

## Compatibility Table

|          Preview [^preview]          | Footprint [^sw-prefix]                   |         Cherry MX         | Cherry MX Low Profile |         TTC KS32         |  Kailh Choc V1 [^k-choc1]   |  Kailh Choc V2 [^k-choc2]  | Gateron Low Profile [^g-lp] |     THT [^tht]     |      Hot-Swap      | *nSilk* variants [^ns-suffix] | *swap* variants [^swap-suffix] |
| :----------------------------------: | ---------------------------------------- | :-----------------------: | :-------------------: | :----------------------: | :-------------------------: | :------------------------: | :-------------------------: | :----------------: | :----------------: | :---------------------------: | :----------------------------: |
| ![](./preview/SW_MX_THT.svg) | MX_THT                                   |    :white_check_mark:     |                       |                          |                             |                            |                             | :white_check_mark: |                    |      :white_check_mark:       |                                |
| ![](./preview/SW_MX_HotSwap_THT.svg) | MX_HotSwap_THT                           |    :white_check_mark:     |                       |                          |                             |                            |                             | :white_check_mark: | :white_check_mark: |      :white_check_mark:       |                                |
| ![](./preview/SW_MX_HotSwap_THT_double.svg) | MX_HotSwap_THT_double                    |    :white_check_mark:     |                       |                          |                             |                            |                             | :white_check_mark: | :white_check_mark: |                               |                                |
| ![](./preview/SW_MX_HotSwap_THT_double_alt1.svg) | MX_HotSwap_THT_double_alt1               |    :white_check_mark:     |                       |                          |                             |                            |                             | :white_check_mark: | :white_check_mark: |                               |                                |
| ![](./preview/SW_MX_HotSwap_THT_double_alt2.svg) | MX_HotSwap_THT_double_alt2               |    :white_check_mark:     |                       |                          |                             |                            |                             | :white_check_mark: | :white_check_mark: |                               |                                |
| ![](./preview/SW_MX_HotSwap_PTH.svg) | MX_HotSwap_PTH                           |    :white_check_mark:     |                       |                          |                             |                            |                             |   :bulb: [^pth]    | :white_check_mark: |      :white_check_mark:       |       :white_check_mark:       |
| ![](./preview/SW_MX_HotSwap_PTH_double.svg) | MX_HotSwap_PTH_double                    |    :white_check_mark:     |                       |                          |                             |                            |                             |   :bulb: [^pth]    | :white_check_mark: |                               |                                |
| ![](./preview/SW_MX_LowProfile_THT.svg) | MX_LowProfile_THT                        |                           |  :white_check_mark:   | :bulb: [^t-ks_vs_c-mxlp] |                             |                            |                             | :white_check_mark: |                    |      :white_check_mark:       |                                |
| ![](./preview/SW_Gateron_LowProfile_THT.svg) | Gateron_LowProfile_THT                   |                           |                       |                          |                             |                            |     :white_check_mark:      | :white_check_mark: |                    |                               |                                |
| ![](./preview/SW_Gateron_LowProfile_HotSwap_THT.svg) | Gateron_LowProfile_HotSwap_THT           |                           |                       |                          |                             |                            |     :white_check_mark:      | :white_check_mark: | :white_check_mark: |                               |                                |
| ![](./preview/SW_Gateron_LowProfile_HotSwap_PTH.svg) | Gateron_LowProfile_HotSwap_PTH           |                           |                       |                          |                             |                            |     :white_check_mark:      |   :bulb: [^pth]    | :white_check_mark: |                               |                                |
| ![](./preview/SW_Kailh_Choc_V1_THT.svg) | Kailh_Choc_V1_THT                        |                           |                       |                          |     :white_check_mark:      |                            |                             | :white_check_mark: |                    |      :white_check_mark:       |       :white_check_mark:       |
| ![](./preview/SW_Kailh_Choc_V1_THT_alt1.svg) | Kailh_Choc_V1_THT_alt1 [^k-cooc1-alt]    |                           |                       |                          |     :white_check_mark:      |                            |                             | :white_check_mark: |                    |                               |                                |
| ![](./preview/SW_Kailh_Choc_V1_HotSwap.svg) | Kailh_Choc_V1_HotSwap                    |                           |                       |                          |     :white_check_mark:      |                            |                             |                    | :white_check_mark: |      :white_check_mark:       |                                |
| ![](./preview/SW_Kailh_Choc_V1_HotSwap_THT.svg) | Kailh_Choc_V1_HotSwap_THT                |                           |                       |                          |     :white_check_mark:      |                            |                             | :white_check_mark: | :white_check_mark: |                               |                                |
| ![](./preview/SW_Kailh_Choc_V1_HotSwap_PTH.svg) | Kailh_Choc_V1_HotSwap_PTH                |                           |                       |                          |     :white_check_mark:      |                            |                             |   :bulb: [^pth]    | :white_check_mark: |                               |                                |
| ![](./preview/SW_Kailh_Choc_V2_THT.svg) | Kailh_Choc_V2_THT                        |                           |                       |                          |                             |     :white_check_mark:     |                             | :white_check_mark: |                    |      :white_check_mark:       |                                |
| ![](./preview/SW_Kailh_Choc_V1V2_THT_Hybrid.svg) | Kailh_Choc_V1V2_THT_Hybrid               |                           |                       |                          | :bulb:[^k-choc1_vs_k-choc2] |     :white_check_mark:     |                             | :white_check_mark: |                    |                               |                                |
| ![](./preview/SW_Kailh_Choc_V1V2_HotSwap_Hybrid.svg) | Kailh_Choc_V1V2_HotSwap_Hybrid           |                           |                       |                          | :bulb:[^k-choc1_vs_k-choc2] |     :white_check_mark:     |                             |                    | :white_check_mark: |                               |                                |
| ![](./preview/SW_MX_Kailh_Choc_V1V2_THT_Hybrid.svg) | MX_Kailh_Choc_V1V2_THT_Hybrid            | :bulb: [^c-mx_vs_k-choc2] |                       |                          | :bulb:[^k-choc1_vs_k-choc2] |     :white_check_mark:     |                             | :white_check_mark: |                    |                               |                                |
| ![](./preview/SW_MX_Kailh_Choc_V1V2_HotSwap_Hybrid.svg) | MX_Kailh_Choc_V1V2_HotSwap_Hybrid        | :bulb: [^c-mx_vs_k-choc2] |                       |                          | :bulb:[^k-choc1_vs_k-choc2] |     :white_check_mark:     |                             |                    | :white_check_mark: |                               |                                |
| ![](./preview/SW_MX_LowProfile_Kailh_Choc_V1V2_THT_Hybrid.svg) | MX_LowProfile_Kailh_Choc_V1V2_THT_Hybrid |                           |  :white_check_mark:   | :bulb: [^t-ks_vs_c-mxlp] | :bulb:[^k-choc1_vs_k-choc2] | :bulb:[^k-choc2_vs_c-mxlp] |                             | :white_check_mark: |                    |                               |                                |

> :white_check_mark:: Compatible; :bulb:: Conditionally compatible; Blank: Not compatible.

[^preview]: Preview images are exported using the `kicad-cli fp export svg` command and processed.
[^tht]: THT means through-hole soldering.
[^pth]: PTH means the holes of the Hot-Swap socket are plated, and the switches can be soldered directly without using a socket. However, the soldering difficulty is higher compared to the standard THT edition.
[^k-choc1]: Kailh Choc V1 also known as PG1350.
[^k-choc2]: Kailh Choc V2 also known as PG1353.
[^g-lp]: Gateron Low Profile 1.0 (aka KS-27) and 2.0 (aka KS-33) footprint are compatible.
[^t-ks_vs_c-mxlp]: TTC KS32 and Cherry MX Low Profile are very similar, basically compatible.
[^k-choc1_vs_k-choc2]: The center fix pin of Choc V1 is smaller than Choc V2, however Choc V1 has two additional fix pins ensuring its stability.
[^k-choc2_vs_c-mxlp]: The center fix pin of Choc V2 is smaller than Cherry MX Low Profile, Choc V2 may not be securely fastened.
[^c-mx_vs_k-choc2]: The center fix pin of Cherry MX is smaller than Choc V2, however some Cherry MX has two additional fix pins ensuring its stability.
[^sw-prefix]: Omit the "SW" prefix from the footprint name.
[^ns-suffix]: The footprint with "nSilk" suffix means no top layer silkscreen.
[^swap-suffix]: The footprint with "swap" suffix means the pin number swap.
[^k-cooc1-alt]: *Kailh_Choc_V1_THT_alt1* has one more NPTH than *Kailh_Choc_V1_THT*, and this hole is located at the position of the spring in the Clicky switch (e.g. White, Jade). If you are likely to use Clicky switches it is recommended to use *Kailh_Choc_V1_THT_alt1*.

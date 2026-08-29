# Key Switches

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

## ★ このフォーク限定: キーキャップサイズバリアント `variants.pretty/`（2026-08-30）

**リポジトリ直下の 33 ベースフットプリントから、キーキャップサイズ別の
バリアント（606 ファイル）を `variants.pretty/`（別ライブラリとして登録する）に
自動生成してある。** 再生成は `python3 scripts/generate_variants.py`。

- **ベース（直下 33 ファイル）= キーキャップなし**。コートヤードはスイッチ単体の
  占有範囲（16.5mm 角）のまま
- **バリアントのコートヤード = キーキャップ 1u=19.05mm ピッチの占有範囲**。
  DRC の「コートヤード重複」で他部品との干渉を検出できる。
  外縁は公称より各辺 0.025mm 控え（例: 1u → 19.00mm 角）にしてあり、
  19.05mm ピッチで隣接するキー同士は誤検出しない
- **命名**: `<ベース名>_<サイズ>` 。サイズは
  `1.00u` `1.25u` `1.50u` `1.75u` `2.00u` `2.25u` `2.75u` `3.00u` `4.50u`
  `6.00u` `6.25u` `6.50u` `7.00u` `ISOEnter`
- **スタビライザー**（2u 以上と ISO Enter）:
  - **プレートマウント用 → サフィックス無し版**をそのまま使う（PCB 側に要素不要。
    Kailh Choc / Gateron Low Profile のスタビはプレートマウント規格のみなので常にこちら）
  - **Cherry MX PCB マウント用 → `_PCBStab` 版**（MX 系ベース 18 種のみ）。
    NPTH 小穴 Ø3.048（y=−6.985）+ 大穴 Ø3.9878（y=+8.225）、ステム位置は
    2u系=±11.938 / 3u=±19.05 / 6u=±47.625 / 6.25u=±50 / 7u=±57.15mm。
    ISO Enter は縦 2u スタビ（90° 回転、大穴＝ワイヤー側が x=−8.225 の左側。
    逆向きに実装する場合は基板側でフットプリントを 180° 回転）
  - **4.50u / 6.50u は PCB マウントスタビの標準規格が無い**（kiswitch にも無い）ため
    `_PCBStab` 版は生成していない
- **寸法出典**: [kiswitch](https://github.com/kiswitch/kiswitch)
  （`KiSwitch/switch.py` StabilizerCherryMX / `keycap.py`）。
  ISO Enter の外形（上段 1.5u + 下段 1.25u 右端揃え、スイッチは下段列の中心）も同準拠
- **注意**: キーキャップ範囲のコートヤードは、キャップ下に置くダイオード等も
  DRC エラーにする。物理的に問題ない配置は KiCad 側で除外指定するか、ベース版を使う
- **検証**: KiCad 10.0.5 の `kicad-cli fp export svg` で 606 ファイル全部のパースを
  確認済み。コートヤード寸法・スタビ穴座標はスクリプトで機械チェック済み。
  プレビュー画像はベース 33 のみ（バリアントは枚数が膨大なため生成しない）

## ★ このフォークの利用

このフォークを submodule として使う場合は上流ではなくこちらの URL を指定する
（次節「Usage」の URL は上流のまま）:

```
git submodule add https://github.com/tryandhappy/kicad-key-switch-footprints.git
```

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

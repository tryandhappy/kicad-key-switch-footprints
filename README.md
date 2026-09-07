# Key Switches

This is a [KiCad](https://www.kicad.org/) footprint library of mechanical keyboard switches, released under the [CERN-OHL-P v2](/LICENSE).

## ★ まずこれを使う（迷ったら 1 系統 1 フットプリント。2026-09-07）

このフォークは選択肢が多い（ハイブリッド、代替パッド配置、スタビ 4 方式、プレート層 4 種）。
**組むスイッチの系統を決めたら、下の 1 行だけ見てライブラリを 1 つ登録すればよい。**
以下の節は「なぜそうなっているか」と例外の説明で、最初は読まなくてよい。

| 組むスイッチ | 登録するライブラリ | 使うフットプリント（1u） | プレートに書き出す層 | 2u 以上のキー |
|---|---|---|---|---|
| **Kailh Choc（V1 でも V2 でも）** | `variants-choc.pretty` | `SW_Kailh_Choc_V1V2_HotSwap_Hybrid_1.00u` | `User.3`（13.95。V1/V2 でプレート共用） | `..._2.00u` を**スタビ無し**で使う（Choc のスタビは入手性・FR4 プレート強度とも難あり）。2u は親指キーに限るか 1.5u にすると傾きが目立たない（下記「スタビ無しの 2u」） |
| **Cherry MX 互換（通常の高さ）** | `variants-mx.pretty` | `SW_MX_HotSwap_PTH_1.00u` | `User.2`（14.00） | `..._2.00u_MXPCBStab`（Cherry PCB マウントスタビ。プレートマウントでも可） |
| **Gateron Low Profile 2.0（KS-33）** | `variants-gateron.pretty` | `SW_Gateron_LowProfile_HotSwap_PTH_1.00u` | `User.2`（14.00） | **FR4 プレートならスタビ無し**（`..._2.00u`）。`..._2.00u_GateronLPStab`（Gateron 純正プレートマウントスタビ）は**金属プレート前提**（FR4 では取り外し時に開口脇の柱が折れ得る。下記警告） |

- サイズは `_1.25u` `_1.50u` `_2.00u` … `_ISOEnter` `_2.00u_Vertical` など（一覧は下のバリアント節）。
  裏面ダイオード込みにしたいときは末尾に `_Diode` を付けた版を使う（回路図は `symbols/` の `SW_Key_Diode`）
- `HotSwap_PTH` はソケットの穴がメッキ済みなので、**ソケットを付けても、直接はんだ付けしても使える**。
  ソケットを使わない前提で穴を小さくしたいときだけ `_THT` 版を選ぶ
- 化粧カバー（スイッチを掴まない上板）を作るなら、上の層に加えて `User.1`（15.60）を書き出す
- **既定の生成物に含めていないもの**: `_alt*`（代替パッド配置。機能差なし）と `MX_LowProfile*`
  （Cherry MX LP。入手困難でこのフォークの想定プレート構成にも載らない）。ベースは
  `single.pretty` / `double.pretty` に残してあり、必要なら
  `python3 scripts/generate_variants.py --all` でバリアントも生成できる
- **スタビ無しの 2u について**: 低背スイッチの 2u をスタビ無しで組むと、端を押したときにキャップが
  ステムを支点に傾く。原因は ① ハウジングが PCB に対して傾く / ② スライダーがハウジング内で傾く /
  ③ キャップがステム上で傾く、の 3 層で、**プレートが直すのは ① だけ**（②③ はスイッチとキャップの
  遊び）。プレートレスからプレート付きにすると少し締まるが、スタビの代わりにはならない。
  実用上は **2u を親指キーに限定する**（キャップ中央付近を押すので傾きが出にくい）か **1.5u にする**
  （支点からの距離が 4.8mm 縮む）のが効く。**FR4 プレートでスタビを使える唯一の経路は
  Choc V1 + Choc V1 スタビ**（`_ChocV1Stab`。ハウジングを PCB スロットに落としワイヤーをプレート下に
  通すので、プレート開口はスイッチ開口と独立で両端固定の梁が残る。ただし国内在庫は
  2026-09 時点で遊舎工房 1 店）。Gateron LP / Choc V2 でスタビを使うなら金属プレート
- **`variants-hybrid-pcb-only.pretty`（MX × Choc ハイブリッド）は上級者向け**。1 枚の PCB を
  MX 版と Choc 版で作り分けたい場合にだけ使う。**互換なのは PCB だけ**で、プレート
  （高さ 5.0 vs 2.2mm）・ケース・スタビはスイッチごとに別設計になる。
  詳細は「ハイブリッドのプレート共用」と「スイッチ × スタビライザー対応表」

## ★ このフォーク限定: プレートのカット線（上流には無い。2026-08-29、四隅リリーフ 2026-09-03）

**33 個すべての `.kicad_mod` に、キーボードプレート加工用のカット線
（原点中心、線幅 0.05mm）を追加してある。** 各ファイルには
そのスイッチに該当するレイヤだけが入っている（`descr` フィールドにも同じ対応を記載）:

| レイヤ | 開口 | 対象スイッチ | 入っているファイル |
|---|---|---|---|
| `User.1` | **15.60mm 角**（`fp_rect`） | 化粧カバー（スイッチを掴まない。全スイッチ共通） | 全 33 ファイル |
| `User.2` | **14.00mm 角 + 四隅 R0.60 リリーフ（中心 0.35 内側）** | **MX / MX Low Profile / Gateron Low Profile** | `SW_MX_*` `SW_Gateron_*`（21） |
| `User.3` | **13.95mm 角 + 四隅 R0.60 リリーフ（中心 0.35 内側）** | **Kailh Choc V2（PG1353）** | `*Choc_V2*` `*Choc_V1V2*`（9） |
| `User.4` | **13.80mm 角 + 四隅 R0.60 リリーフ（中心 0.35 内側）** | **Kailh Choc V1（PG1350）** | `*Choc_V1_*` `*Choc_V1V2*`（15） |

- **四隅リリーフ（dogbone）**: スイッチ保持用の `User.2/3/4` は、正方形の各角に
  半径 0.60mm の円を、中心を角から対角線上に 0.35mm 内側へ置いて重ねた一体外形
  （直線 4 本 + 約 199° の円弧 4 本、`fp_line` + `fp_arc`）。円は角の点を 0.1mm の余裕で
  覆い、辺の外へは 0.25mm はみ出す。FR4 などルーター加工のプレートは内角にビット半径が
  残り、角がほぼピン角のスイッチハウジングが最後まで座らないため、角に逃げを設ける。
  **JLCPCB の内側カットアウトはビット半径 0.5mm（Ø1.0）**
  （[TechOverflow の問い合わせ結果](https://techoverflow.net/2023/04/12/jlcpcb-which-milling-tool-radius-is-used-for-internal-cutouts/)）
  なので R0.6 で足りる。直線部は各辺 12.33mm（14.00 の場合）残るので 4 辺のツメによる
  保持は変わらない。市販例:
  [Waveshare 0.85inch ScreenKey Module 付属プレート](docs/plate-corner-relief-sample.jpeg)
  （[モジュール裏面](docs/waveshare-screenkey-module-back.jpeg)。実測 Ø2.0mm 程度。
  Ø2.0 ビットの加工向けで、JLCPCB には過剰）
  - **履歴**: 2026-09-03〜09-07 は角を中心にした R1.0（はみ出し 1.0mm）だった。
    はみ出しが大きく、`_MXPCBStab` 開口との梁が 0.56mm に痩せ、Choc V2 スタビの
    ワイヤー溝に 0.39mm 食い込んで開口下辺と溝の間の 0.6mm の帯が島になっていたため、
    2026-09-07 に現在の R0.6・中心 0.35 内側へ変更した
  - リリーフの外端は中心から ±7.25mm（14.00 角の場合。旧 R1.0 では ±8.00）。19.05mm
    ピッチの隣接キーとの間に残るプレートの梁は角付近で **4.55mm**（正方形なら 5.05mm）
  - `_MXPCBStab` の 2u 系スタビ開口（内側の辺 x=±8.563）とは重ならず、間の梁は
    角付近で **1.31mm**（正方形なら 1.56mm）。Choc V2 スタビのワイヤー溝
    （y=7.58〜8.98）との間は 0.36mm 残り、開口下辺と溝の間の 0.6mm の帯は両端で
    つながる（島にはならない。帯自体が細い問題は下の `_ChocV2Stab` の警告を参照）。
    Choc V1 スタビ開口とは重ならない（梁 2.3mm 以上）。Gateron LP スタビの溝
    （y=0.15〜2.65）は開口の辺の中間を横切るので島は生じない
  - **テストプレート（2026-09-07）**: [`docs/test-plate-150x150.dxf`](docs/test-plate-150x150.dxf)
    （プレビュー [`docs/test-plate-150x150.svg`](docs/test-plate-150x150.svg)）。150×150mm、19.05mm ピッチ 7×7、
    四隅に M2 用 Ø2.2 穴。1 枚で **板材の見積比較**（JLCCNC の板金見積に DXF をそのまま上げて材料・仕上げを
    切り替える。FR4 なら KiCad で DXF を Edge.Cuts に取り込んで PCB として発注）と、
    **開口寸法・リリーフ・低背スタビカットの実物確認**ができる。内容は上から
    行 1〜3 = 14.00 / 13.95 / 13.80 + 現行リリーフ、行 4 = リリーフ無し 3 種・旧 R1.0（角中心）3 種・
    化粧カバー 15.60、行 5 = 横 2u の Gateron LP / Choc V2 / Choc V1 スタビカット、
    行 6〜7 = 縦 2u の同 3 種 + 14.00。切り抜き 53 個、切り抜き総周長 約 3.0m（金属レーザーの価格は
    ほぼこれで決まる）。生成は `scripts/test_plate_dxf.py`（ezdxf + shapely が必要。寸法は
    `plate_cut_lines.py` / `generate_variants.py` の定数を参照するので単一情報源）。
    重なるスタビ外形は shapely で union 済みで、DXF は閉じた LWPOLYLINE のみ（円弧は 1/4 円 32 分割の折れ線）。
    **見積用の `docs/test-plate-150x150-quote.dxf`** も同時に生成する（Choc V2 スタビの 2 セルを 14.00 開口に
    置き換えて 1mm 未満の残り幅を無くし、円弧を 1/4 円 8 分割・頂点 3,671 に減らしたもの）。完全版は
    JLCCNC の自動見積で「マニュアル見積」に回った（2026-09-07。原因は 0.6mm / 0.36mm の残り幅か
    微小セグメントと推定、未確定）ので、価格を即時に見たいときは見積用を使う
  - 半径と中心のずらし量は `scripts/plate_cut_lines.py` の `RELIEF_R` / `RELIEF_INSET`。変更後
    `python3 scripts/plate_cut_lines.py`（33 ベースを書き直す。冪等）→
    `python3 scripts/generate_variants.py`（`_Diode` と variants を再生成）。
    `RELIEF_R = 0` で以前の `fp_rect` 正方形に戻る。開口寸法（`PLATE_CUTS`）も同スクリプト
  - `User.1`（化粧カバー）はスイッチを掴まない（上部ハウジングの角は丸い）のでリリーフなし
- **想定プレート構成（このフォークの設計前提、2026-09-03）**: プレートは **1.2mm 厚 FR4 基板**、
  **プレート下面と PCB 上面の隙間 1.0mm**（プレート上面から PCB 上面まで 2.2mm）。
  Kailh Choc V1/V2 の規定（1.3mm プレート + 0.9mm = 2.2mm）と Gateron LP（推奨 1.2mm プレート）
  向けの構成。
  **MX（Cherry 規定: 1.5mm プレート、プレート上面〜PCB 5.0mm）はこの構成では組めない**
  （MX の下部ハウジングが PCB に当たるため 3.8mm の隙間が必要。1.2mm プレートは
  ツメの掛かりが 0.3mm 浅くなる）。MX 用プレートは別スタック
- **Cherry MX Low Profile もこの構成では組めない**（2026-09-07、Cherry 図面 MX1B-52NA rev.00 で確認。
  [`docs/cherry-mx-low-profile-drawing-MX1B-52NA-rev00.pdf`](docs/cherry-mx-low-profile-drawing-MX1B-52NA-rev00.pdf)）。
  図面の取付規定は **プレート厚 1.5 ±0.07mm**、開口 14 ±0.05mm 角（角 R max 0.5）、
  ハウジング上端→フランジ下面 2.25 ±0.1 / ハウジング上端→下部ハウジング底 5.0 ±0.25 で、
  下部ハウジング底が PCB 上面に座る構造なので **プレート上面〜PCB 上面 = 2.75mm**
  （1.5mm プレートなら隙間 1.25mm）。本フォークの 2.2mm より **0.55mm 高く**、
  ハウジング底が先に PCB に当たってフランジが浮き、ツメがプレート下面に届かない。
  1.2mm プレートのままなら隙間 1.55mm が必要で Choc と両立しない。
  PCB 下への突出はピン 3.1 ±0.25 / 中央ポスト 3.3 ±0.15、PCB 上の SMD LED は高さ max 0.75
  （ハウジング底の窪みに入る補助 SMD 部品は max 1.6）。
  図面の PCB 穴指定は中央 NPTH Ø6.5 ±0.05 / 固定ピン NPTH Ø2.5 ±0.05 at (0, 3.7) /
  端子 Ø1.5 ±0.05 at (0, 6.05)・(4.13, 3.3)。`SW_MX_LowProfile_*` の座標は一致するが
  穴径は上流（Keebio 系譜）のまま Ø6.25 / Ø2.3 / ドリル 1.2 と小さめ（未変更）

- **レイヤ＝プレート案の排他選択。** 書き出すレイヤを 1 つ選べばプレートの種類が決まる。
  ハイブリッド系のフットプリントには該当レイヤが複数入っているが、共存してよい
- **ハイブリッドのプレート共用（2026-09-07 整理）**: 2 種のスイッチが同居するハイブリッドは
  基本的に **PCB 側だけの互換**で、プレートは載せるスイッチごとに別になる。
  判定は「開口の XY」と「プレート上面〜PCB 上面の高さ」の 2 条件で、
  **例外として Kailh Choc V1V2 ハイブリッド（`SW_Kailh_Choc_V1V2_*`）だけは 1 枚のプレートを
  V1 / V2 で共用できる**

  | ハイブリッド | 開口 XY | 高さ（上面〜PCB） | プレート共用 |
  |---|---|---|---|
  | Kailh Choc V1V2（THT / HotSwap） | 13.80 vs 13.95、差 0.15 | どちらも 2.2mm（Kailh 規定 1.3 + 0.9） | **実用上可** |
  | MX × Choc V1V2（THT / HotSwap / double / alt1） | 14.00 vs 13.95 は差 0.05 で実質同じ、V1 は 0.2 差 | MX 5.0 vs Choc 2.2 | 不可（高さが 2.8mm 違う） |
  | MX LP × Choc V1V2 | 14.00 vs 13.95 は実質同じ | MX LP 2.75 vs Choc 2.2 | 不可（0.55 足りず MX LP のツメが掛からない） |

  - Choc V1V2 が共用できる根拠: 高さ規定が同一で、開口差 0.15mm は JLCPCB のルーター公差
    ±0.2mm の範囲内（工場側で 13.80 と 13.95 を区別して作れる保証がない）。
    cyril279 の [revlp/41_1353](https://github.com/cyril279/keyboards/blob/main/revlp/41_1353/README.md)
    でも 13.95 は「V2 をプレートにクリップさせる場合」、13.80 は「プレートを PCB に固定する構成と
    V1 用」で、V2 も 13.80 に収まる前提で書かれている。V1 は PCB の固定ピン 2 本で位置が決まるので、
    13.95 の穴で 0.075mm/辺ゆるくても実害は小さい
  - 使い方: V2 のクリップを優先して **`User.3`（13.95）を書き出す**のが安全側
    （V1 は PCB ピンで保持と割り切る）。`User.4`（13.80）で V2 も通すかは cyril279 の記述に
    依拠しているだけなので、採用するならテストクーポンで確認する
  - **2u 以上のスタビ付きキーは共用できない**（Choc V1 スタビと V2 スタビは部品も開口も別で
    ワイヤーが互いのハウジングと干渉。対応表の節を参照）。スタビ無しの配列なら
    Choc V1V2 ハイブリッドは PCB もプレートも 1 種類で両方に対応できる
- **MX 系はすべて 14.00mm 角**（通常の Gateron は MX クローンで `SW_MX_*` を使う。
  低背 2 種も開口は同じだが、推奨プレート厚が違う: Gateron LP は 1.20 (+0.01/−0.05)、
  Cherry MX LP は 1.5 ±0.07。開口公差も Gateron 14.00 (+0.05/−0.02) / MX LP 14 ±0.05 で
  公称は同じ。開口の XY は共用できるが板厚とスペーサー高さは別）
- **★ 13.95 と 14.00 の差 0.05mm は JLCPCB のルーター公差（±0.2mm）より小さく、
  実物で区別できない可能性が高い。** 実物比較で差が出なければ V2 も 14.00 に寄せて
  `User.3` を廃止してよい（緩くなる側なので安全）。値の変更は
  `scripts/plate_cut_lines.py` の `PLATE_CUTS` 1 か所 → 再実行
- **出典**: Choc V1=13.80 / V2=13.95 は
  [cyril279/keyboards revlp/41_1353](https://github.com/cyril279/keyboards/blob/main/revlp/41_1353/README.md)、
  Gateron LP の 14.00 は公式データシートの取付図
  （[KS-27](https://www.gateron.co/pages/gateron-low-profile-mechanical-switch-datasheet) /
  [KS-33](https://www.gateron.co/pages/gateron-ks-33-low-profile-2-0-mechanical-switch-datasheet)）、
  Cherry MX LP の 14 ±0.05・プレート厚 1.5・取付高さは Cherry 図面
  [MX1B-52NA rev.00（2018-04-17）](docs/cherry-mx-low-profile-drawing-MX1B-52NA-rev00.pdf)
  （Cherry が問い合わせ者にメールで配布したもの。
  [geekhack の投稿](https://geekhack.org/index.php?topic=106825.0)に添付された PDF を保管。
  公式サイトの Datasheet PDF には取付図が無い。図面左欄に Cherry の複製・再配布制限の
  注記があるため、公開リポジトリに置き続けるかは要判断）、
  14×14 に入ることの二次情報は
  [Deskthority wiki](https://deskthority.net/wiki/Cherry_MX_Low_Profile)
- **検証**: KiCad 10.0.5 の `kicad-cli fp export svg` で 33 ファイル全部のパースと
  リリーフ形状の描画を確認済み。DXF 書き出しは正方形時代（リリーフ追加前）に
  20° 回転を含む配置で `User.1/2/3` から 15.600 / 14.000 / 13.950mm が出ることを
  確認済み（線幅は書き出しに出ないので値は自由に変えてよい）。リリーフ付き外形の
  DXF 書き出し（円弧の連結）は未確認
- `preview/` の画像もカット線入りで再生成してある
  （`kicad-cli fp export svg` + 黒背景化。ベースは上流コミット `b4afad5`）

## ★ このフォーク限定: キーキャップサイズバリアント `variants-*.pretty`（2026-08-30）

**`single.pretty/` + `double.pretty/` の 33 ベースフットプリントから、
キーキャップサイズ別のバリアント（1190 ファイル）をスイッチ種別の
4 ライブラリに自動生成してある**（`variants-mx` 464 / `variants-choc` 464 /
`variants-hybrid-pcb-only` 134 / `variants-gateron` 128。それぞれ別ライブラリとして登録）。
再生成は `python3 scripts/generate_variants.py`。
**既定では `_alt*` 4 ベースと `MX_LowProfile*` 3 ベースを生成対象外**にしている
（2026-09-07。バリアントも `_Diode` ベースも作らない。`--all` で含めると 1540 + 27 になる）。
`variants-hybrid-pcb-only`（旧 `variants-mx-choc`。2026-09-07 改名）は MX × Choc
ハイブリッドで、**PCB 互換のみ**（プレート・スタビは別設計）であることを名前で示す。

- **ベース（直下 33 ファイル）= キーキャップなし**。コートヤードはスイッチ単体の
  占有範囲（16.5mm 角）のまま
- **バリアントのコートヤード = キーキャップ 1u=19.05mm ピッチの占有範囲**。
  DRC の「コートヤード重複」で他部品との干渉を検出できる。
  外縁は公称より各辺 0.025mm 控え（例: 1u → 19.00mm 角）にしてあり、
  19.05mm ピッチで隣接するキー同士は誤検出しない
- **命名**: `<ベース名>_<サイズ>[_<スタビ>][_Diode]` 。サイズは
  `1.00u` `1.25u` `1.50u` `1.75u` `2.00u` `2.25u` `2.75u` `3.00u` `4.50u`
  `6.00u` `6.25u` `6.50u` `7.00u` `ISOEnter` `ISOEnterFlip`（ISO Enter の上下反転。キーキャップ外形のみ反転、スイッチとスタビの向きはそのまま）、
  および縦向きの `1.25u_Vertical` `1.50u_Vertical` `2.00u_Vertical`（幅 1u × 高さ N u。
  テンキーの Enter / + / 0 など。次項）。
  `_Diode` は裏面 SMD ダイオードパッド付き（次節）
- **縦向きキー `_Vertical`**（2026-09-06 追加）: コートヤードは 19.00 × (N×19.05−0.05) mm。
  `2.00u_Vertical` には各スタビ版（`_MXPCBStab` / `_ChocV1Stab` / `_ChocV2Stab` / `_GateronLPStab`）もあり、
  スタビ要素（NPTH 穴・スロット・`User.5` カット線）を ISO Enter と同じ向きに
  90° 回転（(x,y)→(−y,x)）して配置してある。ワイヤー側は
  MX = 左（大穴 x=−8.255）/ Choc V2 = 左（ワイヤー溝 x=−8.28）/ Gateron LP = 左（ワイヤー溝 x=−1.4）/
  Choc V1 = 右（x=+7.25）。
  逆向きに実装したい場合は基板側でフットプリントを 180° 回転する。
  縦向きではスタビ要素がスイッチ本体の上下（|y| ≥ 8.75）に来るため、横向き 2u では
  ソケットパッドと干渉して生成できなかったホットスワップ系の `_ChocV2Stab` も
  縦向きなら生成される（干渉チェックで自動判定。全層の図形・パッドとの干渉なしを確認済み）
- **スタビライザー**（2u 以上と ISO Enter）:
  - **サフィックス無し版 = スタビ用の PCB 要素なし**。MX のプレートマウントスタビは
    そのまま使える
  - **Cherry MX PCB マウント用 → `_MXPCBStab` 版**（MX 系ベース 12 種のみ。`--all` なら 18 種）。
    NPTH 小穴 Ø3.048（y=−6.985）+ 大穴 Ø3.9878（y=+8.255。小穴と 15.24mm 間隔）、
    ステム位置は 2u系=±11.938 / 3u=±19.05 / 4.5u=±33.3375 / 6u=±47.625 /
    6.25u=±50 / 7u=±57.15mm。
    ISO Enter は縦 2u スタビ（90° 回転、大穴＝ワイヤー側が x=−8.255 の左側。
    逆向きに実装する場合は基板側でフットプリントを 180° 回転）。
    **スタビ用プレートカット線は `User.5`**（6.75×14mm 角丸、中心 y=+1.0、
    kb-plategen "Normal" 準拠。プレートマウント・PCB マウント両対応の
    Cherry スタイルなので、プレートマウントスタビで組む場合も
    `_MXPCBStab` 版を使えばカット線が得られる。NPTH 穴は未使用でも無害）
  - **Kailh Choc 1350（V1）スタビ用 → `_ChocV1Stab` 版**（Choc V1 対応ベース 12 種（`--all` なら 15 種）×
    2.00u / 6.25u のみ = Kailh が製造しているサイズ）。丸穴ではなく
    **PCB の角丸スロット切り欠き 4 個（`Edge.Cuts`）+ プレート必須**という方式。
    本体スロット 5.3×5.5mm + ワイヤースロット 4.0×3.5mm（角 R0.5）、
    ステム位置 2u=±12.0 / 6.25u=±38.0mm。スタビ用プレートカット線は `User.5`。
    **Choc V1 スイッチ専用**。ワイヤーが Choc V2 のハウジングと干渉するため
    V2 には使えない（V2 専用ベースには生成しない）
  - **Kailh Choc V2 スタビ（CPG1353G24D01）用 → `_ChocV2Stab` 版**（2.00u のみ =
    Kailh の製造を確認できたサイズ）。対応スイッチは **Choc V2 / Gateron KS-33**
    で、**Choc V1 とは非互換**（Keebio 商品ページ準拠）。
    **PCB の矩形スロット切り欠き 2 個（`Edge.Cuts`、6.5×9.5mm、中心 x=±12.0）+
    プレート必須**。スタビ用プレートカット線は `User.5`（本体 5.95×7.95 +
    突出 4.55×6.25 + ワイヤー溝 全幅×1.4mm、角 R0.5、kb-plategen 準拠。
    3 種の角丸矩形は互いに重なるのでプレート CAD 側で union する）。
    ホットスワップ系ベースはソケットパッドがスロットと物理干渉するため
    横向き 2u では生成対象外（THT 系 5 種のみ（`--all` なら 6 種）。生成スクリプトの干渉チェックで自動判定。
    縦向き `2.00u_Vertical_ChocV2Stab` は干渉しないためホットスワップ系を含む 10 種（`--all` なら 12 種））。
    **⚠ FR4 プレートでの強度警告（2026-09-07）**: この形状は 1.2mm FR4 プレートには向かない。
    図: [`docs/chocv2-stab-plate-cantilever.svg`](docs/chocv2-stab-plate-cantilever.svg)
    - **スイッチ左右の柱が片持ち梁になる**。ワイヤー溝が x=±12 まで走るため、スイッチ開口
      （x=±6.975）とスタビハウジング開口（内側の辺 x=±9.025）の間の柱（幅 2.05mm、
      突出部脇は 2.75mm、厚さ 1.2mm）は y=−3.6 の上端だけで本体につながり、y=7.58 の溝で
      切り離される（長さ 11.2mm）。FR4 の概算では先端 5N で たわみ約 0.4mm・応力約 110MPa と
      静的には折れないが、スイッチ挿入時に開口の縁を押し広げる力で根元から割れやすく、
      ルーター加工中の欠けも起きやすい。打鍵荷重は Choc のハウジング底が PCB で受けるので
      通常のタイピングでは柱に大きな力は掛からない
    - **開口下辺と溝の間に残る帯は 0.6mm しかない**（図の②）。現行の User.3 リリーフ
      （R0.6、中心 0.35 内側、最下点 y=7.225）は溝の上端 7.58 に届かないので帯は両端で
      柱につながるが、0.6mm 幅の FR4 は公差 ±0.2mm で 0.4mm まで痩せるため実用強度は無い。
      元の kb-plategen もリリーフ無しの正方形で同じ 0.6mm の帯を残す設計。
      **旧リリーフ（〜2026-09-07、角中心の R1.0、図の①）では円の最下点 y=7.975 が溝に
      0.39mm 食い込み、帯は上を開口・下を溝・両端を円に囲まれた島になって脱落していた**。
      これが R0.6 へ変更した直接のきっかけ
    - **参考案（未採用、図の③）**: `_ChocV2Stab` 版の User.3 下辺を溝の下端 y=8.981 まで
      下げて一体の開口にすると帯が無くなり加工は確実になるが、スイッチ下辺の保持面が
      無くなる。**いずれにせよ片持ち梁は残る**
    - **推奨**: Choc V2 の 2u はスタビ無しで組む（低背 2u はスタビ無しの実例が多く、
      V2 スタビは 2026-09 時点で在庫ありが世界 1 店）。スタビを使うなら 1.5mm 前後の
      金属プレート（kb-plategen 本来の前提に近い）。FR4 1.2mm で使う場合は試作限定と割り切る。
      この形状は元々 1.5mm 級の金属プレートを想定した設計と考えるのが妥当で、
      ワイヤーがプレートの高さを通る V2 スタビは MX（ワイヤーがプレート下）・
      Choc V1（PCB スロット方式）より FR4 プレートに厳しい
    - **最悪荷重はスイッチの取り外し**。打鍵はハウジング底が PCB で受けるので柱に力は掛からないが、
      ホットスワップからの引き抜きは 20〜40N 必要で、プーラーの先を**プレートに当ててテコにすると
      支点がちょうど開口脇の柱（x 7〜9mm）に来る**。11.2mm の片持ち梁の破断目安は先端約 19N
      （面外）なので、テコ操作 1 回で折れ得る。FR4 で試す場合は「プレートをテコにせず真上に引く」
      運用が前提
  - **Gateron Low Profile 純正プレートマウントスタビ（KS-57B210T）用 → `_GateronLPStab` 版**
    （2026-09-07 追加。Gateron LP ベース 3 種 × 2.00u / 2.00u_Vertical、`_Diode` 版込みで 12 ファイル）。
    図: [`docs/gateron-lp-stab-plate-groove.svg`](docs/gateron-lp-stab-plate-groove.svg)（ワイヤー溝がスイッチ開口を横切る様子）。
    Gateron 公式ストアで 2U 単品が買える純正部品で、対応スイッチは **Gateron LP（KS-33 / KS-27）**。
    **プレートマウント専用で PCB 側の要素は無い**（`Edge.Cuts` も NPTH も追加しない。
    ホットスワップ系ベースにも生成される）。スタビ用プレートカット線は `User.5`
    （ハウジング開口 6.00×12.50 中心 (±12.0, +0.6) + 下辺中央の突起 1.70 幅・深さ 1.2 +
    ワイヤー溝 全幅×2.5 中心 y=+1.4、角 R0.5。3 種の角丸矩形は互いに重なるので
    プレート CAD 側で union する）。寸法出典は Gateron 製品仕様書
    [GATERON Low Profile Plate Mounted Stabilizer 2U（KS-57B210T）](https://gateron.com/u_file/2311/22/file/GATERONLowProfilePlateMountedStabilizer2U-KS-57B210T.pdf)
    の推奨開口図。**図に数値があるのは 6.00 (+0.03/−0.05)・12.50 (+0.03/−0.05)・突起幅 1.70 のみ**で、
    ステム間隔 ±12.0・ハウジング中心 y・溝の高さと位置・突起深さは同図を 400dpi で
    ラスタライズして実測した値（誤差 ±0.1mm 程度）。**ハウジングのプレート下への突出量は
    仕様書に無く、プレート下面〜PCB 間（本フォークの想定は 1.0mm）に収まるかは未検証**。
    6.25U も Gateron 公式にあるがステム間隔の資料が無いため生成していない。
    **⚠ FR4 プレートでの強度注意（2026-09-07）**: ワイヤー溝（y 0.15〜2.65）がスイッチ開口
    （x=±7.0）とハウジング開口（x=±9.0）の間の幅 2.0mm の柱を横切るため、柱は上 5.8mm / 下 4.2mm の
    片持ち梁 2 本になる（島にはならず、両方とも根元は本体に付く。図参照）。1.2mm FR4 の概算では
    破断目安が先端 約 37N（上の柱、面外）で、打鍵・真上への引き抜きでは柱に力が掛からないが、
    **スイッチ取り外し時にプーラーをプレートに当ててテコにすると支点が柱の自由端に来て
    20〜40N が集中し、折れ得る**。Choc V2 版（11.2mm、約 19N）より 2 倍強いが、
    MX の FR4 プレートでスタビ開口脇に残る両端固定の梁（1.3mm 幅）と比べると剛性は約 1/3。
    Gateron の推奨開口は金属プレートの完成品（Keychron / NuPhy）での実績で、1.2mm FR4 での実績は
    確認できていない。**推奨: FR4 プレートでは 2u をスタビ無しにする。スタビを使うなら
    1.2〜1.5mm の金属プレート。** FR4 で試すならテストクーポンで取り外し操作を再現して確認する。
    KS-33 のツメが開口の左右（柱側）か上下かは未確認で、左右ならツメを外すときの荷重も柱に掛かる
  - **6.50u は PCB マウントスタビの標準規格が無い**（kiswitch / marbastlib にも無い）
    ため `_MXPCBStab` 版は生成していない

### スイッチ × スタビライザー対応表

| 実装するスイッチ | MX プレートマウント<br>→ サフィックス無し | MX PCB マウント<br>→ `_MXPCBStab` | Kailh Choc 1350 (V1)<br>→ `_ChocV1Stab` | Kailh Choc V2<br>→ `_ChocV2Stab` | Gateron LP 純正<br>→ `_GateronLPStab` |
|---|---|---|---|---|---|
| Cherry MX | ○ | ○ | ✕ | ✕ | ✕ |
| Cherry MX Low Profile | ✕ ステム高さ不一致 [^mxlp-stab] | ✕ ステム高さ不一致 [^mxlp-stab] | ✕ | ✕ | ✕ |
| Kailh Choc V1 (PG1350) | ✕ | ✕ | ○ | ✕ | ✕ |
| Kailh Choc V2 (PG1353) | ✕ | ✕ | ✕ ワイヤー干渉 | ○ ⚠ FR4 1.2mm では柱が片持ち梁（上記警告） | ✕ 情報なし |
| Gateron Low Profile | ✕ | ✕ | ✕ | ○ KS-33（KS-27 は情報なし）⚠ 同上 | ○ 純正（PCB 側要素なし、プレート下クリアランス未検証） |
| Hybrid（MX × Choc） | 実際に載せるスイッチの行に従う | 同左 | 同左 | 同左 | ✕（Gateron ベースのみ生成） |

- 「プレートマウント」と言っても MX 用と Choc 用のスタビは別部品で互換性はない
  （プレート開口形状・高さ・PCB への要求がすべて異なる）

[^mxlp-stab]: Cherry MX LP はステム上端が通常 MX より低く（プレート上面からハウジング上端 2.25 +
    ステム 3.6mm）、MX 用スタビに載せると 2u 以上のキーだけキーキャップが浮く。Cherry は
    MX LP 用スタビを単品販売しておらず、OEM キーボード（Corsair K70 LP / Cooler Master SK6xx /
    Filco Stingray）は各社独自の細ワイヤースタビ。市販部品で組む手段が無いため ✕（2026-09-07 時点）。
    スイッチ自体も国内自作キーボードショップの取り扱いが無く、DigiKey は MOQ 12,000、
    LCSC は在庫切れで、小口は海外小売か Amazon の小分け出品に限られる
- Hybrid ベースはスイッチ穴こそ MX / Choc 両対応だが、**スタビ付きキーは
  バリアント選択時点でどちらで組むか決める必要がある**（2u では MX NPTH 穴と
  Choc スロットが幾何的に共存できない）。Choc 側の可能性を残したい場合は
  `_ChocV1Stab` / `_ChocV2Stab` を選ぶ（MX で組むときはプレートマウント MX スタビが
  併用可能。`_MXPCBStab` を選ぶと Choc ビルドでのスタビ手段が無くなる）
- MX スタビ用のプレート開口線は `_MXPCBStab` 版の `User.5` にある（Cherry
  スタイル = プレートマウント・PCB マウント両対応）。プレートマウントスタビで
  組む場合もカット線目的で `_MXPCBStab` 版を使ってよい（NPTH 穴は無害）
- **寸法出典**: [kiswitch](https://github.com/kiswitch/kiswitch)
  （`KiSwitch/switch.py` StabilizerCherryMX のステム間隔 / `keycap.py`）と
  [marbastlib](https://github.com/ebastler/marbastlib)（CERN-OHL-P v2。
  `STAB_MX_*` の穴 y 座標・4.5u、`STAB_choc_*` の Choc V1 スロット形状）と
  [Keebio-Parts.pretty](https://github.com/keebio/Keebio-Parts.pretty)（MIT。
  `Kailh-Choc-V2-2u-Stabilizer-CPG1353G24D01-Cutout` の Choc V2 スロット形状）と
  [kb-plategen](https://github.com/keebio/kb-plategen)（MIT。
  `StabilizerCutout.ts` の MX / Choc V2 スタビ用プレートカット寸法）。
  ISO Enter の外形（上段 1.5u + 下段 1.25u 右端揃え、スイッチは下段列の中心）は
  kiswitch 準拠
- **注意**: キーキャップ範囲のコートヤードは、キャップ下に置くダイオード等も
  DRC エラーにする。物理的に問題ない配置は KiCad 側で除外指定するか、ベース版を使う
- **検証**: KiCad 10.0.5 の `kicad-cli fp export svg` で全バリアント（`--all` 時の 1540 ファイル）の
  パースを確認済み（`_GateronLPStab` は横・縦 1 件ずつ描画を目視確認。ライブラリ改名後の
  `variants-hybrid-pcb-only` 134 ファイルも再 export）。コートヤード寸法・スタビ穴座標は
  スクリプトで機械チェック済み。
  プレビュー画像はベース 33 + `_Diode` ベース 22 のみ
  （バリアントは枚数が膨大なため生成しない）

## ★ このフォーク限定: 裏面 SMD ダイオード付き `_Diode` バリアント（2026-08-31）

**手半田できるサイズの表面実装ダイオードを裏面（B.Cu）に組み込んだ `_Diode` 版を
自動生成してある。** ベース版（コートヤードなし）は `single.pretty/` 内の
`<ベース名>_Diode`（22 ファイル、生成物。`_alt*` / MX LP は既定で生成対象外）、キーキャップサイズ別は各 `variants-*` の
`<ベース名>_<サイズ>[_<スタビ>]_Diode`。

- **パッド**: SMD roundrect **2.0×1.4mm** ×2、ダイオード軸方向 ±1.6mm
  （内縁 0.6 / 外縁 2.6mm）。**SOD-123（1N4148W 等）/ SOD-323（1N4148WS 等）/
  MiniMELF（LL-34、LL4148 等）兼用**の手半田ロングパッド
- **パッド番号**: `1` `2` = スイッチ / **`3` = ダイオードのアノード /
  `4` = カソード**
- **回路図シンボル**: `symbols/key-switch-diode.kicad_sym` の **`SW_Key_Diode`**
  （スイッチ＋直列ダイオード一体、ピン 1/2/3=A/4=K）を使う。
  全 `_Diode` フットプリント共通。**ピン 2 と 3 は同一座標にスタックしてあり
  KiCad が接続扱いにするため、シンボルを置くだけでスイッチ→ダイオードの
  直列回路が完成する**（回路図でマトリクスに繋ぐのはピン 1 とピン 4=K のみ。
  検証: ERC エラーなし、ネットリストでピン 2/3 が同一ネット `Net-(SWx-A)` になる）。
  PCB 側ではパッド 2→3 のラッツネストに従って短い配線を 1 本引く
  （フットプリント内固定配線にしない理由: パッド 2 の位置がベースごとに異なり、
  `SW_MX_HotSwap_THT` 等ではクリアランス 0.2mm を満たす固定経路が存在しない。
  裏面の配線自由度も保てる）
- **配置**（全スイッチ種別で統一）: **左端に縦置き、中心 (−7.2, −4.0)、
  カソード = 上**
  - 中央北側 y≈−4.7 の**バックライト LED 窓**（Choc V1/V2・MX 等。
    SK6812 MINI-E のランドで x≈±3.2mm）から 3mm 以上離れており、
    アンダーグロー/バックライト LED と共存できる
  - スイッチ単体のコートヤード（16.5mm 角）内に完全に収まる =
    Choc ホットスワップ等でソケットパッドが左右にはみ出す帯
    （隣接キーと重なる領域）にはかからない。ホットスワップソケット本体
    （下半分）からも離してあり、こてが入る
  - 最小クリアランスは Choc サイドボス NPTH (−5.5, 0) との 0.87mm
- **生成対象外（自動スキップ）**: 裏面に物理干渉がある 6 ベース =
  両面実装の `double.pretty` 全 5 種と `SW_MX_Kailh_Choc_V1V2_HotSwap_Hybrid`
  （MX ソケットが裏面上半分を占有）。`_alt1` 版は両ソケットとも下半分なので生成される
- **Compatibility Table（下記・上流のまま）の各フットプリントについて、
  スイッチ互換性は `_Diode` 版でも同一**（ダイオード要素の追加のみ）

## ★ このフォーク限定: ライブラリ構成（実装方式で分割。2026-08-30）

上流はリポジトリ直下が 1 ライブラリだったが、このフォークでは**ベースを実装方式、
バリアントをスイッチ種別で `.pretty` に分割**してある。KiCad には使うものを
別ライブラリとして登録する（最大 6 つ）:

| ライブラリ | 内容 | ファイル数 |
|---|---|---|
| `single.pretty/` | **片面実装**ベース（`_alt*` の片面版・`_nSilk`・`_swap` を含む） | 50（手書き 28 + 生成 `_Diode` 22） |
| `double.pretty/` | **両面実装**ベース＝リバーシブル基板用（`_double`、その `_alt1/_alt2` を含む） | 5 |
| `variants-mx.pretty/` | バリアント: MX 純系（ハイブリッド除く。生成物） | 464 |
| `variants-choc.pretty/` | バリアント: Choc 純系（V1 / V2 / Choc V1V2 ハイブリッド＝プレート共用可。生成物） | 464 |
| `variants-hybrid-pcb-only.pretty/` | バリアント: MX × Choc ハイブリッド。**PCB 互換のみ**、プレート・スタビは別設計（生成物。旧 `variants-mx-choc`） | 134 |
| `variants-gateron.pretty/` | バリアント: Gateron Low Profile（生成物） | 128 |

このほか `symbols/key-switch-diode.kicad_sym`（`_Diode` フットプリント用の
スイッチ＋ダイオード一体シンボル `SW_Key_Diode`）をシンボルライブラリとして登録できる。

サフィックスの意味（ベース名の系統）:

- **無印** = 片面実装の標準版
- **`_double`** = 両面実装（リバーシブル基板の表裏どちらにも実装できる）
- **`_alt1` / `_alt2`** = 同機能の代替パッド/穴配置（例: `Kailh_Choc_V1_THT_alt1` は
  クリッキースイッチのバネ逃げ NPTH 追加版。詳細は各 descr と Compatibility Table 脚注）
- **`_nSilk`** = 表シルクなし、**`_swap`** = ピン番号入替え
- HotSwap の **`_PTH`** = ソケット穴メッキあり / **`_THT`** = メッキなし
- **`_Diode`** = 裏面 SMD ダイオードパッド付き（生成物。前節参照）

このフォークを submodule として使う場合は上流ではなくこちらの URL を指定する
（次節「Usage」の URL は上流のまま。また上流と違い**リポジトリ直下は
ライブラリではない**ので、上記 6 フォルダのうち使うものを個別に登録すること）:

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

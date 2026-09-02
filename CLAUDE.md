# kicad-key-switch-footprints

キースイッチ(MX / Kailh Choc / Gateron Low Profile)用 KiCad フットプリント集。
`single.pretty/`(片面実装。手書き28+生成 `_Diode` 27)+`double.pretty/`(両面実装5)がベース本体、
`preview/*.svg` が README 用のプレビュー画像(ベース33+`_Diode` 27)。リポジトリ直下はライブラリではない。
`symbols/key-switch-diode.kicad_sym` は `_Diode` フットプリント用の一体シンボル(手書き)。

## 構成とレイヤ規約

- **ベース(single/double.pretty の手書き33ファイル)= キーキャップなし**: F.CrtYd はスイッチ単体の占有範囲(16.5mm角)。
  `_alt1/_alt2` は代替パッド配置で親系統(片面/両面)のフォルダに入れる。
  **`*_Diode.kicad_mod` は生成物**(手編集禁止。`_Diode` はスクリプトの予約サフィックスで、
  再生成時に削除されるため手書きベース名に使ってはいけない)
- **`variants-*.pretty/`(生成物、スイッチ種別で4ライブラリ)**: キーキャップサイズ別バリアント。
  variants-mx(MX純系550) / variants-choc(Choc純系406) / variants-mx-choc(MX×Chocハイブリッド220) /
  variants-gateron(Gateron LP 92)。
  再生成は `python3 scripts/generate_variants.py`(全削除→再生成。手編集禁止、直すのはスクリプト側)
  - コートヤード = キーキャップ範囲。外縁は公称(w×19.05×19.05)より各辺0.025mm控え
    (1u なら中心線±9.475・線幅0.05で外縁19.00mm角)。19.05mmピッチの隣接キーと誤DRCしないため
  - `_MXPCBStab` = Cherry MX PCBマウントスタビのNPTH穴付き(MX系ベースのみ。ステム間隔はkiswitch、
    穴y座標(小−6.985/大+8.255=15.24mm間隔)と4.5uはmarbastlib準拠、詳細はREADMEのフォーク限定節)。
    スタビ用プレートカット線をUser.5に持つ(6.75×14 中心y=+1、kb-plategen "Normal"準拠、
    プレート/PCBマウント両対応)。MXのプレートマウントスタビはPCB側に要素不要なので
    サフィックス無し版でも組めるが、プレートカット線が要るなら_MXPCBStab版を使う
  - `_ChocV1Stab` = Kailh Choc 1350(V1)スタビ用(Choc V1対応ベース×2.00u/6.25uのみ)。丸穴ではなく
    **Edge.Cutsの角丸スロット4個**+プレートカット線をUser.5に持つ(形状はmarbastlib STAB_choc_*準拠)。
    **Choc V1専用**(ワイヤーがV2ハウジングと干渉するためV2不可。V2専用ベースには生成しない)
  - `_ChocV2Stab` = Kailh Choc V2スタビ(CPG1353G24D01)用(2.00uのみ、Choc V2/Gateron KS-33対応・V1非互換)。
    **Edge.Cutsの矩形スロット2個**(6.5×9.5mm、中心x=±12.0、形状はKeebio-Parts.pretty準拠、MIT)。
    プレートカット線をUser.5に持つ(本体5.95×7.95+突出4.55×6.25+ワイヤー溝全幅×1.4、
    kb-plategen準拠、重なる外形はプレートCAD側でunion)。ホットスワップ系はソケットパッドと
    スロットが物理干渉するため生成しない(スクリプトが干渉チェックで自動スキップ、THT系6種のみ)
  - `_Diode` = 裏面SMDダイオードパッド付き(B.Cu/B.Paste/B.Mask の 2.0×1.4mm パッド ±1.6mm =
    SOD-123/SOD-323/MiniMELF 兼用手半田ロング。パッド3=A/4=K、B.SilkSカソードバー+B.Fab外形)。
    配置は全種別統一で左端縦置き(−7.2,−4.0)、カソード=上。中央北側 y≈−4.7 のLED窓
    (SK6812 MINI-E ランド x≈±3.2)を回避するため中央寄りには置かない。ベース版はコートヤードそのままで
    single.pretty 内に生成。裏面が物理干渉する6ベース(double全5+MX×Choc HotSwapハイブリッド)は
    自動スキップ(パッド円近似+裏面図形の線分サンプリング判定)。
    回路図は `symbols/key-switch-diode.kicad_sym` の SW_Key_Diode。ピン2/3は同一座標スタック=
    KiCadが接続扱い(置くだけで直列完成、PCBではパッド2→3の短い配線をラッツネストに従い引く)
- **User.1〜User.4**: プレートカット線(User.1=15.60 化粧カバー / User.2=14.00 MX系 / User.3=13.95 Choc V2 / User.4=13.80 Choc V1)。
  User.2〜4 は正方形+四隅 R2.00 コーナーリリーフ(dogbone。角中心の円を対角外側へ、fp_line 4+fp_arc 4 の一体外形。
  ルーター加工プレートの内角Rでスイッチが座らない対策)。User.1 は fp_rect のまま(R2 だと19.05ピッチで隣と重なる)。
  **User.2〜4 の図形は手編集せず `python3 scripts/plate_cut_lines.py` で書き直す**(半径 `RELIEF_R`・寸法 `PLATE_CUTS` が定数、
  33 ベースを冪等に書き換え、descr も更新。実行後は generate_variants.py で _Diode/variants を再生成)。
  外端 ±9.0 なので `_MXPCBStab` 2u 系のスタビ開口(x=±8.563)と 0.44mm 重なる(既知・許容、プレート CAD で union)。
  参考写真は `docs/plate-corner-relief-sample.jpeg`(Waveshare ScreenKey Module 付属プレート)
- **User.5**: スタビ用プレートカット線(`_MXPCBStab` / `_ChocV1Stab` / `_ChocV2Stab` バリアントのみ)
- 各ファイルの `descr` にレイヤ⇄用途の対応を記載する
- `.kicad_mod` は新旧2書式が混在(旧: 20221018/tstamp/fp_text value が29ファイル、新: 20241229/uuid/property "Value" が4ファイル)。一括処理は正規表現の1行前提を避け、括弧対応カウントでブロック抽出する

## プレビュー SVG の生成

```bash
cd scripts
pnpm install        # 初回のみ
npm run run:all     # export + svg を一括実行
```

- `npm run export` … `kicad-cli fp export svg` で全フットプリントを `scripts/export/`(git 管理外)へエクスポート
  - `kicad-cli` が PATH に無い環境では AppImage 経由で実行する:
    `~/Applications/KiCad-10.0.5-x86_64.AppImage kicad-cli fp export svg -o ./export/ ./../single.pretty/`
    `~/Applications/KiCad-10.0.5-x86_64.AppImage kicad-cli fp export svg -o ./export/ ./../double.pretty/`
    (その後 `npm run svg` で後処理)
- `npm run svg` … `svg-processor.js` が `scripts/export/*.svg` を後処理して `preview/` へ出力

`svg-processor.js` の後処理内容:
1. `width`/`height` を 100% に正規化し黒背景 `<rect>` を追加
2. KiCad が末尾に描く黒塗りのドリル穴円(`fill:#000000; stroke:none` で円のみのグループ)を削除
   - 黒背景と同化して穴が見えなくなり、MX 中央穴の黒円が Fab レイヤーの十字マークを隠すため。
     穴はマスクレイヤーの半透明シアン円で表示される(全フットプリントで下に存在することを確認済み)

## プレビューのレンダリング確認方法

SVG を PNG にラスタライズして目視確認する。Inkscape を使用:

```bash
inkscape -w 400 preview/SW_MX_THT.svg -o /tmp/SW_MX_THT.png
```

確認ポイント:
- 穴(NPTH・ドリル)が見えているか(黒背景に黒円で消えていないか)
- MX フットプリントの中央十字マーク(Fab レイヤー、グレー)が穴に隠れていないか
- PTH パッド内の白いドリル円が表示されているか

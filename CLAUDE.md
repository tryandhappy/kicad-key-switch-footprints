# kicad-key-switch-footprints

キースイッチ(MX / Kailh Choc / Gateron Low Profile)用 KiCad フットプリント集。
`single.pretty/`(片面実装28)+`double.pretty/`(両面実装5)がベース本体、
`preview/*.svg` が README 用のプレビュー画像。リポジトリ直下はライブラリではない。

## 構成とレイヤ規約

- **ベース(single/double.pretty の33ファイル)= キーキャップなし**: F.CrtYd はスイッチ単体の占有範囲(16.5mm角)。
  `_alt1/_alt2` は代替パッド配置で親系統(片面/両面)のフォルダに入れる
- **`variants-*.pretty/`(生成物、スイッチ種別で4ライブラリ)**: キーキャップサイズ別バリアント。
  variants-mx(MX純系299) / variants-choc(Choc純系191) / variants-mx-choc(MX×Chocハイブリッド127) /
  variants-gateron(Gateron LP 43)。
  再生成は `python3 scripts/generate_variants.py`(全削除→再生成。手編集禁止、直すのはスクリプト側)
  - コートヤード = キーキャップ範囲。外縁は公称(w×19.05×19.05)より各辺0.025mm控え
    (1u なら中心線±9.475・線幅0.05で外縁19.00mm角)。19.05mmピッチの隣接キーと誤DRCしないため
  - `_MXPCBStab` = Cherry MX PCBマウントスタビのNPTH穴付き(MX系ベースのみ。ステム間隔はkiswitch、
    穴y座標(小−6.985/大+8.255=15.24mm間隔)と4.5uはmarbastlib準拠、詳細はREADMEのフォーク限定節)。
    MXのプレートマウントスタビはサフィックス無し版で対応(PCB側に要素不要)
  - `_ChocStab` = Kailh Choc 1350(V1)スタビ用(Choc V1対応ベース×2.00u/6.25uのみ)。丸穴ではなく
    **Edge.Cutsの角丸スロット4個**+プレートカット線をUser.5に持つ(形状はmarbastlib STAB_choc_*準拠)。
    **Choc V1専用**(ワイヤーがV2ハウジングと干渉するためV2不可。V2専用ベースには生成しない)
  - `_ChocV2Stab` = Kailh Choc V2スタビ(CPG1353G24D01)用(2.00uのみ、Choc V2/Gateron KS-33対応・V1非互換)。
    **Edge.Cutsの矩形スロット2個**(6.5×9.5mm、中心x=±12.0、形状はKeebio-Parts.pretty準拠、MIT)。
    プレートカット線なし(寸法はKeebio Plate Generator参照)。ホットスワップ系はソケットパッドと
    スロットが物理干渉するため生成しない(スクリプトが干渉チェックで自動スキップ、THT系6種のみ)
- **User.1〜User.4**: プレートカット線(User.1=15.60 化粧カバー / User.2=14.00 MX系 / User.3=13.95 Choc V2 / User.4=13.80 Choc V1)
- **User.5**: Chocスタビ用プレートカット線(`_ChocStab` バリアントのみ)
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

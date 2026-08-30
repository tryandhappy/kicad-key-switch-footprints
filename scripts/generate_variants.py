#!/usr/bin/env python3
"""キーキャップサイズバリアント生成スクリプト

single.pretty/(片面実装)と double.pretty/(両面実装)のベースフットプリント
(キーキャップなし)から、キーキャップサイズ別のフットプリントを
スイッチ種別ごとの 4 ライブラリに生成する:
variants-mx.pretty(MX 純系) / variants-choc.pretty(Choc V1/V2 純系) /
variants-mx-choc.pretty(MX×Choc ハイブリッド) / variants-gateron.pretty(Gateron LP)。

- コートヤードをキーキャップ占有範囲に置換
  (外縁 = 公称キーキャップ範囲より各辺 0.025mm 控え。
   19.05mm ピッチで隣接キー同士が誤 DRC エラーにならないため)
- 2u 以上は Cherry MX PCB マウントスタビ穴付きの `_MXPCBStab` 版も生成
  (MX 系ベースのみ。MX のプレートマウントスタビは PCB 側に要素不要なので
   プレーン版がそのまま対応。スタビ用プレートカット線は User.5 に持ち、
   プレートマウント・PCB マウント両対応の Cherry スタイル)
- Choc V1 対応ベースには Kailh Choc 1350(V1)スタビ用の `_ChocV1Stab` 版も生成
  (2u / 6.25u のみ = Kailh が製造しているサイズ。PCB は丸穴ではなく
   角丸スロット 4 個の切り欠き(Edge.Cuts)+ プレート必須。
   プレートカット線は User.5。Choc V1 スイッチ専用で V2 とは非互換)
- Choc V2 / Gateron KS-33 対応ベースには Kailh Choc V2 スタビ
  (CPG1353G24D01)用の `_ChocV2Stab` 版も生成
  (2u のみ確認。PCB は矩形スロット 2 個の切り欠き(Edge.Cuts)+ プレート必須。
   プレートカット線は User.5)
- 裏面 SMD ダイオード付きの `_Diode` 版も生成する
  (SOD-123 / SOD-323 / MiniMELF 兼用の手半田ロングパッド。パッド 3=A / 4=K。
   ベース(コートヤードなし)への `_Diode` 版は single/double.pretty 内に
   生成する = 生成物。物理干渉するベースは自動スキップ)
- 寸法出典: kiswitch (https://github.com/kiswitch/kiswitch) KiSwitch/switch.py,
  keycap.py、marbastlib (https://github.com/ebastler/marbastlib,
  CERN-OHL-P v2) STAB_MX_*.kicad_mod / STAB_choc_*.kicad_mod、
  Keebio-Parts.pretty (https://github.com/keebio/Keebio-Parts.pretty, MIT)
  Kailh-Choc-V2-2u-Stabilizer-CPG1353G24D01-Cutout.kicad_mod、および
  kb-plategen (https://github.com/keebio/kb-plategen, MIT)
  src/maker_models/StabilizerCutout.ts (MX/Choc V2 のプレートカット寸法)

実行: python3 scripts/generate_variants.py
"""

import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIRS = {k: ROOT / f"variants-{k}.pretty"
            for k in ("mx", "choc", "mx-choc", "gateron")}


def family(base_name):
    """スイッチ種別("mx" / "choc" / "mx-choc" / "gateron")をベース名から決める。"""
    if base_name.startswith("SW_Gateron_"):
        return "gateron"
    if base_name.startswith("SW_Kailh_Choc_"):
        return "choc"
    if "Choc" in base_name:   # SW_MX_*Choc* ハイブリッド
        return "mx-choc"
    return "mx"


def out_dir(base_name):
    """バリアントの出力先ライブラリをベース名から決める(スイッチ種別)。"""
    return OUT_DIRS[family(base_name)]

U = 19.05          # 1u ピッチ [mm]
SHRINK = 0.025     # コートヤード外縁の控え(各辺)[mm]
LINE_W = 0.05      # コートヤード線幅 [mm]

# 通常(矩形)キーキャップの幅 [u]
REGULAR_SIZES = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.75, 3.0, 4.5, 6.0, 6.25, 6.5, 7.0]

# Cherry MX PCB マウントスタビ (ステム間隔は kiswitch StabilizerCherryMX、
# 穴の y と 4.5u は marbastlib STAB_MX_* 準拠)
STAB_MIN_SIZE = 2.0
STAB_X_OFFSET = {   # ステム位置 x = ±offset [mm]。無いサイズは PCB スタビ規格なし
    2.0: 11.938, 2.25: 11.938, 2.75: 11.938,
    3.0: 19.05, 4.5: 33.3375,
    6.0: 47.625, 6.25: 50.0, 7.0: 57.15,
}
STAB_SMALL = (3.048, -6.985)   # (穴径, y) 上側の小穴
STAB_LARGE = (3.9878, 8.255)   # (穴径, y) 下側の大穴(ワイヤー側)。小穴と 15.24mm 間隔

# Kailh Choc 1350 スタビ (marbastlib STAB_choc_2u 準拠)。PCB は角丸スロットの
# 切り欠き(Edge.Cuts)、プレートカット線は User.5(marbastlib では Eco1=19.05mm
# ピッチ注記 / Eco2=プレートカット。当リポジトリの規約に合わせて User.5 に置く)。
# CHOC_STAB_SEGMENTS は 2u(ステム中心 x=±12.0)の右側+左側の全セグメント。
# 他サイズはステム中心の差分だけ各座標を外側へシフトして生成する。
CHOC_STAB_X = {2.0: 12.0, 6.25: 38.0}   # Kailh はこの 2 サイズのみ製造
CHOC_STAB_BASE_X = 12.0

# Kailh Choc V2 スタビ (CPG1353G24D01)。Choc V2 / Gateron KS-33 用で V1 とは非互換
# (Keebio 商品ページより。1350 スタビのワイヤーは V2 ハウジングと干渉する)。
# プレートマウント + PCB 矩形スロット 2 個(Edge.Cuts、角丸なし)。プレートカット
# 寸法は Keebio Plate Generator 参照(当リポジトリにはプレートカット線なし)。
# 形状出典: Keebio-Parts.pretty (MIT)
# Kailh-Choc-V2-2u-Stabilizer-CPG1353G24D01-Cutout.kicad_mod
CHOC_V2_STAB_X = {2.0: 12.0}       # スロット中心 x = ±12.0。Kailh 製造は 2u のみ確認
CHOC_V2_STAB_HALF = (3.25, 4.75)   # スロット半幅/半高 → 6.5 x 9.5mm

# スタビ用プレートカット線 (User.5)。寸法は Keebio kb-plategen (MIT)
# src/maker_models/StabilizerCutout.ts 準拠 (同ソースは y 上向きなので反転)。
# MX = "Normal" カット。プレートマウント・PCB マウント両対応の Cherry スタイル
MX_PLATE_CUT = (6.75, 14.0, 1.0)   # (幅, 高さ, 中心y)。ステム位置は STAB_X_OFFSET
# Choc V2 = 本体+突出+ワイヤー溝の角丸矩形 3 種(角R0.5)。外形は互いに重なる
# (kb-plategen も union して出力している)ので、プレート CAD 側で union する
CHOC_V2_PLATE_PARTS = [(5.95, 7.95, 0.3441), (4.55, 6.25, 6.7559)]  # (幅,高さ,中心y)
CHOC_V2_PLATE_WIRE = (1.4, 8.2809)  # ワイヤー溝 (高さ, 中心y)。幅はステム間隔
# (kind, layer, width, coords) kind: line=(x1,y1,x2,y2) / arc=(sx,sy,mx,my,ex,ey)
CHOC_STAB_SEGMENTS = [
    # --- PCB スロット (Edge.Cuts): 本体 5.3x5.5 / ワイヤー 4.0x3.5, 角 R0.5
    ("line", "Edge.Cuts", 0.12, (14.65, 1.8, 14.65, -2.7)),
    ("line", "Edge.Cuts", 0.12, (14.15, -3.2, 9.85, -3.2)),
    ("line", "Edge.Cuts", 0.12, (14.15, 2.3, 9.85, 2.3)),
    ("line", "Edge.Cuts", 0.12, (9.35, 1.8, 9.35, -2.7)),
    ("arc", "Edge.Cuts", 0.12, (14.15, -3.2, 14.503553, -3.053553, 14.65, -2.7)),
    ("arc", "Edge.Cuts", 0.12, (14.65, 1.8, 14.503553, 2.153553, 14.15, 2.3)),
    ("arc", "Edge.Cuts", 0.12, (9.35, -2.7, 9.496447, -3.053553, 9.85, -3.2)),
    ("arc", "Edge.Cuts", 0.12, (9.85, 2.3, 9.496447, 2.153553, 9.35, 1.8)),
    ("line", "Edge.Cuts", 0.12, (14.0, -6.0, 14.0, -8.5)),
    ("line", "Edge.Cuts", 0.12, (13.5, -9.0, 10.5, -9.0)),
    ("line", "Edge.Cuts", 0.12, (13.5, -5.5, 10.5, -5.5)),
    ("line", "Edge.Cuts", 0.12, (10.0, -6.0, 10.0, -8.5)),
    ("arc", "Edge.Cuts", 0.12, (13.5, -9.0, 13.853553, -8.853553, 14.0, -8.5)),
    ("arc", "Edge.Cuts", 0.12, (14.0, -6.0, 13.853553, -5.646447, 13.5, -5.5)),
    ("arc", "Edge.Cuts", 0.12, (10.0, -8.5, 10.146447, -8.853553, 10.5, -9.0)),
    ("arc", "Edge.Cuts", 0.12, (10.5, -5.5, 10.146447, -5.646447, 10.0, -6.0)),
    # --- プレートカット (User.5): 本体+ワイヤーの一体外形
    ("line", "User.5", 0.05, (15.15, 2.55, 15.15, -3.3)),
    ("line", "User.5", 0.05, (14.65, 3.05, 9.35, 3.05)),
    ("line", "User.5", 0.05, (14.65, -3.8, 14.3, -3.8)),
    ("line", "User.5", 0.05, (13.8, -4.3, 13.8, -7.95)),
    ("line", "User.5", 0.05, (13.3, -8.45, 10.7, -8.45)),
    ("line", "User.5", 0.05, (10.2, -4.3, 10.2, -7.95)),
    ("line", "User.5", 0.05, (9.35, -3.8, 9.7, -3.8)),
    ("line", "User.5", 0.05, (8.85, 2.55, 8.85, -3.3)),
    ("arc", "User.5", 0.05, (14.65, -3.8, 15.003553, -3.653553, 15.15, -3.3)),
    ("arc", "User.5", 0.05, (15.15, 2.55, 15.003553, 2.903553, 14.65, 3.05)),
    ("arc", "User.5", 0.05, (14.3, -3.8, 13.946447, -3.946447, 13.8, -4.3)),
    ("arc", "User.5", 0.05, (13.3, -8.45, 13.653553, -8.303553, 13.8, -7.95)),
    ("arc", "User.5", 0.05, (10.2, -7.95, 10.346447, -8.303553, 10.7, -8.45)),
    ("arc", "User.5", 0.05, (10.2, -4.3, 10.053553, -3.946447, 9.7, -3.8)),
    ("arc", "User.5", 0.05, (8.85, -3.3, 8.996447, -3.653553, 9.35, -3.8)),
    ("arc", "User.5", 0.05, (9.35, 3.05, 8.996447, 2.903553, 8.85, 2.55)),
]

# 裏面 SMD ダイオード(SOD-123 / SOD-323 / MiniMELF LL-34, LL4148 兼用の
# 手半田ロングパッド)。パッド 3 = アノード / 4 = カソード。
# 局所座標: 軸方向 a(カソード = a 負方向)/ 直交方向 c
DIODE_PAD = (2.0, 1.4)        # パッド(軸方向長, 直交高さ)
DIODE_PAD_OFF = 1.6           # パッド中心 = a ±1.6(内縁 0.6 / 外縁 2.6)
DIODE_SILK = (2.86, 0.96)     # B.SilkS 長辺の半長 / c オフセット(線幅 0.12)
DIODE_FAB = (1.9, 0.9, -1.2)  # B.Fab ボディ半長 / 半高 / カソードバー a 位置(線幅 0.1)
# family -> (cx, cy, vertical)。vertical=True は 90°回転。
# カソード向きの規則: 座標の負方向 = 縦置きは上 / 横置きは左。
# 位置は全ベースの B.Cu 占有(パッド・穴・ソケット外形)を実測して決定:
# - mx: 左端縦置き。SW_MX_HotSwap_THT の上半分 THT パッドとソケット本体を回避
# - choc: SW_Kailh_Choc_V1_HotSwap_THT の上半分 THT パッド (0,-5.9)/(5,-3.8) と
#   Choc V2 ボス穴 (5,-5.15) を避けて左寄せ横置き
# - gateron: SW_Gateron_LowProfile_HotSwap_THT の上半分 THT パッド
#   (-2.6,-5.75)/(4.4,-4.7) を避けて右上横置き
DIODE_PLACEMENT = {
    "mx": (-7.2, -4.0, True),
    "choc": (-4.6, -5.0, False),
    "mx-choc": (-4.6, -5.0, False),
    "gateron": (1.8, -7.2, False),
}


def find_blocks(s, keyword):
    """'(keyword' で始まる括弧対応ブロックの (start, end) を列挙する。"""
    i = 0
    while True:
        j = s.find("(" + keyword, i)
        if j < 0:
            return
        depth = 0
        k = j
        while k < len(s):
            if s[k] == "(":
                depth += 1
            elif s[k] == ")":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        yield j, k + 1
        i = k + 1


def new_uuid():
    return str(uuid.uuid4())


def courtyard_items(size, layers):
    """サイズに応じたコートヤード図形(旧書式1行スタイル)を返す。"""
    items = []
    for layer in layers:
        if size in ("ISOEnter", "ISOEnterFlip"):
            # kiswitch の ISO Enter 外形(上段1.5u×1u+下段1.25u×1u、右端揃え、
            # スイッチは下段1.25u列の中心・上下2uの中心)を各辺0.05mm(=控え+線幅/2)
            # 内側にオフセットした中心線
            pts = [
                (11.85625, 19.0), (11.85625, -19.0), (-16.61875, -19.0),
                (-16.61875, -0.05), (-11.85625, -0.05), (-11.85625, 19.0),
            ]
            if size == "ISOEnterFlip":
                # キーキャップのみ上下反転。スイッチ(とスタビ)の向きは変えない
                pts = [(x, -y) for x, y in pts]
            xy = " ".join(f"(xy {x} {y})" for x, y in pts)
            items.append(
                f'(fp_poly (pts {xy}) (stroke (width {LINE_W}) (type solid))'
                f' (fill none) (layer "{layer}") (tstamp {new_uuid()}))'
            )
        else:
            hx = round(size * U / 2 - SHRINK - LINE_W / 2, 6)
            hy = round(U / 2 - SHRINK - LINE_W / 2, 6)
            items.append(
                f'(fp_rect (start {-hx} {-hy}) (end {hx} {hy})'
                f' (stroke (width {LINE_W}) (type solid))'
                f' (fill none) (layer "{layer}") (tstamp {new_uuid()}))'
            )
    return items


def choc_stab_items(size):
    """Kailh Choc 1350 スタビの PCB スロット+プレートカット線を返す。

    CHOC_STAB_SEGMENTS(2u 基準)を、ステム中心の差分だけ左右対称に
    外側へシフトし、左側は x を反転して生成する。
    """
    shift = CHOC_STAB_X[size] - CHOC_STAB_BASE_X
    items = []
    for kind, layer, width, coords in CHOC_STAB_SEGMENTS:
        for mirror in (1, -1):
            pts = []
            for x, y in zip(coords[0::2], coords[1::2]):
                pts.append((round(mirror * (x + shift), 6), y))
            if kind == "line":
                (x1, y1), (x2, y2) = pts
                items.append(
                    f'(fp_line (start {x1} {y1}) (end {x2} {y2})'
                    f' (stroke (width {width}) (type solid))'
                    f' (layer "{layer}") (tstamp {new_uuid()}))'
                )
            else:
                # 左右反転で円弧の向きが逆になるため start/end を入れ替える
                (sx, sy), (mx, my), (ex, ey) = pts
                if mirror == -1:
                    (sx, sy), (ex, ey) = (ex, ey), (sx, sy)
                items.append(
                    f'(fp_arc (start {sx} {sy}) (mid {mx} {my}) (end {ex} {ey})'
                    f' (stroke (width {width}) (type solid))'
                    f' (layer "{layer}") (tstamp {new_uuid()}))'
                )
    return items


def rounded_rect_items(cx, cy, w, h, layer, lw, r=0.5):
    """角丸矩形の外形線(4辺+4円弧、旧書式1行スタイル)を返す。"""
    x1, x2 = cx - w / 2, cx + w / 2
    y1, y2 = cy - h / 2, cy + h / 2
    d = r * (1 - 2 ** 0.5 / 2)   # 角の円弧の中点オフセット
    segs = [
        ("line", (x1 + r, y1, x2 - r, y1)),
        ("line", (x2, y1 + r, x2, y2 - r)),
        ("line", (x2 - r, y2, x1 + r, y2)),
        ("line", (x1, y2 - r, x1, y1 + r)),
        ("arc", (x2 - r, y1, x2 - d, y1 + d, x2, y1 + r)),
        ("arc", (x2, y2 - r, x2 - d, y2 - d, x2 - r, y2)),
        ("arc", (x1 + r, y2, x1 + d, y2 - d, x1, y2 - r)),
        ("arc", (x1, y1 + r, x1 + d, y1 + d, x1 + r, y1)),
    ]
    items = []
    for kind, coords in segs:
        p = [round(v, 6) for v in coords]
        if kind == "line":
            items.append(
                f'(fp_line (start {p[0]} {p[1]}) (end {p[2]} {p[3]})'
                f' (stroke (width {lw}) (type solid))'
                f' (layer "{layer}") (tstamp {new_uuid()}))'
            )
        else:
            items.append(
                f'(fp_arc (start {p[0]} {p[1]}) (mid {p[2]} {p[3]}) (end {p[4]} {p[5]})'
                f' (stroke (width {lw}) (type solid))'
                f' (layer "{layer}") (tstamp {new_uuid()}))'
            )
    return items


def mx_plate_cut_items(size):
    """Cherry MX スタビ用プレートカット線(User.5)を返す。ISO Enter は 90°回転。"""
    w, h, cy = MX_PLATE_CUT
    items = []
    if size in ("ISOEnter", "ISOEnterFlip"):
        # 縦 2u スタビ。stab_holes と同じ回転: (x,y) -> (-y, x)
        # (縦スタビは上下対称なので ISOEnterFlip でも同一配置)
        for y in (-STAB_X_OFFSET[2.0], STAB_X_OFFSET[2.0]):
            items += rounded_rect_items(-cy, y, h, w, "User.5", 0.05)
    else:
        for x in (-STAB_X_OFFSET[size], STAB_X_OFFSET[size]):
            items += rounded_rect_items(x, cy, w, h, "User.5", 0.05)
    return items


def choc_v2_plate_items(size):
    """Kailh Choc V2 スタビ用プレートカット線(User.5)を返す。

    kb-plategen の 3 プリミティブ(本体・突出・ワイヤー溝)をそのまま描く。
    外形は互いに重なるため、プレート CAD 側で union して使う。
    """
    x = CHOC_V2_STAB_X[size]
    items = []
    for mirror in (1, -1):
        for w, h, cy in CHOC_V2_PLATE_PARTS:
            items += rounded_rect_items(mirror * x, cy, w, h, "User.5", 0.05)
    wh, wy = CHOC_V2_PLATE_WIRE
    items += rounded_rect_items(0, wy, 2 * x, wh, "User.5", 0.05)
    return items


def choc_v2_stab_items(size):
    """Kailh Choc V2 スタビの PCB スロット(fp_rect, Edge.Cuts)を返す。"""
    hw, hh = CHOC_V2_STAB_HALF
    items = []
    for mirror in (1, -1):
        cx = mirror * CHOC_V2_STAB_X[size]
        items.append(
            f'(fp_rect (start {round(cx - hw, 6)} {-hh}) (end {round(cx + hw, 6)} {hh})'
            f' (stroke (width 0.12) (type solid)) (fill none)'
            f' (layer "Edge.Cuts") (tstamp {new_uuid()}))'
        )
    return items


def choc_v2_stab_slot_rects(size):
    """Choc V2 スタビの PCB スロット矩形 (x1, y1, x2, y2) を返す(干渉チェック用)。"""
    hw, hh = CHOC_V2_STAB_HALF
    x = CHOC_V2_STAB_X[size]
    return [(m * x - hw, -hh, m * x + hw, hh) for m in (1, -1)]


def choc_stab_slot_rects(size):
    """Choc スタビの PCB スロットの外接矩形 (x1, y1, x2, y2) を返す(干渉チェック用)。"""
    x = CHOC_STAB_X[size]
    rects = []
    for cx, cy, hw, hh in ((x, -0.45, 2.65, 2.75), (x, -7.25, 2.0, 1.75)):
        for mirror in (1, -1):
            rects.append((mirror * cx - hw, cy - hh, mirror * cx + hw, cy + hh))
    return rects


def stab_holes(size):
    """Cherry MX PCB マウントスタビの NPTH パッド(旧書式1行スタイル)を返す。"""
    holes = []
    if size in ("ISOEnter", "ISOEnterFlip"):
        # 縦向き 2u スタビ(90°回転)。大穴(ワイヤー側)が左(x=-8.225)。
        # ステム位置 y=±11.938 は上下対称なので ISOEnterFlip でも同一
        for y in (-STAB_X_OFFSET[2.0], STAB_X_OFFSET[2.0]):
            holes.append((STAB_SMALL[0], -STAB_SMALL[1], y))
            holes.append((STAB_LARGE[0], -STAB_LARGE[1], y))
    else:
        off = STAB_X_OFFSET[size]
        for x in (-off, off):
            holes.append((STAB_SMALL[0], x, STAB_SMALL[1]))
            holes.append((STAB_LARGE[0], x, STAB_LARGE[1]))
    return [
        f'(pad "" np_thru_hole circle (at {x} {y}) (size {d} {d}) (drill {d})'
        f' (layers "*.Cu" "*.Mask") (tstamp {new_uuid()}))'
        for d, x, y in holes
    ]


def diode_xform(cx, cy, vertical):
    """ダイオード局所座標 (a, c) → 全体座標 (x, y) の変換関数を返す。"""
    if vertical:
        return lambda a, c: (round(cx + c, 6), round(cy + a, 6))
    return lambda a, c: (round(cx + a, 6), round(cy + c, 6))


def diode_items(cx, cy, vertical):
    """裏面 SMD ダイオードのパッド 3(A)/4(K)+B.SilkS 極性マーク+B.Fab 外形を返す。

    テキストは置かない(裏面のミラー処理が不要になる)。極性はカソードバーで示す。
    """
    pt = diode_xform(cx, cy, vertical)
    pw, ph = DIODE_PAD
    rot = " 90" if vertical else ""
    items = []
    for num, a in (("3", DIODE_PAD_OFF), ("4", -DIODE_PAD_OFF)):
        x, y = pt(a, 0)
        items.append(
            f'(pad "{num}" smd roundrect (at {x} {y}{rot}) (size {pw} {ph})'
            f' (layers "B.Cu" "B.Paste" "B.Mask") (roundrect_rratio 0.2)'
            f' (tstamp {new_uuid()}))'
        )
    sa, sc = DIODE_SILK
    fa, fc, fbar = DIODE_FAB
    layer_segs = [
        # B.SilkS: 長辺 2 本 + カソードバー(a 負側)
        ("B.SilkS", 0.12, [(-sa, -sc, sa, -sc), (-sa, sc, sa, sc),
                           (-sa, -sc, -sa, sc)]),
        # B.Fab: ボディ矩形 + カソードバー
        ("B.Fab", 0.1, [(-fa, -fc, fa, -fc), (fa, -fc, fa, fc),
                        (fa, fc, -fa, fc), (-fa, fc, -fa, -fc),
                        (fbar, -fc, fbar, fc)]),
    ]
    for layer, lw, segs in layer_segs:
        for a1, c1, a2, c2 in segs:
            (x1, y1), (x2, y2) = pt(a1, c1), pt(a2, c2)
            items.append(
                f'(fp_line (start {x1} {y1}) (end {x2} {y2})'
                f' (stroke (width {lw}) (type solid))'
                f' (layer "{layer}") (tstamp {new_uuid()}))'
            )
    return items


def diode_pad_rects(cx, cy, vertical):
    """ダイオードパッドの外接矩形 (x1, y1, x2, y2) 2 個を返す(干渉チェック用)。"""
    pt = diode_xform(cx, cy, vertical)
    ha, hc = DIODE_PAD[0] / 2, DIODE_PAD[1] / 2
    rects = []
    for a in (DIODE_PAD_OFF, -DIODE_PAD_OFF):
        (x1, y1), (x2, y2) = pt(a - ha, -hc), pt(a + ha, hc)
        rects.append((min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))
    return rects


def diode_bbox(cx, cy, vertical):
    """シルク込みのダイオード外接矩形 1 個を返す(裏面図形との干渉チェック用)。"""
    pt = diode_xform(cx, cy, vertical)
    ha, hc = DIODE_SILK[0] + 0.06, DIODE_SILK[1] + 0.06
    (x1, y1), (x2, y2) = pt(-ha, -hc), pt(ha, hc)
    return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))


def bside_graphic_collides(s, rect, margin=0.2):
    """B.SilkS / B.Fab の図形(fp_line/fp_arc/fp_rect)が矩形 rect と交差・近接
    するかを線分サンプリングで判定する。当たった線分の端点ペアを返す。

    ホットスワップソケット本体の外形や double の裏面シルクを検出するための、
    パッド円近似判定(slot_collides)の補完。円弧は start-mid / mid-end の
    2 弦で近似する(スイッチ外形程度の曲率なら十分)。
    """
    x1, y1, x2, y2 = rect

    def near(px, py):
        dx = max(x1 - px, 0, px - x2)
        dy = max(y1 - py, 0, py - y2)
        return (dx ** 2 + dy ** 2) ** 0.5 < margin

    for kw in ("fp_line", "fp_arc", "fp_rect"):
        for a, b in find_blocks(s, kw):
            blk = s[a:b]
            if not re.search(r'\(layer "(?:B\.SilkS|B\.Fab)"\)', blk):
                continue
            pts = [(float(x), float(y)) for x, y in
                   re.findall(r"\((?:start|mid|end) (-?[\d.]+) (-?[\d.]+)\)", blk)]
            if kw == "fp_rect":
                (rx1, ry1), (rx2, ry2) = pts
                segs = [((rx1, ry1), (rx2, ry1)), ((rx2, ry1), (rx2, ry2)),
                        ((rx2, ry2), (rx1, ry2)), ((rx1, ry2), (rx1, ry1))]
            else:
                segs = list(zip(pts, pts[1:]))
            for (ax, ay), (bx, by) in segs:
                for i in range(17):
                    t = i / 16
                    if near(ax + (bx - ax) * t, ay + (by - ay) * t):
                        return ((ax, ay), (bx, by))
    return None


def diode_descr(vertical):
    """_Diode バリアントの descr 追記文(先頭に空白を含む)。"""
    return (" Series diode pads on back side: pad 3 = anode, pad 4 = cathode"
            " (cathode bar on B.SilkS, body outline on B.Fab, cathode points"
            f" {'up' if vertical else 'left'})."
            " Combined hand-soldering land for SOD-123 / SOD-323 / MiniMELF"
            " (LL-34, LL4148): 2.0x1.4mm pads at +/-1.6mm axial offset."
            " Connect pad 2 to pad 3 (or 1 to 4) externally for the usual"
            " row/column matrix.")


def existing_pads(s):
    """既存パッドの (x, y, 実効半径) を列挙(スタビ穴との干渉チェック用)。"""
    pads = []
    for a, b in find_blocks(s, "pad"):
        blk = s[a:b]
        at = re.search(r"\(at (-?[\d.]+) (-?[\d.]+)", blk)
        sizes = re.findall(r"\((?:size|drill) ([\d.]+)", blk)
        if at and sizes:
            pads.append((float(at.group(1)), float(at.group(2)),
                         max(float(v) for v in sizes) / 2))
    return pads


def check_stab_clearance(base_name, s, items):
    pads = existing_pads(s)
    for item in items:
        m = re.search(r"\(at (-?[\d.]+) (-?[\d.]+)\) \(size ([\d.]+)", item)
        hx, hy, hd = float(m.group(1)), float(m.group(2)), float(m.group(3))
        for px, py, pr in pads:
            dist = ((hx - px) ** 2 + (hy - py) ** 2) ** 0.5
            if dist < hd / 2 + pr + 0.2:
                print(f"  WARN {base_name}: スタビ穴({hx},{hy})と既存パッド"
                      f"({px},{py})の間隔が {dist - hd / 2 - pr:.2f}mm")


def slot_collides(s, rects, margin=0.2):
    """スロット矩形と既存パッドの干渉があれば (パッド座標, 間隔) を返す。"""
    pads = existing_pads(s)
    for x1, y1, x2, y2 in rects:
        for px, py, pr in pads:
            dx = max(x1 - px, 0, px - x2)
            dy = max(y1 - py, 0, py - y2)
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist < pr + margin:
                return (px, py), dist - pr
    return None


def check_slot_clearance(base_name, s, rects):
    pads = existing_pads(s)
    for x1, y1, x2, y2 in rects:
        for px, py, pr in pads:
            dx = max(x1 - px, 0, px - x2)
            dy = max(y1 - py, 0, py - y2)
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist < pr + 0.2:
                print(f"  WARN {base_name}: Choc スロット({x1},{y1})-({x2},{y2})と"
                      f"既存パッド({px},{py})の間隔が {dist - pr:.2f}mm")


def make_variant(base_text, base_name, suffix, size, stab, diode=None):
    """stab: None(スタビ要素なし) / "mx"(Cherry MX PCB 穴) /
    "choc"(Choc V1 スロット) / "chocv2"(Choc V2 スロット)
    diode: None / DIODE_PLACEMENT の (cx, cy, vertical)(裏面 SMD ダイオード)"""
    name = f"{base_name}_{suffix}"
    s = base_text

    # コートヤード置換(F/B は元ファイルにあった層を踏襲)
    spans = []
    layers = []
    for kw in ("fp_rect", "fp_poly"):
        for a, b in find_blocks(s, kw):
            blk = s[a:b]
            if "CrtYd" in blk:
                spans.append((a, b))
                layers.append(re.search(r'\(layer "([^"]+)"\)', blk).group(1))
    assert spans, base_name
    for a, b in sorted(spans, reverse=True):
        s = s[:a] + s[b:]
    s = re.sub(r"\n[ \t]*\n", "\n", s)

    inserts = courtyard_items(size, sorted(set(layers)))
    if stab == "mx":
        holes = stab_holes(size)
        check_stab_clearance(name, s, holes)
        inserts += holes + mx_plate_cut_items(size)
    elif stab == "choc":
        check_slot_clearance(name, s, choc_stab_slot_rects(size))
        inserts += choc_stab_items(size)
    elif stab == "chocv2":
        check_slot_clearance(name, s, choc_v2_stab_slot_rects(size))
        inserts += choc_v2_stab_items(size) + choc_v2_plate_items(size)
    if diode:
        inserts += diode_items(*diode)

    # ファイル末尾の閉じ括弧の直前に挿入
    tail = s.rstrip()
    assert tail.endswith(")")
    s = tail[:-1] + "".join(f"  {it}\n" for it in inserts) + ")\n"

    # 名前(footprint ヘッダ・Value)を置換
    s = s.replace(f'"{base_name}"', f'"{name}"')

    # descr 追記
    if size == "ISOEnter":
        cap = "Keycap: ISO Enter (courtyard)."
    elif size == "ISOEnterFlip":
        cap = ("Keycap: ISO Enter flipped upside down"
               " (courtyard only; switch orientation unchanged).")
    else:
        cap = f"Keycap: {suffix.split('_')[0]} (courtyard {size * U - SHRINK * 2:.2f}x19.00mm)."
    if stab == "mx":
        if size in ("ISOEnter", "ISOEnterFlip"):
            cap += (" Cherry MX PCB-mount stabilizer holes included"
                    " (vertical 2u, wire side at x=-8.255).")
        else:
            cap += " Cherry MX PCB-mount stabilizer holes included."
        cap += (" Stabilizer plate cut on User.5"
                " (fits plate-mount and PCB-mount MX stabilizers).")
    elif stab == "choc":
        cap += (" Kailh Choc 1350 stabilizer: PCB cutout slots (Edge.Cuts)"
                " and plate cuts on User.5. Plate required."
                " For Choc V1 switches only (wire interferes with Choc V2).")
    elif stab == "chocv2":
        cap += (" Kailh Choc V2 stabilizer (CPG1353G24D01): PCB cutout slots"
                " (Edge.Cuts) and plate cuts on User.5 (overlapping outlines;"
                " union in plate CAD). Plate required."
                " For Choc V2 / Gateron KS-33 only (not Choc V1).")
    elif (isinstance(size, str) and size.startswith("ISOEnter")) or (
            isinstance(size, float) and size >= STAB_MIN_SIZE):
        cap += " No stabilizer PCB features."
        if "MX" in base_name:
            cap += " Plate-mount MX stabilizers can be used."
        if "Choc_V1" in base_name and size in CHOC_STAB_X:
            cap += " For Kailh Choc 1350 (V1) stabilizers use the _ChocV1Stab variant."
        if (("Choc_V2" in base_name or "V1V2" in base_name
             or "Gateron" in base_name) and size in CHOC_V2_STAB_X):
            cap += " For Kailh Choc V2 stabilizers use the _ChocV2Stab variant."
    if diode:
        cap += diode_descr(diode[2])
    m = re.search(r'\(descr "((?:\\.|[^"\\])*)"\)', s)
    assert m, base_name
    s = s[:m.start()] + f'(descr "{m.group(1)} {cap}")' + s[m.end():]
    if diode:
        s = re.sub(r'\(tags "([^"]*)"\)',
                   lambda m: f'(tags "{m.group(1)}, diode")', s, count=1)

    # tstamp / uuid を新規発行
    s = re.sub(r"\(tstamp [0-9a-f-]{36}\)", lambda m: f"(tstamp {new_uuid()})", s)
    s = re.sub(r'\(uuid "[0-9a-f-]{36}"\)', lambda m: f'(uuid "{new_uuid()}")', s)

    return name, s


def make_diode_base(base_text, base_name, diode):
    """ベース(コートヤードはスイッチ単体のまま)に裏面ダイオードだけを足した
    `_Diode` ベースを返す。出力先は元ベースと同じディレクトリ(生成物)。"""
    name = f"{base_name}_Diode"
    tail = base_text.rstrip()
    assert tail.endswith(")"), base_name
    s = tail[:-1] + "".join(f"  {it}\n" for it in diode_items(*diode)) + ")\n"
    s = s.replace(f'"{base_name}"', f'"{name}"')
    m = re.search(r'\(descr "((?:\\.|[^"\\])*)"\)', s)
    assert m, base_name
    s = s[:m.start()] + f'(descr "{m.group(1)}{diode_descr(diode[2])}")' + s[m.end():]
    s = re.sub(r'\(tags "([^"]*)"\)',
               lambda m: f'(tags "{m.group(1)}, diode")', s, count=1)
    s = re.sub(r"\(tstamp [0-9a-f-]{36}\)", lambda m: f"(tstamp {new_uuid()})", s)
    s = re.sub(r'\(uuid "[0-9a-f-]{36}"\)', lambda m: f'(uuid "{new_uuid()}")', s)
    return name, s


def diode_fits(base_name, base_text, place):
    """裏面ダイオードが物理的に置けるか判定し、不可なら SKIP を print する。"""
    hit = slot_collides(base_text, diode_pad_rects(*place), margin=0.3)
    if hit:
        print(f"  SKIP {base_name}_Diode: ダイオードパッドが既存パッド"
              f"{hit[0]}と干渉({hit[1]:.2f}mm)")
        return False
    ghit = bside_graphic_collides(base_text, diode_bbox(*place))
    if ghit:
        print(f"  SKIP {base_name}_Diode: ダイオード領域が裏面図形"
              f"(線分 {ghit[0]}-{ghit[1]})と干渉")
        return False
    return True


def main():
    for d in OUT_DIRS.values():
        d.mkdir(exist_ok=True)
        for old in d.glob("*.kicad_mod"):
            old.unlink()
    # _Diode ベースは生成物なので先に削除して再生成する
    for d in (ROOT / "single.pretty", ROOT / "double.pretty"):
        for old in d.glob("*_Diode.kicad_mod"):
            old.unlink()

    bases = sorted([p for p in (*(ROOT / "single.pretty").glob("*.kicad_mod"),
                                *(ROOT / "double.pretty").glob("*.kicad_mod"))
                    # 二重ガード: _Diode は生成物予約名(手書きベースに使用禁止)
                    if not p.stem.endswith("_Diode")],
                   key=lambda p: p.name)
    assert bases, "ベースフットプリントが見つかりません"
    count = 0
    diode_bases = 0
    for base in bases:
        base_name = base.stem
        base_text = base.read_text()
        is_mx = "MX" in base_name
        is_choc_v1 = "Choc_V1" in base_name   # Choc_V1 と Choc_V1V2 Hybrid
        is_choc_v2 = "Choc_V2" in base_name or "V1V2" in base_name
        is_gateron = "Gateron" in base_name   # KS-33 は Choc V2 スタビ対応(Keebio)

        # 裏面 SMD ダイオード。物理干渉するベース(両面実装 double や
        # MX ソケットが上半分にある MX×Choc HotSwap ハイブリッド)はスキップ
        place = DIODE_PLACEMENT[family(base_name)]
        diode = place if diode_fits(base_name, base_text, place) else None
        if diode:
            name, text = make_diode_base(base_text, base_name, diode)
            (base.parent / f"{name}.kicad_mod").write_text(text)
            diode_bases += 1

        variants = []
        for w in REGULAR_SIZES:
            variants.append((f"{w:.2f}u", w, None))
            if is_mx and w >= STAB_MIN_SIZE and w in STAB_X_OFFSET:
                variants.append((f"{w:.2f}u_MXPCBStab", w, "mx"))
            if is_choc_v1 and w in CHOC_STAB_X:
                variants.append((f"{w:.2f}u_ChocV1Stab", w, "choc"))
            if (is_choc_v2 or is_gateron) and w in CHOC_V2_STAB_X:
                # ホットスワップ系はソケットパッドが V2 スロットと物理干渉する
                # ため生成しない(スロットがパッドを切り欠いてしまう)
                hit = slot_collides(base_text, choc_v2_stab_slot_rects(w))
                if hit:
                    print(f"  SKIP {base_name}_{w:.2f}u_ChocV2Stab: "
                          f"V2 スロットがパッド{hit[0]}と干渉({hit[1]:.2f}mm)")
                else:
                    variants.append((f"{w:.2f}u_ChocV2Stab", w, "chocv2"))
        variants.append(("ISOEnter", "ISOEnter", None))
        variants.append(("ISOEnterFlip", "ISOEnterFlip", None))
        if is_mx:
            variants.append(("ISOEnter_MXPCBStab", "ISOEnter", "mx"))
            variants.append(("ISOEnterFlip_MXPCBStab", "ISOEnterFlip", "mx"))

        for suffix, size, stab in variants:
            for dio in ((None, diode) if diode else (None,)):
                sfx = suffix + ("_Diode" if dio else "")
                name, text = make_variant(base_text, base_name, sfx, size, stab, dio)
                (out_dir(base_name) / f"{name}.kicad_mod").write_text(text)
                count += 1

    breakdown = ", ".join(f"{d.name}={len(list(d.glob('*.kicad_mod')))}"
                          for d in OUT_DIRS.values())
    print(f"生成完了: バリアント {count} ファイル ({breakdown})"
          f" + _Diode ベース {diode_bases} ファイル")


if __name__ == "__main__":
    sys.exit(main())

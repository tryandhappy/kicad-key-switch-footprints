#!/usr/bin/env python3
"""キーキャップサイズバリアント生成スクリプト

リポジトリ直下のベースフットプリント(キーキャップなし)から、
variants.pretty/ にキーキャップサイズ別のフットプリントを生成する。

- コートヤードをキーキャップ占有範囲に置換
  (外縁 = 公称キーキャップ範囲より各辺 0.025mm 控え。
   19.05mm ピッチで隣接キー同士が誤 DRC エラーにならないため)
- 2u 以上は Cherry MX PCB マウントスタビ穴付きの `_PCBStab` 版も生成
  (MX 系ベースのみ。MX のプレートマウントスタビは PCB 側に要素不要なので
   プレーン版がそのまま対応)
- Choc 系ベースには Kailh Choc 1350 スタビ用の `_ChocStab` 版も生成
  (2u / 6.25u のみ = Kailh が製造しているサイズ。PCB は丸穴ではなく
   角丸スロット 4 個の切り欠き(Edge.Cuts)+ プレート必須。
   プレートカット線は User.5)
- 寸法出典: kiswitch (https://github.com/kiswitch/kiswitch) KiSwitch/switch.py,
  keycap.py および marbastlib (https://github.com/ebastler/marbastlib,
  CERN-OHL-P v2) STAB_MX_*.kicad_mod / STAB_choc_*.kicad_mod

実行: python3 scripts/generate_variants.py
"""

import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "variants.pretty"

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
        if size == "ISOEnter":
            # kiswitch の ISO Enter 外形(上段1.5u×1u+下段1.25u×1u、右端揃え、
            # スイッチは下段1.25u列の中心・上下2uの中心)を各辺0.05mm(=控え+線幅/2)
            # 内側にオフセットした中心線
            pts = [
                (11.85625, 19.0), (11.85625, -19.0), (-16.61875, -19.0),
                (-16.61875, -0.05), (-11.85625, -0.05), (-11.85625, 19.0),
            ]
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
    if size == "ISOEnter":
        # 縦向き 2u スタビ(90°回転)。大穴(ワイヤー側)が左(x=-8.225)
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


def check_choc_slot_clearance(base_name, s, size):
    pads = existing_pads(s)
    for x1, y1, x2, y2 in choc_stab_slot_rects(size):
        for px, py, pr in pads:
            dx = max(x1 - px, 0, px - x2)
            dy = max(y1 - py, 0, py - y2)
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist < pr + 0.2:
                print(f"  WARN {base_name}: Choc スロット({x1},{y1})-({x2},{y2})と"
                      f"既存パッド({px},{py})の間隔が {dist - pr:.2f}mm")


def make_variant(base_text, base_name, suffix, size, stab):
    """stab: None(スタビ要素なし) / "mx"(Cherry MX PCB 穴) / "choc"(Choc スロット)"""
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
        inserts += holes
    elif stab == "choc":
        check_choc_slot_clearance(name, s, size)
        inserts += choc_stab_items(size)

    # ファイル末尾の閉じ括弧の直前に挿入
    tail = s.rstrip()
    assert tail.endswith(")")
    s = tail[:-1] + "".join(f"  {it}\n" for it in inserts) + ")\n"

    # 名前(footprint ヘッダ・Value)を置換
    s = s.replace(f'"{base_name}"', f'"{name}"')

    # descr 追記
    if size == "ISOEnter":
        cap = "Keycap: ISO Enter (courtyard)."
    else:
        cap = f"Keycap: {suffix.split('_')[0]} (courtyard {size * U - SHRINK * 2:.2f}x19.00mm)."
    if stab == "mx":
        if size == "ISOEnter":
            cap += (" Cherry MX PCB-mount stabilizer holes included"
                    " (vertical 2u, wire side at x=-8.255).")
        else:
            cap += " Cherry MX PCB-mount stabilizer holes included."
    elif stab == "choc":
        cap += (" Kailh Choc 1350 stabilizer: PCB cutout slots (Edge.Cuts)"
                " and plate cuts on User.5. Plate required.")
    elif size == "ISOEnter" or (isinstance(size, float) and size >= STAB_MIN_SIZE):
        cap += " No stabilizer PCB features."
        if "MX" in base_name:
            cap += " Plate-mount MX stabilizers can be used."
        if "Choc" in base_name and size in CHOC_STAB_X:
            cap += " For Kailh Choc 1350 stabilizers use the _ChocStab variant."
    m = re.search(r'\(descr "((?:\\.|[^"\\])*)"\)', s)
    assert m, base_name
    s = s[:m.start()] + f'(descr "{m.group(1)} {cap}")' + s[m.end():]

    # tstamp / uuid を新規発行
    s = re.sub(r"\(tstamp [0-9a-f-]{36}\)", lambda m: f"(tstamp {new_uuid()})", s)
    s = re.sub(r'\(uuid "[0-9a-f-]{36}"\)', lambda m: f'(uuid "{new_uuid()}")', s)

    return name, s


def main():
    OUT_DIR.mkdir(exist_ok=True)
    for old in OUT_DIR.glob("*.kicad_mod"):
        old.unlink()

    bases = sorted(ROOT.glob("*.kicad_mod"))
    assert bases, "ベースフットプリントが見つかりません"
    count = 0
    for base in bases:
        base_name = base.stem
        base_text = base.read_text()
        is_mx = "MX" in base_name
        is_choc = "Choc" in base_name

        variants = []
        for w in REGULAR_SIZES:
            variants.append((f"{w:.2f}u", w, None))
            if is_mx and w >= STAB_MIN_SIZE and w in STAB_X_OFFSET:
                variants.append((f"{w:.2f}u_PCBStab", w, "mx"))
            if is_choc and w in CHOC_STAB_X:
                variants.append((f"{w:.2f}u_ChocStab", w, "choc"))
        variants.append(("ISOEnter", "ISOEnter", None))
        if is_mx:
            variants.append(("ISOEnter_PCBStab", "ISOEnter", "mx"))

        for suffix, size, stab in variants:
            name, text = make_variant(base_text, base_name, suffix, size, stab)
            (OUT_DIR / f"{name}.kicad_mod").write_text(text)
            count += 1

    print(f"生成完了: {count} ファイル -> {OUT_DIR}")


if __name__ == "__main__":
    sys.exit(main())

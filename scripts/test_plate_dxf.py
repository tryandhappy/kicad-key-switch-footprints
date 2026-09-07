#!/usr/bin/env python3
"""テストプレート(150×150mm、1 枚)の DXF と SVG プレビューを生成する。

目的: 板材(FR4 / ステンレス / 塗装鋼 / アルミ)の見積比較と、開口寸法・四隅リリーフ・
低背スタビのプレートカットの実物確認を 1 枚で済ませる。
寸法はすべて `plate_cut_lines.py` と `generate_variants.py` の定数から取る(単一情報源)。

配置(19.05mm ピッチ 7×7、行は上から。KiCad 座標系 y 下向きで組んで DXF 出力時に y を反転):
  行 1: User.2 = 14.00 角 + 現行リリーフ(R0.6、中心 0.35 内側)×7
  行 2: User.3 = 13.95 角 + 現行リリーフ ×7
  行 3: User.4 = 13.80 角 + 現行リリーフ ×7
  行 4: 14.00 / 13.95 / 13.80 のリリーフ無し正方形、同 3 種の旧リリーフ(角中心 R1.0)、15.60 化粧カバー
  行 5: 2u Gateron LP 純正スタビ(User.2+User.5) / 2u Choc V2 スタビ(User.3+User.5) /
        2u Choc V1 スタビ(User.4+User.5) / 14.00 リリーフ
  行 6-7: 縦 2u Gateron LP / 縦 2u Choc V2 / 縦 2u Choc V1(いずれも 90°回転) / 14.00 リリーフ ×8
  四隅: 取付穴 Ø2.2(M2)、外形角 R2.0

出力: docs/test-plate-150x150.dxf(LWPOLYLINE、単位 mm、レイヤ CUT)、docs/test-plate-150x150.svg
      docs/test-plate-150x150-quote.dxf / .svg = 見積用(--quote)。Choc V2 スタビの 2 セルを 14.00 開口に
      置き換えて 1mm 未満の残り幅(0.6mm の帯、0.36mm の首)を無くし、円弧の分割を 1/4 円 8 分割に
      粗くして頂点数を減らしたもの。JLCCNC の自動見積が「マニュアル見積」に回るのを避ける
      (板金ルール: 穴は板厚の 1/2 以上かつ 1mm 以上。残り幅も同程度が目安)
依存: ezdxf, shapely(リポジトリの標準依存ではない。venv 等に pip install して実行)
実行: python3 scripts/test_plate_dxf.py        # 両方を生成
"""

import sys
from pathlib import Path

import ezdxf
from shapely import affinity
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_variants as gv          # noqa: E402
import plate_cut_lines as pcl           # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_DXF = ROOT / "docs" / "test-plate-150x150.dxf"
OUT_SVG = ROOT / "docs" / "test-plate-150x150.svg"

PLATE = 150.0
PLATE_R = 2.0
PITCH = gv.U
HOLE_D = 2.2
HOLE_OFF = 70.0
RES = 32   # 円弧の分割(1/4 円あたり)。--quote 版は 8(R0.6 で弦誤差 0.005mm)
QUOTE = False   # True で見積用(Choc V2 スタビ無し・粗い円弧)


def rrect(cx, cy, w, h, r):
    """角丸矩形(中心 cx,cy、幅 w、高さ h、角 R r)。"""
    if r <= 0:
        return box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    return box(cx - w / 2 + r, cy - h / 2 + r, cx + w / 2 - r, cy + h / 2 - r).buffer(r, resolution=RES)


def relief_square(side, r=pcl.RELIEF_R, inset=pcl.RELIEF_INSET):
    """正方形 + 四隅リリーフ円(中心を角から対角線上に inset 内側)。r=0 でリリーフ無し。"""
    h = side / 2
    parts = [box(-h, -h, h, h)]
    if r > 0:
        for sx in (1, -1):
            for sy in (1, -1):
                parts.append(Point(sx * (h - inset), sy * (h - inset)).buffer(r, resolution=RES))
    return unary_union(parts)


def gateron_lp_stab(size=2.0):
    """Gateron LP 純正スタビ(KS-57)のプレートカット + 14.00 開口(横向き 2u)。"""
    x = gv.GATERON_LP_STAB_X[size]
    parts = [relief_square(pcl.PLATE_CUTS["User.2"])]
    for m in (1, -1):
        for w, h, cy in (gv.GATERON_LP_PLATE_BODY, gv.GATERON_LP_PLATE_TAB):
            parts.append(rrect(m * x, cy, w, h, 0.5))
    wh, wy = gv.GATERON_LP_PLATE_WIRE
    parts.append(rrect(0, wy, 2 * x, wh, 0.5))
    return unary_union(parts)


def choc_v2_stab(size=2.0):
    """Kailh Choc V2 スタビのプレートカット + 13.95 開口(横向き 2u)。"""
    x = gv.CHOC_V2_STAB_X[size]
    parts = [relief_square(pcl.PLATE_CUTS["User.3"])]
    for m in (1, -1):
        for w, h, cy in gv.CHOC_V2_PLATE_PARTS:
            parts.append(rrect(m * x, cy, w, h, 0.5))
    wh, wy = gv.CHOC_V2_PLATE_WIRE
    parts.append(rrect(0, wy, 2 * x, wh, 0.5))
    return unary_union(parts)


def choc_v1_stab(size=2.0):
    """Kailh Choc 1350(V1)スタビのプレートカット + 13.80 開口(横向き 2u)。
    形状は generate_variants.CHOC_STAB_SEGMENTS の User.5 部分(marbastlib 準拠)を
    本体 6.3×6.85 + ワイヤー 3.6×4.65 の角丸矩形の union として再構成(R0.5 の凹フィレットは省略)。"""
    shift = gv.CHOC_STAB_X[size] - gv.CHOC_STAB_BASE_X
    parts = [relief_square(pcl.PLATE_CUTS["User.4"])]
    for m in (1, -1):
        # 本体: x 8.85..15.15, y -3.8..3.05 / ワイヤー: x 10.2..13.8, y -8.45..-3.8(2u、右側)
        bx1, bx2, by1, by2 = 8.85 + shift, 15.15 + shift, -3.8, 3.05
        wx1, wx2, wy1, wy2 = 10.2 + shift, 13.8 + shift, -8.45, -3.3
        parts.append(rrect(m * (bx1 + bx2) / 2, (by1 + by2) / 2, bx2 - bx1, by2 - by1, 0.5))
        parts.append(rrect(m * (wx1 + wx2) / 2, (wy1 + wy2) / 2, wx2 - wx1, wy2 - wy1, 0.5))
    return unary_union(parts)


def vertical(poly):
    """横向き基準の形状を _Vertical と同じ 90°回転((x,y)→(−y,x))にする。"""
    return affinity.rotate(poly, 90, origin=(0, 0))


def at(poly, cx, cy):
    return affinity.translate(poly, cx, cy)


def grid(c, r):
    return c * PITCH, r * PITCH


def build_cutouts():
    cuts = []
    cur = {"User.2": relief_square(pcl.PLATE_CUTS["User.2"]),
           "User.3": relief_square(pcl.PLATE_CUTS["User.3"]),
           "User.4": relief_square(pcl.PLATE_CUTS["User.4"])}
    # 行 1〜3: 現行リリーフの 3 寸法
    for r, layer in zip((-3, -2, -1), ("User.2", "User.3", "User.4")):
        for c in range(-3, 4):
            cuts.append(at(cur[layer], *grid(c, r)))
    # 行 4: リリーフ無し 3 種、旧 R1.0(角中心) 3 種、化粧カバー 15.60
    row4 = [relief_square(14.00, 0), relief_square(13.95, 0), relief_square(13.80, 0),
            relief_square(14.00, 1.0, 0.0), relief_square(13.95, 1.0, 0.0), relief_square(13.80, 1.0, 0.0),
            box(-7.8, -7.8, 7.8, 7.8)]
    for c, p in zip(range(-3, 4), row4):
        cuts.append(at(p, *grid(c, 0)))
    # 行 5: 横向き 2u スタビ 3 種 + 14.00
    cuts.append(at(gateron_lp_stab(), (grid(-3, 1)[0] + grid(-2, 1)[0]) / 2, grid(0, 1)[1]))
    if QUOTE:   # 見積用: 1mm 未満の残り幅を作る Choc V2 スタビは 14.00 開口 2 個に置き換え
        cuts.append(at(cur["User.2"], *grid(-1, 1)))
        cuts.append(at(cur["User.2"], *grid(0, 1)))
    else:
        cuts.append(at(choc_v2_stab(), (grid(-1, 1)[0] + grid(0, 1)[0]) / 2, grid(0, 1)[1]))
    cuts.append(at(choc_v1_stab(), (grid(1, 1)[0] + grid(2, 1)[0]) / 2, grid(0, 1)[1]))
    cuts.append(at(cur["User.2"], *grid(3, 1)))
    # 行 6-7: 縦向き 2u スタビ 3 種(行 6 と 7 の中間に中心)、残りは 14.00
    ymid = (grid(0, 2)[1] + grid(0, 3)[1]) / 2
    cuts.append(at(vertical(gateron_lp_stab()), grid(-3, 0)[0], ymid))
    if QUOTE:
        cuts.append(at(cur["User.2"], *grid(-2, 2)))
        cuts.append(at(cur["User.2"], *grid(-2, 3)))
    else:
        cuts.append(at(vertical(choc_v2_stab()), grid(-2, 0)[0], ymid))
    cuts.append(at(vertical(choc_v1_stab()), grid(-1, 0)[0], ymid))
    for c in range(0, 4):
        for r in (2, 3):
            cuts.append(at(cur["User.2"], *grid(c, r)))
    # 取付穴
    for sx in (1, -1):
        for sy in (1, -1):
            cuts.append(Point(sx * HOLE_OFF, sy * HOLE_OFF).buffer(HOLE_D / 2, resolution=RES))
    return cuts


def build_plate():
    outline = rrect(0, 0, PLATE, PLATE, PLATE_R)
    cuts = unary_union(build_cutouts())
    plate = outline.difference(cuts)
    assert isinstance(plate, Polygon), "プレートが分断された(切り抜き同士がつながった)"
    return plate.simplify(0.01 if QUOTE else 0.002, preserve_topology=True), cuts


def ring_xy(ring):
    """KiCad 座標(y 下向き)→ DXF/SVG 座標(y 上向き)に反転。"""
    pts = [(round(x, 4), round(-y, 4)) for x, y in ring.coords]
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    return pts


def write_dxf(plate, path):
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4   # mm
    doc.layers.add("CUT", color=7)
    msp = doc.modelspace()
    msp.add_lwpolyline(ring_xy(plate.exterior), close=True, dxfattribs={"layer": "CUT"})
    for hole in plate.interiors:
        msp.add_lwpolyline(ring_xy(hole), close=True, dxfattribs={"layer": "CUT"})
    doc.saveas(path)


def write_svg(plate, path):
    def d(ring):
        pts = ring_xy(ring)
        return "M" + " L".join(f"{x:.3f} {-y:.3f}" for x, y in pts) + " Z"   # SVG は y 下向きに戻す
    pd = " ".join([d(plate.exterior)] + [d(h) for h in plate.interiors])
    labels = [
        (-3, -3, "User.2 14.00 + R0.6 relief"), (-3, -2, "User.3 13.95 + R0.6 relief"),
        (-3, -1, "User.4 13.80 + R0.6 relief"),
        (-3, 0, "plain 14.00 / 13.95 / 13.80 | old R1.0 14.00 / 13.95 / 13.80 | cover 15.60"),
        (-3, 1, "2u: Gateron LP stab | " + ("14.00 x2" if QUOTE else "Choc V2 stab") + " | Choc V1 stab | 14.00"),
        (-3, 2, "2u vertical: Gateron LP | " + ("14.00 x2" if QUOTE else "Choc V2") + " | Choc V1 ; 14.00 x8"),
    ]
    txt = "".join(
        f'<text x="{grid(c, r)[0] - 9.0:.2f}" y="{grid(c, r)[1] - 8.6:.2f}" font-size="1.6" '
        f'fill="#1a4a9a" font-family="sans-serif">{s}</text>' for c, r, s in labels)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-80 -80 160 160" width="960" height="960">'
           f'<rect x="-80" y="-80" width="160" height="160" fill="#f7f7f7"/>'
           f'<path d="{pd}" fill="#c9c9c9" fill-rule="evenodd" stroke="#333" stroke-width="0.08"/>'
           f'{txt}'
           f'<text x="-78" y="78.5" font-size="1.8" fill="#333" font-family="sans-serif">'
           f'test plate 150x150 mm{" (quote version: no Choc V2 stab, coarse arcs)" if QUOTE else ""}, '
           f'19.05 pitch 7x7, mounting holes d2.2 at (+-70,+-70). '
           f'Generated by scripts/test_plate_dxf.py</text></svg>')
    path.write_text(svg)


def generate(quote):
    global QUOTE, RES
    QUOTE, RES = quote, (8 if quote else 32)
    dxf = OUT_DXF.with_name(OUT_DXF.stem + ("-quote" if quote else "") + ".dxf")
    svg = OUT_SVG.with_name(OUT_SVG.stem + ("-quote" if quote else "") + ".svg")
    plate, cuts = build_plate()
    write_dxf(plate, dxf)
    write_svg(plate, svg)
    nv = sum(len(r.coords) - 1 for r in (plate.exterior, *plate.interiors))
    print(f"{'見積用' if quote else '完全版'}: {dxf.relative_to(ROOT)} / {svg.relative_to(ROOT)}  "
          f"切り抜き {len(plate.interiors)} 個、頂点 {nv}、"
          f"切り抜き総周長 {sum(h.length for h in plate.interiors):.0f} mm、"
          f"残り面積 {plate.area:.0f} mm^2 ({plate.area / (PLATE * PLATE) * 100:.0f}%)")


def main():
    generate(False)
    generate(True)


if __name__ == "__main__":
    sys.exit(main())

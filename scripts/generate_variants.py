#!/usr/bin/env python3
"""キーキャップサイズバリアント生成スクリプト

リポジトリ直下のベースフットプリント(キーキャップなし)から、
variants.pretty/ にキーキャップサイズ別のフットプリントを生成する。

- コートヤードをキーキャップ占有範囲に置換
  (外縁 = 公称キーキャップ範囲より各辺 0.025mm 控え。
   19.05mm ピッチで隣接キー同士が誤 DRC エラーにならないため)
- 2u 以上は Cherry MX PCB マウントスタビ穴付きの `_PCBStab` 版も生成
  (MX 系ベースのみ。プレートマウントスタビは PCB 側に要素不要なので
   プレーン版がそのまま対応)
- 寸法出典: kiswitch (https://github.com/kiswitch/kiswitch) KiSwitch/switch.py,
  keycap.py

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

# Cherry MX PCB マウントスタビ (kiswitch StabilizerCherryMX 準拠)
STAB_MIN_SIZE = 2.0
STAB_X_OFFSET = {   # ステム位置 x = ±offset [mm]。無いサイズは PCB スタビ規格なし
    2.0: 11.938, 2.25: 11.938, 2.75: 11.938,
    3.0: 19.05,
    6.0: 47.625, 6.25: 50.0, 7.0: 57.15,
}
STAB_SMALL = (3.048, -6.985)   # (穴径, y) 上側の小穴
STAB_LARGE = (3.9878, 8.225)   # (穴径, y) 下側の大穴(ワイヤー側)


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


def make_variant(base_text, base_name, suffix, size, with_stab):
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
    if with_stab:
        holes = stab_holes(size)
        check_stab_clearance(name, s, holes)
        inserts += holes

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
        cap = f"Keycap: {suffix} (courtyard {size * U - SHRINK * 2:.2f}x19.00mm)."
    if with_stab:
        if size == "ISOEnter":
            cap += (" Cherry MX PCB-mount stabilizer holes included"
                    " (vertical 2u, wire side at x=-8.225).")
        else:
            cap += " Cherry MX PCB-mount stabilizer holes included."
    elif size == "ISOEnter" or (isinstance(size, float) and size >= STAB_MIN_SIZE):
        cap += " For plate-mount stabilizers (no PCB holes needed)."
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

        variants = []
        for w in REGULAR_SIZES:
            variants.append((f"{w:.2f}u", w, False))
            if is_mx and w >= STAB_MIN_SIZE and w in STAB_X_OFFSET:
                variants.append((f"{w:.2f}u_PCBStab", w, True))
        variants.append(("ISOEnter", "ISOEnter", False))
        if is_mx:
            variants.append(("ISOEnter_PCBStab", "ISOEnter", True))

        for suffix, size, with_stab in variants:
            name, text = make_variant(base_text, base_name, suffix, size, with_stab)
            (OUT_DIR / f"{name}.kicad_mod").write_text(text)
            count += 1

    print(f"生成完了: {count} ファイル -> {OUT_DIR}")


if __name__ == "__main__":
    sys.exit(main())

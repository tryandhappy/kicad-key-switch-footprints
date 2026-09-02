#!/usr/bin/env python3
"""スイッチ保持用プレートカット線(User.2 / User.3 / User.4)を全ベースファイルに書き直す。

形状 = 正方形開口 + 四隅のコーナーリリーフ(dogbone。角を中心とした半径 RELIEF_R の円を
対角外側へはみ出させる)。FR4 などルーター加工のプレートでは内角にビット半径が残り、
角がほぼピン角のスイッチハウジングが座らないため、角に逃げを設ける。
直線 4 本 + 270° 円弧 4 本の一体外形として描く(そのまま DXF 書き出しできる)。

対象: single.pretty / double.pretty の手書きベース(_Diode は生成物なので対象外。
変更後は `python3 scripts/generate_variants.py` で _Diode と variants を再生成する)。
User.1(15.60 化粧カバー)はスイッチを掴まないのでリリーフ不要、そのまま fp_rect。

冪等: 対象レイヤの既存図形(fp_rect / fp_line / fp_arc)を削除して再生成するので、
RELIEF_R や開口寸法を変えて再実行すればよい。RELIEF_R = 0 なら fp_rect の正方形に戻る。
新旧 2 書式(tstamp / uuid)の両方に対応。
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_variants import find_blocks, new_uuid  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LINE_W = 0.05

# レイヤ → 開口の一辺 [mm]
PLATE_CUTS = {"User.2": 14.00, "User.3": 13.95, "User.4": 13.80}
# コーナーリリーフ半径 [mm](円の中心 = 開口の角)。0 でリリーフなし
RELIEF_R = 2.00


def relief_square_items(side, layer, new_format):
    """正方形 + 四隅リリーフの外形(線 4 + 円弧 4)を .kicad_mod の図形文字列で返す。"""
    h = side / 2
    r = RELIEF_R
    ind = "\t" if new_format else "  "
    ident = (lambda: f'(uuid "{new_uuid()}")') if new_format else (lambda: f"(tstamp {new_uuid()})")

    def fmt(v):
        return f"{round(v, 6):.6f}".rstrip("0").rstrip(".") if abs(v) >= 1e-9 else "0"

    if r <= 0:
        if new_format:
            return [f"(fp_rect\n{ind}\t(start {fmt(-h)} {fmt(-h)})\n{ind}\t(end {fmt(h)} {fmt(h)})\n"
                    f"{ind}\t(stroke (width {LINE_W}) (type solid))\n{ind}\t(fill no)\n"
                    f"{ind}\t(layer \"{layer}\")\n{ind}\t{ident()}\n{ind})"]
        return [f"(fp_rect (start {fmt(-h)} {fmt(-h)}) (end {fmt(h)} {fmt(h)})\n"
                f"{ind}  (stroke (width {LINE_W}) (type solid)) (fill none) (layer \"{layer}\") {ident()})"]

    items = []
    # 直線 4 本: 角から r だけ短くする
    for (x1, y1, x2, y2) in [(-h + r, -h, h - r, -h), (h, -h + r, h, h - r),
                             (h - r, h, -h + r, h), (-h, h - r, -h, -h + r)]:
        if new_format:
            items.append(f"(fp_line\n{ind}\t(start {fmt(x1)} {fmt(y1)})\n{ind}\t(end {fmt(x2)} {fmt(y2)})\n"
                         f"{ind}\t(stroke (width {LINE_W}) (type solid))\n"
                         f"{ind}\t(layer \"{layer}\")\n{ind}\t{ident()}\n{ind})")
        else:
            items.append(f"(fp_line (start {fmt(x1)} {fmt(y1)}) (end {fmt(x2)} {fmt(y2)})\n"
                         f"{ind}  (stroke (width {LINE_W}) (type solid)) (layer \"{layer}\") {ident()})")
    # 円弧 4 本: 角 (sx*h, sy*h) を中心、開口の外側 270°。
    # 中点は角から対角外側へ r/√2 ずつ。start→mid→end は KiCad 座標系(y 下向き)で時計回り
    d = r / 2 ** 0.5
    for sx, sy in [(1, -1), (1, 1), (-1, 1), (-1, -1)]:
        cx, cy = sx * h, sy * h
        # 角から見て、開口辺の続きにある 2 点: 辺の延長上ではなく円周上の (cx - sx*r, cy) と (cx, cy - sy*r)
        p_a = (cx, cy - sy * r)   # 縦辺側の点
        p_b = (cx - sx * r, cy)   # 横辺側の点
        mid = (cx + sx * d, cy + sy * d)
        # 時計回り(KiCad 画面上)になるように start/end を選ぶ
        if sx * sy > 0:
            start, end = p_a, p_b
        else:
            start, end = p_b, p_a
        if new_format:
            items.append(f"(fp_arc\n{ind}\t(start {fmt(start[0])} {fmt(start[1])})\n"
                         f"{ind}\t(mid {fmt(mid[0])} {fmt(mid[1])})\n{ind}\t(end {fmt(end[0])} {fmt(end[1])})\n"
                         f"{ind}\t(stroke (width {LINE_W}) (type solid))\n"
                         f"{ind}\t(layer \"{layer}\")\n{ind}\t{ident()}\n{ind})")
        else:
            items.append(f"(fp_arc (start {fmt(start[0])} {fmt(start[1])}) (mid {fmt(mid[0])} {fmt(mid[1])})"
                         f" (end {fmt(end[0])} {fmt(end[1])})\n"
                         f"{ind}  (stroke (width {LINE_W}) (type solid)) (layer \"{layer}\") {ident()})")
    return items


def rewrite(path):
    s = path.read_text()
    new_format = '(uuid "' in s
    ind = "\t" if new_format else "  "

    # 対象レイヤの既存図形を削除(レイヤ出現順を記録)
    spans = []
    for kw in ("fp_rect", "fp_line", "fp_arc"):
        for a, b in find_blocks(s, kw):
            m = re.search(r'\(layer "(User\.[234])"\)', s[a:b])
            if m:
                spans.append((a, b, m.group(1)))
    layers_present = []
    for _, _, layer in sorted(spans):
        if layer not in layers_present:
            layers_present.append(layer)
    for a, b, _ in sorted(spans, reverse=True):
        # 行頭のインデントごと削除
        la = s.rfind("\n", 0, a) + 1
        if s[la:a].strip() == "":
            a = la
        lb = s.find("\n", b)
        if lb != -1 and s[b:lb].strip() == "":
            b = lb + 1
        s = s[:a] + s[b:]
    if not layers_present:
        return False

    inserts = []
    for layer in layers_present:
        inserts += relief_square_items(PLATE_CUTS[layer], layer, new_format)
    tail = s.rstrip()
    assert tail.endswith(")"), path
    s = tail[:-1] + "".join(f"{ind}{it}\n" for it in inserts) + ")\n"

    # descr のレイヤ説明を更新
    def repl(m):
        layer, side = m.group(1), m.group(2)
        note = f" with R{RELIEF_R:.2f} corner relief" if RELIEF_R > 0 else ""
        return f"{layer}={side}mm square{note}"
    s = re.sub(r"(User\.[234])=(\d+\.\d+)mm square(?: with R[\d.]+ corner relief)?", repl, s)
    path.write_text(s)
    return True


def main():
    n = 0
    for d in ("single.pretty", "double.pretty"):
        for p in sorted((ROOT / d).glob("*.kicad_mod")):
            if p.stem.endswith("_Diode"):
                continue
            if rewrite(p):
                n += 1
    print(f"プレートカット線を書き直しました: {n} ファイル (R={RELIEF_R})")


if __name__ == "__main__":
    sys.exit(main())

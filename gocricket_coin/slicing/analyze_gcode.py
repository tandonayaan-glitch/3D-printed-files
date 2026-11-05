"""
Layer-by-layer printability check on the ACTUAL sliced G-code.
For every layer, rasterise the extruded paths (0.1 mm pixels) and compare with the two layers below
(two, because the design deliberately leaves a one-layer 0.2 mm air gap under every coin and pad).
Material that sits more than TOL from anything below is 'unsupported' (an overhang / bridge); its connected
regions are reported with their bridging span (largest inscribed diameter).
usage: analyze_gcode.py file.gcode [--bbox x0 y0 x1 y1] [--csv out.csv]
"""
import sys, re, math, numpy as np, cv2
from PIL import Image, ImageDraw
from scipy import ndimage

PX = 5           # pixels per mm
LINE_W = 0.45
TOL = 0.40       # mm of allowed overhang per layer (~56 deg at 0.2 mm layers)

def parse(path):
    layers = {}; z = 0.0; x = y = 0.0; absxy = True; cur = None; zs = []
    pat = re.compile(r'([XYZE])(-?\d*\.?\d+)')
    with open(path) as f:
        for ln in f:
            if ln.startswith(';Z:'):
                z = float(ln[3:]); cur = []; layers[z] = cur; zs.append(z); continue
            if ln[0] != 'G': continue
            if ln.startswith('G1 ') or ln.startswith('G0 '):
                d = dict((k, float(v)) for k, v in pat.findall(ln))
                nx = d.get('X', x); ny = d.get('Y', y)
                if 'E' in d and d['E'] > 0 and (nx != x or ny != y) and cur is not None and ln.startswith('G1'):
                    cur.append((x, y, nx, ny))
                x, y = nx, ny
    return zs, layers

def raster(segs, bbox):
    x0, y0, x1, y1 = bbox; W = int((x1 - x0) * PX) + 1; H = int((y1 - y0) * PX) + 1
    im = np.zeros((H, W), np.uint8); w = max(1, int(round(LINE_W * PX)))
    if segs:
        a = np.array(segs); p0 = np.round((a[:, :2] - [x0, y0]) * PX).astype(np.int32); p1 = np.round((a[:, 2:] - [x0, y0]) * PX).astype(np.int32)
        lines = np.stack([p0, p1], axis=1)
        cv2.polylines(im, list(lines), False, 1, thickness=w)
    return im.astype(bool)

def main():
    path = sys.argv[1]; bbox = None; csv = None
    if '--bbox' in sys.argv: i = sys.argv.index('--bbox'); bbox = tuple(float(v) for v in sys.argv[i + 1:i + 5])
    if '--csv' in sys.argv: csv = sys.argv[sys.argv.index('--csv') + 1]
    zs, layers = parse(path)
    allseg = [s for z in zs for s in layers[z]]
    if bbox is None:
        a = np.array(allseg); bbox = (a[:, [0, 2]].min() - 2, a[:, [1, 3]].min() - 2, a[:, [0, 2]].max() + 2, a[:, [1, 3]].max() + 2)
    print(f"layers {len(zs)}  top z {zs[-1]:.2f}  bbox {tuple(round(v,1) for v in bbox)}")
    st = ndimage.generate_binary_structure(2, 1)
    r = int(round(TOL * PX)); kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*r+1, 2*r+1))
    prev1 = prev2 = None; worst = []; rows = []
    for li, z in enumerate(zs):
        m = raster(layers[z], bbox)
        if prev1 is None:
            sup = np.zeros_like(m); 
        else:
            below = prev1 | (prev2 if prev2 is not None else False)
            sup = cv2.dilate(below.astype(np.uint8), kern).astype(bool)
        uns = m & ~sup if li > 0 else np.zeros_like(m)
        area = uns.sum() / PX / PX
        span = 0.0; ncomp = 0; big = []; longest = 0.0
        if area > 0.3:
            lab, n = ndimage.label(cv2.dilate(uns.astype(np.uint8), np.ones((5,5),np.uint8)).astype(bool))
            for c in range(1, n + 1):
                comp = (lab == c) & cv2.dilate(m.astype(np.uint8), np.ones((5,5),np.uint8)).astype(bool)
                a_c = comp.sum() / PX / PX
                if a_c < 0.4: continue
                # bridge span: largest inscribed circle of the surrounding unsupported zone (material + void between anchors)
                dist = ndimage.distance_transform_edt(comp)
                sp = 2 * dist.max() / PX
                ys_, xs_ = np.nonzero(comp); lenmm = max(xs_.max()-xs_.min(), ys_.max()-ys_.min()) / PX
                longest = max(longest, lenmm)
                ncomp += 1; span = max(span, sp)
                if sp > 6: 
                    ys, xs = np.nonzero(comp); big.append((round(sp, 1), round(a_c, 1), round(bbox[0] + xs.mean() / PX, 1), round(bbox[1] + ys.mean() / PX, 1)))
        rows.append((li, z, area, ncomp, span, longest))
        if big: worst.append((z, big))
        prev2, prev1 = prev1, m
    spans = np.array([r[4] for r in rows])
    print("max single-region unsupported width (mm): %.1f" % spans.max())
    print("layers with an unsupported region wider than 6 mm: %d, wider than 10 mm: %d, wider than 14 mm: %d" % ((spans > 6).sum(), (spans > 10).sum(), (spans > 14).sum()))
    lens = np.array([r[5] for r in rows]); print("longest single unsupported region (any direction): %.1f mm; layers with one > 12 mm: %d, > 16 mm: %d, > 20 mm: %d" % (lens.max(), (lens > 12).sum(), (lens > 16).sum(), (lens > 20).sum()))
    for z, big in worst[:3]: print("  z=%.1f" % z, [tuple(float(v) for v in b) for b in big[:4]])
    if csv:
        with open(csv, 'w') as f:
            f.write("layer,z,unsupported_mm2,regions,max_span_mm,longest_mm\n")
            for r_ in rows: f.write("%d,%.2f,%.2f,%d,%.1f,%.1f\n" % r_)
    return rows
if __name__ == "__main__": main()

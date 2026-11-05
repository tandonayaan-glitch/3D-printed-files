"""
Multi-floor coin tower generator (editable CAD source, Bambu Lab A1: 256x256x256, 0.4 mm nozzle, 0.2 mm layers).

Each coin (32 x 3.6 mm, TAILS face down) rests on a flat 1.8 mm "pad" with a 0.2 mm air gap (one layer), exactly
like a slicer support interface.  The pad is the floor of that level and is also the ceiling-support of the coin below
it (it is printed over the coin's top with a 0.2 mm gap).  Pads are tied to a honeycomb of thin ribs and 7 mm pillars
by three 1.2 x 0.8 mm break-away webs.  Small studs on every pad support the wide empty field of the TAILS face.

All Z values are multiples of 0.2 mm so every gap lands exactly on a layer boundary.

usage:  python3 coin_tower.py COLS ROWS LEVELS [out_prefix]
"""
import sys, json, math, numpy as np, trimesh, manifold3d as mf
from shapely.geometry import Point, Polygon, box, LineString
from shapely.ops import unary_union
from shapely import affinity
from PIL import Image, ImageDraw
from scipy import ndimage

# ---------------- parameters (mm) ----------------
D = 36.0            # coin centre pitch (4 mm between coin edges)
RC = 16.0           # coin radius
TC = 3.6            # coin thickness
GAP = 0.2           # air gap pad<->coin (1 layer)
TP = 1.8            # pad / floor thickness (9 layers)
BASE = 2.0          # base plate thickness (10 layers)
PITCH = TP + GAP + TC + GAP   # 5.8 mm per level
R_PAD = 15.5        # pad radius (sits fully under the coin)
R_PILLAR = 3.5
RIB_W = 3.0
WEB_W, WEB_Z0, WEB_Z1 = 1.2, 0.6, 1.4      # break-away webs: width, z-range inside the pad thickness
STUD_D, STUD_H, STUD_PITCH, STUD_CLEAR = 1.8, 0.6, 3.2, 1.8
CAP = 1.8           # top cap ribs thickness
HEX_R = D / math.sqrt(3)       # coin centre -> interstice (pillar) distance
ROT = 90                       # lattice rotation (deg)

def extrude(poly, z0, z1):
    geoms = [poly] if poly.geom_type == "Polygon" else list(poly.geoms)
    parts = []
    for p in geoms:
        if p.is_empty or p.area < 1e-4: continue
        cs = mf.CrossSection([np.array(p.exterior.coords)[:-1]] + [np.array(h.coords)[:-1] for h in p.interiors], mf.FillRule.EvenOdd)
        parts.append(mf.Manifold.extrude(cs, z1 - z0).translate([0, 0, z0]))
    return mf.Manifold.batch_boolean(parts, mf.OpType.Add) if parts else None

def layout(cols, rows):
    cs = [(j * D + (i % 2) * D / 2, i * D * math.sqrt(3) / 2) for i in range(rows) for j in range(cols)]
    cx = np.mean([c[0] for c in cs]); cy = np.mean([c[1] for c in cs])
    return [(-(y - cy), x - cx) for x, y in cs]     # rotated 90 deg: long side along Y

def key(p): return (round(p[0], 2), round(p[1], 2))

def ring_pts(c):
    x, y = c
    return [key((x + HEX_R * math.cos(math.radians(30 + ROT + 60 * k)), y + HEX_R * math.sin(math.radians(30 + ROT + 60 * k)))) for k in range(6)]

def network(coins):
    """Choose, for every coin, the break-away web directions (multiples of 60 deg): all directions that face a neighbour
    (rib shared with it) plus extra outer ones until there are >=3 webs that are not all on one line.
    Returns web directions per coin, honeycomb edges (ribs) and pillars (their end points)."""
    cs = {key(c): c for c in coins}
    dirs = {}
    for c in coins:
        S = [j * 60 + ROT for j in range(6) if key((c[0] + D * math.cos(math.radians(j * 60 + ROT)), c[1] + D * math.sin(math.radians(j * 60 + ROT)))) in cs]
        while len(S) < 3 or len({a % 180 for a in S}) < 2:
            cand = [(a + ROT) % 360 for a in range(0, 360, 60) if (a + ROT) % 360 not in [x % 360 for x in S]]
            best = max(cand, key=lambda a: min(min((a - s_) % 360, (s_ - a) % 360) for s_ in S) if S else 0)
            S.append(best)
        dirs[key(c)] = sorted(a % 360 for a in S)
    edges, pillars = {}, {}
    for c in coins:
        ring = ring_pts(c)
        for ang in dirs[key(c)]:
            j = ((ang - ROT) % 360) // 60
            a_, b_ = ring[(j - 1) % 6], ring[j % 6]
            edges[tuple(sorted((a_, b_)))] = (a_, b_); pillars[a_] = 1; pillars[b_] = 1
    # tie everything into ONE connected frame: add honeycomb edges between existing pillars, then bridge any remaining islands
    allring = [(ring_pts(c)[k], ring_pts(c)[(k + 1) % 6]) for c in coins for k in range(6)]
    for a_, b_ in allring:
        if a_ in pillars and b_ in pillars: edges[tuple(sorted((a_, b_)))] = (a_, b_)
    def comps():
        par = {p: p for p in pillars}
        def f(p):
            while par[p] != p: par[p] = par[par[p]]; p = par[p]
            return p
        for a_, b_ in edges.values(): par[f(a_)] = f(b_)
        return par, f
    while True:
        par, f = comps()
        roots = {f(p) for p in pillars}
        if len(roots) == 1: break
        cand = [(a_, b_) for a_, b_ in allring if f(a_) != f(b_) if a_ in pillars or b_ in pillars]
        a_, b_ = cand[0]; edges[tuple(sorted((a_, b_)))] = (a_, b_); pillars[a_] = 1; pillars[b_] = 1
    return dirs, edges, pillars

def build(cols, rows, levels, out="tower"):
    coins = layout(cols, rows)
    dirs, edges, pillars = network(coins)
    pill_poly = unary_union([Point(p).buffer(R_PILLAR, 24) for p in pillars])
    rib_poly = unary_union([LineString([a, b]).buffer(RIB_W / 2, cap_style=2) for a, b in edges.values()])
    rib_net = unary_union([rib_poly, pill_poly])        # one connected honeycomb diaphragm
    # ---- low-res joined coin
    c = trimesh.load("gocricket_coin_lowres.stl"); coin_mf = mf.Manifold(mf.Mesh(np.array(c.vertices, np.float32), np.array(c.faces, np.uint32)))
    # ---- stud pattern from the TAILS (bottom) relief footprint of the coin
    tails_xy = footprint_bottom()
    studs = stud_polys(tails_xy)
    n = levels
    parts = []
    # base plate (acts as the pad of level 0)
    base_poly = unary_union([rib_net.buffer(0.8), unary_union([Point(c_).buffer(17.0, 64) for c_ in coins])])
    parts.append(extrude(base_poly, 0, BASE))
    def pad_top_features(cxy, ztop):
        st = affinity.translate(studs, cxy[0], cxy[1])
        return extrude(st, ztop - 0.01, ztop + STUD_H)
    for k in range(n):
        zcb = BASE + GAP + k * PITCH               # coin bottom
        zpad_top = zcb - GAP
        for cxy in coins:
            parts.append(coin_mf.translate([cxy[0], cxy[1], zcb]))
            s = pad_top_features(cxy, zpad_top)
            if s is not None: parts.append(s)
        if k >= 1:                                  # floor (pad + ribs + webs) below coin level k
            zb = zpad_top - TP
            parts.append(extrude(rib_net, zb, zb + TP))
            for cxy in coins:
                parts.append(extrude(Point(cxy).buffer(R_PAD, 96), zb, zb + TP))
                for ang in dirs[key(cxy)]:
                    w = box(R_PAD - 0.6, -WEB_W / 2, R_PAD + 1.9, WEB_W / 2)
                    w = affinity.translate(affinity.rotate(w, ang, origin=(0, 0)), cxy[0], cxy[1])
                    parts.append(extrude(w, zb + WEB_Z0, zb + WEB_Z1))
    ztop_coin = BASE + GAP + (n - 1) * PITCH + TC
    zcap = ztop_coin + GAP
    parts.append(extrude(rib_net, zcap, zcap + CAP))              # top cap ties all pillars together
    pillar_full = extrude(pill_poly.buffer(-0.03, 24), 0.0, zcap + CAP)
    parts.append(pillar_full)
    solid = mf.Manifold.batch_boolean([p for p in parts if p is not None], mf.OpType.Add)
    mesh = solid.to_mesh()
    t = trimesh.Trimesh(mesh.vert_properties[:, :3], mesh.tri_verts)
    t.apply_translation([128, 128, 0])
    t.export(out + ".stl")
    info = dict(cols=cols, rows=rows, levels=n, coins_per_level=len(coins), coins=len(coins) * n,
                height=round(float(t.bounds[1][2]), 2), width_x=round(float(t.bounds[1][0] - t.bounds[0][0]), 1),
                width_y=round(float(t.bounds[1][1] - t.bounds[0][1]), 1), faces=len(t.faces), volume_cm3=round(t.volume / 1000, 1),
                watertight=bool(t.is_watertight), pillars=len(pillars), ribs=len(edges), pitch=PITCH)
    json.dump(info, open(out + "_info.json", "w"), indent=1)
    return t, info, coins

# ---------- coin footprint helpers ----------
_cache = {}
def footprint_bottom():
    """2D footprint (shapely) of the raised relief on the coin's bottom (z=0..0.6) in coin-centred coordinates."""
    if "b" in _cache: return _cache["b"]
    c = trimesh.load("gocricket_coin_lowres.stl")
    sl = c.section(plane_origin=[0, 0, 0.3], plane_normal=[0, 0, 1])
    pls, _ = sl.to_planar(to_2D=np.eye(4))
    polys = pls.polygons_full
    g = unary_union([Polygon(p.exterior.coords, [h.coords for h in p.interiors]) for p in polys])
    _cache["b"] = g
    return g

def stud_polys(relief):
    S = 20; N = 36 * S
    im = Image.new("L", (N, N), 0); d = ImageDraw.Draw(im)
    for p in sorted(([relief] if relief.geom_type == "Polygon" else list(relief.geoms)), key=lambda q: -q.area):
        d.polygon([((x + 18) * S, (y + 18) * S) for x, y in p.exterior.coords], fill=1)
        for h in p.interiors: d.polygon([((x + 18) * S, (y + 18) * S) for x, y in h.coords], fill=0)
    R = np.array(im) > 0
    dist = ndimage.distance_transform_edt(~R) / S
    pts = []
    g = np.arange(-14, 14.01, STUD_PITCH)
    for yi, y in enumerate(g):
        for x in g + (STUD_PITCH / 2 if yi % 2 else 0):
            if math.hypot(x, y) > R_PAD - 1.5: continue
            ix, iy = int((x + 18) * S), int((y + 18) * S)
            if dist[iy, ix] >= STUD_CLEAR: pts.append((x, y))
    return unary_union([Point(p).buffer(STUD_D / 2, 12) for p in pts]) if pts else Polygon()

if __name__ == "__main__":
    cols, rows, levels = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    out = sys.argv[4] if len(sys.argv) > 4 else f"tower_{cols}x{rows}x{levels}"
    t, info, _ = build(cols, rows, levels, out)
    print(json.dumps(info))

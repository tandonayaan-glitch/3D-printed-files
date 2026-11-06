"""
Coin RACK generator (editable CAD source) - Bambu Lab A1, 0.4 mm nozzle, 0.2 mm layers.

Vertical pitch is 6.6 mm per coin level:   floor 1.6 | 0.2 print gap | coin 3.6 | 1.2 free headroom   (= 6.6)
i.e. 3.0 mm between consecutive coins, of which 1.6 mm is the thin floor.  Every Z is a multiple of 0.2 mm.

Plan view: towers side by side along X.  Each tower = two side beams (truss walls running along Y, shared between
neighbouring towers) with 1.6 mm floors spanning between them, and TWO coins per floor (front coin and rear coin).
The ends of the tower (+Y / -Y) are open, so every coin slides out of its own floor, in any order.
A truss X-brace in the 6 mm lane between the two coins stiffens the rack across its width.
Studs on each floor support the wide empty TAILS field of the coin above it.

usage: python3 coin_rack.py NX LEVELS [out_prefix]
"""
import sys, json, math, numpy as np, trimesh, manifold3d as mf
from shapely.geometry import box, Polygon, LineString, Point
from shapely.ops import unary_union
from shapely import affinity
import coin_tower as ct                      # reuse extrude(), stud placement, coin footprint

TF, G, TC, HEAD = 1.6, 0.2, 3.6, 1.2
PITCH = round(TF + G + TC + HEAD, 3)         # 6.6
BASE = TF
WALL = 2.4                                   # side-beam thickness
W_IN = 33.6                                  # clear width between beams (coin 32.0 + 0.8 each side)
TPITCH = W_IN + WALL                         # tower pitch along X = 36.0
COIN_Y = 19.0                                # coin centres at y = +-19 (6 mm lane between coins)
HALF_Y = 36.5                                # beam half length
PLATE_HY = 36.2                              # floor half length (slightly shorter than the beams)
POST_W = 5.0
POST_Y = [-34.0, -17.0, 0.0, 17.0, 34.0]
BAND = TF                                    # beam band at every floor
DIAG_W = 3.0
WALL_BLOCK = 3 * PITCH                       # wall X-braces span 3 floors (45-50 deg diagonals)
LANE_BLOCK = 5 * PITCH                       # lane X-braces span 5 floors
EPS = 0.01

def xmap_yz(x0):                             # polygon (y,z) extruded along +x from x0
    return [[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0]]
def xmap_xz(y1):                             # polygon (x,z) extruded along -y from y1
    return [[1, 0, 0, 0], [0, 0, -1, y1], [0, 1, 0, 0]]

def prism(poly, t, mat):
    m = ct.extrude(poly, 0.0, t)
    return m.transform(np.array(mat, float)) if m is not None else None

def diag_poly(p0, p1, clip):
    return LineString([p0, p1]).buffer(DIAG_W / 2, cap_style=2).intersection(clip)

def geometry(NX, n):
    H = PITCH * n + TF                                     # top of cap floor
    xw = [(i - NX / 2) * TPITCH for i in range(NX + 1)]    # beam centre lines
    xc = [(xw[i] + xw[i + 1]) / 2 for i in range(NX)]      # tower centres
    coins = [(x, y) for x in xc for y in (-COIN_Y, COIN_Y)]
    # --- beam (truss wall) outline in (y,z)
    wall = []
    for yp in POST_Y: wall.append(box(yp - POST_W / 2, 0, yp + POST_W / 2, H))
    for k in range(n + 1): wall.append(box(-HALF_Y, max(0.0, PITCH * k - EPS), HALF_Y, PITCH * k + BAND + EPS))
    z = 0.0
    while z + WALL_BLOCK <= H - 1e-6:
        for a, b in zip(POST_Y[:-1], POST_Y[1:]):
            clip = box(a, z, b, z + WALL_BLOCK)
            wall.append(diag_poly((a, z), (b, z + WALL_BLOCK), clip)); wall.append(diag_poly((a, z + WALL_BLOCK), (b, z), clip))
        z += WALL_BLOCK
    wall = unary_union(wall)
    parts = []
    for x in xw: parts.append(prism(wall, WALL, xmap_yz(x - WALL / 2)))
    # --- lane X-braces (xz plane at y=0, 2.4 thick) between neighbouring beams
    lane = []
    z = 0.0
    while z + LANE_BLOCK <= H - 1e-6:
        for i in range(NX):
            xl, xr = xw[i] + WALL / 2 - 0.3, xw[i + 1] - WALL / 2 + 0.3
            clip = box(xl, z, xr, z + LANE_BLOCK)
            lane.append(diag_poly((xl, z), (xr, z + LANE_BLOCK), clip)); lane.append(diag_poly((xl, z + LANE_BLOCK), (xr, z), clip))
        z += LANE_BLOCK
    if lane: parts.append(prism(unary_union(lane), WALL, xmap_xz(WALL / 2)))
    # --- floors (base, 1..n-1 and top cap n): plate between the beams
    px0, px1 = xw[0] - WALL / 2 + 0.3, xw[-1] + WALL / 2 - 0.3
    plate = box(px0, -PLATE_HY, px1, PLATE_HY)
    for k in range(n + 1):
        parts.append(ct.extrude(plate, PITCH * k, PITCH * k + TF))
    # --- studs on the floor top under every coin
    studs = ct.stud_polys(ct.footprint_bottom())
    for k in range(n):
        ztop = PITCH * k + TF
        for (x, y) in coins:
            parts.append(ct.extrude(affinity.translate(studs, x, y), ztop - EPS, ztop + ct.STUD_H))
    return parts, coins, H

def build(NX, n, out):
    parts, coins, H = geometry(NX, n)
    c = trimesh.load("gocricket_coin_lowres.stl")
    coin = mf.Manifold(mf.Mesh(np.array(c.vertices, np.float32), np.array(c.faces, np.uint32)))
    for k in range(n):
        zb = PITCH * k + TF + G
        for (x, y) in coins: parts.append(coin.translate([x, y, zb]))
    solid = mf.Manifold.batch_boolean([p for p in parts if p is not None], mf.OpType.Add)
    mesh = solid.to_mesh()
    t = trimesh.Trimesh(mesh.vert_properties[:, :3], mesh.tri_verts)
    t.apply_translation([128, 128, 0]); t.export(out + ".stl")
    info = dict(towers=NX, coins_per_level=len(coins), levels=n, coins=len(coins) * n, pitch=PITCH,
                height=round(float(t.bounds[1][2]), 2), width_x=round(float(t.bounds[1][0] - t.bounds[0][0]), 1),
                width_y=round(float(t.bounds[1][1] - t.bounds[0][1]), 1), faces=len(t.faces),
                volume_cm3=round(t.volume / 1000, 1), watertight=bool(t.is_watertight))
    json.dump(info, open(out + "_info.json", "w"), indent=1)
    return t, info

if __name__ == "__main__":
    NX, n = int(sys.argv[1]), int(sys.argv[2])
    out = sys.argv[3] if len(sys.argv) > 3 else f"rack_{NX}x{n}"
    t, info = build(NX, n, out); print(json.dumps(info))

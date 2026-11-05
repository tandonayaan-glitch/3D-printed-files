"""Builds gocricket_coin.stl (same format as coin_v10: 32mm, 3.5mm tall, reeded edge, raised rim/text)."""
import numpy as np, trimesh, manifold3d as mf
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from shapely import affinity
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

R, FIELD, TOP = 16.0, 3.0, 3.5
fp = FontProperties(family="DejaVu Sans", weight="bold")

def glyph(ch, size):
    tp = TextPath((0, 0), ch, size=size, prop=fp)
    polys = [Polygon(p) for p in tp.to_polygons() if len(p) > 2]
    polys.sort(key=lambda p: -p.area); out = None
    for p in polys:  # even-odd: holes subtract
        out = p if out is None else (out.difference(p) if out.contains(p) else out.union(p))
    return out, tp.get_extents().width

def arc_text(s, size, r, top=True, gap=0.3):
    items = []
    for ch in s:
        g, w = glyph(ch, size)
        items.append((g, w, (w if ch.strip() else size*0.35) + gap))
    total = sum(i[2] for i in items) - gap
    res = []; pos = -total / 2
    for g, w, adv in items:
        if g is not None and not g.is_empty:
            mid = pos + (w / 2 if g is not None and w else 0)
            g = affinity.translate(g, -(g.bounds[0] + g.bounds[2]) / 2, 0)
            if top:
                g = affinity.translate(g, 0, r)
                g = affinity.rotate(g, np.degrees(-mid / r), origin=(0, 0))
            else:
                g = affinity.translate(g, 0, -r)
                g = affinity.rotate(g, np.degrees(mid / r), origin=(0, 0))
            res.append(g)
        pos += adv
    return unary_union(res)

# ---- 2D layers
n = 120
ang = np.linspace(0, 2*np.pi, n*12, endpoint=False)
rr = R - 0.28 + 0.28*np.abs(np.sin(n/2*ang))  # reeded/scalloped edge
disc = Polygon(np.c_[rr*np.cos(ang), rr*np.sin(ang)])
rim = Point(0,0).buffer(15.3, 128).difference(Point(0,0).buffer(13.9, 128))
bead = Point(0,0).buffer(9.85, 96).difference(Point(0,0).buffer(9.45, 96))

top_txt = arc_text("GOCRICKET", 3.4, 10.3, top=True).buffer(0.12)
bot_txt = arc_text("gocricket.in", 3.0, 12.9, top=False, gap=0.5).buffer(0.05)
# bottom text: rotate so it reads left->right along the bottom
bot_txt = affinity.rotate(bot_txt, 0)
dots = unary_union([Point(-11.7,0).buffer(.5), Point(11.7,0).buffer(.5)])

from shapely.geometry import LineString
CY = 1.3   # vertical offset of centre motif (leaves room for HEADS / TAILS below)
def bat(a):
    blade = box(-1.4,-1.0,1.4,6.8).buffer(-0.5).buffer(0.5, 16)
    shoulder = Polygon([(-1.4,-1.0),(1.4,-1.0),(0.45,-2.7),(-0.45,-2.7)])
    handle = box(-0.45,-7.4,0.45,-2.6)
    grip = box(-0.62,-7.4,0.62,-4.7).buffer(-0.3).buffer(0.3, 16)
    b = unary_union([blade, shoulder, handle, grip])
    cuts = [LineString([(-0.7,y),(0.7,y)]).buffer(0.17, cap_style=2) for y in (-5.3,-6.0,-6.7)]
    cuts.append(LineString([(-1.4,-1.0),(0,0.9),(1.4,-1.0)]).buffer(0.15))
    return affinity.rotate(b.difference(unary_union(cuts)), a, origin=(0,0))

def seamed_ball(cx, cy, r):
    ball = Point(cx, cy).buffer(r, 64)
    seam = unary_union([
        Point(cx-r-0.2, cy).buffer(r*0.92, 64).difference(Point(cx-r-0.55, cy).buffer(r*0.92, 64)),
        Point(cx+r+0.2, cy).buffer(r*0.92, 64).difference(Point(cx+r+0.55, cy).buffer(r*0.92, 64))]).intersection(ball)
    return ball, ball.difference(seam)

def label(txt, size, y_base, bold=0.05):
    return affinity.translate(glyphs_line(txt, size), 0, y_base).buffer(bold)

def glyphs_line(txt, size, gap=0.25):
    parts=[]; x=0
    for ch in txt:
        g, w = glyph(ch, size)
        if g is not None:
            parts.append(affinity.translate(g, x - g.bounds[0], 0)); x += (g.bounds[2]-g.bounds[0]) + gap
    u = unary_union(parts)
    return affinity.translate(u, -(u.bounds[0]+u.bounds[2])/2, 0)

SC = 0.78
def front_center():
    bats = affinity.scale(unary_union([bat(28), bat(-28)]), SC, SC, origin=(0,0))
    bats = affinity.translate(bats, 0, CY)
    ball, ball_solid = seamed_ball(0, CY+0.55, 1.95)
    return unary_union([bats.difference(ball.buffer(0.45)), ball_solid])

def back_center(sw):
    stumps = []
    for x in (-1.55, 0, 1.55):
        stumps.append(box(x-sw/2, CY-4.4, x+sw/2, CY+4.4).buffer(-0.2).buffer(0.2, 12))
    bails = [box(-2.5, CY+4.7, -0.3, CY+5.2), box(0.3, CY+4.7, 2.5, CY+5.2)]
    stumps_u = unary_union(stumps)
    ball, ball_solid = seamed_ball(0, CY-2.7, 1.95)
    return unary_union([stumps_u.difference(ball.buffer(0.45)), unary_union(bails), ball_solid])

common = unary_union([rim, bead, top_txt, bot_txt, dots])
def face(kind, sw=0.95):
    if kind == "front":
        return unary_union([common, front_center(), label("HEADS", 2.2, -7.9, 0.06)])
    return unary_union([common, back_center(sw), label("TAILS", 2.2, -7.9, 0.06)])

# ---- balance: equal relief area on both faces (equal mass front/back)
lo, hi = 0.6, 1.4
fa = face("front").intersection(disc).area
for _ in range(40):
    mid = (lo+hi)/2
    if face("back", mid).intersection(disc).area < fa: lo = mid
    else: hi = mid
sw = (lo+hi)/2
F = face("front").intersection(disc)
B = face("back", sw).intersection(disc)
print("stump width", round(sw,3), "areas", F.area, B.area)

# ---- left/right + up/down balance: centroid of total relief (back is mirrored in X when printed on the bed)
Bm = affinity.scale(B, -1, 1, origin=(0,0))
tot = unary_union([F]).area; cx = (F.centroid.x*F.area + Bm.centroid.x*Bm.area)/(F.area+Bm.area); cy=(F.centroid.y*F.area+Bm.centroid.y*Bm.area)/(F.area+Bm.area)
print("relief centroid offset (mm):", cx, cy)

def extrude(g, z0, z1):
    geoms = [g] if g.geom_type == "Polygon" else list(g.geoms)
    parts = []
    for p in geoms:
        if p.is_empty or p.area < 1e-4: continue
        cs = mf.CrossSection([np.array(p.exterior.coords)[:-1]] + [np.array(h.coords)[:-1] for h in p.interiors], mf.FillRule.EvenOdd)
        parts.append(mf.Manifold.extrude(cs, z1 - z0).translate([0, 0, z0]))
    return mf.Manifold.batch_boolean(parts, mf.OpType.Add)

body = extrude(disc, 0.49, FIELD + 0.01 - 0.0)
top_rel = extrude(F, FIELD - 0.01, TOP)
bot_rel = extrude(Bm, 0.0, 0.51)
# edge band full height both sides is provided by relief rim; body spans 0.5..3.0
m = (body + top_rel + bot_rel).translate([128, 128, 0])
mesh = m.to_mesh()
t = trimesh.Trimesh(mesh.vert_properties[:, :3], mesh.tri_verts)
t.export("gocricket_coin.stl")
print(t.is_watertight, t.bounds, t.volume)
com = t.center_mass - [128,128,0]
print("centre of mass offset x,y,z-1.75:", com[0], com[1], com[2]-1.75)

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
rim = Point(0,0).buffer(15.3, 128).difference(Point(0,0).buffer(13.4, 128))
bead = Point(0,0).buffer(9.9, 96).difference(Point(0,0).buffer(9.45, 96))

top_txt = arc_text("GOCRICKET", 2.3, 10.5, top=True)
bot_txt = arc_text("gocricket.in", 2.0, 12.5, top=False)
# bottom text: rotate so it reads left->right along the bottom
bot_txt = affinity.rotate(bot_txt, 0)
dots = unary_union([Point(-11.6,0).buffer(.45), Point(11.6,0).buffer(.45)])

from shapely.geometry import LineString
def bat(a):
    blade = box(-1.4,-1.0,1.4,6.8).buffer(-0.5).buffer(0.5, 16)           # flat face, rounded toe
    shoulder = Polygon([(-1.4,-1.0),(1.4,-1.0),(0.45,-2.7),(-0.45,-2.7)])
    handle = box(-0.45,-7.4,0.45,-2.6)
    grip = box(-0.62,-7.4,0.62,-4.7).buffer(-0.3).buffer(0.3, 16)
    b = unary_union([blade, shoulder, handle, grip])
    cuts = [LineString([(-0.7,y),(0.7,y)]).buffer(0.17, cap_style=2) for y in (-5.3,-6.0,-6.7)]
    cuts.append(LineString([(-1.4,-1.0),(0,0.9),(1.4,-1.0)]).buffer(0.15))     # splice
    b = b.difference(unary_union(cuts))
    return affinity.rotate(b, a, origin=(0,0))
bats = unary_union([bat(28), bat(-28)])
ball = Point(0, 0.8).buffer(2.2, 64)
seam = unary_union([
    Point(-2.4,0.8).buffer(2.0,64).difference(Point(-2.75,0.8).buffer(2.0,64)),
    Point(2.4,0.8).buffer(2.0,64).difference(Point(2.75,0.8).buffer(2.0,64))]).intersection(ball)
ball_solid = ball.difference(seam)
raised_top = unary_union([rim, bead, top_txt, bot_txt, dots, bats.difference(ball.buffer(0.5)), ball_solid])

def extrude(g, z0, z1):
    geoms = [g] if g.geom_type == "Polygon" else list(g.geoms)
    parts = []
    for p in geoms:
        if p.is_empty or p.area < 1e-4: continue
        cs = mf.CrossSection([np.array(p.exterior.coords)[:-1]] + [np.array(h.coords)[:-1] for h in p.interiors],
                             mf.FillRule.EvenOdd)
        parts.append(mf.Manifold.extrude(cs, z1 - z0).translate([0, 0, z0]))
    return mf.Manifold.batch_boolean(parts, mf.OpType.Add)

body = extrude(disc, 0, FIELD)
relief = extrude(raised_top.intersection(disc), FIELD - 0.01, TOP)
m = (body + relief).translate([128, 128, 0])
mesh = m.to_mesh()
t = trimesh.Trimesh(mesh.vert_properties[:, :3], mesh.tri_verts)
t.export("gocricket_coin.stl")
print(t.is_watertight, t.bounds, t.volume)

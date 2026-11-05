"""Geometry verification of the finished tower mesh (run on the exported STL, not on the generator)."""
import sys, json, numpy as np, trimesh, manifold3d as mf
path = sys.argv[1]
t = trimesh.load(path, process=False); t.merge_vertices()
print("mesh: faces %d  watertight %s  winding-consistent %s" % (len(t.faces), t.is_watertight, t.is_winding_consistent))
lo, hi = t.bounds
print("bounds X %.1f..%.1f  Y %.1f..%.1f  Z %.2f..%.2f   (A1 bed 0..256 x 0..256 x 256)" % (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
assert lo[0] > 0 and lo[1] > 0 and lo[2] >= 0 and hi[0] < 256 and hi[1] < 256 and hi[2] < 256
M = mf.Manifold(mf.Mesh(np.array(t.vertices, np.float32), np.array(t.faces, np.uint32)))
parts = M.decompose()
vols = np.array([p.volume() for p in parts]); bb = [p.bounding_box() for p in parts]
big = int(np.argmax(vols))
coin_ids = [i for i in range(len(parts)) if i != big]
cv = vols[coin_ids]
print("separate bodies: %d  ->  1 structure (%.1f cm3) + %d free-standing coins" % (len(parts), vols[big] / 1000, len(coin_ids)))
print("coin volume min/max %.1f / %.1f mm3 (joined 32x3.6 coin low-res = 2246.5)" % (cv.min(), cv.max()))
cen = np.array([[(bb[i][0] + bb[i][3]) / 2, (bb[i][1] + bb[i][4]) / 2, bb[i][2], bb[i][5]] for i in coin_ids])
print("coin diameter %.2f..%.2f   thickness %.2f..%.2f" % (min(bb[i][3]-bb[i][0] for i in coin_ids), max(bb[i][3]-bb[i][0] for i in coin_ids),
      min(bb[i][5]-bb[i][2] for i in coin_ids), max(bb[i][5]-bb[i][2] for i in coin_ids)))
zb = np.unique(cen[:, 2].round(2)); print("distinct coin-bottom levels:", len(zb), " pitch set:", np.unique(np.diff(zb).round(2)))
coins = mf.Manifold.compose([parts[i] for i in coin_ids]); S = parts[big]
res = {}
for dz in (-0.19, 0.19):
    res[f"dz{dz:+.2f}"] = (S ^ coins.translate([0, 0, dz])).volume()
for ang in range(0, 360, 30):
    d = 0.9; res[f"lat{ang}"] = (S ^ coins.translate([d * np.cos(np.radians(ang)), d * np.sin(np.radians(ang)), 0])).volume()
print("contact test (volume of overlap between structure and ALL coins when coins are nudged; must be 0):")
print("  vertical  +-0.19 mm:", {k: round(v, 4) for k, v in res.items() if k.startswith('dz')})
print("  lateral 0.9 mm, 12 directions: max overlap %.4f mm3" % max(v for k, v in res.items() if k.startswith('lat')))
import math; sys.path.insert(0, '..'); import coin_tower as ct
print("  analytic: coin edge -> nearest pillar surface = %.2f mm ; coin edge -> rib edge = %.2f mm (ribs are at floor level, not coin level)" % (ct.HEX_R - ct.R_PILLAR - ct.RC, ct.D / 2 - ct.RIB_W / 2 - ct.RC))
print("  coins touching structure at rest:", round((S ^ coins).volume(), 4), "mm3")
json.dump(dict(bodies=len(parts), coins=len(coin_ids), results={k: float(v) for k, v in res.items()}), open("/tmp/sp/verify.json", "w"))

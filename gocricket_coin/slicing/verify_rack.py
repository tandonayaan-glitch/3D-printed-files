"""Geometry verification of the rack mesh (run on the exported STL)."""
import sys, json, numpy as np, trimesh, manifold3d as mf
path = sys.argv[1]
t = trimesh.load(path, process=False); t.merge_vertices()
print("mesh: faces %d  watertight %s  winding-consistent %s" % (len(t.faces), t.is_watertight, t.is_winding_consistent))
lo, hi = t.bounds
print("bounds X %.1f..%.1f  Y %.1f..%.1f  Z %.2f..%.2f   (A1 bed 0..256 x 0..256 x 256)" % (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
assert lo[0] > 0 and lo[1] > 0 and lo[2] >= 0 and hi[0] < 256 and hi[1] < 256 and hi[2] < 256
M = mf.Manifold(mf.Mesh(np.array(t.vertices, np.float32), np.array(t.faces, np.uint32)))
parts = M.decompose(); vols = np.array([p.volume() for p in parts]); big = int(np.argmax(vols))
cid = [i for i in range(len(parts)) if i != big]
bb = [parts[i].bounding_box() for i in cid]
print("separate bodies: %d -> 1 structure (%.1f cm3) + %d free coins" % (len(parts), vols[big] / 1000, len(cid)))
cv = vols[cid]; print("coin volume %.1f..%.1f mm3 (joined low-res coin 2246.5); diameter %.2f; thickness %.2f..%.2f" % (cv.min(), cv.max(), np.mean([b[3]-b[0] for b in bb]), min(b[5]-b[2] for b in bb), max(b[5]-b[2] for b in bb)))
zb = np.unique(np.round([b[2] for b in bb], 2)); print("coin levels: %d  coin-bottom pitch: %s mm" % (len(zb), np.unique(np.diff(zb).round(2))))
S = parts[big]
front = [parts[i] for i in cid if (parts[i].bounding_box()[1] + parts[i].bounding_box()[4]) / 2 < 128]
rear = [parts[i] for i in cid if (parts[i].bounding_box()[1] + parts[i].bounding_box()[4]) / 2 >= 128]
F, R = mf.Manifold.compose(front), mf.Manifold.compose(rear)
allc = mf.Manifold.compose(front + rear)
print("coins touching structure at rest: %.4f mm3" % (S ^ allc).volume())
print("vertical nudge +-0.19 mm overlap: %.4f / %.4f mm3" % ((S ^ allc.translate([0, 0, -0.19])).volume(), (S ^ allc.translate([0, 0, 0.19])).volume()))
print("lateral nudge 0.7 mm in X (beam clearance 0.8): %.4f mm3" % max((S ^ allc.translate([d, 0, 0])).volume() for d in (-0.7, 0.7)))
# slide-out test: lift 0.7 mm (clears the studs, 1.2 mm headroom), then front coins go -Y, rear coins +Y, every coin of every floor at once
worst = 0.0
for s in np.arange(0, 50.1, 2.0):
    mv = F.translate([0, -s, 0.7]) + R.translate([0, s, 0.7])
    worst = max(worst, (S ^ mv).volume())
print("slide-out sweep (lift 0.7 mm, travel 0..50 mm along +-Y, all 148 coins at once): max overlap %.4f mm3  (0 = every coin leaves freely)" % worst)

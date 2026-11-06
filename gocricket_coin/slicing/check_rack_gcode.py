"""Real-G-code checks for the rack: gap layer under every coin, free headroom above every coin, floor starts on time,
and the direction of the floor's first (bridge) layer lines (must run ACROSS the tower so both ends are anchored on a beam)."""
import sys, re, math, json, numpy as np
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import coin_rack as cr
NX, n = int(sys.argv[2]), int(sys.argv[3])
parts, coins, H = cr.geometry(NX, n)
C = np.array(coins) + 128.0
P, TF = cr.PITCH, cr.TF
want = {}
for k in range(n):
    zt = P * k + TF                                    # floor top under coin k
    for name, z in (("floor_top", zt), ("gap", zt + 0.2), ("coin_first", zt + 0.4), ("coin_last", zt + 3.8)):
        want.setdefault(round(z, 2), []).append((k, name))
    for j in range(6):                                 # 1.2 mm free headroom above the coin = 6 layers
        want.setdefault(round(zt + 4.0 + 0.2 * j, 2), []).append((k, "headroom"))
    if k >= 1: want.setdefault(round(P * k + 0.2, 2), []).append((k, "floor_bridge_layer"))
stat = {}; bridge_dir = {}
pat = re.compile(r'([XYZE])(-?\d*\.?\d+)')
x = y = 0.0; z = 0.0; cur = None
with open(sys.argv[1]) as f:
    for ln in f:
        if ln.startswith(';Z:'):
            z = round(float(ln[3:]), 2); cur = want.get(z); continue
        if cur is None or ln[:2] != 'G1': continue
        d = dict((a, float(v)) for a, v in pat.findall(ln)); nx, ny = d.get('X', x), d.get('Y', y)
        if d.get('E', 0) > 0 and (nx != x or ny != y):
            mx, my = (x + nx) / 2, (y + ny) / 2; L = math.hypot(nx - x, ny - y)
            for (k, name) in cur:
                if name == "floor_bridge_layer":
                    if abs(mx - 128) < 34 and abs(my - 128) < 34:       # inside the plate, away from beams
                        b = bridge_dir.setdefault(k, [0.0, 0.0]); ang = abs(math.degrees(math.atan2(ny - y, nx - x))) % 180
                        b[0 if (ang < 25 or ang > 155) else 1] += L
                else:
                    dist = np.hypot(C[:, 0] - mx, C[:, 1] - my); i = int(dist.argmin())
                    if dist[i] < 15.8: stat.setdefault((k, name), np.zeros(len(C)))[i] += L
        x, y = nx, ny
out = {}
for name in ("gap", "coin_first", "coin_last", "headroom"):
    arr = np.array([stat.get((k, name), np.zeros(len(C))) for k in range(n)])
    out[name] = [float(arr.min()), float(arr.mean()), float(arr.max())]
    print("%-10s extrusion inside each coin footprint (mm of line): min %.0f mean %.0f max %.0f  (%d coin positions)" % (name, *out[name], arr.size))
fr = [b[0] / (b[0] + b[1]) for k, b in bridge_dir.items() if b[0] + b[1] > 0]
print("floor bridge layer (Z=6.6k+0.2, k=1..%d): lines running across the tower (anchored on both beams): min %.0f%%, mean %.0f%% of extrusion length" % (n - 1, 100 * min(fr), 100 * np.mean(fr)))
out["bridge_across_pct_min"] = 100 * min(fr)
json.dump(out, open('/tmp/sp/rack_gaps.json', 'w'))

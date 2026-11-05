"""Verify in the real G-code that the designed 0.2 mm gaps exist and the coin layers start where intended.
For every coin (all levels) it measures extrusion length inside the coin footprint (r<15.8) on:
   pad-top layer, GAP layer (must hold only the tiny studs / nothing), coin first layer, last coin layer, pad-bottom-gap layer."""
import sys, re, math, json, numpy as np
sys.path.insert(0, '..')
import coin_tower as ct
cols, rows, levels = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
coins = np.array(ct.layout(cols, rows)) + 128.0
pat = re.compile(r'([XYZE])(-?\d*\.?\d+)')
want = {}
for k in range(levels):
    pt = ct.BASE + k * ct.PITCH               # pad (or base) top
    cb = pt + ct.GAP
    ct_ = cb + ct.TC
    for name, z in (("pad_top", pt), ("gap", pt + 0.2), ("coin_first", pt + 0.4), ("coin_last", ct_), ("gap_above_coin", ct_ + 0.2)):
        want.setdefault(round(z, 2), []).append((k, name))
stat = {}   # (k,name) -> list of length per coin
z = 0; x = y = 0.0; cur = None
with open(sys.argv[1]) as f:
    for ln in f:
        if ln.startswith(';Z:'):
            z = round(float(ln[3:]), 2); cur = want.get(z); continue
        if cur is None or ln[:2] != 'G1': continue
        d = dict((k, float(v)) for k, v in pat.findall(ln)); nx = d.get('X', x); ny = d.get('Y', y)
        if d.get('E', 0) > 0 and (nx != x or ny != y):
            mx, my = (x + nx) / 2, (y + ny) / 2; L = math.hypot(nx - x, ny - y)
            dist = np.hypot(coins[:, 0] - mx, coins[:, 1] - my); i = int(dist.argmin())
            if dist[i] < 15.8:
                for key in cur: stat.setdefault(key, np.zeros(len(coins)))[i] += L
        x, y = nx, ny
out = {}
for name in ("pad_top", "gap", "coin_first", "coin_last", "gap_above_coin"):
    arr = np.array([stat.get((k, name), np.zeros(len(coins))) for k in range(levels)])
    out[name] = (arr.min(), arr.mean(), arr.max())
    if name == "pad_top": print("pad_top length by level k=0..5 (min over coins):", [round(float(arr[k].min())) for k in range(6)], " ... k=29:", round(float(arr[29].min())))
    print("%-15s extrusion length inside each coin footprint (mm): min %.0f  mean %.0f  max %.0f   over %d coin positions" % (name, *out[name], arr.size))
json.dump({k: list(map(float, v)) for k, v in out.items()}, open('/tmp/sp/gaps.json', 'w'))

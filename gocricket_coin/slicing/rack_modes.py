"""3-D beam model of the coin rack (beam posts, bands, truss diagonals, floor strips) -> lowest sway modes.
Floors are modelled as in-plane strips (conservative: a real plate is stiffer).  E = 2 GPa (layer-bond value)."""
import sys, math, numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla
sys.path.insert(0, '..'); sys.path.insert(0, '.')
import coin_rack as cr
from tower_modes import beam_K, rot

def modes(NX, n, E=2.0e3, nu=0.35, nm=6):
    G = E / (2 * (1 + nu)); P = cr.PITCH
    xw = [(i - NX / 2) * cr.TPITCH for i in range(NX + 1)]; ys = cr.POST_Y; nl = n + 2    # levels 0..n+1 (n+1 = top of beams)
    zl = [P * k for k in range(n + 1)] + [P * n + cr.TF]
    idx = {}; 
    for l in range(nl):
        for i in range(NX + 1):
            for j in range(len(ys)): idx[(l, i, j)] = len(idx)
    N = len(idx); coo = ([], [], [])
    def pos(l, i, j): return np.array([xw[i], ys[j], zl[l]])
    def add(a, b, A, Iy, Iz, J):
        p0, p1 = pos(*a), pos(*b); L, T = rot(p0, p1); k = beam_K(L, E, G, A, Iy, Iz, J)
        kg = T.T @ k @ T; ids = list(range(6 * idx[a], 6 * idx[a] + 6)) + list(range(6 * idx[b], 6 * idx[b] + 6))
        for p in range(12):
            for q in range(12): coo[0].append(ids[p]); coo[1].append(ids[q]); coo[2].append(kg[p, q])
    t, w = cr.WALL, cr.POST_W
    for l in range(nl - 1):
        for i in range(NX + 1):
            for j in range(len(ys)):
                add((l, i, j), (l + 1, i, j), t * w, t * w ** 3 / 12, w * t ** 3 / 12, 0.2 * t * w * min(t, w) ** 2)
    for l in range(1, nl - 1):                                    # floor levels 1..n (n = cap)
        for i in range(NX + 1):
            for j in range(len(ys) - 1):                          # wall band along Y
                add((l, i, j), (l, i, j + 1), t * cr.BAND, t ** 3 * cr.BAND / 12, cr.BAND ** 3 * t / 12, 0.3 * t * cr.BAND ** 3)
        for i in range(NX):
            for j in range(len(ys)):                              # floor strip along X
                wd = 17.0 if 0 < j < len(ys) - 1 else 9.5
                add((l, i, j), (l, i + 1, j), wd * cr.TF, cr.TF ** 3 * wd / 12, wd ** 3 * cr.TF / 12, 0.3 * wd * cr.TF ** 3)
    # diagonals
    Ad, Id = t * cr.DIAG_W, t * cr.DIAG_W ** 3 / 12; Id2 = cr.DIAG_W * t ** 3 / 12
    def lvl(z): return int(round(z / P))
    z = 0.0; Hh = P * n + cr.TF
    while z + cr.WALL_BLOCK <= Hh - 1e-6:
        l0, l1 = lvl(z), lvl(z + cr.WALL_BLOCK)
        for i in range(NX + 1):
            for j in range(len(ys) - 1):
                add((l0, i, j), (l1, i, j + 1), Ad, Id, Id2, 0.2 * Ad * 2); add((l0, i, j + 1), (l1, i, j), Ad, Id, Id2, 0.2 * Ad * 2)
        z += cr.WALL_BLOCK
    z = 0.0; jm = len(ys) // 2
    while z + cr.LANE_BLOCK <= Hh - 1e-6:
        l0, l1 = lvl(z), lvl(z + cr.LANE_BLOCK)
        for i in range(NX):
            add((l0, i, jm), (l1, i + 1, jm), Ad, Id, Id2, 0.4 * Ad); add((l0, i + 1, jm), (l1, i, jm), Ad, Id, Id2, 0.4 * Ad)
        z += cr.LANE_BLOCK
    K = sp.coo_matrix((coo[2], (coo[0], coo[1])), shape=(6 * N, 6 * N)).tocsr()
    rho = 1.24e-9; m = np.zeros(N)
    for l in range(1, nl - 1):
        floor_m = rho * (NX * cr.W_IN * 2 * cr.PLATE_HY * cr.TF + 0)
        coin_m = rho * 2246.5 * 2 * NX if l - 1 < n else 0
        nn = (NX + 1) * len(ys)
        for i in range(NX + 1):
            for j in range(len(ys)): m[idx[(l, i, j)]] += (floor_m + coin_m) / nn
    for l in range(1, nl):
        for i in range(NX + 1):
            for j in range(len(ys)): m[idx[(l, i, j)]] += rho * t * w * P * 1.0
    Md = np.repeat(m, 6); Md[Md == 0] = 1e-14
    fixed = 6 * (NX + 1) * len(ys); free = np.arange(fixed, 6 * N)
    w2, v = sla.eigsh(K[free][:, free], k=nm, M=sp.diags(Md[free]), sigma=0, which='LM')
    f = np.sqrt(np.abs(w2)) / (2 * math.pi)
    # classify mode direction by participation of x vs y translations at the top level
    out = []
    for q in np.argsort(f):
        vec = v[:, q]; top = [idx[(nl - 1, i, j)] for i in range(NX + 1) for j in range(len(ys))]
        ux = sum(abs(vec[6 * a - fixed]) for a in top); uy = sum(abs(vec[6 * a + 1 - fixed]) for a in top); uz = sum(abs(vec[6 * a + 2 - fixed]) for a in top)
        out.append((round(float(f[q]), 1), "X-sway" if ux > max(uy, uz) else "Y-sway" if uy > max(ux, uz) else "other"))
    return out, m.sum() * 1e9 / 1e3
if __name__ == "__main__":
    NX, n = int(sys.argv[1]), int(sys.argv[2]); o, M = modes(NX, n); print(f"rack {NX} towers x {n} levels: modes {o}  (model mass {M:.0f} g)")

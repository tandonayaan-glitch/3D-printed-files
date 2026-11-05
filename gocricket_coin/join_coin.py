"""Verify that the two printed halves form exactly the ONE complete 32 x 3.6 mm coin (gocricket_coin_joined.stl).
Heads half: relief up, flat face at z=0.  Tails half: turned over like a page (180 deg about Y) and glued flat-to-flat.
The joined coin is produced by make_coin.py from the same polygons (exact, manifold); this script proves it equals the
union of the two half STLs, i.e. nothing was lost, overlapped or doubled (no 5.4 mm coin)."""
import numpy as np, trimesh, manifold3d as mf
def M(path, tf=None):  # load an STL as a manifold
    m = trimesh.load(path); v = np.array(m.vertices, float)
    if tf: v = tf(v)
    return mf.Manifold(mf.Mesh(v.astype(np.float32), np.array(m.faces, np.uint32)))
heads = M("gocricket_heads_half.stl", lambda v: v + [-128, -128, 1.8])   # on top
tm = trimesh.load("gocricket_tails_half.stl")      # turning the half over = rotation 180 deg about Y: x -> -x, z -> 1.8 - z (winding unchanged)
v = np.c_[-(tm.vertices[:, 0] - 128), tm.vertices[:, 1] - 128, 1.8 - tm.vertices[:, 2]]
tails = mf.Manifold(mf.Mesh(v.astype(np.float32), np.array(tm.faces, np.uint32)))
joined = trimesh.load("gocricket_coin_joined.stl"); jm = mf.Manifold(mf.Mesh(np.array(joined.vertices, np.float32), np.array(joined.faces, np.uint32)))
u = heads + tails
print("halves: heads %.1f mm3 (1.8 thick), tails %.1f mm3 (1.8 thick)" % (heads.volume(), tails.volume()))
print("union of halves  : %.1f mm3, bounds z %.2f..%.2f" % (u.volume(), u.bounding_box()[2], u.bounding_box()[5]))
print("joined coin file : %.1f mm3, bounds %s, watertight %s" % (joined.volume, (joined.bounds[1] - joined.bounds[0]).round(3).tolist(), joined.is_watertight))
print("symmetric difference joined vs halves-union: %.3f mm3  (<<1 = identical)" % ((u - jm).volume() + (jm - u).volume()))
print("overlap between the two halves (must be 0, otherwise the coin would be thicker/doubled): %.4f mm3" % (heads ^ tails).volume())

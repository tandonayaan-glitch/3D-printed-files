"""Painter's-algorithm renderer (PIL) for STL previews.  usage: render_preview.py in.stl out.png az el [W H] [zmin zmax] [cutx]"""
import sys, numpy as np, trimesh
from PIL import Image, ImageDraw
def render(stl, out, az, el, W=1400, H=1400, zrange=None, clipx=None, clipy=None, bg=(246,247,249), color=(235,170,40), scale=None):
    m = trimesh.load(stl, process=False)
    V = m.vertices.copy(); F = m.faces
    tri = V[F]
    keep = np.ones(len(F), bool)
    if zrange: c = tri[:, :, 2]; keep &= (c.min(1) >= zrange[0] - 1e-6) & (c.max(1) <= zrange[1] + 1e-6)
    if clipx is not None: keep &= tri[:, :, 0].mean(1) < clipx
    if clipy is not None: keep &= tri[:, :, 1].mean(1) > clipy
    tri = tri[keep]
    c0 = (tri.reshape(-1, 3).max(0) + tri.reshape(-1, 3).min(0)) / 2; tri = tri - c0
    a, e = np.radians(az), np.radians(el)
    Rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    R = Rx.T @ Rz.T   # world -> view (x right, y depth-away, z up)
    P = tri @ R.T
    n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); nl = np.linalg.norm(n, axis=1) + 1e-12; n = n / nl[:, None]
    front = n[:, 1] < 0            # facing the camera (camera looks along +y)
    P = P[front]; n = n[front]
    light = np.array([-0.4, -0.7, 0.6]); light /= np.linalg.norm(light)
    sh = np.clip(n @ light, 0, 1) * 0.75 + 0.25
    depth = P[:, :, 1].mean(1); order = np.argsort(-depth)
    ext = np.abs(P[:, :, [0, 2]]).max() if scale is None else scale
    s = 0.47 * min(W, H) / ext
    img = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(img)
    col = np.array(color, float)
    for i in order:
        t = P[i]; pts = [(W / 2 + t[k, 0] * s, H / 2 - t[k, 2] * s) for k in range(3)]
        d.polygon(pts, fill=tuple((col * sh[i]).astype(int)))
    img.save(out)
if __name__ == "__main__":
    a = sys.argv; zr = None; cx = None
    render(a[1], a[2], float(a[3]), float(a[4]))

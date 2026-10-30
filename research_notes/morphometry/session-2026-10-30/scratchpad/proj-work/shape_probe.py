import sys, math, time
sys.path.insert(0, "/home/user/bordercall")
import numpy as np
from morphoview import shapes as SH, projection as PJ

def dist_to_polyline(q, pts, closed):
    P = np.vstack([pts, pts[:1]]) if closed else pts
    a, b = P[:-1], P[1:]
    ab = b - a
    t = np.clip(((q[:, None, :] - a[None]) * ab[None]).sum(-1) / (ab * ab).sum(-1)[None], 0, 1)
    proj = a[None] + t[..., None] * ab[None]
    return np.linalg.norm(q[:, None, :] - proj, axis=-1).min(axis=1)

# arc
c = np.array([1.0, 2.0, 3.0]); n = np.array([0.3, -0.2, 0.9])
cur = SH.arc(c, n, c + [10.0, 0, 0], 250.0)
e1 = cur.points[0] - c; r = np.linalg.norm(e1); e1 /= r; e2 = np.cross(SH.unit(n), e1)
t = np.linspace(0, math.radians(250), 20001)
true = c + r * (np.cos(t)[:, None] * e1 + np.sin(t)[:, None] * e2)
print("arc pts", len(cur.points), "max dev", dist_to_polyline(true, cur.points, False).max())
cir = SH.circle(c, n, 12.0)
t = np.linspace(0, 2 * math.pi, 20001)
E1, E2 = SH.across(n)
true = c + 12 * (np.cos(t)[:, None] * E1 + np.sin(t)[:, None] * E2)
print("circle pts", len(cir.points), "max dev", dist_to_polyline(true, cir.points, True).max())
a = np.array([20.0, 0, 0]); b = np.array([0, 3.0, 0])
el = SH.ellipse(c, a, b)
true = c + np.cos(t)[:, None] * a + np.sin(t)[:, None] * b
print("ellipse pts", len(el.points), "max dev", dist_to_polyline(true, el.points, True).max())
# spline
rng = np.random.default_rng(3)
pts = np.cumsum(rng.normal(size=(7, 3)) * [5, 5, 30], axis=0)
sp = SH.spline(pts)
ext = np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]])
dense = np.vstack([SH.catmull_rom(ext[i:i + 4], np.linspace(0, 1, 4001)) for i in range(len(pts) - 1)])
print("spline pts", len(sp.points), "max dev", dist_to_polyline(dense, sp.points, False).max(),
      "through:", max(np.linalg.norm(sp.points - p, axis=1).min() for p in pts))
spc = SH.spline(pts, closed=True)
extc = np.vstack([pts[-1:], pts, pts[:2]])
dense = np.vstack([SH.catmull_rom(extc[i:i + 4], np.linspace(0, 1, 4001)) for i in range(len(pts))])
print("closed spline pts", len(spc.points), "max dev", dist_to_polyline(dense, spc.points, True).max())
# ball chords under parallel rays
sp_ = (0.5, 0.5, 0.5)
R = 10.0
g = np.indices((48, 48, 48)).reshape(3, -1).T * 0.5
centre = np.array([12.1, 11.9, 12.05])
mask = (np.linalg.norm(g - centre, axis=1) <= R).reshape(48, 48, 48)
aff = np.diag([0.5, 0.5, 0.5, 1.0])
vol = SH.Volume(mask, aff)
view = PJ.View(rot_deg=(0, 0, 0), xyz_mm=(0, 800, 0), isocentre_mm=tuple(centre), sdd=1200, delx=0.7, height=48, width=48, orthographic=True)
cam = PJ.Camera(view)
t0 = time.time(); L = vol.path_length(cam); print("fine path %.2f s" % (time.time() - t0))
uv = cam.pixel_centres()
src, det = cam.rays(uv)
d = cam.beam
# distance of each ray from the centre
w = centre - src
perp = np.linalg.norm(w - (w @ d)[:, None] * d, axis=1)
chord = 2 * np.sqrt(np.clip(R ** 2 - perp ** 2, 0, None))
Lf = L.ravel()
inside = perp < R - 1.0
print("ball fine: max err %.3f median %.3f (inside), max err overall %.3f" % (np.abs(Lf - chord)[inside].max(), np.median(np.abs(Lf - chord)[inside]), np.abs(Lf - chord).max()))
t0 = time.time(); Ln = vol.path_length(cam, n_samples=500); print("flexray path %.2f s" % (time.time() - t0))
print("ball flexray 500: max err %.3f" % np.abs(Ln.ravel() - chord)[inside].max())

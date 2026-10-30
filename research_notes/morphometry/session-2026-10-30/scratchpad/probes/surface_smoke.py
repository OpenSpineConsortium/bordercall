import math, time
import numpy as np
from morphoview import projection as PJ
from morphoview import shapes as SH

cam = PJ.Camera(PJ.View(rot_deg=(0.0, 0.0, 0.0), xyz_mm=(0.0, 800.0, 0.0), isocentre_mm=(0.0, 0.0, 0.0), sdd=1200.0,
                        delx=1.0, height=200, width=240))
plane = SH.Plane([0, 0, 0], [0, 1, 0])
flat = SH.Surface.over(plane, lambda u, v: 0 * u, 20.0, 10.0)
print("flat", flat.vertices.shape, flat.triangles.shape, flat.area(), 4 * 20 * 10, flat.sag(), len(flat.rims()), flat.rims()[0].length())
R, r = 30.0, 15.0
h = R - math.sqrt(R * R - r * r)
cap = SH.Surface.over(plane, lambda u, v: np.sqrt(np.clip(R * R - u * u - v * v, 0, None)) - (R - h), 10.0, 10.0)
print("cap over square", cap.vertices.shape, cap.area())
# a disc-shaped cap by points
rings = []
K = 40
for k in range(K + 1):
    rad = r * k / K
    n = max(1, 6 * k)
    t = np.arange(n) * 2 * math.pi / n
    rings.append(np.stack([rad * np.cos(t), rad * np.sin(t)], 1))
xy = np.vstack(rings)
z = np.sqrt(R * R - (xy ** 2).sum(1)) - (R - h)
pts = np.stack([xy[:, 0], z, xy[:, 1]], 1)
t0 = time.time()
disc = SH.Surface.through(pts)
print("through", time.time() - t0, disc.vertices.shape, disc.triangles.shape)
print("area", disc.area(), 2 * math.pi * R * h, disc.area() / (2 * math.pi * R * h))
print("sag", disc.sag(), h)
rims = disc.rims()
print("rims", len(rims), len(rims[0].points), np.linalg.norm(rims[0].points[:, [0, 2]], axis=1).min(), np.linalg.norm(rims[0].points[:, [0, 2]], axis=1).max())
t0 = time.time()
sil = disc.silhouette(cam)
print("silhouette", time.time() - t0, sil.sum(), math.pi * (r * 1.5) ** 2)
fit, rms = SH.Surface.fit(pts)
print("fit sphere", rms, fit.sag())

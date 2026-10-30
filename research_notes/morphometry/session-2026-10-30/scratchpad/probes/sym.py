import sys
sys.path.insert(0, sys.argv[1])
import numpy as np  # noqa: E402
from morphoview import shapes as SH  # noqa: E402
from morphoview.tests import test_shapes as T  # noqa: E402

V = T.Volumes
V.setUpClass()
self = V()
cam = self.oblique()
src, det = cam.rays(cam.pixel_centres())
inv = np.linalg.inv(self.affine)
a, b = (p @ inv[:3, :3].T + inv[:3, 3] for p in (src, det))
L = np.linalg.norm(det - src, axis=1)
lo, hi = self.ball.box()
f = self.ball.fine_samples(a, b, L, lo, hi, 0.25)
g = self.ball.fine_samples(b, a, L, lo, hi, 0.25)
bad = np.nonzero(np.abs(f - g) > 1e-9)[0]
print(len(bad), "rays differ")
t0, t1 = SH.slab(a, b, lo, hi)
u0, u1 = SH.slab(b, a, lo, hi)
print("t0 vs 1-u1 max", np.abs(t0 - (1 - u1)).max(), " t1 vs 1-u0 max", np.abs(t1 - (1 - u0)).max())
for i in bad[:3]:
    print("ray", i, "forth", f[i], "back", g[i], "t", t0[i], t1[i], "u", u0[i], u1[i], "span", (t1[i]-t0[i])*L[i], (u1[i]-u0[i])*L[i])
import math  # noqa: E402
span = np.clip(t1 - t0, 0, None) * L
n = int(math.ceil(float(span.max()) / 0.25))
print("n", n, "max span", span.max())
i = bad[0]
s = (np.arange(n) + 0.5) / n
pf = a[i] + (t0[i] + s * (t1[i] - t0[i]))[:, None] * (b[i] - a[i])
pb = b[i] + (u0[i] + s * (u1[i] - u0[i]))[:, None] * (a[i] - b[i])
hf, hb = self.ball.inside(pf), self.ball.inside(pb)[::-1]
print("hits", hf.sum(), hb.sum())
d = np.nonzero(hf != hb)[0]
print("differing samples", d[:10])
for k in d[:4]:
    print(k, pf[k], pb[::-1][k], "frac", pf[k] - np.floor(pf[k]))
print("a", a[i], "b", b[i], "b-a", b[i] - a[i])
print("rays whose y runs flat:", int((np.abs((b - a)[:, 1]) < 1e-9).sum()), "of", len(a))
print("pixel of ray", np.unravel_index(i, (cam.view.height, cam.view.width)), "src", src[i], "det", det[i])
print("beam", cam.beam, "to_world", cam.to_world.round(6).tolist())

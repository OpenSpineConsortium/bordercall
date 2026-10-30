"""The two faults the handoff says no output can show: does either move an output?"""
import math
import numpy as np
from morphoview import projection as PJ
from morphoview import shapes as SH

h, R = 0.5, 10.0
centre = np.array([12.1, 11.9, 12.05])
grid = np.indices((48, 48, 48)).reshape(3, -1).T * h
mask = (np.linalg.norm(grid - centre, axis=1) <= R).reshape(48, 48, 48)
ball = SH.Volume(mask, np.diag([h, h, h, 1.0]))

def camera(orthographic, **more):
    view = dict(rot_deg=(10.0, 20.0, 5.0), xyz_mm=(0.0, 800.0, 0.0), isocentre_mm=tuple(centre),
                sdd=1200.0, delx=0.7, height=48, width=48, orthographic=orthographic)
    view.update(more)
    return PJ.Camera(PJ.View(**view))

# fault 1: each fine step sampled at its start rather than its middle
orig_fine = SH.Volume.fine_samples
def fine_at_start(self, a, b, length, lo, hi, step):
    t0, t1 = SH.slab(a, b, lo, hi)
    span = np.clip(t1 - t0, 0.0, None) * length
    n = int(math.ceil(float(span.max(initial=0.0)) / step)) if span.size else 0
    if n == 0:
        return np.zeros(len(a))
    hits = np.zeros(len(a))
    for k in range(0, n, 256):
        s = (np.arange(k, min(n, k + 256)) + 0.0) / n
        tk = t0[:, None] + s[None, :] * (t1 - t0)[:, None]
        pts = a[:, None, :] + tk[:, :, None] * (b - a)[:, None, :]
        hits += self.inside(pts).sum(axis=1)
    return hits * span / n
for orth in (True, False):
    cam = camera(orth)
    good = ball.path_length(cam)
    SH.Volume.fine_samples = fine_at_start
    bad = ball.path_length(cam)
    SH.Volume.fine_samples = orig_fine
    print("fine step at its start, orthographic=%s: pixels changed %d of %d, largest change %.4f mm, silhouette pixels changed %d"
          % (orth, int((good != bad).sum()), good.size, float(np.abs(good - bad).max()), int(((good > 0) != (bad > 0)).sum())))

# fault 2: the slab test's refusal of a ray parallel to a face outside the box dropped
orig_slab = SH.slab
def slab_no_refusal(a, b, lo, hi):
    d = b - a
    parallel = d == 0
    with np.errstate(divide="ignore", invalid="ignore"):
        ta, tb = (lo - a) / d, (hi - a) / d
    near = np.where(parallel, -np.inf, np.minimum(ta, tb))
    far = np.where(parallel, np.inf, np.maximum(ta, tb))
    return np.clip(near.max(axis=1), 0.0, 1.0), np.clip(far.min(axis=1), 0.0, 1.0)
block = np.zeros((40, 40, 40), bool)
block[10:30, 12:26, 15:22] = True
vol = SH.Volume(block, np.eye(4))
for orth in (True, False):
    cam = PJ.Camera(PJ.View(rot_deg=(0.0, 0.0, 0.0), xyz_mm=(0.0, 800.0, 0.0), isocentre_mm=(20.0, 20.0, 20.0),
                            sdd=1200.0, delx=1.0, height=60, width=60, orthographic=orth))
    for kw in ({}, {"n_samples": 500}):
        good = vol.path_length(cam, **kw)
        SH.slab = slab_no_refusal
        bad = vol.path_length(cam, **kw)
        SH.slab = orig_slab
        print("slab refusal dropped, orthographic=%s %s: pixels changed %d, largest change %.6f mm"
              % (orth, kw or "fine", int((good != bad).sum()), float(np.abs(good - bad).max())))

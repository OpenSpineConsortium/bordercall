"""How far the fine-step-at-start fault moves each path length: in mm, in the ray's own steps, and
against the test's bounds."""
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

def chords(cam, radius):
    src, det = cam.rays(cam.pixel_centres())
    d = (det - src) / np.linalg.norm(det - src, axis=1, keepdims=True)
    w = centre - src
    perp = np.linalg.norm(w - (w * d).sum(axis=1, keepdims=True) * d, axis=1)
    return 2.0 * np.sqrt(np.clip(radius ** 2 - perp ** 2, 0.0, None))

orig_fine = SH.Volume.fine_samples
def make(offset):
    def fine(self, a, b, length, lo, hi, step):
        t0, t1 = SH.slab(a, b, lo, hi)
        span = np.clip(t1 - t0, 0.0, None) * length
        n = int(math.ceil(float(span.max(initial=0.0)) / step)) if span.size else 0
        if n == 0:
            return np.zeros(len(a))
        hits = np.zeros(len(a))
        for k in range(0, n, 256):
            s = (np.arange(k, min(n, k + 256)) + offset) / n
            tk = t0[:, None] + s[None, :] * (t1 - t0)[:, None]
            pts = a[:, None, :] + tk[:, :, None] * (b - a)[:, None, :]
            hits += self.inside(pts).sum(axis=1)
        # record the ray's own step for the probe
        fine.last_step = span / n
        return hits * span / n
    return fine

for orth in (True, False):
    cam = camera(orth)
    SH.Volume.fine_samples = make(0.5)
    good = ball.path_length(cam).ravel()
    SH.Volume.fine_samples = make(0.0)
    bad = ball.path_length(cam).ravel()
    SH.Volume.fine_samples = orig_fine
    d = np.abs(good - bad)
    step = 0.25
    low = chords(cam, R - math.sqrt(3) / 2 * h) - step
    high = chords(cam, R + math.sqrt(3) / 2 * h) + step
    print("orthographic=%s: changed %d; >0.25 mm %d; >0.5 mm %d; max %.4f" % (orth, int((d > 0).sum()), int((d > 0.25 + 1e-12).sum()), int((d > 0.5 + 1e-12).sum()), d.max()))
    # in units of the ray's step (all rays share one chunk here, so n is one number; step_i = span_i / n)
    nz = good > 0
    print("   good within bounds:", bool(((good >= low - 1e-9) & (good <= high + 1e-9)).all()),
          " bad within bounds:", bool(((bad >= low - 1e-9) & (bad <= high + 1e-9)).all()))
    # how close the bad gets to the bounds, in mm
    print("   least room to the low bound good %.4f bad %.4f; to the high bound good %.4f bad %.4f" % (
        float((good - low)[nz | (bad > 0)].min()), float((bad - low)[nz | (bad > 0)].min()),
        float((high - good).min()), float((high - bad).min())))
    exact = chords(cam, R)
    inner = chords(cam, R - 1.0) > 0
    print("   median |err| inner good %.4f bad %.4f (limit %.2f)" % (float(np.median(np.abs(good - exact)[inner])), float(np.median(np.abs(bad - exact)[inner])), h))
    print("   mean signed err over all rays good %.5f bad %.5f; sum good %.3f bad %.3f" % (float((good - exact).mean()), float((bad - exact).mean()), good.sum(), bad.sum()))
    hist = np.histogram(d[d > 0], bins=[0, 0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6])
    print("   histogram of changes (mm):", list(zip(hist[1][:-1].round(2), hist[0])))

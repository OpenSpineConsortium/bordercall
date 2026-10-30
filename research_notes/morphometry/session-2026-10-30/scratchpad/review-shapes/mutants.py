"""Each mutant patches morphoview.shapes at run time; the tests are run against it and the verdict
printed: KILLED where a test fails, SURVIVED where every test passes."""
import io, math, sys, unittest
import numpy as np
from scipy import ndimage
from morphoview import shapes as SH
from morphoview import projection as PJ

ORIG = {name: getattr(SH, name) for name in dir(SH)}
ORIG_CLS = {(c, k): v for c in (SH.Curve, SH.Plane, SH.Polygon, SH.Volume, SH.Curve2D) for k, v in vars(c).items() if not k.startswith('__')}

def restore():
    for name, v in ORIG.items():
        setattr(SH, name, v)
    for (c, k), v in ORIG_CLS.items():
        setattr(c, k, v)

def m_resampled_ignores_step():
    SH.Curve.resampled = lambda self, step: SH.Curve(self.points, self.closed)

def m_resampled_drops_corners():
    def resampled(self, step):
        pts = np.vstack([self.points, self.points[:1]]) if self.closed else self.points
        s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
        n = max(2, int(math.ceil(s[-1] / step)) + 1)
        u = np.linspace(0, s[-1], n)
        out = np.stack([np.interp(u, s, pts[:, k]) for k in range(3)], 1)
        return SH.Curve(out[:-1] if self.closed else out, self.closed)
    SH.Curve.resampled = resampled

def m_fine_uses_sdd():
    orig = ORIG_CLS[(SH.Volume, "path_length")]
    def path_length(self, camera, step=None, n_samples=None, chunk=4096):
        if n_samples is not None:
            return orig(self, camera, step, n_samples, chunk)
        out = np.zeros((camera.view.height, camera.view.width))
        pix = self.footprint(camera)
        to_voxel = np.linalg.inv(self.affine)
        lo, hi = self.box()
        for i in range(0, len(pix), chunk):
            part = pix[i:i + chunk]
            src, tgt = camera.rays(part[:, ::-1] + 0.5)
            a = src @ to_voxel[:3, :3].T + to_voxel[:3, 3]
            b = tgt @ to_voxel[:3, :3].T + to_voxel[:3, 3]
            length = np.full(len(a), camera.view.sdd)     # the mutant: every ray as long as the axis
            out[part[:, 0], part[:, 1]] = self.fine_samples(a, b, length, lo, hi, step or 0.5 * float(self.spacing.min()))
        return out
    SH.Volume.path_length = path_length

def m_seen_at_uses_beam():
    SH.Plane.seen_at_deg = lambda self, camera: math.degrees(math.asin(min(1.0, abs(float(camera.beam @ self.normal)))))

def m_largest_any_touch():
    @classmethod
    def from_labels(cls, labels, affine, value, largest=True):
        mask = np.isin(np.asarray(labels), np.atleast_1d(value))
        if largest and mask.any():
            parts, n = ndimage.label(mask, structure=np.ones((3, 3, 3)))   # the mutant: 26-connected
            if n > 1:
                sizes = np.bincount(parts.ravel()); sizes[0] = 0
                mask = parts == int(np.argmax(sizes))
        return cls(mask, affine)
    SH.Volume.from_labels = from_labels

def m_inside_floor():
    def inside(self, ijk):
        idx = np.floor(ijk).astype(np.int64)
        shape = np.array(self.mask.shape)
        ok = np.all((idx >= 0) & (idx < shape), axis=-1)
        hit = np.zeros(idx.shape[:-1], bool)
        hit[ok] = self.mask[idx[ok][:, 0], idx[ok][:, 1], idx[ok][:, 2]]
        return hit
    SH.Volume.inside = inside

def m_inside_round_half_up():
    def inside(self, ijk):
        idx = np.floor(np.asarray(ijk) + 0.5).astype(np.int64)
        shape = np.array(self.mask.shape)
        ok = np.all((idx >= 0) & (idx < shape), axis=-1)
        hit = np.zeros(idx.shape[:-1], bool)
        hit[ok] = self.mask[idx[ok][:, 0], idx[ok][:, 1], idx[ok][:, 2]]
        return hit
    SH.Volume.inside = inside

def m_fine_left_ends():
    def fine_samples(self, a, b, length, lo, hi, step):
        t0, t1 = SH.slab(a, b, lo, hi)
        span = np.clip(t1 - t0, 0.0, None) * length
        n = int(math.ceil(float(span.max(initial=0.0)) / step)) if span.size else 0
        if n == 0:
            return np.zeros(len(a))
        s = np.arange(n) / n                                # the mutant: each step's start, not its middle
        tk = t0[:, None] + s[None, :] * (t1 - t0)[:, None]
        pts = a[:, None, :] + tk[:, :, None] * (b - a)[:, None, :]
        return self.inside(pts).sum(axis=1) * span / n
    SH.Volume.fine_samples = fine_samples

def m_fine_full_voxel_step():
    orig = ORIG_CLS[(SH.Volume, "path_length")]
    SH.Volume.path_length = lambda self, camera, step=None, n_samples=None, chunk=4096: orig(
        self, camera, step or float(self.spacing.min()), n_samples, chunk)

def m_length_px_open():
    def length_px(self):
        return float(sum(np.linalg.norm(np.diff(p, axis=0), axis=1).sum() for p in self.pieces()))
    SH.Curve2D.length_px = length_px

def m_patch_ignores_toward_sign():
    orig = ORIG_CLS[(SH.Plane, "patch")]
    SH.Plane.patch = lambda self, half_a, half_b, toward=None: orig(self, half_b, half_a, toward)

def m_fit_rms_dof():
    @classmethod
    def fit(cls, points):
        pts = np.atleast_2d(np.asarray(points, float))
        centre = pts.mean(axis=0)
        _, sv, vt = np.linalg.svd(pts - centre, full_matrices=False)
        if not sv[1] > 1e-12 * max(1.0, float(sv[0])):
            raise ValueError("the points lie on one line")
        return cls(centre, vt[2]), float(sv[2] / math.sqrt(len(pts) - 3))
    SH.Plane.fit = fit

def m_circle_negative_radius_ok():
    pass  # no mutant: the original is the subject (a check of the suite, not of a mutant)

def m_no_closed_merge():
    orig = ORIG["in_front"]
    def in_front(segments, camera, closed):
        return orig(segments, camera, False) if closed and not camera.view.orthographic else orig(segments, camera, closed)
    SH.in_front = in_front

def m_project_points_cone_only():
    pass

MUTANTS = [m_resampled_ignores_step, m_resampled_drops_corners, m_fine_uses_sdd, m_seen_at_uses_beam,
           m_largest_any_touch, m_inside_floor, m_inside_round_half_up, m_fine_left_ends, m_fine_full_voxel_step,
           m_length_px_open, m_patch_ignores_toward_sign, m_fit_rms_dof, m_no_closed_merge]

def run(suite_names):
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for n in suite_names:
        suite.addTests(loader.loadTestsFromName(n))
    res = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    return res

if __name__ == "__main__":
    names = sys.argv[1:] or ["morphoview.tests.test_shapes"]
    for m in MUTANTS:
        restore(); m()
        res = run(names)
        bad = [t.id().rsplit(".", 1)[-1] for t, _ in res.failures + res.errors]
        print("%-32s %s %s" % (m.__name__, "KILLED  " if bad else "SURVIVED", bad[:3]))
    restore()

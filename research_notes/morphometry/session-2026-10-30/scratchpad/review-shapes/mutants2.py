import sys
import numpy as np
sys.path.insert(0, "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/review-shapes")
import mutants as MU
from morphoview import shapes as SH

def m_inside_axes_reversed():
    def inside(self, ijk):
        idx = np.rint(ijk).astype(np.int64)[..., ::-1]           # the mutant: k, j, i read as i, j, k
        shape = np.array(self.mask.shape)
        ok = np.all((idx >= 0) & (idx < shape), axis=-1)
        hit = np.zeros(idx.shape[:-1], bool)
        hit[ok] = self.mask[idx[ok][:, 0], idx[ok][:, 1], idx[ok][:, 2]]
        return hit
    SH.Volume.inside = inside

def m_flexray_is_fine():
    orig = MU.ORIG_CLS[(SH.Volume, "path_length")]
    SH.Volume.path_length = lambda self, camera, step=None, n_samples=None, chunk=4096: orig(self, camera, step, None, chunk)

def m_flexray_midpoints():
    def flexray_samples(self, a, b, length, n, lo, hi):
        t = (np.arange(n) + 0.5) / n                              # the mutant: n midpoints, not n points end to end
        hits = np.zeros(len(a))
        for j in range(0, n, 128):
            tt = t[j:j + 128]
            pts = a[:, None, :] + tt[None, :, None] * (b - a)[:, None, :]
            hits += self.inside(pts).sum(axis=1)
        return hits * length / (n - 1)
    SH.Volume.flexray_samples = flexray_samples

def m_inside_one_voxel_wider():
    def inside(self, ijk):
        from scipy import ndimage
        wide = ndimage.binary_dilation(self.mask)
        idx = np.rint(ijk).astype(np.int64)
        shape = np.array(self.mask.shape)
        ok = np.all((idx >= 0) & (idx < shape), axis=-1)
        hit = np.zeros(idx.shape[:-1], bool)
        hit[ok] = wide[idx[ok][:, 0], idx[ok][:, 1], idx[ok][:, 2]]
        return hit
    SH.Volume.inside = inside

if __name__ == "__main__":
    for m in (m_inside_axes_reversed, m_flexray_is_fine, m_flexray_midpoints, m_inside_one_voxel_wider):
        for names in (["morphoview.tests.test_shapes"],
                      ["morphoview.tests.test_projection.Shadows", "morphoview.tests.test_projection.Pieces"]):
            MU.restore(); m()
            res = MU.run(names)
            bad = [t.id().rsplit(".", 1)[-1] for t, _ in res.failures + res.errors]
            print("%-28s %-22s %s %s" % (m.__name__, names[0].rsplit(".", 1)[-1], "KILLED  " if bad else "SURVIVED", bad[:3]))
    MU.restore()

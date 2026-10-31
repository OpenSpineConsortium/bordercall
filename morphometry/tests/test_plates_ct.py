"""The plate readings (plates.py) and the canal read on a CT (ct_canal.py), on the straight lumbar
phantom of test_morphometry: each plate's width and depth land within TOL_MM of the phantom's; a
CT drawn from the phantom's own label (bone 1000 HU, all else 0) gives the canal's width between
the pedicles' least and greatest interpedicular distances and its depth between the phantom's least
and greatest midline depth over the enclosed planes, within TOL_MM; and with no CT the canal's two
CT readings are not taken."""
import math
import unittest

import numpy as np

from morphometry import ct_canal as CTC, measure as M
from morphometry.tests import phantom as P
from morphometry.tests.test_morphometry import LUMBAR, TOL_MM
from scanimport import geometry as G

DRAW = dict(spacing=(0.8, 0.8, 1.0), grid_turn=((0.0, 0.0, 1.0), 7.0))


def rows_of(v, with_ct):
    lab, aff = P.draw(P.straight(LUMBAR, v), **DRAW)
    grid = G.VoxelGrid(aff, lab.shape)
    names = {P.LEVEL_IDS[lv]: lv for lv in LUMBAR}
    ct = (np.where(lab > 0, 1000.0, 0.0).astype(np.float32), np.linalg.inv(aff)) if with_ct else None
    out = {}
    for r in M.measure_volume(lab, grid, names, "phantom", pelvis=False, ct=ct):
        out.setdefault(r["level"], {})[r["key"]] = r["value"] if not r["key"].startswith("flag") else r["note"]
    return out


class Plates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v = P.Vert()
        cls.rows = rows_of(cls.v, with_ct=True)
        cls.truth = P.truth(cls.v)

    def test_widths_and_depths(self):
        for got, want in (("plate_w", "endplate"), ("plate_w_lower", "endplate_lower"),
                          ("plate_d", "endplate_depth"), ("plate_d_lower", "endplate_lower_depth")):
            value = self.rows["L3"][got]
            self.assertTrue(np.isfinite(value), got)
            self.assertLessEqual(abs(value - self.truth[want]), TOL_MM, "%s %.2f against %.2f" % (got, value, self.truth[want]))

    def test_canal_on_the_ct(self):
        w, d = self.rows["L3"]["canal_w_ct"], self.rows["L3"]["canal_ap_ct"]
        lo, hi = self.truth["interpedicular"], self.truth["interpedicular_max"]
        self.assertTrue(lo - TOL_MM <= w <= hi + TOL_MM, "canal_w_ct %.2f outside %.2f to %.2f" % (w, lo, hi))
        depths = [P.canal_ap_at(self.v, z) for z in np.linspace(0.0, self.v.Hp, 40)]
        depths = [x for x in depths if math.isfinite(x)]
        self.assertTrue(min(depths) - TOL_MM <= d <= max(depths) + TOL_MM,
                        "canal_ap_ct %.2f outside %.2f to %.2f" % (d, min(depths), max(depths)))

    def test_no_ct_no_reading(self):
        rows = rows_of(self.v, with_ct=False)
        self.assertTrue(math.isnan(rows["L3"]["canal_w_ct"]))
        self.assertTrue(math.isnan(rows["L3"]["canal_ap_ct"]))


class CanalPlane(unittest.TestCase):
    def test_an_open_ring_is_not_read(self):
        img = np.zeros((80, 80), np.float32)
        img[10:70, 10:12] = img[10:70, 68:70] = img[10:12, 10:70] = 1000.0   # three sides of a ring
        self.assertIsNone(CTC.canal_in_plane(img, (40, 40)))
        img[68:70, 10:70] = 1000.0
        w, d = CTC.canal_in_plane(img, (40, 40))
        self.assertAlmostEqual(w, 56 * CTC.STEP_MM)
        self.assertAlmostEqual(d, 56 * CTC.STEP_MM)


if __name__ == "__main__":
    unittest.main()

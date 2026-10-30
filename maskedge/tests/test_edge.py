"""The mask-edge reading on the morphometry phantom: L2 to L4 drawn as ENHANCE.PET-style labels at
0.8 by 0.8 by 1 mm, tilted 18 degrees, with a CT drawn for L3 from the same shapes, each voxel the
mean of 27 points inside it (a cortex 0.8 mm deep at 800 HU over cancellous bone at 200, soft
tissue at 40) and blurred as a scanner blurs (sigma 0.45 mm across, 0.55 along the column).
The exact mask, the mask grown by one voxel and the mask shrunk by one voxel are read against
that CT. A one-voxel growth through faces moves a surface whose normal is n by the largest of
|n_i| times the spacing along axis i, the support of the face cross, so that is the shift each
region must show."""
import math
import unittest

import numpy as np
from scipy import ndimage

from maskedge import edge as E
from morphometry.tests import phantom as P
from scanimport import geometry as G

LEVELS = ["L2", "L3", "L4"]
SPACING = np.array([0.8, 0.8, 1.0])
PSF_MM = np.array([0.45, 0.45, 0.55])
CORTEX_MM = 0.8
HU = {"outside": 40.0, "cancellous": 200.0, "cortex": 800.0}
SUB = 3
EXACT_MM = 0.5
SHIFT_TOL_MM = 0.3


def ct_for(placed: P.Placed, lab: np.ndarray, aff: np.ndarray) -> np.ndarray:
    """The CT of the placed vertebra on the label's grid, the rest of the column flat bone."""
    ct = np.where(lab > 0, HU["cancellous"], HU["outside"]).astype(np.float32)
    mine = lab == P.LEVEL_IDS[placed.level]
    near = ndimage.binary_dilation(mine, iterations=3) & ~ndimage.binary_erosion(mine, iterations=3)
    at = np.argwhere(near).astype(float)
    a3, t = aff[:3, :3], aff[:3, 3]
    grid = np.stack(np.meshgrid(*[np.arange(SUB)] * 3, indexing="ij"), -1).reshape(-1, 3)
    offsets = (grid + 0.5) / SUB - 0.5
    probes = CORTEX_MM * np.vstack([np.eye(3), -np.eye(3)])
    inside_of = lambda w: P.solid((w - placed.c) @ placed.R, placed.v)  # noqa: E731
    total = np.zeros(len(at))
    for o in offsets:
        w = (at + o) @ a3.T + t
        inside = inside_of(w)
        shell = np.zeros(len(w), bool)
        for d in probes:
            shell |= ~inside_of(w + d)
        total += np.where(inside, np.where(shell, HU["cortex"], HU["cancellous"]), HU["outside"])
    ct[tuple(at.astype(int).T)] = total / len(offsets)
    return ndimage.gaussian_filter(ct, PSF_MM / SPACING)


def by_region(rows, level="L3"):
    return {r["region"]: r for r in rows if r["level"] == level}


class Phantom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        placed = P.straight(LEVELS, P.Vert())
        cls.lab, aff = P.draw(placed, spacing=tuple(SPACING))
        cls.grid = G.VoxelGrid(aff, cls.lab.shape)
        cls.names = {P.LEVEL_IDS[lv]: lv for lv in LEVELS}
        cls.ct = ct_for(placed[1], cls.lab, aff)
        cls.v = E.vertebrae(cls.lab, cls.grid, cls.names)["L3"]
        cls.exact = by_region(E.measure_arrays(cls.ct, cls.lab, cls.grid, cls.names, "exact"))
        l3 = P.LEVEL_IDS["L3"]
        grown = cls.lab.copy()
        grown[ndimage.binary_dilation(cls.lab == l3) & (cls.lab == 0)] = l3
        shrunk = cls.lab.copy()
        shrunk[(cls.lab == l3) & ~ndimage.binary_erosion(cls.lab == l3)] = 0
        cls.grown = by_region(E.measure_arrays(cls.ct, grown, cls.grid, cls.names, "grown"))
        cls.shrunk = by_region(E.measure_arrays(cls.ct, shrunk, cls.grid, cls.names, "shrunk"))

    def support(self, region: str) -> float:
        f = self.v.frame
        d = {"upper_plate": f.ez, "lower_plate": f.ez, "lateral_wall": f.ex, "anterior_wall": f.ey,
             "posterior_wall": f.ey}[region]
        return float(np.max(np.abs(self.grid.axes.T @ d) * self.grid.spacing))

    def test_every_region_reads_most_of_its_points(self):
        for name in E.REGIONS:
            r = self.exact[name]
            self.assertGreaterEqual(r["edges"], 0.75 * r["points"], name)

    def test_an_exact_mask_lies_on_the_bone(self):
        for name in E.REGIONS:
            self.assertLess(abs(self.exact[name]["offset_median"]), EXACT_MM, name)

    def test_a_grown_mask_reads_one_voxel_beyond_the_bone(self):
        for name in E.REGIONS[:-1]:
            shift = self.grown[name]["offset_median"] - self.exact[name]["offset_median"]
            self.assertAlmostEqual(shift, -self.support(name), delta=SHIFT_TOL_MM, msg=name)

    def test_a_shrunk_mask_reads_one_voxel_inside_the_bone(self):
        for name in E.REGIONS[:-1]:
            shift = self.shrunk[name]["offset_median"] - self.exact[name]["offset_median"]
            self.assertAlmostEqual(shift, self.support(name), delta=SHIFT_TOL_MM, msg=name)

    def test_a_flat_ct_shows_no_edge(self):
        flat = np.full(self.lab.shape, HU["outside"], np.float32)
        rows = by_region(E.measure_arrays(flat, self.lab, self.grid, self.names, "flat"))
        for name in E.REGIONS:
            self.assertEqual(rows[name]["edges"], 0, name)
            self.assertTrue(math.isnan(rows[name]["offset_median"]), name)


class Summary(unittest.TestCase):
    def test_what_the_offsets_make_of_each_measure(self):
        rows = [{"region": "upper_plate", "offset_median": -1.0}, {"region": "lower_plate", "offset_median": -0.5},
                {"region": "lateral_wall", "offset_median": -0.25}, {"region": "anterior_wall", "offset_median": 0.5},
                {"region": "posterior_wall", "offset_median": "nan"}, {"region": "arch", "offset_median": 0.0}]
        got = E.summary(rows)
        self.assertAlmostEqual(got["implied"]["height"], 1.5)
        self.assertAlmostEqual(got["implied"]["disc"], -1.5)
        self.assertAlmostEqual(got["implied"]["width"], 0.5)
        self.assertNotIn("posterior_wall", got)
        self.assertTrue(math.isnan(got["implied"]["depth"]))


class Crossing(unittest.TestCase):
    def test_a_step_falls_through_its_level_between_samples(self):
        s = np.array([0.0, 0.2, 0.4, 0.6])
        prof = np.array([[1.0, 1.0, 0.0, 0.0], [1.0, 0.75, 0.25, 0.0]])
        got = E.crossing(prof, s, np.array([0.5, 0.5]), np.array([0, 0]))
        np.testing.assert_allclose(got, [0.3, 0.3])

    def test_no_fall_is_no_crossing(self):
        got = E.crossing(np.ones((1, 4)), np.arange(4.0), np.array([0.5]), np.array([0]))
        self.assertTrue(math.isnan(got[0]))


if __name__ == "__main__":
    unittest.main()

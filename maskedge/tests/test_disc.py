"""The disc reading on the morphometry phantom: L2 to L4 with a 10 mm disc between each pair,
drawn at 0.8 by 0.8 by 1 mm, with the CT test_edge.py draws (L3 with its cortex, the others flat
bone, the discs soft tissue). The exact masks leave the true gap and the CT shows it; L3's mask
grown by one voxel narrows both of its discs by one voxel along the column and leaves the CT as
it was, so the difference reads the voxel, and shrunk by one widens them by as much.

    python -m unittest maskedge.tests.test_disc   (from the repository's root, about a minute)"""
import unittest

import numpy as np
from scipy import ndimage

from maskedge import disc as D
from maskedge.tests import test_edge as T
from morphometry.tests import phantom as P
from scanimport import geometry as G

GAP_TOL_MM = 0.3
CT_TOL_MM = 0.5


class Phantom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        placed = P.straight(T.LEVELS, P.Vert())
        lab, aff = P.draw(placed, spacing=tuple(T.SPACING))
        grid = G.VoxelGrid(aff, lab.shape)
        names = {P.LEVEL_IDS[lv]: lv for lv in T.LEVELS}
        ct = T.ct_for(placed[1], lab, aff)
        cls.truth = P.Joint().gap
        cls.exact = {r["disc"]: r for r in D.measure_arrays(ct, lab, grid, names, "exact")}
        l3 = P.LEVEL_IDS["L3"]
        grown = lab.copy()
        grown[ndimage.binary_dilation(lab == l3) & (lab == 0)] = l3
        cls.grown = {r["disc"]: r for r in D.measure_arrays(ct, grown, grid, names, "grown")}
        shrunk = lab.copy()
        shrunk[(lab == l3) & ~ndimage.binary_erosion(lab == l3)] = 0
        cls.shrunk = {r["disc"]: r for r in D.measure_arrays(ct, shrunk, grid, names, "shrunk")}
        cls.support = float(np.max(np.abs(grid.axes.T @ np.array([0.0, 0.0, 1.0])) * grid.spacing))

    def test_both_discs_read_on_most_lines(self):
        for d in ("L2-L3", "L3-L4"):
            self.assertIn(d, self.exact)
            self.assertGreaterEqual(self.exact[d]["read"], 0.8 * self.exact[d]["lines"], d)

    def test_exact_masks_leave_the_true_gap(self):
        """A voxel is labelled where its centre lies inside, so each drawn surface lies within half a
        voxel of the true one and the gap within one voxel along the column of the truth."""
        for d in ("L2-L3", "L3-L4"):
            self.assertAlmostEqual(self.exact[d]["masks_gap"], self.truth, delta=self.support, msg=d)

    def test_the_ct_shows_the_disc_the_exact_masks_leave(self):
        """L2 and L4 are drawn in the CT from their labels, so the CT's disc is the labels' own gap
        but for the half-maximum edge of L3's cortex, which test_edge.py finds 0.14 to 0.20 mm
        outside the surface."""
        for d in ("L2-L3", "L3-L4"):
            self.assertAlmostEqual(self.exact[d]["difference"], 0.0, delta=GAP_TOL_MM, msg=d)
            self.assertAlmostEqual(self.exact[d]["ct_height"], self.truth, delta=CT_TOL_MM + self.support / 2, msg=d)

    def test_a_grown_mask_reads_the_voxel_it_took(self):
        for d in ("L2-L3", "L3-L4"):
            moved = self.grown[d]["difference"] - self.exact[d]["difference"]
            self.assertAlmostEqual(moved, -self.support, delta=GAP_TOL_MM, msg=d)
            self.assertAlmostEqual(self.grown[d]["ct_height"], self.exact[d]["ct_height"], delta=0.15, msg=d)

    def test_a_shrunk_mask_reads_the_voxel_it_gave_up(self):
        for d in ("L2-L3", "L3-L4"):
            moved = self.shrunk[d]["difference"] - self.exact[d]["difference"]
            self.assertAlmostEqual(moved, self.support, delta=GAP_TOL_MM, msg=d)


if __name__ == "__main__":
    unittest.main()

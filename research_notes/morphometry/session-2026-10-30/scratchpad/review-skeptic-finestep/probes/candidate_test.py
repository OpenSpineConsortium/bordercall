"""A candidate test that would hold the fine sampling to its midpoints: a block's box is its
shadow's whole chord, so midpoints count every step of an axis-aligned parallel ray through it and
its path length is the block's depth exactly; a step counted by its start reads the box's face,
whose nearest voxel, rounded half to even, lies outside the block for one parity of its end."""
import unittest

import numpy as np

from morphoview import projection as PJ
from morphoview import shapes as SH


class FineMidpoints(unittest.TestCase):
    def test_an_axis_aligned_block_is_its_depth_exactly(self):
        h = 0.5
        affine = np.diag([h, h, h, 1.0])
        for y0, y1 in ((16, 30), (15, 29), (16, 29), (15, 30)):
            block = np.zeros((48, 48, 48), bool)
            block[14:34, y0:y1, 18:32] = True
            vol = SH.Volume(block, affine)
            for orth in (True, False):
                cam = PJ.Camera(PJ.View(rot_deg=(0.0, 0.0, 0.0), xyz_mm=(0.0, 800.0, 0.0),
                                        isocentre_mm=(12.13, 11.9, 12.21), sdd=1200.0, delx=0.7,
                                        height=48, width=48, orthographic=orth))
                got = vol.path_length(cam)
                if orth:
                    on = got > 0
                    np.testing.assert_allclose(got[on], (y1 - y0) * h, rtol=0, atol=1e-9,
                                               err_msg="block y %d:%d" % (y0, y1))


if __name__ == "__main__":
    unittest.main()

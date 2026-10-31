"""The stretched template of autoanatomist/template.py (bordercall #55): the stretch undoes itself,
folds nowhere and gives each measured region its own ratio exactly; a level made from a template
sets landmarks whose chords have the drawn lengths; and the oracle, reading the rendered column, finds
the drawn values to within a voxel.

    python -m unittest tests.test_autoanatomist_template -v      # from the repository's root, in the venv

The template is read at 0.75 mm over two phases of the lattice, coarser than the module's default, so
the test runs in about a minute; the module's own reading is finer.
"""
import unittest

import numpy as np

from autoanatomist import oracle as O
from autoanatomist import phantom as PH
from autoanatomist import specs as S
from autoanatomist import template as T

READ_MM = 0.75
TEMPLATE_TO_TRUTH_MM = 0.5     # the template's read values against its frustum's drawn ones
SET_GAP_MM = 0.05              # a set chord against its drawn length
READBACK_MM = 1.0              # the oracle on the rendered column against the drawn value


def a_stretch(rng):
    ratio = {k: float(rng.uniform(0.75, 1.35)) for k in T.MEASURED}
    return T.Stretch(wall=-1.5, z_bot=-6.0, z_top=6.0, canal_x=9.0, ratio=ratio)


def gaps(st, p, q):
    """The gap between two points along each axis after the stretch, over the gap before."""
    return (st.forward(p[None])[0] - st.forward(q[None])[0]) / (p - q)


class TheStretch(unittest.TestCase):
    def test_inverse_undoes_forward(self):
        rng = np.random.default_rng(3)
        for _ in range(10):
            st = a_stretch(rng)
            p = rng.uniform(-30.0, 30.0, size=(500, 3))
            np.testing.assert_allclose(st.inverse(st.forward(p)), p, atol=1e-6)

    def test_folds_nowhere(self):
        rng = np.random.default_rng(4)
        for _ in range(10):
            st = a_stretch(rng)
            p = rng.uniform(-30.0, 30.0, size=(2000, 3))
            self.assertGreater(st.jacobian_det(p).min(), T.FOLD_FLOOR)

    def test_each_region_takes_its_ratio(self):
        st = a_stretch(np.random.default_rng(5))
        r, front, back = st.ratio, st.wall + 2.0, st.wall - 6.0
        top = gaps(st, np.array([8.0, front + 9.0, 12.0]), np.array([-5.0, front, 10.0]))
        self.assertAlmostEqual(top[0], r["endplate"], places=9)
        self.assertAlmostEqual(top[1], r["endplate_depth"], places=9)
        bottom = gaps(st, np.array([8.0, front + 9.0, -12.0]), np.array([-5.0, front, -10.0]))
        self.assertAlmostEqual(bottom[0], r["endplate_lower"], places=9)
        self.assertAlmostEqual(bottom[1], r["endplate_lower_depth"], places=9)
        self.assertAlmostEqual(top[2], r["h_post"], places=9)
        canal = gaps(st, np.array([5.0, back - 7.0, 1.0]), np.array([-6.0, back, 3.0]))
        self.assertAlmostEqual(canal[0], r["canal_w"], places=9)
        self.assertAlmostEqual(canal[1], r["canal_ap"], places=9)
        self.assertAlmostEqual(canal[2], r["h_post"], places=9)


class AStretchedLevel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = PH.draw_levels("typical", seed=1, start="L1", count=3)
        cls.base = base[1]
        cls.template = T.template_from(base, 1, spacing=READ_MM, phases=2)
        drawn = PH.draw_levels("typical", seed=2, start="L1", count=3)
        cls.drawn = drawn[1]
        cls.column = [drawn[0], T.warp(cls.template, drawn[1]), drawn[2]]

    def test_the_template_reads_its_frustum(self):
        truth = self.base.truth()
        for k in T.MEASURED:
            self.assertLess(abs(self.template.values[k] - truth[k]), TEMPLATE_TO_TRUTH_MM, k)

    def test_set_chords_have_the_drawn_lengths(self):
        truth, found = self.drawn.truth(), T.set_values(self.column[1].shape)
        for k in T.MEASURED:
            self.assertLess(abs(found[k] - truth[k]), SET_GAP_MM, k)

    def test_the_level_folds_nowhere(self):
        self.assertGreater(T.folds(self.column[1]), T.FOLD_FLOOR)

    def test_the_oracle_reads_the_drawn_values(self):
        ph = PH.render(self.column, spacing=(READ_MM,) * 3, sub=1, with_ct=False)
        reading = O.ChordOracle(S.SEVEN).read(ph.labels, ph.affine, ph.names)[1]
        truth = self.drawn.truth()
        for k in S.SEVEN:
            self.assertLess(abs(reading.measurements[k].value - truth[k]), READBACK_MM, k)

    def test_set_landmarks_land_in_the_world_frame(self):
        ph = PH.render(self.column, spacing=(1.5,) * 3, sub=1, with_ct=False)
        world = T.landmarks_world(ph, 1)
        self.assertEqual(set(world), set(self.column[1].shape.points))
        for k in T.MEASURED:
            a, b = (world[n] for n in S.SPECS[k].points)
            self.assertAlmostEqual(float(np.linalg.norm(a - b)), T.set_values(self.column[1].shape)[k], places=6)


if __name__ == "__main__":
    unittest.main()

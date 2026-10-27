"""The chords on synthetic spines with known chords: tilted, turned, prone, thick-sliced and
cervical-sized, in whole-vertebra and SPINEPS-subregion labels. Each chord must land within one
voxel's shadow on its axis of the truth, and never worse than TOLERANCE_MM where that shadow is
smaller (a chord's two surfaces each carry up to half a shadow)."""
import math
import unittest

import numpy as np

from scanimport import geometry as G
from scanimport import schemes, volume as V
from scanimport.tests import phantom as PH

LEVELS = ["T12", "L1", "L2"]
IDS = {lv: v for v, lv in schemes.VERSE.items() if lv in LEVELS}
NAMES = {v: lv for lv, v in IDS.items()}
TOLERANCE_MM = 0.75
SPINOUS_MM = 1.0
CERVICAL = PH.Shape(W=17, D=15, H=13, CW=24, CD=14, T=3, TP=52, LS=14)
CONFIGS = {
    "aligned 1 mm": dict(tilt=((1, 0, 0), 0.0), grid_turn=((0, 0, 1), 0.0), spacing=(1, 1, 1)),
    "thick 3 mm slices, tilted 25": dict(tilt=((1, 0.2, 0), 25.0), spacing=(0.7, 0.7, 3.0), grid_turn=((0, 0, 1), 0.0)),
    "prone": dict(tilt=((1, 0, 0), 192.0), grid_turn=((0, 0, 1), 5.0)),
    "middle body turned 20": dict(turns={"L1": 20.0}),
    "cervical sizes": dict(shape=CERVICAL, gap=18.0, spacing=(0.6, 0.6, 1.0)),
}
AXIS = {"endplate": "x", "endplate_lower": "x", "canal_w": "x", "tp_span": "x", "endplate_depth": "y",
        "endplate_lower_depth": "y", "canal_ap": "y", "h_post": "z"}


def truth(s):
    return dict(endplate=s.W, endplate_depth=s.D, endplate_lower=s.W, endplate_lower_depth=s.D, h_post=s.H,
                canal_w=s.CW, canal_ap=s.CD, tp_span=s.TP, spinous_length=PH.spinous_reach(s))


def shadow(grid, kw, level, measure):
    """One voxel's shadow on the chord's axis in the vertebra's true frame."""
    R = PH.rotation(*kw.get("tilt", ((1.0, 0.3, 0.0), 18.0))) @ PH.rotation((0, 0, 1), kw.get("turns", {}).get(level, 0.0))
    return grid.footprint(R[:, "xyz".index(AXIS[measure])])


class Chords(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {}
        for name, kw in CONFIGS.items():
            lab, aff, sub, ez = PH.column(LEVELS, IDS, margin=12.0, subregions=True, **kw)
            cls.cases[name] = (lab, G.VoxelGrid(aff, lab.shape), sub, kw.get("shape", PH.Shape()))

    def check(self, name, sub_on):
        lab, grid, sub, shape = self.cases[name]
        bodies = V.measure_volume(lab, grid, NAMES, sub if sub_on else None)
        self.assertEqual([b.level for b in bodies], LEVELS)
        for b in bodies:
            self.assertEqual(b.flags, {}, "%s %s" % (name, b.level))
        for m, t in truth(shape).items():
            for b in bodies:
                tol = SPINOUS_MM if m == "spinous_length" else max(TOLERANCE_MM, shadow(grid, CONFIGS[name], b.level, m))
                with self.subTest(case=name, labels="subregions" if sub_on else "whole", level=b.level, measure=m):
                    self.assertLessEqual(abs(b.values[m] - t), tol, "%s %.2f, truth %.2f" % (m, b.values[m], t))

    def test_whole_vertebra_labels(self):
        for name in CONFIGS:
            self.check(name, False)

    def test_spineps_subregions(self):
        for name in CONFIGS:
            self.check(name, True)


class Surfaces(unittest.TestCase):
    def test_edge_gap_on_a_grid_axis_and_off_it(self):
        on = np.arange(0.0, 20.0, 1.5)
        self.assertAlmostEqual(G.edge_gap(on, True, 1.5), 1.5)
        self.assertAlmostEqual(G.extent(on, 1.5), on.max() - on.min() + 1.5)
        rng = np.random.default_rng(0)
        off = np.sort(rng.uniform(0, 20, 400))
        self.assertLess(G.edge_gap(off, True, 1.5), 0.3)

    def test_extent_needs_enough_points(self):
        self.assertTrue(math.isnan(G.extent(np.arange(3.0), 1.0)))


class Cut(unittest.TestCase):
    def test_a_vertebra_cut_by_the_field_of_view_loses_its_cut_chords(self):
        lab, aff, sub, ez = PH.column(LEVELS, IDS, margin=12.0, tilt=((1, 0, 0), 0.0), grid_turn=((0, 0, 1), 0.0),
                                      spacing=(1.2, 1.2, 1.2))
        grid = G.VoxelGrid(aff, lab.shape)
        x_mid = int(np.argwhere(lab > 0)[:, 0].mean())
        cut = lab[x_mid - 10:].copy()                       # the patient's right side is out of the field
        aff2 = aff.copy()
        aff2[:3, 3] = grid.world(np.array([[x_mid - 10.0, 0.0, 0.0]]))[0]
        bodies = V.measure_volume(cut, G.VoxelGrid(aff2, cut.shape), NAMES, None)
        for b in bodies:
            self.assertTrue(math.isnan(b.values.get("tp_span", math.nan)))
            self.assertTrue(math.isnan(b.values.get("endplate", math.nan)))
            self.assertIn(b.flags.get("tp_span", b.flags.get("all", "")).split()[0], ("the", "no", "a"))


if __name__ == "__main__":
    unittest.main()

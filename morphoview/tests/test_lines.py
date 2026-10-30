"""The drawings on the morphometry phantom: L2 to L4 at 0.8 by 0.8 by 1 mm, whose solids are known.

Every line built for L3 and its two discs must give the value the measuring code gives, so all are
drawn; each length's ends must lie on the surface it is said to end at, a step inward on one side
of it and a step outward on the other, the step under a voxel's diagonal; a median is drawn in the
reading nearest it; a value off by more than the rows' rounding is withheld; and the four panels
draw with one key line for each drawn line."""
import math
import os
import tempfile
import unittest

import numpy as np

from maskedge import edge as E
from morphometry import column as COL
from morphometry import measure as M
from morphometry.tests import phantom as P
from morphoview import lines as LN
from morphoview import render as R
from scanimport import geometry as G

LEVELS = ["L2", "L3", "L4"]
STEP_MM = 0.8
# the lines that end where bone gives way to what is outside it, and the side bone lies on
BONE_WITHIN = ("h_ant", "h_mid", "h_post_inset", "h_post", "body_d_mid", "body_w_mid", "endplate", "endplate_lower",
               "tp_span", "pedicle_chord_right", "pedicle_chord_left")
CANAL_WITHIN = ("canal_ap_min", "interpedicular", "canal_w", "canal_ap")
# a median is drawn in the row, cell or section whose reading is nearest it: on this phantom the
# canal's depth runs from 16.0 to 19.5 mm over the band it is read in and the section drawn reads
# 0.07 mm over the median, the furthest of any median's line from its value
MEDIAN_MM = 0.1


class Phantom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.placed = {p.level: p for p in P.straight(LEVELS, P.Vert())}
        cls.lab, aff = P.draw(list(cls.placed.values()), spacing=(0.8, 0.8, 1.0))
        cls.names = {P.LEVEL_IDS[lv]: lv for lv in LEVELS}
        cls.vs = E.vertebrae(cls.lab, G.VoxelGrid(aff, cls.lab.shape), cls.names)
        v = cls.vs["L3"]
        vals, _, ped = M.vertebra_values(v)
        cls.lines = LN.checked(LN.vertebra_lines(v, ped), vals)
        for up, low in (("L2", "L3"), ("L3", "L4")):
            cls.lines += LN.checked(LN.discs(cls.vs[up], cls.vs[low]), COL.disc_heights(cls.vs[up], cls.vs[low]))

    def inside(self, level: str, w: np.ndarray) -> bool:
        p = self.placed[level]
        return bool(P.solid(((np.atleast_2d(w) - p.c) @ p.R), p.v)[0])

    def by_key(self, key: str, level: str = "L3") -> LN.Line:
        return next(ln for ln in self.lines if ln.key == key and ln.level == level)

    def test_every_line_gives_its_measured_value(self):
        self.assertGreaterEqual(len(self.lines), 25)
        for ln in self.lines:
            self.assertEqual(ln.status, "drawn", "%s %s %s" % (ln.level, ln.key, ln.status))

    def test_a_length_is_the_distance_between_its_ends(self):
        for ln in self.lines:
            if ln.rule == "length":
                self.assertAlmostEqual(ln.drawn, ln.value, places=9, msg=ln.key)

    def test_bone_ends_lie_on_the_bone_surface(self):
        for key in BONE_WITHIN:
            ln = self.by_key(key)
            d = (ln.b - ln.a) / np.linalg.norm(ln.b - ln.a)
            for end, inward in ((ln.a, d), (ln.b, -d)):
                self.assertTrue(self.inside("L3", end + STEP_MM * inward), key)
                self.assertFalse(self.inside("L3", end - STEP_MM * inward), key)

    def test_canal_ends_lie_on_the_canal_wall(self):
        for key in CANAL_WITHIN:
            ln = self.by_key(key)
            d = (ln.b - ln.a) / np.linalg.norm(ln.b - ln.a)
            for end, inward in ((ln.a, d), (ln.b, -d)):
                self.assertFalse(self.inside("L3", end + STEP_MM * inward), key)
                self.assertTrue(self.inside("L3", end - STEP_MM * inward), key)

    def test_a_median_is_drawn_in_the_reading_nearest_it(self):
        medians = [ln for ln in self.lines if ln.rule == "median"]
        self.assertTrue({"h_post", "canal_w", "canal_ap"} <= {ln.key for ln in medians})
        for ln in medians:
            self.assertLessEqual(abs(ln.drawn - ln.value), MEDIAN_MM, ln.key)

    def test_a_disc_runs_from_the_plate_below_to_the_plate_above(self):
        for up, low in (("L2", "L3"), ("L3", "L4")):
            for key in ("disc_h_ant", "disc_h_mid", "disc_h_post"):
                ln = self.by_key(key, "%s-%s" % (up, low))
                d = (ln.b - ln.a) / np.linalg.norm(ln.b - ln.a)
                self.assertTrue(self.inside(low, ln.a - STEP_MM * d), key)
                self.assertFalse(self.inside(low, ln.a + STEP_MM * d), key)
                self.assertTrue(self.inside(up, ln.b + STEP_MM * d), key)
                self.assertFalse(self.inside(up, ln.b - STEP_MM * d), key)

    def test_the_lines_match_the_phantoms_truth_where_it_is_exact(self):
        t = P.truth(self.placed["L3"].v)
        for key, tol in (("endplate", 0.6), ("body_w_mid", 0.8), ("canal_ap_min", 0.6), ("h_mid", 0.6)):
            self.assertAlmostEqual(self.by_key(key).value, t[key], delta=tol, msg=key)

    def test_four_panels_draw_with_one_key_line_each(self):
        v = self.vs["L3"]
        fig = R.figure(v, self.lab, P.LEVEL_IDS["L3"], self.lines, "phantom")
        texts = [t.get_text() for ax in fig.axes for t in ax.texts if "\n" in t.get_text() or "  " in t.get_text()]
        keyed = sum(len([s for s in t.split("\n") if s.strip()]) for t in texts if t[:1].isdigit())
        self.assertEqual(keyed, sum(ln.status == "drawn" for ln in self.lines))
        with tempfile.TemporaryDirectory() as d:
            from schwingcheck import figures as FIG
            paths = FIG.save(fig, d, "render", "A phantom.")
            self.assertTrue(all(os.path.getsize(p) > 0 for p in paths))


class Checked(unittest.TestCase):
    def line(self, value: float) -> LN.Line:
        return LN.Line("h_ant", "L3", value, np.zeros(3), np.array([0.0, 0.0, value]), "length", "sagittal")

    def test_a_value_off_its_row_is_withheld(self):
        got = LN.checked([self.line(27.0)], {"h_ant": 27.01})[0]
        self.assertTrue(got.status.startswith("withheld"))

    def test_the_rows_rounding_is_allowed(self):
        got = LN.checked([self.line(27.00004)], {"h_ant": 27.0}, places=4)[0]
        self.assertEqual(got.status, "drawn")
        got = LN.checked([self.line(27.0001)], {"h_ant": 27.0}, places=4)[0]
        self.assertTrue(got.status.startswith("withheld"))

    def test_a_measure_not_taken_is_not_drawn(self):
        got = LN.checked([self.line(27.0)], {"h_ant": math.nan})[0]
        self.assertEqual(got.status, "not measured")
        got = LN.checked([self.line(27.0)], {})[0]
        self.assertEqual(got.status, "not measured")


if __name__ == "__main__":
    unittest.main()

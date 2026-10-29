"""The oracle, the measurements' definitions, the phantoms and the line renderer of autoanatomist/,
each claim checked against something outside the code it tests.

    python -m unittest discover -s tests -v          # from the repository's root, in the venv

The stand-in oracle's values are scanimport.volume.measure_volume's to the bit, on scanimport's
phantom column with whole masks and with SPINEPS-style subregions, and every one of its lines is
drawn and passes oracle.check with every key present; check names a value NaN beside its points,
points given in part, ends the wrong way round, a chord along the wrong axis, a left-handed frame
and a key not carried; a level the rule does not measure (C2) still carries every key, each not
taken with the reason; each line's ends lie on the mask's boundary, the mask's own label on one
side of each end and not on the other, but for the spinous length's tip, which is the farthest
voxel and so a corner of the voxelised process, where the test asks only that the tip is the
vertebra's and the step beyond it is not; on autoanatomist's phantoms, whose anatomy is drawn from
the generator's columns, the oracle reads the drawn values back within the bounds measured on
2026-10-29 over the five columns the test runs (a mean error of 0.44 mm and at most 1.34 mm
over fifteen bodies); the measurements' rules give known lengths, angles and areas in NumPy and in
JAX alike; and the renderer draws a PNG for the mask and for the CT, cuts each panel where its
lines lie together (the end-plate widths on the coronal cut, the transverse span behind it) and
gives a reslice the extent imshow reads.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from scanimport import geometry as G                              # noqa: E402
from scanimport import volume as V                                # noqa: E402
from scanimport.tests import phantom as SP                        # noqa: E402

from autoanatomist import oracle as O                             # noqa: E402
from autoanatomist import phantom as PH                           # noqa: E402
from autoanatomist import specs as S                              # noqa: E402

try:
    import jax.numpy as jnp
except ImportError:                                               # pragma: no cover
    jnp = None

LEVELS = ["L1", "L2", "L3", "L4"]
VALUES = {"L1": 20, "L2": 21, "L3": 22, "L4": 23}
NAMES = {v: lv for lv, v in VALUES.items()}
BODY_CHORDS = ("endplate", "endplate_depth", "endplate_lower", "endplate_lower_depth", "h_post", "tp_span",
               "spinous_length")
CANAL_CHORDS = ("canal_w", "canal_ap")


def nearest_label(labels, affine, world):
    ijk = np.rint(np.linalg.solve(affine[:3, :3], (np.asarray(world, float) - affine[:3, 3]).T).T).astype(int)
    ijk = np.clip(ijk, 0, np.array(labels.shape) - 1)
    return labels[tuple(ijk.T)]


class TheOracle(unittest.TestCase):
    def test_values_are_measure_volumes_and_every_line_is_drawn(self):
        for subregions in (False, True):
            lab, aff, sub, _ = SP.column(LEVELS, VALUES, subregions=subregions)
            oracle = O.ChordOracle()
            readings = oracle.read(lab, aff, NAMES, sub)
            bodies = V.measure_volume(lab, G.VoxelGrid(aff, lab.shape), NAMES, sub)
            self.assertEqual([r.level for r in readings], LEVELS)
            for r, b in zip(readings, bodies):
                self.assertEqual(O.check(r, atol=1e-9, keys=oracle.keys), [], (subregions, r.level))
                for k in S.SEVEN + S.EXTRA:
                    if np.isfinite(b.values[k]):
                        self.assertEqual(r.measurements[k].value, b.values[k], (subregions, r.level, k))
                        self.assertTrue(r.measurements[k].drawn, (subregions, r.level, k, r.measurements[k].flag))

    def test_line_ends_lie_on_the_mask_boundary(self):
        lab, aff, _, _ = SP.column(LEVELS, VALUES)
        h = float(np.min(G.VoxelGrid(aff, lab.shape).spacing))
        step = 1.5 * h
        for r in O.ChordOracle().read(lab, aff, NAMES):
            for k in BODY_CHORDS + CANAL_CHORDS:
                m = r.measurements[k]
                if not m.drawn:
                    continue
                a, b = m.array()
                d = (b - a) / np.linalg.norm(b - a)
                for end, out in ((a, -d), (b, d)):
                    inner = nearest_label(lab, aff, end - step * out) == r.label
                    outer = nearest_label(lab, aff, end + step * out) == r.label
                    if k == "spinous_length" and end is b:
                        self.assertTrue(nearest_label(lab, aff, end) == r.label, (r.level, k))
                        self.assertFalse(outer, (r.level, k))
                    elif k in CANAL_CHORDS:
                        self.assertFalse(inner, (r.level, k))
                        self.assertTrue(outer, (r.level, k))
                    else:
                        self.assertTrue(inner, (r.level, k))
                        self.assertFalse(outer, (r.level, k))

    def test_a_reading_carries_its_landmarks(self):
        lab, aff, _, _ = SP.column(LEVELS[:2], {lv: VALUES[lv] for lv in LEVELS[:2]})
        r = O.ChordOracle(S.SEVEN).read(lab, aff, {20: "L1", 21: "L2"})[0]
        P = r.landmarks(S.SEVEN)
        self.assertEqual(P.shape, (len(S.landmarks(S.SEVEN)), 3))
        self.assertTrue(np.isfinite(P).all())
        self.assertTrue(np.isfinite(r.values(S.SEVEN)).all())
        np.testing.assert_allclose(S.values(P, S.SEVEN), r.values(S.SEVEN), atol=1e-9)

    def test_check_names_what_breaks_the_interface(self):
        import copy
        lab, aff, _, _ = SP.column(LEVELS, VALUES)
        good = O.ChordOracle().read(lab, aff, NAMES)[1]
        self.assertEqual(O.check(good, keys=S.SEVEN + S.EXTRA), [])
        bad = copy.deepcopy(good)
        bad.measurements["endplate"].value = float("nan")
        self.assertEqual(O.check(bad), ["L2 endplate: the value is NaN though its points are given"])
        bad = copy.deepcopy(good)
        m = bad.measurements["endplate"]
        m.points["endplate.right"], m.points["endplate.left"] = m.points["endplate.left"], m.points["endplate.right"]
        self.assertEqual(O.check(bad), ["L2 endplate: the ends endplate.right and endplate.left are the wrong way round"])
        bad = copy.deepcopy(good)
        m = bad.measurements["endplate"]
        local = good.frame.local(m.array())
        local[1] = local[0] + np.array([0.0, 0.0, -float(m.value)])
        m.points["endplate.right"], m.points["endplate.left"] = good.frame.world(local)
        self.assertEqual(O.check(bad), ["L2 endplate: the line runs along z, not its axis x"])
        bad = copy.deepcopy(good)
        bad.frame.ex = -bad.frame.ex
        self.assertEqual(O.check(bad)[0], "L2: the frame is left-handed; x is cross(y, z)")
        bad = copy.deepcopy(good)
        bad.measurements["endplate"].points["endplate.left"] = np.full(3, np.nan)
        self.assertEqual(O.check(bad), ["L2 endplate: points given in part"])
        empty = O.Reading("L1", 20, good.frame, good.centre)
        self.assertEqual(O.check(empty, keys=["endplate"]), ["L1: no measurement endplate"])

    def test_unmeasured_levels_carry_every_key(self):
        lab, aff, _, _ = SP.column(LEVELS, VALUES)
        readings = O.ChordOracle(S.SEVEN).read(lab, aff, {20: "C2", 21: "L2", 22: "L3", 23: "L4"})
        c2 = [r for r in readings if r.level == "C2"][0]
        self.assertEqual(sorted(c2.measurements), sorted(S.SEVEN))
        self.assertEqual(O.check(c2, keys=S.SEVEN), [])
        for k in S.SEVEN:
            self.assertFalse(c2.measurements[k].taken)
            self.assertIn("not measured", c2.measurements[k].flag)
        self.assertTrue(np.isnan(c2.landmarks(S.SEVEN)).all())
        self.assertTrue(np.isnan(c2.values(S.SEVEN)).all())


class ThePhantoms(unittest.TestCase):
    def test_the_oracle_reads_the_drawn_anatomy_back(self):
        errors = []
        for kind, start, seed in (("typical", "T12", 3), ("six_lumbar", "L4", 3), ("t13", "T12", 3),
                                  ("typical", "L2", 11), ("four_lumbar", "L2", 5)):
            levels = PH.draw_levels(kind, seed=seed, start=start, count=3)
            ph = PH.render(levels, spacing=(1.25,) * 3, sub=1)
            oracle = O.ChordOracle(S.SEVEN)
            readings = oracle.read(ph.labels, ph.affine, ph.names)
            self.assertEqual([r.level for r in readings], [lv.name for lv in levels])
            for r, lv in zip(readings, levels):
                self.assertEqual(O.check(r, atol=1e-9, keys=oracle.keys), [])
                errors += [r.measurements[k].value - lv.truth()[k] for k in S.SEVEN]
        errors = np.abs(errors)
        self.assertLess(errors.mean(), 0.6)
        self.assertLess(errors.max(), 1.5)

    def test_the_ct_shows_bone_where_the_mask_is(self):
        levels = PH.draw_levels("typical", seed=4, start="L1", count=2)
        ph = PH.render(levels, spacing=(1.5,) * 3, sub=1)
        bone = ph.hu > 150.0
        inside = ph.labels > 0
        self.assertGreater((bone & inside).sum() / inside.sum(), 0.9)
        self.assertLess((bone & ~inside).sum() / bone.sum(), 0.15)


class TheMeasurements(unittest.TestCase):
    def test_known_figures(self):
        for xp in (np, jnp) if jnp is not None else (np,):
            seg = xp.asarray(np.array([[0.0, 0.0, 0.0], [3.0, 4.0, 0.0]]))
            self.assertAlmostEqual(float(S.length(seg[0], seg[1], xp)), 5.0, places=5)
            right = xp.asarray(np.array([[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 3.0, 0.0]]))
            ang = S.Spec("a", "angle", ("p", "q", "r", "s"), "", "axial", "", "").value(right, xp)
            self.assertAlmostEqual(float(ang), 90.0, places=4)
            square = xp.asarray(np.array([[0.0, 0.0, 1.0], [2.0, 0.0, 1.0], [2.0, 2.0, 1.0], [0.0, 2.0, 1.0]]))
            area = S.Spec("b", "area", ("p", "q", "r", "s"), "", "axial", "", "").value(square, xp)
            self.assertAlmostEqual(float(area), 4.0, places=5)

    def test_landmarks_and_their_indices(self):
        names = S.landmarks(S.SEVEN)
        self.assertEqual(len(names), 14)
        self.assertEqual(len(S.landmarks(S.SEVEN + S.EXTRA)), 18)
        for k, at in S.index_of(S.SEVEN).items():
            self.assertEqual([names[i] for i in at], list(S.SPECS[k].points))
        with self.assertRaises(ValueError):
            S.select(["no_such_measure"])


class TheRenderer(unittest.TestCase):
    def test_it_draws_the_mask_and_the_ct(self):
        from autoanatomist import render as RD
        levels = PH.draw_levels("typical", seed=3, start="L1", count=2)
        ph = PH.render(levels, spacing=(1.5,) * 3, sub=1)
        r = O.ChordOracle().read(ph.labels, ph.affine, ph.names)[0]
        with tempfile.TemporaryDirectory() as d:
            for kind, vol in (("mask", ph.labels), ("ct", ph.hu)):
                out = os.path.join(d, kind + ".png")
                cuts = RD.draw(r, vol, ph.affine, out, kind=kind, half_mm=50.0, step_mm=1.0)
                self.assertEqual(set(cuts), {"coronal", "sagittal", "axial"})
                with open(out, "rb") as f:
                    self.assertEqual(f.read(8), b"\x89PNG\r\n\x1a\n")

    def test_each_panel_cuts_where_its_lines_lie(self):
        from autoanatomist import render as RD
        lab, aff, _, _ = SP.column(LEVELS, VALUES)
        r = O.ChordOracle().read(lab, aff, NAMES)[1]
        with tempfile.TemporaryDirectory() as d:
            cuts = RD.draw(r, lab, aff, os.path.join(d, "m.png"), kind="mask", half_mm=50.0, step_mm=1.0)
        for k in ("endplate", "endplate_lower"):
            self.assertLessEqual(abs(RD.line_depth(r, k, "coronal") - cuts["coronal"]), RD.OFF_PLANE_MM, k)
        self.assertGreater(cuts["coronal"] - RD.line_depth(r, "tp_span", "coronal"), 20.0)
        for k in ("endplate_depth", "endplate_lower_depth", "h_post", "spinous_length"):
            self.assertLessEqual(abs(RD.line_depth(r, k, "sagittal") - cuts["sagittal"]), RD.OFF_PLANE_MM, k)
        for k in ("canal_w", "canal_ap"):
            self.assertLessEqual(abs(RD.line_depth(r, k, "axial") - cuts["axial"]), RD.OFF_PLANE_MM, k)
        self.assertEqual(RD.plane_offset(r, "coronal", []), float(r.frame.local(r.centre[None])[0, 1]))
        img, ext = RD.reslice(lab, aff, r, "coronal", cuts["coronal"], half_mm=50.0, step_mm=1.0)
        self.assertEqual(img.shape, (101, 101))
        self.assertAlmostEqual(ext[1] - ext[0], 101.0, places=9)
        self.assertAlmostEqual(ext[3] - ext[2], 101.0, places=9)
        centre = r.frame.local(r.centre[None])[0]
        self.assertAlmostEqual(0.5 * (ext[0] + ext[1]), centre[0], places=9)
        self.assertAlmostEqual(0.5 * (ext[2] + ext[3]), centre[2], places=9)


if __name__ == "__main__":
    unittest.main()

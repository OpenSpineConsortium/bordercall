"""The run's lines export (`python -m morphometry run --lines`) on phantoms written as label files.

Every measure the rows hold a value for gets its line, built by morphoview.lines on the vertebrae
the rows were read from and checked against the same values, so on a whole column every line is
drawn and its value is the row's; a length's ends lie its value apart; each measured vertebra's
frame is written in the world the ends are written in, so a height runs up its frame's z and a
width across its x. A run with the lines resumes like one without, writes a study again whose
lines are missing, and has a stamp of its own; a drawing that fails flags its level and loses no
row of the measuring."""
import contextlib
import csv
import io
import math
import os
import shutil
import tempfile
import unittest
from unittest import mock

import nibabel as nib
import numpy as np

from morphometry import __main__ as RUN
from morphometry import measure as M
from morphometry.tests import phantom as P
from morphoview import lines as LN
from scanimport import geometry as G

LEVELS = ["L2", "L3", "L4"]
ROUNDING = 1e-4                 # every number in the files is written to four places


def save(lab: np.ndarray, aff: np.ndarray, folder: str, study: str) -> str:
    path = os.path.join(folder, study + ".nii.gz")
    nib.save(nib.Nifti1Image(lab.astype(np.int16), aff), path)
    return path


def cut_below(lab: np.ndarray, aff: np.ndarray, level: str) -> tuple:
    """The volume with its edge through the middle of a level, on the side away from the rest."""
    ax = RUN.head_foot_axis(aff)
    at = np.flatnonzero(np.any(lab == P.LEVEL_IDS[level], axis=tuple(i for i in range(3) if i != ax)))
    others = np.flatnonzero(np.any((lab > 0) & (lab != P.LEVEL_IDS[level]), axis=tuple(i for i in range(3) if i != ax)))
    mid = int(0.5 * (at.min() + at.max()))
    keep = [slice(None)] * 3
    out = np.array(aff, float)
    if at.mean() > others.mean():
        keep[ax] = slice(0, mid)
    else:
        keep[ax] = slice(mid, None)
        out[:3, 3] += mid * out[:3, ax]
    return lab[tuple(keep)], out


def run(argv) -> str:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        RUN.main(argv)
    return out.getvalue()


def read(path: str) -> list:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def masks(folder: str) -> None:
    lab, aff = P.draw(P.straight(LEVELS, P.Vert()), spacing=(0.8, 0.8, 1.0))
    save(lab, aff, folder, "0001")
    save(*cut_below(lab, aff, "L4"), folder, "0002")


class RunWithLines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.masks, cls.out = os.path.join(cls.tmp, "masks"), os.path.join(cls.tmp, "out")
        os.makedirs(cls.masks)
        masks(cls.masks)
        cls.said = run(["run", "--masks", cls.masks, "--scheme", "verse", "--out", cls.out, "--workers", "1", "--lines"])
        cls.rows = read(os.path.join(cls.out, "rows.csv"))
        cls.lines = read(os.path.join(cls.out, "lines.csv"))
        cls.frames = read(os.path.join(cls.out, "frames.csv"))
        cls.main = [r for r in cls.lines if r["part"] == ""]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def value(self, study: str, level: str, key: str) -> str:
        return next(r["value"] for r in self.rows if (r["study"], r["level"], r["key"]) == (study, level, key))

    def test_on_the_whole_column_every_line_is_drawn(self):
        whole = [r for r in self.main if r["study"] == "0001"]
        for level in LEVELS + ["L2-L3", "L3-L4"]:
            got = [r for r in whole if r["level"] == level]
            self.assertGreaterEqual(len(got), 3 if "-" in level else 20, level)
            for r in got:
                self.assertEqual(r["status"], "drawn", "%s %s %s" % (level, r["key"], r["status"]))

    def test_a_drawn_line_holds_the_rows_value(self):
        for r in self.main:
            if r["status"] == "drawn":
                self.assertEqual(r["value"], self.value(r["study"], r["level"], r["key"]), r["key"])
                self.assertEqual(r["measured"], r["value"], r["key"])

    def test_a_length_is_the_distance_between_its_ends(self):
        for r in self.main:
            if r["rule"] == "length" and r["value"]:
                a = np.array([float(r[k]) for k in ("ax", "ay", "az")])
                b = np.array([float(r[k]) for k in ("bx", "by", "bz")])
                self.assertAlmostEqual(float(np.linalg.norm(b - a)), float(r["value"]), delta=4 * ROUNDING, msg=r["key"])

    def test_the_further_segments_ride_with_their_line(self):
        parts = [r for r in self.lines if r["part"]]
        self.assertTrue({"lower plate", "apex to apex"} <= {r["part"] for r in parts})
        for r in parts:
            self.assertEqual(r["value"], "")
            self.assertTrue(any((m["study"], m["level"], m["key"]) == (r["study"], r["level"], r["key"]) for m in self.main))

    def frame(self, study: str, level: str) -> G.Frame:
        f = next(r for r in self.frames if (r["study"], r["level"]) == (study, level))
        vec = lambda p: np.array([float(f[p + a]) for a in "xyz"])  # noqa: E731
        return G.Frame(vec("o"), vec("ex"), vec("ey"), vec("ez"))

    def test_each_measured_vertebra_has_a_right_handed_frame(self):
        levels = {(r["study"], r["level"]) for r in self.main if "-" not in r["level"]}
        self.assertEqual(levels, {(r["study"], r["level"]) for r in self.frames})
        for study, level in levels:
            f = self.frame(study, level)
            R = np.stack([f.ex, f.ey, f.ez])
            np.testing.assert_allclose(R @ R.T, np.eye(3), atol=4 * ROUNDING)
            self.assertAlmostEqual(float(np.linalg.det(R)), 1.0, delta=4 * ROUNDING)

    def test_a_height_runs_up_its_frame_and_a_width_across_it(self):
        for key, axis in (("h_mid", "ez"), ("body_w_mid", "ex"), ("body_d_mid", "ey")):
            r = next(r for r in self.main if (r["study"], r["level"], r["key"]) == ("0001", "L3", key))
            d = np.array([float(r["b" + a]) - float(r["a" + a]) for a in "xyz"])
            self.assertGreater(abs(float(d @ getattr(self.frame("0001", "L3"), axis))) / np.linalg.norm(d), 0.99, key)

    def test_a_vertebra_the_edge_cuts_draws_nothing_its_rows_do_not_hold(self):
        """The edge runs through L4's body, whose every measure the rows leave empty: its lines say
        not measured, its canal and pedicles among them, and L3 above it is drawn whole."""
        cut = [r for r in self.main if (r["study"], r["level"]) == ("0002", "L4")]
        self.assertTrue(cut, "the cut L4 is measured and has lines")
        self.assertTrue([r for r in cut if r["key"].startswith(("canal_", "interpedicular", "pedicle_"))])
        for r in cut:
            self.assertEqual(r["status"], "not measured", r["key"])
            self.assertEqual(self.value("0002", "L4", r["key"]), "", r["key"])
        above = [r for r in self.main if (r["study"], r["level"]) == ("0002", "L3")]
        self.assertGreaterEqual(len(above), 20)
        self.assertTrue(all(r["status"] == "drawn" for r in above))
        self.assertFalse([r for r in self.rows if r["key"] == "flag:lines"])

    def test_the_joined_files_hold_every_studys_files(self):
        for name, joined in (("lines", self.lines), ("frames", self.frames)):
            each = []
            for study in ("0001", "0002"):
                each += read(os.path.join(self.out, name, study + ".csv"))
            self.assertEqual(each, joined, name)

    def test_the_stamp_is_the_lines_own(self):
        self.assertIn("code %s" % RUN.code_stamp(True), self.said)
        self.assertNotEqual(RUN.code_stamp(True), RUN.code_stamp(False))


class Resuming(unittest.TestCase):
    """A run cut short resumes; a study whose lines are missing is written again."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.masks, self.out = os.path.join(self.tmp, "masks"), os.path.join(self.tmp, "out")
        os.makedirs(self.masks)
        lab, aff = P.draw(P.straight(LEVELS, P.Vert()), spacing=(0.86, 0.86, 2.5))
        save(lab, aff, self.masks, "0001")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def again(self, *more) -> str:
        return run(["run", "--masks", self.masks, "--scheme", "verse", "--out", self.out, "--workers", "1", *more])

    def test_a_study_is_measured_once_and_again_only_where_its_files_are_not_current(self):
        self.assertIn("1 to measure", self.again("--lines"))
        self.assertIn("0 to measure", self.again("--lines"))
        os.remove(os.path.join(self.out, "lines", "0001.csv"))
        self.assertIn("1 to measure", self.again("--lines"))
        self.assertTrue(os.path.exists(os.path.join(self.out, "lines", "0001.csv")))
        os.remove(os.path.join(self.out, "frames", "0001.csv"))
        self.assertIn("1 to measure", self.again("--lines"))
        self.assertIn("1 to measure", self.again(), "a run without the lines has the measuring code's own stamp")
        self.assertIn("0 to measure", self.again())
        self.assertIn("1 to measure", self.again("--lines"))


class Failing(unittest.TestCase):
    """A drawing that fails flags its level and loses no row; a study that fails writes empty
    lines and frames beside its error, and is measured again."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        lab, aff = P.draw(P.straight(LEVELS, P.Vert()), spacing=(0.86, 0.86, 2.5))
        cls.path = save(lab, aff, cls.tmp, "0001")
        cls.plain = M.measure_file(cls.path, "verse", "0001")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def one(self, name: str) -> str:
        top = os.path.join(self.tmp, name)
        for sub in ("rows", "lines", "frames"):
            os.makedirs(os.path.join(top, sub))
        out = os.path.join(top, "rows", "0001.csv")
        RUN.one_study((self.path, "verse", "0001", out, RUN.code_stamp(True), True))
        return out

    def test_a_level_whose_drawing_fails_is_flagged_and_its_rows_stand(self):
        real = LN.vertebra_lines

        def broken(v, ped, vals=None):
            if v.level == "L3":
                raise ValueError("drawn wrong")
            return real(v, ped, vals)

        with mock.patch.object(LN, "vertebra_lines", broken):
            out = self.one("broken")
        rows = read(out)
        flags = [r for r in rows if r["key"] == "flag:lines"]
        self.assertEqual([(r["level"], r["note"]) for r in flags], [("L3", "ValueError: drawn wrong")])
        want = {(r["level"], r["key"]): str(RUN.number(r["value"])) for r in self.plain if r["level"] != "study"}
        got = {(r["level"], r["key"]): r["value"] for r in rows if r["level"] != "study" and r["key"] != "flag:lines"}
        self.assertEqual(got, want)
        lines = read(os.path.join(self.tmp, "broken", "lines", "0001.csv"))
        self.assertEqual({r["level"] for r in lines}, {"L2", "L4", "L2-L3", "L3-L4"})
        self.assertTrue(RUN.current(out, RUN.code_stamp(True), True), "a drawing that fails is not measured again")

    def test_a_study_that_fails_writes_empty_lines_and_is_measured_again(self):
        with mock.patch.object(M, "measure_file", side_effect=RuntimeError("no mask")):
            out = self.one("failed")
        self.assertTrue(any(r["key"] == "flag:error" for r in read(out)))
        for sub in ("lines", "frames"):
            self.assertEqual(read(os.path.join(self.tmp, "failed", sub, "0001.csv")), [])
        self.assertFalse(RUN.current(out, RUN.code_stamp(True), True))


class SameLines(unittest.TestCase):
    """The pedicles' lines drawn on the measure's own reading are the lines read again."""

    def test_the_measures_reading_draws_what_reading_again_draws(self):
        lab, aff = P.draw(P.straight(LEVELS, P.Vert()), spacing=(0.8, 0.8, 1.0))
        kept: dict = {}
        M.measure_volume(lab, G.VoxelGrid(aff, lab.shape), {P.LEVEL_IDS[lv]: lv for lv in LEVELS}, "same",
                         pelvis=False, keep=kept)
        v, ped, vals = kept["verts"]["L3"], kept["peds"]["L3"], kept["values"]["L3"]
        again = LN.checked(LN.vertebra_lines(v, ped), vals)
        reused = LN.checked(LN.vertebra_lines(v, ped, vals), vals)
        self.assertEqual([ln.key for ln in again], [ln.key for ln in reused])
        self.assertTrue(any(ln.key.startswith("pedicle_") for ln in reused))
        for x, y in zip(again, reused):
            self.assertEqual((x.status, x.rule, x.panel), (y.status, y.rule, y.panel), x.key)
            self.assertTrue(math.isclose(x.value, y.value, rel_tol=0, abs_tol=1e-12), x.key)
            np.testing.assert_array_equal(x.a, y.a)
            np.testing.assert_array_equal(x.b, y.b)


if __name__ == "__main__":
    unittest.main()

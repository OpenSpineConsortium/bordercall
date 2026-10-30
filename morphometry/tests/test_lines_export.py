"""The run's lines export (`python -m morphometry run --lines`) on phantoms, written as label files
where a run reads them.

The measures morphoview.lines draws, every one of scanimport's seven chords among them, get their
lines, built on the vertebrae the rows were read from and checked against the same values, so on
a whole column every line is drawn and its value is the row's; a length's ends lie its value
apart; each measured vertebra's frame is written in the world the ends are written in, its origin
the centroid of the label's main piece, and on a column whose vertebrae lean against its line each
line's ends lie in it as their builder placed them and where their names say, and each frame
names the axis its z lies along. The geometry is written whole, to the bit; a line off its row
keeps both values. A run with the lines resumes like one without, writes a study again whose
lines are missing or were cut short at any of its writes, and has a stamp of its own, which
follows the drawing's code; a builder that fails flags its level and loses no row of the
measuring and no other builder's line; a run a dead worker cuts short joins only the lines its
own code drew."""
import contextlib
import csv
import io
import math
import os
import shutil
import tempfile
import unittest
from concurrent.futures import Future
from concurrent.futures.process import BrokenProcessPool
from unittest import mock

import nibabel as nib
import numpy as np

from morphometry import __main__ as RUN
from morphometry import measure as M
from morphometry.tests import phantom as P
from morphoview import lines as LN
from scanimport import SEVEN
from scanimport import geometry as G

LEVELS = ["L2", "L3", "L4"]
ROUNDING = 1e-4                 # the rows and the lines' measured column are written to four places
WHOLE = 1e-9                    # the ends, the frames and a construction's value are written whole
# what a line's two ends share in its vertebra's frame, as its builder placed them: a height runs
# along z, a width along x, a depth along y
SHARED = {"x": ("h_ant", "h_mid", "h_post_inset", "h_post", "wedge"),
          "yz": ("body_w_mid", "endplate", "endplate_lower", "canal_w", "tp_span", "interpedicular",
                 "interpedicular_max", "pedicle_w_right", "pedicle_w_left"),
          "xz": ("body_d_mid", "endplate_depth", "endplate_lower_depth", "canal_ap_min", "canal_ap",
                 "canal_ap_lateral_film"),
          "xy": ("pedicle_h_right", "pedicle_h_left")}
SHARED_MM = 1e-6
# which way each end's name lies along the frame's axes, either way round: (axis, sign of b less a)
ORDER = {("inferior", "superior"): (2, 1), ("posterior", "anterior"): (1, 1), ("left", "right"): (0, 1),
         ("tip", "canal"): (1, 1)}
ORDER.update({(b, a): (axis, -sign) for (a, b), (axis, sign) in list(ORDER.items())})


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

    def test_every_one_of_panjabis_seven_chords_is_drawn(self):
        for level in LEVELS:
            drawn = {r["key"] for r in self.main if (r["study"], r["level"]) == ("0001", level) and r["status"] == "drawn"}
            self.assertEqual(set(SEVEN) - drawn, set(), level)

    def test_the_keys_drawn_are_the_ones_the_lines_name(self):
        for level, keys in (("L3", LN.VERTEBRA_KEYS), ("L2-L3", LN.DISC_KEYS)):
            got = [r["key"] for r in self.main if (r["study"], r["level"]) == ("0001", level)]
            self.assertEqual(sorted(got), sorted(keys), level)
        for r in self.lines:
            self.assertTrue(r["a_end"] and r["b_end"], "%s %s %r" % (r["key"], r["part"], (r["a_end"], r["b_end"])))

    def test_a_drawn_line_holds_the_rows_value(self):
        for r in self.main:
            if r["status"] == "drawn":
                self.assertEqual(r["measured"], self.value(r["study"], r["level"], r["key"]), r["key"])
                self.assertLessEqual(abs(float(r["value"]) - float(r["measured"])), 0.5 * ROUNDING + WHOLE, r["key"])

    def test_a_length_is_the_distance_between_its_ends(self):
        for r in self.main:
            if r["rule"] == "length" and r["value"]:
                a = np.array([float(r[k]) for k in ("ax", "ay", "az")])
                b = np.array([float(r[k]) for k in ("bx", "by", "bz")])
                self.assertAlmostEqual(float(np.linalg.norm(b - a)), float(r["value"]), delta=WHOLE, msg=r["key"])
                self.assertAlmostEqual(float(r["drawn"]), float(r["value"]), delta=WHOLE, msg=r["key"])

    def test_the_further_segments_ride_with_their_line(self):
        """Each further segment has its line, and ends of its own: the wedge's lower plate lies a
        body's height below the upper plate the line runs along."""
        ends = lambda r: np.array([[float(r[p + a]) for a in "xyz"] for p in "ab"])  # noqa: E731
        parts = [r for r in self.lines if r["part"]]
        self.assertTrue({"lower plate", "apex to apex"} <= {r["part"] for r in parts if r["status"] == "drawn"})
        for r in parts:
            self.assertEqual(r["value"], "")
            line = next(m for m in self.main if (m["study"], m["level"], m["key"]) == (r["study"], r["level"], r["key"]))
            if r["status"] != "drawn":
                continue
            self.assertGreater(float(np.abs(ends(r) - ends(line)).max()), 1.0, (r["level"], r["key"], r["part"]))
            if r["part"] == "lower plate":
                drop = float((ends(line).mean(0) - ends(r).mean(0)) @ self.frame(r["study"], r["level"]).ez)
                self.assertGreater(drop, 20.0, r["level"])

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
            np.testing.assert_allclose(R @ R.T, np.eye(3), atol=WHOLE)
            self.assertAlmostEqual(float(np.linalg.det(R)), 1.0, delta=WHOLE)

    def test_a_height_runs_up_its_frame_and_a_width_across_it(self):
        for key, axis in (("h_mid", "ez"), ("body_w_mid", "ex"), ("body_d_mid", "ey")):
            r = next(r for r in self.main if (r["study"], r["level"], r["key"]) == ("0001", "L3", key))
            d = np.array([float(r["b" + a]) - float(r["a" + a]) for a in "xyz"])
            self.assertGreater(abs(float(d @ getattr(self.frame("0001", "L3"), axis))) / np.linalg.norm(d), 0.99, key)

    def test_a_vertebra_the_edge_cuts_draws_nothing_its_rows_do_not_hold(self):
        """The edge runs through L4's body, whose every measure but its axis readings the rows
        leave empty: its lines say not measured, its canal and pedicles among them, and L3 above it
        is drawn whole."""
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


def chain_masks(folder: str) -> str:
    """L2 to L4 with each joint opened 8 degrees in front, tilted 4 sideways, turned 5 and slipped
    4 mm, the whole turned 12 degrees (test_morphometry.Joints): each vertebra's own axis lies
    degrees off the column's line through its neighbours, so a frame left on that line, or turned
    a few degrees off the vertebra's own, puts the lines' ends off where their builders placed them."""
    joint = P.Joint(gap=10.0, sagittal=8.0, coronal=4.0, axial=5.0, slip=4.0)
    placed = P.chain(LEVELS, {lv: P.Vert() for lv in LEVELS}, {lv: joint for lv in LEVELS[1:]},
                     R0=P.rotation((1.0, 0.3, 0.0), 12.0))
    lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), strict=False)
    return save(lab, aff, folder, "0001")


class Frames(unittest.TestCase):
    """Each frame against the label it was read from and the lines drawn in it, on a leaning column."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        masks, out = os.path.join(cls.tmp, "masks"), os.path.join(cls.tmp, "out")
        os.makedirs(masks)
        cls.path = chain_masks(masks)
        run(["run", "--masks", masks, "--scheme", "verse", "--out", out, "--workers", "1", "--lines"])
        cls.lines = read(os.path.join(out, "lines.csv"))
        cls.main = [r for r in cls.lines if r["part"] == ""]
        cls.rows = read(os.path.join(out, "rows.csv"))
        cls.frames = {r["level"]: r for r in read(os.path.join(out, "frames.csv"))}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def to_local(self, level: str, rows: list) -> list:
        """(row, a, b) for each row, the line's two ends in the written frame it was drawn in: a
        vertebra's own, a disc's the vertebra's below."""
        f = self.frames[level.split("-")[-1]]
        o = np.array([float(f["o" + a]) for a in "xyz"])
        R = np.array([[float(f[e + a]) for a in "xyz"] for e in ("ex", "ey", "ez")])
        end = lambda r, p: R @ (np.array([float(r[p + a]) for a in "xyz"]) - o)  # noqa: E731
        return [(r, end(r, "a"), end(r, "b")) for r in rows if r["level"] == level]

    def local(self, level: str) -> dict:
        """{key: (a, b)}, each line's two ends in its vertebra's written frame."""
        return {r["key"]: (a, b) for r, a, b in self.to_local(level, self.main)}

    def test_the_origin_is_the_labels_centroid(self):
        img = nib.load(self.path)
        lab, aff = np.asarray(img.dataobj), img.affine
        self.assertEqual(set(self.frames), set(LEVELS))
        for level in LEVELS:
            idx, _ = M.main_piece(np.argwhere(lab == P.LEVEL_IDS[level]))
            want = (idx @ aff[:3, :3].T + aff[:3, 3]).mean(0)
            got = np.array([float(self.frames[level]["o" + a]) for a in "xyz"])
            np.testing.assert_allclose(got, want, atol=WHOLE, err_msg=level)

    def test_each_lines_ends_share_what_their_builder_gave_them(self):
        for level in LEVELS:
            ends = self.local(level)
            for axes, keys in SHARED.items():
                for key in keys:
                    a, b = ends[key]
                    for axis in axes:
                        k = "xyz".index(axis)
                        self.assertLessEqual(abs(a[k] - b[k]), SHARED_MM, "%s %s %s" % (level, key, axis))

    def test_y_points_to_the_body_z_up_and_x_to_the_right(self):
        for level in LEVELS:
            ends = self.local(level)
            self.assertGreater(min(ends["h_ant"][0][1], ends["h_ant"][1][1]), 0.0, level)
            self.assertGreater(ends["h_ant"][0][1], ends["h_post_inset"][0][1], level)
            self.assertLess(ends["spinous_length"][1][1], 0.0, level)
            self.assertGreater(ends["h_mid"][1][2], ends["h_mid"][0][2], level)
            self.assertGreater(min(ends["pedicle_w_right"][0][0], ends["pedicle_w_right"][1][0]), 0.0, level)
            self.assertLess(max(ends["pedicle_w_left"][0][0], ends["pedicle_w_left"][1][0]), 0.0, level)

    def test_each_end_lies_where_its_name_says(self):
        levels = sorted({r["level"] for r in self.lines})
        self.assertIn("L2-L3", levels)
        for level in levels:
            for r, a, b in self.to_local(level, self.lines):
                names = (r["a_end"], r["b_end"])
                where = "%s %s %s %s" % (level, r["key"], r["part"], names)
                if set(names) == {"medial", "lateral"}:
                    medial, lateral = (a, b) if names[0] == "medial" else (b, a)
                    self.assertGreater(abs(lateral[0]), abs(medial[0]), where)
                else:
                    self.assertIn(names, ORDER, where)
                    axis, sign = ORDER[names]
                    self.assertGreater(sign * (b[axis] - a[axis]), 0.0, where)

    def test_each_frame_says_which_axis_its_z_lies_along(self):
        """L3 faces a neighbour with both end-plates, L2 and L4 with one each; each z lies off the
        column's line through its neighbours by the angle its row axis_offset gives, 6.8 to 11.6
        degrees on this chain."""
        self.assertEqual({lv: self.frames[lv]["axis"] for lv in LEVELS},
                         {"L2": "one plate", "L3": "bisector", "L4": "one plate"})
        for level in LEVELS:
            f = self.frames[level]
            ez = np.array([float(f["ez" + a]) for a in "xyz"])
            column = np.array([float(f["c" + a]) for a in "xyz"])
            self.assertAlmostEqual(float(np.linalg.norm(column)), 1.0, delta=WHOLE)
            turn = math.degrees(math.acos(min(1.0, float(ez @ column))))
            offset = next(float(r["value"]) for r in self.rows if (r["level"], r["key"]) == (level, "axis_offset"))
            self.assertGreater(turn, 5.0, level)
            self.assertAlmostEqual(turn, offset, delta=1e-3, msg=level)


class Resuming(unittest.TestCase):
    """A study is measured once, and again only where its lines or frames file is missing or its
    rows carry the stamp of a run with the lines or without them that it is not."""

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


class Killed(Exception):
    """A job's end between two of a study's writes."""


class Failing(unittest.TestCase):
    """A builder that fails flags its level and loses no row and no other builder's line; a study
    that fails writes empty lines and frames beside its error, however late in the measuring it
    fails, and is measured again; so is one cut short at any of its three writes."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        lab, aff = P.draw(P.straight(LEVELS, P.Vert()), spacing=(0.86, 0.86, 2.5))
        cls.path = save(lab, aff, cls.tmp, "0001")
        cls.plain = M.measure_file(cls.path, "verse", "0001")
        cls.one("whole")
        cls.whole = read(os.path.join(cls.tmp, "whole", "lines", "0001.csv"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    @classmethod
    def one(cls, name: str, stamp: str = "") -> str:
        top = os.path.join(cls.tmp, name)
        for sub in ("rows", "lines", "frames"):
            os.makedirs(os.path.join(top, sub), exist_ok=True)
        out = os.path.join(top, "rows", "0001.csv")
        RUN.one_study((cls.path, "verse", "0001", out, stamp or RUN.code_stamp(True), True))
        return out

    def test_a_builder_that_fails_is_flagged_and_loses_only_its_own_lines(self):
        real = LN.spinous

        def broken(v):
            if v.level == "L3":
                raise ValueError("drawn wrong")
            return real(v)

        with mock.patch.object(LN, "spinous", broken):
            out = self.one("broken")
        rows = read(out)
        flags = [r for r in rows if r["key"] == "flag:lines"]
        self.assertEqual([(r["level"], r["note"]) for r in flags], [("L3", "spinous: ValueError: drawn wrong")])
        want = {(r["level"], r["key"]): str(RUN.number(r["value"])) for r in self.plain if r["level"] != "study"}
        got = {(r["level"], r["key"]): r["value"] for r in rows if r["level"] != "study" and r["key"] != "flag:lines"}
        self.assertEqual(got, want)
        lines = read(os.path.join(self.tmp, "broken", "lines", "0001.csv"))
        self.assertEqual(lines, [r for r in self.whole if (r["level"], r["key"]) != ("L3", "spinous_length")])
        self.assertTrue([r for r in self.whole if (r["level"], r["key"]) == ("L3", "spinous_length")])
        self.assertTrue(RUN.current(out, RUN.code_stamp(True), True), "a drawing that fails is not measured again")

    def test_a_study_that_fails_writes_empty_lines_and_is_measured_again(self):
        with mock.patch.object(M, "measure_file", side_effect=RuntimeError("no mask")):
            out = self.one("failed")
        self.assertTrue(any(r["key"] == "flag:error" for r in read(out)))
        for sub in ("lines", "frames"):
            self.assertEqual(read(os.path.join(self.tmp, "failed", sub, "0001.csv")), [])
        self.assertFalse(RUN.current(out, RUN.code_stamp(True), True))

    def test_a_line_off_its_row_is_withheld_and_keeps_both_values(self):
        """A line whose construction lies off the value it is checked against is withheld, its
        value the construction's and measured the value it was checked against."""
        real = LN.checked

        def off(lines, vals, *args, **kwargs):
            if "h_mid" in vals:
                vals = {**vals, "h_mid": vals["h_mid"] + 1.0}
            return real(lines, vals, *args, **kwargs)

        with mock.patch.object(LN, "checked", off):
            self.one("off")
        lines = read(os.path.join(self.tmp, "off", "lines", "0001.csv"))
        was = [r for r in self.whole if r["key"] == "h_mid" and r["status"] == "drawn"]
        self.assertTrue(was)
        for w in was:
            got = next(r for r in lines if (r["level"], r["key"], r["part"]) == (w["level"], "h_mid", ""))
            self.assertTrue(got["status"].startswith("withheld"), w["level"])
            self.assertEqual(got["value"], w["value"], w["level"])
            self.assertAlmostEqual(float(got["measured"]), float(w["measured"]) + 1.0, delta=ROUNDING, msg=w["level"])

    def test_a_study_that_fails_after_its_vertebrae_are_kept_writes_empty_lines(self):
        """The column's regional measures come after measure_volume keeps its vertebrae: a failure
        there leaves the rows an error, and lines drawn beside it would stand for good."""
        with mock.patch.object(M.COL, "regional", side_effect=RuntimeError("late")):
            out = self.one("late")
        self.assertTrue(any(r["key"] == "flag:error" for r in read(out)))
        for sub in ("lines", "frames"):
            self.assertEqual(read(os.path.join(self.tmp, "late", sub, "0001.csv")), [])

    def test_a_study_cut_short_at_any_of_its_writes_is_measured_again(self):
        """The rows are written last and say whose code wrote the study, so a job that ends between
        its writes leaves the older code's rows, and the study is measured again."""
        older = self.one("older", "older")
        self.assertTrue(RUN.current(older, "older", True))
        real = RUN.write_atomic
        for k in (1, 2, 3):
            with self.subTest(write=k):
                top = os.path.join(self.tmp, "cut%d" % k)
                shutil.copytree(os.path.join(self.tmp, "older"), top)
                calls = []

                def cut(rows, path, fields=RUN.FIELDS):
                    calls.append(path)
                    if len(calls) == k:
                        raise Killed(path)
                    real(rows, path, fields)

                with mock.patch.object(RUN, "write_atomic", cut), self.assertRaises(Killed):
                    self.one("cut%d" % k, "newer")
                self.assertEqual(len(calls), k)
                self.assertFalse(RUN.current(os.path.join(top, "rows", "0001.csv"), "newer", True))


class Stamp(unittest.TestCase):
    """The stamp of a run with the lines follows the drawing's code, and a run's without them does not."""

    def test_a_change_to_the_drawing_changes_the_lines_stamp_alone(self):
        rows, lines = RUN.code_stamp(False), RUN.code_stamp(True)
        real = RUN.read_bytes
        edited = lambda path: real(path) + (b"# edited\n" if path.endswith(RUN.LINES_SOURCE) else b"")  # noqa: E731
        with mock.patch.object(RUN, "read_bytes", edited):
            self.assertEqual(RUN.code_stamp(False), rows)
            self.assertNotEqual(RUN.code_stamp(True), lines)


class Pool:
    """A pool whose first study is measured here and whose every later one finds its worker dead."""

    def __init__(self, workers: int):
        self.submitted = 0

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def submit(self, fn, job) -> Future:
        f: Future = Future()
        self.submitted += 1
        if self.submitted == 1:
            f.set_result(fn(job))
        else:
            f.set_exception(BrokenProcessPool("a worker was killed"))
        return f


class CutShort(unittest.TestCase):
    """A run a dead worker cuts short joins the lines and frames its own code drew, and only those,
    while rows.csv holds every study's rows, each with its code."""

    def test_the_join_leaves_out_what_older_code_drew(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        masks, out = os.path.join(tmp, "masks"), os.path.join(tmp, "out")
        os.makedirs(masks)
        lab, aff = P.draw(P.straight(LEVELS, P.Vert()), spacing=(0.86, 0.86, 2.5))
        for study in ("0001", "0002"):
            save(lab, aff, masks, study)
        argv = ["run", "--masks", masks, "--scheme", "verse", "--out", out, "--workers", "1", "--lines"]
        run(argv)
        before = RUN.code_stamp(True)
        with mock.patch.object(RUN, "code_stamp", lambda lines=False: "later"), \
                mock.patch.object(RUN, "ProcessPoolExecutor", Pool):
            said = run(argv)
        self.assertIn("a worker died", said)
        codes = {r["study"]: r["note"] for r in read(os.path.join(out, "rows.csv")) if r["key"] == "code"}
        self.assertEqual(codes, {"0001": "later", "0002": before})
        for name in ("lines", "frames"):
            self.assertEqual({r["study"] for r in read(os.path.join(out, name + ".csv"))}, {"0001"}, name)
            self.assertFalse(os.path.exists(os.path.join(out, name + ".csv.part")), name)


class SameLines(unittest.TestCase):
    """The pedicles' lines drawn on the measure's own reading are the lines read again, on a whole
    vertebra and on one the volume's edge cuts, where the measure's values are blanked."""

    def lines_both_ways(self, lab: np.ndarray, aff: np.ndarray, level: str) -> tuple:
        kept: dict = {}
        M.measure_volume(lab, G.VoxelGrid(aff, lab.shape), {P.LEVEL_IDS[lv]: lv for lv in LEVELS}, "same",
                         pelvis=False, keep=kept)
        v, ped, vals = kept["verts"][level], kept["peds"][level], kept["values"][level]
        return LN.checked(LN.vertebra_lines(v, ped), vals), LN.checked(LN.vertebra_lines(v, ped, vals), vals)

    def test_the_measures_reading_draws_what_reading_again_draws(self):
        lab, aff = P.draw(P.straight(LEVELS, P.Vert()), spacing=(0.8, 0.8, 1.0))
        for name, (vol, at), level in (("whole", (lab, aff), "L3"), ("cut", cut_below(lab, aff, "L4"), "L4")):
            with self.subTest(name):
                self.same(*self.lines_both_ways(vol, at, level))

    def same(self, again: list, reused: list) -> None:
        self.assertEqual([ln.key for ln in again], [ln.key for ln in reused])
        self.assertTrue(any(ln.key.startswith("pedicle_") for ln in reused))
        for x, y in zip(again, reused):
            self.assertEqual((x.status, x.rule, x.panel), (y.status, y.rule, y.panel), x.key)
            np.testing.assert_array_equal([x.value, x.measured], [y.value, y.measured], err_msg=x.key)
            np.testing.assert_array_equal(x.a, y.a)
            np.testing.assert_array_equal(x.b, y.b)


if __name__ == "__main__":
    unittest.main()

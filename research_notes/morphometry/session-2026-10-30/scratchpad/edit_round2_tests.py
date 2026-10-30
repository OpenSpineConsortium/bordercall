"""Round two of the tests: the files' geometry whole, the ends named, the frame's axis."""
import sys
root = sys.argv[1]
path = root + "/morphometry/tests/test_lines_export.py"
src = open(path).read()

def swap(old, new):
    global src
    assert src.count(old) == 1, (old[:70], src.count(old))
    src = src.replace(old, new)

swap('''LEVELS = ["L2", "L3", "L4"]
ROUNDING = 1e-4                 # every number in the files is written to four places
''', '''LEVELS = ["L2", "L3", "L4"]
ROUNDING = 1e-4                 # the rows and the lines' measured column are written to four places
WHOLE = 1e-9                    # the ends, the frames and a construction's value are written whole
''')
swap('''# the four places of an axis's components leave a direction up to about 1e-4 off, which over a
# line's 80 mm moves one end's coordinate 0.008 mm against the other's
SHARED_MM = 0.01
''', '''SHARED_MM = 1e-6
# which way each end's name lies along the frame's axes: (axis, sign of b less a)
ORDER = {("inferior", "superior"): (2, 1), ("superior", "inferior"): (2, -1), ("posterior", "anterior"): (1, 1),
         ("anterior", "posterior"): (1, -1), ("left", "right"): (0, 1), ("canal", "tip"): (1, -1)}
''')
swap('''    def test_every_one_of_panjabis_seven_chords_is_drawn(self):
        for level in LEVELS:
            drawn = {r["key"] for r in self.main if (r["study"], r["level"]) == ("0001", level) and r["status"] == "drawn"}
            self.assertEqual(set(SEVEN) - drawn, set(), level)
''', '''    def test_every_one_of_panjabis_seven_chords_is_drawn(self):
        for level in LEVELS:
            drawn = {r["key"] for r in self.main if (r["study"], r["level"]) == ("0001", level) and r["status"] == "drawn"}
            self.assertEqual(set(SEVEN) - drawn, set(), level)

    def test_the_keys_drawn_are_the_ones_the_lines_name(self):
        for level, keys in (("L3", LN.VERTEBRA_KEYS), ("L2-L3", LN.DISC_KEYS)):
            got = [r["key"] for r in self.main if (r["study"], r["level"]) == ("0001", level)]
            self.assertEqual(sorted(got), sorted(keys), level)
        for r in self.lines:
            self.assertTrue(r["a_end"] and r["b_end"], "%s %s %r" % (r["key"], r["part"], (r["a_end"], r["b_end"])))
''')
swap('''    def test_a_drawn_line_holds_the_rows_value(self):
        for r in self.main:
            if r["status"] == "drawn":
                self.assertEqual(r["value"], self.value(r["study"], r["level"], r["key"]), r["key"])
                self.assertEqual(r["measured"], r["value"], r["key"])
''', '''    def test_a_drawn_line_holds_the_rows_value(self):
        for r in self.main:
            if r["status"] == "drawn":
                self.assertEqual(r["measured"], self.value(r["study"], r["level"], r["key"]), r["key"])
                self.assertLessEqual(abs(float(r["value"]) - float(r["measured"])), 0.5 * ROUNDING + WHOLE, r["key"])
''')
swap('''                self.assertAlmostEqual(float(np.linalg.norm(b - a)), float(r["value"]), delta=4 * ROUNDING, msg=r["key"])
''', '''                self.assertAlmostEqual(float(np.linalg.norm(b - a)), float(r["value"]), delta=WHOLE, msg=r["key"])
                self.assertAlmostEqual(float(r["drawn"]), float(r["value"]), delta=WHOLE, msg=r["key"])
''')
swap('''            np.testing.assert_allclose(R @ R.T, np.eye(3), atol=4 * ROUNDING)
            self.assertAlmostEqual(float(np.linalg.det(R)), 1.0, delta=4 * ROUNDING)
''', '''            np.testing.assert_allclose(R @ R.T, np.eye(3), atol=WHOLE)
            self.assertAlmostEqual(float(np.linalg.det(R)), 1.0, delta=WHOLE)
''')
swap('''            np.testing.assert_allclose(got, want, atol=2 * ROUNDING, err_msg=level)
''', '''            np.testing.assert_allclose(got, want, atol=WHOLE, err_msg=level)
''')
swap('''    def local(self, level: str) -> dict:
        """{key: (a, b)}, each line's two ends in its vertebra's written frame."""
        f = self.frames[level]
        o = np.array([float(f["o" + a]) for a in "xyz"])
        R = np.array([[float(f[e + a]) for a in "xyz"] for e in ("ex", "ey", "ez")])
        end = lambda r, p: R @ (np.array([float(r[p + a]) for a in "xyz"]) - o)  # noqa: E731
        return {r["key"]: (end(r, "a"), end(r, "b")) for r in self.main if r["level"] == level}
''', '''    def to_local(self, level: str, rows: list) -> list:
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
''')
swap('''            self.assertGreater(min(ends["pedicle_w_right"][0][0], ends["pedicle_w_right"][1][0]), 0.0, level)
            self.assertLess(max(ends["pedicle_w_left"][0][0], ends["pedicle_w_left"][1][0]), 0.0, level)
''', '''            self.assertGreater(min(ends["pedicle_w_right"][0][0], ends["pedicle_w_right"][1][0]), 0.0, level)
            self.assertLess(max(ends["pedicle_w_left"][0][0], ends["pedicle_w_left"][1][0]), 0.0, level)

    def test_each_end_lies_where_its_name_says(self):
        levels = sorted({r["level"] for r in self.lines})
        self.assertIn("L2-L3", levels)
        for level in levels:
            for r, a, b in self.to_local(level, self.lines):
                names = (r["a_end"], r["b_end"])
                where = "%s %s %s %s" % (level, r["key"], r["part"], names)
                if names == ("medial", "lateral"):
                    self.assertGreater(abs(b[0]), abs(a[0]), where)
                else:
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
''')
swap('''import contextlib
import csv
import io
import os
''', '''import contextlib
import csv
import io
import math
import os
''')
swap('''        run(["run", "--masks", masks, "--scheme", "verse", "--out", out, "--workers", "1", "--lines"])
        cls.main = [r for r in read(os.path.join(out, "lines.csv")) if r["part"] == ""]
''', '''        run(["run", "--masks", masks, "--scheme", "verse", "--out", out, "--workers", "1", "--lines"])
        cls.lines = read(os.path.join(out, "lines.csv"))
        cls.main = [r for r in cls.lines if r["part"] == ""]
        cls.rows = read(os.path.join(out, "rows.csv"))
''')
swap('''frame is written in the world the ends are written in, its origin
the label's centroid, and on a column whose vertebrae lean against its line each line's ends lie
in it as their builder placed them.''', '''frame is written in the world the ends are written in, its origin
the centroid of the label's main piece, and on a column whose vertebrae lean against its line each
line's ends lie in it as their builder placed them and where their names say, and each frame
names the axis its z lies along. The geometry is written whole, to the bit.''')
open(path, "w").write(src)
print("ok")

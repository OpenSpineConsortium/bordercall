"""The facts a column's names give, its offsets, and its files."""
import math
import os
import tempfile
import unittest

from scanimport import column as C

SPINE = ["C%d" % i for i in range(1, 8)] + ["T%d" % i for i in range(1, 13)] + ["L%d" % i for i in range(1, 6)] + ["sacrum"]
ALL = {"L6": True, "T13": True}


class Facts(unittest.TestCase):
    def test_typical_whole_spine_is_countable(self):
        f = C.facts_from_levels(SPINE, ALL)
        self.assertTrue(f["countable"] and f["has_c2"] and f["has_sacrum"])
        self.assertEqual(f["phenotype"], "typical")
        self.assertEqual(f["n_lumbar"], 5)

    def test_a_scheme_that_cannot_say_L6_never_says_typical(self):
        f = C.facts_from_levels(SPINE, {"L6": False, "T13": False})
        self.assertEqual(f["phenotype"], "typical_as_far_as_the_scheme_says")

    def test_anomalies(self):
        t13 = SPINE[:19] + ["T13"] + SPINE[19:]
        six = SPINE[:-1] + ["L6", "sacrum"]
        four = SPINE[:-2] + ["sacrum"]
        self.assertEqual(C.facts_from_levels(t13, ALL)["phenotype"], "t13")
        self.assertEqual(C.facts_from_levels(six, ALL)["phenotype"], "six_lumbar")
        self.assertEqual(C.facts_from_levels(four, ALL)["phenotype"], "four_lumbar")
        self.assertTrue(C.facts_from_levels(six, ALL)["countable"])

    def test_a_missing_body_or_no_c2_is_not_a_count(self):
        gap = [lv for lv in SPINE if lv != "T7"]
        self.assertFalse(C.facts_from_levels(gap, ALL)["countable"])
        self.assertIn("missing", C.facts_from_levels(gap, ALL)["count_basis"])
        lumbar = ["T12", "L1", "L2", "L3", "L4", "L5", "sacrum"]
        f = C.facts_from_levels(lumbar, ALL)
        self.assertFalse(f["countable"])
        self.assertEqual(f["phenotype"], "unknown")       # a T13 could be hiding above


class Offsets(unittest.TestCase):
    def test_gaps_and_order(self):
        self.assertEqual(C.offsets_of(["T11", "T12", "L2"]), [0, 1, 3])
        self.assertEqual(C.offsets_of(["T12", "T13", "L1"]), [0, 1, 2])
        self.assertIsNone(C.offsets_of(["L1", "T12"]))
        self.assertIsNone(C.offsets_of(["T12", "?"]))


class Files(unittest.TestCase):
    def test_roundtrip_with_missing_values(self):
        col = C.Column(study={"study_id": "s1", "countable": False, "modality": "ct"},
                       bodies=[C.Body("L1", {"endplate": 40.123456, "h_post": math.nan}, {}, {"h_post": "cut"}),
                               C.Body("L3", {"endplate": 44.0})])
        with tempfile.TemporaryDirectory() as d:
            C.write_column(col, d)
            back = C.read_columns(d)[0]
            self.assertEqual(back.levels, ["L1", "L3"])
            self.assertAlmostEqual(back.bodies[0].values["endplate"], 40.123, places=6)
            self.assertTrue(math.isnan(back.bodies[0].values["h_post"]))
            with open(os.path.join(d, "fields", "s1.csv")) as fh:
                lines = fh.read().splitlines()
            self.assertEqual(lines[0], "# study s1")
            self.assertTrue(lines[3].startswith("body,offset,level,endplate"))
            self.assertTrue(lines[5].startswith("1,2,L3,44.0"))
            C.write_tables(d, [back])
            self.assertTrue(os.path.exists(os.path.join(d, "bodies.csv")))

    def test_not_a_column(self):
        with self.assertRaises(ValueError):
            C.Column.from_json({"format": "something else"})


if __name__ == "__main__":
    unittest.main()

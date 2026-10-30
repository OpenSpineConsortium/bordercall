"""The truth join against hand cases and the recorded VerSe Genant join
(records/verse-genant-2026-10-29/), whose aggregates re-derive from its joined.csv to the digit."""
from __future__ import annotations

import csv
import json
import math
import os
import shutil
import tempfile
import unittest

from screening import truth as T
from screening.contracts import ViolationError

RECORD = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                      "records", "verse-genant-2026-10-29")


class PureTest(unittest.TestCase):
    def test_implied_grade_at_genants_cuts(self):
        self.assertEqual([T.implied_grade(r) for r in (0.80, 0.7999, 0.75, 0.7499, 0.60, 0.5999, 1.2)], [0, 1, 1, 2, 2, 3, 0])
        with self.assertRaises(ViolationError):
            T.implied_grade(math.nan)

    def test_smaller_ratio_and_grade_of(self):
        self.assertEqual(T.smaller_ratio({"body_index_ant_post": 0.9, "body_index_mid_post": 0.85}), 0.85)
        self.assertEqual(T.smaller_ratio({"body_index_ant_post": 0.9, "h_ant": 20.0}), 0.9)
        self.assertIsNone(T.smaller_ratio({"h_ant": 20.0}))
        self.assertIsNone(T.smaller_ratio({"body_index_ant_post": math.nan}))
        self.assertEqual([T.grade_of(c) for c in ("0", " 3 ", "5", "8", "", "x")], [0, 3, None, None, None, None])

    def test_region_and_reading_order(self):
        self.assertEqual([T.region_of(n) for n in ("T4", "L1", "C5", "sacrum")], ["thoracic", "lumbar", "cervical", "cervical"])
        a = {"study": "verse009", "ratios_read": 1, "voxels": 900, "truth": 0}
        b = {"study": "verse002", "ratios_read": 2, "voxels": 100, "truth": 0}
        c = {"study": "verse001", "ratios_read": 2, "voxels": 100, "truth": 0}
        self.assertEqual([x["study"] for x in T.reading_order([a, b, c])], ["verse001", "verse002", "verse009"])
        with self.assertRaises(ViolationError):
            T.reading_order([])

    def test_detect_by_hand(self):
        items = [{"ratio": 0.9, "truth": 0, "person": "p1", "level": "T6", "region": "thoracic"},
                 {"ratio": 0.85, "truth": 0, "person": "p2", "level": "L1", "region": "lumbar"},
                 {"ratio": 0.7, "truth": 2, "person": "p1", "level": "T8", "region": "thoracic"},
                 {"ratio": 0.85, "truth": 1, "person": "p3", "level": "L2", "region": "lumbar"}]
        d = T.detect(items, "all")
        self.assertEqual((d["vertebrae"], d["persons"], d["grade0"], d["grade1plus"], d["grade2plus"]), (4, 3, 2, 2, 1))
        self.assertEqual(d["auc_grade1plus"], 0.875)
        self.assertEqual(d["auc_grade2plus"], 1.0)
        self.assertEqual(d["sens_grade1plus_at_0.80"], 0.5)
        self.assertEqual(d["spec_at_0.80"], 1.0)
        self.assertEqual(d["grade0_below_0.80_count"], 0)
        with self.assertRaises(ViolationError):
            T.detect([{"ratio": math.nan, "truth": 0, "person": "p"}], "all")

    def test_agreement_and_groups(self):
        read = [{"truth": 0, "ratio": 0.9}, {"truth": 1, "ratio": 0.77}, {"truth": 3, "ratio": 0.5}, {"truth": 2, "ratio": 0.9}]
        a = T.agreement(read)
        self.assertEqual(a["rows_readers_grade_cols_implied_grade"], [[1, 0, 0, 0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]])
        self.assertEqual(a["exact"], 0.75)
        self.assertEqual(T.agreement([]), {})
        items = [{"person": "b", "truth": 0, "ratio": 0.9}, {"person": "a", "truth": 2, "ratio": 0.6}, {"person": "b", "truth": 1, "ratio": 0.7}]
        self.assertEqual(T.groups_by_person(items, 1), [([], [0.6]), ([0.9], [0.7])])
        self.assertEqual(T.groups_by_person(items, 2), [([], [0.6]), ([0.9, 0.7], [])])


class TableTest(unittest.TestCase):
    def test_riedels_cells_and_the_truth_form(self):
        text = "verse;T4;T5;L1\n4;0;1;\n9;;5;3\n;\n"
        cells = T.riedel_cells(text)
        self.assertEqual(cells, [{"study": "verse4", "level": "T4", "code": "0"}, {"study": "verse4", "level": "T5", "code": "1"},
                                 {"study": "verse9", "level": "T5", "code": "5"}, {"study": "verse9", "level": "L1", "code": "3"}])
        rows, not_grades = T.truth_rows(cells)
        self.assertEqual([r["truth"] for r in rows], [0, 1, 3])
        self.assertEqual(dict(not_grades), {"5": 1})


class JoinTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def measures(self, rows):
        path = os.path.join(self.tmp, "rows.csv")
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["study", "level", "key", "value", "note"], lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        return T.read_measures(path)

    def test_one_reading_per_persons_level_with_duplicates_and_reasons(self):
        rows = [{"study": "s1", "level": "study", "key": "coarsest_mm", "value": "1.0", "note": ""},
                {"study": "s1", "level": "L1", "key": "body_index_ant_post", "value": "0.9", "note": ""},
                {"study": "s1", "level": "L1", "key": "body_index_mid_post", "value": "0.7", "note": ""},
                {"study": "s1", "level": "L1", "key": "h_ant", "value": "25.0", "note": ""},
                {"study": "s2", "level": "study", "key": "coarsest_mm", "value": "2.0", "note": ""},
                {"study": "s2", "level": "L1", "key": "body_index_ant_post", "value": "0.95", "note": ""},
                {"study": "s2", "level": "L1", "key": "body_index_mid_post", "value": "", "note": "the mid chord did not read"},
                {"study": "s2", "level": "L2", "key": "body_index_ant_post", "value": "", "note": "the body touches the edge of the volume"},
                {"study": "s2", "level": "L2", "key": "body_index_mid_post", "value": "", "note": "the body touches the edge of the volume"},
                {"study": "s2", "level": "L2", "key": "flag:pedicle", "value": "", "note": "no pedicle"}]
        truths = [{"study": "s1", "level": "L1", "truth": 0, "person": ""}, {"study": "s2", "level": "L1", "truth": 1, "person": ""},
                  {"study": "s2", "level": "L2", "truth": 2, "person": ""}, {"study": "s2", "level": "L3", "truth": 0, "person": ""},
                  {"study": "s3", "level": "L1", "truth": 0, "person": ""}]
        persons = {"s1": "p", "s2": "p", "s3": "q"}
        held = {"s2": {"L1": 100, "L2": 100}, "s1": {"L1": 100}}
        joined, counts = T.join(truths, self.measures(rows), persons, held)
        self.assertEqual({k: counts[k] for k in ("cells_graded", "vertebrae", "duplicates_dropped", "conflicting_duplicates")},
                         {"cells_graded": 5, "vertebrae": 4, "duplicates_dropped": 1, "conflicting_duplicates": 1})
        by = {(r["person"], r["level"]): r for r in joined}
        l1 = by[("p", "L1")]
        self.assertEqual((l1["study"], l1["smaller_ratio"], l1["ratios_read"], l1["duplicates"], l1["coarsest_mm"]), ("s1", 0.7, 2, ["s2"], 1.0))
        self.assertEqual(by[("p", "L2")]["no_reading"], ["the body touches the edge of the volume", "no pedicle"])
        self.assertEqual(by[("p", "L3")]["no_reading"], ["level not in the mask"])
        self.assertEqual(by[("q", "L1")]["no_reading"], ["study not measured"])
        out = os.path.join(self.tmp, "joined.csv")
        T.write_joined(joined, out)
        back = T.read_joined(out)
        self.assertEqual([r["study"] for r in back], [r["study"] for r in joined])
        self.assertEqual(back[0]["no_reading"], joined[0]["no_reading"])
        self.assertEqual(back[0]["duplicates"], joined[0]["duplicates"])

    def test_aggregates_with_identity_picks(self):
        joined = [{"study": "s1", "person": "p1", "level": "T6", "region": "thoracic", "truth": 0, "smaller_ratio": 0.9, "ratios_read": 2,
                   "coarsest_mm": 1.0, "slice_mm": 1.0, "duplicates": [], "no_reading": [], "h_ant": 20.0, "h_mid": 19.0,
                   "h_post_inset": 21.0, "body_index_ant_post": 0.95, "body_index_mid_post": 0.9},
                  {"study": "s2", "person": "p2", "level": "T8", "region": "thoracic", "truth": 2, "smaller_ratio": 0.6, "ratios_read": 1,
                   "coarsest_mm": 2.0, "slice_mm": 2.0, "duplicates": [], "no_reading": [], "h_ant": 12.0, "h_mid": 11.0,
                   "h_post_inset": 20.0, "body_index_ant_post": 0.6, "body_index_mid_post": None},
                  {"study": "s3", "person": "p3", "level": "L1", "region": "lumbar", "truth": 3, "smaller_ratio": None, "ratios_read": 0,
                   "coarsest_mm": None, "slice_mm": None, "duplicates": [], "no_reading": ["study not measured"], "h_ant": None,
                   "h_mid": None, "h_post_inset": None, "body_index_ant_post": None, "body_index_mid_post": None}]
        agg = T.aggregates(joined, {"vertebrae": 3}, [[0, 1], [1, 0]])
        self.assertEqual(agg["detection"][0]["auc_grade1plus_ci95"], [1.0, 1.0])
        self.assertEqual(agg["detection"][0]["auc_grade2plus_ci95"], [1.0, 1.0])
        self.assertEqual(agg["no_reading"], {"vertebrae": 1, "by_grade": {"3": 1}, "reasons": {"study not measured": 1}, "one_ratio_only": 1})
        self.assertEqual(agg["per_grade"]["2"]["h_post_inset"], {"n": 1, "q1": 20.0, "median": 20.0, "q3": 20.0})
        self.assertEqual([d["stratum"] for d in agg["detection"]][:3], ["all", "thoracic", "lumbar"])


class RecordTest(unittest.TestCase):
    """The recorded VerSe join re-derives from joined.csv: the same aggregates, bootstrap included."""

    def test_the_record_re_derives(self):
        joined = T.read_joined(os.path.join(RECORD, "joined.csv"))
        with open(os.path.join(RECORD, "aggregates.json")) as f:
            want = json.load(f)
        self.assertEqual(len(joined), 3674)
        persons = len({r["person"] for r in joined if r["smaller_ratio"] is not None})
        self.assertEqual(persons, 320)
        got = T.aggregates(joined, want["counts"], T.picks_from_numpy(T.SEED, persons, T.BOOT))
        self.assertEqual(got["detection"], want["detection"])
        self.assertEqual(got["agreement"], want["agreement"])
        self.assertEqual(got["no_reading"], want["no_reading"])
        self.assertEqual(got["per_grade"], want["per_grade"])
        self.assertEqual(got["detection"][0]["auc_grade1plus"], 0.8362)

    def test_neighbour_rows_on_the_record(self):
        rows = T.neighbour_rows(T.read_joined(os.path.join(RECORD, "joined.csv")))
        self.assertTrue(all(set(r) == {"truth", "caught", "n", "median_post_over_neighbours", "share_under_0.80"} for r in rows))
        self.assertEqual(sorted({r["truth"] for r in rows}), [0, 1, 2, 3])


if __name__ == "__main__":
    unittest.main()

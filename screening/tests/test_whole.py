"""The whole-spine rules against hand-made spines, numpy's inverse, and SchwingNet's own classes
and verdicts on recorded samples of the three members (tests/fixtures/*-sample.jsonl, each row
with the class tools/gold3_ct.py gave it and the verdict data/gold3-ct/admission.json holds)."""
from __future__ import annotations

import json
import math
import os
import unittest

import numpy as np

from screening import ORDER, rank
from screening import whole as W
from screening.contracts import ViolationError

HERE = os.path.dirname(os.path.abspath(__file__))
FULL = [n for n in ORDER if n not in ("T13", "L6")]


def spine(names, top=1000.0, height=30.0, step=25.0, voxels=5000, cut=(), field=(2000.0, -2000.0)):
    """A study whose levels stand `step` apart with `height` each, so neighbours overlap by 5 mm;
    the sacrum takes the slot after the last lumbar name given."""
    levels = {}
    for name in names:
        slot = rank(name) if name != "sacrum" else rank(names[-2]) + 1 if len(names) > 1 else rank("L5") + 1
        t = top - slot * step
        levels[name] = {"voxels": voxels, "top": t, "bottom": t - height, "centre": t - height / 2,
                        "head_cut": name in cut, "foot_cut": name in cut, "side_cut": False,
                        "field_top": field[0], "field_bottom": field[1]}
    return {"member": "test", "id": "x", "person": None, "age": None, "site": None,
            "top": field[0], "bottom": field[1], "levels": levels, "image_planes": [False, False]}


class MaskRuleTest(unittest.TestCase):
    def test_a_full_spine_is_strict(self):
        s = spine(FULL)
        self.assertEqual(W.count_class(s), "strict")
        self.assertEqual(W.whole_problems(s), [])
        self.assertEqual(W.label_pattern(s), "C2 to L5 named")
        self.assertEqual(W.call_by_names(s), {"thoracic": 12, "lumbar": 5, "presacral": 24, "call": "T12L5"})

    def test_no_l5_when_l4_meets_the_sacrum(self):
        s = spine([n for n in FULL if n != "L5"])
        self.assertEqual(W.count_class(s), "no_l5")
        self.assertEqual(W.label_pattern(s), "no L5, L4 meeting the sacrum")
        self.assertEqual(W.call_by_names(s)["call"], "T12L4")

    def test_a_lumbar_gap_is_whole_and_listed_for_a_look(self):
        s = spine([n for n in FULL if n != "L3"])
        self.assertEqual(W.count_class(s), "lumbar_look")
        self.assertEqual(W.label_pattern(s), "lumbar label missing: L3")
        self.assertEqual(W.whole_problems(s), [])

    def test_missing_ends_and_skipped_labels(self):
        self.assertEqual(W.count_class(spine([n for n in FULL if n != "C2"])), "no_c2")
        self.assertEqual(W.count_class(spine([n for n in FULL if n != "sacrum"])), "no_sacrum")
        s = spine([n for n in FULL if n != "T5"])
        self.assertEqual(W.count_class(s), "skipped_label")
        self.assertEqual(W.whole_problems(s), ["T5 missing"])
        self.assertEqual(W.whole_problems(spine(["C3", "sacrum"])), ["no C2"])

    def test_a_wide_space_above_t12_holds_an_unlabelled_body(self):
        s = spine(FULL)
        for name in FULL[rank("T8"):]:
            for key in ("top", "bottom", "centre"):
                s["levels"][name][key] -= 30.0
        self.assertEqual(W.count_class(s), "unlabelled_body")
        self.assertEqual(W.whole_problems(s), ["a space of 25.0 mm between T7 and T8"])

    def test_a_fragment_l5_and_an_l6(self):
        s = spine(FULL)
        s["levels"]["L5"]["voxels"] = 500
        s["levels"]["sacrum"]["top"] = s["levels"]["L4"]["bottom"] + 6.0
        self.assertTrue(W.l5_fragment(s))
        self.assertEqual(W.label_pattern(s), "L5 label a fragment, L4 meeting the sacrum")
        six = spine([*FULL[:-1], "L6", "sacrum"])
        self.assertEqual(W.label_pattern(six), "L6 named below an L5")
        self.assertEqual(W.count_class(six), "strict")
        no5 = spine([n for n in [*FULL[:-1], "L6", "sacrum"] if n != "L5"])
        self.assertEqual(W.label_pattern(no5), "no L5, an L6 in its place")

    def test_a_level_under_the_floor_is_not_drawn(self):
        s = spine(FULL)
        s["levels"]["sacrum"]["voxels"] = 199
        self.assertEqual(W.count_class(s), "no_sacrum")
        self.assertEqual(W.gap_mm({"bottom": 10.0}, {"top": 12.5}), -2.5)
        with self.assertRaises(ViolationError):
            W.gap_mm({"bottom": math.nan}, {"top": 1.0})


HEAD = {"C3 to C2's foot": {"n": 30, "low": -15.0, "median": -9.0, "high": -5.0}, "C4 to C2's foot": {"n": 5}}
FOOT = {"last lumbar": {"n": 30, "low": -10.0, "median": 0.0, "high": 5.0}, "L2": {"n": 3}}


class FieldRuleTest(unittest.TestCase):
    def test_both_ends_drawn_is_admitted(self):
        s = spine(FULL)
        self.assertEqual(W.head_end(s, HEAD), ("drawn", {}))
        self.assertEqual(W.foot_end(s, FOOT), ("drawn", {}))
        self.assertEqual(W.judge(s, {"head": HEAD, "foot": FOOT})["verdict"], "admitted")

    def test_an_undrawn_c2_is_placed_by_the_head_table(self):
        # no C1 either: a C1 drawn above an undrawn C2 is its own case below
        s = spine([n for n in FULL if n not in ("C1", "C2")])
        c3 = s["levels"]["C3"]
        c3["field_top"] = c3["top"] + 0.0
        self.assertEqual(W.head_end(s, HEAD)[0], "in_view")
        c3["field_top"] = c3["top"] - 10.0
        self.assertEqual(W.head_end(s, HEAD)[0], "border")
        c3["field_top"] = c3["top"] - 20.0
        self.assertEqual(W.head_end(s, HEAD)[0], "out")
        s4 = spine([n for n in FULL if n not in ("C1", "C2", "C3")])
        self.assertIn("fewer than", W.head_end(s4, HEAD)[1]["why"])
        self.assertEqual(W.head_end(s4, HEAD)[0], "border")

    def test_a_head_most_level_cut_by_the_top_is_out_and_a_sliver_of_c2_too(self):
        s = spine([n for n in FULL if n not in ("C1", "C2")], cut=("C3",))
        self.assertEqual(W.head_end(s, HEAD)[0], "out")
        sliver = spine(FULL, cut=("C2", "C3"))
        self.assertEqual(W.head_end(sliver, HEAD)[0], "out")
        only_c2 = spine(FULL, cut=("C2",))
        self.assertEqual(W.head_end(only_c2, HEAD)[0], "drawn")
        self.assertIn("c2_at_field_top", W.flags(only_c2, "drawn", "drawn"))

    def test_c1_alone_and_c1_above_an_undrawn_c2(self):
        self.assertEqual(W.head_end(spine(["C1"]), HEAD)[0], "border")
        self.assertEqual(W.head_end(spine([n for n in FULL if n != "C2"]), HEAD)[0], "in_view")
        self.assertEqual(W.head_end(spine(["sacrum"]), HEAD)[0], "no_column")

    def test_an_undrawn_sacrum_is_placed_by_the_foot_table(self):
        s = spine([n for n in FULL if n != "sacrum"])
        l5 = s["levels"]["L5"]
        l5["field_bottom"] = l5["bottom"] - 10.0
        self.assertEqual(W.foot_end(s, FOOT)[0], "in_view")
        l5["field_bottom"] = l5["bottom"] - 2.0
        self.assertEqual(W.foot_end(s, FOOT)[0], "border")
        l5["field_bottom"] = l5["bottom"] + 6.0
        self.assertEqual(W.foot_end(s, FOOT)[0], "out")
        cut = spine([n for n in FULL if n != "sacrum"], cut=("L5",))
        self.assertEqual(W.foot_end(cut, FOOT)[0], "out")
        short = spine([n for n in FULL if rank(n) <= rank("L2")])
        self.assertEqual(W.foot_end(short, FOOT)[0], "border")

    def test_s1_view_asks_for_more_of_the_sacrum(self):
        s = spine(FULL, cut=("sacrum",))
        s["levels"]["sacrum"]["field_bottom"] = s["levels"]["sacrum"]["top"] - 5.0
        self.assertEqual(W.foot_end(s, FOOT)[0], "drawn")
        self.assertEqual(W.foot_end(s, FOOT, s1_view=20.0)[0], "border")
        self.assertEqual(W.sacrum_held(s), 5.0)
        self.assertIn("sacrum_at_field_foot", W.flags(s, "drawn", "drawn"))

    def test_verdicts(self):
        self.assertEqual(W.verdict_of("drawn", "in_view"), "admitted")
        self.assertEqual(W.verdict_of("border", "drawn"), "look")
        self.assertEqual(W.verdict_of("out", "drawn"), "not_admitted")
        self.assertEqual(W.verdict_of("drawn", "no_column"), "not_admitted")
        with self.assertRaises(ViolationError):
            W.verdict_of("bogus", "drawn")

    def test_a_gap_is_completed_and_a_skipped_name_is_flagged(self):
        gap = spine([n for n in FULL if n != "T7"])
        self.assertEqual(W.name_runs(gap), (["T7"], []))
        self.assertEqual(W.judge(gap, {"head": HEAD, "foot": FOOT})["complete"], ["T7"])
        skipped = spine([n for n in FULL if n != "T7"])
        for name in FULL[rank("T8"):]:
            for key in ("top", "bottom", "centre"):
                skipped["levels"][name][key] += 25.0
        self.assertEqual(W.name_runs(skipped), ([], ["T7"]))
        self.assertIn("name_skipped", W.flags(skipped, "drawn", "drawn"))
        two = spine([n for n in FULL if n not in ("T7", "T8")])
        self.assertEqual(W.name_runs(two)[0], ["T7", "T8"])

    def test_completion_of_an_undrawn_c2_and_sacrum(self):
        s = spine([n for n in FULL if n not in ("C2", "C3", "sacrum", "L5")])
        self.assertEqual(W.completion(s, "in_view", "in_view"), ["C2", "C3", "sacrum"])
        short = spine([n for n in FULL if rank(n) <= rank("L2")])
        self.assertEqual(W.completion(short, "drawn", "in_view"), ["L3", "L4", "L5", "sacrum"])
        self.assertEqual(W.to_complete(s, "not_admitted", "out", "in_view"), [])
        self.assertEqual(W.to_complete(s, "look", "border", "border"), ["C2", "C3", "sacrum"])

    def test_study_flags(self):
        s = spine(FULL)
        s["levels"]["T13"] = {**s["levels"]["T12"], "voxels": 100}
        s["age"] = 10
        self.assertEqual(W.flags(s, "drawn", "drawn"), ["stray_labels", "child"])
        small = spine(FULL, step=10.0, height=12.0)
        self.assertIn("small_column", W.flags(small, "drawn", "drawn"))
        tall = spine(FULL)
        tall["levels"]["T1"]["top"] += 200.0
        self.assertEqual(W.tall_labels(tall), ["T1"])
        self.assertIn("label_spans_levels", W.flags(tall, "drawn", "drawn"))
        no5 = spine([n for n in FULL if n != "L5"])
        self.assertIn("no_l5", W.flags(no5, "drawn", "drawn"))

    def test_tables_from_hand_made_spines(self):
        studies = [spine(FULL, top=1000.0 + k) for k in range(25)]
        t = W.tables(studies)
        self.assertEqual(t["head"]["C3"], {"n": 25, "low": 25.0, "median": 25.0, "high": 25.0})
        self.assertEqual(t["head"]["C3 to C2's foot"]["median"], -5.0)
        self.assertEqual(t["foot"]["last lumbar"]["median"], 5.0)
        self.assertEqual(t["foot"]["L5"], t["foot"]["last lumbar"])
        self.assertEqual(W.summary([1.0] * 19), {"n": 19})
        self.assertEqual(list(t["head"])[:4], ["C3", "C3 to C2's foot", "C4", "C4 to C2's foot"])


class GeometryTest(unittest.TestCase):
    def test_inverse_against_numpy(self):
        m = [[1.4, 0.4, 0.1], [-0.4, 1.4, 0.0], [0.1, 0.0, 1.5]]
        self.assertTrue(np.allclose(np.array(W.inverse3(m)) @ np.array(m), np.eye(3)))
        with self.assertRaises(ValueError):
            W.inverse3([[1.0, 2.0, 3.0], [2.0, 4.0, 6.0], [0.0, 0.0, 1.0]])
        with self.assertRaises(ViolationError):
            W.inverse3([[1.0, 2.0], [3.0, 4.0]])

    def test_vertical_edges_are_the_faces_on_an_untilted_grid(self):
        affine = [[-0.8, 0.0, 0.0, 100.0], [0.0, 0.8, 0.0, -20.0], [0.0, 0.0, 2.5, -1000.0], [0.0, 0.0, 0.0, 1.0]]
        up, down = W.vertical_edges(affine, [12, 12, 40], [96.0, -16.0, -950.0])
        self.assertAlmostEqual(up, -1000.0 + 39.5 * 2.5)
        self.assertAlmostEqual(down, -1000.0 - 0.5 * 2.5)
        self.assertFalse(W.tilted(affine, 2))

    def test_vertical_edges_lie_within_the_corners_on_a_tilted_grid(self):
        c, s = math.cos(math.radians(10)), math.sin(math.radians(10))
        affine = [[1.0, 0.0, 0.0, 0.0], [0.0, c, -s, 0.0], [0.0, s, c, 0.0], [0.0, 0.0, 0.0, 1.0]]
        shape = [20, 20, 20]
        heights = W.corner_heights(shape, affine)
        up, down = W.vertical_edges(affine, shape, [10.0, 10.0, 10.0])
        self.assertTrue(W.tilted(affine, 2))
        self.assertTrue(min(heights) <= down < up <= max(heights))

    def test_an_enhance_facts_row_refuses_a_tilted_grid(self):
        row = {"id": "t", "mask": {"affine": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.1, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
                                   "shape": [4, 4, 4], "head_foot_axis": 2}, "labels": {}}
        with self.assertRaises(ValueError):
            W.study_from_enhance_facts(row)


class RecordedSamplesTest(unittest.TestCase):
    """SchwingNet's classes and verdicts on recorded rows of the three members, with the package's
    tables (the members' own, tables.json)."""

    def rows(self, name):
        with open(os.path.join(HERE, "fixtures", name + "-sample.jsonl")) as f:
            return [json.loads(line) for line in f]

    def test_enhance_pet_classes_and_verdicts(self):
        table = W.default_tables()
        rows = self.rows("enhance")
        self.assertGreaterEqual(len(rows), 50)
        self.assertEqual(sorted({r["expected"]["count_class"] for r in rows}),
                         ["no_c2", "no_l5", "skipped_label", "strict", "unlabelled_body"])
        for r in rows:
            s = W.study_from_row(r)
            want = r["expected"]
            self.assertEqual(W.count_class(s), want["count_class"], r["id"])
            self.assertEqual(W.whole_problems(s), want["problems"], r["id"])
            self.assertEqual(W.label_pattern(s), want["pattern"], r["id"])
            self.assertEqual(W.call_by_names(s), want["call"], r["id"])
            got = W.judge(s, table)
            for key in ("verdict", "head", "foot", "complete", "flags"):
                if key in r.get("known_difference", {}):
                    continue
                self.assertEqual(got[key], want[key], "%s %s" % (r["id"], key))

    def test_verse_and_totalsegmentator_verdicts(self):
        table = W.default_tables()
        for member in ("verse", "totalsegmentator"):
            rows = self.rows(member)
            self.assertGreaterEqual(len(rows), 20)
            for r in rows:
                got = W.judge(W.study_from_row(r, r.get("age")), table)
                for key in ("verdict", "head", "foot", "complete", "flags"):
                    self.assertEqual(got[key], r["expected"][key], "%s %s %s" % (member, r["id"], key))

    def test_verdict_rows_carry_both_readings(self):
        table = W.default_tables()
        row = W.verdict_row(W.study_from_row(self.rows("enhance")[0]), table)
        self.assertEqual(list(row), list(W.VERDICT_FIELDS))
        self.assertIn(row["count_class"], W.MASK_CLASSES)
        self.assertIn(row["verdict"], ("admitted", "look", "not_admitted"))


if __name__ == "__main__":
    unittest.main()

"""disagree.py and synth_corpus.py on a made-up corpus: the three arms run, every table carries
its denominator, and the count's naming of a thirteenth rib-bearing body is L1."""
from __future__ import annotations

import contextlib
import csv
import io
import os
import shutil
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "bordercall"))

import disagree  # noqa: E402
import panjabi as P  # noqa: E402
import synth_corpus  # noqa: E402


class CountNames(unittest.TestCase):
    def test_a_thirteenth_thoracic_body_is_named_l1_by_the_count(self):
        ref = P.load_reference(measures=synth_corpus.MEASURES)
        rng = np.random.default_rng(0)
        c = P.synthesize(ref, "t13", rng, measures=synth_corpus.MEASURES)
        self.assertIn("T13", c.levels)
        names = synth_corpus.count_names(c)
        self.assertNotIn("T13", names)
        self.assertEqual(names[names.index("T12") + 1:], ["L1", "L2", "L3", "L4", "L5", "L6"])
        self.assertEqual(len(names), len(c.levels))

    def test_a_typical_column_keeps_its_names(self):
        ref = P.load_reference(measures=synth_corpus.MEASURES)
        c = P.synthesize(ref, "typical", np.random.default_rng(0), measures=synth_corpus.MEASURES)
        self.assertEqual(synth_corpus.count_names(c), c.levels)


class Disagree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.counts = synth_corpus.write(cls.tmp, n=150, seed=2)
        cls.levels = os.path.join(cls.tmp, "levels.csv")
        cls.phenotype = os.path.join(cls.tmp, "phenotype.csv")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_arms(self, above, below):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            r = disagree.run(self.levels, self.phenotype, above=above, below=below, folds=5, seed=0)
        return r, buf.getvalue()

    def test_the_thoracolumbar_arms_report_with_denominators(self):
        r, text = self.run_arms("T12", "L1")
        self.assertEqual(r["n"], 150)
        self.assertGreater(r["right"] / r["n"], 0.75)
        self.assertEqual(r["disagreements"], r["n"] - r["right"])
        self.assertIn("against the count names", text)
        self.assertIn("the ribs (independent)", text)
        self.assertIn("circular (for scale, proves nothing)", text)
        # the rib reading moves the name in every column whose lowest rib is not on T12
        moved = self.counts.get("lumbar_rib", 0) + self.counts.get("no_rib_T12", 0)
        self.assertIn("names shifted in %d of 150 ribbed cases" % moved, text)
        # every class row is "disagreements / cases"
        for pretty in ("Typical column", "Rib on a lumbar body"):
            line = next(l for l in text.splitlines() if pretty in l)
            k, n = (int(x) for x in line.split()[-3::2])
            self.assertLessEqual(k, n)
        # the made-up corpus draws the transitional body in its own shape, so the shape disagrees
        # with the count there and the ribs, read independently, side with the shape in most
        in_rib_classes = r["by_class"].get("lumbar_rib", 0) + r["by_class"].get("no_rib_T12", 0)
        self.assertGreater(in_rib_classes, 0)
        self.assertGreaterEqual(r["sided"], 0.6 * in_rib_classes, (r["sided"], in_rib_classes))

    def test_a_level_the_measurement_skipped_leaves_the_arms_whole(self):
        # T5 blank in every case: the circular arm takes the model's own per-level calls as labels,
        # so a gap above the border neither moves its truth nor breaks the refit
        gapped = os.path.join(self.tmp, "gapped.csv")
        with open(self.levels, encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        for row in rows:
            for k in list(row):
                if "_T5_" in k:
                    row[k] = ""
        with open(gapped, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            r = disagree.run(gapped, self.phenotype, above="T12", below="L1", folds=5, seed=0)
        text = buf.getvalue()
        self.assertEqual(r["n"], 150)
        line = next(l for l in text.splitlines() if "circular" in l)
        k, n = (int(x) for x in line.split("scored:")[1].split()[0:3:2])
        self.assertEqual(n, 150)
        self.assertGreaterEqual(k, r["right"])

    def test_rib_labels_hold_at_the_ends_of_the_column(self):
        levels = ["C2", "C3", "T12", "L1", "L2"]
        upper = {"C2", "C3", "T12"}
        # a shift of +1 (the lowest rib on L1): the top level is still above, L1 joins the upper
        self.assertEqual([disagree.rib_label_at(i - 1, upper, levels) for i in range(5)], [1, 1, 1, 1, 0])
        # a shift of -1 (no rib on T12): T12 drops below, the bottom stays below
        self.assertEqual([disagree.rib_label_at(i + 1, upper, levels) for i in range(5)], [1, 1, 0, 0, 0])

    def test_the_class_falls_back_on_the_count_without_ribs(self):
        self.assertEqual(disagree.class_of({"phenotype": "typical", "n_lumbar": "6"}), "typical")
        self.assertEqual(disagree.class_of({"phenotype": "", "n_lumbar": "6"}), "six_lumbar")
        self.assertEqual(disagree.class_of({"phenotype": "", "n_lumbar": "4", "has_sacrum": "1"}), "four_lumbar")
        self.assertEqual(disagree.class_of({"phenotype": "", "n_lumbar": "4"}), "unknown")
        self.assertEqual(disagree.class_of({"phenotype": "", "n_lumbar": "5"}), "unknown")

    def test_the_cervicothoracic_arms_run_and_the_ribs_shift_nothing(self):
        r, text = self.run_arms("C7", "T1")
        self.assertEqual(r["n"], 150)
        self.assertIn("names shifted in 0 of 150 ribbed cases", text)

    def test_rib_shift_reads_the_census_columns(self):
        # bordercall's own phenotype command writes no phenotype_known: a filled rib column counts
        self.assertEqual(disagree.rib_shift({"lowest_rib_bearing": "L1"}, "T12", "L1"), 1)
        self.assertIsNone(disagree.rib_shift({"lowest_rib_bearing": ""}, "T12", "L1"))
        self.assertIsNone(disagree.rib_shift({"lowest_rib_bearing": "L1"}, "C7", "T1"))
        self.assertEqual(disagree.rib_shift({"phenotype_known": "1", "lowest_rib_bearing": "L1"}, "T12", "L1"), 1)
        self.assertEqual(disagree.rib_shift({"phenotype_known": "1", "lowest_rib_bearing": "T11"}, "T12", "L1"), -1)
        self.assertIsNone(disagree.rib_shift({"phenotype_known": "0", "lowest_rib_bearing": "T12"}, "T12", "L1"))
        self.assertEqual(disagree.rib_shift({"phenotype_known": "1", "first_rib_bearing": "T1"}, "C7", "T1"), 0)
        self.assertIsNone(disagree.rib_shift({"phenotype_known": "1"}, "L5", "L6"))


if __name__ == "__main__":
    unittest.main()

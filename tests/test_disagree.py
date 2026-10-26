"""disagree.py and synth_corpus.py on a made-up corpus: the three arms run, every table carries
its denominator, and the count's naming of a thirteenth rib-bearing body is L1."""
from __future__ import annotations

import contextlib
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
        self.assertGreater(r["right"] / r["n"], 0.8)
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

    def test_the_cervicothoracic_arms_run_and_the_ribs_shift_nothing(self):
        r, text = self.run_arms("C7", "T1")
        self.assertEqual(r["n"], 150)
        self.assertIn("names shifted in 0 of 150 ribbed cases", text)

    def test_rib_shift_reads_the_census_columns(self):
        self.assertEqual(disagree.rib_shift({"phenotype_known": "1", "lowest_rib_bearing": "L1"}, "T12", "L1"), 1)
        self.assertEqual(disagree.rib_shift({"phenotype_known": "1", "lowest_rib_bearing": "T11"}, "T12", "L1"), -1)
        self.assertIsNone(disagree.rib_shift({"phenotype_known": "0", "lowest_rib_bearing": "T12"}, "T12", "L1"))
        self.assertEqual(disagree.rib_shift({"phenotype_known": "1", "first_rib_bearing": "T1"}, "C7", "T1"), 0)
        self.assertIsNone(disagree.rib_shift({"phenotype_known": "1"}, "L5", "L6"))


if __name__ == "__main__":
    unittest.main()

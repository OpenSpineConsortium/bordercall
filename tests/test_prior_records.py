"""The fitted correlation priors under records/prior-2026-10-31 load, hold as correlations, and say
what the grid job's report says.

The priors were fitted on the grid by SchwingNet's word `morphometry prior` (job 40902475, commit
59ef820), and their JSON stays under the morphometry root there; the records here are rebuilt from
the matrices the job's report carries, rounded to three places, which report.md beside them keeps
whole. A record that mistyped a row would still load, so each is held to the report's own summary
lines: the count of whole spines it was fitted on and the mean correlation of two levels at each
lag from one to five, which the job computed from the unrounded matrix. VerSe gave too few whole
spines to fit and has no record.
"""
from __future__ import annotations

import json
import os
import re
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from schwingcheck import LEVELS                  # noqa: E402
from schwingcheck import correlation as CORR     # noqa: E402

FOLDER = os.path.join(os.path.dirname(HERE), "records", "prior-2026-10-31")
MEASURES = ["endplate", "endplate_depth", "endplate_lower", "endplate_lower_depth", "h_post"]
FITS = {("enhance_pet", "C3"): 693, ("enhance_pet", "T1"): 710,
        ("totalsegmentator", "C3"): 67, ("totalsegmentator", "T1"): 69}


def record(population, first):
    with open(os.path.join(FOLDER, "prior-%s-%s-L5.json" % (population, first))) as f:
        return CORR.Prior.from_json(json.load(f))


def report_lags(population, first):
    with open(os.path.join(FOLDER, "report.md")) as f:
        text = f.read()
    line = re.search(r"- %s %s\.\.L5: level correlation by lag 1 to 5: ([0-9. ]+)" % (population, first), text)
    return [float(v) for v in line.group(1).split()]


class Records(unittest.TestCase):
    def test_every_fit_has_its_record_and_no_other(self):
        names = sorted(n for n in os.listdir(FOLDER) if n.endswith(".json"))
        self.assertEqual(names, sorted("prior-%s-%s-L5.json" % key for key in FITS))

    def test_each_is_a_correlation_on_its_levels_and_measures(self):
        for (population, first), n in FITS.items():
            with self.subTest(population=population, levels=first):
                p = record(population, first)
                self.assertEqual(p.levels, LEVELS[LEVELS.index(first):])
                self.assertEqual(p.measures, MEASURES)
                self.assertEqual(p.n, n)
                self.assertEqual(p.shrink, 0.05)
                for r in (p.r_level, p.r_measure):
                    np.testing.assert_array_equal(r, r.T)
                    np.testing.assert_array_equal(np.diag(r), 1.0)
                    self.assertGreater(np.linalg.eigvalsh(r).min(), 0.1)

    def test_rounded_matrices_keep_the_reports_lag_means(self):
        for population, first in FITS:
            with self.subTest(population=population, levels=first):
                r = record(population, first).r_level
                mine = [float(np.mean(np.diag(r, k))) for k in range(1, 6)]
                np.testing.assert_allclose(mine, report_lags(population, first), atol=0.0015)

    def test_draws_carry_the_record(self):
        p = record("enhance_pet", "C3")
        rng = np.random.default_rng(20261031)
        draws = np.stack([CORR.draw_field(rng, p, p.levels, p.measures) for _ in range(4000)])
        endplate = draws[:, 0, :]
        seen = np.corrcoef(endplate, rowvar=False)
        self.assertLess(np.abs(seen - p.r_level).max(), 0.08)


if __name__ == "__main__":
    unittest.main()

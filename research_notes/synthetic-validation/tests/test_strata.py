"""The stratum layer, every paper its own population, held to what its docstrings say.

    python3 -m unittest discover -s research_notes/synthetic-validation/tests    # from the repository's root

- strata_of's pools are pooled_cells's numbers on every placed cell, and a stratum is the paper
  unless another grouping is given;
- pooled_without leaves one population out and gives None where none is left;
- between takes the cell's own tau from three series on and borrows below, saying which, and the
  predictive SD is never under the within SD;
- a paper's table carries its own means and its own SD only where certain; a measure the paper
  does not print at every level, or a ratio, is left out;
- the arms are scored on the same fields, the own arm's loss is zero, and a rule built on a
  table far from the population loses to the own table;
- pooled_losses gives no spread between papers where every paper lost the same, and floors a
  zero SE;
- a drawn population's means spread by `between` and share their shift as the share says.
"""
from __future__ import annotations

import math
import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
NOTE = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(NOTE))
sys.path[:0] = [REPO, NOTE]

from schwingcheck import LEVELS  # noqa: E402
from synthval import literature as L  # noqa: E402
from synthval import papers_table as PT  # noqa: E402
from synthval import strata as ST  # noqa: E402
from synthval.population import GENERATOR, draw_table  # noqa: E402

LUMBAR = list(ST.LUMBAR)
VOC = {"canal_ap": {"kind": "length"}, "h_ant": {"kind": "length"}, "canal_index": {"kind": "ratio"}}


def series(paper, key, level, mean, sd=2.0, n=30.0, cohort="c", uncertain=False):
    return L.Series(paper=paper, cohort=cohort, technique="ct", modality="ct", group="", sex="all", key=key, level=level,
                    mean=mean, sd=sd, n=n, vs_panjabi="same", sd_uncertain=uncertain)


def three_papers(shift=(0.0, 1.0, -1.0), keys=("canal_ap", "h_ant")):
    """Three papers printing two measures at every lumbar level, each paper's means moved from a
    base by its own shift in SDs."""
    base = {"canal_ap": 17.0, "h_ant": 26.0}
    out = []
    for p, s in zip(("a", "b", "c"), shift):
        for key in keys:
            for i, lv in enumerate(LUMBAR):
                out.append(series(p, key, lv, base[key] + 0.5 * i + 2.0 * s))
    return out


class Strata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = PT.load_rows_all()
        cls.series, _ = PT.select_all(rows)
        cls.cells = PT.pooled_cells(cls.series)
        cls.strata = ST.strata_of(cls.series)

    def test_the_pools_are_pooled_cells_numbers(self):
        to_panjabi = PT._reread_to_panjabi()
        by = {(to_panjabi.get(c["measure"], c["measure"]), c["placed_at"]): c for c in self.cells if c["placed_at"]}
        self.assertEqual(len(self.strata), len(by))
        for c in self.strata:
            r = by[c.measure, c.level]
            self.assertAlmostEqual(c.pool.mean, r["mean"], places=9)
            self.assertAlmostEqual(c.pool.sd, r["sd"], places=9)
            self.assertEqual(c.pool.k, r["k"])
            if c.pool.k >= 2:
                self.assertAlmostEqual(c.pool.tau, r["tau"], places=9)
            self.assertEqual(c.pool.papers, len(r["papers"].split(";")))

    def test_a_stratum_is_the_paper_unless_told_otherwise(self):
        for c in self.strata:
            self.assertEqual(sorted(c.papers), sorted({s.paper for st in c.strata for s in st.series}))
        by_cohort = ST.strata_of(self.series, by=ST.by_cohort)
        self.assertGreaterEqual(sum(len(c.strata) for c in by_cohort), sum(len(c.strata) for c in self.strata))
        self.assertTrue(all("/" in s.paper for c in by_cohort for s in c.strata))

    def test_pooled_without_leaves_one_out(self):
        cells = ST.strata_of(three_papers())
        c = cells[0]
        self.assertEqual(c.pool.k, 3)
        rest = ST.pooled_without(c, "a")
        self.assertEqual(rest.k, 2)
        self.assertEqual(rest.papers, 2)
        self.assertAlmostEqual(rest.mean, ST._pool([s for st in c.strata if st.paper != "a" for s in st.series]).mean)
        one = ST.strata_of([series("a", "canal_ap", "L1", 17.0)])[0]
        self.assertIsNone(ST.pooled_without(one, "a"))


class Between(unittest.TestCase):
    def test_own_tau_from_three_series_borrowed_below(self):
        cells = ST.strata_of(three_papers() + [series("d", "canal_ap", "L1", 19.0)] + [series("a", "canal_index", "L2", 0.5)])
        borrowed = ST.set_between(cells)
        by = ST.cells_by_key(cells)
        own = by["canal_ap", "L1"]
        self.assertEqual(own.tau_from, ST.TAU_OWN)
        self.assertAlmostEqual(own.between, math.hypot(own.pool.tau, own.pool.se))
        alone = by["canal_index", "L2"]
        self.assertEqual(alone.pool.k, 1)
        self.assertEqual(alone.tau_from, ST.TAU_ALL)
        self.assertAlmostEqual(alone.between, math.hypot(borrowed[1] * alone.pool.sd, alone.pool.se))
        for c in cells:
            self.assertGreaterEqual(c.predictive_sd, c.pool.sd)

    def test_the_measures_median_comes_before_every_cells(self):
        rows = three_papers() + [series("a", "h_ant", "L5", 40.0, cohort="x")]
        cells = ST.strata_of(rows)
        ST.set_between(cells)
        by = ST.cells_by_key(cells)
        self.assertEqual(by["h_ant", "L5"].tau_from, ST.TAU_OWN)
        two = ST.strata_of([series("a", "h_ant", "L1", 26.0), series("b", "h_ant", "L1", 27.0)] +
                           [series(p, "canal_ap", lv, 17.0 + i) for p in "abc" for i, lv in enumerate(LUMBAR)])
        borrowed = ST.set_between(two)
        self.assertNotIn("h_ant", borrowed[0])
        self.assertEqual(ST.cells_by_key(two)["h_ant", "L1"].tau_from, ST.TAU_ALL)


class Tables(unittest.TestCase):
    def setUp(self):
        self.cells = ST.strata_of(three_papers() + [series("a", "canal_index", lv, 0.5) for lv in LUMBAR] +
                                  [series("b", "canal_ap", "L1", 18.0, cohort="u", uncertain=True)])
        self.borrowed = ST.set_between(self.cells)

    def test_paper_measures_ask_for_every_level_the_others_and_an_error(self):
        self.assertEqual(ST.paper_measures(self.cells, "a", VOC), ["canal_ap", "h_ant"])
        self.assertEqual(ST.paper_measures(self.cells, "a", VOC, keys=["h_ant"]), ["h_ant"])
        short = ST.strata_of(three_papers() + [series("d", "canal_ap", "L1", 18.0)])
        self.assertEqual(ST.paper_measures(short, "d", VOC), [])

    def test_a_papers_table_is_its_own_means_and_certain_sds(self):
        t, own = ST.paper_table(self.cells, "a", ["canal_ap", "h_ant"], VOC)
        self.assertEqual(t.levels, LUMBAR)
        self.assertAlmostEqual(t.mu[0, 0], 17.0)
        self.assertAlmostEqual(t.mu[1, 4], 28.0)
        self.assertEqual(own, 10)
        self.assertEqual(t.kinds, ["length", "length"])

    def test_an_uncertain_sd_takes_the_others(self):
        cells = ST.strata_of([series("t", "canal_ap", lv, 15.0, sd=9.0, uncertain=True) for lv in LUMBAR] + three_papers())
        t, own = ST.paper_table(cells, "t", ["canal_ap"], VOC)
        self.assertEqual(own, 0)
        self.assertAlmostEqual(t.mu[0, 0], 15.0)
        self.assertAlmostEqual(t.sd[0, 0], ST.pooled_without(ST.cells_by_key(cells)["canal_ap", "L1"], "t").sd)

    def test_the_others_table_leaves_the_paper_out_and_widens_when_asked(self):
        plain = ST.others_table(self.cells, "a", ["canal_ap"], VOC, self.borrowed, False)
        wide = ST.others_table(self.cells, "a", ["canal_ap"], VOC, self.borrowed, True)
        every = ST.others_table(self.cells, None, ["canal_ap"], VOC, self.borrowed, False)
        c = ST.cells_by_key(self.cells)["canal_ap", "L2"]
        self.assertAlmostEqual(plain.mu[0, 1], ST.pooled_without(c, "a").mean)
        self.assertAlmostEqual(every.mu[0, 1], c.pool.mean)
        self.assertTrue((wide.sd > plain.sd).all())
        self.assertTrue((wide.mu == plain.mu).all())


class Scoring(unittest.TestCase):
    def test_the_arms_share_their_fields_and_the_own_arm_loses_nothing(self):
        cells = ST.strata_of(three_papers(shift=(0.0, 4.0, -4.0)))
        rows = ST.leave_one_out(cells, VOC, 20, widths=(1, 3))
        self.assertEqual(len(rows), 3 * 2 * 3)
        for paper in "abc":
            for w in (1, 3):
                mine = [r for r in rows if r["paper"] == paper and r["width"] == w]
                self.assertEqual(len({r["fields"] for r in mine}), 1)
                own = [r for r in mine if r["arm"] == ST.OWN][0]
                self.assertEqual(own["loss"], 0.0)
                self.assertEqual(own["n_measures"], 2)
        far = [r for r in rows if r["paper"] == "b" and r["width"] == 3 and r["arm"] == ST.MERGED][0]
        self.assertGreater(far["loss"], 0.0)
        self.assertTrue(math.isfinite(far["loss_se"]))

    def test_pooled_losses_pool_the_papers(self):
        rows = []
        for paper in "abcd":
            rows += [{"reading": "r", "paper": paper, "arm": ST.MERGED, "width": 3, "loss": 5.0, "loss_se": 1.0,
                      "exact": 0.5, "precision": 0.9, "answered": 0.1},
                     {"reading": "r", "paper": paper, "arm": ST.PREDICTED, "width": 3, "loss": 0.0, "loss_se": 0.0,
                      "exact": 0.55, "precision": float("nan"), "answered": 0.0}]
        got = {r["arm"]: r for r in ST.pooled_losses(rows, widths=(3,))}
        self.assertEqual(got[ST.MERGED]["papers"], 4)
        self.assertAlmostEqual(got[ST.MERGED]["loss_pooled"], 5.0)
        self.assertAlmostEqual(got[ST.MERGED]["tau_between_papers"], 0.0)
        self.assertAlmostEqual(got[ST.MERGED]["loss_se"], 0.5)
        self.assertAlmostEqual(got[ST.PREDICTED]["loss_pooled"], 0.0)
        self.assertAlmostEqual(got[ST.PREDICTED]["loss_se"], ST.LOSS_SE_FLOOR / 2.0)
        self.assertTrue(math.isnan(got[ST.PREDICTED]["precision_mean"]))


class Drawn(unittest.TestCase):
    def test_a_drawn_populations_means_spread_by_between_and_share_a_shift(self):
        cells = ST.strata_of(three_papers())
        borrowed = ST.set_between(cells)
        pooled = ST.others_table(cells, None, ["canal_ap", "h_ant"], VOC, borrowed, False)
        bet = np.full(pooled.mu.shape, 3.0)
        rng = np.random.default_rng(1)
        draws = np.array([ST.new_table(pooled, bet, 0.8, rng) - pooled.mu for _ in range(4000)])
        self.assertAlmostEqual(float(draws.std()), 3.0, delta=0.15)
        r = np.corrcoef(draws[:, 0, 0], draws[:, 0, 4])[0, 1]
        self.assertAlmostEqual(r, 0.8, delta=0.05)
        self.assertAlmostEqual(ST.shift_share({"shift_sd_calibrated": 3.0, "level_sd_calibrated": 4.0}), 9.0 / 25.0)

    def test_new_populations_score_three_arms_on_each_table(self):
        cells = ST.strata_of(three_papers())
        rows = ST.new_populations(cells, VOC, ["canal_ap", "h_ant"], 0.8, 20, tables=2, widths=(3,))
        self.assertEqual(len(rows), 2 * 3)
        self.assertEqual({r["paper"] for r in rows}, {"population 0", "population 1"})
        self.assertTrue(all(r["loss"] == 0.0 for r in rows if r["arm"] == ST.OWN))


if __name__ == "__main__":
    unittest.main()

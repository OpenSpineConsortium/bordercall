"""The bounds card, held to what synthval/bounds.py says of it.

    python3 -m unittest discover -s research_notes/synthetic-validation/tests    # from the repository's root

- on a toy literature of twelve populations drawn from a known model, new populations from that
  model pass the card a little under the nominal 0.95 (the plug-in interval's spread is estimated
  from twelve), Higgins's t interval at least as often, and cohorts the card draws from its own
  model pass at about 0.95;
- the ideal spine at the card's centre passes every mean test, and the same spine with its
  gradient flattened or reversed, or its means moved far off, fails where the break is;
- a step counts only where a paper prints the same cohorts at both levels, and one paper's step
  borrows its spread and widens by it twice, as strata.between widens a one-series mean;
- a step's variance takes the within-person correlation r: it matches the variance of the step of
  correlated people's means, REML's step tau is biased to zero at r = 0 where people correlate and
  unbiased at the true r, the card records the r it was read under, and choose_r takes the r
  nearest the nominal;
- the sex test reads the sign where the interval for a new population's contrast, tau included,
  clears zero, never the pooled effect's interval; a one-paper contrast borrows tau from the
  donor cells and widens by it twice, the donors falling back to two-paper cells and saying so,
  their taus summarised by the steps' rule (root mean square by measure, the measures' median) or
  the means'; two strata of one set of people count once, as covariates.by_paper_cell counts them;
  a paper held out whose contrast has the other sign fails the sign the rest give;
- every paper left out in turn: on the toy literature the held-out papers pass near the nominal, a
  paper far off fails every held-out mean and keeps its steps (so it is not in the card it is
  scored on), the per-paper rows add up to the verdicts, the bar is their median and 10th
  percentile over the papers of MIN_BAR_ROWS rows, a test with fewer than MIN_BAR_PAPERS such
  papers has none, and a kind's held-out card is built from that kind's papers alone;
- check() gives each test a verdict against its bar and the cohort one that fails where the steps
  fail, however high the pooled rate, no verdict where the steps have no bar or the card no
  calibration, and a kind its own bar;
- a cohort given as rows reads as the same cohort given as columns, and a written card, with each
  kind's bar, reads back to the same check;
- on the snapshot, every paper's card has strata.between's spread to the bit, a t interval is never
  narrower than the z interval, the SD interval is missing exactly where no SD is certain, every
  written field is ASCII, and the card's sex contrasts are covariates.py's pooled at each cell.
"""
from __future__ import annotations

import math
import os
import sys
import tempfile
import unittest
from types import SimpleNamespace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
NOTE = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(NOTE))
sys.path[:0] = [REPO, NOTE]

from synthval import bounds as B  # noqa: E402
from synthval import covariates as CV  # noqa: E402
from synthval import literature as L  # noqa: E402
from synthval import papers_table as PT  # noqa: E402
from synthval import pooling as P  # noqa: E402
from synthval import register as RG  # noqa: E402
from synthval import strata as ST  # noqa: E402

LUMBAR = list(ST.LUMBAR)
VOC = {"canal_ap": {"kind": "length"}, "h_ant": {"kind": "length"}}
BASE = {"canal_ap": [17.5, 16.8, 16.2, 16.6, 17.4], "h_ant": [26.0, 27.0, 28.0, 29.0, 30.0]}
SD = 2.0
TAU_SHIFT, TAU_LEVEL, TAU_LOG_SD = 1.0, 0.2, 0.1


def series(paper, key, level, mean, sd, n=200.0, cohort="c"):
    return L.Series(paper=paper, cohort=cohort, technique="ct", modality="ct", group="", sex="all", key=key, level=level,
                    mean=mean, sd=sd, n=n, vs_panjabi="same")


def population(rng):
    """One population of the toy model: per measure one shift through every level and a small one
    at each level, and an SD of its own."""
    out = {}
    for key, base in BASE.items():
        shift = rng.normal(0.0, TAU_SHIFT)
        sd = SD * math.exp(rng.normal(0.0, TAU_LOG_SD))
        out[key] = ([b + shift + rng.normal(0.0, TAU_LEVEL) for b in base], sd)
    return out


def toy_literature(papers=12, n=200.0, seed=5):
    """Twelve papers, each one population of the toy model, printing both measures at every lumbar
    level with its sampling error."""
    rng = np.random.default_rng(seed)
    out = []
    for p in range(papers):
        pop = population(rng)
        for key, (means, sd) in pop.items():
            printed_sd = sd * math.exp(rng.normal(0.0, 1.0 / math.sqrt(2.0 * (n - 1.0))))
            for lv, m in zip(LUMBAR, means):
                out.append(series("p%02d" % p, key, lv, m + rng.normal(0.0, sd / math.sqrt(n)), printed_sd, n))
    return out


def cohort_of(pop, people, rng, sexes=None):
    cols = {"measure": [], "level": [], "value": [], "person": []}
    to_panjabi = PT._reread_to_panjabi()
    for key, (means, sd) in pop.items():
        for lv, m in zip(LUMBAR, means):
            cols["measure"] += [to_panjabi.get(key, key)] * people
            cols["level"] += [lv] * people
            cols["value"] += list(m + sd * rng.normal(size=people))
            cols["person"] += list(range(people))
    return cols


def rates(results):
    made, passed = {}, {}
    for r in results:
        for t, v in r["summary"]["tests"].items():
            made[t] = made.get(t, 0) + v["made"]
            passed[t] = passed.get(t, 0) + v["passed"]
    return {t: passed[t] / made[t] for t in made}


class Toy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.card = B.build(toy_literature(), [], VOC, {})
        cls.cells, cls.steps = cls.card.of_kind(B.ALL)

    def test_the_card_holds_every_cell_and_step(self):
        self.assertEqual(len(self.cells), 10)
        self.assertEqual(len(self.steps), 8)
        self.assertTrue(all(r["tau_from"] == B.TAU_OWN and r["k"] == 12 for r in self.cells + self.steps))
        self.assertTrue(all(r["sd_tau_from"] == B.TAU_OWN for r in self.cells))

    def test_steps_are_tighter_than_means_when_the_shift_runs_through_the_measure(self):
        mean_half = np.median([r["half_width_over_sd"] for r in self.cells])
        step_half = np.median([r["half_width_over_sd"] for r in self.steps])
        self.assertLess(step_half, 0.5 * mean_half)

    def test_new_populations_of_the_model_pass_near_the_nominal_rate(self):
        """Four toy literatures of a dozen populations each: the plug-in z interval, its spread
        estimated from twelve, covers a little under 0.95 (0.85 to 0.95 a literature), as the
        README's answer 8 found of the plug-in interval, and Higgins's t interval covers at least as
        often."""
        z_results, t_results = [], []
        for seed in (5, 6, 7, 8):
            card = B.build(toy_literature(seed=seed), [], VOC, {})
            rng = np.random.default_rng(17)
            for i in range(60):
                cohort = cohort_of(population(rng), 300, np.random.default_rng(i))
                z_results.append(B.check(cohort, card))
                t_results.append(B.check(cohort, card, interval="t"))
        z, t = rates(z_results), rates(t_results)
        for test in ("mean", "sd", "step"):
            self.assertGreater(z[test], 0.85, (test, z))
            self.assertLess(z[test], 0.995, (test, z))
        for test in ("mean", "step"):
            self.assertGreaterEqual(t[test], z[test], (test, z, t))

    def test_cohorts_the_card_draws_pass_at_about_the_nominal_rate(self):
        rng = np.random.default_rng(23)
        results = [B.check(B.simulate(self.card, B.ALL, 300, rng), self.card) for _ in range(150)]
        got = rates(results)
        for test in ("mean", "sd", "step"):
            self.assertGreater(got[test], 0.91, (test, got))
            self.assertLess(got[test], 0.985, (test, got))
        self.assertLess(abs(np.mean([r["summary"]["mean_square_z"] for r in results]) - 1.0), 0.25)

    def test_the_centre_passes_every_mean_and_a_broken_gradient_fails(self):
        rng = np.random.default_rng(29)
        centre = B.simulate(self.card, B.ALL, 1000, rng, centre=True)
        ok = B.check(centre, self.card)
        self.assertEqual(ok["summary"]["tests"]["mean"]["rate"], 1.0)
        self.assertEqual(ok["summary"]["tests"]["step"]["rate"], 1.0)
        flat = B.check(B.flattened(centre, LUMBAR), self.card)
        h_ant = [s for s in flat["steps"] if s["measure"] == "h_ant"]
        self.assertEqual(len(h_ant), 4)
        self.assertEqual(sum(s["step_pass"] for s in h_ant), 0)
        self.assertLess(flat["summary"]["rate"], ok["summary"]["rate"])
        rev = B.check(B.with_levels(centre, dict(zip(LUMBAR, LUMBAR[::-1]))), self.card)
        self.assertEqual(sum(s["step_pass"] for s in rev["steps"] if s["measure"] == "h_ant"), 0)
        self.assertGreater(rev["summary"]["mean_square_z"], 10 * ok["summary"]["mean_square_z"])

    def test_means_moved_far_off_fail_the_mean_test_and_keep_the_steps(self):
        rng = np.random.default_rng(31)
        centre = B.simulate(self.card, B.ALL, 1000, rng, centre=True)
        far = B.Cohort(measure=centre.measure, level=centre.level, value=centre.value + 4.0 * SD, person=centre.person)
        got = B.check(far, self.card)["summary"]["tests"]
        self.assertEqual(got["mean"]["rate"], 0.0)
        self.assertEqual(got["step"]["rate"], 1.0)

    def test_rows_and_columns_read_alike(self):
        rng = np.random.default_rng(37)
        cols = cohort_of(population(rng), 50, rng)
        rows = [dict(measure=m, level=lv, value=v, person=p)
                for m, lv, v, p in zip(cols["measure"], cols["level"], cols["value"], cols["person"])]
        a, b = B.check(cols, self.card), B.check(rows, self.card)
        self.assertEqual(a["summary"], b["summary"])

    def test_a_written_card_reads_back_to_the_same_check(self):
        from run import write_csv
        rng = np.random.default_rng(41)
        cohort = cohort_of(population(rng), 200, rng)
        with tempfile.TemporaryDirectory() as tmp:
            write_csv(tmp, "bounds.csv", self.card.cells)
            write_csv(tmp, "gradients.csv", self.card.steps)
            back = B.load(tmp)
        a, b = B.check(cohort, self.card), B.check(cohort, back)
        self.assertEqual(a["summary"]["tests"], b["summary"]["tests"])
        self.assertAlmostEqual(a["summary"]["mean_square_z"], b["summary"]["mean_square_z"], places=9)


class Steps(unittest.TestCase):
    def test_a_paper_with_other_cohorts_at_each_level_gives_no_step(self):
        rows = [series("a", "canal_ap", "L1", 17.0, 2.0, cohort="x"), series("a", "canal_ap", "L2", 16.0, 2.0, cohort="y"),
                series("b", "canal_ap", "L1", 17.5, 2.0), series("b", "canal_ap", "L2", 16.4, 2.0)]
        est = B.step_estimates(ST.strata_of(rows))
        self.assertEqual(len(est), 1)
        self.assertEqual(est[0].papers, ["b"])
        self.assertEqual(est[0].skipped, ["a"])

    def test_one_papers_step_borrows_its_spread_and_counts_it_twice(self):
        rows = [series("b", "canal_ap", "L1", 17.5, 2.0, n=50.0), series("b", "canal_ap", "L2", 16.4, 2.0, n=50.0)]
        est = B.step_estimates(ST.strata_of(rows), r=0.0)[0]
        row = B.step_row(B.ALL, est, ({}, 0.25))
        tau = 0.25 * 2.0
        self.assertEqual(row["tau_from"], B.TAU_ALL)
        self.assertAlmostEqual(row["between"], math.sqrt(2 * tau * tau + 2 * 4.0 / 50.0), places=12)
        self.assertAlmostEqual(row["step"], 16.4 - 17.5, places=12)
        self.assertTrue(math.isnan(row["step_t_low"]))


class Sex(unittest.TestCase):
    def setUp(self):
        self.card = B.build(toy_literature(), [], VOC, {})
        self.measure = PT._reread_to_panjabi().get("canal_ap", "canal_ap")
        self.row = self.card.cell(B.ALL, self.measure, "L3")
        self.row.update(sex_g=1.0, sex_g_se=0.2, sex_g_low=0.6, sex_g_high=1.4, sex_g_tau=float("nan"),
                        sex_g_between=0.4, sex_g_new_low=0.216, sex_g_new_high=1.784)

    def cohort(self, a, b):
        return {"measure": [self.measure] * 400, "level": ["L3"] * 400, "value": list(a) + list(b),
                "sex": [B.MALE] * 200 + [B.FEMALE] * 200}

    def sexes(self):
        rng = np.random.default_rng(43)
        return self.row["mean"] + 1.0 + SD * rng.normal(size=200), self.row["mean"] - 1.0 + SD * rng.normal(size=200)

    def test_the_sign_is_read_where_a_new_populations_interval_clears_zero(self):
        men, women = self.sexes()
        right = B.check(self.cohort(men, women), self.card)
        wrong = B.check(self.cohort(women, men), self.card)
        self.assertEqual(right["summary"]["tests"]["sex"], {"made": 1, "passed": 1, "rate": 1.0})
        self.assertEqual(wrong["summary"]["tests"]["sex"]["passed"], 0)
        self.assertTrue(right["cells"][0]["sex_inside"])

    def test_a_pooled_interval_clear_of_zero_is_not_enough(self):
        """The pooled effect's interval clears zero and a new population's, tau included, does not:
        no sign test is made, as the verifier asked of the 58 cells the old gate kept."""
        men, women = self.sexes()
        self.row.update(sex_g_between=0.8, sex_g_new_low=1.0 - B.Z * 0.8, sex_g_new_high=1.0 + B.Z * 0.8)
        self.assertTrue(B.clear_of_zero(self.row, "sex_g", "_low", "_high"))
        self.assertFalse(B.clear_of_zero(self.row, "sex_g"))
        self.assertNotIn("sex", B.check(self.cohort(men, women), self.card)["summary"]["tests"])

    def test_one_papers_contrast_borrows_tau_and_widens_by_it_twice(self):
        got = {"papers": 1, "mean": 0.9, "tau": float("nan"), "values": {"a": (0.9, 0.01)}}
        borrowed = {"by_measure": {"canal_ap": 0.5}, "overall": 0.3}
        tau, came, between = B.covariate_spread(got, borrowed, "canal_ap")
        self.assertEqual((tau, came), (0.5, B.TAU_MEASURE))
        self.assertAlmostEqual(between, math.sqrt(2 * 0.25 + 0.01), places=12)
        tau, came, _ = B.covariate_spread(got, borrowed, "h_ant")
        self.assertEqual((tau, came), (0.3, B.TAU_ALL))
        own = {"papers": 3, "mean": 0.9, "tau": 0.2, "values": {"a": (0.8, 0.01), "b": (0.9, 0.02), "c": (1.1, 0.01)}}
        self.assertEqual(B.covariate_spread(own, borrowed, "canal_ap")[:2], (0.2, B.TAU_OWN))
        none = {"by_measure": {}, "overall": float("nan")}
        self.assertEqual(B.covariate_spread(got, none, "h_ant")[1], B.NO_TAU)

    def test_donors_are_three_paper_cells_else_two_paper_cells_and_say_which(self):
        def cell(papers, tau):
            return {"papers": papers, "tau": tau, "papers_named": ";".join("p%d" % i for i in range(papers))}
        two = {("canal_ap", "L1"): {"sex": cell(2, 0.4)}, ("canal_ap", "L2"): {"sex": cell(2, 0.6)},
               ("h_ant", "L1"): {"sex": cell(1, float("nan"))}}
        got = B.covariate_borrowed(two)["sex"]
        self.assertEqual(got["donor_cells"], 2)
        self.assertIn("two papers", got["donors"])
        self.assertEqual(got["rule"], B.RMS)
        self.assertAlmostEqual(got["overall"], math.sqrt((0.4 ** 2 + 0.6 ** 2) / 2), places=12)
        self.assertEqual(set(got["by_measure"]), {"canal_ap"})
        self.assertAlmostEqual(B.covariate_borrowed(two, B.MEDIAN)["sex"]["overall"], 0.5, places=12)
        three = dict(two)
        three[("h_ant", "L2")] = {"sex": cell(3, 0.9)}
        got = B.covariate_borrowed(three)["sex"]
        self.assertEqual((got["donor_cells"], got["overall"], got["by_measure"]), (1, 0.9, {"h_ant": 0.9}))
        self.assertIn("3 papers or more", got["donors"])
        self.assertTrue(math.isnan(B.covariate_borrowed(three)["age"]["overall"]))

    def test_the_steps_rule_keeps_the_spread_a_median_of_zeros_drops(self):
        """Three donor cells of one measure, two of them on a tau of exactly zero: the means' rule
        lends that measure nothing, the steps' rule the root mean square, one vote a measure over
        all where the means' rule takes every cell's median."""
        def cell(tau):
            return {"papers": 3, "tau": tau, "papers_named": "a;b;c"}
        found = {("canal_ap", "L1"): {"sex": cell(0.0)}, ("canal_ap", "L2"): {"sex": cell(0.0)},
                 ("canal_ap", "L3"): {"sex": cell(0.6)}, ("h_ant", "L1"): {"sex": cell(0.3)}}
        rms, med = B.covariate_borrowed(found, B.RMS)["sex"], B.covariate_borrowed(found, B.MEDIAN)["sex"]
        self.assertEqual(med["by_measure"]["canal_ap"], 0.0)
        self.assertAlmostEqual(rms["by_measure"]["canal_ap"], math.sqrt(0.36 / 3), places=12)
        self.assertAlmostEqual(rms["overall"], float(np.median([math.sqrt(0.12), 0.3])), places=12)
        self.assertAlmostEqual(med["overall"], float(np.median([0.0, 0.0, 0.6, 0.3])), places=12)
        self.assertEqual(rms["donor_taus_of_zero"], 2)

    def contrast(self, paper, g_shift, group="", cohort="c", level="L1", n=100.0):
        return CV.Contrast(paper, cohort, "canal_ap", level, group, 17.0 + g_shift, 2.0, n, 17.0, 2.0, n)

    def test_strata_of_one_set_of_people_count_once(self):
        """Two strata of the same people (one cohort and group) are one value, as covariates.by_paper_cell
        reads them; two of different people combine by inverse variance."""
        one = B.covariate_effects({"sex": [self.contrast("a", 1.0)]}, {}, B.ALL)[("canal_ap", "L1")]["sex"]
        same = B.covariate_effects({"sex": [self.contrast("a", 1.0), self.contrast("a", 1.0)]}, {}, B.ALL)
        apart = B.covariate_effects({"sex": [self.contrast("a", 1.0), self.contrast("a", 1.0, group="g2")]}, {}, B.ALL)
        self.assertAlmostEqual(same[("canal_ap", "L1")]["sex"]["se"], one["se"], places=12)
        self.assertAlmostEqual(apart[("canal_ap", "L1")]["sex"]["se"], one["se"] / math.sqrt(2), places=12)

    def test_a_paper_held_out_against_the_sign_of_the_rest_fails_it(self):
        """Four papers agreeing: each held out has the sign the other three give, on their own tau. A
        fifth of the other sign fails it; with it among the rest, the others' intervals widen."""
        agree = [self.contrast(p, 1.0 + 0.05 * i) for i, p in enumerate("abcd")]
        got = B.held_out_signs({"sex": agree}, {})
        self.assertEqual(sorted(r["paper"] for r in got), list("abcd"))
        self.assertTrue(all(r["passed"] and r["tau_from"] == B.TAU_OWN for r in got))
        got = {r["paper"]: r for r in B.held_out_signs({"sex": agree + [self.contrast("e", -1.0)]}, {})}
        self.assertFalse(got["e"]["passed"])
        self.assertTrue(all(r["passed"] for p, r in got.items() if p != "e"))


def correlated_steps(r_true, rng, papers=20, n=50.0, tau_step=0.3, sd=2.0):
    """One step printed by each of `papers` papers, its two means made from the same people whose two
    levels correlate at r_true, the step itself varying between papers by tau_step."""
    out = []
    cov = sd * sd / n * np.array([[1.0, r_true], [r_true, 1.0]])
    for p in range(papers):
        ea, eb = rng.multivariate_normal([0.0, 0.0], cov)
        step = 1.0 + rng.normal(0.0, tau_step)
        out += [series("p%02d" % p, "h_ant", "L1", 26.0 + ea, sd, n), series("p%02d" % p, "h_ant", "L2", 26.0 + step + eb, sd, n)]
    return out


class StepCorrelation(unittest.TestCase):
    def test_the_variance_is_that_of_correlated_peoples_means(self):
        """Two levels of the same 40 people correlating at 0.7, and of 40 and a 25 among them: the
        step of the means varies as step_variance says, the covariance over the larger count."""
        rng = np.random.default_rng(47)
        cov = np.array([[4.0, 0.7 * 2.0 * 3.0], [0.7 * 2.0 * 3.0, 9.0]])
        for n_a, n_b in ((40, 40), (40, 25)):
            steps = []
            for _ in range(20000):
                x = rng.multivariate_normal([0.0, 0.0], cov, size=n_a)
                steps.append(x[:n_b, 1].mean() - x[:, 0].mean())
            want = B.step_variance(2.0, n_a, 3.0, n_b, 0.7)
            self.assertAlmostEqual(np.var(steps) / want, 1.0, delta=0.04)
        self.assertAlmostEqual(B.step_variance(2.0, 50, 2.0, 50, 0.0), 2 * 4.0 / 50, places=12)

    def test_reml_tau_is_biased_to_zero_at_r_zero_and_unbiased_at_the_true_r(self):
        """Steps of people correlating at 0.8, varying between papers by 0.3: read at r = 0 the
        papers' own variances are five times too large and REML's tau^2 falls to zero in most draws;
        read at 0.8 its mean is the truth."""
        rng = np.random.default_rng(53)
        got = {0.0: [], 0.8: []}
        for _ in range(150):
            cells = ST.strata_of(correlated_steps(0.8, rng))
            for r in got:
                e = B.step_estimates(cells, r)[0]
                got[r].append(P.pool(e.steps, e.variances).tau2)
        self.assertGreater(np.mean(np.array(got[0.0]) == 0.0), 0.5)
        self.assertLess(np.mean(got[0.0]), 0.3 * 0.09)
        self.assertAlmostEqual(np.mean(got[0.8]) / 0.09, 1.0, delta=0.15)

    def test_the_card_records_its_r_and_a_larger_r_narrows_the_papers_own_error(self):
        lit = toy_literature()
        at0, at5 = B.build(lit, [], VOC, {}, r=0.0), B.build(lit, [], VOC, {}, r=0.5)
        self.assertTrue(all(s["within_r"] == 0.5 for s in at5.steps))
        self.assertEqual(at5.borrowed["step_tau_over_sd"]["within_r"], 0.5)
        for a, b in zip(at0.steps, at5.steps):
            self.assertEqual((a["measure"], a["upper"]), (b["measure"], b["upper"]))
            self.assertGreaterEqual(b["step_tau"] + 1e-12, a["step_tau"])
        self.assertEqual([c["between"] for c in at0.cells], [c["between"] for c in at5.cells])

    def test_choose_r_takes_the_nearest_the_nominal_and_the_smaller_on_a_tie(self):
        self.assertEqual(B.choose_r({0.0: 0.93, 0.5: 0.96, 0.8: 0.99}), 0.5)
        self.assertEqual(B.choose_r({0.0: 0.94, 0.5: 0.96}), 0.0)
        self.assertEqual(B.choose_r({0.0: 0.935, 0.5: 0.909, 0.8: 0.894}), 0.0)

    def test_readings_set_the_card_and_the_left_out_papers_r_apart(self):
        self.assertEqual(B.readings((0.0, 0.5), (B.RMS,)), [(0.0, 0.0, B.RMS), (0.5, 0.5, B.RMS)])
        self.assertEqual(len(B.readings((0.0, 0.5), (B.RMS, B.MEDIAN), (0.0, 0.5, 0.8))), 12)
        v = B.held_out_verdicts(toy_literature(papers=6), {}, B.readings((0.0, 0.5), (B.RMS,), (0.0, 0.5)))
        steps = B.matching(v, test="step")
        self.assertEqual({(x["r"], x["test_r"]) for x in steps}, {(0.0, 0.0), (0.0, 0.5), (0.5, 0.0), (0.5, 0.5)})
        self.assertTrue(all(x["r"] is None for x in v if x["test"] != "step"))


class HeldOut(unittest.TestCase):
    def test_held_out_toy_papers_pass_near_the_nominal(self):
        """Four toy literatures, each paper left out in turn and scored on the card of the other
        eleven: the plug-in z interval read from eleven covers a little under 0.95, 0.875 to 0.958
        a test and literature when this was written."""
        for seed in (5, 6, 7, 8):
            v = B.held_out_verdicts(toy_literature(seed=seed), {}, B.readings((0.0,), (B.RMS,)))
            for test in B.CALIBRATED:
                rate = B.coverage(B.matching(v, test=test))["rate"]
                self.assertGreater(rate, 0.84, (seed, test, rate))
                self.assertLess(rate, 0.995, (seed, test, rate))

    def test_a_paper_far_off_fails_its_means_and_keeps_its_steps(self):
        """A paper whose every mean sits 8 SDs above p00's fails every held-out mean, so the card it
        is scored on does not hold it; its steps, read inside the paper, pass."""
        lit = toy_literature()
        far = [series("zz", s.key, s.level, s.mean + 8 * SD, s.sd, s.n) for s in lit if s.paper == "p00"]
        v = B.held_out_verdicts(lit + far, {}, B.readings((0.0,), (B.RMS,)))
        self.assertEqual(B.coverage(B.matching(v, test="mean", paper="zz"))["rate"], 0.0)
        self.assertEqual(B.coverage(B.matching(v, test="step", paper="zz"))["rate"], 1.0)
        self.assertEqual(B.coverage(B.matching(v, test="mean", paper="zz"))["made"], 10)

    def test_the_rows_add_up_and_the_bar_is_their_median_and_low_quantile(self):
        v = B.held_out_verdicts(toy_literature(), {}, B.readings((0.0,), (B.RMS,)))
        rows = B.per_paper(v, 0.0, B.RMS)
        self.assertEqual(sum(r["made"] for r in rows if r["test"] == B.ALL), len(v))
        for r in rows:
            if r["test"] == B.ALL:
                parts = [x["made"] for x in rows if x["paper"] == r["paper"] and x["test"] != B.ALL]
                self.assertEqual(r["made"], sum(parts))
        bar = B.bar_of(rows, least_rows=1)
        steps = [r["passed"] / r["made"] for r in rows if r["test"] == "step"]
        self.assertEqual(bar["step"]["median"], float(np.median(steps)))
        self.assertEqual(bar["step"]["low"], float(np.quantile(steps, B.BAR_LOW)))
        self.assertEqual(bar["step"]["papers"], 12)
        self.assertNotIn(B.ALL, bar)
        self.assertEqual(B.bar_of(rows)["step"], {"papers": 0, "least_rows": B.MIN_BAR_ROWS, "low_quantile": B.BAR_LOW,
                                                  "papers_with_any_row": 12})

    def test_check_gives_a_verdict_against_the_bar_and_a_written_bar_reads_back(self):
        from run import write_csv
        card = B.build(toy_literature(), [], VOC, {})
        rows = B.per_paper(B.held_out_verdicts(toy_literature(), {}, B.readings((0.0,), (B.RMS,))), 0.0, B.RMS)
        rng = np.random.default_rng(59)
        cohort = cohort_of(population(rng), 200, rng)
        bare = B.check(cohort, card)["summary"]["verdict"]
        self.assertEqual(bare["bar"], B.UNCALIBRATED)
        self.assertIsNone(bare["passed"])
        self.assertTrue(all(t["passed"] is None and "at_or_above_nominal" in t for t in bare["tests"].values()))
        card.calibration = {B.ALL: B.bar_of(rows, least_rows=1)}
        got = B.check(cohort, card)["summary"]["verdict"]
        for test in B.CALIBRATED:
            b = card.calibration[B.ALL][test]
            self.assertEqual(got["tests"][test]["low"], b["low"])
            self.assertEqual(got["tests"][test]["passed"], got["tests"][test]["rate"] >= b["low"])
        with tempfile.TemporaryDirectory() as tmp:
            write_csv(tmp, "bounds.csv", card.cells)
            write_csv(tmp, "gradients.csv", card.steps)
            write_csv(tmp, "calibration.csv", rows + [dict(r, kind="living") for r in rows])
            back = B.load(tmp)
        self.assertEqual(back.calibration, {B.ALL: B.bar_of(rows), "living": B.bar_of(rows)})
        card.calibration = {B.ALL: B.bar_of(rows)}
        self.assertEqual(B.check(cohort, back)["summary"]["verdict"], B.check(cohort, card)["summary"]["verdict"])


def bar_rows(rates, made, test="step", kind=B.ALL):
    return [{"kind": kind, "paper": "p%02d" % i, "test": test, "made": m, "passed": round(r * m)}
            for i, (r, m) in enumerate(zip(rates, made))]


class Bars(unittest.TestCase):
    def test_only_papers_of_twenty_rows_vote_and_five_make_a_bar(self):
        rates = [0.5, 0.625, 0.9, 0.92, 0.95, 0.975, 1.0]
        made = [8, 8, 20, 25, 40, 40, 60]
        bar = B.bar_of(bar_rows(rates, made))["step"]
        voting = [0.9, 0.92, 0.95, 0.975, 1.0]
        self.assertEqual(bar["papers"], 5)
        self.assertAlmostEqual(bar["low"], float(np.quantile(voting, B.BAR_LOW)), places=12)
        self.assertAlmostEqual(bar["median"], 0.95, places=12)
        self.assertEqual(bar["papers_with_any_row"], 7)
        self.assertNotIn("low", B.bar_of(bar_rows(rates[:6], made[:6]))["step"])
        without = B.bar_of(bar_rows(rates, made), min_papers=4, without=("p02",))["step"]
        self.assertAlmostEqual(without["low"], float(np.quantile(voting[1:], B.BAR_LOW)), places=12)


def summary_of(rates, made=None):
    made = made or {t: 600 for t in rates}
    return {t: {"made": made[t], "passed": round(rates[t] * made[t]), "rate": rates[t]} for t in rates}


BAR = {t: {"low": 0.85, "median": 0.93, "papers": 7} for t in B.CALIBRATED}


class Verdicts(unittest.TestCase):
    def test_a_cohort_fails_where_its_steps_fail_however_high_its_pooled_rate(self):
        got = B.verdict(summary_of({"mean": 1.0, "sd": 1.0, "step": 0.84}), BAR)
        self.assertFalse(got["passed"])
        self.assertEqual(got["why"], "fails its bar on: step")
        self.assertTrue(got["tests"]["mean"]["passed"])

    def test_a_cohort_passes_where_every_test_with_a_bar_does(self):
        got = B.verdict(summary_of({"mean": 0.9, "sd": 0.86, "step": 0.85}), BAR)
        self.assertTrue(got["passed"])
        self.assertFalse(got["tests"]["sd"]["at_or_above_median"])
        self.assertFalse(B.verdict(summary_of({"mean": 0.5, "sd": 1.0, "step": 1.0}), BAR)["passed"])

    def test_no_verdict_without_the_steps_or_their_bar(self):
        self.assertIsNone(B.verdict(summary_of({"mean": 1.0, "sd": 1.0}), BAR)["passed"])
        no_step = {t: b for t, b in BAR.items() if t != "step"}
        got = B.verdict(summary_of({"mean": 1.0, "sd": 1.0, "step": 1.0}), dict(no_step, step={"papers": 1}))
        self.assertIsNone(got["passed"])
        self.assertIn("no bar", got["tests"]["step"]["why"])
        self.assertFalse(B.verdict(summary_of({"mean": 0.1, "sd": 1.0, "step": 1.0}), no_step)["passed"])
        self.assertIsNone(B.verdict(summary_of({"mean": 1.0, "sd": 1.0, "step": 1.0}), None, calibrated=False)["passed"])

    def test_the_toy_centre_passes_and_its_flattened_gradient_fails_on_the_toys_own_bar(self):
        card = B.build(toy_literature(), [], VOC, {})
        rows = B.per_paper(B.held_out_verdicts(toy_literature(), {}, B.readings((0.0,), (B.RMS,))), 0.0, B.RMS)
        card.calibration = {B.ALL: B.bar_of(rows, least_rows=1)}
        centre = B.simulate(card, B.ALL, 1000, np.random.default_rng(29), centre=True)
        self.assertTrue(B.check(centre, card)["summary"]["verdict"]["passed"])
        flat = B.check(B.flattened(centre, LUMBAR), card)["summary"]
        self.assertFalse(flat["verdict"]["passed"])
        self.assertFalse(flat["verdict"]["tests"]["step"]["passed"])


class Kinds(unittest.TestCase):
    """Six toy papers of living people and six of dry bone; a seventh of dry bone far off."""

    def register(self, lit):
        return {(s.paper, s.cohort): SimpleNamespace(specimen="living" if s.paper < "p06" else "dry bone") for s in lit}

    def test_a_kinds_held_out_card_is_built_from_that_kinds_papers(self):
        lit = toy_literature()
        far = [series("zz", s.key, s.level, s.mean + 8 * SD, s.sd, s.n) for s in lit if s.paper == "p00"]
        reg = self.register(lit + far)
        under = B.readings((0.0,), (B.RMS,))
        living = B.held_out_verdicts(lit, reg, under, kind="living")
        self.assertEqual({v["paper"] for v in living}, {"p%02d" % i for i in range(6)})
        self.assertTrue(all(v["kind"] == "living" for v in living))
        self.assertEqual(living, B.held_out_verdicts(lit + far, reg, under, kind="living"))
        dry = B.held_out_verdicts(lit + far, reg, under, kind="dry bone")
        self.assertEqual(B.coverage(B.matching(dry, test="mean", paper="zz"))["rate"], 0.0)

    def test_check_on_a_kind_reads_that_kinds_bar_and_none_without_one(self):
        lit = toy_literature()
        reg = self.register(lit)
        card = B.build(lit, [], VOC, reg)
        rows = B.per_paper(B.held_out_verdicts(lit, reg, B.readings((0.0,), (B.RMS,)), kind="living"), 0.0, B.RMS)
        card.calibration = {B.ALL: BAR, "living": B.bar_of(rows, least_rows=1)}
        rng = np.random.default_rng(61)
        cohort = cohort_of(population(rng), 200, rng)
        got = B.check(cohort, card, "living")["summary"]["verdict"]
        self.assertEqual(got["tests"]["step"]["low"], card.calibration["living"]["step"]["low"])
        none = B.check(cohort, card, "dry bone")["summary"]["verdict"]
        self.assertIsNone(none["passed"])
        self.assertTrue(all("no bar" in t["why"] for t in none["tests"].values()))


class Snapshot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = PT.load_rows_all()
        cls.sex_rows = cls.rows + PT.load_rows_sexes()
        cls.series, _ = PT.select_all(cls.rows)
        cls.register = RG.load()
        cls.voc = PT.load_vocabulary()
        cls.card = B.build(cls.series, cls.rows, cls.voc, cls.register, sex_rows=cls.sex_rows)

    def test_every_papers_card_has_strata_between(self):
        cells = ST.strata_of(self.series)
        ST.set_between(cells)
        for c in cells:
            row = self.card.cell(B.ALL, c.measure, c.level)
            self.assertEqual(row["between"], c.between)
            self.assertEqual(row["tau_from"], c.tau_from)
            self.assertEqual(row["predictive_sd"], c.predictive_sd)

    def test_the_t_interval_is_never_narrower(self):
        for r in self.card.cells + self.card.steps:
            lo, hi = (r["mean_t_low"], r["mean_t_high"]) if "mean_t_low" in r else (r["step_t_low"], r["step_t_high"])
            if math.isfinite(lo):
                centre = r.get("mean", r.get("step"))
                self.assertGreaterEqual(hi - centre + 1e-9, B.Z * r["between"])

    def test_the_sd_interval_is_missing_exactly_where_no_sd_is_certain(self):
        for r in self.card.cells:
            self.assertEqual(math.isnan(r["sd_low"]), r["sd_strata"] == 0)
            if r["sd_strata"]:
                self.assertLess(r["sd_low"], r["sd_high"])
                self.assertLessEqual(r["sd_min"], r["sd_median"])
                self.assertLessEqual(r["sd_median"], r["sd_max"])

    def test_every_kind_is_the_registers_specimen_and_every_field_ascii(self):
        kinds = B.kinds_present(self.series, self.register)
        self.assertEqual(kinds[0], B.ALL)
        self.assertTrue(set(kinds[1:]) <= {"cadaver", "dry bone", "living", "mixed"})
        for r in self.card.cells + self.card.steps:
            for v in r.values():
                if isinstance(v, str):
                    v.encode("ascii")

    def test_the_cards_sex_contrasts_are_the_covariates_pooled_at_each_cell(self):
        """At every vertebra's own cell (a disc or a foramen is placed at its upper level, so its cell
        is not covariates.py's), the card's contrast is covariates.py's papers pooled over the same
        strata, the sexes' snapshot among them: the card reads the final covariates."""
        contrasts = CV.sex_contrasts(self.sex_rows, self.voc)
        cells = CV.by_paper_cell(contrasts)
        effects = B.covariate_effects(B.covariate_items(self.rows, self.voc, self.sex_rows), self.register, B.ALL)
        compared = 0
        for (base, level), d in effects.items():
            if "sex" not in d or base.startswith(PT.DISC_OR_FORAMEN):
                continue
            want = CV.pooled(CV.paper_values(cells, base, level))
            self.assertAlmostEqual(d["sex"]["mean"], want["mean"], places=12)
            self.assertEqual(d["sex"]["papers"], want["papers"])
            compared += 1
        self.assertGreater(compared, 100)
        self.assertGreater(len(contrasts), len(CV.sex_contrasts(self.rows, self.voc)))

    def test_the_ideal_spine_passes_every_mean_and_its_flattened_lumbar_steps_fail(self):
        centre = B.simulate(self.card, B.ALL, 500, np.random.default_rng(3), centre=True)
        ok = B.check(centre, self.card)
        self.assertEqual(ok["summary"]["tests"]["mean"]["rate"], 1.0)
        flat = B.check(B.flattened(centre, LUMBAR), self.card)
        lumbar = [s["step_pass"] for s in flat["steps"] if s["lower"] in LUMBAR[1:]]
        intact = [s["step_pass"] for s in ok["steps"] if s["lower"] in LUMBAR[1:]]
        self.assertLess(np.mean(lumbar), np.mean(intact) - 0.3)


if __name__ == "__main__":
    unittest.main()

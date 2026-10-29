"""The note's own code, held to what its docstrings say.

    python3 -m unittest discover -s research_notes/synthetic-validation/tests    # from the repository's root

- population.draw at the generator's settings gives columns.draw_columns' columns in distribution:
  every mean and SD of every measure at every level agrees within five standard errors;
- sd_mode "size_removed" gives the true anatomy the printed mean and SD in every cell it does not hold;
- the pooling is the textbook's: one series pools to nothing, equal series to no spread, the
  prediction interval takes t on k - 2 degrees of freedom, the REML spread recovers a known one,
  and the many-row REML of the simulations is the one-row REML;
- the literature selection gives the counts the README quotes from the pinned snapshot, the
  snapshot is the one SOURCE.json records, the jump screen catches a jump and nothing smooth or
  far apart, children and diseased cohorts are left out, a cell's published SD is its one
  certain series' where Tan's is the other, Olsewski's Part 2 leaves wherever Part 1 holds the
  cell, his pedicle counts are halved and Gilad's counts are his per level;
- the quality indicators flag what they say they flag, their unions hold what they name, and the
  drawing's superellipse holds the area it is asked for, its pedicles meeting the body;
- the power tests have the power they say, the calibrated spreads read above the raw ones, as a
  correction of estimates that read low must, and Griffith's sexes taken together give the
  mixture's correlation.
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
from schwingcheck import columns as C  # noqa: E402
from schwingcheck import measures as MS  # noqa: E402
from synthval import literature as L  # noqa: E402
from synthval import pooling as P  # noqa: E402
from synthval import power as PW  # noqa: E402
from synthval import qi as Q  # noqa: E402
from synthval import structure as ST  # noqa: E402
from synthval import sweep as SW  # noqa: E402
from synthval import validate as V  # noqa: E402
from synthval.population import GENERATOR, draw, size_moments  # noqa: E402

import render as R  # noqa: E402


class PopulationMatchesTheGenerator(unittest.TestCase):
    N = 6000

    def test_moments_agree_with_draw_columns(self):
        ms = MS.pool()
        keys = [MS.archive_key(m) for m in ms]
        cols = C.draw_columns(MS.reference(ms), ["typical"], 7, self.N, keys, power=MS.powers(ms),
                              noise_mm=MS.errors(ms))
        pop = draw(GENERATOR, self.N, 8, ms)
        self.assertEqual(cols.levels[0], pop.levels)
        a, b = cols.values, pop.measured
        se = np.sqrt(a.var(0, ddof=1) / self.N + b.var(0, ddof=1) / self.N)
        z_mean = (a.mean(0) - b.mean(0)) / se
        z_sd = np.log(a.std(0, ddof=1) / b.std(0, ddof=1)) / math.sqrt(1.0 / (self.N - 1))
        self.assertLess(float(np.abs(z_mean).max()), 5.0)
        self.assertLess(float(np.abs(z_sd).max()), 5.0)


    def test_size_removed_gives_the_printed_moments(self):
        ms = MS.select(MS.SPINEPS_7)
        st = GENERATOR.but(sd_mode="size_removed", floor=False)
        pop = draw(st, 40000, 9, ms)
        _, _, mu, sd = C.profiles(MS.reference(ms), [MS.archive_key(m) for m in ms], "typical", st.blend)
        e1, e2 = size_moments(MS.powers(ms), st.scale_sd)
        left = (sd ** 2 - (mu / e1[:, None]) ** 2 * (e2 - e1 ** 2)[:, None]) / e2[:, None]
        held = left < (0.1 * sd) ** 2 / e2[:, None]
        self.assertEqual(int(held.sum()), pop.clipped)
        ok = ~held.T
        se_mean = sd.T / math.sqrt(40000)
        self.assertLess(float(np.abs((pop.true.mean(0) - mu.T) / se_mean)[ok].max()), 5.0)
        z_sd = np.log(pop.true.std(0, ddof=1) / sd.T) * math.sqrt(2 * 39999)
        self.assertLess(float(np.abs(z_sd)[ok].max()), 6.0)


class Pooling(unittest.TestCase):
    def test_one_series_pools_to_nothing_and_two_give_no_interval(self):
        self.assertIsNone(P.pool_means([40.0], [4.0], [16]))
        got = P.pool_means([40.0, 42.0], [4.0, 4.0], [16, 16])
        self.assertAlmostEqual(got.mean, 41.0)
        self.assertTrue(math.isnan(got.pi_low))

    def test_equal_series_have_no_spread(self):
        got = P.pool_means([40.0] * 5, [4.0] * 5, [16] * 5)
        self.assertAlmostEqual(got.tau2, 0.0, places=8)
        self.assertAlmostEqual(got.se, 1.0 / math.sqrt(5))

    def test_prediction_interval_takes_t_on_k_minus_2(self):
        got = P.pool_means([38.0, 40.0, 45.0, 41.0], [4.0] * 4, [16] * 4)
        from scipy import stats
        half = stats.t.ppf(0.975, 2) * math.sqrt(got.tau2 + got.se ** 2)
        self.assertAlmostEqual(got.pi_high - got.mean, half, places=8)
        self.assertAlmostEqual(got.mean - got.pi_low, half, places=8)

    def test_reml_recovers_a_known_spread(self):
        rng = np.random.default_rng(3)
        k, tau, se = 400, 2.0, 0.5
        means = 30 + tau * rng.normal(size=k) + se * rng.normal(size=k)
        got = P.pool_means(means, [se * 10] * k, [100] * k)
        self.assertAlmostEqual(got.tau, tau, delta=0.25)


    def test_many_row_reml_is_the_one_row_reml(self):
        rng = np.random.default_rng(4)
        v = rng.uniform(0.2, 2.0, 4)
        y = rng.normal(size=(50, 4)) * rng.uniform(0.0, 2.0, (50, 1))
        t2, mu = P.reml_rows(y, v)
        for r in range(50):
            one = P.pool(y[r], v)
            self.assertAlmostEqual(t2[r], one.tau2, places=6)
            self.assertAlmostEqual(mu[r], one.mean, places=6)


class Literature(unittest.TestCase):
    def test_snapshot_is_the_recorded_one(self):
        self.assertEqual(L.check_snapshot(), [])

    def test_selection_counts(self):
        rows = L.load_rows()
        series, why = L.select(rows)
        self.assertEqual(len(rows), 2407)
        self.assertEqual(len(series), 954)
        self.assertEqual(sum(1 for s in series if L.usable(s)), 903)
        self.assertEqual(len(rows) - sum(why.values()), len(series))
        self.assertEqual(len({s.paper for s in series if L.usable(s)}), 25)
        self.assertNotIn(L.BREAKS_OWN_SERIES, why)
        self.assertEqual(sum(1 for s in series if s.flag.endswith("one side only")), 1)
        self.assertEqual(sum(1 for s in series if L.usable(s) and s.key in ("endplate_incl", "endplate_lower_incl")), 44)

    def test_one_set_of_people_and_counts_of_people(self):
        series, _ = L.select(L.load_rows())
        olsewski = {}
        for s in series:
            if s.paper == "olsewski1990":
                olsewski.setdefault((s.key, s.level, s.technique), set()).add(s.cohort)
                self.assertEqual(s.n_note, "n is the printed pedicles halved")
        self.assertFalse([c for c in olsewski.values() if {"part1_cadavers", "part2_cadavers"} <= c])
        gilad = {s.level: s.n for s in series if s.paper == "gilad1985"}
        self.assertEqual(gilad.get("C7"), 126)
        self.assertEqual(gilad.get("L1"), 154)

    def test_jump_screen(self):
        base = dict(paper="p", cohort="c", technique="t", source_of_values="this paper", key="endplate_lower_area",
                    sex="all", group="", side="", units="mm2")
        smooth = [dict(base, level=lv, mean=m) for lv, m in zip(("L1", "L2", "L3", "L4"), (1010.0, 1090.0, 1150.0, 1199.0))]
        self.assertEqual(L.breaks_own_series(smooth), set())
        jump = [dict(base, level=lv, mean=m) for lv, m in zip(("L1", "L2", "L3", "L4"), (1010.0, 1090.0, 172.0, 1199.0))]
        self.assertEqual(L.breaks_own_series(jump), {id(jump[2])})
        angle = [dict(r, units="deg", mean=-r["mean"] if r["level"] == "L3" else r["mean"]) for r in smooth]
        self.assertEqual(L.breaks_own_series(angle), set())
        no_l6 = [dict(base, level=lv, mean=m) for lv, m in zip(("L4", "L5", "S1"), (1199.0, 400.0, 1300.0))]
        self.assertEqual(L.breaks_own_series(no_l6), {id(no_l6[1])})
        far = [dict(base, key="pedicle_w", units="mm", level=lv, mean=m) for lv, m in zip(("T4", "T5", "L5"), (3.5, 3.8, 17.6))]
        self.assertEqual(L.breaks_own_series(far), set())

    def test_children_and_diseased_cohorts_are_left_out(self):
        base = dict(source_of_values="this paper", species="", key="canal_ap", vs_panjabi="same", technique="ct",
                    cohort="adults", group="")
        self.assertIsNone(L.excluded_why(base, L.DEFINITIONS_MAIN))
        self.assertEqual(L.excluded_why(dict(base, group="age 6-10 years"), L.DEFINITIONS_MAIN), "children")
        self.assertIsNone(L.excluded_why(dict(base, group="age 20-29 years"), L.DEFINITIONS_MAIN))
        self.assertEqual(L.excluded_why(dict(base, cohort="stenosis"), L.DEFINITIONS_MAIN),
                         "selected, diseased or example group")

    def test_a_lone_certain_sd_is_the_published_sd(self):
        def one(paper, sd):
            return L.Series(paper=paper, cohort="c", technique="t", modality="ct", group="", sex="all", key="canal_ap",
                            level="L3", mean=15.0, sd=sd, n=30, vs_panjabi="same", flag="", n_note="",
                            sd_uncertain=paper in L.DISPERSION_UNCERTAIN)
        lit = V.literature_at([one("tan2004", 5.0), one("other", 2.0)])
        self.assertEqual(lit.k_sd, 1)
        self.assertAlmostEqual(lit.sd, 2.0)
        self.assertTrue(math.isnan(V.literature_at([one("tan2004", 5.0)]).sd))

    def test_sexes_pool_with_the_difference_of_means(self):
        mean, sd, n = L._pool_sexes({"n": 10, "mean": 50.0, "sd": 3.0}, {"n": 10, "mean": 44.0, "sd": 3.0})
        self.assertAlmostEqual(mean, 47.0)
        self.assertEqual(n, 20)
        self.assertAlmostEqual(sd, math.sqrt((9 * 9 + 9 * 9 + 10 * 10 / 20 * 36) / 19))


class Quality(unittest.TestCase):
    def setUp(self):
        self.pop = draw(GENERATOR, 400, 5, MS.pool())

    def test_box_flags_an_area_over_its_rectangle(self):
        pop = self.pop
        a, w, d = (pop.keys.index(k) for k in ("canal_area", "canal_w", "canal_ap"))
        pop.true[:, :, a] = 0.8 * pop.true[:, :, w] * pop.true[:, :, d]
        for k in ("endplate_area", "endplate_lower_area"):
            j = pop.keys.index(k)
            ww, dd = (pop.keys.index(x) for x in (("endplate", "endplate_depth") if k == "endplate_area"
                                                   else ("endplate_lower", "endplate_lower_depth")))
            pop.true[:, :, j] = 0.8 * pop.true[:, :, ww] * pop.true[:, :, dd]
        for k in ("facet_area_sup:mean", "facet_area_inf:mean"):
            j = pop.keys.index(k)
            side = "sup" if "sup" in k else "inf"
            ww, hh = pop.keys.index("facet_w_%s:mean" % side), pop.keys.index("facet_h_%s:mean" % side)
            pop.true[:, :, j] = 0.8 * pop.true[:, :, ww] * pop.true[:, :, hh]
        self.assertFalse(Q.flags(pop).by["box"].any())
        pop.true[3, 10, a] = 1.2 * pop.true[3, 10, w] * pop.true[3, 10, d]
        box = Q.flags(pop).by["box"]
        self.assertTrue(box[3, 10])
        self.assertEqual(int(box.sum()), 1)

    def test_curate_drops_only_on_sign_and_inside(self):
        kept, counts = Q.curate(self.pop)
        self.assertEqual(counts["kept"] + counts["dropped"], 400)
        fl = Q.flags(self.pop)
        bad = fl.by["sign"].any(1) | fl.by["inside"].any(1)
        self.assertTrue(np.array_equal(kept, ~bad))

    def test_unions_hold_what_they_name(self):
        fl = Q.flags(self.pop)
        rates = Q.vertebra_rates(fl)
        hard = (fl.by["sign"] | fl.by["inside"]).mean()
        self.assertAlmostEqual(rates["sign or inside"], hard)
        self.assertLessEqual(rates["sign or inside"], rates["any but floor"])
        self.assertLessEqual(rates["any but floor"], rates["any"])


class Drawing(unittest.TestCase):
    def test_superellipse_area(self):
        self.assertAlmostEqual(R.area_share(2.0), math.pi / 4, places=10)
        self.assertAlmostEqual(R.area_share(1.0), 0.5, places=10)
        for share in (0.55, 0.7, 0.785, 0.9, 0.98):
            self.assertAlmostEqual(R.area_share(R.exponent_for(share)), share, places=6)
        self.assertIsNone(R.exponent_for(1.07))

    def test_pedicles_meet_the_body(self):
        width, depth, area = 44.1, 35.2, 1194.0
        x, y, n = R.outline(width, depth, area, (0.0, depth / 2), points=4000)
        for at in (12.0, 17.0, 21.0):
            top = R.pedicle_top(width, depth, n, at)
            behind = y[(np.abs(np.abs(x) - at) < 0.2) & (y < depth / 2)]
            self.assertGreaterEqual(top, behind.max() if len(behind) else 0.0)
            self.assertLessEqual(top, depth / 2)

    def test_spinous_tip_from_the_end_plate(self):
        v = {"endplate_depth": 35.2, "spinous_length": 71.7}
        self.assertAlmostEqual(R.spinous_tip(v), 17.6 - 71.7)

    def test_outline_holds_the_area(self):
        x, y, n = R.outline(44.1, 35.2, 1194.0, (0.0, 0.0), points=4000)
        area = 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
        self.assertAlmostEqual(area, 1194.0, delta=1.5)
        self.assertAlmostEqual(x.max() - x.min(), 44.1, places=4)


class Power(unittest.TestCase):
    def test_least_shift_has_the_power_it_says(self):
        from scipy import stats
        for n, tests in ((12, 1), (159, 1), (159, 154)):
            d = PW.least_shift(n, tests)
            crit = stats.t.ppf(1 - 0.05 / (2 * tests), n - 1)
            nc = d * math.sqrt(n)
            self.assertAlmostEqual(stats.nct.sf(crit, n - 1, nc) + stats.nct.cdf(-crit, n - 1, nc), 0.80, places=6)
        self.assertAlmostEqual(PW.least_shift(10 ** 5), (1.959964 + 0.841621) / math.sqrt(10 ** 5), places=4)

    def test_least_sd_ratio_has_the_power_it_says(self):
        from scipy import stats
        for n in (17, 159):
            ratio = PW.least_sd_ratio(n)
            crit = stats.chi2.ppf(0.975, n - 1)
            self.assertAlmostEqual(stats.chi2.sf(crit / ratio ** 2, n - 1), 0.80, places=8)

    def test_calibrated_spreads_read_above_the_raw_ones(self):
        series, _ = L.select(L.load_rows())
        split = PW.shift_split(series, replicates=60)
        self.assertGreaterEqual(split["shift_sd_calibrated"], split["shift_sd"])
        self.assertGreaterEqual(split["level_sd_calibrated"], split["level_sd"])
        cal = PW.calibrated_median_f(series, replicates=60)
        self.assertGreater(cal["calibrated_median"], cal["observed_median"])
        self.assertLess(cal["expected_median_if_true_were_observed"], cal["observed_median"])

    def test_correlation_half_width_shrinks(self):
        self.assertGreater(PW.correlation_half_width(50), PW.correlation_half_width(159))
        self.assertAlmostEqual(PW.correlation_half_width(10 ** 7), 0.0, places=3)

    def test_shifted_table_with_no_shift_is_the_table(self):
        mu, sd = MS.arrays(MS.select(MS.SPINEPS_7), LEVELS)
        got = PW.shifted_table(mu, sd, np.random.default_rng(1), 0.0, 0.0)
        self.assertTrue(np.array_equal(got, mu))

    def test_two_sample_tests_against_panjabi(self):
        # Welch at 159 against 12 with an SD 1.47 times the gold persons': about 1.3 SD on 11.8 df
        self.assertAlmostEqual(PW.least_shift_two_sample(159, sd_ratio=1.47), 1.32, places=2)
        self.assertGreater(PW.least_shift_two_sample(159, sd_ratio=1.0), PW.least_shift(159))
        from scipy import stats
        ratio = PW.least_sd_ratio_two_sample(159)
        crit = stats.f.ppf(0.975, 11, 158)
        self.assertAlmostEqual(stats.f.sf(crit / ratio ** 2, 11, 158), 0.80, places=8)

    def test_shared_shift_moves_every_measure_alike(self):
        mu, sd = MS.arrays(MS.select(MS.SPINEPS_7), LEVELS)
        got = (PW.shifted_table(mu, sd, np.random.default_rng(3), 0.5, 0.0, shared=True) - mu) / sd
        self.assertTrue(np.allclose(got, got[0, 0]))

    def test_griffith_sexes_together(self):
        rng = np.random.default_rng(5)
        a, b, men, women = ST.GRIFFITH[2]
        draws = []
        for sex, r in ((0, men), (1, women)):
            (ma, sa), (mb, sb) = ST.GRIFFITH_SEX[a][sex], ST.GRIFFITH_SEX[b][sex]
            z = rng.multivariate_normal([0, 0], [[1, r], [r, 1]], size=200000)
            draws.append(np.c_[ma + sa * z[:, 0], mb + sb * z[:, 1]])
        both = np.vstack(draws)
        self.assertAlmostEqual(np.corrcoef(both.T)[0, 1], ST.mixed_sex_r(a, b, men, women), places=2)

    def test_gold_power_leaves_out_what_the_papers_do_not_count(self):
        row = PW.gold_power((159,))[0]
        self.assertNotIn("expected: a thirteenth rib-bearing body (T13)", row)
        self.assertAlmostEqual(row["expected: six lumbar-type segments (L6 or lumbarised S1)"], 159 * 0.0248)

    def test_beyond_edges_reads_only_past_the_ends_the_nearest_point_sits_on(self):
        grid = {"scale_sd": (0.0, 0.07), "sd_scale": (0.7, 1.0), "rho": (0.25, 0.5, 0.9), "r_between": (0.0, 0.4)}
        best = {"scale_sd": 0.0, "sd_scale": 0.7, "rho": 0.5, "r_between": 0.4}
        series, _ = L.select(L.load_rows())
        got = SW.beyond_edges(best, series, n=200, seed=1, grid=grid)
        self.assertEqual(sorted((p["axis"], p[p["axis"]]) for p in got),
                         [("r_between", 0.8), ("sd_scale", 0.5), ("sd_scale", 0.55)])
        self.assertEqual([p["distance"] for p in got], sorted(p["distance"] for p in got))
        self.assertTrue(all(p["rho"] == 0.5 and p["scale_sd"] == 0.0 for p in got))


if __name__ == "__main__":
    unittest.main()

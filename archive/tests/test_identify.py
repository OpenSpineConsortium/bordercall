"""Which vertebrae a normal spine identifies best: the pieces checked against something outside.

    python -m unittest discover -s tests -v

Kunkel 2010's regressions must come back from this table: the paper's Fig 2A states the linear
fit of the upper end-plate width on the posterior body height, y = 2.20 x - 10.51 with R^2 0.94,
and the cubic's R^2 0.98, and Table 1 prints the cubic's coefficients and R^2 for six measures
this package holds; refitting on the table's means over Kunkel's sixteen levels must give them.
The closed-form moments must follow the generator where the spread is small; the Helmert
contrasts must be orthonormal and blind to a common factor; the three isolations must order as
the algebra says (size known, then unknown, then shape only); the rank statistic must be the
area under the curve; the confusion table must add up; and the abstention threshold must keep
the precision it was chosen for on the rows it was chosen on.
"""
from __future__ import annotations

import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "bordercall"))

import identify as ID         # noqa: E402
import neighbour as NB        # noqa: E402
import neighbour_more as NM   # noqa: E402
import panjabi as P           # noqa: E402

MEASURES = list(ID.MEASURES7)


def _ref():
    return P.load_reference(measures=MEASURES)


class TestKunkel(unittest.TestCase):
    def test_fig2a_linear_fit_is_reproduced(self):
        k = ID.kunkel_fits(_ref())["measures"]["endplate"]
        slope, intercept = k["linear_16"]["coefficients"][1], k["linear_16"]["coefficients"][0]
        self.assertAlmostEqual(slope, ID.KUNKEL_LINEAR_EPWS[0], delta=0.01)
        self.assertAlmostEqual(intercept, ID.KUNKEL_LINEAR_EPWS[1], delta=0.01)
        self.assertAlmostEqual(k["linear_16"]["r2"], ID.KUNKEL_LINEAR_EPWS[2], delta=0.005)
        self.assertAlmostEqual(k["cubic_16"]["r2"], ID.KUNKEL_CUBIC_R2_EPWS, delta=0.005)

    def test_table1_r2_and_coefficients_are_reproduced(self):
        fits = ID.kunkel_fits(_ref())["measures"]
        for m, (name, printed, sd_printed, r2_printed) in ID.KUNKEL.items():
            got = fits[m]["cubic_16"]
            self.assertAlmostEqual(got["r2"], r2_printed, delta=0.002, msg=name)
            # the printed coefficients are rounded to three decimals; the refit must agree to that
            for want, have in zip(printed, got["coefficients"]):
                self.assertAlmostEqual(want, have, delta=0.0015 + 0.004 * abs(want), msg=name)
            # Kunkel's SD column is the residual SD on n - 4 degrees of freedom
            self.assertAlmostEqual(got["sd"], sd_printed, delta=0.02, msg=name)

    def test_printed_cubic_rounding_is_recorded(self):
        fits = ID.kunkel_fits(_ref())["measures"]
        # rounding C4 to three decimals moves the curve by millimetres at 24 mm, so the record
        # says how far the printed curve sits from the table it was fitted on
        self.assertGreater(fits["endplate_depth"]["printed"]["max_mm_at_this_table"], 1.0)
        self.assertLess(fits["endplate"]["cubic_16"]["sd"], fits["endplate"]["printed"]["rms_mm_at_this_table"] + 0.5)

    def test_left_out_levels_depart_from_the_curve(self):
        k = ID.kunkel_fits(_ref())
        self.assertEqual(k["left_out"], ["C3", "C4", "C5", "C6", "C7", "L5"])
        dep = k["measures"]["endplate"]["departures_from_cubic_16"]
        # the T1-L4 cubic, carried to the cervical body heights, overshoots the cervical widths
        # by many table SDs and undershoots L5; neither joins Kunkel's curve
        for lv in ["C3", "C4", "C5", "C6"]:
            self.assertLess(dep[lv]["in_table_sd"], -3.0, msg=lv)
        self.assertGreater(dep["L5"]["residual_mm"], 5.0)
        # the departure in SD is the departure in mm over that level's own table SD
        ref = _ref()
        self.assertAlmostEqual(dep["L5"]["in_table_sd"], dep["L5"]["residual_mm"] / ref["endplate"]["L5"][1])


class TestOneMeasure(unittest.TestCase):
    def test_t12_rival_along_body_height(self):
        ref = _ref()
        all22 = ID.one_measure_isolation(ref, "h_post", P.LEVELS, 1.0, 0.07)
        k16 = ID.one_measure_isolation(ref, "h_post", ID.KUNKEL_LEVELS, 1.0, 0.07)
        self.assertEqual(all22["T12"]["rival"], "L5")
        self.assertEqual(k16["T12"]["rival"], "L1")
        self.assertLess(all22["T12"]["gap_body_sd"], 0.1)
        self.assertLess(k16["T12"]["gap_body_sd"], 0.5)
        # the single-body spread is never below the table's
        for lv in P.LEVELS:
            self.assertGreaterEqual(all22[lv]["body_sd_mm"], all22[lv]["table_sd_mm"])
            self.assertLessEqual(all22[lv]["gap_body_sd"], all22[lv]["gap_table_sd"] + 1e-12)

    def test_single_body_sd_adds_in_quadrature(self):
        ref = _ref()
        mu, sd = ref["h_post"]["T12"]
        want = np.sqrt(sd ** 2 + 1.0 + (0.07 * mu) ** 2)
        self.assertAlmostEqual(ID.single_body_sd(ref, "h_post", "T12", 1.0, 0.07), want, places=9)


class TestIsolation(unittest.TestCase):
    def test_helmert_is_orthonormal_and_blind_to_size(self):
        H = ID.helmert(7)
        self.assertTrue(np.allclose(H @ H.T, np.eye(6)))
        self.assertTrue(np.allclose(H @ np.ones(7), 0.0))

    def test_formula_follows_the_draw_where_the_spread_is_small(self):
        ref = _ref()
        constant = NB.external_constant(ref, MEASURES)
        M, S = ID.level_moments(ref, MEASURES, constant, 0.07, 1.0, 0.5, 0.0)
        Me, Se = ID.level_moments_empirical(ref, MEASURES, constant, NB.SYNTH, 1500, 3)
        i = ID.CLASSES.index("L2")                     # cv at most 0.16 here
        self.assertTrue(np.allclose(M[i], Me[i], atol=0.03))
        self.assertTrue(np.allclose(np.diag(S[i]), np.diag(Se[i]), rtol=0.2))
        off = ~np.eye(7, dtype=bool)
        self.assertLess(np.abs(S[i][off] - Se[i][off]).max(), 0.004)

    def test_formula_puts_the_size_on_every_pair(self):
        ref = _ref()
        constant = NB.external_constant(ref, MEASURES)
        M, S = ID.level_moments(ref, MEASURES, constant, 0.07, 1.0, 0.5, 0.0)
        off = ~np.eye(7, dtype=bool)
        self.assertTrue(np.allclose(S[:, off], 0.07 ** 2))
        M, S = ID.level_moments(ref, MEASURES, constant, 0.0, 1.0, 0.5, 0.0)
        self.assertTrue(np.allclose(S[:, off], 0.0))

    def test_distances_are_symmetric_and_ordered(self):
        ref = _ref()
        constant = NB.external_constant(ref, MEASURES)
        iso = ID.isolation_analytic(ref, MEASURES, constant, NB.SYNTH)
        for mode in ("size_unknown", "size_known", "shape_only"):
            D = np.asarray(iso[mode]["matrix"])
            self.assertTrue(np.allclose(D, D.T))
            self.assertTrue(np.allclose(np.diag(D), 0.0))
        for lv in ID.CLASSES:
            known, unknown, shape = (iso[m]["nearest"][lv]["d"] for m in ("size_known", "size_unknown", "shape_only"))
            self.assertGreaterEqual(known + 1e-9, unknown, lv)
            self.assertGreaterEqual(unknown + 1e-9, shape, lv)

    def test_shape_only_ignores_the_size_spread(self):
        ref = _ref()
        constant = NB.external_constant(ref, MEASURES)
        a = ID.isolation_analytic(ref, MEASURES, constant, dict(NB.SYNTH, scale_sd=0.07))["shape_only"]["matrix"]
        b = ID.isolation_analytic(ref, MEASURES, constant, dict(NB.SYNTH, scale_sd=0.5))["shape_only"]["matrix"]
        self.assertTrue(np.allclose(a, b))

    def test_subsets_cover_every_subset_and_the_full_set_is_never_beaten(self):
        ref = _ref()
        constant = NB.external_constant(ref, MEASURES)
        M, S = ID.level_moments(ref, MEASURES, constant, 0.07, 1.0, 0.5, 0.0)
        sub = ID.subset_isolation(M, S)
        self.assertEqual(sub["n_subsets"], 127)
        for lv in ID.CLASSES:
            self.assertGreaterEqual(sub["best_subset"][lv]["d"] + 1e-9, sub["full"][lv], lv)
            self.assertGreaterEqual(sub["best_subset"][lv]["d"] + 1e-9, sub["best_single"][lv]["d"], lv)
            self.assertIn(sub["best_single"][lv]["measure"], MEASURES)


class TestClassifierPieces(unittest.TestCase):
    def test_auc_is_the_rank_statistic(self):
        pos = np.array([True, True, False, False])
        self.assertEqual(ID.auc(np.array([0.9, 0.8, 0.2, 0.1]), pos), 1.0)
        self.assertEqual(ID.auc(np.array([0.1, 0.2, 0.8, 0.9]), pos), 0.0)
        self.assertEqual(ID.auc(np.array([0.5, 0.5, 0.5, 0.5]), pos), 0.5)
        self.assertTrue(np.isnan(ID.auc(np.array([0.5, 0.5]), np.array([True, True]))))

    def test_level_table_adds_up(self):
        rng = np.random.default_rng(0)
        y = rng.integers(0, 4, 400)
        prob = rng.random((400, ID.K))
        prob[np.arange(400), y] += 0.6 * rng.random(400)
        rows = NB.Rows(X=np.zeros((400, 1)), y=y, rib=-np.ones(400, int), group=np.arange(400) // 20, phenotype=np.array(["typical"] * 400))
        table, conf = ID.level_table(prob, rows, [0, 1, 2, 3])
        conf = np.asarray(conf)
        self.assertEqual(conf.sum(), 400)
        for c in range(4):
            lv = ID.CLASSES[c]
            self.assertEqual(table[lv]["n"], conf[c].sum())
            self.assertEqual(table[lv]["tp"], conf[c, c])
            self.assertEqual(table[lv]["n_called"], conf[:, c].sum())
            self.assertAlmostEqual(table[lv]["recall"], conf[c, c] / conf[c].sum())
            self.assertAlmostEqual(table[lv]["precision"], conf[c, c] / conf[:, c].sum())

    def test_abstention_keeps_its_precision_where_it_was_chosen(self):
        rng = np.random.default_rng(1)
        y = rng.integers(0, 3, 600)
        prob = rng.random((600, ID.K))
        prob[np.arange(600), y] += rng.random(600)
        prob /= prob.sum(1, keepdims=True)
        rows = NB.Rows(X=np.zeros((600, 1)), y=y, rib=-np.ones(600, int), group=np.arange(600) // 30, phenotype=np.array(["typical"] * 600))
        th = ID.abstain_thresholds(prob, rows, [0, 1, 2], (0.9,))
        applied = ID.abstain_apply(prob, rows, [0, 1, 2], th, (0.9,))
        for c in range(3):
            e = applied[ID.CLASSES[c]]["0.9"]
            if e["threshold"] is not None:
                self.assertGreaterEqual(e["precision"], 0.9 - 1e-12)
                self.assertGreater(e["n_called"], 0)

    def test_binary_detector_separates_what_is_separable(self):
        rng = np.random.default_rng(2)
        X = rng.normal(size=(300, 3))
        pos = X[:, 0] + 0.5 * X[:, 1] > 0.3
        w = ID.fit_binary(X, pos)
        self.assertGreater(ID.auc(ID.binary_score(w, X), pos), 0.97)

    def test_shape_only_features_are_blind_to_a_common_factor(self):
        ref = _ref()
        constant = NB.external_constant(ref, MEASURES)
        cols = NB.draw_columns(ref, ("typical",), 7, 5, MEASURES)
        offs = NM.field_offsets(1, True)
        rows = NM.field_rows(cols, offs, MEASURES, constant)
        a = ID.shape_only(rows, offs, 7).X
        rows.X = rows.X + 0.3                            # every log measure scaled alike
        b = ID.shape_only(rows, offs, 7).X
        self.assertTrue(np.allclose(a, b))
        self.assertEqual(a.shape[1], 3 * 6)


class TestQuickRun(unittest.TestCase):
    def test_quick_run_writes_every_section(self):
        rec = ID.run(outdir=None, n_fit=40, n_select=20, n_score=30, quick=True)
        for key in ("kunkel", "one_measure", "isolation", "isolation_analytic", "isolation_in_r", "field_isolation",
                    "table_bootstrap", "subsets", "covariance_check", "cells", "axes", "bayes", "table", "size",
                    "r_sweep"):
            self.assertIn(key, rec)
        self.assertEqual(rec["phenotype"], "typical")
        c = rec["cells"][0]
        self.assertEqual(c["shuffle"]["identical"], c["shuffle"]["trials"])
        self.assertEqual(len(c["levels"]), len(c["by_level"]))
        self.assertEqual(int(np.asarray(c["confusion"]).sum()), c["n_score_rows"])


class TestPatchedPieces(unittest.TestCase):
    """The pieces the skeptics asked for, each held to a case whose answer is known."""

    def setUp(self):
        self.ref = _ref()
        self.constant = NB.external_constant(self.ref, MEASURES)
        self.synth = dict(NB.SYNTH)

    def test_bhattacharyya_is_an_eighth_of_the_squared_distance_under_one_covariance(self):
        M, S = ID.level_moments(self.ref, MEASURES, self.constant, 0.07, 1.0, 0.5, 0.0)
        pooled = S.mean(0)
        S1 = np.repeat(pooled[None], len(M), axis=0)
        D = ID.mahalanobis_matrix(M, S1)
        B = ID.bhattacharyya_matrix(M, S1)
        self.assertTrue(np.allclose(B, D ** 2 / 8))
        B2 = ID.bhattacharyya_matrix(M, S)
        D2 = ID.mahalanobis_matrix(M, S)
        self.assertTrue(np.allclose(B2, B2.T))
        self.assertTrue(np.all(B2[np.triu_indices(len(M), 1)] >= D2[np.triu_indices(len(M), 1)] ** 2 / 8 - 1e-9))

    def test_field_at_one_body_is_the_one_body_isolation(self):
        M, S = ID.level_moments(self.ref, MEASURES, self.constant, self.synth["scale_sd"], self.synth["noise_mm"],
                                self.synth["rho"], 0.0)
        near = ID.nearest_rivals(ID.mahalanobis_matrix(M, S))
        f0 = ID.field_isolation(self.ref, MEASURES, self.constant, self.synth, 0)
        self.assertEqual(f0["visible_bodies"], 1)
        for lv in f0["nearest"]:
            self.assertAlmostEqual(f0["nearest"][lv]["d"], near[lv]["d"], places=9)
            self.assertEqual(f0["nearest"][lv]["rival"], near[lv]["rival"])

    def test_a_wider_field_isolates_the_common_levels_further(self):
        f0 = ID.field_isolation(self.ref, MEASURES, self.constant, self.synth, 0)["nearest"]
        f2 = ID.field_isolation(self.ref, MEASURES, self.constant, self.synth, 2)["nearest"]
        for lv in ID.COMMON_LEVELS:
            self.assertGreater(f2[lv]["d"], f0[lv]["d"], lv)

    def test_the_formula_follows_the_draw_in_a_field(self):
        offs = NM.field_offsets(1, True)
        c = ID.CLASSES.index("T6")
        mean, cov = ID.field_moments(self.ref, MEASURES, self.constant, self.synth, offs, c)
        cols = NB.draw_columns(self.ref, ("typical",), 3, 4000, MEASURES)
        rows = NM.field_rows(cols, offs, MEASURES, self.constant)
        X = rows.X[rows.y == c]
        self.assertGreater(len(X), 3000)
        self.assertTrue(np.allclose(X.mean(0), mean, atol=0.02))
        emp = np.cov(X.T)
        rel = np.abs(np.diag(emp) - np.diag(cov)) / np.diag(emp)
        self.assertLess(float(rel.max()), 0.25)

    def test_table_bootstrap_shares_add_up_and_intervals_hold(self):
        tb = ID.table_bootstrap(self.ref, MEASURES, self.constant, self.synth, 12, seed=3)
        by = tb["by_level"]
        self.assertAlmostEqual(sum(v["most_isolated_7"] for v in by.values()), 1.0)
        self.assertAlmostEqual(sum(v["most_isolated_h_post"] for v in by.values()), 1.0)
        for lv, v in by.items():
            self.assertLessEqual(v["d_lo"], v["d_hi"])
            self.assertLessEqual(v["gap_body_sd_lo"], v["gap_body_sd_hi"])
            self.assertTrue(1 <= v["rank_7_lo"] <= v["rank_7_hi"] <= ID.K)
            self.assertTrue(0.0 <= v["same_rival_7"] <= 1.0)

    def test_precision_under_a_uniform_prior_is_the_plain_precision(self):
        rng = np.random.default_rng(1)
        levels = list(range(ID.K))
        conf = rng.integers(0, 6, size=(ID.K, ID.K)) + 20 * np.eye(ID.K, dtype=int)
        conf = conf.tolist()
        uniform = {lv: 1.0 / ID.K for lv in ID.CLASSES}
        under = ID.precision_under_prior(conf, levels, uniform)
        C = np.asarray(conf, float)
        C = C / C.sum(1, keepdims=True)
        for c, lv in enumerate(ID.CLASSES):
            self.assertAlmostEqual(under[lv], C[c, c] / C[:, c].sum())
        point = {"T12": 1.0}
        under = ID.precision_under_prior(conf, levels, point)
        self.assertAlmostEqual(under["T12"], 1.0)
        self.assertTrue(np.isnan(under["T11"]))

    def test_chance_by_level_knows_the_region(self):
        ch = ID.chance_by_level(list(range(ID.K)))
        for lv, v in ch.items():
            self.assertAlmostEqual(v["uniform"], 1.0 / ID.K)
            self.assertGreaterEqual(v["region_known"], v["uniform"])
        self.assertAlmostEqual(ch["L3"]["region_known"], 0.2)
        self.assertAlmostEqual(ch["T6"]["region_known"], 1.0 / 12)

    def test_r_sweep_of_the_formula_brackets_r_zero(self):
        sw = ID.isolation_in_r(self.ref, MEASURES, self.constant, self.synth)
        for lv, v in sw["by_level"].items():
            self.assertLessEqual(v["lo"], v["at_r0"])
            self.assertLessEqual(v["at_r0"], v["hi"])
            self.assertEqual(v["rises_with_r"], v["at_r_max"] > v["at_r0"])
        self.assertTrue(any(v["rises_with_r"] for v in sw["by_level"].values()))


    def test_exact_likelihood_is_the_ceiling_at_one_body(self):
        cols = NB.draw_columns(self.ref, ("typical",), 97, 60, MEASURES)
        exact = ID.bayes_exact_one_body(self.ref, MEASURES, self.synth, cols)
        self.assertEqual(exact["n_bodies"], 60 * ID.K)
        recalls = [exact["recall_by_level"][lv] for lv in ID.CLASSES]
        self.assertAlmostEqual(float(np.mean(recalls)), exact["exact"])
        fit = NB.draw_columns(self.ref, ("typical",), 11, 80, MEASURES)
        c = ID.cell(self.ref, "both", 0, fit, fit, cols, self.constant, False)
        self.assertGreater(exact["exact"], c["exact"])

    def test_exact_likelihood_at_one_node_is_the_diagonal_quadratic_rule(self):
        cols = NB.draw_columns(self.ref, ("typical",), 2, 20, MEASURES)
        exact = ID.bayes_exact_one_body(self.ref, MEASURES, self.synth, cols, n_nodes=1)
        mu = np.array([[self.ref[m][lv][0] for m in MEASURES] for lv in ID.CLASSES])
        var = np.array([[self.ref[m][lv][1] ** 2 for m in MEASURES] for lv in ID.CLASSES]) + self.synth["noise_mm"] ** 2
        hits = []
        for col in cols:
            for c in range(ID.K):
                v = np.array([col.values[m][c] for m in MEASURES])
                logl = [-0.5 * float(np.sum((v - mu[i]) ** 2 / var[i] + np.log(2 * np.pi * var[i]))) for i in range(ID.K)]
                hits.append(int(np.argmax(logl)) == c)
        self.assertAlmostEqual(exact["exact"], float(np.mean(hits)))

    def test_exact_likelihood_names_a_body_at_its_own_mean_when_the_spreads_are_equal(self):
        ref = {m: {lv: (self.ref[m][lv][0], 0.5) for lv in P.LEVELS} for m in MEASURES}
        synth = dict(self.synth, noise_mm=0.0, scale_sd=1e-6)
        cols = NB.draw_columns(ref, ("typical",), 1, 2, MEASURES)
        for col in cols:
            for m in MEASURES:
                col.values[m][:] = [ref[m][lv][0] for lv in col.levels]
        exact = ID.bayes_exact_one_body(ref, MEASURES, synth, cols, n_nodes=5)
        self.assertEqual(exact["exact"], 1.0)

    def test_table_arm_carries_the_pedicle_rows(self):
        t = ID.table_study(40, 20, 30, 300, halves=(0,))
        self.assertEqual(t["measures"], list(ID.MEASURES7) + ["pedicle", "pedicle_h"])
        self.assertEqual(t["cells"][0]["measures"], t["measures"])
        self.assertEqual(len(t["isolation_size_unknown"]), ID.K)
        self.assertEqual(int(np.asarray(t["cells"][0]["confusion"]).sum()), t["cells"][0]["n_score_rows"])

    def test_second_order_term_lifts_the_variance_where_the_spread_is_wide(self):
        M, S = ID.level_moments(self.ref, MEASURES, self.constant, 0.0, 0.0, 0.0, 0.0)
        i = ID.CLASSES.index("T2")
        j = MEASURES.index("canal_ap")
        mu, sd = self.ref["canal_ap"]["T2"]
        cv = sd / mu
        self.assertAlmostEqual(S[i, j, j], cv ** 2 + 2.5 * cv ** 4, places=9)


if __name__ == "__main__":
    unittest.main()

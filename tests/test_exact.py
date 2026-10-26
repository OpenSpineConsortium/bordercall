"""The exact rule for a run of consecutive vertebrae: each piece checked against something outside it.

    python -m unittest discover -s tests -v

The closed-form likelihood (a diagonal plus a rank-one covariance, Sherman-Morrison) must equal
the dense multivariate normal density computed by scipy, and the dense joint over all measures at
r = 0; at one body the rule must reproduce the earlier study's exact one-body Bayes rule on the
same columns; with two places and equal covariances its error must be the textbook Phi(-d/2); the
posterior of the named place must keep the selective guarantee on fresh draws; the quadrature
must agree with an independent trapezoid rule; the log-space formula's covariance must follow a
draw where the spreads are small; and the coarse claims must be monotone, minimal and leave out
the boundaries a field's size settles.
"""
from __future__ import annotations

import math
import os
import sys
import unittest

import numpy as np
from scipy.stats import multivariate_normal, norm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "bordercall"))

import exact as E             # noqa: E402
import identify as ID         # noqa: E402
import neighbour as NB        # noqa: E402
import panjabi as P           # noqa: E402

MEASURES = list(E.MEASURES7)
SYNTH = dict(rho=0.5, noise_mm=1.0, scale_sd=0.07)


def _ref():
    return P.load_reference(measures=MEASURES)


def _values(n_columns, seed=97, ref=None, **synth):
    ref = ref or _ref()
    return E.column_values(NB.draw_columns(ref, ["typical"], seed, n_columns, MEASURES, **synth), MEASURES)


class TestLikelihood(unittest.TestCase):
    def test_closed_form_equals_the_dense_normal_density(self):
        mu, sd = E.table_arrays(_ref(), MEASURES)
        V = _values(4)
        sizes = np.array([0.93, 1.0, 1.08])
        for n in (1, 2, 5):
            X, _, _ = E.fields(V, n)
            for start in (0, 7, E.L - n):
                got = E.place_loglik(X, mu, sd, start, sizes, 0.5, 1.0)
                for j, s in enumerate(sizes):
                    for m in (0, 4, 6):
                        sw = sd[m, start:start + n]
                        shape = 0.25 * np.ones((n, n)) + 0.75 * np.eye(n)
                        cov = s * s * np.outer(sw, sw) * shape + np.eye(n)
                        want = multivariate_normal(mean=s * mu[m, start:start + n], cov=cov).logpdf(X[:, m, :])
                        np.testing.assert_allclose(got[:, m, j], want, rtol=0, atol=1e-9)

    def test_dense_joint_at_r_zero_is_the_product_over_measures(self):
        mu, sd = E.table_arrays(_ref(), MEASURES)
        X, _, _ = E.fields(_values(3), 4)
        sizes = np.array([0.95, 1.05])
        a = E.place_loglik(X, mu, sd, 6, sizes, 0.5, 1.0).sum(1)
        b = E.joint_place_loglik(X, mu, sd, 6, sizes, 0.5, 1.0, 0.0)
        np.testing.assert_allclose(a, b, rtol=0, atol=1e-9)

    def test_dense_joint_follows_the_generator_with_correlated_offsets(self):
        # the covariance the joint likelihood assumes must be the one the generator draws from
        ref = _ref()
        mu, sd = E.table_arrays(ref, MEASURES)
        V = _values(4000, seed=3, scale_sd=0.0, r_between=0.6)
        n, start = 2, 9
        x = V[:, :, start:start + n].reshape(len(V), -1)
        R = E.CV.exchangeable(len(MEASURES), 0.6)
        shape = 0.25 * np.kron(R, np.ones((n, n))) + 0.75 * np.eye(len(MEASURES) * n)
        d = sd[:, start:start + n].reshape(-1)
        cov = np.outer(d, d) * shape + np.eye(len(d))
        emp = np.cov(x.T)
        rel = np.abs(emp - cov) / np.sqrt(np.outer(np.diag(cov), np.diag(cov)))
        self.assertLess(float(rel.max()), 0.08)

    def test_quadrature_agrees_with_an_independent_rule(self):
        mu, sd = E.table_arrays(_ref(), MEASURES)
        X, _, _ = E.fields(_values(5), 9)
        a = E.posterior(E.evidence_lean(X, mu, sd, SYNTH, *E.quadrature(0.07, E.GH_NODES)))
        b = E.posterior(E.evidence_lean(X, mu, sd, SYNTH, *E.trapezoid(0.07)))
        self.assertLess(float(np.abs(a - b).max()), 1e-8)

    def test_no_size_spread_takes_one_node(self):
        sizes, logw = E.quadrature(0.0)
        self.assertEqual(list(sizes), [1.0])
        self.assertEqual(list(logw), [0.0])


class TestRule(unittest.TestCase):
    def test_one_body_reproduces_the_earlier_exact_rule(self):
        ref = _ref()
        cols = NB.draw_columns(ref, ["typical"], 97, 60, MEASURES)
        old = ID.bayes_exact_one_body(ref, MEASURES, dict(NB.SYNTH), cols, n_nodes=41)
        mu, sd = E.table_arrays(ref, MEASURES)
        X, truth, _ = E.fields(E.column_values(cols, MEASURES), 1)
        post = E.posterior(E.log_evidence(E.field_loglik(X, mu, sd, SYNTH, 41), E.quadrature(0.07, 41)[1]))
        self.assertAlmostEqual(float((post.argmax(1) == truth).mean()), old["exact"], places=12)

    def test_the_whole_column_has_one_place(self):
        mu, sd = E.table_arrays(_ref(), MEASURES)
        X, truth, _ = E.fields(_values(3), E.L)
        post = E.posterior(E.log_evidence(E.field_loglik(X, mu, sd, SYNTH), E.quadrature(0.07)[1]))
        self.assertEqual(post.shape, (3, 1))
        np.testing.assert_allclose(post, 1.0)

    def test_two_places_with_equal_covariance_err_at_phi_of_half_d(self):
        # one measure whose SD is the same at every level and no size spread: the two places a
        # field of 21 can take have one covariance, and the Bayes error is Phi(-d/2)
        ref = _ref()
        flat = {m: {lv: (ref[m][lv][0], 2.0) for lv in ref[m]} for m in ref}
        synth = dict(rho=0.5, noise_mm=1.0, scale_sd=0.0)
        mu, sd = E.table_arrays(flat, ["h_post"])
        n = E.L - 1
        cov = 4.0 * (0.25 * np.ones((n, n)) + 0.75 * np.eye(n)) + np.eye(n)
        dmu = mu[0, 1:] - mu[0, :-1]
        d = math.sqrt(dmu @ np.linalg.solve(cov, dmu))
        cols = NB.draw_columns(flat, ["typical"], 5, 40000, ["h_post"], **synth)
        V = E.column_values(cols, ["h_post"])
        X, truth, _ = E.fields(V, n)
        post = E.posterior(E.log_evidence(E.field_loglik(X, mu, sd, synth), E.quadrature(0.0)[1]))
        err = float((post.argmax(1) != truth).mean())
        want = float(norm.cdf(-d / 2.0))
        se = math.sqrt(want * (1 - want) / len(truth))
        self.assertLess(abs(err - want), 4 * se + 1e-4)

    def test_the_selective_guarantee_holds_on_fresh_draws(self):
        mu, sd = E.table_arrays(_ref(), MEASURES)
        X, truth, _ = E.fields(_values(150, seed=41), 3)
        post = E.posterior(E.log_evidence(E.field_loglik(X, mu, sd, SYNTH), E.quadrature(0.07)[1]))
        top, hit = post.max(1), post.argmax(1) == truth
        for t in (0.5, 0.9):
            sel = top >= t
            prec = float(hit[sel].mean())
            se = math.sqrt(prec * (1 - prec) / sel.sum()) + 1e-3
            self.assertGreater(prec, t - 3 * se)
        # and the error the posterior predicts is the error counted
        self.assertLess(abs(float((1 - top).mean()) - float(1 - hit.mean())), 0.03)

    def test_credible_sets_hold_their_mass_and_are_smallest(self):
        rng = np.random.default_rng(0)
        post = rng.dirichlet(np.ones(6) * 0.3, size=200)
        size, member = E.credible_sets(post, 0.9)
        self.assertTrue(np.all((post * member).sum(1) >= 0.9 - 1e-12))
        for p, k in zip(post, size):
            self.assertLess(np.sort(p)[::-1][:k - 1].sum(), 0.9)

    def test_mapping_quality_is_capped(self):
        self.assertAlmostEqual(float(E.mapq(np.array([0.999]))[0]), 30.0, places=6)
        self.assertEqual(float(E.mapq(np.array([1.0]))[0]), E.MAPQ_CAP)


class TestFormula(unittest.TestCase):
    def test_log_moments_follow_a_draw_where_the_spread_is_small(self):
        ref = _ref()
        mu, sd = E.table_arrays(ref, MEASURES)
        V = _values(6000, seed=8)
        n, start = 3, 10
        y = np.log(V[:, :, start:start + n].reshape(len(V), -1))
        mean, cov = E.log_moments(mu, sd, start, n, SYNTH)
        self.assertLess(float(np.abs(y.mean(0) - mean).max()), 0.01)
        rel = np.abs(np.cov(y.T) - cov) / np.sqrt(np.outer(np.diag(cov), np.diag(cov)))
        self.assertLess(float(rel.max()), 0.1)

    def test_formula_names_fields_close_to_the_exact_rule(self):
        mu, sd = E.table_arrays(_ref(), MEASURES)
        X, truth, _ = E.fields(_values(100, seed=12), 5)
        a = E.posterior(E.log_evidence(E.field_loglik(X, mu, sd, SYNTH), E.quadrature(0.07)[1])).argmax(1)
        b = E.posterior(E.formula_log_evidence(X, mu, sd, SYNTH)).argmax(1)
        self.assertGreater(float((a == b).mean()), 0.9)


class TestClaims(unittest.TestCase):
    def test_open_cuts_leave_out_what_the_field_size_settles(self):
        self.assertEqual(len(E.open_cuts(1)), E.L - 1)
        names = [E.CUT_NAMES[c - 1] for c in E.open_cuts(3)]
        self.assertNotIn("C3/C4", names)
        self.assertNotIn("L4/L5", names)
        self.assertIn("C4/C5", names)
        self.assertIn("L3/L4", names)

    def test_below_is_monotone_and_decisions_match_it(self):
        rng = np.random.default_rng(1)
        tp = rng.dirichlet(np.ones(E.L) * 0.2, size=300)
        say, below = E.cut_decisions(tp, 0.95)
        self.assertTrue(np.all(np.diff(below, axis=1) <= 1e-12))
        self.assertTrue(np.all((say == 1) == (below >= 0.95)))
        self.assertTrue(np.all((say == -1) == (below <= 0.05)))

    def test_shortest_interval_is_minimal(self):
        rng = np.random.default_rng(2)
        tp = rng.dirichlet(np.ones(E.L) * 0.3, size=100)
        start, width = E.shortest_intervals(tp, 0.9)
        for p, a, w in zip(tp, start, width):
            self.assertGreaterEqual(p[a:a + w].sum(), 0.9 - 1e-12)
            if w > 1:
                best = max(p[i:i + w - 1].sum() for i in range(E.L - w + 2))
                self.assertLess(best, 0.9)

    def test_target_posterior_moves_the_place_posterior(self):
        post = np.array([[0.2, 0.8] + [0.0] * (E.L - 3 - 2 + 1)])
        tp = E.target_posterior(post / post.sum(), 3)
        self.assertAlmostEqual(float(tp[0, 1]), 0.2)
        self.assertAlmostEqual(float(tp[0, 2]), 0.8)
        self.assertAlmostEqual(float(tp.sum()), 1.0)


class TestTallies(unittest.TestCase):
    """The subset walk keeps its own tallies; the subset of all seven measures is the 'both'
    regime, so its tallies must agree with the regime's full summary on the same fields."""

    @classmethod
    def setUpClass(cls):
        ref = _ref()
        cls.mu, cls.sd = E.table_arrays(ref, MEASURES)
        cls.V = _values(8, seed=97, ref=ref)
        keep = {k: sorted(MEASURES.index(m) for m in v) for k, v in E.REGIMES.items()}
        cls.out = E.width_study(cls.V, cls.mu, cls.sd, SYNTH, 3, MEASURES, keep)

    def test_all_seven_subset_is_the_both_regime(self):
        full = [s for s in self.out["subsets"] if s["k"] == len(MEASURES)][0]
        both = self.out["regimes"]["both"]
        self.assertAlmostEqual(full["exact"], both["exact"], places=12)
        self.assertAlmostEqual(full["answered_099"], both["selective"]["0.99"]["answered"], places=12)
        for cut, row in both["claims"]["cuts"].items():
            self.assertAlmostEqual(full["claims"]["cuts_decided"][cut], row["decided"], places=12)
            self.assertEqual(full["claims"]["cuts_errors"][cut], row["errors"])
            if cut in full["claims"]["cuts_decided_within_two"]:
                self.assertAlmostEqual(full["claims"]["cuts_decided_within_two"][cut], row["decided_within_two"], places=12)

    def test_cut_tally_agrees_with_the_claims_summary(self):
        X, truth, _ = E.fields(self.V, 3)
        _, logw = E.quadrature(SYNTH["scale_sd"])
        post = E.posterior(E.log_evidence(E.field_loglik(X, self.mu, self.sd, SYNTH), logw))
        tally = E.cut_tally(post, truth, 3)
        summ = E.claims_summary(post, truth, 3, detail=False)
        for cut, (dec, err, nf, nd, ne, nn) in tally.items():
            row = summ["cuts"][cut]
            self.assertEqual((dec, err, nf), (row["n_decided"], row["errors"], len(truth)))
            self.assertEqual((nd, ne, nn), (row["n_decided_within_two"], row["errors_within_two"], row["n_within_two"]))

    def test_near_claims_by_column_sum_to_the_tallies(self):
        X, truth, grp = E.fields(self.V, 3)
        _, logw = E.quadrature(SYNTH["scale_sd"])
        post = E.posterior(E.log_evidence(E.field_loglik(X, self.mu, self.sd, SYNTH), logw))
        made, wrong = E.near_claims_by_group(post, truth, grp, 3)
        tally = np.array(list(E.cut_tally(post, truth, 3).values())).sum(0)
        self.assertEqual((int(made.sum()), int(wrong.sum())), (int(tally[3]), int(tally[4])))
        self.assertEqual(len(made), len(self.V))

    def test_within_two_is_the_four_levels_either_side_of_the_border(self):
        """At the border c (between levels c - 1 and c), within two holds levels c - 2 to c + 1."""
        n, c = 1, 10
        truth = np.arange(E.L)
        post = np.eye(E.L)                                    # every call right, every claim made
        row = E.cut_tally(post, truth, n)[E.CUT_NAMES[c - 1]]
        self.assertEqual(row[5], 4)
        self.assertEqual(row[3], 4)
        self.assertEqual(row[1], 0)


class TestRobust(unittest.TestCase):
    def test_specimen_table_is_centred_on_the_published_one(self):
        ref = _ref()
        rng = np.random.default_rng(4)
        diffs = []
        for _ in range(30):
            t = E.redrawn_table(ref, MEASURES, rng, "specimens", SYNTH)
            diffs.append([t["h_post"][lv][0] - ref["h_post"][lv][0] for lv in E.LEVELS])
        self.assertLess(float(np.abs(np.mean(diffs, axis=0)).max()), 0.6)

    def test_redrawn_levels_keep_the_table_shape(self):
        ref = _ref()
        t = E.redrawn_table(ref, MEASURES, np.random.default_rng(5), "levels", SYNTH)
        self.assertEqual(set(t["canal_w"]), set(ref["canal_w"]))

    def test_honest_table_grows_every_sd_by_the_twelve_spine_error_and_keeps_the_means(self):
        ref = _ref()
        t = E.rule_table(ref, MEASURES, {"table_n": 12})
        for m in MEASURES:
            for lv in E.LEVELS:
                self.assertEqual(t[m][lv][0], ref[m][lv][0])
                self.assertAlmostEqual(t[m][lv][1], ref[m][lv][1] * math.sqrt(13.0 / 12.0), places=12)
        self.assertEqual(E.rule_table(ref, MEASURES, {}), {m: dict(ref[m]) for m in ref})

    def test_mean_error_of_twelve_spines_is_the_inflation(self):
        """The covariance of a field drawn about twelve-spine means, over draws of the means, is
        (1 + 1/12) times the generator's, the error left out: what sqrt(1 + 1/12) claims."""
        rng = np.random.default_rng(8)
        sd = np.array([2.0, 3.0, 4.0])
        rho = 0.5
        shape = rho * rho * np.ones((3, 3)) + (1 - rho * rho) * np.eye(3)
        S = np.outer(sd, sd) * shape
        draws = rng.multivariate_normal(np.zeros(3), S, size=(40000, 13))
        diff = draws[:, 0, :] - draws[:, 1:, :].mean(1)        # a new spine about the twelve's mean
        emp = np.cov(diff.T)
        self.assertLess(float(np.abs(emp / (S * 13.0 / 12.0) - 1.0).max()), 0.05)

    def test_predictive_table_takes_the_t_variance(self):
        ref = _ref()
        t = E.rule_table(ref, MEASURES, E.RULES["predictive"])
        f = math.sqrt(13.0 / 12.0 * 11.0 / 9.0)
        for m in MEASURES:
            for lv in E.LEVELS:
                self.assertEqual(t[m][lv][0], ref[m][lv][0])
                self.assertAlmostEqual(t[m][lv][1], ref[m][lv][1] * f, places=12)

    def test_redrawn_levels_sd_is_the_sd_a_twelve_spine_estimate_could_come_from(self):
        """If the printed SD is a twelve-spine estimate s, the true sigma given s is s over
        sqrt(chi^2_11 / 11), whose square averages s^2 11 / 9: the redraw must lean wide."""
        ref = _ref()
        rng = np.random.default_rng(11)
        ratios = []
        for _ in range(60):
            t = E.redrawn_table(ref, MEASURES, rng, "levels", SYNTH)
            ratios += [(t[m][lv][1] / ref[m][lv][1]) ** 2 for m in MEASURES for lv in E.LEVELS]
        self.assertAlmostEqual(float(np.mean(ratios)), 11.0 / 9.0, delta=0.03)

    def test_biased_tables(self):
        ref = _ref()
        g = E.biased_table(ref, MEASURES, "gradient")
        c = E.biased_table(ref, MEASURES, "canal_low")
        for m in MEASURES:
            self.assertAlmostEqual(g[m]["C3"][0], ref[m]["C3"][0], places=12)
            self.assertAlmostEqual(g[m]["L5"][0], ref[m]["L5"][0] * 1.05, places=12)
            f = 0.92 if m.startswith("canal") else 1.0
            self.assertAlmostEqual(c[m]["T6"][0], ref[m]["T6"][0] * f, places=12)
        self.assertTrue(any(m.startswith("canal") for m in MEASURES))
        with self.assertRaises(ValueError):
            E.biased_table(ref, MEASURES, "other")

    def test_ratio_se_with_equal_worlds_is_the_se_of_the_world_rates(self):
        rng = np.random.default_rng(3)
        answered = np.full(12, 200)
        errors = rng.binomial(200, 0.02, size=12)
        rates = errors / answered
        self.assertAlmostEqual(E.ratio_se(errors, answered), float(rates.std(ddof=1) / math.sqrt(12)), places=12)
        self.assertTrue(math.isnan(E.ratio_se([1], [10])))

    def test_robust_tasks_are_fixed_by_their_seed(self):
        self.assertEqual(E.robust_tasks(3, seed=29), E.robust_tasks(3, seed=29))
        kinds = [t[0] for t in E.robust_tasks(3, seed=29)]
        self.assertEqual(kinds.count("table"), 6)
        self.assertEqual(kinds.count("misspecified"), 1 + sum(len(v) for v in E.MISSPEC.values()))
        self.assertEqual(kinds.count("bias"), len(E.BIASES))
        self.assertEqual(kinds.count("combined"), E.COMBINED_WORLDS)
        self.assertEqual(kinds.count("pilot"), E.PILOT_WORLDS)
        # one kind's seeds do not move when another kind has more worlds
        self.assertEqual([t for t in E.robust_tasks(3) if t[0] == "pilot"],
                         [t for t in E.robust_tasks(5) if t[0] == "pilot"])
        self.assertEqual([t for t in E.robust_tasks(3) if t[0] == "table"][:3],
                         [t for t in E.robust_tasks(5) if t[0] == "table"][:3])

    def test_a_robust_task_runs_every_rule_on_one_world(self):
        ref = _ref()
        task = [t for t in E.robust_tasks(1) if t[0] == "pilot"][0]
        got_task, out = E.robust_task(task, ref, MEASURES, SYNTH, n_columns=4)
        self.assertEqual(got_task, task)
        self.assertEqual(set(out), set(E.PILOT_RULES))
        self.assertEqual(set(out["nominal"]), {str(n) for n in E.PILOT_WIDTHS})
        pooled = E.pool_cells([out["nominal"], out["predictive"]])
        self.assertEqual(pooled["3"]["worlds"], 2)
        self.assertIn("cuts_precision_within_two", pooled["3"]["claims"])


class TestChallengers(unittest.TestCase):
    def test_network_learns_a_separable_problem_and_keeps_its_best_step(self):
        rng = np.random.default_rng(0)
        t = rng.integers(0, 3, 600)
        Y = rng.normal(0, 0.3, (600, 2)) + np.array([[0, 0], [3, 0], [0, 3]])[t]
        ts = rng.integers(0, 3, 300)
        Ys = rng.normal(0, 0.3, (300, 2)) + np.array([[0, 0], [3, 0], [0, 3]])[ts]
        prob, step, losses, _ = E.train_network(Y, t, Ys, ts, 3, hidden=8, max_steps=400, check_every=50)
        self.assertEqual(step % 50, 0)
        self.assertEqual(len(losses), 8)
        self.assertAlmostEqual(losses[step // 50 - 1], min(losses), places=12)
        self.assertGreater(float((prob(Ys).argmax(1) == ts).mean()), 0.98)

    def test_fitted_qda_recovers_its_gaussians(self):
        rng = np.random.default_rng(1)
        t = np.repeat([0, 1], 4000)
        Y = rng.normal(0, 1, (8000, 2)) * np.array([1.0, 2.0]) + np.array([[0, 0], [1, 1]])[t]
        stats = E.fitted_qda(Y, t, 2)
        ll = E.qda_log_evidence(stats, np.array([[0.0, 0.0]]))
        want = [multivariate_normal(m, np.diag([1.0, 4.0])).logpdf([0, 0]) + math.log(2 * math.pi) for m in ([0, 0], [1, 1])]
        self.assertTrue(np.allclose(ll[0], want, atol=0.05))

    def test_challenger_study_sets_each_rule_beside_the_exact_one(self):
        ref = _ref()
        mu, sd = E.table_arrays(ref, MEASURES)
        V = _values(6, seed=97, ref=ref)
        out = E.challenger_study(ref, MEASURES, SYNTH, V, mu, sd, widths=(3,), n_fit=60, n_select=20)
        row = out["3"]
        self.assertEqual(set(row), {"exact", "closed_form", "qda_log", "qda_raw", "network"})
        for name in ("closed_form", "qda_log", "qda_raw", "network"):
            self.assertAlmostEqual(row[name]["minus_exact"], row[name]["exact"] - row["exact"]["exact"], places=12)
        X, truth, grp = E.fields(V, 3)
        _, logw = E.quadrature(SYNTH["scale_sd"])
        direct = E.summary(E.posterior(E.log_evidence(E.field_loglik(X, mu, sd, SYNTH), logw)), truth, grp, 3, False)
        self.assertAlmostEqual(row["exact"]["exact"], direct["exact"], places=12)


class TestRecord(unittest.TestCase):
    def test_save_writes_whole_files_and_a_failed_part_is_recorded(self):
        import tempfile
        from concurrent.futures import Future
        with tempfile.TemporaryDirectory() as d:
            E.save({"a": 1, "complete": False}, d)
            E.save({"a": 2, "complete": True}, d)
            import json
            with open(os.path.join(d, "exact.json")) as fh:
                self.assertEqual(json.load(fh), {"a": 2, "complete": True})
            self.assertEqual(sorted(os.listdir(d)), ["exact.json"])
        f = Future()
        f.set_exception(MemoryError("out"))
        self.assertEqual(E._result(f, "test"), {"error": "MemoryError: out"})


if __name__ == "__main__":
    unittest.main()

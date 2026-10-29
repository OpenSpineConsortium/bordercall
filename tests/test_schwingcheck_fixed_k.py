"""The fixed-k NUTS review (fixed_k.py) on fields small enough for a test, and its record as committed.

    python -m unittest tests.test_schwingcheck_fixed_k -v      # from the repository's root, in the PyMC venv

free_level is the naming model's field written with the patient's offsets explicit: its log density
at a place, a size and offsets is place_loglik's with the priors, and with the offsets integrated
out it is rule.py's likelihood at that size, for every place and measure. The batch-means helpers
give a share and its error as a hand count does, and the Rao-Blackwellised posterior is the mean of
the place's conditional. Draws of log s made independently from its exact posterior have its mean
and SD, and the spread rows' posteriors are the exact posterior. A quick run gives every row its
tables read, the proportional proposal stops on a place all but certain and says why, the summed-out
model's averaged posterior is the exact one within its errors, each proposal on a bare place gives
the law its transition matrix leaves stationary, check finds a stale or missing table, and the
figures drawn twice are the same files. Liu's Metropolised Gibbs and the uniform proposal leave a
place's law stationary, and PyMC's proportional proposal, as its code computes the acceptance,
another law, or none on two places, where it never moves. The committed record: the README carries its
tables, it was made by committed code that did not change while it ran, and every claim the README
makes of it holds on its rows.
"""
from __future__ import annotations

import hashlib
import math
import os
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from schwingcheck import LEVELS                                   # noqa: E402
from schwingcheck import compiled as K                            # noqa: E402
from schwingcheck import fixed_k as FK                            # noqa: E402
from schwingcheck import rule as R                                # noqa: E402

# numpy's two ways of refusing the proportional proposal's weights where the current place is all but
# certain: 1 less its probability is 0 (NaN) or a rounding error far above the others' sum
PROPORTIONAL_STOPS = ("Probabilities contain NaN", "Probabilities do not sum to 1")


def quiet(*args):
    pass


def field(which: str = "seven", bodies: int = 3, f: int = 5):
    X, truth, _ = FK.draw_fields(8, bodies)
    mu, sd, noise, power, keys, idx = FK.cut(which)
    return X[f:f + 1][:, idx, :], int(truth[f]), mu, sd, noise, power


def sha256(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def mvn_logpdf(x: np.ndarray, mean: np.ndarray, cov: np.ndarray) -> float:
    r = x - mean
    sign, logdet = np.linalg.slogdet(cov)
    return float(-0.5 * (r @ np.linalg.solve(cov, r) + logdet + len(x) * math.log(2 * math.pi)))


class FreeLevel(unittest.TestCase):
    def test_its_density_is_place_loglik_with_the_priors(self):
        x, truth, mu, sd, noise, power = field()
        hyp = K.hypotheses(len(LEVELS), [[0, 1, 2]])
        m = FK.free_level(x, hyp, mu, sd, noise, power)
        logp = m.compile_logp()
        rng = np.random.default_rng(3)
        scale = float(R.SYNTH["scale_sd"])
        for k in (0, truth, len(hyp) - 1):
            log_s, z = rng.normal(0, scale), rng.normal(size=x.shape[1])
            want = (FK.place_loglik(np.array([log_s]), z[None], x, hyp, mu, sd, noise, power)[0, k]
                    - 0.5 * (log_s / scale) ** 2 - math.log(scale * math.sqrt(2 * math.pi))
                    - 0.5 * float(z @ z) - 0.5 * len(z) * math.log(2 * math.pi) - math.log(len(hyp)))
            got = float(logp({"log_s": log_s, "offset": z, "place": k}))
            self.assertAlmostEqual(got, want, places=8, msg="place %d" % k)

    def test_with_the_offsets_integrated_out_it_is_the_rules_likelihood(self):
        x, truth, mu, sd, noise, power = field()
        hyp = K.hypotheses(len(LEVELS), [[0, 1, 2]])
        rho = float(R.SYNTH["rho"])
        s = 1.04
        LL = R.loglik(x, [0, 1, 2], mu, sd, R.SYNTH, sizes=np.array([s]), noise=noise, power=power)[0, :, :, 0]
        self.assertEqual(LL.shape, (len(hyp), x.shape[1]))
        for k in (0, truth, len(hyp) - 1):
            for mi in range(x.shape[1]):
                sm = s ** power[mi]
                v = sd[mi, hyp.levels[k]]
                cov = (sm * rho) ** 2 * np.outer(v, v) + np.diag(sm * sm * (1 - rho * rho) * v * v + noise[mi] ** 2)
                want = mvn_logpdf(x[0, mi], sm * mu[mi, hyp.levels[k]], cov)
                self.assertAlmostEqual(LL[k, mi], want, places=8, msg="place %d, measure %d" % (k, mi))


class Helpers(unittest.TestCase):
    def test_the_counted_share_and_its_error_by_batch_means(self):
        labels = np.array([[0, 0, 1, 1, 1, 2], [2, 2, 2, 0, 0, 0]])
        share, se = FK.counted_posterior(labels, 3, n_batches=2)
        batches = np.array([[2 / 3, 1 / 3, 0], [0, 2 / 3, 1 / 3], [0, 0, 1], [1, 0, 0]])
        np.testing.assert_allclose(share, batches.mean(0))
        np.testing.assert_allclose(se, batches.std(0, ddof=1) / 2)

    def test_the_averaged_posterior_is_the_mean_of_the_conditional(self):
        x, truth, mu, sd, noise, power = field()
        hyp = K.hypotheses(len(LEVELS), [[0, 1, 2]])
        rng = np.random.default_rng(5)
        log_s = rng.normal(0, 0.05, size=(2, 6))
        z = rng.normal(size=(2, 6, x.shape[1]))
        idata = type("I", (), {"posterior": {"log_s": type("V", (), {"values": log_s}),
                                              "offset": type("V", (), {"values": z})}})
        post, se = FK.place_posterior(idata, x, hyp, mu, sd, noise, power, n_batches=3)
        ll = FK.place_loglik(log_s.reshape(-1), z.reshape(-1, x.shape[1]), x, hyp, mu, sd, noise, power)
        p = np.exp(ll - ll.max(1, keepdims=True))
        p /= p.sum(1, keepdims=True)
        np.testing.assert_allclose(post, p.mean(0), atol=1e-12)
        self.assertAlmostEqual(post.sum(), 1.0, places=12)


class Kernels(unittest.TestCase):
    def test_liu_and_the_uniform_proposal_leave_the_places_law_stationary(self):
        rng = np.random.default_rng(4)
        for k in (2, 3, 5):
            p = rng.dirichlet(np.ones(k))
            for how in ("uniform", "liu"):
                T = FK.proposal_kernel(p, how)
                np.testing.assert_allclose(T.sum(1), 1.0, atol=1e-12)
                np.testing.assert_allclose(FK.stationary(T), p, atol=1e-9)

    def test_pymcs_proportional_proposal_leaves_another_law_or_none(self):
        np.testing.assert_allclose(FK.proposal_kernel((0.89, 0.11), "proportional"), np.eye(2))
        self.assertIsNone(FK.stationary(FK.proposal_kernel((0.89, 0.11), "proportional")))
        pi = FK.stationary(FK.proposal_kernel((0.6, 0.3, 0.1), "proportional"))
        self.assertGreater(np.abs(pi - (0.6, 0.3, 0.1)).max(), 0.1)
        self.assertTrue(np.all(FK.proposal_kernel((0.889, 0.11, 0.001), "proportional") >= 0))


class ExactDraws(unittest.TestCase):
    def test_they_have_the_exact_posteriors_mean_and_sd(self):
        x, truth, mu, sd, noise, power = field()
        t, joint, _ = FK.size_posterior(x, 3, mu, sd, noise, power, step=FK.SAMPLER_STEP)
        g = FK.grid_summary(t, joint.sum(0))
        d = FK.exact_draws(x, 3, mu, sd, noise, power, (4, 50000), np.random.default_rng(1))
        self.assertLess(abs(d.mean() - g["mean"]), 4 * g["sd"] / math.sqrt(d.size))
        self.assertLess(abs(d.std() / g["sd"] - 1), 0.02)

    def test_the_spread_rows_posteriors_are_the_exact_posterior(self):
        x, truth, mu, sd, noise, power = field()
        exact = FK.exact_posterior_cut(x, 3, mu, sd, noise, power)[0]
        rows = FK.spread_rows(x, 3, mu, sd, noise, power, exact, FK.TAIL)
        got = np.array([r["posterior"] for r in rows])
        self.assertEqual(len(rows), len(exact))
        big = exact > 1e-4
        np.testing.assert_allclose(got[big], exact[big], rtol=1e-3)
        self.assertTrue(all(r["relative_variance"] >= 0 for r in rows))
        self.assertTrue(all(0 < r["size_mass_carrying_90pc"] <= 1 for r in rows))


class Quick(unittest.TestCase):
    """One quick run, written, read back and drawn twice."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = os.path.join(cls.tmp.name, "fixed_k.json")
        record, draws = FK.run(quick=True, log=quiet)
        FK.write(record, draws, cls.path)
        cls.record = FK.load(cls.path)
        cls.tables = FK.tables(cls.path)
        cls.drawn = []
        for i in range(2):
            out = os.path.join(cls.tmp.name, "figures-%d" % i)
            FK.draw_figures(out, cls.path)
            cls.drawn.append(out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_row_is_there(self):
        r = self.record
        q = FK.QUICK
        self.assertEqual([k["set"] for k in r["known"]], list(FK.SETS))
        self.assertTrue(all(len(k["fields"]) == q["known"]["fields"] for k in r["known"]))
        self.assertEqual(len(r["free"]), q["free"]["fields"] * len(FK.SETS))
        self.assertTrue(all([x["how"] for x in row["runs"]] == ["uniform", "proportional", "marginal"] for row in r["free"]))
        self.assertEqual(len(r["sharp"]), q["sharp"]["fields"])
        self.assertEqual(len(r["tail"]), 1 + q["tail"]["fields"])
        self.assertEqual(r["tail"][0]["field"], "example")
        for row in r["tail"]:
            self.assertEqual([len(row["runs"][k]) for k, _ in FK.METHODS],
                             [q["tail"]["runs"], q["tail"]["runs"], q["tail"]["long_runs"]])
        self.assertEqual(r["command"], "python -m schwingcheck.fixed_k run --quick")
        self.assertIn("pymc-extras", r["versions"])

    def test_the_known_runs_closed_form_is_a_density_of_log_s(self):
        for run in self.record["known"]:
            for row in run["fields"]:
                d = row["exact"]["density"]
                self.assertAlmostEqual(sum(d["mass"]), 1.0, delta=1e-6)
                self.assertLess(row["exact"]["eti89"][0], row["exact"]["mean"])
                self.assertLess(row["exact"]["mean"], row["exact"]["eti89"][1])

    def test_the_proportional_proposal_stops_where_the_place_is_certain(self):
        for row in self.record["sharp"]:
            runs = {x["how"]: x for x in row["runs"]}
            self.assertGreater(row["exact_top"], 1 - 1e-9)
            self.assertTrue(runs["proportional"]["error"].startswith(PROPORTIONAL_STOPS), runs["proportional"]["error"])
            self.assertNotIn("error", runs["uniform"])
            self.assertTrue(runs["marginal"]["rb_within"])

    def test_the_bare_place_rows_are_the_samplers_and_the_kernels(self):
        rows = self.record["categorical"]
        self.assertEqual([(tuple(r["probs"]), r["how"]) for r in rows],
                         [(tuple(p), how) for p in FK.QUICK["categorical"]["probs"] for how in ("uniform", "proportional")])
        for r in rows:
            share, se = np.array(r["share"]), np.array(r["share_se"])
            self.assertAlmostEqual(share.sum(), 1.0)
            np.testing.assert_allclose(r["liu_stationary"], r["probs"], atol=1e-9)
            law = r["probs"] if r["how"] == "uniform" else r["kernel_stationary"]
            if law is not None:
                self.assertTrue(np.all(np.abs(share - law) <= 5 * se + 0.05), (r["probs"], r["how"], share))
            else:
                self.assertIn(r["switch"], (0.0, 1.0), r["probs"])

    def test_the_averaged_posterior_is_exact_within_its_errors(self):
        for row in self.record["free"]:
            m = [x for x in row["runs"] if x["how"] == "marginal"][0]
            self.assertNotIn("error", m)
            self.assertAlmostEqual(sum(m["rb"]), 1.0, places=9)
            self.assertAlmostEqual(sum(row["exact"]), 1.0, places=9)

    def test_the_tables_read_the_rows(self):
        self.assertEqual(sorted(self.tables),
                         sorted("fixed_k:" + n for n in ("known", "free", "sharp", "tail", "spread", "categorical")))
        known = self.tables["fixed_k:known"].splitlines()
        rows = [x for x in known if x.startswith("| the seven") or x.startswith("| all ")]
        self.assertEqual(len(rows), sum(len(k["fields"]) for k in self.record["known"]))
        first = self.record["known"][0]["fields"][0]
        self.assertIn("%.4f, %.4f" % (first["nuts"]["mean"], first["nuts"]["sd"]), rows[0])
        free = [x for x in self.tables["fixed_k:free"].splitlines() if x.startswith("| the seven") or x.startswith("| all ")]
        self.assertEqual(len(free), sum(len(row["runs"]) for row in self.record["free"]))
        self.assertIn("stopped: Probabilities contain NaN", self.tables["fixed_k:sharp"])
        tail = [x for x in self.tables["fixed_k:tail"].splitlines() if x.startswith("| example") or x.startswith("| column")]
        self.assertEqual(len(tail), len(self.record["tail"]) * len(FK.METHODS))
        bare = [x for x in self.tables["fixed_k:categorical"].splitlines()[2:] if x.startswith("| ")]
        self.assertEqual(len(bare), len(self.record["categorical"]))
        self.assertIn("| 0.5, 0.5 | proportional |", self.tables["fixed_k:categorical"])

    def test_check_finds_a_stale_and_a_missing_table(self):
        text = "".join("<!-- %s -->\n%s<!-- /%s -->\n\n" % (k, v, k) for k, v in self.tables.items())
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
            fh.write(text)
        try:
            self.assertEqual(FK.check(fh.name, self.path), [])
            with open(fh.name, "w") as out:
                out.write(text.replace(self.tables["fixed_k:tail"], self.tables["fixed_k:tail"].replace("|", "| x", 1)))
            self.assertTrue(any("fixed_k:tail" in p for p in FK.check(fh.name, self.path)))
            with open(fh.name, "w") as out:
                out.write(text.split("<!-- fixed_k:spread -->")[0])
            self.assertTrue(any("fixed_k:spread" in p for p in FK.check(fh.name, self.path)))
        finally:
            os.unlink(fh.name)

    def test_drawn_twice_the_figures_are_the_same_files(self):
        a, b = (sorted(os.listdir(d)) for d in self.drawn)
        self.assertEqual(a, b)
        for name in ("fixed_k_trace", "fixed_k_forest", "fixed_k_mixing", "fixed_k_tail"):
            for ext in (".pdf", ".png", ".csv", ".caption.txt"):
                self.assertIn(name + ext, a)
        for f in a:
            if f == "FIGURES.md":
                continue
            self.assertEqual(*(sha256(os.path.join(d, f)) for d in self.drawn), f)


@unittest.skipUnless(os.path.exists(FK.RECORD), "no committed record")
class CommittedRecord(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = FK.load()

    def test_the_readme_carries_its_tables(self):
        self.assertEqual(FK.check(), [])

    def test_it_was_made_by_committed_code_that_did_not_change(self):
        made = self.record["made_by"]["git"]
        self.assertFalse(made["package_changed"])
        self.assertRegex(made["commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(self.record["changed_during_run"], {})
        self.assertEqual(self.record["command"], "python -m schwingcheck.fixed_k run")

    def test_nuts_on_known_levels_is_the_closed_form_within_its_errors(self):
        for run in self.record["known"]:
            self.assertEqual(run["divergences"], 0)
            for row in run["fields"]:
                self.assertLess(abs(row["z_mean"]), 4, row["field"])
                self.assertLess(abs(row["z_sd"]), 4, row["field"])
                self.assertLess(row["r_hat"], 1.01, row["field"])

    def test_the_summed_out_model_is_exact_within_its_errors_on_every_field(self):
        for row in self.record["free"]:
            m = [x for x in row["runs"] if x["how"] == "marginal"][0]
            self.assertTrue(m["rb_within"], row["field"])

    def test_the_uniform_proposal_leaves_chains_that_disagree(self):
        rhat = [x["rhat_top"] for row in self.record["free"] for x in row["runs"] if x["how"] == "uniform"]
        self.assertTrue(any(r > 1.1 for r in rhat if np.isfinite(r)))

    def test_on_a_bare_place_pymcs_proportional_proposal_samples_its_kernels_law_and_not_the_places(self):
        rows = self.record["categorical"]
        for r in rows:
            share, se = np.array(r["share"]), np.array(r["share_se"])
            if r["how"] == "uniform":
                self.assertTrue(np.all(np.abs(share - r["probs"]) <= 5 * se + 0.01), (r["probs"], share))
            elif r["kernel_stationary"] is None:
                self.assertIn(r["switch"], (0.0, 1.0), r["probs"])
                if r["switch"] == 0.0:
                    self.assertTrue(all(c in (0.0, 1.0) for c in r["chain_first"]), r["probs"])
            else:
                self.assertTrue(np.all(np.abs(share - r["kernel_stationary"]) <= 5 * se + 0.01), (r["probs"], share))
                self.assertGreater(np.abs(share - r["probs"]).max(), 0.1, r["probs"])

    def test_the_proportional_proposal_mixes_and_is_off_on_every_free_field(self):
        """Its chains agree, R-hat below 1.01 at the top place, and its share there is more than
        2.9 of its errors from the exact posterior on every field."""
        for row in self.record["free"]:
            p = [x for x in row["runs"] if x["how"] == "proportional"][0]
            top = int(np.argmax(row["exact"]))
            self.assertLess(p["rhat_top"], 1.01, row["field"])
            self.assertGreater(abs(p["counted"][top] - row["exact"][top]), 2.9 * p["counted_se"][top], row["field"])

    def test_a_stuck_chain_passes_the_five_error_bound_and_not_r_hat(self):
        """With the place summed out, one field's averaged posterior is within five errors plus
        0.001 of the exact one only because a stuck chain inflated the error: its R-hat is above 1.5."""
        stuck = [(row["field"], x["rb_gap"]) for row in self.record["free"] for x in row["runs"]
                 if x["how"] == "marginal" and x["rb_within"] and x["rhat_top"] > 1.5]
        self.assertEqual(len(stuck), 1, stuck)
        self.assertGreater(stuck[0][1], 0.1, stuck)

    def test_the_far_tail_runs_low_from_the_estimator_and_lower_on_nuts(self):
        """On every tail field the median estimate over the exact one is below 1 on NUTS's draws and
        on independent draws alike while the runs' mean is within 10 per cent of 1; NUTS's median is
        below the independent draws', and NUTS ten times as long brings it up."""
        spec = self.record["tail_spec"]
        for row in self.record["tail"]:
            t = {k: FK.tail_stats(row, k, spec["low"], spec["high"]) for k, _ in FK.METHODS}
            for k in ("nuts", "independent"):
                self.assertLess(t[k]["median_ratio"], 1.0, (row["field"], k))
                self.assertTrue(0.9 < t[k]["mean_ratio"] < 1.1, (row["field"], k, t[k]["mean_ratio"]))
            self.assertLess(t["nuts"]["median_ratio"], t["independent"]["median_ratio"], row["field"])
            self.assertGreater(t["nuts_long"]["median_ratio"], t["nuts"]["median_ratio"], row["field"])

    def test_the_proportional_proposal_stopped_on_every_sharp_field(self):
        for row in self.record["sharp"]:
            p = [x for x in row["runs"] if x["how"] == "proportional"][0]
            self.assertTrue(p.get("error", "").startswith(PROPORTIONAL_STOPS), (row["field"], p.get("error")))


if __name__ == "__main__":
    unittest.main()

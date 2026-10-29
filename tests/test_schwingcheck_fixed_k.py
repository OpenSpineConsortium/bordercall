"""The fixed-k NUTS review (fixed_k.py) on fields small enough for a test, and its record as committed.

    python -m unittest tests.test_schwingcheck_fixed_k -v      # from the repository's root, in the PyMC venv

free_level is the naming model's field written with the patient's offsets explicit: its log density
at a place, a size and offsets is place_loglik's with the priors, and with the offsets integrated
out it is rule.py's likelihood at that size, for every place and measure. The batch-means helpers
give a share and its error as a hand count does, and the Rao-Blackwellised posterior is the mean of
the place's conditional. Draws of log s made independently from its exact posterior have its mean
and SD, and the spread rows' posteriors are the exact posterior. A quick run gives every row its
tables read, the proportional proposal stops on a place all but certain and says why, the summed-out
model's averaged posterior is the exact one within its errors, outright where its chains agree and
flagged by R-hat where one sat in a far mode, each proposal on a bare place gives the law its
transition matrix leaves stationary, or never moves where it has none, check finds a stale or
missing table, and the figures drawn twice are the same files. Liu's Metropolised Gibbs and the uniform proposal leave a
place's law stationary, and PyMC's proportional proposal, as its code computes the acceptance with
its own rounding, another law, or on two places none, at 0.5 and 0.5, where it never moves, or each
place half, at 0.89 and 0.11, where it swaps at every step. The closed form's interval reads the
distribution function at the nodes. The committed record: the README carries its tables, it was made
by committed code that did not change while it ran, ArviZ's own trace and forest ran on its draws,
and the claims the README makes of it that the tests below name hold on its rows at the README's own
bounds.
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


def near(x: float, printed: str) -> bool:
    """Whether x rounds to the number as the README prints it, to its last digit, a tie read either
    way; a percentage is passed as its hundredfold and a comma in a count is dropped."""
    s = printed.replace(",", "")
    decimals = len(s.split(".")[1]) if "." in s else 0
    return abs(float(x) - float(s)) <= 0.5 * 10 ** -decimals + 1e-12


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
        """place_loglik's density, which the first test ties to free_level's, integrated over each
        measure's offset by Gauss-Hermite quadrature at a fixed size, is rule.loglik's log likelihood
        of that measure at that place and size; a measure's offset reaches no other measure, so the
        field is read one measure at a time."""
        x, truth, mu, sd, noise, power = field()
        hyp = K.hypotheses(len(LEVELS), [[0, 1, 2]])
        s = 1.04
        LL = R.loglik(x, [0, 1, 2], mu, sd, R.SYNTH, sizes=np.array([s]), noise=noise, power=power)[0, :, :, 0]
        self.assertEqual(LL.shape, (len(hyp), x.shape[1]))
        nodes, weights = np.polynomial.hermite_e.hermegauss(60)
        log_w = np.log(weights) - 0.5 * math.log(2 * math.pi)                     # the standard normal's weights
        for k in (0, truth, len(hyp) - 1):
            for mi in range(x.shape[1]):
                one = np.full_like(x, np.nan)
                one[0, mi] = x[0, mi]
                z = np.zeros((len(nodes), x.shape[1]))
                z[:, mi] = nodes
                ll = FK.place_loglik(np.full(len(nodes), math.log(s)), z, one, hyp, mu, sd, noise, power)[:, k]
                self.assertAlmostEqual(float(np.logaddexp.reduce(ll + log_w)), LL[k, mi], places=8,
                                       msg="place %d, measure %d" % (k, mi))


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

    def test_pymcs_proportional_proposal_leaves_another_law_or_on_two_places_none_or_half(self):
        """With PyMC's own rounding: at 0.5 and 0.5 the ratio divides by zero and the chain never
        moves, so no one law; at 0.89 and 0.11 the ratio is finite and large both ways, so the chain
        swaps at every step and its law is each place half; on three places another law than p."""
        np.testing.assert_allclose(FK.proposal_kernel((0.5, 0.5), "proportional"), np.eye(2))
        self.assertIsNone(FK.stationary(FK.proposal_kernel((0.5, 0.5), "proportional")))
        swap = FK.proposal_kernel((0.89, 0.11), "proportional")
        np.testing.assert_allclose(swap, [[0.0, 1.0], [1.0, 0.0]], atol=1e-12)
        np.testing.assert_allclose(FK.stationary(swap), [0.5, 0.5], atol=1e-12)
        pi = FK.stationary(FK.proposal_kernel((0.6, 0.3, 0.1), "proportional"))
        self.assertGreater(np.abs(pi - (0.6, 0.3, 0.1)).max(), 0.1)
        self.assertTrue(np.all(FK.proposal_kernel((0.889, 0.11, 0.001), "proportional") >= 0))

    def test_the_bare_log_density_is_pymcs_and_its_softmax_rounds_as_pymc_does(self):
        """bare_log_density is log p from PyMC's compiled Categorical, and the kernel from it is the
        kernel from any log density that softmaxes to the same probabilities; p / p.sum() rounds
        the other way at 0.89 and 0.11, where it gives the identity."""
        p = (0.89, 0.11)
        ld = FK.bare_log_density(p)
        np.testing.assert_allclose(np.exp(ld), p, rtol=1e-12)
        np.testing.assert_allclose(FK.proposal_kernel(p, "proportional", log_density=ld + 3.0),
                                   FK.proposal_kernel(p, "proportional"), atol=0)
        from scipy import special
        soft = special.softmax(ld)
        np.testing.assert_allclose(soft, p, rtol=1e-14)
        q = np.asarray(p) / np.sum(p)
        self.assertLess(soft[1] / (1.0 - soft[0]), 1.0)                 # PyMC's rounding: a finite ratio, the swap
        self.assertGreater(q[1] / (1.0 - q[0]), 1.0)                    # the plain division's: a negative one, no move


def example_field():
    """The README's example field, T11 to L1 with the seven, whose places T11 and T10 share the
    posterior, so that the size's posterior with the places summed out is not the top place's."""
    from schwingcheck import measures as MS
    from schwingcheck.__main__ import read_field
    x, _ = read_field(FK.EXAMPLE, list(MS.SPINEPS_7))
    mu, sd, noise, power, keys, idx = FK.cut("seven")
    return x, mu, sd, noise, power


class ExactDraws(unittest.TestCase):
    def test_they_have_the_exact_posteriors_mean_and_sd(self):
        """On the example field, where two places are likely: the draws' mean and SD are the
        summed-out posterior's and not the top place's conditional's, which lies more than the
        bounds away."""
        x, mu, sd, noise, power = example_field()
        t, joint, _ = FK.size_posterior(x, 3, mu, sd, noise, power, step=FK.SAMPLER_STEP)
        g = FK.grid_summary(t, joint.sum(0))
        top = FK.grid_summary(t, joint[int(np.argmax(joint.sum(1)))])
        d = FK.exact_draws(x, 3, mu, sd, noise, power, (4, 50000), np.random.default_rng(1))
        self.assertLess(abs(d.mean() - g["mean"]), 4 * g["sd"] / math.sqrt(d.size))
        self.assertLess(abs(d.std() / g["sd"] - 1), 0.02)
        self.assertGreater(abs(top["mean"] - g["mean"]), 4 * g["sd"] / math.sqrt(d.size))
        self.assertGreater(abs(top["sd"] / g["sd"] - 1), 0.02)

    def test_the_grid_summarys_interval_is_the_distribution_functions_at_the_nodes(self):
        """A normal density on a grid: the 89% interval is the normal's within a hundredth of a step
        where the cumulative sum alone would put it half a step low."""
        from scipy import stats
        step = 0.004
        t = np.arange(-0.4, 0.4 + step / 2, step)
        p = stats.norm.pdf(t, 0.01, 0.07)
        g = FK.grid_summary(t, p)
        want = stats.norm.ppf([0.055, 0.945], 0.01, 0.07)
        np.testing.assert_allclose(g["eti89"], want, atol=step / 20)
        low = [np.interp(q, np.cumsum(p / p.sum()), t) for q in (0.055, 0.945)]
        np.testing.assert_allclose(np.subtract(want, low), step / 2, atol=step / 20)

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
            self.assertGreaterEqual(run["arviz_plots"]["plot_trace_axes"], 2)       # ArviZ's own plots ran on the draws
            self.assertGreaterEqual(run["arviz_plots"]["plot_forest_axes"], 1)
            for row in run["fields"]:
                d = row["exact"]["density"]
                self.assertAlmostEqual(sum(d["mass"]), 1.0, delta=1e-6)
                self.assertLess(row["exact"]["eti89"][0], row["exact"]["mean"])
                self.assertLess(row["exact"]["mean"], row["exact"]["eti89"][1])
                t, p = np.asarray(d["log_s"]), np.asarray(d["mass"])
                np.testing.assert_allclose(row["exact"]["eti89"], FK.grid_summary(t, p)["eti89"], atol=1e-6)

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
                self.assertEqual(r["switch"], 0.0, r["probs"])              # the kernel is the identity: the chain never moved
                self.assertTrue(all(c in (0.0, 1.0) for c in r["chain_first"]), r["probs"])
        swap = [r for r in rows if r["how"] == "proportional" and tuple(r["probs"]) == (0.89, 0.11)]
        self.assertEqual(len(swap), 1)
        self.assertEqual(swap[0]["switch"], 1.0)
        np.testing.assert_allclose(swap[0]["kernel_stationary"], [0.5, 0.5], atol=1e-12)

    def test_the_averaged_posterior_is_exact_within_its_errors_and_a_stuck_chain_is_flagged(self):
        """On every quick free field the summed-out model's averaged posterior is the exact one
        within five of its errors plus 0.001; where its chains agree at the top place (R-hat below
        1.1) it is within 0.1 of the exact one outright, and at least one field is such; and where
        it is off by more than 0.1, a chain sat in a far mode and R-hat at the top place says so."""
        agreeing = 0
        for row in self.record["free"]:
            m = [x for x in row["runs"] if x["how"] == "marginal"][0]
            self.assertNotIn("error", m)
            self.assertAlmostEqual(sum(m["rb"]), 1.0, places=9)
            self.assertTrue(m["rb_within"], (row["field"], m["rb_gap"], m["rb_se"]))
            self.assertAlmostEqual(m["rb_gap"], float(np.abs(np.subtract(m["rb"], row["exact"])).max()), places=12)
            if m["rhat_top"] < 1.1:
                agreeing += 1
                self.assertLess(m["rb_gap"], 0.1, (row["field"], m["rb_gap"]))
            if m["rb_gap"] > 0.1:
                self.assertGreater(m["rhat_top"], 1.1, (row["field"], m["rb_gap"]))
        self.assertGreaterEqual(agreeing, 1)

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

    def test_its_figures_are_what_the_code_draws_from_it(self):
        """FIGURES.md names the record, the draws and the code by their hashes as they stand, and every
        committed figure file, PNG and PDF included, is what the code draws from the record now."""
        with open(os.path.join(FK.FIGURE_DIR, "FIGURES.md"), encoding="ascii") as fh:
            said = fh.read()
        for p in (FK.RECORD, FK.draws_path("seven")):
            self.assertIn("sha256 %s." % sha256(p), said)
        for name in ("figures.py", "fixed_k.py"):
            self.assertIn("`schwingcheck/%s`, sha256 %s." % (name, sha256(os.path.join(ROOT, "schwingcheck", name))), said)
        with tempfile.TemporaryDirectory() as tmp:
            drawn = sorted(os.path.basename(p) for p in FK.draw_figures(tmp, figures_md=False))
            self.assertEqual(len(drawn), 16, drawn)
            for name in drawn:
                self.assertIn("`%s`" % name, said)
                with open(os.path.join(tmp, name), "rb") as fa, open(os.path.join(FK.FIGURE_DIR, name), "rb") as fb:
                    self.assertEqual(fa.read(), fb.read(), name)

    # The README's own numbers, held to the record at the README's precision (near), so that a record
    # made again moves the prose with it or fails here.

    def runs(self, section: str, how: str):
        return [(row, [x for x in row["runs"] if x["how"] == how][0]) for row in self.record[section]]

    def test_the_readmes_numbers_for_the_level_known_are_the_records(self):
        """Every mean and SD within 1.9 Monte Carlo errors, R-hat 1.002 at most, a bulk ESS of 2,941 to
        6,698, no divergence, 7.0 and 14.6 leapfrog steps a draw, beta_height back as its prior (0.999,
        SD 0.51), and ArviZ's trace and forest drawn on every run, their panels counted."""
        runs = self.record["known"]
        rows = [row for run in runs for row in run["fields"]]
        self.assertTrue(near(max(abs(r["z_mean"]) for r in rows), "1.9"))
        self.assertTrue(near(max(abs(r["z_sd"]) for r in rows), "1.9"))
        self.assertTrue(near(max(r["r_hat"] for r in rows), "1.002"))
        self.assertTrue(near(min(r["ess_bulk"] for r in rows), "2,941"))
        self.assertTrue(near(max(r["ess_bulk"] for r in rows), "6,698"))
        self.assertEqual([run["set"] for run in runs], ["seven", "all"])
        self.assertTrue(near(runs[0]["steps"], "7.0") and near(runs[1]["steps"], "14.6"), [r["steps"] for r in runs])
        for run in runs:
            self.assertEqual(run["divergences"], 0)
            self.assertTrue(near(run["beta_height"]["mean"], "0.999") and near(run["beta_height"]["sd"], "0.51"))
            self.assertGreaterEqual(run["arviz_plots"]["plot_trace_axes"], 2)
            self.assertGreaterEqual(run["arviz_plots"]["plot_forest_axes"], 1)

    def test_the_readmes_numbers_for_the_uniform_proposal_are_the_records(self):
        """The place changes in 0.15% to 2.9% of draws; on the third field with the seven the chains put
        0.72, 0.32, 0.82 and 1.00 of their draws at the top place, the share is 0.714 where the exact
        posterior gives 0.519, R-hat 1.314 and log s's ESS 23; R-hat flags the five-body field (1.157)
        and not the first (1.006), whose chains still differ by 0.12."""
        runs = self.runs("free", "uniform")
        self.assertEqual([row["field"] for row, _ in runs], [56, 47, 112, 358])
        switch = [x["switch"] for _, x in runs]
        self.assertTrue(near(100 * min(switch), "0.15") and near(100 * max(switch), "2.9"), switch)
        row, x = runs[2]
        top = int(np.argmax(row["exact"]))
        self.assertTrue(all(near(c, s) for c, s in zip(x["chain_top"], ("0.72", "0.32", "0.82", "1.00"))), x["chain_top"])
        self.assertTrue(near(x["counted"][top], "0.714") and near(row["exact"][top], "0.519"))
        self.assertTrue(near(x["rhat_top"], "1.314") and near(x["log_s_ess"], "23"))
        self.assertTrue(near(runs[3][1]["rhat_top"], "1.157") and near(runs[0][1]["rhat_top"], "1.006"))
        first = runs[0][1]["chain_top"]
        self.assertTrue(near(max(first) - min(first), "0.12"), first)

    def test_the_readmes_numbers_for_the_proportional_proposal_are_the_records(self):
        """It changes the place in 41% to 97% of draws with R-hat 1.001 at most, its share at the top
        place 3 to 37 Monte Carlo errors off the exact posterior on every field, 0.593 where the exact
        posterior gives 0.890 on the five-body field; on a bare Categorical of 0.6, 0.3 and 0.1 its
        chains give 0.479, 0.411 and 0.110 and its kernel's law is 0.480, 0.408 and 0.112; on two
        places it never moves at 0.5 and 0.5 and swaps at every draw at 0.89 and 0.11, each place half."""
        runs = self.runs("free", "proportional")
        switch = [x["switch"] for _, x in runs]
        self.assertTrue(near(100 * min(switch), "41") and near(100 * max(switch), "97"), switch)
        self.assertTrue(near(max(x["rhat_top"] for _, x in runs), "1.001"))
        z = []
        for row, x in runs:
            top = int(np.argmax(row["exact"]))
            z.append(abs(x["counted"][top] - row["exact"][top]) / x["counted_se"][top])
        self.assertTrue(near(min(z), "3") and near(max(z), "37"), z)
        row, x = runs[3]
        top = int(np.argmax(row["exact"]))
        self.assertTrue(near(x["counted"][top], "0.593") and near(row["exact"][top], "0.890"))
        rows = {tuple(r["probs"]): r for r in self.record["categorical"] if r["how"] == "proportional"}
        three = rows[(0.6, 0.3, 0.1)]
        self.assertTrue(all(near(s, p) for s, p in zip(three["share"], ("0.479", "0.411", "0.110"))), three["share"])
        self.assertTrue(all(near(s, p) for s, p in zip(three["kernel_stationary"], ("0.480", "0.408", "0.112"))))
        half = rows[(0.5, 0.5)]
        self.assertEqual(half["switch"], 0.0)
        self.assertIsNone(half["kernel_stationary"])
        skew = rows[(0.89, 0.11)]
        self.assertEqual(skew["switch"], 1.0)
        self.assertEqual(skew["share"], [0.5, 0.5])
        self.assertTrue(all(near(s, "0.500") for s in skew["kernel_stationary"]))

    def test_the_readmes_numbers_for_the_place_summed_out_are_the_records(self):
        """Within 0.001 to 0.010 of the exact posterior on the three fields with the seven, R-hat 1.005
        at most; on the five-body field with all 32 one chain of four took the bodies for L1 to L5,
        exact 9e-53, so the share at the top place is 0.668 where it is 0.890, its error 0.062,
        R-hat 1.825 at the place and 1.53 at log s."""
        runs = self.runs("free", "marginal")
        seven = [x for row, x in runs if row["set"] == "seven"]
        self.assertEqual(len(seven), 3)
        self.assertTrue(near(min(x["rb_gap"] for x in seven), "0.001") and near(max(x["rb_gap"] for x in seven), "0.010"))
        self.assertTrue(near(max(x["rhat_top"] for x in seven), "1.005"))
        row, x = runs[3]
        self.assertEqual((row["set"], row["bodies"]), ("all", 5))
        top = int(np.argmax(row["exact"]))
        lumbar = [row["places"].index(p) for p in ("L1", "L2", "L3", "L4", "L5") if p in row["places"]]
        self.assertTrue(8.5e-53 <= sum(row["exact"][i] for i in lumbar) <= 9.5e-53)
        self.assertTrue(near(min(x["chain_top"]), "0.00"), x["chain_top"])
        self.assertTrue(near(x["rb"][top], "0.668") and near(row["exact"][top], "0.890") and near(x["rb_se"][top], "0.062"))
        self.assertTrue(near(x["rhat_top"], "1.825") and near(x["log_s_rhat"], "1.53"))

    def test_the_readmes_numbers_for_the_sharp_fields_are_the_records(self):
        """Four nine-body fields with all 32, the true place at 1.000000: the proportional proposal
        stops with NaN on three and with probabilities that do not sum to one on the fourth, and the
        uniform step never moves and is within 4e-22 of the exact posterior."""
        rows = self.record["sharp"]
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(row["exact_top"] > 1 - 1e-6 for row in rows))
        errors = [x.get("error", "") for row, x in self.runs("sharp", "proportional")]
        self.assertEqual(sum(e.startswith("Probabilities contain NaN") for e in errors), 3, errors)
        self.assertEqual(sum(e.startswith("Probabilities do not sum to 1") for e in errors), 1, errors)
        for row, x in self.runs("sharp", "uniform"):
            self.assertEqual(x["switch"], 0.0, row["field"])
            self.assertLess(x["counted_gap"], 4e-22, row["field"])

    def test_the_readmes_numbers_for_the_far_tail_are_the_records(self):
        """The median estimate over the exact one is 0.948 on NUTS's draws and 0.965 on independent
        ones on the example field, 0.863 and 0.984 on the second, 0.406 and 0.850 on the third; the
        median over the places of the runs' mean is 0.97 to 1.04 for both, single places' means
        0.52 to 3.66; NUTS ten times as long brings the median to 0.987, 0.981 and 0.792; the example
        field's T6, at 6.35e-6, has 90% of its mass on 0.013% of the size's posterior and takes
        3,454,310 independent draws for 10 per cent."""
        spec = self.record["tail_spec"]
        rows = self.record["tail"]
        self.assertEqual([row["field"] for row in rows], ["example", "column 32, T9", "column 8, T8"])
        medians = {"nuts": ("0.948", "0.863", "0.406"), "independent": ("0.965", "0.984", "0.850"),
                   "nuts_long": ("0.987", "0.981", "0.792")}
        means, per_place = [], []
        for row, i in zip(rows, range(3)):
            for method, printed in medians.items():
                t = FK.tail_stats(row, method, spec["low"], spec["high"])
                self.assertTrue(near(t["median_ratio"], printed[i]), (row["field"], method, t["median_ratio"]))
                if method != "nuts_long":
                    means.append(t["mean_ratio"])
                    ex = np.asarray(row["exact"])
                    tail = (ex > spec["low"]) & (ex < spec["high"])
                    est = np.array([r["post"] for r in row["runs"][method]])
                    per_place += list(est[:, tail].mean(0) / ex[tail])
        self.assertTrue(near(min(means), "0.97") and near(max(means), "1.04"), means)
        self.assertTrue(near(min(per_place), "0.52") and near(max(per_place), "3.66"), (min(per_place), max(per_place)))
        t6 = [s for s in rows[0]["spread"] if s["place"] == "T6"][0]
        self.assertLess(abs(t6["posterior"] / 6.35e-6 - 1), 1e-3)
        self.assertTrue(near(100 * t6["size_mass_carrying_90pc"], "0.013") and near(t6["draws_for_10pc"], "3,454,310"))


if __name__ == "__main__":
    unittest.main()

"""The PyMC rewrite of step d against the NumPy reference, each claim checked against code it
does not share: rule.py, the compiled rule, ArviZ, or a closed form on a grid.

- The compiled rule (compiled.py) equals rule.py to 1e-10 on contiguous, gapped and incomplete
  fields, under every regime and with each measure's own error, and its generalisations (several
  gap patterns at once, a size prior of each field's own, scaled means) equal what rule.py
  computes for each case by hand.
- The naming model (model.py), integrated over log s on rule.py's nodes, equals the compiled rule
  to 1e-6, and its observed density is rule.py's likelihood summed over the hypotheses, at three
  sizes and at every node of the rule's quadrature, and integrated over the sizes; sampled by
  NUTS, its Rao-Blackwellised posterior is within five Monte Carlo standard errors of the exact
  one at every place above 0.05 and within five plus 1e-3 everywhere, with no discrete variable
  sampled, and at the places above 0.05 its errors are within 0.6 to 1.6 of ArviZ's own for the
  same draws and as large as their distances from the exact posterior, a mean square z between 0.4
  and 2.5, bounds a correct sampler crosses in fewer than one run in a thousand.
- The covariates leave the archive's answers where nothing is known, and a known height or a
  non-zero hook moves the model exactly as it moves the compiled rule.
- The fixed-level baseline's NUTS posterior of log s is the closed form's, integrated on a grid.
- The PyMC generator's columns match the NumPy generator's in distribution.
- The committed graphs are the models' graphs, and the README draws each of them.
"""
from __future__ import annotations

import math
import os
import sys
import unittest
import warnings

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from schwingcheck import LEVELS                  # noqa: E402
from schwingcheck import columns as C            # noqa: E402
from schwingcheck import compiled as K           # noqa: E402
from schwingcheck import covariates as CV        # noqa: E402
from schwingcheck import measures as MS          # noqa: E402
from schwingcheck import model as MD             # noqa: E402
from schwingcheck import rule as R               # noqa: E402

warnings.filterwarnings("ignore", module="pymc")
warnings.filterwarnings("ignore", module="pytensor")
warnings.filterwarnings("ignore", module="arviz")

# an error of each measure's own, unlike the archive's 1 mm for all, to hold every path that
# carries the errors to the one that does not share its arithmetic
NOISE = np.array([0.6, 1.0, 1.4, 2.0, 0.8, 1.2, 2.5])


def seven():
    ms = MS.select(MS.SPINEPS_7)
    mu, sd = MS.arrays(ms)
    return MS.reference(ms), [MS.archive_key(m) for m in ms], mu, sd


def fields(offsets, n_columns, seed, n_fields=None, missing=0.0):
    """Fields of the typical column drawn by columns.py, a sample of them when n_fields is given,
    with a share of their values blanked."""
    ref, keys, mu, sd = seven()
    cols = C.draw_columns(ref, ["typical"], seed, n_columns, keys)
    X, truth, _ = C.fields(cols.values, offsets)
    rng = np.random.default_rng(seed + 1)
    if n_fields is not None:
        pick = rng.choice(len(X), n_fields, replace=False)
        X, truth = X[pick], truth[pick]
    if missing:
        X = np.where(rng.random(X.shape) < missing, np.nan, X)
    return X, truth, keys, mu, sd


def softmax(a):
    a = np.exp(a - a.max(axis=1, keepdims=True))
    return a / a.sum(axis=1, keepdims=True)


class CompiledRule(unittest.TestCase):
    def _same(self, X, offsets, mu, sd, subsets=None, noise=None):
        hyp = K.hypotheses(len(LEVELS), [offsets])
        got = K.ExactRule(mu, sd, noise=noise).evaluate(X, hyp, subsets=subsets)
        sizes, logw = R.quadrature(R.SYNTH["scale_sd"])
        LL = R.loglik(X, offsets, mu, sd, R.SYNTH, sizes=sizes, noise=noise)
        for name, idx in (subsets or {"all": range(X.shape[1])}).items():
            logev = R.log_evidence(LL, logw, list(idx))
            self.assertLess(np.abs(got[name]["logev"] - logev).max(), 1e-10, name)
            self.assertLess(np.abs(got[name]["post"] - R.posterior(logev)).max(), 1e-10, name)

    def test_it_equals_rule_py_at_1_3_and_9_bodies_under_every_regime(self):
        for n in (1, 3, 9):
            X, _, keys, mu, sd = fields(list(range(n)), 12, 31)
            regimes = {name: sorted(MS.SPINEPS_7.index(k) for k in ks) for name, ks in MS.REGIMES.items()}
            self._same(X, list(range(n)), mu, sd, regimes)

    def test_each_measures_own_error_is_rule_pys(self):
        X, _, keys, mu, sd = fields([0, 2, 4], 8, 36, missing=0.2)
        self._same(X, [0, 2, 4], mu, sd, noise=NOISE)
        one = K.ExactRule(mu, sd).evaluate(X, K.hypotheses(len(LEVELS), [[0, 2, 4]]))["all"]["logev"]
        own = K.ExactRule(mu, sd, noise=NOISE).evaluate(X, K.hypotheses(len(LEVELS), [[0, 2, 4]]))["all"]["logev"]
        self.assertGreater(np.abs(own - one).max(), 1.0)
        with self.assertRaises(ValueError):
            K.ExactRule(mu, sd, noise=NOISE[:3])

    def test_it_equals_rule_py_on_gapped_fields_with_values_missing(self):
        X, _, keys, mu, sd = fields([0, 2, 4], 10, 32, missing=0.25)
        X[0] = np.nan                                   # a field with nothing read gets the prior
        X[1, 3] = np.nan                                # a measure missing on every body
        self._same(X, [0, 2, 4], mu, sd)
        post = K.ExactRule(mu, sd).name(X[:1], [0, 2, 4])["all"]
        self.assertLess(np.abs(post - 1.0 / post.shape[1]).max(), 1e-12)

    def test_several_gap_patterns_are_scored_as_the_union_of_one_pattern_each(self):
        X, _, keys, mu, sd = fields([0, 1, 2], 6, 33, n_fields=20)
        rule = K.ExactRule(mu, sd)
        pats = [[0, 1, 2], [0, 2, 4]]
        both = rule.evaluate(X, K.hypotheses(len(LEVELS), pats))["all"]
        one = [rule.evaluate(X, K.hypotheses(len(LEVELS), [p]))["all"]["logev"] for p in pats]
        self.assertLess(np.abs(both["logev"] - np.concatenate(one, axis=1)).max(), 1e-12)
        self.assertLess(np.abs(both["post"] - softmax(np.concatenate(one, axis=1))).max(), 1e-12)
        hyp = K.hypotheses(len(LEVELS), pats)
        by_place, by_pattern = K.marginal(both["post"], hyp, "place"), K.marginal(both["post"], hyp, "pattern")
        self.assertLess(np.abs(by_place.sum(1) - 1).max(), 1e-12)
        self.assertLess(np.abs(by_pattern.sum(1) - 1).max(), 1e-12)
        k = 5
        want = both["post"][:, (hyp.place == k)].sum(1)
        self.assertLess(np.abs(by_place[:, k] - want).max(), 1e-15)
        sizes, logw = R.quadrature(R.SYNTH["scale_sd"])
        by_rule = np.concatenate([R.log_evidence(R.loglik(X, p, mu, sd, R.SYNTH, sizes=sizes), logw)
                                  for p in pats], axis=1)
        self.assertLess(np.abs(both["logev"] - by_rule).max(), 1e-10)

    def test_a_size_prior_of_each_fields_own_reweights_the_nodes(self):
        X, _, keys, mu, sd = fields([0, 1, 2], 4, 34, n_fields=15)
        rule = K.ExactRule(mu, sd)
        hyp = K.hypotheses(len(LEVELS), [[0, 1, 2]])
        t = np.log(rule.sizes)
        base = R.SYNTH["scale_sd"]
        same = K.size_log_weights(t, rule.logw, base, np.zeros(len(X)), np.full(len(X), base))
        self.assertTrue(np.array_equal(same, np.broadcast_to(rule.logw, same.shape)))
        mean, spread = np.linspace(-0.05, 0.06, len(X)), np.linspace(0.06, 0.09, len(X))
        got = rule.evaluate(X, hyp, logw=K.size_log_weights(t, rule.logw, base, mean, spread))["all"]["logev"]
        x, w = np.polynomial.hermite.hermgauss(R.GH_NODES)
        for f in range(len(X)):
            sizes = np.exp(mean[f] + math.sqrt(2.0) * spread[f] * x)       # the prior's own nodes
            LL = R.loglik(X[f:f + 1], [0, 1, 2], mu, sd, R.SYNTH, sizes=sizes)
            want = R.log_evidence(LL, np.log(w / math.sqrt(math.pi)))
            self.assertLess(np.abs(got[f] - want[0]).max(), 1e-8)

    def test_scaled_means_are_the_table_with_its_means_scaled(self):
        X, _, keys, mu, sd = fields([0, 1, 2], 4, 35, n_fields=12)
        rule = K.ExactRule(mu, sd)
        hyp = K.hypotheses(len(LEVELS), [[0, 1, 2]])
        plain = rule.evaluate(X, hyp)["all"]["logev"]
        ones = rule.evaluate(X, hyp, factors=np.ones((len(X), len(keys))))["all"]["logev"]
        self.assertTrue(np.array_equal(plain, ones))
        fac = np.ones((len(X), len(keys)))
        fac[::2, 0] = 1.08
        got = rule.evaluate(X, hyp, factors=fac)["all"]["logev"]
        sizes, logw = R.quadrature(R.SYNTH["scale_sd"])
        scaled = R.log_evidence(R.loglik(X[::2], [0, 1, 2], mu * fac[0][:, None], sd, R.SYNTH, sizes=sizes), logw)
        self.assertLess(np.abs(got[::2] - scaled).max(), 1e-10)
        self.assertLess(np.abs(got[1::2] - plain[1::2]).max(), 1e-12)


class NamingModel(unittest.TestCase):
    def test_integrated_on_the_nodes_it_is_the_exact_rule(self):
        for offsets, missing, noise in (([0], 0.0, None), ([0, 1, 2], 0.0, None), ([0, 2, 4], 0.2, None),
                                        (list(range(9)), 0.0, None), ([0, 2, 4], 0.2, NOISE)):
            X, _, keys, mu, sd = fields(offsets, 4, 41, n_fields=30, missing=missing)
            hyp = K.hypotheses(len(LEVELS), [offsets])
            m = MD.naming(X, hyp, mu, sd, keys, noise=noise)
            got = MD.quadrature_evidence(m)
            want = K.ExactRule(mu, sd, noise=noise).evaluate(X, hyp)["all"]
            self.assertLess(np.abs(got - want["logev"]).max(), 1e-6, offsets)
            self.assertLess(np.abs(softmax(got) - want["post"]).max(), 1e-6, offsets)

    def test_the_observed_density_is_the_sum_over_hypotheses(self):
        X, _, keys, mu, sd = fields([0, 2], 4, 42, n_fields=10, missing=0.1)
        pats = [[0, 1], [0, 2]]
        hyp = K.hypotheses(len(LEVELS), pats)
        lp = np.log(np.linspace(1.0, 2.0, len(hyp)))
        lp -= np.log(np.exp(lp).sum())
        m = MD.naming(X, hyp, mu, sd, keys, log_prior=lp)
        logp = m.compile_logp(vars=[m["x"]], sum=False)
        density = lambda model_logp, t: np.asarray(model_logp({"log_s": np.full(len(X), t)})[0])

        def by_rule(sizes):
            """rule.py's log likelihood of every hypothesis at every size, (fields, hypotheses, sizes)."""
            return np.concatenate([R.loglik(X, p, mu, sd, R.SYNTH, sizes=sizes).sum(2) for p in pats], axis=1)

        for t in (-0.1, 0.0, 0.07):
            want = R.logsumexp(by_rule(np.array([math.exp(t)]))[:, :, 0] + lp, axis=1)
            self.assertLess(np.abs(density(logp, t) - want).max(), 1e-9)
        # at every one of rule.py's nodes, where quadrature_evidence integrates, and integrated
        # over log s on them, the observed density is rule.py's evidence summed over the hypotheses
        sizes, logw = R.quadrature(R.SYNTH["scale_sd"])
        at_nodes = np.stack([density(logp, t) for t in np.log(sizes)], axis=1)
        self.assertLess(np.abs(at_nodes - R.logsumexp(by_rule(sizes) + lp[None, :, None], axis=1)).max(), 1e-9)
        got = R.logsumexp(at_nodes + logw, axis=1)
        want = R.logsumexp(R.logsumexp(by_rule(sizes) + logw, axis=2) + lp, axis=1)
        self.assertLess(np.abs(got - want).max(), 1e-9)
        # a prior given with any other sum is normalised, so the density stays a density, and
        # so is one set later in the model's data
        import pymc as pm
        shifted = MD.naming(X, hyp, mu, sd, keys, log_prior=lp + 3.0)
        other = shifted.compile_logp(vars=[shifted["x"]], sum=False)
        self.assertLess(np.abs(density(other, 0.0) - density(logp, 0.0)).max(), 1e-12)
        with shifted:
            pm.set_data({"log_prior": lp - 5.0})
        self.assertLess(np.abs(density(other, 0.0) - density(logp, 0.0)).max(), 1e-12)

    def test_nuts_gives_the_exact_posterior_within_monte_carlo_error(self):
        # The bounds are set so that a correct sampler crosses them in fewer than one run in a
        # thousand, by what 24 other seeds of the sampler measured (schwingcheck/README.md, The
        # naming model): the errors are right there, but the largest of 130 distances is the tail
        # of the tail, and four errors failed one of those runs; with R-hat below 1.01 and the
        # gapped fields' mean square z taken alone, the old bounds failed about one run in fifteen
        import arviz as az
        z = []
        for offsets, n_fields, missing in (([0], 24, 0.0), ([0, 2, 4], 12, 0.2)):
            X, _, keys, mu, sd = fields(offsets, 6, 43, n_fields=n_fields, missing=missing)
            hyp = K.hypotheses(len(LEVELS), [offsets])
            m = MD.naming(X, hyp, mu, sd, keys)
            idata = MD.sample(m, draws=1500, tune=1000, chains=4, seed=44)
            post, se = MD.hypothesis_posterior(m, idata)
            want = K.ExactRule(mu, sd).evaluate(X, hyp)["all"]["post"]
            lead = want > 0.05
            # every place above 0.05 within five of its own errors; the far tail, carried by the
            # few draws that reach the sizes it needs, runs low and is held to 1e-3 besides
            self.assertTrue(np.all(np.abs(post - want)[lead] <= 5.0 * se[lead]), np.abs(post - want)[lead].max())
            self.assertTrue(np.all(np.abs(post - want) <= 5.0 * se + 1e-3), np.abs(post - want).max())
            self.assertLess(float(r_hat(idata).max()), 1.02)
            # the errors themselves, where they can be trusted: by batch means, within 0.6 to 1.6
            # of ArviZ's error of the same draws, which it computes from their effective sample size
            theirs = np.asarray(az.mcse(per_draw(m, idata), method="mean"))
            ratio = se[lead] / theirs[lead]
            self.assertTrue(np.all((ratio > 0.6) & (ratio < 1.6)), (ratio.min(), ratio.max()))
            z.append((post - want)[lead] / se[lead])
        # and as large as the distances from the exact posterior: a mean square z of 1 over both
        # kinds of field, some 40 independent terms, which an error doubled or halved cannot give
        z2 = float(np.mean(np.concatenate(z) ** 2))
        self.assertTrue(0.4 < z2 < 2.5, z2)

    def test_the_posterior_and_its_error_come_from_the_same_draws(self):
        import arviz as az
        X, _, keys, mu, sd = fields([0, 1], 2, 47, n_fields=3)
        m = MD.naming(X, K.hypotheses(len(LEVELS), [[0, 1]]), mu, sd, keys)
        draws = np.random.default_rng(48).normal(0.0, 0.07, size=(2, 47, len(X)))
        post, se = MD.hypothesis_posterior(m, az.from_dict({"posterior": {"log_s": draws}}))
        # 47 draws a chain fill 20 batches of 2, and the 7 left over count in neither the mean
        # nor the error; p(h | x, s) here is rule.py's, each field at its own size
        fi = np.arange(len(X))
        per = np.array([[R.posterior(R.loglik(X, [0, 1], mu, sd, R.SYNTH, sizes=np.exp(draws[c, d])).sum(2)[fi, :, fi])
                         for d in range(40)] for c in range(2)])
        batches = per.reshape(2, 20, 2, len(X), -1).mean(axis=2).reshape(40, len(X), -1)
        self.assertLess(np.abs(post - per.mean(axis=(0, 1))).max(), 1e-10)
        self.assertLess(np.abs(se - batches.std(axis=0, ddof=1) / math.sqrt(40)).max(), 1e-10)
        with self.assertRaises(ValueError):
            MD.hypothesis_posterior(m, az.from_dict({"posterior": {"log_s": draws[:, :19]}}))

    def test_its_prior_draws_have_the_fields_shape(self):
        X, _, keys, mu, sd = fields([0, 1, 2], 2, 45, n_fields=5, missing=0.3)
        m = MD.naming(X, K.hypotheses(len(LEVELS), [[0, 1, 2]]), mu, sd, keys)
        import pymc as pm
        x = pm.draw(m["x"], random_seed=46)
        self.assertEqual(x.shape, X.shape)
        self.assertTrue(np.all(x[~np.isfinite(X)] == 0.0))
        self.assertTrue(np.all(x[np.isfinite(X)] > 0.0))


def r_hat(idata):
    import arviz as az
    return np.asarray(az.summary(idata, kind="diagnostics")["r_hat"], float)


def per_draw(m, idata):
    """p(h | x, s) at every draw of log s, (chains, draws, fields, hypotheses)."""
    fn = MD._of_log_s(m, m.schwingcheck["hypothesis_loglik"])
    lp = np.asarray(m["log_prior"].get_value(), float)
    draws = np.asarray(idata.posterior["log_s"].values)
    return np.array([[softmax(fn(t) + lp) for t in chain] for chain in draws])


class Covariates(unittest.TestCase):
    def test_the_reference_is_panjabis_twelve_specimens(self):
        self.assertAlmostEqual(CV.HEIGHT_REF, 167.75)
        self.assertAlmostEqual(CV.REFERENCE["weight_kg"][0], 67.8333, places=4)
        self.assertAlmostEqual(CV.REFERENCE["age_years"][0], 46.3333, places=4)
        self.assertAlmostEqual(CV.REFERENCE["male"][0], 8 / 12)
        self.assertEqual(len(CV.from_specimens()), 12)

    def test_nothing_known_is_the_archives_size_prior_and_table(self):
        cm = CV.CovariateModel()
        mean, sd = cm.size_prior(CV.unknown(3))
        self.assertTrue(np.array_equal(mean, np.zeros(3)))
        self.assertTrue(np.array_equal(sd, np.full(3, 0.07)))
        self.assertTrue(np.array_equal(cm.mean_factors(CV.unknown(3), MS.SPINEPS_7), np.ones((3, 7))))
        self.assertTrue(cm.hooks_off)

    def test_a_known_height_moves_the_model_as_it_moves_the_compiled_rule(self):
        X, _, keys, mu, sd = fields([0, 1, 2], 4, 51, n_fields=8)
        hyp = K.hypotheses(len(LEVELS), [[0, 1, 2]])
        covs = [CV.Covariates(height_cm=h, sex=s) for h, s in zip(np.linspace(157, 185, 8), "MFMFMFMF")]
        covs[4] = CV.Covariates()                                   # one patient of whom nothing is known
        cm = CV.CovariateModel(sex_size=0.03)
        m = MD.naming(X, hyp, mu, sd, keys, covs=covs, cm=cm)
        got = MD.quadrature_evidence(m)
        rule = K.ExactRule(mu, sd)
        mean, spread = cm.size_prior(covs)
        want = rule.evaluate(X, hyp, logw=K.size_log_weights(np.log(rule.sizes), rule.logw, 0.07, mean, spread))["all"]
        self.assertLess(np.abs(got - want["logev"]).max(), 1e-6)
        plain = rule.evaluate(X, hyp)["all"]["logev"]
        self.assertGreater(np.abs(want["logev"] - plain).max(), 1e-3)
        self.assertEqual((mean[4], spread[4]), (0.0, 0.07))
        self.assertLess(np.abs(got[4] - plain[4]).max(), 1e-6)

    def test_a_weight_or_age_hook_moves_the_model_as_it_moves_the_compiled_rule(self):
        X, _, keys, mu, sd = fields([0, 1, 2], 4, 52, n_fields=8)
        hyp = K.hypotheses(len(LEVELS), [[0, 1, 2]])
        covs = [CV.Covariates(weight_kg=w, age_years=a) for w, a in zip(np.linspace(50, 95, 8), np.linspace(20, 80, 8))]
        cm = CV.CovariateModel(weight_effects={keys[0]: 0.04}, age_effects={keys[4]: -0.03})
        m = MD.naming(X, hyp, mu, sd, keys, covs=covs, cm=cm)
        got = MD.quadrature_evidence(m)
        want = K.ExactRule(mu, sd).evaluate(X, hyp, factors=cm.mean_factors(covs, keys))["all"]["logev"]
        self.assertLess(np.abs(got - want).max(), 1e-6)
        at_zero = MD.quadrature_evidence(MD.naming(X, hyp, mu, sd, keys, covs=covs))
        self.assertLess(np.abs(at_zero - K.ExactRule(mu, sd).evaluate(X, hyp)["all"]["logev"]).max(), 1e-6)


class FixedLevel(unittest.TestCase):
    def test_nuts_gives_the_closed_form_size_posterior(self):
        offsets = [0, 1, 2]
        X, truth, keys, mu, sd = fields(offsets, 3, 61, n_fields=8)
        X[0, 3, 1] = np.nan
        m = MD.fixed_level(X, truth[:, None] + np.array(offsets)[None, :], mu, sd, keys, noise=NOISE)
        idata = MD.sample(m, draws=1000, tune=1000, chains=4, seed=62, var_names=["log_s", "offset", "beta_height"])
        import arviz as az
        s = az.summary(idata, var_names=["log_s"])
        grid = np.linspace(-0.5, 0.5, 4001)
        LL = R.loglik(X, offsets, mu, sd, R.SYNTH, sizes=np.exp(grid), noise=NOISE)
        lj = LL[np.arange(len(X)), truth].sum(1) - 0.5 * (grid / R.SYNTH["scale_sd"]) ** 2
        p = np.exp(lj - lj.max(1, keepdims=True))
        p /= p.sum(1, keepdims=True)
        mean = (p * grid).sum(1)
        spread = np.sqrt((p * (grid[None] - mean[:, None]) ** 2).sum(1))
        draws = idata.posterior["log_s"]
        z_mean = (draws.mean(("chain", "draw")).values - mean) / np.asarray(s["mcse_mean"], float)
        z_sd = (draws.std(("chain", "draw")).values - spread) / np.asarray(s["mcse_sd"], float)
        self.assertLess(np.abs(z_mean).max(), 4.0)
        self.assertLess(np.abs(z_sd).max(), 4.0)
        self.assertLess(float(np.asarray(s["r_hat"], float).max()), 1.01)


class Generator(unittest.TestCase):
    N = 6 * 1000

    def _pair(self, r_between=0.0, noise=None):
        ref, keys, _, _ = seven()
        a = MD.draw(MD.generator(ref, keys, C.PHENOTYPES, self.N, r_between=r_between, noise=noise), seed=71)
        b = C.draw_columns(ref, C.PHENOTYPES, 72, self.N, keys, r_between=r_between,
                           noise_mm=C.SYNTH["noise_mm"] if noise is None else noise)
        return a, b

    def test_the_layout_is_the_numpy_generators(self):
        a, b = self._pair()
        self.assertEqual(a.levels, b.levels)
        self.assertEqual(a.phenotype, b.phenotype)
        self.assertEqual(a.transitional_at, b.transitional_at)
        self.assertTrue(np.array_equal(np.isfinite(a.values), np.isfinite(b.values)))
        self.assertGreaterEqual(np.nanmin(a.values), C.FLOOR)
        ref, keys, _, _ = seven()
        for n in (1, 2):                    # fewer columns than phenotypes: padded to the widest listed
            short = MD.draw(MD.generator(ref, keys, C.PHENOTYPES, n), seed=73)
            self.assertEqual(short.values.shape, C.draw_columns(ref, C.PHENOTYPES, 74, n, keys).values.shape)

    def _z_scores(self, a, b):
        """Two-sample z scores of every mean, SD and correlation, phenotype by phenotype."""
        zs = []
        for p in C.PHENOTYPES:
            rows = [i for i, q in enumerate(a.phenotype) if q == p]
            W = len(a.levels[rows[0]])
            u, v = a.values[rows, :W], b.values[rows, :W]
            n = len(rows)
            zs.append(((u.mean(0) - v.mean(0)) / np.sqrt((u.var(0, ddof=1) + v.var(0, ddof=1)) / n)).ravel())
            zs.append((np.log(u.std(0, ddof=1) / v.std(0, ddof=1)) / math.sqrt(1.0 / (n - 1))).ravel())
            fisher = lambda r: np.arctanh(np.clip(r, -0.999999, 0.999999))
            adj = lambda w: np.array([[np.corrcoef(w[:, i, m], w[:, i + 1, m])[0, 1] for m in range(w.shape[2])] for i in range(W - 1)])
            zs.append(((fisher(adj(u)) - fisher(adj(v))) / math.sqrt(2.0 / (n - 3))).ravel())
            iu = np.triu_indices(u.shape[2], 1)
            within = lambda w: np.array([np.corrcoef(w[:, i, :].T)[iu] for i in range(W)])
            zs.append(((fisher(within(u)) - fisher(within(v))) / math.sqrt(2.0 / (n - 3))).ravel())
            la, lb = np.log(a.scale[rows]), np.log(b.scale[rows])
            zs.append(np.array([(la.mean() - lb.mean()) / math.sqrt((la.var() + lb.var()) / n),
                                np.log(la.std() / lb.std()) / math.sqrt(1.0 / (n - 1))]))
        return np.concatenate(zs)

    def test_columns_match_the_numpy_generator_in_distribution(self):
        z = self._z_scores(*self._pair())
        self.assertGreater(len(z), 5000)
        self.assertLess(np.abs(z).max(), 4.8)                     # Bonferroni over the z scores at 1 per cent
        self.assertLess(abs(float(np.mean(z * z)) - 1.0), 0.15)

    def test_correlated_offsets_and_each_measures_own_error_match_too(self):
        z = self._z_scores(*self._pair(r_between=0.3, noise=NOISE))
        self.assertLess(np.abs(z).max(), 4.8)
        self.assertLess(abs(float(np.mean(z * z)) - 1.0), 0.15)


class Graphs(unittest.TestCase):
    def test_the_committed_graphs_are_the_models_graphs(self):
        self.assertEqual(MD.check_graphs(), [])

    def test_the_readme_draws_every_committed_graph(self):
        with open(os.path.join(ROOT, "schwingcheck", "README.md"), encoding="utf-8") as fh:
            readme = fh.read()
        for name in ("naming", "fixed_level", "generator"):
            with open(MD.graph_path(name), encoding="ascii") as fh:
                self.assertIn("```mermaid\n" + fh.read() + "```", readme, name)


if __name__ == "__main__":
    unittest.main()

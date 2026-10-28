"""The chain of levels (chain.py) and its two PyMC models (chain_pymc.py), each claim checked
against something outside the code it tests.

    python -m unittest discover -s tests -v          # from the repository's root, in the PyMC venv

The chain's start and rows are laws, block diagonal by type, and its support paths are every path
of positive probability, summing to one; with one step and the typical type alone its prior is
step d's, every place that fits equally likely, and its posterior is rule.name's within 1e-12;
with uniform steps every fitting (pattern, place) pair is equally likely, counted by brute force;
the forward-backward algorithm equals enumeration; the extended table is the generator's to the
bit. Model (b)'s log density is a dense normal computed by scipy, summed over the chain's paths,
within 1e-10, and model (a)'s is the enumeration of its emissions given the offsets, with a
finite gradient; recover() through (b) draws each body's level as often as (b)'s posterior says.
"""
from __future__ import annotations

import itertools
import os
import sys
import unittest
import warnings

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from schwingcheck import LEVELS                                   # noqa: E402
from schwingcheck import chain as CH                              # noqa: E402
from schwingcheck import columns as C                             # noqa: E402
from schwingcheck import measures as MS                           # noqa: E402
from schwingcheck import rule as R                                # noqa: E402


def seven():
    """The seven SPINEPS measures' table, extended, with their errors and powers."""
    ms = MS.select(MS.SPINEPS_7)
    mu, sd = MS.arrays(ms)
    mu_e, sd_e = CH.extended_table(mu, sd)
    return ms, mu, sd, mu_e, sd_e, MS.errors(ms), MS.powers(ms)


def fields(n_bodies, per_column, seed=5, types=CH.TYPES):
    ms, _, _, _, _, noise, power = seven()
    ref, keys = MS.reference(ms), [MS.archive_key(m) for m in ms]
    cols = C.draw_columns(ref, list(types), 97, 2, keys, noise_mm=noise, power=power)
    return CH.draw_fields(cols, CH.step_law(), n_bodies, per_column, seed)


class TheChain(unittest.TestCase):
    def test_laws_and_blocks(self):
        for B in (1, 3, 5):
            ch = CH.build(CH.TYPES, None, CH.step_law(), B)
            self.assertAlmostEqual(ch.init.sum(), 1.0, places=12)
            np.testing.assert_allclose(ch.P.sum(-1), 1.0, atol=1e-12)
            other = ch.state_type[:, None] != ch.state_type[None, :]
            self.assertTrue(np.all(ch.P[:, other] == 0))
            for ti, w in enumerate(ch.weights):
                self.assertAlmostEqual(ch.init[ch.state_type == ti].sum(), w, places=12)

    def test_support_paths_are_every_positive_path(self):
        ch = CH.build(CH.TYPES, None, CH.step_law(), 3)
        sp = CH.support_paths(ch.init, ch.P)
        brute = [p for p in itertools.product(range(ch.n_states), repeat=3)
                 if ch.init[p[0]] * ch.P[0, p[0], p[1]] * ch.P[1, p[1], p[2]] > 0]
        self.assertEqual(sorted(map(tuple, sp)), sorted(brute))
        self.assertAlmostEqual(np.exp(CH.path_log_prior(ch.init, ch.P, sp)).sum(), 1.0, places=12)
        pa = CH.paths_of(ch)
        self.assertAlmostEqual(np.exp(pa.log_prior).sum(), 1.0, places=12)
        np.testing.assert_allclose(pa.type_mass.sum(1), 1.0, atol=1e-12)

    def test_one_step_typical_is_step_d(self):
        B = 3
        ch = CH.build(("typical",), (1.0,), (1.0,), B)
        pa = CH.paths_of(ch)
        self.assertEqual(len(pa), len(LEVELS) - B + 1)
        np.testing.assert_allclose(pa.log_prior, -np.log(len(pa)), atol=1e-12)
        X, _, _, _ = fields(B, 2, types=("typical",))
        _, mu, sd, mu_e, sd_e, noise, power = seven()
        nodes = R.trapezoid(R.SYNTH["scale_sd"])
        subsets = {"all": list(range(X.shape[1]))}
        ev = CH.path_logev(X, pa, ch, mu_e, sd_e, subsets, noise, power, nodes)["all"]
        got = CH.body_posterior(CH.posterior(ev, pa.log_prior), pa.names, 0)
        ref = R.name(X, (0, 1, 2), mu, sd, R.SYNTH, subsets=subsets, noise=noise, power=power, nodes=nodes)["all"]
        np.testing.assert_allclose(got[:, :ref.shape[1]], ref, atol=1e-12)

    def test_uniform_steps_is_item_4c(self):
        B, K = 3, 2
        pa = CH.paths_of(CH.build(("typical",), (1.0,), CH.uniform_steps(K), B))
        pairs = {tuple(p + np.cumsum((0,) + ks)) for ks in itertools.product(range(1, K + 1), repeat=B - 1)
                 for p in range(len(LEVELS)) if p + sum(ks) < len(LEVELS)}
        self.assertEqual(len(pa), len(pairs))
        np.testing.assert_allclose(pa.log_prior, -np.log(len(pairs)), atol=1e-12)

    def test_forward_backward_is_enumeration(self):
        ch = CH.build(CH.TYPES, None, CH.step_law(), 4)
        le = np.random.default_rng(1).normal(size=(2, 4, ch.n_states)) * 3
        marg, logev = CH.forward_backward(le, ch.init, ch.P)
        sp = CH.support_paths(ch.init, ch.P)
        tot = CH.path_log_prior(ch.init, ch.P, sp)[None] + np.stack([le[f][np.arange(4)[:, None], sp.T].sum(0) for f in range(2)])
        np.testing.assert_allclose(logev, np.logaddexp.reduce(tot, 1), atol=1e-10)
        pp = np.exp(tot - logev[:, None])
        want = np.zeros_like(marg)
        for f, t in itertools.product(range(2), range(4)):
            np.add.at(want[f, t], sp[:, t], pp[f])
        np.testing.assert_allclose(marg, want, atol=1e-10)

    def test_extended_table_is_the_generators(self):
        ms, _, _, mu_e, sd_e, _, _ = seven()
        ref, keys = MS.reference(ms), [MS.archive_key(m) for m in ms]
        for phenotype, name in (("six_lumbar", "L6"), ("t13", "T13")):
            levels, _, pmu, psd = C.profiles(ref, keys, phenotype, C.SYNTH["blend"])
            j = levels.index(name)
            self.assertTrue(np.array_equal(pmu[:, j], mu_e[:, CH.NAME_INDEX[name]]))
            self.assertTrue(np.array_equal(psd[:, j], sd_e[:, CH.NAME_INDEX[name]]))


class TheModels(unittest.TestCase):
    """The PyMC models on five fields of three bodies over the three types."""

    @classmethod
    def setUpClass(cls):
        warnings.filterwarnings("ignore")
        from schwingcheck import chain_pymc as CP
        cls.CP = CP
        _, _, _, cls.mu_e, cls.sd_e, cls.noise, cls.power = seven()
        cls.chain = CH.build(CH.TYPES, None, CH.step_law(), 3)
        cls.paths = CH.paths_of(cls.chain)
        cls.X = fields(3, 3)[0][:5]
        rng = np.random.default_rng(3)
        cls.log_s = rng.normal(0, R.SYNTH["scale_sd"], len(cls.X))
        cls.z = rng.normal(size=cls.X.shape[:2])

    def dense(self, x, names, log_s):
        rho, out = R.SYNTH["rho"], 0.0
        for m in range(x.shape[0]):
            s = np.exp(self.power[m] * log_s)
            sd = self.sd_e[m, names]
            cov = s * s * (rho * rho * np.outer(sd, sd) + (1 - rho * rho) * np.diag(sd * sd)) + self.noise[m] ** 2 * np.eye(len(names))
            out += stats.multivariate_normal(s * self.mu_e[m, names], cov).logpdf(x[m])
        return out

    def test_enumerated_is_a_dense_normal_over_the_paths(self):
        model = self.CP.enumerated(self.X, self.chain, self.mu_e, self.sd_e, self.noise, self.power)
        got = model.compile_logp()({"log_s": self.log_s})
        want = sum(np.logaddexp.reduce(self.paths.log_prior + [self.dense(self.X[f], n, self.log_s[f]) for n in self.paths.names])
                   for f in range(len(self.X))) + stats.norm(0, R.SYNTH["scale_sd"]).logpdf(self.log_s).sum()
        self.assertLess(abs(got - want), 1e-10)

    def test_sampled_is_its_enumeration_with_a_finite_gradient(self):
        model = self.CP.sampled(self.X, self.chain, self.mu_e, self.sd_e, self.noise, self.power)
        point = {"log_s": self.log_s, "z": self.z}
        le = CH.state_loglik(self.X, self.chain, self.mu_e, self.sd_e, self.log_s[None], self.z[None],
                             R.SYNTH["rho"], self.noise, self.power)[0]
        sp = CH.support_paths(self.chain.init, self.chain.P)
        lp = CH.path_log_prior(self.chain.init, self.chain.P, sp)
        want = sum(np.logaddexp.reduce(lp + le[f][np.arange(3)[:, None], sp.T].sum(0)) for f in range(len(self.X)))
        want += stats.norm(0, R.SYNTH["scale_sd"]).logpdf(self.log_s).sum() + stats.norm().logpdf(self.z).sum()
        self.assertLess(abs(model.compile_logp()(point) - want), 1e-10)
        self.assertTrue(np.all(np.isfinite(model.compile_dlogp()(point))))

    def test_recover_draws_levels_as_the_posterior_says(self):
        import pymc as pm
        from pymc_extras.marginal import recover
        model = self.CP.enumerated(self.X, self.chain, self.mu_e, self.sd_e, self.noise, self.power)
        with model:
            idata = pm.sample(draws=500, tune=500, chains=2, cores=1, random_seed=11, progressbar=False,
                              compute_convergence_checks=False)
        want, _ = self.CP.body_posterior_enumerated(idata, self.X, self.paths, self.mu_e, self.sd_e, self.noise, self.power, 1)
        state = np.asarray(recover(idata, model=model, var_names=["state"], random_seed=5).posterior["state"].values)
        names = self.chain.state_name[state[..., 1]]
        got = np.stack([(names == k).mean((0, 1)) for k in range(len(CH.NAMES))], -1)
        self.assertLess(np.abs(got - want).max(), 5 * 0.5 / np.sqrt(names.shape[0] * names.shape[1]))


if __name__ == "__main__":
    unittest.main()

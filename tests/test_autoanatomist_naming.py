"""The naming layer of autoanatomist/ (naming.py) held to schwingcheck's chain and rule in float64.

    python -m unittest discover -s tests -v          # from the repository's root, in the venv

Built over chain.py's three types, the layer's chain is chain.build's to the bit; its exact log
evidence of every name path is chain.path_logev's within 1e-9, with each measure's error and with
the same errors given value by value, on fields with a value not read, at 1, 3 and 4 bodies; its
path and body posteriors are chain.py's; the forward pass at gamma 1 is chain.forward_backward's
log evidence and marginals, and towards gamma 0 the best path of the enumeration, its value and
its gradient; the emissions given the size and the offsets are chain.state_loglik's; at rho 0 the
forward pass on every node of the size, summed over them, is the enumeration's answer at rho 0;
with the typical type alone and one step it is rule.name's posterior. With four types the priors
sum to one and keep each type's weight, the bottom anchor ends every path on L4, L5 or L6 and the
top anchor starts every path at C3; and the loss's gradient in the measurements is a finite
difference's. In float32, as train.py runs it: the loss far from the table, where every true
name's posterior is below the type's smallest number, is float64's with a gradient that is
float64's at every body; the forward pass at a gamma of 1e-10 is finite and is the Viterbi path;
and whatever a per-value noise holds at a value not read changes nothing.
"""
from __future__ import annotations

import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from schwingcheck import chain as CH                              # noqa: E402
from schwingcheck import columns as C                             # noqa: E402
from schwingcheck import measures as MS                           # noqa: E402
from schwingcheck import rule as R                                # noqa: E402

try:
    import jax
    import jax.numpy as jnp
    HAVE_JAX = True
except ImportError:                                               # pragma: no cover
    HAVE_JAX = False


def seven():
    ms = MS.select(MS.SPINEPS_7)
    mu, sd = MS.arrays(ms)
    mu_e, sd_e = CH.extended_table(mu, sd)
    return ms, mu, sd, mu_e, sd_e, MS.errors(ms), MS.powers(ms)


def fields(n_bodies, per_column, seed=5, types=CH.TYPES, n_columns=3):
    ms, _, _, _, _, noise, power = seven()
    ref, keys = MS.reference(ms), [MS.archive_key(m) for m in ms]
    cols = C.draw_columns(ref, list(types), 97, n_columns, keys, noise_mm=noise, power=power)
    return CH.draw_fields(cols, CH.step_law(), n_bodies, per_column, seed)


@unittest.skipUnless(HAVE_JAX, "jax is not installed")
class AgainstTheChain(unittest.TestCase):
    def test_the_exact_answer(self):
        from autoanatomist import naming as N
        ms, mu, sd, mu_e, sd_e, noise, power = seven()
        nodes = R.trapezoid(R.SYNTH["scale_sd"])
        with jax.enable_x64(True):
            for B in (1, 3, 4):
                ch = CH.build(CH.TYPES, None, CH.step_law(), B)
                mine = N.build(CH.TYPES, None, CH.step_law(), B)
                np.testing.assert_array_equal(mine.init, ch.init)
                np.testing.assert_array_equal(mine.P, ch.P)
                pa = N.paths_of(mine)
                X, _, _, _ = fields(B, 2, seed=B)
                X = X.copy()
                X[0, 1, 0] = np.nan
                ref = CH.path_logev(X, pa, ch, mu_e, sd_e, {"all": list(range(7))}, noise, power, nodes)["all"]
                got = np.asarray(N.path_logev(jnp.asarray(X), pa.names, mu_e, sd_e, noise, power, nodes))
                np.testing.assert_allclose(got, ref, atol=1e-9, rtol=0)
                each = np.broadcast_to(noise[None, :, None], X.shape)
                got_each = np.asarray(N.path_logev(jnp.asarray(X), pa.names, mu_e, sd_e, each, power, nodes))
                np.testing.assert_allclose(got_each, ref, atol=1e-9, rtol=0)
                post_ref = CH.posterior(ref, pa.log_prior)
                post = np.exp(np.asarray(jax.nn.log_softmax(got + pa.log_prior[None], -1)))
                np.testing.assert_allclose(post, post_ref, atol=1e-9)
                body = np.asarray(N.body_posterior(jnp.asarray(post), pa.names))
                for t in range(B):
                    np.testing.assert_allclose(body[:, t], CH.body_posterior(post_ref, pa.names, t), atol=1e-9)

    def test_the_forward_pass(self):
        from autoanatomist import naming as N
        with jax.enable_x64(True):
            for B in (1, 3, 4):
                ch = N.build(CH.TYPES, None, CH.step_law(), B)
                le = np.random.default_rng(1).normal(size=(2, B, ch.n_states)) * 3
                marg, logev = CH.forward_backward(le, ch.init, ch.P)
                li, lP = N.log_laws(ch)
                v, m = N.soft_marginals(jnp.asarray(le), li, lP, 1.0)
                np.testing.assert_allclose(np.asarray(v), logev, atol=1e-10)
                np.testing.assert_allclose(np.asarray(m), marg, atol=1e-10)
                sp = CH.support_paths(ch.init, ch.P)
                score = CH.path_log_prior(ch.init, ch.P, sp)[None] + np.stack(
                    [le[f][np.arange(B)[:, None], sp.T].sum(0) for f in range(2)])
                best = np.zeros_like(marg)
                for f in range(2):
                    best[f, np.arange(B), sp[score[f].argmax()]] = 1.0
                v0, m0 = N.soft_marginals(jnp.asarray(le), li, lP, 1e-4)
                np.testing.assert_allclose(np.asarray(v0), score.max(1), atol=1e-3)
                np.testing.assert_allclose(np.asarray(m0), best, atol=1e-6)

    def test_the_emissions_and_rho_zero(self):
        from autoanatomist import naming as N
        _, _, _, mu_e, sd_e, noise, power = seven()
        nodes = R.trapezoid(R.SYNTH["scale_sd"])
        with jax.enable_x64(True):
            B = 3
            ch = N.build(CH.TYPES, None, CH.step_law(), B)
            pa = N.paths_of(ch)
            X, _, _, _ = fields(B, 2, seed=7)
            rng = np.random.default_rng(3)
            log_s = rng.normal(size=(2, len(X))) * 0.07
            z = rng.normal(size=(2, len(X), 7))
            ref = CH.state_loglik(X, ch, mu_e, sd_e, log_s, z, 0.5, noise, power)
            got = np.asarray(N.state_loglik(jnp.asarray(X), ch.state_name, mu_e, sd_e, log_s, z, 0.5, noise, power))
            np.testing.assert_allclose(got, ref, atol=1e-9)
            ev0 = np.asarray(N.path_logev(jnp.asarray(X), pa.names, mu_e, sd_e, noise, power, nodes, rho=0.0))
            whole = np.logaddexp.reduce(ev0 + pa.log_prior[None], axis=1)
            value, marg = N.forward_logev(jnp.asarray(X), ch, mu_e, sd_e, noise, power, nodes)
            np.testing.assert_allclose(np.asarray(value), whole, atol=1e-9)
            body = np.asarray(N.body_posterior(jnp.asarray(np.exp(ev0 + pa.log_prior[None] - whole[:, None])), pa.names))
            np.testing.assert_allclose(np.asarray(N.state_names(marg, ch.state_name)), body, atol=1e-9)

    def test_one_step_typical_is_the_rule(self):
        from autoanatomist import naming as N
        _, mu, sd, mu_e, sd_e, noise, power = seven()
        nodes = R.trapezoid(R.SYNTH["scale_sd"])
        with jax.enable_x64(True):
            ch = N.build(("typical",), (1.0,), (1.0,), 3)
            pa = N.paths_of(ch)
            X, _, _, _ = fields(3, 2, types=("typical",), n_columns=2)
            ev = N.path_logev(jnp.asarray(X), pa.names, mu_e, sd_e, noise, power, nodes)
            post = jnp.exp(jax.nn.log_softmax(ev + pa.log_prior[None], -1))
            got = np.asarray(N.body_posterior(post, pa.names))[:, 0]
            ref = R.name(X, (0, 1, 2), mu, sd, R.SYNTH, subsets={"all": list(range(7))}, noise=noise, power=power,
                         nodes=nodes)["all"]
            np.testing.assert_allclose(got[:, :ref.shape[1]], ref, atol=1e-12)


@unittest.skipUnless(HAVE_JAX, "jax is not installed")
class FourTypesAndAnchors(unittest.TestCase):
    def test_priors_and_anchors(self):
        from autoanatomist import naming as N
        w = np.array([N.WEIGHTS[t] for t in N.TYPES])
        for top, bottom in ((False, False), (False, True), (True, False)):
            ch = N.build(N.TYPES, None, CH.step_law(), 4, top, bottom)
            pa = N.paths_of(ch)
            self.assertAlmostEqual(float(np.exp(pa.log_prior).sum()), 1.0, places=12)
            for i in range(len(N.TYPES)):
                self.assertAlmostEqual(float(ch.init[ch.state_type == i].sum()), w[i] / w.sum(), places=12)
            ends = {N.NAMES[n] for n in pa.names[:, -1]}
            starts = {N.NAMES[n] for n in pa.names[:, 0]}
            if bottom:
                self.assertEqual(ends, {"L4", "L5", "L6"})
            if top:
                self.assertEqual(starts, {"C3"})
        with self.assertRaises(ValueError):
            N.build(("typical",), None, (1.0,), 3, top=True, bottom=True)

    def test_the_loss_gradient(self):
        from autoanatomist import naming as N
        with jax.enable_x64(True):
            nm = N.prepare(n_bodies=3)
            X, names, _, _ = fields(3, 1, seed=9)
            X = jnp.asarray(X)
            loss = lambda X: N.body_loss(nm, X, names)
            g = jax.grad(loss)(X)
            v = jnp.asarray(np.random.default_rng(2).standard_normal(X.shape))
            h = 1e-6
            fd = (loss(X + h * v) - loss(X - h * v)) / (2 * h)
            self.assertTrue(bool(jnp.isfinite(g).all()))
            self.assertLess(abs(float(jnp.sum(g * v)) - float(fd)), 1e-6 * abs(float(fd)) + 1e-9)
            out = N.posteriors(nm, X)
            np.testing.assert_allclose(np.asarray(out["body"]).sum(-1), 1.0, atol=1e-12)
            np.testing.assert_allclose(np.asarray(out["type"]).sum(-1), 1.0, atol=1e-12)
            np.testing.assert_allclose(np.asarray(out["body"]), np.asarray(N.body_posterior(
                jnp.exp(out["log_path"]), nm.paths.names)), atol=1e-12)


@unittest.skipUnless(HAVE_JAX, "jax is not installed")
class InFloat32(unittest.TestCase):
    def test_the_loss_far_from_the_table(self):
        from autoanatomist import naming as N
        X, names, _, _ = fields(3, 1, seed=9)
        zero = np.zeros(np.shape(X))
        nm = N.prepare(n_bodies=3)
        loss32, g32 = jax.value_and_grad(lambda X: N.body_loss(nm, X, names))(jnp.asarray(zero, jnp.float32))
        at_truth32 = N.body_loss(nm, jnp.asarray(X, jnp.float32), names)
        with jax.enable_x64(True):
            nm64 = N.prepare(n_bodies=3)
            loss64, g64 = jax.value_and_grad(lambda X: N.body_loss(nm64, X, names))(jnp.asarray(zero, jnp.float64))
            at_truth64 = N.body_loss(nm64, jnp.asarray(X, jnp.float64), names)
        self.assertGreater(float(loss64), 100.0)
        self.assertAlmostEqual(float(loss32), float(loss64), delta=1e-4 * float(loss64))
        self.assertAlmostEqual(float(at_truth32), float(at_truth64), delta=1e-4 * float(at_truth64))
        np.testing.assert_allclose(np.asarray(g32), np.asarray(g64), atol=1e-4)
        self.assertTrue(bool((np.abs(np.asarray(g32)).sum(1) > 0).all()))

    def test_the_forward_pass_at_a_tiny_gamma(self):
        from autoanatomist import naming as N
        ch = N.build(N.TYPES, None, CH.step_law(), 3)
        le = jnp.asarray(np.random.default_rng(1).normal(size=(2, 3, ch.n_states)) * 3, jnp.float32)
        li, lP = N.log_laws(ch)
        li, lP = jnp.asarray(li, jnp.float32), jnp.asarray(lP, jnp.float32)
        v4, m4 = N.soft_marginals(le, li, lP, 1e-4)
        v10, m10 = N.soft_marginals(le, li, lP, 1e-10)
        self.assertTrue(bool(jnp.isfinite(v10).all() and jnp.isfinite(m10).all()))
        np.testing.assert_allclose(np.asarray(m10).sum(-1), 1.0, atol=1e-5)
        np.testing.assert_allclose(np.asarray(m10), np.asarray(m4), atol=1e-6)
        np.testing.assert_allclose(np.asarray(v10), np.asarray(v4), atol=1e-2)

    def test_an_unread_values_noise_counts_for_nothing(self):
        from autoanatomist import naming as N
        X, names, _, _ = fields(3, 1, seed=9)
        X = np.array(X, float)
        X[0, 1, 0] = np.nan
        nm = N.prepare(n_bodies=3)
        plain = np.broadcast_to(np.asarray(nm.noise)[None, :, None], X.shape).copy()
        base = N.posteriors(nm, jnp.asarray(X, jnp.float32), jnp.asarray(plain, jnp.float32))["body"]
        for bad in (np.nan, np.inf):
            noise = plain.copy()
            noise[0, 1, 0] = bad
            got = N.posteriors(nm, jnp.asarray(X, jnp.float32), jnp.asarray(noise, jnp.float32))["body"]
            self.assertTrue(bool(jnp.isfinite(got).all()))
            np.testing.assert_array_equal(np.asarray(got), np.asarray(base))
            ch = nm.chain
            le = N.state_loglik(jnp.asarray(X, jnp.float32), ch.state_name, nm.mu_ext, nm.sd_ext,
                                jnp.zeros((2, X.shape[0]), jnp.float32), jnp.zeros((2, X.shape[0], X.shape[1]), jnp.float32),
                                0.0, jnp.asarray(noise, jnp.float32), nm.power)
            self.assertTrue(bool(jnp.isfinite(le).all()))


if __name__ == "__main__":
    unittest.main()

"""The vectorised rule is the archive's rule, and more: each claim checked against something
outside the package.

    python -m unittest discover -s tests -v          # from the repository's root, in the PyMC venv

On contiguous, complete fields of widths 1, 2, 3, 5, 9 and 22 the per-measure log likelihoods
and the posteriors equal exact.py's to 1e-10, absolutely; on gapped fields and fields with missing values the closed form equals a
dense multivariate normal computed by scipy on the bodies present; a measure missing on every
body changes no posterior; a field with no measure gets the prior back; the chunking of the
matrix product changes nothing; lengths, areas and angles, each with its own power of the size,
equal a dense normal too, every power given as 1 is no power given to the bit, and the archive's
rule to 1e-10; the trapezoid rule
is the integral where every measure of the pool knows the size closely; and the selective
guarantee holds on fresh draws.
"""
from __future__ import annotations

import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "archive", "bordercall"))

import exact as E                     # noqa: E402
import neighbour as NB                # noqa: E402
import panjabi as P                   # noqa: E402
from schwingcheck import LEVELS       # noqa: E402
from schwingcheck import columns as C  # noqa: E402
from schwingcheck import measures as MS  # noqa: E402
from schwingcheck import rule as R    # noqa: E402

MEASURES = list(E.MEASURES7)
SYNTH = dict(rho=0.5, noise_mm=1.0, scale_sd=0.07)


def archive_table():
    ref = P.load_reference(measures=MEASURES)
    return ref, E.table_arrays(ref, MEASURES)


def archive_columns(n, seed=97):
    ref, (mu, sd) = archive_table()
    cols = NB.draw_columns(ref, ["typical"], seed, n, MEASURES)
    return E.column_values(cols, MEASURES), mu, sd


class SameRule(unittest.TestCase):
    def test_contiguous_complete_fields_of_six_widths_equal_the_archive_to_1e_10(self):
        V, mu, sd = archive_columns(30)
        sizes, logw = R.quadrature(SYNTH["scale_sd"])
        for n in (1, 2, 3, 5, 9, 22):
            X, truth, grp = E.fields(V, n)
            LLa = E.field_loglik(X, mu, sd, SYNTH)
            LLb = R.loglik(X, np.arange(n), mu, sd, SYNTH)
            self.assertEqual(LLa.shape, LLb.shape)
            self.assertLess(np.abs(LLa - LLb).max(), 1e-10)          # absolute: the log likelihoods run to 6,000
            pa = E.posterior(E.log_evidence(LLa, logw))
            pb = R.posterior(R.log_evidence(LLb, logw))
            self.assertLess(np.abs(pa - pb).max(), 1e-10)
            for name, ms in E.REGIMES.items():
                idx = sorted(MEASURES.index(m) for m in ms)
                self.assertLess(np.abs(E.posterior(E.log_evidence(LLa, logw, idx)) - R.posterior(R.log_evidence(LLb, logw, idx))).max(), 1e-10)

    def test_name_equals_the_archive_whatever_the_chunk(self):
        V, mu, sd = archive_columns(20)
        X, truth, grp = E.fields(V, 4)
        _, logw = R.quadrature(SYNTH["scale_sd"])
        want = E.posterior(E.log_evidence(E.field_loglik(X, mu, sd, SYNTH), logw))
        for chunk in (7, 100, 10000):
            got = R.name(X, [0, 1, 2, 3], mu, sd, SYNTH, chunk=chunk)["all"]
            self.assertLess(np.abs(got - want).max(), 1e-10)
        for block in (1, 5, 1000):
            LL = R.loglik(X, [0, 1, 2, 3], mu, sd, SYNTH, block=block)
            self.assertLess(np.abs(R.posterior(R.log_evidence(LL, logw)) - want).max(), 1e-10)

    def test_the_quadrature_is_the_archives(self):
        for ssd in (0.0, 0.07, 0.14):
            sa, wa = E.quadrature(ssd)
            sb, wb = R.quadrature(ssd)
            self.assertTrue(np.array_equal(sa, sb) and np.array_equal(wa, wb))


class GapsAndMissing(unittest.TestCase):
    def test_gapped_fields_equal_a_dense_normal(self):
        V, mu, sd = archive_columns(6)
        sizes, _ = R.quadrature(SYNTH["scale_sd"], 7)
        for offsets in ([0, 2], [0, 1, 3], [0, 2, 4], [0, 3, 6], [0, 2, 4, 6, 8]):
            X = V[:, :, offsets]
            LL = R.loglik(X, offsets, mu, sd, SYNTH, sizes=sizes)
            dense = R.dense_loglik(X, offsets, mu, sd, SYNTH, sizes)
            self.assertEqual(LL.shape[1], len(LEVELS) - offsets[-1])
            self.assertLess(np.abs(LL - dense).max(), 1e-9)

    def test_missing_values_equal_a_dense_normal_on_the_bodies_present(self):
        V, mu, sd = archive_columns(6)
        sizes, _ = R.quadrature(SYNTH["scale_sd"], 5)
        X = V[:, :, 3:8].copy()
        X[0, 1, 2] = np.nan
        X[1, 0, :] = np.nan
        X[2, :, 1] = np.nan
        X[3, 4, [0, 4]] = np.nan
        LL = R.loglik(X, [0, 1, 2, 3, 4], mu, sd, SYNTH, sizes=sizes)
        dense = R.dense_loglik(X, [0, 1, 2, 3, 4], mu, sd, SYNTH, sizes)
        self.assertLess(np.abs(LL - dense).max(), 1e-9)
        # a measure missing on every body contributes the same constant at every place
        self.assertTrue(np.allclose(LL[1, :, 0, :], LL[1, 0:1, 0, :]))
        self.assertTrue(np.all(LL[1, :, 0, :] == 0.0))

    def test_a_field_with_nothing_gets_the_prior_back(self):
        _, (mu, sd) = archive_table()
        X = np.full((2, len(MEASURES), 3), np.nan)
        post = R.name(X, [0, 1, 2], mu, sd, SYNTH)["all"]
        self.assertTrue(np.allclose(post, 1.0 / post.shape[1]))
        prior = np.log(np.arange(1, post.shape[1] + 1, dtype=float))
        prior -= R.logsumexp(prior[None, :], 1)[0]
        post = R.name(X, [0, 1, 2], mu, sd, SYNTH, log_prior=prior)["all"]
        self.assertTrue(np.allclose(post, np.exp(prior)))

    def test_a_missing_value_is_the_marginal(self):
        """Dropping a value gives the likelihood of the other values alone: the posterior with it
        NaN equals the posterior of the field without that body when it is the last one."""
        V, mu, sd = archive_columns(10)
        X = V[:, :, 5:8].copy()
        Xn = X.copy()
        Xn[:, :, 2] = np.nan
        post_short = R.name(X[:, :, :2], [0, 1], mu, sd, SYNTH)["all"]
        post_nan = R.name(Xn, [0, 1, 2], mu, sd, SYNTH)["all"]
        # the NaN field has one place fewer than the short field at the bottom of the column
        k = post_nan.shape[1]
        short = post_short[:, :k] / post_short[:, :k].sum(1, keepdims=True)
        self.assertLess(np.abs(post_nan - short).max(), 1e-10)

    def test_offsets_are_checked(self):
        _, (mu, sd) = archive_table()
        with self.assertRaises(ValueError):
            R.places_of(22, [1, 2])
        with self.assertRaises(ValueError):
            R.places_of(22, [0, 0, 1])
        with self.assertRaises(ValueError):
            R.places_of(22, [0, 22])
        with self.assertRaises(ValueError):
            R.loglik(np.zeros((1, 7, 2)), [0], mu, sd, SYNTH)


# a length, two areas, two angles and a mirrored pair's mean: every kind and every power of the size
MIXED = ["endplate", "canal_area", "endplate_incl", "pedicle_area:mean", "facet_sag_sup:mean", "canal_ap"]


def mixed_columns(n, seed, keys=MIXED):
    ms = MS.select(keys)
    mu, sd = MS.arrays(ms)
    cols = C.draw_columns(MS.reference(ms), ["typical"], seed, n, [MS.archive_key(m) for m in ms],
                          noise_mm=MS.errors(ms), power=MS.powers(ms))
    return ms, cols.values, mu, sd


class Kinds(unittest.TestCase):
    """Each kind with its own power of the size (step e): a length's mean and spread scale with
    s, an area's with s squared and an angle's not at all, and every power 1 is the archive's."""

    def test_mixed_kinds_equal_a_dense_normal_on_gapped_fields_with_values_missing(self):
        ms, V, mu, sd = mixed_columns(6, 51)
        X, _, _ = C.fields(V, [0, 2, 3])
        X = X[::9].copy()
        X[0, 1, 2] = np.nan
        X[2, 4, :] = np.nan
        X[3, :, 0] = np.nan
        sizes = np.array([0.8, 0.95, 1.0, 1.04, 1.25])
        noise, power = MS.errors(ms), MS.powers(ms)
        LL = R.loglik(X, [0, 2, 3], mu, sd, R.SYNTH, sizes=sizes, noise=noise, power=power)
        dense = R.dense_loglik(X, [0, 2, 3], mu, sd, R.SYNTH, sizes, noise=noise, power=power)
        self.assertLess(np.abs(LL - dense).max(), 1e-9)
        # an angle's likelihood is the same at every size; a length's and an area's are not
        for m, p in enumerate(power):
            spread = np.abs(LL[:, :, m, :] - LL[:, :, m, :1]).max()
            if p == 0:
                self.assertEqual(spread, 0.0, ms[m].key)
            else:
                self.assertGreater(spread, 1.0, ms[m].key)

    def test_every_power_given_as_one_is_no_power_given_to_the_bit_and_the_archives_rule(self):
        # the closed form sums its terms in another order than exact.py's, so the archive's rule is
        # matched to about 1e-11, not to the bit; what is to the bit is that a power of 1 changes
        # nothing of the arithmetic of no power at all
        V, mu, sd = archive_columns(8)
        X, _, _ = E.fields(V, 3)
        plain = R.loglik(X, [0, 1, 2], mu, sd, SYNTH)
        ones = R.loglik(X, [0, 1, 2], mu, sd, SYNTH, power=np.ones(7))
        self.assertTrue(np.array_equal(plain, ones))
        self.assertLess(np.abs(ones - E.field_loglik(X, mu, sd, SYNTH)).max(), 1e-10)
        self.assertTrue(np.array_equal(R.name(X, [0, 1, 2], mu, sd, SYNTH)["all"],
                                       R.name(X, [0, 1, 2], mu, sd, SYNTH, power=MS.powers(MS.select(MS.SPINEPS_7)))["all"]))
        sizes, _ = R.quadrature(SYNTH["scale_sd"])
        f = R.size_factors(sizes, np.array([1.0, 2.0, 0.0, 0.5]), 4)
        self.assertTrue(np.array_equal(f[0], sizes))
        self.assertTrue(np.array_equal(f[1], sizes * sizes))
        self.assertTrue(np.all(f[2] == 1.0))
        self.assertLess(np.abs(f[3] - np.sqrt(sizes)).max(), 1e-15)
        with self.assertRaises(ValueError):
            R.size_factors(sizes, np.ones(3), 4)

    def test_the_trapezoid_rule_is_the_integral_where_the_size_is_known_closely(self):
        # with every measure of the pool the posterior of log s is narrow, about 0.011 at nine
        # bodies; the trapezoid rule's step of 0.004 agrees with a grid twice as fine, and on the
        # seven, where the size is known loosely, it is the archive's Gauss-Hermite rule
        pool = MS.pool()
        noise, power = MS.errors(pool), MS.powers(pool)
        _, V, mu, sd = mixed_columns(3, 53, [MS.archive_key(m) for m in pool])
        coarse, fine = R.trapezoid(SYNTH["scale_sd"]), R.trapezoid(SYNTH["scale_sd"], step=0.002)
        self.assertEqual((len(coarse[0]), len(fine[0])), (281, 561))
        self.assertAlmostEqual(float(np.exp(R.logsumexp(coarse[1][None, :], 1)[0])), 1.0, places=14)
        for n in (1, 3, 9):
            X, truth, _ = C.fields(V, list(range(n)))
            X, truth = X[::4], truth[::4]
            evidence = []
            for sizes, logw in (coarse, fine):
                LL = R.loglik(X, list(range(n)), mu, sd, SYNTH, sizes=sizes, noise=noise, power=power)
                evidence.append(R.log_evidence(LL, logw))
            at_truth = [e[np.arange(len(X)), truth] for e in evidence]
            self.assertLess(np.abs(at_truth[0] - at_truth[1]).max(), 1e-11, n)
            self.assertLess(np.abs(R.posterior(evidence[0]) - R.posterior(evidence[1])).max(), 1e-12, n)
        V7, mu7, sd7 = archive_columns(10)
        for n in (1, 3, 9):
            X, _, _ = E.fields(V7, n)
            gh = R.name(X, list(range(n)), mu7, sd7, SYNTH)["all"]
            tr = R.name(X, list(range(n)), mu7, sd7, SYNTH, nodes=coarse)["all"]
            self.assertLess(np.abs(gh - tr).max(), 1e-9, n)
        sizes0, logw0 = R.trapezoid(0.0)                 # no size spread: one node, s = 1
        self.assertTrue(np.array_equal(sizes0, np.ones(1)) and np.array_equal(logw0, np.zeros(1)))


class Guarantee(unittest.TestCase):
    def test_names_given_at_099_are_right_at_least_99_per_cent_of_the_time(self):
        ds = MS.dataset()
        seven = MS.select(MS.SPINEPS_7)
        ref = MS.reference(seven)
        mu, sd = MS.arrays(seven)
        cols = C.draw_columns(ref, ["typical"], 5, 300, [MS.archive_key(m) for m in seven])
        for offsets in ([0, 1, 2], [0, 2, 4]):
            X, truth, grp = C.fields(cols.values, offsets)
            post = R.name(X, offsets, mu, sd, R.SYNTH)["all"]
            top, call = post.max(1), post.argmax(1)
            sure = top >= 0.99
            self.assertGreater(sure.sum(), 100)
            # the draws are seed 5's, so the share is fixed: 0.997 and 1.0 for the two patterns
            self.assertGreaterEqual((call[sure] == truth[sure]).mean(), 0.99)
            self.assertGreater((call == truth).mean(), 0.5)


if __name__ == "__main__":
    unittest.main()

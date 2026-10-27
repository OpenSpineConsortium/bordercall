"""The vectorised rule is the archive's rule, and more: each claim checked against something
outside the package.

    python -m unittest discover -s tests -v          # from the repository's root, in the PyMC venv

On contiguous, complete fields of widths 1, 2, 3, 5, 9 and 22 the per-measure log likelihoods
and the posteriors equal exact.py's to 1e-10, absolutely; on gapped fields and fields with missing values the closed form equals a
dense multivariate normal computed by scipy on the bodies present; a measure missing on every
body changes no posterior; a field with no measure gets the prior back; the chunking of the
matrix product changes nothing; and the selective guarantee holds on fresh draws.
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

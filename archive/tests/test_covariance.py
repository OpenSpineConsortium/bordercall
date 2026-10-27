"""The between-measure covariance: the correlation machinery and what the tables can supply.

    python -m unittest discover -s tests -v

Two things are guarded here. First, that asking the generator for a correlation of r
actually produces a correlation of r -- a Cholesky factor applied to the wrong axis, or a
factor built from a matrix that is not a correlation matrix, gives finite, plausible,
uncorrelated draws and raises nothing. Second, that the reading of Panjabi's ratio rows
stays a reading of the TWO-DECIMAL rows. A ratio printed to one decimal cannot distinguish
a ratio of means from a mean of ratios, so letting one carry the verdict would make the
answer depend on typesetting.
"""
from __future__ import annotations

import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "bordercall"))

import covariance as CV       # noqa: E402
import panjabi as P           # noqa: E402


class TestExchangeable(unittest.TestCase):
    def test_is_a_correlation_matrix(self):
        for k in (2, 3, 7):
            for r in (0.0, 0.3, 0.8, 0.9):
                R = CV.exchangeable(k, r)
                self.assertEqual(R.shape, (k, k))
                np.testing.assert_allclose(np.diag(R), np.ones(k))
                np.testing.assert_allclose(R, R.T)
                # positive definite, or the Cholesky below is meaningless
                self.assertGreater(np.linalg.eigvalsh(R).min(), 0.0)

    def test_off_diagonal_is_r(self):
        R = CV.exchangeable(5, 0.42)
        off = R[~np.eye(5, dtype=bool)]
        np.testing.assert_allclose(off, 0.42)

    def test_factor_reproduces_the_matrix(self):
        for r in (0.0, 0.5, 0.9):
            L = CV.offset_factor(7, r)
            np.testing.assert_allclose(L @ L.T, CV.exchangeable(7, r), atol=1e-12)


class TestCorrelatedOffsets(unittest.TestCase):
    """Asked for r, the draws must actually come back at r."""

    measures = ["endplate", "h_post", "canal_w", "canal_ap"]

    def _draws(self, r, n, seed):
        """n patients x k measures. ONE call per patient -- calling it once per measure
        would take each component from a different draw and read r = 0 whatever r is."""
        rng = np.random.default_rng(seed)
        rows = []
        for _ in range(n):
            got = CV.correlated_offsets(rng, self.measures, r)
            rows.append([got[m] for m in self.measures])
        return np.array(rows)

    def _measured_r(self, r, n=20000, seed=3):
        draws = self._draws(r, n, seed)
        C = np.corrcoef(draws.T)
        return float(np.mean(C[~np.eye(len(self.measures), dtype=bool)]))

    def test_zero_stays_zero(self):
        # the recorded runs were made at the default, so this is also a reproducibility gate
        self.assertLess(abs(self._measured_r(0.0)), 0.03)

    def test_asked_eight_gets_eight(self):
        self.assertAlmostEqual(self._measured_r(0.8), 0.8, delta=0.03)

    def test_unit_variance(self):
        draws = self._draws(0.6, 20000, 11)
        np.testing.assert_allclose(draws.std(axis=0), np.ones(len(self.measures)),
                                   rtol=0.05)

    def test_every_r_on_the_grid_comes_back(self):
        for r in CV.R_GRID:
            got = self._measured_r(r, n=8000, seed=13)
            self.assertAlmostEqual(got, r, delta=0.04,
                                   msg="asked r = %.2f, measured %.3f" % (r, got))

    def test_every_measure_is_present(self):
        rng = np.random.default_rng(5)
        got = CV.correlated_offsets(rng, self.measures, 0.5)
        self.assertEqual(sorted(got), sorted(self.measures))


class TestGeneratorHonoursIt(unittest.TestCase):
    """r_between has to reach the synthesized column, not stop at the signature."""

    def test_r_between_changes_the_column(self):
        ref = P.load_reference(measures=["endplate", "h_post", "canal_w"])
        a = P.synthesize(ref, "typical", np.random.default_rng(7),
                         measures=["endplate", "h_post", "canal_w"], r_between=0.0)
        b = P.synthesize(ref, "typical", np.random.default_rng(7),
                         measures=["endplate", "h_post", "canal_w"], r_between=0.9)
        same = all(np.allclose(a.values[m], b.values[m]) for m in a.values)
        self.assertFalse(same, "r_between is being ignored by the generator")


class TestRatioTest(unittest.TestCase):
    def test_verdict_rests_on_two_decimal_rows(self):
        ok, rows = CV.ratio_test()
        self.assertTrue(ok, "the two-decimal rows should read as ratios of means")
        two_dp = [r for r in rows if r[4] >= 2]
        self.assertTrue(two_dp, "there must be at least one decisive row")
        for name, d, tol, within, dp in two_dp:
            self.assertTrue(within, "%s: residual %.4f exceeds rounding %.4f"
                            % (name, d, tol))

    def test_one_decimal_row_cannot_flip_the_verdict(self):
        """The thoracic row is printed to 1 d.p. and one cell sits outside even that.

        That is a rounding or typesetting question, not evidence of a covariance, and it
        must not be able to carry the answer.
        """
        one_dp = [r for r in CV.ratio_test()[1] if r[4] == 1]
        self.assertTrue(one_dp, "the thoracic row should still be in the table")
        self.assertFalse(all(r[3] for r in one_dp),
                         "this test is only meaningful while a 1 d.p. row fails its "
                         "tolerance; if the transcription is corrected, retire it")
        # fails its own tolerance, and the verdict is still yes
        self.assertTrue(CV.ratio_test()[0])

    def test_report_runs(self):
        self.assertEqual(CV.report(), 0)


class TestBinomialSe(unittest.TestCase):
    def test_known_value(self):
        self.assertAlmostEqual(CV.binomial_se(0.5, 100), 0.05, places=6)

    def test_zero_n_is_nan_not_a_crash(self):
        self.assertTrue(np.isnan(CV.binomial_se(0.5, 0)))


if __name__ == "__main__":
    unittest.main()

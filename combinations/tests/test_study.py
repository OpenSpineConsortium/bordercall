"""The combination rules on a handful of synthetic columns: each rule is what it says it is."""
import math
import unittest

import numpy as np

from combinations import study as S

N_COLUMNS = 12


class Rules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ref = S.P.load_reference(S.P.DEFAULT_REFERENCE, S.SEVEN)
        cls.mu, cls.sd = S.EX.table_arrays(ref, S.SEVEN)
        cls.synth = dict(S.NB.SYNTH)
        cls.V = S.EX.column_values(S.NB.draw_columns(ref, ["typical"], S.NB.SCORE_SEED, N_COLUMNS, S.SEVEN), S.SEVEN)

    def field(self, n):
        X, truth, group = S.EX.fields(self.V, n)
        return X[::7], np.log(X[::7].reshape(len(X[::7]), -1))

    def test_the_raw_family_is_the_archive_formula_rule(self):
        X, Y = self.field(3)
        A = S.families(3)["raw measures (the formula rule)"]
        ours = S.formula_posterior(Y, A, self.mu, self.sd, 3, self.synth)
        archive = S.EX.posterior(S.EX.formula_log_evidence(X, self.mu, self.sd, self.synth))
        np.testing.assert_allclose(ours, archive, atol=1e-10)

    def test_every_ratio_is_a_contrast_and_the_basis_is_orthonormal(self):
        C = S.contrasts(21)
        np.testing.assert_allclose(C.sum(1), 0.0, atol=1e-12)
        np.testing.assert_allclose(C @ C.T, np.eye(20), atol=1e-12)
        fam = S.families(3)
        scale_free = {k for k, A in fam.items() if S.is_scale_free(A)}
        self.assertEqual(set(fam) - scale_free, {"raw measures (the formula rule)", "body size: EPWu x EPDu x VBHp"})

    def test_a_scale_free_family_does_not_see_the_unit(self):
        X, Y = self.field(3)
        for name, A in S.families(3).items():
            if not S.is_scale_free(A):
                continue
            with self.subTest(family=name):
                a = S.formula_posterior(Y, A, self.mu, self.sd, 3, self.synth)
                b = S.formula_posterior(Y + math.log(7.3), A, self.mu, self.sd, 3, self.synth)
                np.testing.assert_allclose(a, b, atol=1e-10)

    def test_the_exact_scale_free_rule_does_not_see_the_unit(self):
        X, _ = self.field(3)
        a = S.invariant_posterior(X, self.mu, self.sd, self.synth)
        b = S.invariant_posterior(X * 7.3, self.mu, self.sd, self.synth)
        np.testing.assert_allclose(a, b, atol=1e-9)

    def test_a_wrong_magnification_moves_the_raw_rule_and_not_the_ratios(self):
        X, Y = self.field(5)
        raw = S.families(5)["raw measures (the formula rule)"]
        ratios = S.families(5)["every ratio (all scale-free contrasts)"]
        shift = math.log(S.M_WRONG / S.M0)
        moved = np.abs(S.formula_posterior(Y + shift, raw, self.mu, self.sd, 5, self.synth)
                       - S.formula_posterior(Y, raw, self.mu, self.sd, 5, self.synth)).max()
        kept = np.abs(S.formula_posterior(Y + shift, ratios, self.mu, self.sd, 5, self.synth)
                      - S.formula_posterior(Y, ratios, self.mu, self.sd, 5, self.synth)).max()
        self.assertGreater(moved, 0.01)
        self.assertLess(kept, 1e-10)


class Deterministic(unittest.TestCase):
    def test_a_deterministic_combination_adds_nothing_to_the_log_density(self):
        from combinations import pymc_check as Q
        ref = S.P.load_reference(S.P.DEFAULT_REFERENCE, S.SEVEN)
        mu, sd = S.EX.table_arrays(ref, S.SEVEN)
        V = S.EX.column_values(S.NB.draw_columns(ref, ["typical"], S.NB.SCORE_SEED, 2, S.SEVEN), S.SEVEN)
        X, _, _ = S.EX.fields(V, 3)
        self.assertEqual(Q.logp_same(X[0], mu, sd, dict(S.NB.SYNTH)), 0.0)


if __name__ == "__main__":
    unittest.main()

"""The run-naming study (schwingcheck/run_naming.py, bordercall #56), checked against what holds
outside its own code: a correctly specified Bayes rule is calibrated, so over fields drawn from the
model the mean probability it gives the truth equals the mean of the sum of its squared
probabilities, and the misspecified scorer has no such guarantee; the size integral has converged;
and the anchors and the answer do what their names say.

    python -m unittest tests.test_schwingcheck_run_naming -v
"""
import unittest

import numpy as np

from schwingcheck import run_naming as RN

FIELDS = 600


def by_names(s, hyps, post, k):
    labels = [RN.names_of(s, h, k) for h in hyps]
    unique = sorted(set(labels))
    P = np.zeros((len(post), len(unique)))
    for j, u in enumerate(labels):
        P[:, unique.index(u)] += post[:, j]
    return unique, P


class RunNaming(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prior = RN.stand_in_prior()
        cls.s = RN.Setting()

    def test_the_true_scorer_is_calibrated(self):
        # With one type the fields below are drawn exactly as the model says (a uniform place, the
        # size, the prior's field, the error), so the true scorer's mean probability of the truth
        # equals its mean sum of squared probabilities; the assumed scorer's need not.
        types = RN.TYPES
        try:
            RN.TYPES = {"typical": 1.0}
            s = RN.Setting()
            X, truth = RN.draw_fields(s, self.prior, "typical", 2, "none", FIELDS, 11)
            gaps, mean_true = {}, {}
            for structure in ("true", "assumed"):
                hyps, post = RN.posterior(X, s, self.prior, structure, 2, "none")
                unique, P = by_names(s, hyps, post, 2)
                p_true = np.array([P[i, unique.index(truth[i])] for i in range(len(truth))])
                gaps[structure] = p_true.mean() - (P * P).sum(axis=1).mean()
                mean_true[structure] = p_true.mean()
        finally:
            RN.TYPES = types
        self.assertLess(abs(gaps["true"]), 0.03, gaps)
        # and the rule that knows how the levels move together gives the truth more probability
        self.assertGreater(mean_true["true"], mean_true["assumed"] + 0.03, mean_true)

    def test_the_posterior_sums_to_one_and_the_truth_is_a_hypothesis(self):
        X, truth = RN.draw_fields(self.s, self.prior, "t13", 3, "none", 50, 3)
        hyps, post = RN.posterior(X, self.s, self.prior, "assumed", 3, "none")
        np.testing.assert_allclose(post.sum(axis=1), 1.0, atol=1e-12)
        names = {RN.names_of(self.s, h, 3) for h in hyps}
        self.assertTrue(all(n in names for n in truth))

    def test_the_size_integral_has_converged(self):
        X, _ = RN.draw_fields(self.s, self.prior, "typical", 6, "none", 40, 5)
        _, coarse = RN.posterior(X, self.s, self.prior, "true", 6, "none")
        nodes = RN.SIZE_NODES
        try:
            RN.SIZE_NODES = 281
            fine_setting = RN.Setting()
        finally:
            RN.SIZE_NODES = nodes
        _, fine = RN.posterior(X, fine_setting, self.prior, "true", 6, "none")
        self.assertLess(np.abs(coarse - fine).max(), 1e-6)

    def test_an_anchor_fixes_the_place_and_leaves_the_type(self):
        for anchor, place in (("bottom", lambda n, k: n - k), ("top", lambda n, k: 0)):
            hyps = RN.hypotheses(self.s, 2, anchor)
            self.assertEqual(sorted(t for t, _ in hyps), sorted(RN.TYPES))
            for t, p in hyps:
                self.assertEqual(p, place(len(self.s.levels(t)), 2))

    def test_the_answer_is_the_first_run_whose_interval_clears_the_target(self):
        rows = [dict(k=k, anchor="none", type="typical", structure="true", accuracy=a, lo=lo)
                for k, a, lo in ((1, 0.5, 0.45), (2, 0.92, 0.89), (3, 0.95, 0.91), (4, 0.97, 0.95))]
        self.assertEqual(RN.answer(rows)["k"], 3)
        self.assertIsNone(RN.answer(rows[:2])["k"])

    def test_the_wilson_interval_holds_the_estimate(self):
        lo, hi = RN.wilson(45, 50)
        self.assertLess(lo, 0.9)
        self.assertGreater(hi, 0.9)
        self.assertLessEqual(hi, 1.0)


if __name__ == "__main__":
    unittest.main()

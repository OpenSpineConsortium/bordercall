"""The phantom's anatomy drawn jointly from a correlation prior (bordercall #53): the levels and
measures of one column move together as the prior says, never independently, and with no prior
every phantom is as before."""
import unittest

import numpy as np

from autoanatomist import phantom as PH
from schwingcheck import correlation as CORR

FITTED = ["endplate", "endplate_depth", "endplate_lower", "endplate_lower_depth", "h_post"]
R_MEASURE = np.array([[1.0, 0.6, 0.8, 0.5, 0.3],
                      [0.6, 1.0, 0.5, 0.8, 0.2],
                      [0.8, 0.5, 1.0, 0.6, 0.3],
                      [0.5, 0.8, 0.6, 1.0, 0.2],
                      [0.3, 0.2, 0.3, 0.2, 1.0]])
DRAWS = 4000
TOLERANCE = 0.05


def known_prior():
    levels = CORR.expand_levels("C3..L5")
    lag = np.abs(np.subtract.outer(np.arange(len(levels)), np.arange(len(levels))))
    return CORR.Prior(levels=levels, measures=list(FITTED), r_level=0.8 ** lag, r_measure=R_MEASURE, n=1000,
                      note="a known structure for the test")


def draws(prior, start="L1", count=4):
    """(draws, levels, measures) of SHAPE_MEASURES, at size 1 so a value is linear in the field."""
    out = []
    for seed in range(DRAWS):
        levels = PH.draw_levels("typical", seed=seed, start=start, count=count, correlation=prior, scale_sd=0.0)
        out.append([[getattr(l, a) for a in ("W_top", "D_top", "W_bot", "D_bot", "H", "CW", "CD")] for l in levels])
    return np.array(out)


def corr(a, b):
    return float(np.corrcoef(a, b)[0, 1])


class PhantomPrior(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prior = known_prior()
        cls.x = draws(cls.prior)          # columns: endplate, depth, lower, lower depth, h_post, canal w, canal ap

    def test_no_prior_is_unchanged(self):
        a = PH.draw_levels("typical", seed=7, start="L1", count=3)
        b = PH.draw_levels("typical", seed=7, start="L1", count=3, correlation=None)
        self.assertEqual(a, b)

    def test_levels_move_together_as_the_prior_says(self):
        r = self.prior.r_level
        at = {n: i for i, n in enumerate(self.prior.levels)}
        for m in range(5):
            for i, j in ((0, 1), (0, 2), (1, 3)):
                want = r[at[["L1", "L2", "L3", "L4"][i]], at[["L1", "L2", "L3", "L4"][j]]]
                self.assertAlmostEqual(corr(self.x[:, i, m], self.x[:, j, m]), want, delta=TOLERANCE)

    def test_measures_move_together_as_the_prior_says(self):
        for a in range(5):
            for b in range(a + 1, 5):
                self.assertAlmostEqual(corr(self.x[:, 1, a], self.x[:, 1, b]), R_MEASURE[a, b], delta=TOLERANCE)

    def test_an_independent_draw_would_fail(self):
        # the generator's assumed structure correlates two levels of a measure at 0.25 and two measures at 0
        self.assertGreater(corr(self.x[:, 0, 0], self.x[:, 1, 0]), 0.25 + 4 * TOLERANCE)
        self.assertGreater(corr(self.x[:, 1, 0], self.x[:, 1, 2]), 4 * TOLERANCE)

    def test_unfitted_measures_follow_the_levels_and_not_the_fitted_measures(self):
        canal = 5
        self.assertAlmostEqual(corr(self.x[:, 0, canal], self.x[:, 1, canal]), 0.8, delta=TOLERANCE)
        self.assertAlmostEqual(corr(self.x[:, 1, canal], self.x[:, 1, 0]), 0.0, delta=TOLERANCE)

    def test_a_prior_without_the_columns_levels_is_refused(self):
        lumbar = CORR.Prior(levels=CORR.expand_levels("T1..L5"), measures=list(FITTED),
                            r_level=np.eye(17), r_measure=R_MEASURE)
        with self.assertRaises(ValueError):
            PH.draw_levels("typical", seed=0, start="L1", count=2, correlation=lumbar)


if __name__ == "__main__":
    unittest.main()

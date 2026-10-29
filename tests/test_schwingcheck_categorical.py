"""The corrected Metropolised Gibbs step (categorical.py), checked lightly, as the owner asked.

    python -m unittest tests.test_schwingcheck_categorical -v      # from the repository's root, in the PyMC venv

One move from each value goes where Liu's kernel (fixed_k.proposal_kernel, 'liu') says, counted over
many moves; the step in pm.sample gives a bare Categorical its own law, on three values and on the
two-value one where PyMC's proportional proposal gives each value half; and a value all but certain,
or certain, is kept with no NaN and no error, where PyMC's proposal stops.
"""
from __future__ import annotations

import os
import sys
import unittest
import warnings

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from schwingcheck import categorical as CG                        # noqa: E402
from schwingcheck import fixed_k as FK                            # noqa: E402


def sample(p, draws=4000, chains=2, seed=11):
    import pymc as pm
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with pm.Model():
            place = pm.Categorical("place", p=np.asarray(p, float))
            idata = pm.sample(draws=draws, tune=200, chains=chains, cores=1, step=CG.MetropolisedGibbs([place]),
                              random_seed=seed, progressbar=False, compute_convergence_checks=False)
    return np.asarray(idata.posterior["place"].values, int)


class OneMove(unittest.TestCase):
    def test_each_move_follows_liu_kernel(self):
        p = np.array([0.6, 0.3, 0.1])
        want = FK.proposal_kernel(p, "liu")
        rng = np.random.default_rng(5)
        n = 40_000
        for i in range(len(p)):
            got = np.bincount([CG.liu_move(np.log(p), i, rng) for _ in range(n)], minlength=len(p)) / n
            se = np.sqrt(want[i] * (1 - want[i]) / n)
            self.assertTrue(np.all(np.abs(got - want[i]) <= 5 * se + 1e-12), (i, got, want[i]))

    def test_the_complements_are_one_less_each_probability(self):
        log_p = np.log([0.5, 0.25, 0.25])
        np.testing.assert_allclose(np.exp(CG.log_complements(log_p)), [0.5, 0.75, 0.75], rtol=1e-12)


class InPyMC(unittest.TestCase):
    def test_a_bare_place_gets_its_own_law(self):
        for p in ([0.6, 0.3, 0.1], [0.89, 0.11]):
            labels = sample(p)
            share, se = FK.counted_posterior(labels, len(p), 10)
            self.assertTrue(np.all(np.abs(share - p) <= 5 * se + 1e-3), (p, share, se))

    def test_a_value_certain_or_all_but_certain_is_kept(self):
        for p in ([1.0, 1e-30], [1.0, 0.0, 0.0]):
            labels = sample(p, draws=300, chains=1)
            self.assertTrue(np.all(labels == 0), p)


if __name__ == "__main__":
    unittest.main()

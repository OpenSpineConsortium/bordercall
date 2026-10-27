"""The exact rule extended to missing measures, gaps and an unknown scale: the archive's rule
where nothing is missing, the normal marginal where something is."""
import math
import unittest

import numpy as np

from scanimport import SEVEN, RULE_LEVELS, bridge as B
from scanimport.column import Body, Column, facts_from_levels
import exact as EX
import neighbour as NB
import panjabi as P

REF = P.load_reference(P.DEFAULT_REFERENCE, SEVEN)
MU, SD = EX.table_arrays(REF, SEVEN)


def columns(n, seed):
    rng = np.random.default_rng(seed)
    cols = [P.synthesize(REF, "typical", rng, scale_sd=0.07, rho=0.5, noise_mm=1.0, measures=SEVEN) for _ in range(n)]
    return EX.column_values(cols, SEVEN)


def dense_loglik(X, offsets, start, s, rho=0.5, noise=1.0):
    """The same density written out: per measure, the full covariance over the field's bodies,
    its rows and columns for the present entries, a Cholesky factor."""
    total = 0.0
    pos = start + np.asarray(offsets)
    for m in range(X.shape[0]):
        have = np.isfinite(X[m])
        if not have.any():
            continue
        sw, mw = SD[m, pos], MU[m, pos]
        C = s * s * (rho * rho * np.outer(sw, sw) + (1 - rho * rho) * np.diag(sw * sw)) + noise * noise * np.eye(len(pos))
        C = C[np.ix_(have, have)]
        r = X[m, have] - s * mw[have]
        Lc = np.linalg.cholesky(C)
        z = np.linalg.solve(Lc, r)
        total += -0.5 * (z @ z + 2 * np.log(np.diag(Lc)).sum() + have.sum() * math.log(2 * math.pi))
    return total


class SameAsTheArchive(unittest.TestCase):
    def test_complete_consecutive_fields(self):
        V = columns(3, 5)
        sizes, logw = EX.trapezoid(NB.SYNTH["scale_sd"])
        for n in (1, 3, 9, 22):
            X, _, _ = EX.fields(V, n)
            archive = EX.evidence_lean(X, MU, SD, NB.SYNTH, sizes, logw)
            mine = np.array([B.log_evidence(x, list(range(n)), MU, SD, NB.SYNTH) for x in X])
            self.assertLess(np.abs(mine - archive).max(), 1e-10)
            gh = EX.posterior(EX.log_evidence(EX.field_loglik(X, MU, SD, NB.SYNTH), EX.quadrature(NB.SYNTH["scale_sd"])[1]))
            self.assertLess(np.abs(np.array([B.posterior(e) for e in mine]) - gh).max(), 1e-6)


class Marginals(unittest.TestCase):
    def test_missing_values_are_the_normal_marginal(self):
        X = columns(1, 7)[0][:, 4:10].copy()
        X[0, 2] = X[3, 0] = X[3, 1] = math.nan
        X[5, :] = math.nan
        offs = list(range(6))
        for k in (0, 7, 16):
            for s in (0.9, 1.0, 1.13):
                mine = B.place_loglik(X, offs, MU, SD, k, np.array([s]), 0.5, 1.0).sum()
                self.assertAlmostEqual(mine, dense_loglik(X, offs, k, s), places=9)

    def test_a_gap_compares_each_body_with_its_own_level(self):
        V = columns(1, 9)[0]
        offs = [0, 1, 3, 4]
        X = V[:, [10, 11, 13, 14]]
        for k in (0, 5, 17):
            for s in (0.95, 1.05):
                mine = B.place_loglik(X, offs, MU, SD, k, np.array([s]), 0.5, 1.0).sum()
                self.assertAlmostEqual(mine, dense_loglik(X, offs, k, s), places=9)
        self.assertEqual(B.places(offs), len(RULE_LEVELS) - 4)
        post = B.posterior(B.log_evidence(X, offs, MU, SD, NB.SYNTH))
        self.assertEqual(int(np.argmax(post)), 10)

    def test_an_unknown_scale_names_by_proportion_alone(self):
        X = columns(1, 11)[0][:, 6:13]
        a = B.posterior(B.log_evidence(X, list(range(7)), MU, SD, NB.SYNTH, 0.0, None))
        b = B.posterior(B.log_evidence(X * 6.25, list(range(7)), MU, SD, NB.SYNTH, 0.0, None))
        self.assertLess(np.abs(a - b).max(), 1e-9)
        self.assertEqual(int(np.argmax(a)), 6)

    def test_a_wider_scale_spread_is_less_sure_on_average(self):
        V = columns(12, 13)
        X, truth, _ = EX.fields(V, 3)
        tight = np.mean([B.posterior(B.log_evidence(x, [0, 1, 2], MU, SD, NB.SYNTH))[t] for x, t in zip(X, truth)])
        loose = np.mean([B.posterior(B.log_evidence(x, [0, 1, 2], MU, SD, NB.SYNTH, 0.0, 0.2))[t] for x, t in zip(X, truth)])
        self.assertGreater(tight, loose)


class Scoring(unittest.TestCase):
    def test_a_counted_synthetic_study_is_scored_against_its_names(self):
        V = columns(1, 17)[0]
        levels = ["C1", "C2"] + RULE_LEVELS + ["sacrum"]
        bodies = [Body(lv) for lv in levels]
        for j, lv in enumerate(RULE_LEVELS):
            bodies[j + 2].values = {m: float(V[i, j]) for i, m in enumerate(SEVEN)}
        study = {"study_id": "syn", "source": "panjabi", "scale_log_mean": 0.0, "scale_log_sd": 0.0}
        study.update(facts_from_levels(levels, {"L6": True, "T13": True}))
        rows = B.score_column(Column(study, bodies), MU, SD, SEVEN, NB.SYNTH, widths=(1, 15))
        self.assertEqual(len([r for r in rows if r["n"] == 1]), 22)
        self.assertEqual(len([r for r in rows if r["n"] == 15]), 8)
        wide = [r for r in rows if r["n"] == 15]
        self.assertGreaterEqual(np.mean([r["hit"] for r in wide]), 0.75)
        summary = B.summarise(rows)
        self.assertEqual({s["group"] for s in summary}, {"typical"})


if __name__ == "__main__":
    unittest.main()

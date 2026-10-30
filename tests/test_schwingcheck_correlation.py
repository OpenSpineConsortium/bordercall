"""The correlation prior recovers a known structure, scores held-out spines, and draws as fitted.

Spines are drawn from a matrix normal with a known correlation between levels (an AR(1) at 0.8)
and between measures, so the truth is exact: the flip-flop fit must find both within sampling
error, and on held-out spines from the same truth the fitted structure must beat the generator's
assumed one. The assumed one is checked against the generator itself, which shows the default
rho of 0.5 correlates two levels of one measure at 0.25. draw_columns without a prior is the
stream it was before this block, to the bit (a digest taken on bordercall a87e0b3); with a prior,
its standardised draws carry the prior's correlation, and L6 and T13 borrow their neighbours'.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from schwingcheck import LEVELS                  # noqa: E402
from schwingcheck import columns as C            # noqa: E402
from schwingcheck import correlation as CORR     # noqa: E402

MAIN_DIGEST = "b2802f68784c5b8c2d6e5625ce34526fb4433f22b76ddac8beaa992cf2d08f8b"
MS = ["a", "b", "c"]


def ar1(n: int, phi: float) -> np.ndarray:
    i = np.arange(n)
    return phi ** np.abs(i[:, None] - i[None, :])


def truth(L: int = 10, M: int = 3):
    rm = np.array([[1.0, 0.6, -0.3], [0.6, 1.0, 0.1], [-0.3, 0.1, 1.0]])[:M, :M]
    return ar1(L, 0.8), rm


def matrix_normal(rng, n, rl, rm, mean=20.0, sd=2.0):
    al, am = np.linalg.cholesky(rl), np.linalg.cholesky(rm)
    e = rng.normal(size=(n, rl.shape[0], rm.shape[0]))
    return mean + sd * np.einsum("lk,nkj,mj->nlm", al, e, am)


def reference():
    return {m: {l: (10.0 + i + 3 * k, 1.0 + 0.1 * i) for i, l in enumerate(LEVELS)} for k, m in enumerate(MS)}


class Recovers(unittest.TestCase):
    def test_flip_flop_finds_the_truth(self):
        rl, rm = truth()
        x = matrix_normal(np.random.default_rng(1), 2000, rl, rm)
        p = CORR.fit(x, ["l%d" % i for i in range(10)], MS, shrink=0.0)
        self.assertEqual(p.n, 2000)
        self.assertLess(np.abs(p.r_level - rl).max(), 0.05)
        self.assertLess(np.abs(p.r_measure - rm).max(), 0.05)

    def test_incomplete_spines_are_left_out(self):
        rl, rm = truth()
        x = matrix_normal(np.random.default_rng(2), 300, rl, rm)
        x[:40, 3, 1] = np.nan
        self.assertEqual(CORR.fit(x, list("abcdefghij"), MS).n, 260)

    def test_too_few_spines_refused(self):
        with self.assertRaises(ValueError):
            CORR.flip_flop(np.zeros((1, 30, 3)))


class Assumed(unittest.TestCase):
    def test_generator_matches_its_stated_structure(self):
        ref = reference()
        cols = C.draw_columns(ref, ["typical"], 3, 6000, MS, noise_mm=0.0, scale_sd=1e-9, floor=False)
        mu = np.array([[ref[m][l][0] for m in MS] for l in LEVELS])
        sd = np.array([[ref[m][l][1] for m in MS] for l in LEVELS])
        z = (cols.values - mu) / sd
        emp = np.corrcoef(z.reshape(len(z), -1).T)
        want = CORR.assumed_cov(len(LEVELS), len(MS), 0.5, 0.0)
        self.assertLess(np.abs(emp - want).max(), 0.06)
        self.assertAlmostEqual(want[0, len(MS)], 0.25)


class HeldOut(unittest.TestCase):
    def test_fitted_beats_assumed_on_its_own_truth(self):
        rl, rm = truth()
        rng = np.random.default_rng(4)
        train, test = matrix_normal(rng, 800, rl, rm), matrix_normal(rng, 300, rl, rm)
        p = CORR.fit(train, list("abcdefghij"), MS)
        r = CORR.compare(train, test, p)
        self.assertEqual(r["n_test"], 300)
        self.assertGreater(r["gain_per_spine"], 5 * r["gain_se"])
        self.assertGreater(r["share_better"], 0.8)

    def test_assumed_wins_when_it_is_the_truth(self):
        L, M = 8, 3
        cov = CORR.assumed_cov(L, M, 0.5, 0.0)
        rng = np.random.default_rng(5)
        draw = lambda n: rng.multivariate_normal(np.zeros(L * M), cov, size=n).reshape(n, L, M)
        train, test = draw(800), draw(400)
        p = CORR.fit(train, list("abcdefgh"), MS)
        r = CORR.compare(train, test, p)
        self.assertLess(r["gain_per_spine"], 0.0)


class Draws(unittest.TestCase):
    def test_default_stream_unchanged(self):
        h = hashlib.sha256()
        for rb in (0.0, 0.4):
            cols = C.draw_columns(reference(), C.PHENOTYPES, 7, 24, MS, r_between=rb)
            h.update(np.nan_to_num(cols.values, nan=-1.0).tobytes())
            self.assertNotIn("correlation", cols.meta)
        self.assertEqual(h.hexdigest(), MAIN_DIGEST)

    def prior(self):
        rl = ar1(len(LEVELS), 0.7)
        rm = truth()[1]
        return CORR.Prior(list(LEVELS), list(MS), rl, rm, n=1, note="test")

    def test_draws_carry_the_prior(self):
        p, ref = self.prior(), reference()
        cols = C.draw_columns(ref, ["typical"], 9, 6000, MS, noise_mm=0.0, scale_sd=1e-9, floor=False, correlation=p)
        mu = np.array([[ref[m][l][0] for m in MS] for l in LEVELS])
        sd = np.array([[ref[m][l][1] for m in MS] for l in LEVELS])
        z = (cols.values - mu) / sd
        emp = np.corrcoef(z.reshape(len(z), -1).T)
        self.assertLess(np.abs(emp - CORR.prior_cov(p)).max(), 0.06)
        self.assertEqual(cols.meta["correlation"]["note"], "test")

    def test_every_phenotype_draws(self):
        cols = C.draw_columns(reference(), C.PHENOTYPES, 1, 60, MS, correlation=self.prior())
        for i, lv in enumerate(cols.levels):
            self.assertTrue(np.isfinite(cols.values[i, :len(lv)]).all())

    def test_borrowed_levels(self):
        p = self.prior()
        r = CORR.level_block(p, ["L4", "L5", "L6"])
        self.assertAlmostEqual(r[1, 2], p.r_level[LEVELS.index("L5"), LEVELS.index("L4")])
        self.assertAlmostEqual(r[0, 2], r[0, 1])
        r = CORR.level_block(p, ["T12", "T13", "L1"])
        self.assertAlmostEqual(r[0, 1], p.r_level[LEVELS.index("T12"), LEVELS.index("T11")])
        np.linalg.cholesky(r)

    def test_unfitted_measure_refused(self):
        with self.assertRaises(ValueError):
            C.draw_columns({**reference(), "zz": reference()["a"]}, ["typical"], 1, 2, ["a", "zz"],
                           correlation=self.prior())


class Rows(unittest.TestCase):
    def test_reads_engine_rows_and_cli_round_trip(self):
        rl, rm = truth(L=5)
        x = matrix_normal(np.random.default_rng(6), 200, rl, rm)
        levels = ["L1", "L2", "L3", "L4", "L5"]
        with tempfile.TemporaryDirectory() as d:
            rows = os.path.join(d, "rows.csv")
            with open(rows, "w", newline="") as f:
                w = csv.writer(f, lineterminator="\n")
                w.writerow(["study", "level", "key", "value", "note"])
                for s in range(len(x)):
                    for i, l in enumerate(levels):
                        for k, m in enumerate(MS):
                            w.writerow(["%04d" % s, l, "eng_" + m, x[s, i, k], ""])
                w.writerow(["0000", "L1", "eng_a", "nan", "failed"])
                w.writerow(["0000", "T5", "eng_a", "1", ""])
            keymap = os.path.join(d, "map.csv")
            with open(keymap, "w") as f:
                f.write("engine,table\n" + "".join("eng_%s,%s\n" % (m, m) for m in MS))
            train = os.path.join(d, "train.txt")
            test = os.path.join(d, "test.txt")
            open(train, "w").write("".join("%04d\n" % s for s in range(150)))
            open(test, "w").write("".join("%04d\n" % s for s in range(150, 200)))
            got, studies = CORR.read_rows(rows, levels, MS, keymap=CORR.read_keymap(keymap))
            self.assertEqual(len(studies), 200)
            self.assertTrue(np.allclose(got, x))
            out = os.path.join(d, "prior.json")
            CORR.main(["fit", "--rows", rows, "--levels", "L1..L5", "--keys", ",".join(MS), "--studies", train,
                       "--keymap", keymap, "--out", out])
            p = CORR.Prior.from_json(json.load(open(out)))
            self.assertEqual(p.n, 150)
            self.assertEqual(p.levels, levels)
            CORR.main(["compare", "--rows", rows, "--prior", out, "--train", train, "--test", test, "--keymap", keymap])


if __name__ == "__main__":
    unittest.main()

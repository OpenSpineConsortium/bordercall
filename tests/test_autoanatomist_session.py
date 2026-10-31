"""The resumable session (autoanatomist/session.py) and the examples from rows (rows.py), on the
sizes the model tests use: a crop of 16 by 20 by 12 voxels and two phantoms of three levels.

    python -m unittest tests.test_autoanatomist_session -v        # from the repository's root, in the venv

With no block named the session's three steps are train.train's three steps to the bit, every
loss and every weight; a session saved after two steps, loaded and trained one more is the three
steps straight, to the bit, and a state file of another configuration is refused; the other
blocks run (sgd with a clip and a warm-up, the joint schedule, the standardised input, the
intensity augmentation, the quantile calibration) and a continued anneal moves (w, lambda) on
from where they stood; evaluate reports the calibrated figures; rows render the same wherever
they stand, are read back from the cache to the bit, and a row appended renders alone.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

try:
    import jax  # noqa: F401
    from flax import nnx  # noqa: F401
    HAVE_JAX = True
except ImportError:                                               # pragma: no cover
    HAVE_JAX = False

ROWS = [{"kind": "phantom", "id": "p0", "count": 3, "seed": 1, "spacing": 2.0, "start": "T12"},
        {"kind": "phantom", "id": "p1", "count": 3, "seed": 2, "spacing": 2.0, "start": "L1"}]


def tiny_config():
    from autoanatomist.model import Config
    return Config(widths=(4, 8, 8), shape=(16, 20, 12), spacing=6.0)


def same_rows(test, a, b):
    test.assertEqual(len(a), len(b))
    for x, y in zip(a, b):
        for k in x:
            if k != "seconds":
                test.assertEqual(x[k], y[k], (k, x, y))


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheRows(unittest.TestCase):
    def test_rows_render_the_same_anywhere_and_the_cache_reads_back(self):
        from autoanatomist import rows as R
        cfg = tiny_config()
        with tempfile.TemporaryDirectory() as d:
            ex = R.examples_for(ROWS, cfg, cache_dir=d)
            self.assertEqual(len(ex), 6)
            self.assertEqual([len(g) for g in ex.spines()], [3, 3])
            self.assertEqual(len(ex.frames), 6)
            self.assertEqual([m["id"] for m in ex.meta], ["p0", "p1"])
            self.assertEqual(R.cached(ROWS, cfg, d), {"p0": True, "p1": True})
            again = R.examples_for(ROWS, cfg, cache_dir=d)
            for k in ("hu", "masks", "targets", "values", "names", "spine"):
                np.testing.assert_array_equal(getattr(again, k), getattr(ex, k), k)
            self.assertEqual(again.meta, ex.meta)
            self.assertEqual(len(again.frames), 0)                 # read back: the arrays, not the frames
            alone = R.render_row(ROWS[1], cfg)
            np.testing.assert_array_equal(alone.hu, ex.hu[3:])      # the same row renders the same alone
            np.testing.assert_array_equal(alone.targets, ex.targets[3:])
            more = ROWS + [{"kind": "phantom", "id": "p2", "count": 3, "seed": 3, "spacing": 2.0}]
            self.assertEqual(R.cached(more, cfg, d)["p2"], False)
            grown = R.examples_for(more, cfg, cache_dir=d)
            self.assertEqual(len(grown), 9)
            np.testing.assert_array_equal(grown.hu[:6], ex.hu)
            self.assertNotEqual(R.digest(more), R.digest(ROWS))
            self.assertEqual(R.digest(ROWS), R.digest([dict(r) for r in ROWS]))
            self.assertNotEqual(R.row_digest(ROWS[0], cfg), R.row_digest(ROWS[0], cfg, jitter=False))
            self.assertEqual(len(os.listdir(d)), 3)

    def test_rows_are_refused_in_words(self):
        from autoanatomist import rows as R
        for row, said in [({"kind": "cube", "id": "x"}, "phantom or volume"), ({"kind": "phantom"}, "needs an id"),
                          ({"kind": "phantom", "id": "x", "colour": 1}, "a phantom row takes"),
                          ({"kind": "phantom", "id": "x", "count": 0}, "at least 1"),
                          ({"kind": "phantom", "id": "x", "spacing": 0}, "above 0"),
                          ({"kind": "volume", "id": "x", "ct": "a.nii", "labels": "b.nii"}, "names"),
                          ({"kind": "volume", "id": "x", "ct": "a.nii", "labels": "b.nii", "names": {"1": "Q9"}}, "no name for"),
                          ({"kind": "volume", "id": "x", "ct": "a.nii", "labels": "b.nii", "scheme": "spineps", "names": {}}, "one of the two")]:
            with self.assertRaises(ValueError, msg=row) as cm:
                R.canonical(row)
            self.assertIn(said, str(cm.exception), row)
        c = R.canonical({"kind": "volume", "id": "v", "ct": "a.nii", "labels": "b.nii", "names": {"20": "L1", "21": "L2"}})
        self.assertEqual(c["names"], {"20": "L1", "21": "L2"})
        self.assertEqual(c["seed"], 0)


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheSession(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from autoanatomist import rows as R
        from autoanatomist import train as T
        cls.cfg = tiny_config()
        cls.ex = R.examples_for(ROWS, cls.cfg)
        cls.straight = T.train(cls.ex, cls.cfg, steps=3, spines_per_batch=2, lr=2e-3, seed=0)

    def params(self, model):
        from autoanatomist import session as S
        return S.flat_arrays(model, "model")

    def test_no_block_named_is_the_smoke_run_to_the_bit(self):
        from autoanatomist import blocks as B
        from autoanatomist import session as S
        b = B.parse("widths=4:8:8")                                # the test's small network; every other block its default
        self.assertEqual(b.changed(), ["widths=4:8:8"])
        s = S.Session.new(b, keys=self.cfg.keys, shape=self.cfg.shape, spacing=self.cfg.spacing)
        self.assertEqual(s.cfg, self.cfg)
        self.assertEqual(s.step, 0)
        self.assertIsNone(s.anneal)
        rows = s.train(self.ex, 3)
        self.assertEqual(s.step, 3)
        self.assertEqual(s.anneal.steps, 3)
        same_rows(self, rows, self.straight.record)
        mine, theirs = self.params(s.model), self.params(self.straight.model)
        self.assertEqual(set(mine), set(theirs))
        for k in mine:
            np.testing.assert_array_equal(mine[k], theirs[k], k)

    def test_saved_loaded_and_trained_on_is_the_run_straight_to_the_bit(self):
        from autoanatomist import blocks as B
        from autoanatomist import session as S
        b = B.parse("widths=4:8:8 anneal=3")                       # the straight run's three steps, two now and one later
        s = S.Session.new(b, keys=self.cfg.keys, shape=self.cfg.shape, spacing=self.cfg.spacing)
        self.assertEqual(s.anneal.steps, 3)
        first = s.train(self.ex, 2)
        with tempfile.TemporaryDirectory() as d:
            meta = s.save(d)
            self.assertEqual(sorted(os.listdir(d)), sorted([S.STATE, S.META, S.RECORD]))
            self.assertEqual(meta["step"], 2)
            self.assertEqual(meta["anneal"]["steps"], 3)
            with open(os.path.join(d, S.RECORD)) as f:
                self.assertEqual(len(f.read().splitlines()), 2)
            with open(os.path.join(d, S.META)) as f:
                back = json.load(f)
            self.assertEqual(back["blocks"]["digest"], b.digest())
            self.assertEqual(back["blocks"]["changed"], ["anneal=3", "widths=4:8:8"])
            self.assertIn("model/ct/b1/conv1/kernel", np.load(os.path.join(d, S.STATE)).files)
            t = S.Session.load(d)
            self.assertEqual((t.step, t.n_bodies, t.anneal), (2, 3, s.anneal))
            self.assertEqual(t.rng.bit_generator.state, s.rng.bit_generator.state)
            for k, v in self.params(s.model).items():
                np.testing.assert_array_equal(self.params(t.model)[k], v, k)
            third = t.train(self.ex, 1)
            same_rows(self, first + third, self.straight.record)
            for k, v in self.params(self.straight.model).items():
                np.testing.assert_array_equal(self.params(t.model)[k], v, k)
            t.save(d)
            with open(os.path.join(d, S.RECORD)) as f:
                self.assertEqual(len(f.read().splitlines()), 3)
            other = S.Session.new(B.parse("widths=4:4:8"), keys=self.cfg.keys, shape=self.cfg.shape, spacing=self.cfg.spacing)
            with self.assertRaises(ValueError) as cm:               # the same paths, another shape
                S.put_arrays(other.model, np.load(os.path.join(d, S.STATE)), "model")
            self.assertIn("does not hold the model", str(cm.exception))
            self.assertIn("has shape", str(cm.exception))
            with self.assertRaises(ValueError) as cm:               # the model's arrays alone are not the optimizer's
                S.put_arrays(other.opt, {k: v for k, v in np.load(os.path.join(d, S.STATE)).items() if k.startswith("model/")},
                             "optimizer")
            self.assertIn("missing optimizer/", str(cm.exception))

    def test_the_other_blocks_the_continued_anneal_and_the_calibration(self):
        from autoanatomist import blocks as B
        from autoanatomist import session as S
        b = B.parse("widths=4:8:8 optimiser=sgd clip=1 warmup=2 weight_decay=0.001 schedule=joint normalise=clip-zscore "
                    "intensity=gain-offset-noise calibrate=quantile coverage=0.8 knee=1 spread_floor=0.3 w_spread=0.2")
        s = S.Session.new(b, keys=self.cfg.keys, shape=self.cfg.shape, spacing=self.cfg.spacing)
        rows = s.train(self.ex, 2)
        self.assertEqual(s.status()["blocks"], b.changed())
        for row in rows:
            for k in ("total", "landmark", "spread", "value", "feature", "naming", "distance_mm"):
                self.assertTrue(np.isfinite(row[k]), (k, row))
        self.assertEqual((rows[0]["w"], rows[0]["lam"]), (1.0, 0.0))
        self.assertEqual((rows[1]["w"], rows[1]["lam"]), (0.0, 1.0))      # the anneal spanned the two steps
        s.continue_anneal(until=6)
        self.assertEqual(s.anneal.rebased["from"], 2)
        self.assertEqual(s.position(), (0.0, 1.0))
        more = s.train(self.ex, 2)
        self.assertEqual([r["step"] for r in more], [2, 3])
        self.assertEqual(s.step, 4)
        fresh = S.Session.new(B.parse("widths=4:8:8 schedule=fixed lam_fixed=0.2 w_fixed=0.9"), keys=self.cfg.keys,
                              shape=self.cfg.shape, spacing=self.cfg.spacing)
        fresh.continue_anneal(until=4)                            # a fixed schedule anneals to the ends from its values
        self.assertEqual(fresh.position(), (0.9, 0.2))
        self.assertEqual(fresh.anneal.at(4), (0.0, 1.0))
        self.assertEqual(fresh.anneal.rebased["from"], 0)
        cal = s.calibrate(self.ex)
        self.assertEqual((cal["kind"], cal["coverage"], cal["rows"]), ("quantile", 0.8, 6))
        self.assertEqual(set(cal["factors"]), set(self.cfg.keys))
        res = s.evaluate(self.ex)
        for k in ("distance_mm", "value_mae", "sigma_mm", "calibrated_sigma_mm", "coverage_at_1", "coverage_at_2",
                  "named_right", "named_right_values_alone", "named_right_from_oracle", "step", "w", "lam"):
            self.assertIn(k, res)
        self.assertEqual(res["step"], 4)
        from statistics import NormalDist
        from autoanatomist import calibrate as C
        out = s.predict(self.ex)
        spread = C.apply(out["sigma"], s.factors())
        self.assertAlmostEqual(res["calibrated_sigma_mm"], float(np.mean(spread)))
        k = NormalDist().inv_cdf(0.9)                               # the Gaussian interval at the coverage of 0.8
        # fit on these six crops a measure, the 0.8 quantile is the fifth of six sorted z, which rounding puts either
        # side of k times its own calibrated spread, so the coverage is 5 or 4 of 6 a column
        self.assertGreaterEqual(C.coverage_at(out["values"] - self.ex.values, spread, k), 4.0 / 6.0 - 1e-9)
        self.assertLessEqual(res["coverage_at_1"], res["coverage_at_2"])
        with tempfile.TemporaryDirectory() as d:
            s.save(d)
            t = S.Session.load(d)
            self.assertEqual(t.calibration, cal)
            self.assertEqual(t.anneal, s.anneal)
            np.testing.assert_array_equal(t.factors(), s.factors())
        rng = np.random.default_rng(0)
        aug = S.augmented(self.ex.hu, "gain-offset", rng)
        self.assertEqual(aug.shape, self.ex.hu.shape)
        self.assertFalse(np.array_equal(aug, self.ex.hu))
        self.assertIs(S.augmented(self.ex.hu, "off", rng), self.ex.hu)
        noisy = S.augmented(self.ex.hu, "gain-offset-noise", rng)
        self.assertFalse(np.array_equal(noisy, aug))


if __name__ == "__main__":
    unittest.main()

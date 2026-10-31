"""The blocks (autoanatomist/blocks.py), the anneal in absolute steps (ladder.Anneal) and the
calibration of the spread (autoanatomist/calibrate.py).

    python -m unittest tests.test_autoanatomist_blocks -v          # from the repository's root

The defaults are the smoke run's numbers, held to train.py's, smoke.py's, ladder.py's, gates.py's,
model.py's and optax.adamw's constants, which the blocks spell as literals so as to import no JAX, and
the architecture's choices are model.ARCHITECTURES' names;
every spelling of one configuration has one digest and a word is refused in words; the anneal over
a run's length gives Schedule's (w, lambda) to the bit, each kind places the ramps as it says, and a
continued anneal carries on from where it stood to the ends by the step named; the calibration's
scale recovers a known factor and its quantile covers what it promises on the set it was fit on.
"""
from __future__ import annotations

import inspect
import math
import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

try:
    import jax  # noqa: F401
    HAVE_JAX = True
except ImportError:                                               # pragma: no cover
    HAVE_JAX = False


class TheBlocks(unittest.TestCase):
    def test_nothing_named_is_the_defaults_and_every_key_round_trips(self):
        from autoanatomist import blocks as B
        self.assertEqual(B.parse([]), B.DEFAULTS)
        self.assertEqual(B.parse(None), B.DEFAULTS)
        self.assertEqual(B.parse(B.DEFAULTS.words()), B.DEFAULTS)
        self.assertEqual(len(B.DEFAULTS.words()), len(B.TABLE))
        self.assertEqual(B.DEFAULTS.changed(), [])
        b = B.parse("optimiser=sgd lr=0.00100 clip=1 warmup=5 batch=3 knee=1 spread_floor=0.25 w_naming=0 naming=off "
                    "schedule=w-first lam_span=0.1:0.5 w_span=0.5:0.9 lam_fixed=0.5 w_fixed=0 anneal=900 "
                    "intensity=gain-offset-noise normalise=clip-zscore widths=8:16:32 groups=4 blur_mm=2 "
                    "threshold_hu=150 threshold_width_hu=30 calibrate=quantile coverage=0.9 seed=3 architecture=plain-unet")
        self.assertEqual(B.parse(b.words()), b)
        self.assertEqual(b.architecture, "plain-unet")
        self.assertIn("architecture=plain-unet", b.words())
        self.assertIn("lr=0.001", b.words())                         # spelled canonically, not as written
        self.assertIn("naming=off", b.words())
        self.assertIn("widths=8:16:32", b.words())
        self.assertEqual(b.lam_span, (0.1, 0.5))
        self.assertEqual(b.widths, (8, 16, 32))
        self.assertFalse(b.naming)
        self.assertEqual(B.parse({"lr": "0.001"}).lr, 0.001)
        self.assertEqual(sorted(b.changed()), sorted(set(b.words()) - set(B.DEFAULTS.words())))

    def test_one_configuration_has_one_digest(self):
        from autoanatomist import blocks as B
        a = B.parse(["lr=0.002", "knee=2"])
        self.assertEqual(a.digest(), B.DEFAULTS.digest())
        self.assertNotEqual(B.parse("lr=0.0021").digest(), B.DEFAULTS.digest())
        self.assertNotEqual(B.parse("naming=off").digest(), B.DEFAULTS.digest())
        self.assertEqual(len(a.digest()), 64)
        self.assertEqual(a.record()["digest"], a.digest())
        self.assertEqual(B.parse("lr=0.0021").changed(), ["lr=0.0021"])

    def test_refusals_in_words(self):
        from autoanatomist import blocks as B
        for words, said in [("foo=1", "no block is named 'foo'"), ("lr", "KEY=VALUE"), ("lr=1 lr=2", "named twice"),
                            ("optimiser=rmsprop", "adamw, adam or sgd"), ("naming=yes", "on or off"),
                            ("batch=2.5", "whole number"), ("batch=0", "at least 1"), ("lr=fast", "takes a number"),
                            ("lr=0", "above 0.0"), ("lr=nan", "finite"), ("coverage=1", "below 1.0"),
                            ("lam_fixed=1.5", "at most 1.0"), ("lam_span=0.5:0.4", "0 <= a < b <= 1"),
                            ("lam_span=0.5", "0 <= a < b <= 1"), ("widths=8:16", "three whole numbers"),
                            ("widths=8:0:16", "at least 1"), ("schedule=cosine", "lambda-then-w, joint, w-first, fixed, cyclic or adaptive"),
                            ("architecture=unet", "residual-unet, plain-unet or probe")]:
            with self.assertRaises(ValueError, msg=words) as cm:
                B.parse(words)
            self.assertIn(said, str(cm.exception), words)

    def test_the_table_describes_itself(self):
        from autoanatomist import blocks as B
        text = B.describe()
        for k in B.TABLE:
            self.assertIn(k.name + " (", text)
        self.assertIn("default adamw", text)
        self.assertIn("default 16:32:64", text)
        self.assertIn("default residual-unet", text)
        self.assertEqual(len(B.TABLE), 40)                      # 31 at the first count, then w_mask, objective and w_name,
                                                                # then the second screen's six (tests/test_autoanatomist_arms.py)
        self.assertEqual(B.DEFAULTS.weights(), {"landmark": 1.0, "spread": 0.1, "value": 1.0, "feature": 1.0, "naming": 0.1,
                                                 "mask": 1.0, "name": 0.1})
        self.assertEqual(B.DEFAULTS.rungs(), {"bone_hu": 200.0, "width_hu": 60.0, "blur_max_mm": 4.0})


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheDefaultsAreTheSmokeRun(unittest.TestCase):
    def test_against_the_modules_constants(self):
        import optax
        from autoanatomist import blocks as B
        from autoanatomist import gates, ladder, smoke, train
        from autoanatomist.model import ARCHITECTURES, DEFAULT_ARCHITECTURE, Config
        d = B.DEFAULTS
        self.assertEqual(d.weights(), train.LOSS_WEIGHTS)
        self.assertEqual(d.knee, train.HUBER_KNEE_MM)
        self.assertEqual(d.spread_floor, train.SPREAD_FLOOR_MM)
        self.assertEqual(d.lr, smoke.LR)
        self.assertEqual(d.batch, smoke.SPINES_PER_BATCH)
        s = ladder.Schedule(10)
        self.assertEqual((d.lam_span, d.w_span), (s.lam_span, s.w_span))
        self.assertEqual(d.blur_mm, ladder.BLUR_MAX_MM)
        self.assertEqual(d.threshold_width_hu, ladder.THRESHOLD_WIDTH_HU)
        self.assertEqual(d.threshold_hu, gates.BONE_HU)
        self.assertEqual((d.widths, d.groups, d.normalise), (Config().widths, Config().groups, Config().normalise))
        self.assertEqual(d.architecture, Config().architecture)
        self.assertEqual(d.architecture, DEFAULT_ARCHITECTURE)
        self.assertEqual(B.KEYS["architecture"].choices, tuple(ARCHITECTURES))
        self.assertEqual(d.weight_decay, inspect.signature(optax.adamw).parameters["weight_decay"].default)
        self.assertEqual(d.seed, smoke.SEEDS["run"])


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheAnneal(unittest.TestCase):
    def test_the_default_kind_is_the_schedule_to_the_bit(self):
        from autoanatomist import ladder as LD
        for steps in (1, 2, 3, 150):
            s, a = LD.Schedule(steps), LD.Anneal(steps=steps)
            for step in range(steps + 2):
                self.assertEqual(a.at(step), s.at(step), (steps, step))
        self.assertEqual(LD.Anneal(steps=150).at(0), (1.0, 0.0))
        self.assertEqual(LD.Anneal(steps=150).at(149), (0.0, 1.0))

    def test_each_kind_places_the_ramps_as_it_says(self):
        from autoanatomist import ladder as LD
        lam_span, w_span = (0.1, 0.4), (0.6, 0.9)
        ramp = LD.Schedule.ramp
        n = 101
        joint = LD.Anneal(kind="joint", steps=n, lam_span=lam_span, w_span=w_span)
        first = LD.Anneal(kind="w-first", steps=n, lam_span=lam_span, w_span=w_span)
        fixed = LD.Anneal(kind="fixed", steps=n, lam_fixed=0.3, w_fixed=0.7)
        for step in range(n):
            t = step / (n - 1)
            self.assertEqual(joint.at(step), (1.0 - ramp(t, lam_span), ramp(t, lam_span)))
            self.assertEqual(first.at(step), (1.0 - ramp(t, lam_span), ramp(t, w_span)))
            self.assertEqual(fixed.at(step), (0.7, 0.3))
        self.assertEqual(first.at(50), (0.0, 0.0))                 # w is down before lambda has begun
        with self.assertRaises(ValueError):
            LD.Anneal(kind="cosine")
        with self.assertRaises(ValueError):
            LD.Anneal(steps=0)

    def test_a_continued_anneal_carries_on_to_the_ends(self):
        from autoanatomist import ladder as LD
        a = LD.Anneal(steps=100)
        w0, lam0 = a.at(40)
        self.assertTrue(0.0 < lam0 < 1.0 and w0 == 1.0)
        c = a.continued(40, 120)
        self.assertEqual(c.at(40), (w0, lam0))
        self.assertEqual(c.at(120), (0.0, 1.0))
        self.assertEqual(c.at(130), (0.0, 1.0))
        ws, lams = zip(*(c.at(s) for s in range(40, 121)))
        self.assertTrue(all(b <= a for a, b in zip(ws, ws[1:])))
        self.assertTrue(all(b >= a for a, b in zip(lams, lams[1:])))
        self.assertEqual(c.at(80), (w0 + (0.0 - w0) * 0.5, lam0 + (1.0 - lam0) * 0.5))
        again = c.continued(100, 200)
        self.assertEqual(again.at(100), c.at(100))
        self.assertEqual(again.at(200), (0.0, 1.0))
        fixed = LD.Anneal(kind="fixed", steps=10, lam_fixed=0.3, w_fixed=0.7).continued(5, 15)
        self.assertEqual(fixed.at(5), (0.7, 0.3))
        self.assertEqual(fixed.at(15), (0.0, 1.0))
        with self.assertRaises(ValueError):
            a.continued(40, 40)
        self.assertEqual(LD.Anneal.from_record(c.as_record()), c)
        self.assertEqual(LD.Anneal.from_record(a.as_record()), a)


class TheCalibration(unittest.TestCase):
    def test_scale_recovers_the_factor_and_quantile_covers_what_it_promises(self):
        from autoanatomist import calibrate as C
        rng = np.random.default_rng(0)
        n, m = 4000, 3
        sigma = rng.uniform(0.5, 5.0, (n, m))
        true = np.array([0.5, 1.0, 2.5])
        error = rng.normal(0.0, 1.0, (n, m)) * true * C.floored(sigma)
        error[0, 1] = np.nan                                       # a value the oracle did not give
        np.testing.assert_allclose(C.fit(error, sigma, "scale"), true, rtol=0.05)
        np.testing.assert_array_equal(C.fit(error, sigma, "none"), np.ones(m))
        from statistics import NormalDist
        for cov in (0.68, 0.9):
            f = C.fit(error, sigma, "quantile", cov)
            spread = C.apply(sigma, f)
            k = NormalDist().inv_cdf((1.0 + cov) / 2.0)             # the Gaussian interval at the coverage
            got = [np.nanmean(np.abs(error[:, j]) <= k * spread[:, j]) for j in range(m)]
            np.testing.assert_allclose(got, cov, atol=0.01)
            self.assertAlmostEqual(C.coverage_at(error, spread, k), cov, delta=0.01)
        quantile = C.apply(sigma, C.fit(error, sigma, "quantile", 0.68))
        self.assertAlmostEqual(C.coverage_at(error, quantile, 1.0), 0.68, delta=0.015)   # one spread at the default
        scaled = C.apply(sigma, C.fit(error, sigma, "scale"))
        self.assertAlmostEqual(C.coverage_at(error, scaled, 1.0), 0.683, delta=0.02)
        self.assertAlmostEqual(C.coverage_at(error, scaled, 2.0), 0.954, delta=0.02)
        self.assertTrue(np.all(C.floored(np.zeros(3)) == C.Z_FLOOR_MM))
        rec = C.record("quantile", 0.9, f, ("a", "b", "c"), n)
        self.assertEqual(set(rec), {"kind", "coverage", "rows", "factors"})
        self.assertEqual(set(rec["factors"]), {"a", "b", "c"})
        with self.assertRaises(ValueError):
            C.fit(error, sigma, "temperature")
        self.assertTrue(math.isnan(C.coverage_at(np.full((2, 1), np.nan), np.ones((2, 1)))))


if __name__ == "__main__":
    unittest.main()

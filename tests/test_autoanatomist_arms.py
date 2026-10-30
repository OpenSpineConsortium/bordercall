"""The second screen's four arms: schedule=cyclic, schedule=adaptive, ladder=overlapping and
restraint=abf (ladder.py, train.py, session.py, blocks.py), on the session tests' tiny phantoms.

    python -m unittest tests.test_autoanatomist_arms -v        # from the repository's root, in the venv

Every arm ends where every anneal ends, lambda 1 and w 0, and none touches a run that does not
name it: the rungs in turn are rung's own arithmetic to the bit, the defaults of the new blocks are
the ladder's constants, and with no sample yet the restraint's first step is the unrestrained
step. The cyclic anneal is lambda-then-w twice in half the steps, back to its cycle's values
between; the adaptive controller makes the moves its rule says, never leaves [0, 1], and the
session holds lambda at or above the floor, checks on the batch just trained and saves and
restores the controller to the bit; overlapping rungs move together where their spans meet and
give the same channels as the rungs in turn at both ends; the restraint's weight is zero at both
ends, its gradient on a variable is its bin's mean force, its estimate is ABF's running and then
moving mean, and a session saved mid-run and trained on is the run straight, to the bit.
"""
from __future__ import annotations

import math
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
TINY = "widths=4:8:8"
MASK = "objective=mask naming=off"


def tiny_config():
    from autoanatomist.model import Config
    return Config(widths=(4, 8, 8), shape=(16, 20, 12), spacing=6.0)


def session(words):
    from autoanatomist import blocks as B
    from autoanatomist import session as S
    cfg = tiny_config()
    return S.Session.new(B.parse(words), keys=cfg.keys, shape=cfg.shape, spacing=cfg.spacing)


def same_rows(test, a, b):
    test.assertEqual(len(a), len(b))
    for x, y in zip(a, b):
        test.assertEqual(set(x), set(y))
        for k in x:
            if k != "seconds":
                test.assertEqual(x[k], y[k], (k, x, y))


def same_params(test, a, b):
    from autoanatomist import session as S
    mine, theirs = S.flat_arrays(a, "model"), S.flat_arrays(b, "model")
    test.assertEqual(set(mine), set(theirs))
    for k in mine:
        np.testing.assert_array_equal(mine[k], theirs[k], k)


class TheBlocks(unittest.TestCase):
    def test_the_arms_are_words_and_their_defaults_change_nothing(self):
        from autoanatomist import blocks as B
        b = B.parse("schedule=cyclic cycle_lam=0.4 cycle_w=0.2 adapt_every=10 ladder=overlapping restraint=abf abf_weight=0.5")
        self.assertEqual(B.parse(b.words()), b)
        self.assertEqual(sorted(b.changed()), sorted(["schedule=cyclic", "cycle_lam=0.4", "cycle_w=0.2", "adapt_every=10",
                                                      "ladder=overlapping", "restraint=abf", "abf_weight=0.5"]))
        self.assertEqual(B.DEFAULTS.rungs(), {"bone_hu": 200.0, "width_hu": 60.0, "blur_max_mm": 4.0})
        self.assertEqual(B.parse("ladder=overlapping").rungs()["rung_span"], 0.5)
        self.assertEqual(B.parse("ladder=together").rungs()["rung_span"], 1.0)
        self.assertEqual(B.parse("schedule=adaptive").schedule, "adaptive")
        for words, said in [("ladder=sideways", "in-turn, overlapping or together"), ("restraint=on", "off or abf"),
                            ("abf_weight=-1", "at least 0.0"), ("adapt_every=0", "at least 1"),
                            ("cycle_lam=1.5", "at most 1.0"), ("schedule=cosine", "fixed, cyclic or adaptive")]:
            with self.assertRaises(ValueError, msg=words) as cm:
                B.parse(words)
            self.assertIn(said, str(cm.exception), words)
        text = B.describe()
        for name in ("cycle_lam", "cycle_w", "adapt_every", "ladder", "restraint", "abf_weight"):
            self.assertIn(name + " (", text)

    @unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
    def test_the_defaults_are_the_ladders_constants(self):
        from autoanatomist import blocks as B
        from autoanatomist import ladder as LD
        d = B.DEFAULTS
        self.assertEqual((d.cycle_lam, d.cycle_w, d.adapt_every), (LD.CYCLE_LAM, LD.CYCLE_W, LD.ADAPT_EVERY))
        self.assertEqual(B.RUNG_SPANS, LD.RUNG_SPANS)
        self.assertEqual(B.KEYS["ladder"].choices, tuple(LD.RUNG_SPANS))
        self.assertEqual(B.KEYS["schedule"].choices, LD.KINDS)
        self.assertEqual((d.ladder, d.restraint), ("in-turn", "off"))


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheRungs(unittest.TestCase):
    def test_in_turn_is_the_old_arithmetic_and_the_spans_place_each_rung(self):
        import jax.numpy as jnp
        from autoanatomist import ladder as LD
        lams = jnp.linspace(0.0, 1.0, 101)
        for k in range(3):
            np.testing.assert_array_equal(LD.rung(lams, k), LD.smoothstep(3.0 * lams - k))
            np.testing.assert_allclose(LD.rung(lams, k, 1.0 / 3.0), LD.rung(lams, k), atol=1e-6)
            np.testing.assert_array_equal(LD.rung(lams, k, 1.0), LD.smoothstep(lams))     # together: all of lambda
        half = LD.RUNG_SPANS["overlapping"]
        for k, (start, end) in enumerate([(0.0, 0.5), (0.25, 0.75), (0.5, 1.0)]):
            self.assertEqual(float(LD.rung(start, k, half)), 0.0)
            self.assertEqual(float(LD.rung(end, k, half)), 1.0)
            self.assertAlmostEqual(float(LD.rung((start + end) / 2.0, k, half)), 0.5, places=6)
        self.assertTrue(0.0 < float(LD.rung(0.4, 0, half)) < 1.0 and 0.0 < float(LD.rung(0.4, 1, half)) < 1.0)

    def test_the_channels_are_the_same_at_both_ends_whatever_the_span(self):
        import jax.numpy as jnp
        from autoanatomist import ladder as LD
        from autoanatomist import rows as R
        ex = R.examples_for(ROWS, tiny_config())
        masks, hu = jnp.asarray(ex.masks[:2]), jnp.asarray(ex.hu[:2])
        for lam in (0.0, 1.0):
            base = np.asarray(LD.degrade(masks, hu, lam, spacing_mm=6.0))
            np.testing.assert_array_equal(np.asarray(LD.degrade(masks, hu, lam, spacing_mm=6.0, rung_span=None)), base)
            for span in (0.5, 1.0):
                np.testing.assert_allclose(np.asarray(LD.degrade(masks, hu, lam, spacing_mm=6.0, rung_span=span)), base,
                                           atol=1e-6, err_msg=str((lam, span)))
        mid = [np.asarray(LD.degrade(masks, hu, 0.4, spacing_mm=6.0, rung_span=s)) for s in (None, 0.5)]
        self.assertGreater(float(np.max(np.abs(mid[0] - mid[1]))), 1e-3)


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheCyclicAnneal(unittest.TestCase):
    def test_two_passes_of_lambda_then_w_and_back_between(self):
        from autoanatomist import ladder as LD
        n = 1001
        c = LD.Anneal(kind="cyclic", steps=n)
        base = LD.Anneal(steps=n)
        w_knots, lam_knots = c.cycle_knots()
        back, on = w_knots[2][0], w_knots[3][0]
        self.assertAlmostEqual(back, 0.425)
        self.assertAlmostEqual(on, 0.575)
        self.assertEqual(c.at(0), (1.0, 0.0))
        self.assertEqual(c.at(n - 1), (LD.W_END, LD.LAMBDA_END))
        for step in range(0, round(back * (n - 1)) + 1, 5):          # the first pass: lambda-then-w at twice the pace
            for got, want in zip(c.at(step), base.at(2 * step)):
                self.assertAlmostEqual(got, want, places=9)
        for step in range(round(on * (n - 1)), n, 5):                 # the second: the same from the cycle's values
            bw, blam = base.at(2 * step - (n - 1))
            w, lam = c.at(step)
            self.assertAlmostEqual(w, LD.CYCLE_W * bw, places=9)
            self.assertAlmostEqual(lam, LD.CYCLE_LAM + (1.0 - LD.CYCLE_LAM) * blam, places=9)
        for share, want in ((back, (LD.W_END, LD.LAMBDA_END)), (on, (LD.CYCLE_W, LD.CYCLE_LAM))):
            for got, value in zip(c.at(round(share * (n - 1))), want):
                self.assertAlmostEqual(got, value, places=9)
        path = [c.at(s) for s in range(n)]
        jumps = max(max(abs(a[0] - b[0]), abs(a[1] - b[1])) for a, b in zip(path, path[1:]))
        self.assertLess(jumps, 0.02)                                   # half cosines, no step changes
        for knots in (w_knots, lam_knots):
            self.assertTrue(all(a[0] <= b[0] for a, b in zip(knots, knots[1:])))
        other = LD.Anneal(kind="cyclic", steps=n, cycle_lam=0.2, cycle_w=0.6)
        for got, value in zip(other.at(round(on * (n - 1))), (0.6, 0.2)):
            self.assertAlmostEqual(got, value, places=9)
        self.assertEqual(LD.Anneal.from_record(other.as_record()), other)
        old = base.as_record()
        del old["cycle_lam"], old["cycle_w"]                           # a session.json written before the cycle's numbers
        self.assertEqual(LD.Anneal.from_record(old), base)

    def test_along_is_a_half_cosine_between_knots(self):
        from autoanatomist import ladder as LD
        knots = ((0.2, 1.0), (0.6, 3.0), (0.6, 3.0), (0.8, 2.0))
        self.assertEqual(LD.along(0.0, knots), 1.0)
        self.assertEqual(LD.along(1.0, knots), 2.0)
        self.assertAlmostEqual(LD.along(0.4, knots), 2.0)
        self.assertAlmostEqual(LD.along(0.7, knots), 2.5)
        self.assertEqual(LD.along(0.6, knots), 3.0)


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheAdaptiveAnneal(unittest.TestCase):
    def test_its_clock_floor_and_moves(self):
        from autoanatomist import ladder as LD
        n = 101
        a = LD.Anneal(kind="adaptive", steps=n)
        base = LD.Anneal(steps=n)
        ramp = LD.Schedule.ramp
        floor = a.floor_span()
        self.assertEqual(floor[0], 0.15)
        self.assertAlmostEqual(floor[1], 0.65)
        for step in range(n):
            self.assertEqual(a.at(step), (base.at(step)[0], ramp(step / (n - 1), floor)))
        self.assertFalse(a.adapting(14))
        self.assertTrue(a.adapting(15))
        self.assertFalse(a.continued(40, 80).adapting(50))
        self.assertFalse(base.adapting(50))
        self.assertAlmostEqual(a.nominal(15, 0.0, 10), 1.0 / 4.0)          # (55 - 15) / 10 checks left
        self.assertAlmostEqual(a.nominal(54, 0.6, 10), 0.4)                 # less than one check left: the rest
        self.assertAlmostEqual(a.nominal(80, 0.9, 10), 0.1)                 # past lam_span: the rest at once

    def test_the_controller_moves_as_its_rule_says(self):
        from autoanatomist import ladder as LD
        lo, hi = LD.ADAPT_GAIN
        a = LD.adapt(LD.Adapt(), now=0.0, rise=0.0, slope=2.0, nominal=0.1)
        self.assertEqual((a.lam, a.last, a.pace, a.checks), (0.1, 0.0, 2.0, 1))        # the first: the even move
        b = LD.adapt(a, now=0.1, rise=0.1, slope=2.0, nominal=0.1)                        # rose as the slope promised
        self.assertAlmostEqual(b.lam, 0.2)
        flat = LD.adapt(b, now=0.2, rise=0.0, slope=0.0, nominal=0.1)
        self.assertAlmostEqual(flat.lam, 0.2 + hi * 0.1)                                 # flat: the most
        steep = LD.adapt(b, now=0.2, rise=0.0, slope=100.0, nominal=0.1)
        self.assertAlmostEqual(steep.lam, 0.2 + lo * 0.1)                                # steep: the least
        self.assertAlmostEqual(steep.pace, (2.0 + 2.0 + 100.0) / 3.0)
        jumped = LD.adapt(b, now=0.2, rise=LD.ADAPT_JUMP * b.pace * 0.1 + 1e-6, slope=1.0, nominal=0.1)
        self.assertAlmostEqual(jumped.lam, 0.15)                                         # half the move back
        self.assertEqual(jumped.last, 0.2)
        held = LD.adapt(b, now=0.2, rise=LD.ADAPT_JUMP * b.pace * 0.1 - 1e-6, slope=2.0, nominal=0.1)
        self.assertGreater(held.lam, 0.2)
        top = LD.adapt(b, now=0.95, rise=0.0, slope=0.0, nominal=0.2)
        self.assertEqual(top.lam, 1.0)
        self.assertEqual(LD.Adapt.from_record(jumped.as_record()), jumped)


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheRestraint(unittest.TestCase):
    def test_its_weight_bins_and_gradient(self):
        import jax
        import jax.numpy as jnp
        from autoanatomist import train as T
        self.assertEqual(float(T.restraint_weight(0.0)), 0.0)
        self.assertAlmostEqual(float(T.restraint_weight(1.0)), 0.0, places=6)
        self.assertAlmostEqual(float(T.restraint_weight(0.5)), 1.0, places=6)
        bins = np.asarray(T.bin_of(jnp.array([[-0.5], [0.0], [0.019], [0.021], [0.999], [7.0]]), "mask"))
        self.assertEqual(bins[:, 0].tolist(), [0, 0, 0, 1, 49, 49])
        self.assertEqual(np.asarray(T.bin_of(jnp.array([[-200.0, 41.5, 500.0]]), "landmarks")).tolist(), [[0, 241, 399]])
        bias = jnp.zeros((2, 400)).at[0, 241].set(3.0).at[1, 230].set(-2.0)
        cv = jnp.array([[41.5, 30.2], [41.9, 30.7]])
        grad = jax.grad(lambda c: T.restraint_term(c, bias, 0.25, "landmarks"))(cv)
        weight = float(T.restraint_weight(0.25))
        np.testing.assert_allclose(np.asarray(grad), -weight * np.array([[3.0, -2.0], [3.0, -2.0]]) / 4.0, rtol=1e-6)
        self.assertAlmostEqual(float(T.restraint_term(cv, bias, 0.0, "landmarks")), 0.0)

    def test_the_estimate_is_abfs_running_then_moving_mean(self):
        from autoanatomist import train as T
        f = T.Forces.empty("mask", 1)
        scale = T.ABF_SCALE["mask"]
        cv, ok = np.full((T.ABF_FULL, 1), 0.31), np.ones((T.ABF_FULL, 1), bool)
        f.update(cv[:40], cv[:40] + 0.01, ok[:40])
        self.assertEqual(int(f.count[0, 15]), 40)
        self.assertAlmostEqual(float(f.mean[0, 15]), 0.01 / scale ** 2)
        self.assertAlmostEqual(float(f.bias()[0, 15]), 0.4 * 0.01 / scale ** 2, places=4)   # 40 of ABF_FULL samples
        f.update(cv[:60], cv[:60] + 0.01, ok[:60])
        self.assertAlmostEqual(float(f.bias()[0, 15]), 0.01 / scale ** 2, places=4)
        f.update(cv[:1], cv[:1] + 0.03, ok[:1])                     # past ABF_FULL: a moving mean of weight 1 / ABF_FULL
        self.assertAlmostEqual(float(f.mean[0, 15]), (0.01 + (0.03 - 0.01) / T.ABF_FULL) / scale ** 2)
        g = T.Forces.empty("landmarks", 2)
        g.update(np.array([[40.5, 10.0]]), np.array([[42.0, 0.0]]), np.array([[True, False]]))     # off a bin's edge
        self.assertEqual((int(g.count.sum()), int(g.count[0, 240])), (1, 1))     # a value the oracle did not give adds nothing
        self.assertEqual(float(g.mean[0, 240]), 1.5 / T.ABF_SCALE["landmarks"] ** 2)


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheArmsInASession(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from autoanatomist import rows as R
        cls.ex = R.examples_for(ROWS, tiny_config())

    def test_the_restraints_first_step_is_the_unrestrained_step(self):
        for objective in (MASK, ""):
            plain, held = session("%s %s anneal=8" % (TINY, objective)), session("%s %s anneal=8 restraint=abf" % (TINY, objective))
            a, b = plain.train(self.ex, 1), held.train(self.ex, 1)
            self.assertEqual(b[0]["restraint"], 0.0)
            self.assertEqual(a[0]["total"], b[0]["total"])
            same_params(self, plain.model, held.model)
            given = len(self.ex.hu) if objective else int(np.sum(np.isfinite(self.ex.values)))
            self.assertEqual(int(held.forces.count.sum()), given)      # one batch of both phantoms: every crop's samples

    def test_each_arm_ends_at_lambda_1_and_w_0_with_finite_losses(self):
        for objective in (MASK, ""):
            for arm in ("schedule=cyclic", "schedule=adaptive adapt_every=2", "ladder=overlapping", "restraint=abf"):
                s = session("%s %s %s" % (TINY, objective, arm))
                rows = s.train(self.ex, 12)
                self.assertEqual((rows[-1]["w"], rows[-1]["lam"]), (0.0, 1.0), (objective, arm))
                self.assertEqual(rows[0]["lam"], 0.0)
                for row in rows:
                    self.assertTrue(all(math.isfinite(v) for k, v in row.items() if k != "seconds"), (objective, arm, row))

    def test_the_adaptive_session_stays_on_or_above_its_floor_and_checks(self):
        s = session("%s %s schedule=adaptive adapt_every=2 anneal=40" % (TINY, MASK))
        rows = s.train(self.ex, 40)
        self.assertGreater(s.adapt.checks, 3)
        for row in rows:
            self.assertGreaterEqual(row["lam"], s.anneal.at(row["step"])[1])
            self.assertEqual(row["w"], s.anneal.at(row["step"])[0])
        self.assertTrue(any(row["lam"] > s.anneal.at(row["step"])[1] + 1e-3 for row in rows))   # the checks moved it
        self.assertEqual(s.position(), (0.0, 1.0))

    def test_saved_mid_run_and_trained_on_is_the_run_straight(self):
        for words in ("%s %s schedule=adaptive adapt_every=2 lam_span=0:0.5 anneal=10" % (TINY, MASK),
                      "%s %s restraint=abf lam_span=0:0.5 anneal=10" % (TINY, MASK),
                      "%s schedule=cyclic ladder=overlapping anneal=10" % TINY):
            straight = session(words)
            rows = straight.train(self.ex, 10)
            s = session(words)
            first = s.train(self.ex, 5)
            with tempfile.TemporaryDirectory() as d:
                s.save(d)
                t = type(s).load(d)
            self.assertEqual(t.adapt, s.adapt, words)
            if s.forces is not None:
                np.testing.assert_array_equal(t.forces.mean, s.forces.mean)
                np.testing.assert_array_equal(t.forces.count, s.forces.count)
            same_rows(self, first + t.train(self.ex, 5), rows)
            same_params(self, t.model, straight.model)


if __name__ == "__main__":
    unittest.main()

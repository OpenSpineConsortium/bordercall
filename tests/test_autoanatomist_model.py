"""The network (model.py) and the training path (train.py, smoke.py) of autoanatomist/, on sizes a
test can afford: a crop of 16 by 20 by 12 voxels and two phantoms of three levels.

    python -m unittest discover -s tests -v          # from the repository's root, in the venv

The soft-argmax reads a one-hot heatmap back as its voxel's position with no spread and a
two-voxel heatmap as their midpoint; the delta method gives sqrt(2) sigma for a length between
two points of isotropic spread sigma; the network's values are the measurements' rules applied
to its points, its CT-only path is the fused pass at w 0 to the bit, and its outputs have the
shapes the interface promises; one training step lowers the loss it is given and three steps run
through the schedule with finite losses, the error curve E(lambda) and its derivative are finite
and E is the same function at lambda 0 and 1 as degrade's ends give, evaluate reports what it
promises, timing measures the CT-only path, and a reading made from the network's points draws.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

try:
    import jax
    import jax.numpy as jnp
    from flax import nnx
    HAVE_JAX = True
except ImportError:                                               # pragma: no cover
    HAVE_JAX = False


def tiny_config():
    from autoanatomist.model import Config
    return Config(widths=(4, 8, 8), shape=(16, 20, 12), spacing=6.0)


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheHeatmapReading(unittest.TestCase):
    def test_soft_argmax_on_known_heatmaps(self):
        from autoanatomist import model as Mo
        shape, spacing, heat = (16, 20, 12), 6.0, (8, 10, 6)
        grid = Mo.heatmap_grid(shape, spacing, heat)
        self.assertEqual(grid.shape, (np.prod(heat), 3))
        np.testing.assert_allclose(grid.mean(0), 0.0, atol=1e-9)
        logits = np.full((1,) + heat + (2,), -1e4, np.float32)
        logits[0, 2, 3, 1, 0] = 0.0                             # one voxel for the first landmark
        logits[0, 2, 3, 1, 1] = 0.0                             # two voxels, equal, for the second
        logits[0, 6, 3, 1, 1] = 0.0
        mean, cov = Mo.soft_argmax(jnp.asarray(logits), grid)
        at = grid.reshape(heat + (3,))
        np.testing.assert_allclose(np.asarray(mean[0, 0]), at[2, 3, 1], atol=1e-5)
        np.testing.assert_allclose(np.asarray(cov[0, 0]), 0.0, atol=1e-4)
        np.testing.assert_allclose(np.asarray(mean[0, 1]), 0.5 * (at[2, 3, 1] + at[6, 3, 1]), atol=1e-5)
        half = 0.5 * (at[6, 3, 1] - at[2, 3, 1])
        np.testing.assert_allclose(np.asarray(cov[0, 1]), np.outer(half, half), atol=1e-3)

    def test_the_delta_method_on_a_length(self):
        from autoanatomist import model as Mo
        keys = ("endplate",)
        points = jnp.asarray(np.array([[[0.0, 0.0, 0.0], [30.0, 0.0, 0.0]]]))
        sigma = 1.7
        cov = jnp.asarray(np.broadcast_to(sigma ** 2 * np.eye(3), (1, 2, 3, 3)))
        got = Mo.value_sigma(points, cov, keys)
        np.testing.assert_allclose(np.asarray(got), [[np.sqrt(2.0) * sigma]], rtol=1e-5)


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheNetwork(unittest.TestCase):
    def test_shapes_values_and_the_ct_only_path(self):
        from autoanatomist import model as Mo
        from autoanatomist import specs as S
        cfg = tiny_config()
        m = Mo.Model(cfg, nnx.Rngs(0))
        rng = np.random.default_rng(0)
        hu = jnp.asarray(rng.normal(100.0, 300.0, (2,) + cfg.shape + (1,)), jnp.float32)
        masks = jnp.asarray(rng.random((2,) + cfg.shape + (2,)), jnp.float32)
        out = m(hu, masks, 0.5)
        K, M = cfg.n_landmarks, len(cfg.keys)
        self.assertEqual(out["points"].shape, (2, K, 3))
        self.assertEqual(out["cov"].shape, (2, K, 3, 3))
        self.assertEqual(out["values"].shape, (2, M))
        self.assertEqual(out["sigma"].shape, (2, M))
        self.assertEqual(len(out["f_ct"]), 3)
        np.testing.assert_allclose(np.asarray(out["values"]), S.values(np.asarray(out["points"]), cfg.keys), rtol=1e-5)
        eig = np.linalg.eigvalsh(np.asarray(out["cov"]))
        self.assertTrue(np.all(eig > -1e-4))
        self.assertTrue(bool(jnp.isfinite(out["sigma"]).all()))
        alone = m.ct_only(hu)
        fused = m(hu, masks, 0.0)
        np.testing.assert_array_equal(np.asarray(alone["points"]), np.asarray(fused["points"]))
        np.testing.assert_array_equal(np.asarray(alone["values"]), np.asarray(fused["values"]))


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheTraining(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from autoanatomist import train as T
        cls.cfg = tiny_config()
        cls.ex = T.make_examples(cls.cfg, n_spines=2, count=3, seed=1, spacing_mm=2.0, keep=True)

    def test_the_examples(self):
        ex, cfg = self.ex, self.cfg
        self.assertEqual(len(ex), 6)
        self.assertEqual(ex.hu.shape, (6,) + cfg.shape + (1,))
        self.assertEqual(ex.masks.shape, (6,) + cfg.shape + (2,))
        self.assertEqual(ex.targets.shape, (6, cfg.n_landmarks, 3))
        self.assertEqual([len(g) for g in ex.spines()], [3, 3])
        self.assertTrue(np.isfinite(ex.targets).all())
        self.assertTrue(np.isfinite(ex.values).all())
        self.assertEqual(len(ex.frames), 6)
        self.assertEqual(len(ex.phantoms), 2)

    def test_a_step_lowers_the_loss_and_a_run_records_the_schedule(self):
        from autoanatomist import train as T
        ex, cfg = self.ex, self.cfg
        run = T.train(ex, cfg, steps=3, spines_per_batch=2, seed=0)
        self.assertEqual(len(run.record), 3)
        self.assertEqual((run.record[0]["w"], run.record[0]["lam"]), (1.0, 0.0))
        self.assertEqual((run.record[-1]["w"], run.record[-1]["lam"]), (0.0, 1.0))
        for row in run.record:
            for k in ("total", "landmark", "spread", "value", "feature", "naming", "distance_mm"):
                self.assertTrue(np.isfinite(row[k]), (k, row))
        batch = T.batch_of(ex, np.arange(len(ex)))
        nm = __import__("autoanatomist.naming", fromlist=["prepare"]).prepare(cfg.keys, n_bodies=3)
        import optax
        model = T.Model(cfg, nnx.Rngs(1))
        opt = nnx.Optimizer(model, optax.adamw(2e-3), wrt=nnx.Param)
        step = T.make_step(nm, 2)
        before = float(T.losses(model, batch, 1.0, 0.0, nm, 2)[0])
        step(model, opt, batch, jnp.float32(1.0), jnp.float32(0.0))
        after = float(T.losses(model, batch, 1.0, 0.0, nm, 2)[0])
        self.assertLess(after, before)

    def test_evaluate_error_curve_timing_and_drawing(self):
        from autoanatomist import ladder as LD
        from autoanatomist import render as RD
        from autoanatomist import train as T
        ex, cfg = self.ex, self.cfg
        model = T.Model(cfg, nnx.Rngs(2))
        res = T.evaluate(model, ex)
        for k in ("distance_mm", "value_mae", "sigma_mm", "named_right", "named_right_values_alone",
                  "named_right_from_oracle"):
            self.assertIn(k, res)
        self.assertEqual(set(res["value_mae"]), set(cfg.keys))
        batch = T.batch_of(ex, np.arange(len(ex)))
        E, dE = T.error_curve(model, batch, [0.0, 0.5, 1.0])
        self.assertTrue(np.isfinite(E).all() and np.isfinite(dE).all())
        from autoanatomist import gates as GT
        bone = GT.soft_threshold(batch["hu"][..., 0], GT.BONE_HU, LD.THRESHOLD_WIDTH_HU)
        raw, ct_alone = batch["masks"], jnp.stack([bone, bone], -1)         # the ladder's two ends, made by hand
        ends = [float(T.landmark_terms(model(batch["hu"], m, 1.0), batch["targets"])[2]) for m in (raw, ct_alone)]
        np.testing.assert_allclose([E[0], E[2]], ends, rtol=1e-5)
        t = T.timing(model, n=2, repeats=1)
        self.assertGreater(t["seconds_per_crop"], 0.0)
        i = 1
        pred = model.ct_only(jnp.asarray(ex.hu[i:i + 1]))
        r = T.as_reading(ex.readings[i], ex.frames[i], np.asarray(pred["points"][0]), np.asarray(pred["values"][0]),
                         list(cfg.keys))
        self.assertEqual(r.level, ex.readings[i].level)
        for k in cfg.keys:
            self.assertTrue(r.measurements[k].drawn)
        back = T.as_reading(ex.readings[i], ex.frames[i], ex.targets[i], ex.values[i], list(cfg.keys))
        np.testing.assert_allclose(back.landmarks(list(cfg.keys)), ex.readings[i].landmarks(list(cfg.keys)), atol=1e-9)
        ph = ex.phantoms[0]
        with tempfile.TemporaryDirectory() as d:
            RD.draw(r, ph.hu, ph.affine, os.path.join(d, "net.png"), kind="ct", keys=list(cfg.keys), half_mm=40.0,
                    step_mm=1.0)
            self.assertTrue(os.path.getsize(os.path.join(d, "net.png")) > 0)


if __name__ == "__main__":
    unittest.main()

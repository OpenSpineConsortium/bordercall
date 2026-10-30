"""The network as a block (autoanatomist/model.py, ARCHITECTURES) and the probe, the architecture
whose answer is known before it trains, on the sizes the model tests use: a crop of 16 by 20 by 12
voxels at 6 mm and two phantoms of three levels.

    python -m unittest tests.test_autoanatomist_probe -v        # from the repository's root, in the venv

Each of the three architectures gives the fusion frame's shapes from either branch, its CT-only
path is the fused pass at w 0 to the bit, and it trains through a session with finite losses; the
residual and the plain network each lower the loss in one step and are two different sizes. The
probe has two parameters, the CT branch's tau and sigma, and its mask path, the mask branch and the
decoder, has none: its landmark error is one number whatever the seed, to the bit, and training
leaves it as it was. At lambda 1 the ladder's own soft threshold of the CT is what the mask branch
shows, so the CT branch's features equal the mask branch's at (tau, sigma) = (BONE_HU,
THRESHOLD_WIDTH_HU) over HU_SCALE, a zero of the feature loss, and not at the start nor at lambda
0; no term but the feature term reaches tau and sigma, since the decoder passes no gradient back;
and 150 steps at lr 0.01 at lambda 1 take the CT branch from its start to that optimum within 0.01
(measured 2026-10-29 in the container: within 0.0004 on this crop, within 0.0003 on the full crop
at 2 mm). A session with the probe saved after two steps, loaded and trained one more is the three
steps straight, to the bit.
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

STEPS, LR = 150, 0.01                                             # the probe's training to the gate (model.py's docstring)
WITHIN = 0.01


def tiny_config(architecture: str = "residual-unet"):
    from autoanatomist.model import Config
    return Config(widths=(4, 8, 8), shape=(16, 20, 12), spacing=6.0, architecture=architecture)


def examples(cfg):
    from autoanatomist import train as T
    return T.make_examples(cfg, n_spines=2, count=3, seed=0, spacing_mm=2.0)


def forward(cfg, model, ex, w: float, lam: float):
    """The fused pass over every crop at (w, lambda), the masks down the ladder as losses takes them."""
    from autoanatomist import ladder, train as T
    batch = T.batch_of(ex, np.arange(len(ex)))
    masks = ladder.degrade(batch["masks"], batch["hu"], jnp.float32(lam), spacing_mm=cfg.spacing)
    return batch, model(batch["hu"], masks, jnp.float32(w))


def scales_of(shape):
    """The three scales' shapes: a half, a quarter and an eighth, each rounded up as SAME padding rounds."""
    out, s = [], tuple(shape)
    for _ in range(3):
        s = tuple(-(-n // 2) for n in s)
        out.append(s)
    return out


def same_rows(test, a, b):
    test.assertEqual(len(a), len(b))
    for x, y in zip(a, b):
        for k in x:
            if k != "seconds":
                test.assertEqual(x[k], y[k], (k, x, y))


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheArchitectures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ex = examples(tiny_config())

    def test_each_gives_the_frames_shapes_reads_the_ct_alone_and_trains(self):
        from autoanatomist import blocks as B
        from autoanatomist import model as Mo
        from autoanatomist import session as Se
        self.assertEqual(tuple(Mo.ARCHITECTURES), ("residual-unet", "plain-unet", "probe"))
        self.assertEqual(Mo.DEFAULT_ARCHITECTURE, "residual-unet")
        self.assertEqual(Mo.DEFAULT_ARCHITECTURE, B.DEFAULTS.architecture)
        for name, arch in Mo.ARCHITECTURES.items():
            self.assertEqual(arch.name, name)
            cfg = tiny_config(name)
            m = Mo.Model(cfg, nnx.Rngs(0))
            batch, out = forward(cfg, m, self.ex, 0.5, 0.3)
            n = len(self.ex)
            self.assertEqual(out["points"].shape, (n, cfg.n_landmarks, 3), name)
            self.assertEqual(out["cov"].shape, (n, cfg.n_landmarks, 3, 3), name)
            self.assertEqual(out["values"].shape, (n, len(cfg.keys)), name)
            self.assertEqual(out["sigma"].shape, (n, len(cfg.keys)), name)
            self.assertEqual(len(out["f_ct"]), 3, name)
            for k, (a, b) in enumerate(zip(out["f_ct"], out["f_mask"])):
                self.assertEqual(a.shape, b.shape, (name, k))
                self.assertEqual(tuple(a.shape[1:4]), scales_of(cfg.shape)[k], (name, k))
            self.assertTrue(np.isfinite(np.asarray(out["points"])).all(), name)
            alone = m.ct_only(batch["hu"])
            _, at_zero = forward(cfg, m, self.ex, 0.0, 0.3)
            np.testing.assert_array_equal(np.asarray(alone["points"]), np.asarray(at_zero["points"]), name)
            s = Se.Session.new(B.parse("architecture=%s" % name), keys=cfg.keys, shape=cfg.shape, spacing=cfg.spacing)
            self.assertEqual(s.cfg.architecture, name)
            self.assertEqual(s.status()["blocks"], [] if name == Mo.DEFAULT_ARCHITECTURE else ["architecture=%s" % name])
            rows = s.train(self.ex, 2)
            self.assertEqual(len(rows), 2)
            for row in rows:
                for k in ("total", "landmark", "spread", "value", "feature", "naming", "distance_mm"):
                    self.assertTrue(np.isfinite(row[k]), (name, k, row))

    def test_the_two_networks_lower_the_loss_in_one_step_and_are_different_sizes(self):
        import optax
        from autoanatomist import model as Mo
        from autoanatomist import train as T
        sizes = {}
        for name in ("residual-unet", "plain-unet"):
            cfg = tiny_config(name)
            m = Mo.Model(cfg, nnx.Rngs(1))
            sizes[name] = Mo.count_parameters(m)
            opt = nnx.Optimizer(m, optax.adamw(2e-3), wrt=nnx.Param)
            step = T.make_step(None, 0)
            batch = T.batch_of(self.ex, np.arange(len(self.ex)))
            before = float(T.losses(m, batch, 1.0, 0.0)[0])
            step(m, opt, batch, jnp.float32(1.0), jnp.float32(0.0))
            self.assertLess(float(T.losses(m, batch, 1.0, 0.0)[0]), before, name)
        sizes["probe"] = Mo.count_parameters(Mo.Model(tiny_config("probe"), nnx.Rngs(1)))
        self.assertEqual(sizes["probe"], 2)
        self.assertGreater(sizes["plain-unet"], 1000)
        self.assertGreater(sizes["residual-unet"], sizes["plain-unet"])


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = tiny_config("probe")
        cls.ex = examples(cls.cfg)

    def test_two_parameters_and_a_mask_path_with_no_seed_in_it(self):
        from autoanatomist import model as Mo
        from autoanatomist import train as T
        cfg, ex = self.cfg, self.ex
        got = []
        for seed in (0, 1):
            m = Mo.Model(cfg, nnx.Rngs(seed))
            self.assertEqual(Mo.count_parameters(m), 2)
            for v, start in zip((m.ct.tau.value, m.ct.sigma.value), Mo.PROBE_START):
                self.assertAlmostEqual(float(v), start, places=6)
            self.assertEqual(Mo.count_parameters(m.mask), 0)
            self.assertEqual(Mo.count_parameters(m.decoder), 0)
            batch, out = forward(cfg, m, ex, 1.0, 0.0)
            _, _, dist = T.landmark_terms(out, batch["targets"])
            got.append((np.asarray(out["points"]), np.asarray(out["values"]), float(dist)))
        np.testing.assert_array_equal(got[0][0], got[1][0])
        np.testing.assert_array_equal(got[0][1], got[1][1])
        self.assertEqual(got[0][2], got[1][2])
        self.assertTrue(np.isfinite(got[0][2]))
        self.assertGreater(got[0][2], 0.0)
        self.assertLess(got[0][2], 3 * cfg.spacing)                  # within three voxels of the oracle's chord ends

    def test_at_lambda_one_the_optimum_is_the_ladders_gate(self):
        from autoanatomist import gates, ladder
        from autoanatomist import model as Mo
        from autoanatomist import train as T
        cfg, ex = self.cfg, self.ex
        self.assertEqual(Mo.PROBE_OPTIMUM, (gates.BONE_HU / Mo.HU_SCALE, ladder.THRESHOLD_WIDTH_HU / Mo.HU_SCALE))
        self.assertEqual(Mo.PROBE_OPTIMUM, (0.2, 0.06))
        m = Mo.Model(cfg, nnx.Rngs(0))
        _, at_start = forward(cfg, m, ex, 0.5, 1.0)
        self.assertGreater(float(T.feature_term(at_start)), 1e-3)
        m.ct.tau.value = jnp.float32(Mo.PROBE_OPTIMUM[0])
        m.ct.sigma.value = jnp.float32(Mo.PROBE_OPTIMUM[1])
        self.assertAlmostEqual(m.ct.threshold()[0], Mo.PROBE_OPTIMUM[0], places=6)
        self.assertAlmostEqual(m.ct.threshold()[1], Mo.PROBE_OPTIMUM[1], places=6)
        _, at_optimum = forward(cfg, m, ex, 0.5, 1.0)
        for a, b in zip(at_optimum["f_ct"], at_optimum["f_mask"]):
            np.testing.assert_allclose(np.asarray(a), np.asarray(b), atol=1e-6)
        self.assertLess(float(T.feature_term(at_optimum)), 1e-12)
        _, at_lambda_zero = forward(cfg, m, ex, 0.5, 0.0)            # the drawn mask is not a threshold of the CT
        self.assertGreater(float(T.feature_term(at_lambda_zero)), 1e-3)

    def test_only_the_feature_term_reaches_the_ct_branch(self):
        from autoanatomist import model as Mo
        from autoanatomist import train as T
        cfg, ex = self.cfg, self.ex
        m = Mo.Model(cfg, nnx.Rngs(0))
        batch = T.batch_of(ex, np.arange(len(ex)))

        def gradient(weights):
            loss = lambda model: T.losses(model, batch, 0.5, 0.5, None, 0, weights)[0]
            grads = nnx.grad(loss)(m)
            return np.array([float(v) for v in jax.tree.leaves(grads)])

        every_other = gradient({"landmark": 1.0, "spread": 1.0, "value": 1.0, "feature": 0.0, "naming": 0.0})
        self.assertEqual(len(every_other), 2)
        np.testing.assert_array_equal(every_other, 0.0)
        feature = gradient({"landmark": 0.0, "spread": 0.0, "value": 0.0, "feature": 1.0, "naming": 0.0})
        self.assertTrue(np.all(np.isfinite(feature)) and np.all(feature != 0.0), feature)

    def test_feature_training_reaches_the_gate_and_leaves_the_mask_path_as_it_was(self):
        from autoanatomist import blocks as B
        from autoanatomist import model as Mo
        from autoanatomist import session as Se
        cfg, ex = self.cfg, self.ex
        words = "architecture=probe lr=%s schedule=fixed lam_fixed=1 w_fixed=0.5 naming=off" % LR
        s = Se.Session.new(B.parse(words), keys=cfg.keys, shape=cfg.shape, spacing=cfg.spacing)
        _, before = forward(cfg, s.model, ex, 1.0, 0.0)
        rows = s.train(ex, STEPS)
        self.assertEqual(s.step, STEPS)
        self.assertEqual((rows[0]["w"], rows[0]["lam"], rows[-1]["w"], rows[-1]["lam"]), (0.5, 1.0, 0.5, 1.0))
        tau, sigma = s.model.ct.threshold()
        self.assertLess(abs(tau - Mo.PROBE_OPTIMUM[0]), WITHIN, (tau, sigma))
        self.assertLess(abs(sigma - Mo.PROBE_OPTIMUM[1]), WITHIN, (tau, sigma))
        self.assertLess(rows[-1]["feature"], 1e-5)
        self.assertLess(rows[-1]["feature"], rows[0]["feature"])
        _, after = forward(cfg, s.model, ex, 1.0, 0.0)
        np.testing.assert_array_equal(np.asarray(before["points"]), np.asarray(after["points"]))
        res = s.evaluate(ex)
        self.assertEqual(res["step"], STEPS)
        self.assertTrue(np.isfinite(res["distance_mm"]) and np.isfinite(res["sigma_mm"]), res)
        self.assertEqual(set(res["value_mae"]), set(cfg.keys))
        self.assertTrue(all(np.isfinite(v) for v in res["value_mae"].values()), res)

    def test_saved_loaded_and_trained_on_is_the_run_straight_to_the_bit(self):
        from autoanatomist import blocks as B
        from autoanatomist import session as Se
        cfg, ex = self.cfg, self.ex
        words = "architecture=probe lr=%s anneal=3" % LR
        straight = Se.Session.new(B.parse(words), keys=cfg.keys, shape=cfg.shape, spacing=cfg.spacing)
        rows = straight.train(ex, 3)
        s = Se.Session.new(B.parse(words), keys=cfg.keys, shape=cfg.shape, spacing=cfg.spacing)
        first = s.train(ex, 2)
        with tempfile.TemporaryDirectory() as d:
            meta = s.save(d)
            self.assertEqual(meta["blocks"]["changed"], ["lr=%s" % LR, "anneal=3", "architecture=probe"])
            names = np.load(os.path.join(d, Se.STATE)).files
            self.assertEqual(sorted(n for n in names if n.startswith("model/")), ["model/ct/sigma", "model/ct/tau"])
            t = Se.Session.load(d)
        self.assertEqual(t.cfg.architecture, "probe")
        self.assertEqual(t.model.ct.threshold(), s.model.ct.threshold())
        self.assertEqual(t.step, 2)
        same_rows(self, rows, first + t.train(ex, 1))


if __name__ == "__main__":
    unittest.main()

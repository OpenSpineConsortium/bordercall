"""The fully latent objective (blocks.py's objective=mask) and what it rests on: the windowed
sampler and the centroid frame (crops.py), the centroid rows (rows.py), the mask decoder and the
name head (model.py), the mask, name and metric terms (train.py) and the session under it
(session.py), on the model tests' sizes: a crop of 16 by 20 by 12 voxels and two phantoms of
three levels.

    python -m unittest tests.test_autoanatomist_latent -v          # from the repository's root, in the venv

Each test holds a claim to something outside the code it tests: the windowed sampler to
map_coordinates over the whole volume, voxel for voxel, and the centroids to argwhere's mean; a
phantom row in the centroid frame to one crop per level, top down, with no reading, no target and
no value; a volume row read from NIfTI files in the centroid frame to the same phantom rendered in
memory, and on two grids, where the oracle frame refuses, to the same levels about the same centres; the mask terms to their known answers on
exact blocks (a Dice of 1 and a loss near 0 where the logits are the pooled truth, 0 where they
are its opposite), the name term to a right and a wrong answer, the neighbour table to the chain's
columns (T12 to L1, T12 to T13, T13 to L1, L5 to L6), the centroid error to a shifted cube, the
surface distance to a cube against itself and against a shift of one voxel; the model's shapes and
its CT-only path to the fused pass at w 0; the blocks' refusals in words; and a session under the
objective trained, evaluated, saved and loaded, its latents the same before and after.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

try:
    import jax  # noqa: F401
    from flax import nnx  # noqa: F401
    HAVE_JAX = True
except ImportError:                                               # pragma: no cover
    HAVE_JAX = False

try:
    import nibabel  # noqa: F401
    HAVE_NIBABEL = True
except ImportError:                                               # pragma: no cover
    HAVE_NIBABEL = False

ROWS = [{"kind": "phantom", "id": "p0", "count": 3, "seed": 1, "spacing": 2.0, "start": "T12", "frame": "centroid"},
        {"kind": "phantom", "id": "p1", "count": 3, "seed": 2, "spacing": 2.0, "start": "L1", "frame": "centroid"}]
WORDS = "objective=mask naming=off widths=4:8:8"


def tiny_config():
    from autoanatomist.model import Config
    return Config(widths=(4, 8, 8), shape=(16, 20, 12), spacing=6.0, objective="mask")


def whole_volume_sample(volume, affine, cf, order, fill):
    """What sample gave before the window: map_coordinates over the whole volume."""
    from autoanatomist import crops
    ijk = crops.voxel_coordinates(affine, cf)
    out = ndimage.map_coordinates(np.asarray(volume, np.float32), ijk.T, order=order, mode="constant", cval=fill)
    return out.reshape(cf.shape).astype(np.float32)


class TheWindowAndTheCentroidFrame(unittest.TestCase):
    def setUp(self):
        from autoanatomist import crops
        self.rng = np.random.default_rng(0)
        self.vol = self.rng.normal(size=(20, 24, 16)).astype(np.float32)
        A = np.eye(4)
        A[:3, :3] = np.diag([1.5, 1.0, 2.5]) @ crops.turn([0.0, 0.0, 1.0], 10.0)
        A[:3, 3] = [-10.0, 5.0, 3.0]
        self.A = A

    def test_the_window_gives_the_whole_volume_s_values(self):
        from autoanatomist import crops
        for k in range(12):
            centre = self.rng.uniform([-10, 0, 0], [25, 30, 45])
            cf = crops.perturbed(crops.CropFrame(centre, np.eye(3), 2.0, (8, 10, 6)), self.rng, 20.0, 30.0)
            for order in (0, 1):
                got = crops.sample(self.vol, self.A, cf, order=order, fill=-7.0)
                np.testing.assert_array_equal(got, whole_volume_sample(self.vol, self.A, cf, order, -7.0), (k, order))
        far = crops.CropFrame(np.array([500.0, 500.0, 500.0]), np.eye(3), 2.0, (8, 10, 6))
        self.assertTrue(np.all(crops.sample(self.vol, self.A, far, fill=-3.0) == -3.0))
        with self.assertRaises(ValueError):
            crops.sample(self.vol, self.A, far, order=3)

    def test_the_centroids_and_the_frame(self):
        from autoanatomist import crops
        lab = np.zeros((20, 24, 16), np.int16)
        lab[2:6, 3:9, 4:10] = 20
        lab[10:15, 5:12, 2:9] = 21
        c = crops.centroids(lab, self.A, [20, 21, 22])
        self.assertEqual(sorted(c), [20, 21])
        for v in (20, 21):
            ijk = np.argwhere(lab == v).mean(0)
            np.testing.assert_allclose(c[v], ijk @ self.A[:3, :3].T + self.A[:3, 3])
        cf = crops.from_centroid(c[20], shift=3.0, spacing=1.0, shape=(8, 10, 6))
        np.testing.assert_allclose(cf.origin, c[20] + [0.0, 3.0, 0.0])
        np.testing.assert_array_equal(cf.axes, np.eye(3))
        self.assertEqual((cf.spacing, cf.shape), (1.0, (8, 10, 6)))
        m = crops.mask_channels(lab, self.A, cf, 20)
        np.testing.assert_array_equal(m[..., 0], whole_volume_sample((lab == 20).astype(np.float32), self.A, cf, 1, 0.0))
        np.testing.assert_array_equal(m[..., 1], whole_volume_sample((lab > 0).astype(np.float32), self.A, cf, 1, 0.0))
        self.assertGreater(m[..., 0].sum(), 0.0)


class TheBlocks(unittest.TestCase):
    def test_the_objective_s_refusals_and_its_words(self):
        from autoanatomist import blocks as B
        for words, said in [("objective=mask", "naming=off"), ("objective=mask naming=off calibrate=scale", "calibrate=none"),
                            ("objective=mask naming=off architecture=probe", "probe"), ("objective=ring", "objective")]:
            with self.assertRaises(ValueError, msg=words) as cm:
                B.parse(words)
            self.assertIn(said, str(cm.exception), words)
        b = B.parse("objective=mask naming=off w_name=0.5")
        self.assertEqual(b.weights()["name"], 0.5)
        self.assertEqual(b.weights()["mask"], 1.0)
        self.assertEqual(sorted(b.changed()), ["naming=off", "objective=mask", "w_name=0.5"])
        self.assertIn("w_name=0.1", B.parse().words())
        self.assertNotEqual(b.digest(), B.parse().digest())
        self.assertEqual(B.parse(b.words()).digest(), b.digest())


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheCentroidRows(unittest.TestCase):
    def test_a_phantom_row_in_the_centroid_frame(self):
        from autoanatomist import naming
        from autoanatomist import rows as R
        cfg = tiny_config()
        ex = R.render_row(ROWS[0], cfg)
        self.assertEqual(len(ex), 3)
        self.assertEqual([naming.NAMES[i] for i in ex.names], ["T12", "L1", "L2"])          # top down
        self.assertEqual((ex.readings, len(ex.frames), len(ex.phantoms)), ([], 3, 1))
        self.assertTrue(np.isnan(ex.targets).all() and np.isnan(ex.values).all())
        self.assertEqual((ex.targets.shape, ex.values.shape), ((3, cfg.n_landmarks, 3), (3, len(cfg.keys))))
        for i in range(3):
            self.assertGreater(ex.masks[i, ..., 0].sum(), 0.0, i)                            # the vertebra is in its crop
            self.assertGreaterEqual(ex.masks[i, ..., 1].sum(), ex.masks[i, ..., 0].sum(), i)
        for f in ex.frames:
            self.assertEqual(f.shape, cfg.shape)
        plain = R.render_row(ROWS[0], cfg, jitter=False)
        for f in plain.frames:
            np.testing.assert_array_equal(f.axes, np.eye(3))                                  # the world's axes, unjittered
        self.assertEqual(R.canonical(dict(ROWS[0]))["frame"], "centroid")
        self.assertEqual(R.canonical({"kind": "phantom", "id": "x"})["frame"], "oracle")
        with self.assertRaises(ValueError) as cm:
            R.canonical({"kind": "phantom", "id": "x", "frame": "ring"})
        self.assertIn("oracle or centroid", str(cm.exception))
        self.assertNotEqual(R.row_digest(ROWS[0], cfg), R.row_digest(dict(ROWS[0], frame="oracle"), cfg))
        with tempfile.TemporaryDirectory() as d:
            both = R.examples_for(ROWS, cfg, cache_dir=d)
            self.assertEqual(len(both), 6)
            again = R.examples_for(ROWS, cfg, cache_dir=d)
            np.testing.assert_array_equal(again.masks, both.masks)
            np.testing.assert_array_equal(again.names, both.names)

    @unittest.skipUnless(HAVE_NIBABEL, "nibabel is not installed")
    def test_a_volume_row_in_the_centroid_frame_reads_from_files_and_from_two_grids(self):
        import nibabel as nib
        from autoanatomist import phantom
        from autoanatomist import rows as R
        cfg = tiny_config()
        r = R.canonical(ROWS[1])
        rng = np.random.default_rng(r["seed"])
        levels = phantom.draw_levels(r["phenotype"], seed=r["seed"], start=r["start"], count=r["count"])
        tilt = (tuple(float(v) for v in rng.normal(size=3)), float(rng.uniform(0.0, 15.0)))
        ph = phantom.render(levels, spacing=(r["spacing"],) * 3, tilt=tilt, sub=r["sub"], noise_hu=r["noise"], seed=r["seed"])
        names = {str(k): v for k, v in ph.names.items()}
        with tempfile.TemporaryDirectory() as d:
            ct, lab = os.path.join(d, "ct.nii.gz"), os.path.join(d, "lab.nii.gz")
            nib.save(nib.Nifti1Image(np.asarray(ph.hu, np.float32), ph.affine), ct)
            nib.save(nib.Nifti1Image(np.asarray(ph.labels, np.int16), ph.affine), lab)
            row = {"kind": "volume", "id": "v", "ct": ct, "labels": lab, "names": names, "seed": r["seed"], "frame": "centroid"}
            got = R.render_row(row, cfg, jitter=False)
            want = R.render_row(ROWS[1], cfg, jitter=False)
            self.assertEqual(len(got), len(want))
            np.testing.assert_array_equal(got.names, want.names)
            np.testing.assert_allclose(got.hu, want.hu, atol=0.5)                           # the header's float32 affine
            np.testing.assert_allclose(got.masks, want.masks, atol=1e-3)
            coarse = os.path.join(d, "coarse.nii.gz")                                       # the labels on a grid of their own
            A = np.array(ph.affine, float)
            A[:3, :3] = A[:3, :3] * 2.0
            nib.save(nib.Nifti1Image(np.asarray(ph.labels[::2, ::2, ::2], np.int16), A), coarse)
            two = dict(row, labels=coarse)
            with self.assertRaises(ValueError) as cm:
                R.render_row(dict(two, frame="oracle"), cfg)
            self.assertIn("one grid", str(cm.exception))
            ex = R.render_row(two, cfg, jitter=False)
            self.assertEqual(len(ex), len(want))
            np.testing.assert_array_equal(ex.names, want.names)
            for i in range(len(ex)):                                  # the coarse mask's centroid moves the frame a voxel at most
                self.assertLess(np.abs(ex.frames[i].origin - want.frames[i].origin).max(), 2.0 * r["spacing"], i)
                self.assertGreater(ex.masks[i, ..., 0].sum(), 0.0, i)


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheTerms(unittest.TestCase):
    def test_the_mask_terms_on_exact_blocks(self):
        import jax.numpy as jnp
        from autoanatomist import train as T
        masks = np.zeros((2, 8, 8, 4, 2), np.float32)
        masks[0, 2:6, 2:6, 0:2, 0] = 1.0                      # whole 2 by 2 by 2 blocks: the pooled truth is 0 or 1
        masks[0, 0:8, 2:6, 0:4, 1] = 1.0
        masks[1, 4:8, 0:4, 2:4, 0] = 1.0
        masks[1, 4:8, 0:8, 2:4, 1] = 1.0
        t = np.asarray(T.pooled(jnp.asarray(masks), (4, 4, 2)))
        self.assertEqual(set(np.unique(t).tolist()), {0.0, 1.0})
        right = jnp.where(t > 0.5, 20.0, -20.0)
        loss, dice, every = T.mask_terms(right, jnp.asarray(masks))
        self.assertEqual((float(dice), float(every)), (1.0, 1.0))
        self.assertLess(float(loss), 1e-3)
        loss, dice, every = T.mask_terms(-right, jnp.asarray(masks))
        self.assertLess(max(float(dice), float(every)), 1e-6)
        self.assertGreater(float(loss), 10.0)
        self.assertAlmostEqual(float(T.mask_error(right, jnp.asarray(masks))), 0.0, places=5)
        with self.assertRaises(ValueError):
            T.pooled(jnp.asarray(masks), (3, 4, 2))

    def test_the_name_term_the_neighbours_and_the_distances(self):
        import jax.numpy as jnp
        from autoanatomist import naming
        from autoanatomist import train as T
        n = len(naming.NAMES)
        names = np.array([naming.NAME_INDEX["L1"], naming.NAME_INDEX["T13"]])
        logits = np.full((2, n), -10.0, np.float32)
        logits[np.arange(2), names] = 10.0
        ce, right = T.name_terms(jnp.asarray(logits), jnp.asarray(names))
        self.assertLess(float(ce), 1e-6)
        self.assertEqual(float(right), 1.0)
        ce, right = T.name_terms(jnp.asarray(np.roll(logits, 1, 1)), jnp.asarray(names))
        self.assertGreater(float(ce), 10.0)
        self.assertEqual(float(right), 0.0)
        I = naming.NAME_INDEX
        pairs = T.adjacent_names()
        for a, b in [("T12", "L1"), ("T12", "T13"), ("T13", "L1"), ("L5", "L6"), ("C3", "C4"), ("L4", "L5")]:
            self.assertIn(frozenset((I[a], I[b])), pairs, (a, b))
        for a, b in [("C3", "L5"), ("L5", "T13"), ("T11", "L1"), ("L6", "T13"), ("L4", "L6")]:
            self.assertNotIn(frozenset((I[a], I[b])), pairs, (a, b))
        near = T.within_one(np.array([I["L1"], I["L1"], I["T12"], I["C3"]]), np.array([I["L1"], I["T13"], I["T13"], I["L5"]]))
        self.assertEqual(near.tolist(), [True, True, True, False])
        cube = np.zeros((10, 10, 10), bool)
        cube[2:6, 2:6, 2:6] = True
        self.assertEqual(T.centroid_error_mm(cube, np.roll(cube, 2, 0), 3.0, 99.0), 6.0)
        self.assertEqual(T.centroid_error_mm(cube, np.zeros_like(cube), 3.0, 99.0), 99.0)
        self.assertEqual(T.surface_distance_mm(cube, cube, 2.0, 99.0), 0.0)
        d = T.surface_distance_mm(cube, np.roll(cube, 1, 0), 2.0, 99.0)
        self.assertTrue(0.0 < d <= 2.0, d)
        self.assertEqual(T.surface_distance_mm(cube, np.zeros_like(cube), 2.0, 99.0), 99.0)


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheModelAndTheSession(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from autoanatomist import blocks as B
        from autoanatomist import rows as R
        from autoanatomist import session as S
        cls.cfg = tiny_config()
        cls.ex = R.examples_for(ROWS, cls.cfg)
        cls.session = S.Session.new(B.parse(WORDS), keys=cls.cfg.keys, shape=cls.cfg.shape, spacing=cls.cfg.spacing)
        cls.rows = cls.session.train(cls.ex, 6)

    def test_the_config_and_the_model(self):
        import jax.numpy as jnp
        from autoanatomist.model import Config, Model, N_NAMES
        from autoanatomist import naming
        with self.assertRaises(ValueError):
            Config(objective="mask", architecture="probe")
        with self.assertRaises(ValueError):
            Config(objective="ring")
        cfg = self.cfg
        self.assertEqual((cfg.n_outputs, Config(widths=cfg.widths, shape=cfg.shape).n_outputs), (2, cfg.n_landmarks))
        self.assertEqual(N_NAMES, len(naming.NAMES))
        m = Model(cfg, nnx.Rngs(0))
        hu, masks = jnp.asarray(self.ex.hu[:2]), jnp.asarray(self.ex.masks[:2])
        out = m(hu, masks, 0.3)
        self.assertEqual(out["logits"].shape, (2, 8, 10, 6, 2))
        self.assertEqual((out["latent"].shape, out["name_logits"].shape), ((2, 8), (2, N_NAMES)))
        self.assertNotIn("points", out)
        alone = m.ct_only(hu)
        fused = m(hu, masks, 0.0)
        for k in ("logits", "latent", "name_logits"):
            np.testing.assert_allclose(np.asarray(alone[k]), np.asarray(fused[k]), atol=1e-5, err_msg=k)
        plain = Model(Config(widths=cfg.widths, shape=cfg.shape, spacing=cfg.spacing), nnx.Rngs(0))
        self.assertIsNone(plain.names)
        self.assertIn("points", plain.ct_only(hu))

    def test_the_session_trains_evaluates_and_comes_back_from_disk(self):
        from autoanatomist import blocks as B
        from autoanatomist import naming
        from autoanatomist import session as S
        from autoanatomist import train as T
        s = self.session
        self.assertEqual((s.cfg.objective, s.step), ("mask", 6))
        self.assertEqual(set(self.rows[0]) - {"seconds"}, {"step", "w", "lam", "total", "mask", "feature", "name", "dice", "dice_every", "named_right"})
        w = s.blocks.weights()
        r = self.rows[0]
        self.assertAlmostEqual(r["total"], w["mask"] * r["mask"] + w["feature"] * r["feature"] + w["name"] * r["name"], places=4)
        self.assertLess(np.mean([r["total"] for r in self.rows[-2:]]), self.rows[0]["total"])
        self.assertIn("dice", T.progress_words(r))
        rep = s.evaluate(self.ex)
        for k in ("dice", "dice_every", "distance_mm", "centroid_mm", "named_right", "named_within_one", "feature_gap"):
            self.assertTrue(np.isfinite(rep[k]), k)
        self.assertTrue(0.0 <= rep["dice"] <= 1.0 and rep["named_within_one"] >= rep["named_right"])
        self.assertEqual((rep["crops"], rep["step"], rep["surface_bound_mm"]), (6, 6, T.longest_side_mm(s.cfg)))
        self.assertEqual(sorted(rep["by_level"]), sorted({naming.NAMES[i] for i in self.ex.names}))
        self.assertEqual(sum(v["crops"] for v in rep["by_level"].values()), 6)
        lat = s.latents(self.ex)
        self.assertEqual(lat.shape, (6, 8))
        with self.assertRaises(ValueError):
            s.calibrate(self.ex)
        with tempfile.TemporaryDirectory() as d:
            s.save(d)
            back = S.Session.load(d)
            self.assertEqual((back.step, back.blocks.objective, back.cfg.objective), (6, "mask", "mask"))
            np.testing.assert_array_equal(back.latents(self.ex), lat)
            self.assertEqual(back.evaluate(self.ex)["dice"], rep["dice"])
        plain = S.Session.new(B.parse("widths=4:8:8"), keys=self.cfg.keys, shape=self.cfg.shape, spacing=self.cfg.spacing)
        with self.assertRaises(ValueError):
            plain.latents(self.ex)
        E, dE = T.error_curve(s.model, T.batch_of(self.ex, np.arange(3)), [0.0, 0.5, 1.0])
        self.assertTrue(np.all(np.isfinite(E)) and np.all(np.isfinite(dE)) and np.all((0.0 <= E) & (E <= 1.0)))


if __name__ == "__main__":
    unittest.main()

"""The soft gates, the degradation ladder and the crops of autoanatomist/, each claim checked
against something outside the code it tests.

    python -m unittest discover -s tests -v          # from the repository's root, in the venv

The soft dilation and erosion reach scipy.ndimage's binary dilation and erosion by a ball within
tau log N, N the ball's voxels, in float64 with a hard maximum and a narrow rim, and threshold to
them exactly; a constant is kept up to the volume's edges; their gradients in the radius and in
the mask are finite differences' within 1e-6 relatively; their sums grow with the radius; the
blur is scipy's gaussian_filter with mode 'nearest'; the soft threshold is a step as its width
shrinks. The ladder gives the masks back exactly at lambda 0 and a function of the CT alone at
1, with a gradient in lambda that matches finite differences inside each rung; the schedule
starts at w 1 and lambda 0 and ends at w 0 and lambda 1. A crop carries a point into the world and
back, its axes stay a rotation when jittered, and the oracle's landmarks land inside it.
"""
from __future__ import annotations

import os
import sys
import unittest

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

try:
    import jax
    import jax.numpy as jnp
    HAVE_JAX = True
except ImportError:                                               # pragma: no cover
    HAVE_JAX = False


def ball(R: int, r: float) -> np.ndarray:
    t = np.arange(-R, R + 1)
    return np.sqrt(t[:, None, None] ** 2 + t[None, :, None] ** 2 + t[None, None, :] ** 2) <= r


def sparse_mask(seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    m = (rng.random((2, 20, 18, 16)) < 0.01).astype(float)
    m[0, 5:9, 5:8, 4:10] = 1.0
    return m


@unittest.skipUnless(HAVE_JAX, "jax is not installed")
class TheGates(unittest.TestCase):
    def test_soft_morphology_reaches_the_hard_one(self):
        from autoanatomist import gates as GT
        m = sparse_mask()
        tau, R = 0.004, 4
        for r in (1.5, 2.05, 3.08):                     # each between two of a voxel grid's distances
            n = ball(R, r).sum()
            with jax.enable_x64(True):
                soft_d = np.asarray(GT.soft_dilate(jnp.asarray(m), r, tau=tau, edge=0.01, max_radius=R))
                soft_e = np.asarray(GT.soft_erode(jnp.asarray(1.0 - m), r, tau=tau, edge=0.01, max_radius=R))
            hard_d = np.stack([ndimage.binary_dilation(x > 0.5, ball(R, r)) for x in m]).astype(float)
            hard_e = np.stack([ndimage.binary_erosion(x > 0.5, ball(R, r), border_value=1) for x in 1.0 - m]).astype(float)
            bound = tau * np.log(n) + 0.01                # the soft maximum's own error, and the rim's
            self.assertLess(np.abs(soft_d - hard_d).max(), bound, r)
            self.assertLess(np.abs(soft_e - hard_e).max(), bound, r)
            np.testing.assert_array_equal(soft_d > 0.5, hard_d > 0.5)
            np.testing.assert_array_equal(soft_e > 0.5, hard_e > 0.5)

    def test_a_constant_is_kept_and_float32_stays_finite(self):
        from autoanatomist import gates as GT
        c = jnp.full((2, 10, 9, 8), 0.37, jnp.float32)
        self.assertLess(float(jnp.abs(GT.soft_dilate(c, 2.0) - 0.37).max()), 1e-6)
        self.assertLess(float(jnp.abs(GT.soft_erode(c, 2.0) - 0.37).max()), 1e-6)
        m = jnp.asarray(sparse_mask(), jnp.float32)
        self.assertTrue(bool(jnp.isfinite(GT.soft_dilate(m, 2.0, tau=0.005, edge=0.1)).all()))

    def test_gradients_are_finite_differences(self):
        from autoanatomist import gates as GT
        rng = np.random.default_rng(1)
        with jax.enable_x64(True):
            mm = jnp.asarray(np.clip(ndimage.gaussian_filter(sparse_mask(), 1.0) * 3.0, 0.0, 1.0))
            h = 1e-5
            for op in (GT.soft_dilate, GT.soft_erode):
                f = lambda r: jnp.sum(op(mm, r, tau=0.1, edge=0.5, max_radius=4))
                fd = (f(2.0 + h) - f(2.0 - h)) / (2 * h)
                self.assertLess(abs(float(jax.grad(f)(2.0)) - float(fd)), 1e-6 * abs(float(fd)) + 1e-8)
            fm = lambda x: jnp.sum(GT.soft_dilate(x, 2.0, tau=0.1, edge=0.5, max_radius=4) ** 2)
            v = jnp.asarray(rng.standard_normal(mm.shape))
            fd = (fm(mm + h * v) - fm(mm - h * v)) / (2 * h)
            self.assertLess(abs(float(jnp.sum(jax.grad(fm)(mm) * v)) - float(fd)), 1e-6 * abs(float(fd)))
            sums = [float(jnp.sum(GT.soft_dilate(mm, r, tau=0.1, edge=0.5, max_radius=4))) for r in (0.5, 1.0, 2.0, 3.0)]
            self.assertTrue(all(a < b for a, b in zip(sums, sums[1:])), sums)

    def test_blur_and_threshold(self):
        from autoanatomist import gates as GT
        m = np.random.default_rng(2).random((1, 12, 11, 10)).astype(np.float32)
        for sigma in (0.7, 1.6):
            got = np.asarray(GT.gaussian_blur(jnp.asarray(m), sigma, max_sigma=2.0))[0]
            want = ndimage.gaussian_filter(m[0], sigma, mode="nearest", truncate=int(np.ceil(6.0)) / sigma)
            self.assertLess(np.abs(got - want).max(), 1e-5, sigma)
        x = jnp.linspace(-3.0, 3.0, 7)
        np.testing.assert_allclose(np.asarray(GT.soft_threshold(x, 0.5, 1e-4)), (np.asarray(x) > 0.5).astype(float))
        band = np.asarray(GT.soft_band(jnp.asarray([-100.0, 0.0, 100.0]), *GT.CANAL_HU, 1e-3))
        np.testing.assert_allclose(band, [0.0, 1.0, 0.0], atol=1e-6)


@unittest.skipUnless(HAVE_JAX, "jax is not installed")
class TheLadder(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(3)
        self.masks = jnp.asarray(rng.random((2, 12, 11, 10, 2)), jnp.float32)
        self.hu = jnp.asarray(rng.normal(150.0, 300.0, (2, 12, 11, 10, 1)), jnp.float32)

    def test_its_ends(self):
        from autoanatomist import gates as GT
        from autoanatomist import ladder as LD
        np.testing.assert_allclose(np.asarray(LD.degrade(self.masks, self.hu, 0.0)), np.asarray(self.masks), atol=1e-6)
        top = np.asarray(LD.degrade(self.masks, self.hu, 1.0))
        bone = np.asarray(GT.soft_threshold(self.hu[..., 0], GT.BONE_HU, LD.THRESHOLD_WIDTH_HU))
        np.testing.assert_allclose(top[..., 0], bone, atol=1e-6)
        np.testing.assert_allclose(top[..., 1], bone, atol=1e-6)
        other = np.asarray(LD.degrade(1.0 - self.masks, self.hu, 1.0))
        np.testing.assert_allclose(other, top, atol=1e-6)

    def test_its_gradient_in_lambda(self):
        from autoanatomist import ladder as LD
        with jax.enable_x64(True):
            masks, hu = jnp.asarray(np.asarray(self.masks, float)), jnp.asarray(np.asarray(self.hu, float))
            w = jnp.asarray(np.random.default_rng(4).standard_normal(masks.shape))
            f = lambda lam: jnp.sum(w * LD.degrade(masks, hu, lam))
            h = 1e-6
            for lam in (0.2, 0.5, 0.8):                   # inside each rung
                fd = (f(lam + h) - f(lam - h)) / (2 * h)
                g = jax.grad(f)(lam)
                self.assertTrue(np.isfinite(float(g)))
                self.assertLess(abs(float(g) - float(fd)), 1e-5 * abs(float(fd)) + 1e-6, lam)

    def test_the_schedule(self):
        from autoanatomist import ladder as LD
        s = LD.Schedule(100)
        self.assertEqual(s.at(0), (1.0, 0.0))
        self.assertEqual(s.at(99), (0.0, 1.0))
        ws, lams = zip(*[s.at(i) for i in range(100)])
        self.assertTrue(all(a >= b for a, b in zip(ws, ws[1:])))
        self.assertTrue(all(a <= b for a, b in zip(lams, lams[1:])))


class TheCrops(unittest.TestCase):
    def test_points_go_into_a_crop_and_back(self):
        from autoanatomist import crops as CR
        from autoanatomist import oracle as O
        from autoanatomist import phantom as PH
        from autoanatomist import specs as S
        levels = PH.draw_levels("typical", seed=5, start="L1", count=2)
        ph = PH.render(levels, spacing=(1.5,) * 3, sub=1)
        rng = np.random.default_rng(0)
        for r in O.ChordOracle(S.SEVEN).read(ph.labels, ph.affine, ph.names):
            cf = CR.perturbed(CR.from_reading(r), rng)
            np.testing.assert_allclose(cf.axes.T @ cf.axes, np.eye(3), atol=1e-12)
            self.assertAlmostEqual(float(np.linalg.det(cf.axes)), 1.0, places=12)
            P = r.landmarks(S.SEVEN)
            np.testing.assert_allclose(cf.world(cf.local(P)), P, atol=1e-9)
            t = CR.targets(r, cf, S.SEVEN)
            half = (np.array(cf.shape) - 1) / 2.0 * cf.spacing
            self.assertTrue(np.all(np.abs(t) <= half), (r.level, np.abs(t).max(0), half))
            ch = CR.mask_channels(ph.labels, ph.affine, cf, r.label)
            self.assertEqual(ch.shape, tuple(cf.shape) + (2,))
            self.assertTrue(np.all((ch >= 0) & (ch <= 1)))
            self.assertTrue(np.all(ch[..., 1] >= ch[..., 0] - 1e-6))      # every vertebra holds the target
            self.assertGreater(ch[..., 0].sum(), 0)


if __name__ == "__main__":
    unittest.main()

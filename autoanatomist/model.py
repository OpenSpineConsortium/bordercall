"""The auto-anatomist: a network that places a vertebra's measurement landmarks in a CT crop,
trained with the vertebra's mask as privileged information and then weaned off it, so that at
the end it reads the CT alone.

The privileged information is the mask: in training the network is given the target vertebra's
mask and every vertebra's beside the CT, which a test-time CT never comes with (learning using
privileged information, Vapnik and Vashist, Neural Networks 22, 2009; generalized distillation,
Lopez-Paz, Bottou, Schoelkopf and Vapnik, ICLR 2016). Two encoders of one architecture read the
two: E_ct the CT crop, E_mask the mask channels after the degradation ladder has taken them down
by lambda (ladder.py). At every scale the decoder reads the fusion

    F = (1 - w) F_ct + w F_mask,

w the fusion weight, 1 at the start of training and 0 at the end (ladder.Schedule), so the head
is first trained on what the mask makes plain and then handed over to the CT's features, which
the feature-matching loss ||F_ct - stopgrad(F_mask)||^2 (train.py) pulls toward the mask's all
along. That is the owner's pasted design (the homotopy and the feature matching), in the form
generalized distillation gives it; the architecture's sizes are this module's choices.

The head gives one heatmap per landmark (specs.landmarks: the two ends of each chord), read by
the soft-argmax, integral regression: the landmark is the heatmap's expected position, which is
differentiable and finer than its grid, and its spread is the heatmap's covariance about that
position. The values come from the landmarks by the measurements' own rules (specs.values), so a
reported value and the line drawn for it never disagree, and each value's uncertainty is the
delta method: var(v) = sum over its points of J S J', J the value's gradient in the point and S
the point's covariance, the points' errors taken as independent. Whether the spread is a
calibrated error is for train.py's spread loss and a held-out check to say; untrained, it is not.

ct_only is the path a raw CT takes at test time: E_ct and the decoder, no mask, jitted by the
caller (train.timing measures it).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

import jax
import jax.numpy as jnp
import numpy as np
from flax import nnx

from . import crops
from .specs import SEVEN, landmarks, values

HU_RANGE = (-1000.0, 3000.0)        # the CT is clipped here and divided by HU_SCALE: air -1, dense cortex 1 to 2
HU_SCALE = 1000.0


@dataclass(frozen=True)
class Config:
    """The network's sizes: the measurements it places (their landmarks are its outputs), the
    encoders' widths at the three scales (a half, a quarter and an eighth of the crop), and the
    crop it reads (crops.SHAPE at crops.SPACING_MM unless given)."""
    keys: Tuple[str, ...] = tuple(SEVEN)
    widths: Tuple[int, int, int] = (16, 32, 64)
    shape: Tuple[int, int, int] = crops.SHAPE
    spacing: float = crops.SPACING_MM
    groups: int = 8

    @property
    def n_landmarks(self) -> int:
        return len(landmarks(self.keys))


def ct_input(hu):
    """The CT channel as the encoder reads it: (batch, X, Y, Z, 1) in HU to a unit scale."""
    return jnp.clip(hu, *HU_RANGE) / HU_SCALE


class Block(nnx.Module):
    """Two 3x3x3 convolutions, each with group norm, and a residual, the first strided when the
    block halves the scale."""

    def __init__(self, cin: int, cout: int, groups: int, stride: int, rngs: nnx.Rngs):
        g = max(1, min(groups, cout))
        self.conv1 = nnx.Conv(cin, cout, (3, 3, 3), strides=stride, padding="SAME", rngs=rngs)
        self.norm1 = nnx.GroupNorm(cout, num_groups=g, rngs=rngs)
        self.conv2 = nnx.Conv(cout, cout, (3, 3, 3), padding="SAME", rngs=rngs)
        self.norm2 = nnx.GroupNorm(cout, num_groups=g, rngs=rngs)
        self.skip = nnx.Conv(cin, cout, (1, 1, 1), strides=stride, rngs=rngs) if (cin != cout or stride != 1) else None

    def __call__(self, x):
        h = nnx.gelu(self.norm1(self.conv1(x)))
        h = self.norm2(self.conv2(h))
        return nnx.gelu(h + (x if self.skip is None else self.skip(x)))


class Encoder(nnx.Module):
    """Three strided blocks: features at a half, a quarter and an eighth of the crop."""

    def __init__(self, cin: int, widths: Sequence[int], groups: int, rngs: nnx.Rngs):
        w0, w1, w2 = widths
        self.b1 = Block(cin, w0, groups, 2, rngs)
        self.b2 = Block(w0, w1, groups, 2, rngs)
        self.b3 = Block(w1, w2, groups, 2, rngs)

    def __call__(self, x) -> List[jnp.ndarray]:
        f1 = self.b1(x)
        f2 = self.b2(f1)
        return [f1, f2, self.b3(f2)]


def upsample_to(x, like):
    """x (batch, X, Y, Z, C) resized trilinearly to like's spatial shape."""
    return jax.image.resize(x, like.shape[:4] + x.shape[4:], "trilinear")


class Decoder(nnx.Module):
    """Up from the eighth to the half scale with the fused features of each scale beside, then
    one heatmap logit per landmark at the half scale."""

    def __init__(self, widths: Sequence[int], n_landmarks: int, groups: int, rngs: nnx.Rngs):
        w0, w1, w2 = widths
        self.up2 = Block(w2 + w1, w1, groups, 1, rngs)
        self.up1 = Block(w1 + w0, w0, groups, 1, rngs)
        self.head = nnx.Conv(w0, n_landmarks, (1, 1, 1), rngs=rngs)

    def __call__(self, feats: Sequence[jnp.ndarray]):
        f1, f2, f3 = feats
        h = self.up2(jnp.concatenate([upsample_to(f3, f2), f2], -1))
        h = self.up1(jnp.concatenate([upsample_to(h, f1), f1], -1))
        return self.head(h)


def heatmap_grid(crop_shape: Sequence[int], spacing: float, heat_shape: Sequence[int]) -> np.ndarray:
    """The crop's local millimetres of each heatmap voxel's centre, (N, 3): the crop's extent
    divided evenly into the heatmap's voxels, centred as the crop is (crops.CropFrame)."""
    ticks = []
    for n, m in zip(crop_shape, heat_shape):
        step = n * spacing / m
        ticks.append((np.arange(m) - (m - 1) / 2.0) * step)
    return np.stack(np.meshgrid(*ticks, indexing="ij"), -1).reshape(-1, 3)


def soft_argmax(logits, grid):
    """Each landmark's expected position and covariance under the softmax of its heatmap:
    logits (batch, X, Y, Z, K), grid (X Y Z, 3); returns (batch, K, 3) and (batch, K, 3, 3)."""
    b, k = logits.shape[0], logits.shape[-1]
    p = jax.nn.softmax(logits.reshape(b, -1, k), axis=1)                   # (batch, N, K)
    g = jnp.asarray(grid, logits.dtype)
    mean = jnp.einsum("bnk,ni->bki", p, g)
    d = g[None, :, None, :] - mean[:, None]                                # (batch, N, K, 3)
    cov = jnp.einsum("bnk,bnki,bnkj->bkij", p, d, d)
    return mean, cov


def value_sigma(points, cov, keys: Sequence[str]):
    """Each value's standard deviation by the delta method, (batch, M): the value's gradient in
    each point, from specs.values, against the point's covariance, the points independent."""
    jac = jax.vmap(jax.jacfwd(lambda P: values(P, keys, jnp)))(points)      # (batch, M, K, 3)
    var = jnp.einsum("bmki,bkij,bmkj->bm", jac, cov, jac)
    return jnp.sqrt(jnp.maximum(var, 0.0))


class Model(nnx.Module):
    """The two encoders, the shared decoder and the reading of its heatmaps (the module's
    docstring)."""

    def __init__(self, cfg: Config, rngs: nnx.Rngs):
        self.cfg = cfg
        self.ct = Encoder(1, cfg.widths, cfg.groups, rngs)
        self.mask = Encoder(2, cfg.widths, cfg.groups, rngs)
        self.decoder = Decoder(cfg.widths, cfg.n_landmarks, cfg.groups, rngs)

    def features(self, hu, masks) -> Tuple[List[jnp.ndarray], List[jnp.ndarray]]:
        return self.ct(ct_input(hu)), self.mask(masks)

    def read(self, logits) -> Dict[str, jnp.ndarray]:
        """Landmarks, their covariances, the values and their deltas from the heatmap logits."""
        grid = heatmap_grid(self.cfg.shape, self.cfg.spacing, logits.shape[1:4])
        points, cov = soft_argmax(logits, grid)
        return {"points": points, "cov": cov, "values": values(points, self.cfg.keys, jnp),
                "sigma": value_sigma(points, cov, self.cfg.keys)}

    def __call__(self, hu, masks, w) -> Dict[str, object]:
        """The fused pass: hu (batch, X, Y, Z, 1) in HU, masks (batch, X, Y, Z, 2) already down
        the ladder, w the fusion weight; the reading of the heatmaps and both encoders' features."""
        f_ct, f_mask = self.features(hu, masks)
        fused = [(1.0 - w) * a + w * b for a, b in zip(f_ct, f_mask)]
        out = self.read(self.decoder(fused))
        out["f_ct"], out["f_mask"] = f_ct, f_mask
        return out

    def ct_only(self, hu) -> Dict[str, jnp.ndarray]:
        """The test-time path: the CT alone, E_ct and the decoder, which is the fused pass at w 0
        without computing the mask's branch."""
        return self.read(self.decoder(self.ct(ct_input(hu))))

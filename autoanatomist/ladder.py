"""The degradation ladder, lambda from the instance mask to a soft threshold of the CT, and the
schedules of lambda and of the fusion weight w.

The privileged branch of the network (model.py) sees two channels beside the CT: the target
vertebra's mask and every vertebra's. lambda takes them down a ladder of three rungs, each a
third of [0, 1], each rung's progress a smoothstep so lambda's derivative is continuous within it:

1. identity fades (lambda 0 to 1/3): the target's channel is blended into every vertebra's, so at
   1/3 the branch no longer knows which voxels are the target's;
2. shape blurs (1/3 to 2/3): both channels are blurred by a Gaussian whose sigma grows to
   BLUR_MAX_MM, so the edges a mask states exactly become uncertain;
3. the mask gives way to the CT (2/3 to 1): both channels are blended into a soft threshold of the
   CT at BONE_HU (scanimport.intensity's dense bone), so at lambda 1 the branch sees a function of
   the CT alone, which a raw CT gives at test time.

Every step is a soft gate (gates.py), so the error of a network as a function of lambda, E(lambda),
has a derivative dE/dlambda that jax.grad computes (train.error_curve). The rungs and their order
are this module's design, from the owner's pasted notes (a perfect mask, then semantic bone, then
softer shapes, then HU thresholding), not a published schedule.

The schedules (Schedule) run lambda from 0 to 1 first and then the fusion weight w from 1 to 0,
each by a half cosine over its share of the training steps, so the branch is degraded before it is
taken away, and at the end the network reads the CT alone (w = 0), with no mask asked for.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

import jax.numpy as jnp

from . import gates

BLUR_MAX_MM = 4.0
THRESHOLD_WIDTH_HU = 60.0


def smoothstep(u):
    u = jnp.clip(u, 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def rung(lam, k: int):
    """How far along rung k (0, 1 or 2) lambda is, 0 to 1, smoothly."""
    return smoothstep(3.0 * lam - k)


def degrade(masks, hu, lam, spacing_mm: float = 2.0, bone_hu: float = gates.BONE_HU,
            width_hu: float = THRESHOLD_WIDTH_HU, blur_max_mm: float = BLUR_MAX_MM):
    """The privileged channels at lambda: masks (batch, X, Y, Z, 2), target then every vertebra,
    hu (batch, X, Y, Z, 1); returns (batch, X, Y, Z, 2)."""
    target, every = masks[..., 0], masks[..., 1]
    a = rung(lam, 0)
    target = (1.0 - a) * target + a * every
    b = rung(lam, 1)
    sigma = jnp.maximum(b * blur_max_mm / spacing_mm, 1e-3)
    max_sigma = blur_max_mm / spacing_mm
    target = gates.gaussian_blur(target, sigma, max_sigma)
    every = gates.gaussian_blur(every, sigma, max_sigma)
    c = rung(lam, 2)
    bone = gates.soft_threshold(hu[..., 0], bone_hu, width_hu)
    target = (1.0 - c) * target + c * bone
    every = (1.0 - c) * every + c * bone
    return jnp.stack([target, every], -1)


@dataclass(frozen=True)
class Schedule:
    """lambda and w over `steps` training steps: lambda from 0 to 1 over the shares lam_span of the
    steps, then w from 1 to 0 over w_span, each by a half cosine; before a span its start value
    holds and after it its end value."""
    steps: int
    lam_span: Tuple[float, float] = (0.15, 0.55)
    w_span: Tuple[float, float] = (0.45, 0.85)

    @staticmethod
    def ramp(t: float, span: Tuple[float, float]) -> float:
        u = (t - span[0]) / max(span[1] - span[0], 1e-12)
        u = min(max(u, 0.0), 1.0)
        return 0.5 * (1.0 - math.cos(math.pi * u))

    def at(self, step: int) -> Tuple[float, float]:
        """(w, lambda) at a step."""
        t = step / max(self.steps - 1, 1)
        return 1.0 - self.ramp(t, self.w_span), self.ramp(t, self.lam_span)

"""A synthetic population drawn from the generator's model, with each part of a person kept apart.

schwingcheck/columns.py draws a column as

    value = s^p * (mu + sd * (rho * z + sqrt(1 - rho^2) * e)) + error * n

and keeps only the value. To validate the synthetic population against the published series,
the parts have to be read on their own: the true anatomy (no measurement error, no floor), the
measured value (with error and the floor, as the rule sees it), and the patient's size. This
module draws the same model, vectorised over people, and returns all of them. It also opens the
model's settings to the axes the state-space exploration sweeps:

- scale_sd, rho, r_between, the error scale, the floor and the blend of a transitional body are
  the generator's own (columns.SYNTH, curve.ERROR_SCALES, curve's correlated arm);
- phi makes the level-specific part of a person's offset an AR(1) chain down the column, so that
  neighbouring levels are more alike than distant ones (the statespace model of TODO.md, item P
  step e, "What it needs"); at phi 0 it is the generator's independent draw at every level;
- sd_mode "size_removed" takes the size out of the table's SD and divides the mean by E[s^p], so
  that the true anatomy has the printed mean and SD at every level, where the generator, which
  adds its size on top of an SD that already holds the twelve specimens' sizes, spreads wider;
- sd_scale multiplies every SD of the table, the one free factor that sets the spread of the
  level-specific part against the published SDs (validate.py);
- loadings give a measure its own exponent on the size, s^(p x loading), in place of the
  generator's isometric s^p: the papers that print both sexes put the canal's and the pedicle's
  width at about a third of the body's (structure.isometry_table).

At the generator's settings (phi 0, sd_mode "printed") the values are those of
columns.draw_columns in distribution, not to the bit, since the stream is consumed in another
order (tests/test_synthval.py holds the moments to it).
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, replace
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from schwingcheck import LEVELS
from schwingcheck import columns as C
from schwingcheck import measures as MS

FLOOR = C.FLOOR
SD_MODES = ("printed", "size_removed")
MIN_RESIDUAL = 0.1          # the least share of the printed SD size_removed leaves a level, where the size would take all of it


@dataclass(frozen=True)
class Settings:
    """One point of the generator's state space. The defaults are the generator's (columns.SYNTH)."""
    name: str = "generator"
    scale_sd: float = C.SYNTH["scale_sd"]
    rho: float = C.SYNTH["rho"]
    phi: float = 0.0
    r_between: float = 0.0
    error_scale: float = 1.0
    sd_mode: str = "printed"
    floor: bool = True
    blend: float = C.SYNTH["blend"]
    sd_scale: float = 1.0
    loadings: Tuple[Tuple[str, float], ...] = ()     # (measure key without ":mean", loading on log s)

    def loading(self, key: str) -> float:
        return dict(self.loadings).get(key.split(":")[0], 1.0)

    def but(self, **kw) -> "Settings":
        return replace(self, **kw)

    def as_dict(self) -> dict:
        return asdict(self)


GENERATOR = Settings()


@dataclass
class Population:
    """n people of one phenotype: true and measured values (person, body, measure), the size of
    each person, the column's level names and the settings that drew them."""
    true: np.ndarray
    measured: np.ndarray
    scale: np.ndarray
    levels: List[str]
    keys: List[str]
    power: np.ndarray
    error: np.ndarray
    phenotype: str
    settings: Settings
    seed: int
    clipped: int = 0          # level cells where size_removed left only MIN_RESIDUAL of the SD

    def level_index(self, level: str) -> int:
        return self.levels.index(level)

    def floored(self) -> np.ndarray:
        """Where the floor holds a measured value, for the measures that scale with the size."""
        return (self.measured == FLOOR) & (self.power > 0)[None, None, :] & bool(self.settings.floor)


def size_moments(power: np.ndarray, scale_sd: float):
    """E[s^p] and E[s^2p] for log s ~ N(0, scale_sd^2), one per measure."""
    v = (np.asarray(power, float) * scale_sd) ** 2
    return np.exp(v / 2.0), np.exp(2.0 * v)


def calibrated(mu: np.ndarray, sd: np.ndarray, power: np.ndarray, settings: Settings):
    """The (measures, levels) means and SDs the model draws from. "printed" is the table as it is.
    "size_removed" solves E[s^p] mu' = mu and mu'^2 Var(s^p) + E[s^2p] sd'^2 = sd^2, so the true
    anatomy has the printed mean and SD; where the size alone would pass the printed SD, sd' is
    held at MIN_RESIDUAL of it and the cell is counted."""
    if settings.sd_mode == "printed":
        return mu, sd, 0
    if settings.sd_mode != "size_removed":
        raise ValueError("sd_mode is one of %r, not %r" % (SD_MODES, settings.sd_mode))
    e1, e2 = size_moments(power, settings.scale_sd)
    var_size = (mu / e1[:, None]) ** 2 * (e2 - e1 ** 2)[:, None]
    left = (sd ** 2 - var_size) / e2[:, None]
    floor = (MIN_RESIDUAL * sd) ** 2 / e2[:, None]
    clipped = int((left < floor).sum())
    return mu / e1[:, None], np.sqrt(np.maximum(left, floor)), clipped


def ar1(rng, m: int, n: int, w: int, phi: float) -> np.ndarray:
    """(n, w, m) standard normal draws, an AR(1) chain of correlation phi along the body axis."""
    a = rng.normal(size=(n, w, m))
    if abs(phi) < 1e-12:
        return a
    out = np.empty_like(a)
    out[:, 0] = a[:, 0]
    c = math.sqrt(1.0 - phi * phi)
    for b in range(1, w):
        out[:, b] = phi * out[:, b - 1] + c * a[:, b]
    return out


def draw(settings: Settings, n: int, seed: int, measures: Optional[Sequence[MS.Measure]] = None,
         phenotype: str = "typical") -> Population:
    """n people of one phenotype at one point of the state space, every measure of `measures`
    (the pool of 32 when none is given)."""
    measures = list(MS.pool() if measures is None else measures)
    keys = [MS.archive_key(m) for m in measures]
    power = MS.powers(measures)
    size_power = power * np.array([settings.loading(m.key) for m in measures])
    error = MS.errors(measures) * settings.error_scale
    ref = MS.reference(measures)
    levels, _, mu, sd = C.profiles(ref, keys, phenotype, settings.blend)
    mu, sd, clipped = calibrated(mu, sd * settings.sd_scale, size_power, settings)
    M, W = mu.shape
    rng = np.random.default_rng(seed)
    s = np.exp(rng.normal(0.0, settings.scale_sd, size=n)) if settings.scale_sd > 0 else np.ones(n)
    z = rng.normal(size=(n, M))
    if abs(settings.r_between) >= 1e-12:
        z = z @ C.offset_factor(M, settings.r_between).T
    a = ar1(rng, M, n, W, settings.phi)
    noise = rng.normal(size=(n, W, M))
    g = s[:, None] ** size_power[None, :]                                          # (n, M)
    rho = settings.rho
    dev = rho * z[:, None, :] + math.sqrt(1.0 - rho * rho) * a                     # (n, W, M)
    true = g[:, None, :] * (mu.T[None] + sd.T[None] * dev)
    measured = true + error[None, None, :] * noise
    if settings.floor:
        measured = np.where((power > 0)[None, None, :], np.maximum(measured, FLOOR), measured)
    return Population(true=true, measured=measured, scale=s, levels=list(levels), keys=keys, power=power,
                      error=error, phenotype=phenotype, settings=settings, seed=seed, clipped=clipped)


def moments(pop: Population, which: str = "true") -> Dict[str, np.ndarray]:
    """Mean, SD and quantiles over people, (body, measure) each."""
    x = getattr(pop, which)
    q = np.quantile(x, [0.005, 0.025, 0.5, 0.975, 0.995], axis=0)
    return {"mean": x.mean(0), "sd": x.std(0, ddof=1), "q005": q[0], "q025": q[1], "q50": q[2], "q975": q[3], "q995": q[4]}


def level_correlation(pop: Population, which: str = "true") -> np.ndarray:
    """(measure, body, body) correlation of one measure between the levels of one person."""
    x = getattr(pop, which)
    x = x - x.mean(0)
    x = x / x.std(0)
    return np.einsum("nbm,ncm->mbc", x, x) / x.shape[0]


def measure_correlation(pop: Population, which: str = "true") -> np.ndarray:
    """(body, measure, measure) correlation between measures at one level of one person."""
    x = getattr(pop, which)
    x = x - x.mean(0)
    x = x / x.std(0)
    return np.einsum("nbm,nbk->bmk", x, x) / x.shape[0]


def typical_levels() -> List[str]:
    return list(LEVELS)

"""Random-effects pooling of published series, for means and for log standard deviations.

Each series gives a mean, a population SD and a count. The means are pooled by restricted
maximum likelihood (REML) for the between-series variance tau^2, by Fisher scoring from the
DerSimonian-Laird estimate, with the 95 per cent prediction interval of Higgins, Thompson and
Spiegelhalter (2009), mean +/- t(k - 2) sqrt(tau^2 + SE^2), for where a new population's mean
falls; with two series the interval is not defined and is left NaN. The SDs are pooled the same
way on the log scale, each log SD with its large-sample variance 1 / (2 (n - 1)), so that a
synthetic SD can be set inside or outside the spread of published SDs.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np
from scipy import stats

REML_ITER = 200
REML_TOL = 1e-10


@dataclass
class Pooled:
    k: int
    mean: float
    se: float
    tau2: float
    i2: float
    q: float
    pi_low: float
    pi_high: float

    @property
    def tau(self) -> float:
        return math.sqrt(self.tau2)

    def as_dict(self) -> dict:
        return {"k": self.k, "mean": self.mean, "se": self.se, "tau": self.tau, "tau2": self.tau2, "i2": self.i2,
                "q": self.q, "pi_low": self.pi_low, "pi_high": self.pi_high}


def dersimonian_laird(y: np.ndarray, v: np.ndarray) -> float:
    w = 1.0 / v
    mu = (w * y).sum() / w.sum()
    q = (w * (y - mu) ** 2).sum()
    c = w.sum() - (w ** 2).sum() / w.sum()
    return max(0.0, (q - (len(y) - 1)) / c) if c > 0 else 0.0


def reml_tau2(y: np.ndarray, v: np.ndarray) -> float:
    """REML estimate of tau^2 by Fisher scoring, from the DL estimate, held at zero or above."""
    t2 = dersimonian_laird(y, v)
    for _ in range(REML_ITER):
        w = 1.0 / (v + t2)
        mu = (w * y).sum() / w.sum()
        grad = 0.5 * ((w ** 2) * ((y - mu) ** 2) - w).sum() + 0.5 * (w ** 2).sum() / w.sum()
        info = 0.5 * (w ** 2).sum()
        step = grad / info
        new = max(0.0, t2 + step)
        if abs(new - t2) < REML_TOL * max(1.0, t2):
            t2 = new
            break
        t2 = new
    return t2


def reml_rows(y: np.ndarray, v: np.ndarray) -> tuple:
    """reml_tau2 and the pooled mean for every row of y at once (rows are replicates of one cell,
    columns its series, v the series' within-series variances), for the simulations of power.py."""
    w = 1.0 / v
    mu = (y * w).sum(1) / w.sum()
    q = (w * (y - mu[:, None]) ** 2).sum(1)
    c = w.sum() - (w ** 2).sum() / w.sum()
    t2 = np.maximum(0.0, (q - (y.shape[1] - 1)) / c) if c > 0 else np.zeros(len(y))
    for _ in range(REML_ITER):
        w = 1.0 / (v[None, :] + t2[:, None])
        mu = (w * y).sum(1) / w.sum(1)
        grad = 0.5 * ((w ** 2) * (y - mu[:, None]) ** 2 - w).sum(1) + 0.5 * (w ** 2).sum(1) / w.sum(1)
        new = np.maximum(0.0, t2 + grad / (0.5 * (w ** 2).sum(1)))
        done = np.abs(new - t2) < REML_TOL * np.maximum(1.0, t2)
        t2 = new
        if done.all():
            break
    w = 1.0 / (v[None, :] + t2[:, None])
    return t2, (w * y).sum(1) / w.sum(1)


def pool(y: Sequence[float], v: Sequence[float]) -> Optional[Pooled]:
    """Pool estimates y with within-series variances v; None for fewer than two series."""
    y = np.asarray(y, float)
    v = np.asarray(v, float)
    ok = np.isfinite(y) & np.isfinite(v) & (v > 0)
    y, v = y[ok], v[ok]
    k = len(y)
    if k < 2:
        return None
    t2 = reml_tau2(y, v)
    w = 1.0 / (v + t2)
    mu = float((w * y).sum() / w.sum())
    se = float(math.sqrt(1.0 / w.sum()))
    w0 = 1.0 / v
    mu0 = (w0 * y).sum() / w0.sum()
    q = float((w0 * (y - mu0) ** 2).sum())
    i2 = max(0.0, (q - (k - 1)) / q) if q > 0 else 0.0
    if k >= 3:
        half = stats.t.ppf(0.975, k - 2) * math.sqrt(t2 + se * se)
        lo, hi = mu - half, mu + half
    else:
        lo = hi = float("nan")
    return Pooled(k=k, mean=mu, se=se, tau2=float(t2), i2=float(i2), q=q, pi_low=float(lo), pi_high=float(hi))


def pool_means(mean: Sequence[float], sd: Sequence[float], n: Sequence[float]) -> Optional[Pooled]:
    mean, sd, n = (np.asarray(a, float) for a in (mean, sd, n))
    return pool(mean, sd ** 2 / n)


def pool_log_sd(sd: Sequence[float], n: Sequence[float]) -> Optional[Pooled]:
    """Pooled log SD; exp of its mean and interval are SDs. The small-sample bias of log SD,
    1 / (2 (n - 1)), is added back so that each series' term estimates log sigma."""
    sd, n = np.asarray(sd, float), np.asarray(n, float)
    ok = (n > 1) & (sd > 0)
    y = np.log(sd[ok]) + 1.0 / (2.0 * (n[ok] - 1.0))
    v = 1.0 / (2.0 * (n[ok] - 1.0))
    return pool(y, v)


def pooled_sd(sd: Sequence[float], n: Sequence[float]) -> float:
    """The SD within series, pooled on n - 1 degrees of freedom each."""
    sd, n = np.asarray(sd, float), np.asarray(n, float)
    ok = (n > 1) & np.isfinite(sd)
    return float(math.sqrt(((n[ok] - 1) * sd[ok] ** 2).sum() / (n[ok] - 1).sum())) if ok.any() else float("nan")

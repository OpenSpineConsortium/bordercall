"""Every synthetic measure and level held to the published populations.

For each measure of the pool (the two end-plate inclinations left out, literature.py) and each
level a published series covers, the synthetic population drawn at a setting of the state space
is set beside:

- the pooled mean of the published series, by REML with its 95 per cent prediction interval
  (pooling.py): the synthetic mean is a plausible population when it falls inside that interval,
  and z_mean says by how many between-population SDs (sqrt(tau^2 + SE^2)) it misses the pool;
- the pooled SD of the published series on the log scale, with its interval: sd_ratio is the
  synthetic SD over the pooled SD, and the synthetic SD is a plausible spread when it falls inside;
- Panjabi's own mean and SD as the generator reads them (measures.arrays), which no published
  series here contains, so z_panjabi says where the reference the generator is built on sits
  among the others.

Where fewer than three series cover a cell there is no prediction interval; d_mean, the synthetic
mean's distance from the pooled (or single) published mean in Panjabi's SD at that level, the SD
the generator draws with, is given for every cell, so a shift reads as what it would cost the
rule: a population whose mean sits d SD from the table's.

The main comparison pools bone and CT series, the two that measure the bone itself; film
magnifies by 10 to 20 per cent and MRI reads soft-tissue edges, so they are compared on their own
(modality "film_mri"). Tan's SDs, whose conversion the reread could not settle
(literature.DISPERSION_UNCERTAIN), weight the pooled means and set tau like any other series', but
the published SD a synthetic SD is held to leaves them out: it is pooled over the other series
where two or more print one, and is the one series' SD where one does (k_sd says which).
lit_sd_with_uncertain is the SD with Tan's taken in, and every cell says whether Tan 2004 is its
only series, since many cells rest on him alone.
The true synthetic values are compared with bone and CT alike; the measured values carry the
generator's error on top, which a caliper on bone and a CT read add in part (references.py).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence

import numpy as np

from schwingcheck import LEVELS
from schwingcheck import measures as MS

from . import literature as L
from . import pooling as P
from .population import Population

MAIN_MODALITIES = ("bone", "ct")
MODALITY_SETS = {"bone_ct": ("bone", "ct"), "bone": ("bone",), "ct": ("ct",), "film_mri": ("film", "mri")}


def validated_measures(measures: Optional[Sequence[MS.Measure]] = None) -> List[MS.Measure]:
    """The pool's measures but those left out of validation (literature.LEFT_OUT_MEASURES)."""
    return [m for m in (MS.pool() if measures is None else measures) if L.measure_key(m.key) not in L.LEFT_OUT_MEASURES]


def cells(series: Iterable[L.Series], modalities: Sequence[str]) -> Dict[tuple, List[L.Series]]:
    """The usable series of these modalities by (reread key, level)."""
    out: Dict[tuple, List[L.Series]] = {}
    for s in series:
        if L.usable(s) and s.modality in modalities:
            out.setdefault((s.key, s.level), []).append(s)
    return out


@dataclass
class Literature:
    """What the published series of one measure and level say."""
    k: int
    papers: str
    mean: Optional[P.Pooled]
    log_sd: Optional[P.Pooled]
    log_sd_all: Optional[P.Pooled]
    single_mean: float
    single_sd: float
    k_sd: int = 0           # the series behind the published SD: Tan's left out, pooled when two or more

    @property
    def sd(self) -> float:
        return math.exp(self.log_sd.mean) if self.log_sd else self.single_sd


def literature_at(rows: List[L.Series]) -> Literature:
    """Pool the series of one cell: the means over all of them, the SD over the series whose SD is
    certain (pooled on the log scale where there are two or more, the one where there is one), and
    the SD over all of them for the sensitivity reading."""
    mean = np.array([s.mean for s in rows])
    sd = np.array([s.sd for s in rows])
    n = np.array([s.n for s in rows])
    certain = np.array([not s.sd_uncertain for s in rows])
    one = rows[0] if len(rows) == 1 else None
    one_certain = float(sd[certain][0]) if certain.sum() == 1 else float("nan")
    return Literature(k=len(rows), papers=";".join(sorted({s.paper for s in rows})),
                      mean=P.pool_means(mean, sd, n),
                      log_sd=P.pool_log_sd(sd[certain], n[certain]) if certain.sum() >= 2 else None,
                      log_sd_all=P.pool_log_sd(sd, n),
                      single_mean=one.mean if one else float("nan"),
                      single_sd=one_certain, k_sd=int(certain.sum()))


def synthetic_moments(pop: Population, archive_key: str, level: str, which: str) -> tuple:
    x = getattr(pop, which)[:, pop.level_index(level), pop.keys.index(archive_key)]
    return float(x.mean()), float(x.std(ddof=1))


def _z(value: float, lit: Literature) -> float:
    """How many between-population SDs a value misses the pool by; only with three series or
    more, as the prediction interval, since two give no usable tau."""
    if lit.mean is None or lit.k < 3:
        return float("nan")
    return (value - lit.mean.mean) / math.sqrt(lit.mean.tau2 + lit.mean.se ** 2)


def _inside(value: float, lo: float, hi: float) -> Optional[bool]:
    return None if not (math.isfinite(lo) and math.isfinite(hi)) else bool(lo <= value <= hi)


def compare(pops: Dict[str, Population], series: Sequence[L.Series], modality_set: str = "bone_ct",
            measures: Optional[Sequence[MS.Measure]] = None) -> List[dict]:
    """One row per (measure, level, setting, which) with a published series: the synthetic mean
    and SD beside the pooled literature and Panjabi."""
    measures = validated_measures(measures)
    by_cell = cells(series, MODALITY_SETS[modality_set])
    mu, sd = MS.arrays(measures, LEVELS)
    rows = []
    for j, m in enumerate(measures):
        key, ak = L.measure_key(m.key), MS.archive_key(m)
        for i, level in enumerate(LEVELS):
            found = by_cell.get((key, level))
            if not found:
                continue
            lit = literature_at(found)
            base = {"measure": key, "level": level, "kind": m.kind, "modalities": modality_set, "k": lit.k,
                    "papers": lit.papers, "panjabi_mean": float(mu[j, i]), "panjabi_sd": float(sd[j, i]),
                    "z_panjabi": _z(float(mu[j, i]), lit), "lit_sd": lit.sd, "k_sd": lit.k_sd,
                    "only_tan2004": lit.papers == "tan2004"}
            base["d_panjabi"] = ((base["panjabi_mean"] - (lit.mean.mean if lit.mean else lit.single_mean)) / base["panjabi_sd"])
            if lit.mean:
                base.update({"lit_mean": lit.mean.mean, "lit_se": lit.mean.se, "lit_tau": lit.mean.tau,
                             "lit_i2": lit.mean.i2, "pi_low": lit.mean.pi_low, "pi_high": lit.mean.pi_high})
            else:
                base.update({"lit_mean": lit.single_mean, "lit_se": float("nan"), "lit_tau": float("nan"),
                             "lit_i2": float("nan"), "pi_low": float("nan"), "pi_high": float("nan")})
            sd_lo, sd_hi = (math.exp(lit.log_sd.pi_low), math.exp(lit.log_sd.pi_high)) if lit.log_sd else (float("nan"),) * 2
            base.update({"lit_sd_low": sd_lo, "lit_sd_high": sd_hi,
                         "lit_sd_with_uncertain": math.exp(lit.log_sd_all.mean) if lit.log_sd_all else float("nan"),
                         "panjabi_sd_ratio": float(sd[j, i]) / lit.sd if lit.sd > 0 else float("nan")})
            for name, pop in pops.items():
                for which in ("true", "measured"):
                    m_syn, s_syn = synthetic_moments(pop, ak, level, which)
                    rows.append(dict(base, setting=name, which=which, syn_mean=m_syn, syn_sd=s_syn,
                                     z_mean=_z(m_syn, lit), mean_inside=_inside(m_syn, base["pi_low"], base["pi_high"]),
                                     d_mean=(m_syn - base["lit_mean"]) / base["panjabi_sd"],
                                     sd_ratio=s_syn / lit.sd if lit.sd > 0 else float("nan"),
                                     sd_inside=_inside(s_syn, sd_lo, sd_hi)))
    return rows


def summarise(rows: Sequence[dict], by: Sequence[str] = ("setting", "which")) -> List[dict]:
    """Per group: the cells compared, the share of synthetic means inside the prediction interval
    (where there is one), the median |z| of the means, the median SD ratio and its quartiles, and
    the share of synthetic SDs inside the SD interval."""
    groups: Dict[tuple, List[dict]] = {}
    for r in rows:
        groups.setdefault(tuple(r[b] for b in by), []).append(r)
    out = []
    for g, rs in sorted(groups.items()):
        inside = [r["mean_inside"] for r in rs if r["mean_inside"] is not None]
        sd_in = [r["sd_inside"] for r in rs if r["sd_inside"] is not None]
        z = np.array([abs(r["z_mean"]) for r in rs if math.isfinite(r["z_mean"])])
        d = np.array([abs(r["d_mean"]) for r in rs if math.isfinite(r["d_mean"])])
        ratio = np.array([r["sd_ratio"] for r in rs if math.isfinite(r["sd_ratio"])])
        out.append(dict(zip(by, g), cells=len(rs), with_interval=len(inside),
                        mean_inside=float(np.mean(inside)) if inside else float("nan"),
                        median_abs_z=float(np.median(z)) if len(z) else float("nan"),
                        median_abs_d=float(np.median(d)) if len(d) else float("nan"),
                        d_under_half=float((d < 0.5).mean()) if len(d) else float("nan"),
                        d_over_one=float((d > 1.0).mean()) if len(d) else float("nan"),
                        sd_ratio_median=float(np.median(ratio)) if len(ratio) else float("nan"),
                        sd_ratio_q1=float(np.quantile(ratio, 0.25)) if len(ratio) else float("nan"),
                        sd_ratio_q3=float(np.quantile(ratio, 0.75)) if len(ratio) else float("nan"),
                        with_sd_interval=len(sd_in), sd_inside=float(np.mean(sd_in)) if sd_in else float("nan")))
    return out

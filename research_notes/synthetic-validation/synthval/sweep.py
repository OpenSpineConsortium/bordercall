"""The generator's state space, one axis at a time and on a grid, read against the papers.

Each point is a Settings (population.py). At each, a population of typical columns is drawn and
read four ways: its spread against the published SDs (validate.py, bone and CT series), its
correlations (the neighbouring levels of one measure, and Griffith's four correlations of subject
means, structure.py), its quality indicators (qi.py), and, for the points that naming is run at,
the exact rule's accuracy (naming.py). The anomalous phenotypes are read for their indicators.

nearest() searches a grid of the four axes that set a population's spread and correlations,
the size's spread, the SDs' scale, rho and the between-measure correlation, for the point whose
synthetic SDs and Griffith correlations sit closest to the papers': the median log SD ratio
squared plus the mean squared distance of the four correlations from Griffith's men and women
taken together (structure.mixed_sex_r), since the synthetic population has no sex. It is the
nearest point of this space, not a fitted model of the population. The grid reaches no size
spread at all and a between-measure correlation of 0.6, since r_between stands in for the size
in the correlations and the two trade against each other; beyond_edges reads past each end of the
grid the nearest point sits on.
"""
from __future__ import annotations

import itertools
import math
from typing import Dict, List, Optional, Sequence

import numpy as np

from schwingcheck import measures as MS

from . import literature as L
from . import qi as Q
from . import structure as ST
from . import validate as V
from .population import GENERATOR, Population, Settings, draw

AXES = {
    "scale_sd": (0.0, 0.035, 0.05, 0.07, 0.10),
    "rho": (0.0, 0.25, 0.5, 0.75, 0.9),
    "phi": (0.0, 0.3, 0.6, 0.9),
    "r_between": (0.0, 0.2, 0.4),
    "error_scale": (0.5, 1.0, 2.0),
    "sd_scale": (0.7, 0.85, 1.0),
    "sd_mode": ("printed", "size_removed"),
}
GRID = {"scale_sd": (0.0, 0.01, 0.02, 0.035, 0.05, 0.07), "sd_scale": (0.6, 0.7, 0.8, 0.9, 1.0),
        "rho": (0.25, 0.5, 0.75, 0.9), "r_between": (0.0, 0.2, 0.4, 0.6)}
# Values past each end of GRID, read where the nearest point sits on that end, since a point on
# the grid's edge may have a nearer one past it. scale_sd and r_between end at 0 below, so nothing
# is read past their lower ends, and rho stops short of 1.
BEYOND = {"scale_sd": ((), (0.1,)), "sd_scale": ((0.5, 0.55), (1.1,)),
          "rho": ((0.0, 0.1), (0.95, 0.99)), "r_between": ((), (0.8,))}
LUMBAR = ST.LUMBAR


def one_at_a_time(axes: Dict[str, Sequence] = AXES, base: Settings = GENERATOR) -> List[Settings]:
    """The generator's own point, then each axis moved alone through its values."""
    out = [base]
    for axis, values in axes.items():
        for v in values:
            if getattr(base, axis) != v:
                out.append(base.but(name="%s=%s" % (axis, v), **{axis: v}))
    return out


def neighbour_correlation(pop: Population, which: str = "true") -> float:
    """The median over measures and lumbar levels of the correlation of a level with the next."""
    x = getattr(pop, which)
    idx = [pop.level_index(l) for l in LUMBAR]
    rs = []
    for m in range(x.shape[2]):
        for a, b in zip(idx, idx[1:]):
            rs.append(np.corrcoef(x[:, a, m], x[:, b, m])[0, 1])
    return float(np.nanmedian(rs))


def read_point(settings: Settings, series: Sequence[L.Series], n: int, seed: int,
               measures: Optional[Sequence[MS.Measure]] = None) -> dict:
    """Spread, correlations and quality indicators of one point's typical population."""
    measures = list(MS.pool() if measures is None else measures)
    pop = draw(settings, n, seed, measures)
    rows = V.compare({settings.name: pop}, series, "bone_ct", V.validated_measures(measures))
    sums = {s["which"]: s for s in V.summarise(rows)}
    out = dict(settings.as_dict(), n=n, seed=seed, clipped=pop.clipped, clipped_size_passes=pop.size_passes,
               sd_ratio_true=sums["true"]["sd_ratio_median"], sd_ratio_measured=sums["measured"]["sd_ratio_median"],
               sd_ratio_true_q1=sums["true"]["sd_ratio_q1"], sd_ratio_true_q3=sums["true"]["sd_ratio_q3"],
               neighbour_r=neighbour_correlation(pop))
    for r, (a, b, men, women) in zip(ST.subject_mean_correlations(pop), ST.GRIFFITH):
        out["griffith %s~%s" % (a, b)] = r["synthetic"]
    fl = Q.flags(pop)
    for k, v in Q.vertebra_rates(fl).items():
        out["qi vertebra " + k] = v
    for k, v in Q.person_rates(fl).items():
        out["qi person " + k] = v
    return out


def distance(point: dict) -> float:
    """How far a point sits from the papers: (log median SD ratio)^2 plus the mean squared distance
    of the four subject-mean correlations from Griffith's, his sexes taken together."""
    d_sd = math.log(point["sd_ratio_true"]) ** 2
    d_r = np.mean([(point["griffith " + pair] - target) ** 2 for pair, target in ST.griffith_targets().items()])
    return float(d_sd + d_r)


def nearest(series: Sequence[L.Series], n: int = 4000, seed: int = 11, grid: Dict[str, Sequence] = GRID,
            base: Settings = GENERATOR) -> List[dict]:
    """Every grid point read and scored by distance(), nearest first."""
    out = []
    keys = list(grid)
    for values in itertools.product(*(grid[k] for k in keys)):
        kw = dict(zip(keys, values))
        st = base.but(name="grid " + " ".join("%s=%s" % kv for kv in kw.items()), **kw)
        p = read_point(st, series, n, seed)
        p["distance"] = distance(p)
        out.append(p)
    return sorted(out, key=lambda p: p["distance"])


def beyond_edges(best: dict, series: Sequence[L.Series], n: int = 4000, seed: int = 11,
                 grid: Dict[str, Sequence] = GRID, base: Settings = GENERATOR,
                 beyond: Dict[str, tuple] = BEYOND) -> List[dict]:
    """The points past each end of the grid that the nearest point sits on, the other axes held at
    the nearest point's values, read and scored as the grid's are, nearest first."""
    out = []
    for axis, values in grid.items():
        lower, upper = beyond.get(axis, ((), ()))
        past = lower if best[axis] == min(values) else upper if best[axis] == max(values) else ()
        for x in past:
            kw = dict({k: best[k] for k in grid}, **{axis: x})
            p = read_point(base.but(name="past the grid, %s=%s" % (axis, x), **kw), series, n, seed)
            p["distance"] = distance(p)
            p["axis"] = axis
            out.append(p)
    return sorted(out, key=lambda p: p["distance"])


def phenotype_qi(settings: Settings, n: int, seed: int, phenotypes: Sequence[str]) -> List[dict]:
    """The quality indicators of each phenotype's population at one point."""
    out = []
    for ph in phenotypes:
        pop = draw(settings, n, seed, None, ph)
        fl = Q.flags(pop)
        row = {"phenotype": ph, "setting": settings.name}
        row.update({"vertebra " + k: v for k, v in Q.vertebra_rates(fl).items()})
        row.update({"person " + k: v for k, v in Q.person_rates(fl).items()})
        out.append(row)
    return out

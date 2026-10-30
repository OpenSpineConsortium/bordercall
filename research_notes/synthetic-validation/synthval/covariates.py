"""Covariates of the spine's shape, read both ways from what the papers print apart.

The owner's words of 2026-10-30, 02:55 UTC: "i want to demonstrate how this shows there are
demographic and sex and age ect covariate effects on spine morphology and hpw you can predict these
covariates based on the measurements or vice versa". The papers give no person's measurements, but
many print a cohort's men and women apart, or its age bands, or (Yu 2015) its body heights and
weights apart, each with a mean, an SD and a count. A difference read inside one paper carries none of
that paper's own shift (method, specimen, country), so every effect here is within a paper first and
pooled across papers second, as a meta-analysis pools, the populations kept apart as the owner asked
on 2026-10-29.

1. Effects, covariate on shape. Sex: every stratum a paper prints for both sexes on the same measure,
   level, side, group and technique gives one contrast, men minus women, as Hedges' g (the difference
   over the pooled within-sex SD, small-sample corrected). Age, body height and body weight: every
   series a paper prints over two or more bands of the variable gives a weighted least-squares slope
   of the band means on the bands' midpoints (weights n / sd^2), in the within-band SD per decade,
   per 100 mm or per 10 kg. A paper's strata at one cell (its age bands' sex contrasts, say) are
   different people and are combined by inverse variance; its cells of one measure share people, so
   a paper's value for a measure is the mean over its cells with the mean variance (no gain claimed
   for the shared people); the papers are then pooled by REML (pooling.pool), with the interval for
   the mean and, from three papers, for one more paper.

2. Prediction, held out by paper. For each paper, the effect is taken from the other papers alone
   (the same cell pooled over them, else the measure pooled over its cells), and applied to the
   held-out paper's population as a new population would be met: its sexes-pooled mean and SD known,
   as a published table without sexes gives them, and nothing of its own split. Shape to covariate:
   the posterior probability of male from one measure at a known level, a two-Gaussian classifier
   whose class means sit g within-sex SDs apart about the population's mean, scored on the held-out
   paper's own men and women (equal numbers): the AUC, the log loss against ln 2 for the base rate,
   and the same for the population's own split (the ceiling). Covariate to shape: the out-of-sample
   R^2 of the measure predicted from sex by the transferred effect, against the population's own
   split's R^2; for age, the band means predicted from the band's age by the transferred slope. Every
   expectation over a person is exact (Gaussian, by Gauss-Hermite quadrature), so no draw is made.

What this cannot do: combine measures. A person's measures share their size, so two measures' sex
evidence is not independent, and no paper prints the correlation within a person; one measure at one
level is the honest unit here, and the combination waits for measured people (the gold tier 3 CTs'
morphometry, with each person's age and sex), where the same functions run on rows of people.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
from numpy.polynomial.hermite_e import hermegauss
from scipy import stats

from . import pooling as P
from .literature import EXCLUDED_GROUP

OWN_SOURCE = "this paper"          # a paper's own people; a quoted study is that study's, met where it is a paper here
KINDS = ("length", "area", "angle")
ADULT = 18.0
OPEN_SPAN = 15.0                   # years a band open at one end is taken to span (">55" is 55 to 70)
NODES, WEIGHTS = hermegauss(40)
WEIGHTS = WEIGHTS / WEIGHTS.sum()


# ---- the rows a contrast may be read from -------------------------------------------------------

def usable(r: dict, vocabulary: Dict[str, dict]) -> bool:
    """A row of a paper's own people, of a human, on a measure with a kind, with a mean, an SD and
    a count of its own, in a group that is a population (not a stenosis, a size quartile or a
    figure's example)."""
    kind = vocabulary.get(r["base_key"], {}).get("kind")
    return (r["source_of_values"] == OWN_SOURCE and r["species"] != "pig" and kind in KINDS
            and all(isinstance(r[k], float) and math.isfinite(r[k]) for k in ("mean", "sd", "n"))
            and r["sd"] > 0 and r["n"] > 1 and not EXCLUDED_GROUP.search(r["group"] or "")
            and not EXCLUDED_GROUP.search(r["cohort"] or ""))


def stratum_key(r: dict, *leave_out: str) -> tuple:
    """Everything that names a printed stratum but the fields left out."""
    fields = ("paper", "cohort", "technique", "key", "base_key", "level", "sex", "group", "side", "definition", "modality")
    return tuple(r[f] for f in fields if f not in leave_out)


def largest(rows: Sequence[dict]) -> dict:
    return max(rows, key=lambda r: r["n"])


# ---- sex -------------------------------------------------------------------------------------------

@dataclass
class Contrast:
    """Men minus women in one printed stratum."""
    paper: str
    cohort: str
    base_key: str
    level: str
    group: str
    mean_m: float
    sd_m: float
    n_m: float
    mean_f: float
    sd_f: float
    n_f: float

    @property
    def sd_within(self) -> float:
        return math.sqrt(((self.n_m - 1) * self.sd_m ** 2 + (self.n_f - 1) * self.sd_f ** 2) / (self.n_m + self.n_f - 2))

    @property
    def g(self) -> float:
        """Hedges' g, the difference over the pooled within-sex SD with the small-sample factor."""
        j = 1.0 - 3.0 / (4.0 * (self.n_m + self.n_f) - 9.0)
        return j * (self.mean_m - self.mean_f) / self.sd_within

    @property
    def var_g(self) -> float:
        n = self.n_m + self.n_f
        return n / (self.n_m * self.n_f) + self.g ** 2 / (2.0 * n)


def sex_contrasts(rows: Sequence[dict], vocabulary: Dict[str, dict]) -> List[Contrast]:
    """Every stratum printed for both sexes, the largest row of each sex where one is printed twice."""
    by: Dict[tuple, Dict[str, List[dict]]] = {}
    for r in rows:
        if r["sex"] in ("male", "female") and usable(r, vocabulary):
            by.setdefault(stratum_key(r, "sex"), {}).setdefault(r["sex"], []).append(r)
    out = []
    for key, sexes in sorted(by.items()):
        if "male" in sexes and "female" in sexes:
            m, f = largest(sexes["male"]), largest(sexes["female"])
            out.append(Contrast(m["paper"], m["cohort"], m["base_key"], m["level"], m["group"],
                                m["mean"], m["sd"], m["n"], f["mean"], f["sd"], f["n"]))
    return out


# ---- age, body height and body weight ------------------------------------------------------------------

ORDINALS = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9}


def age_band(group: str) -> Optional[Tuple[float, float]]:
    """The years a group names, low and high, or None: "decade 20" and "Third Decade" are 20 to 29,
    "18-35", "21-40 years", "age 31-49 yr" as written, ">55", "60+" and "age >=70 yr" open above by
    OPEN_SPAN, "age <=30 yr" from ADULT. A group that names no age is None."""
    g = (group or "").strip().lower()
    m = re.fullmatch(r"decade (\d+)", g)
    if m:
        lo = float(m.group(1))
        return lo, lo + 9.0
    m = re.fullmatch(r"(\w+) decade", g)
    if m and m.group(1) in ORDINALS:
        lo = 10.0 * (ORDINALS[m.group(1)] - 1)
        return lo, lo + 9.0
    g = re.sub(r"^age\s*", "", re.sub(r"\s*(years|yr)$", "", g))
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)", g)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.fullmatch(r"(?:>=?|>)\s*(\d+)|(\d+)\s*\+", g)
    if m:
        lo = float(m.group(1) or m.group(2))
        return lo, lo + OPEN_SPAN
    m = re.fullmatch(r"<=?\s*(\d+)", g)
    if m:
        return ADULT, float(m.group(1))
    return None


def size_band(group: str, what: str) -> Optional[Tuple[float, float]]:
    """Yu 2015's body height (mm) and weight (kg) bands: "body height 1601-1699 mm", "<=1600 mm",
    ">=1800 mm", the open ends spanning as the next band does."""
    g = (group or "").strip().lower()
    if not g.startswith("body %s " % what):
        return None
    g = re.sub(r"\s*(mm|kg)$", "", g[len("body %s " % what):])
    span = 100.0 if what == "height" else 9.0
    m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", g)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.fullmatch(r">=\s*(\d+)", g)
    if m:
        return float(m.group(1)), float(m.group(1)) + span
    m = re.fullmatch(r"<=\s*(\d+)", g)
    if m:
        return float(m.group(1)) - span, float(m.group(1))
    return None


VARIABLES: Dict[str, Tuple[Callable[[str], Optional[Tuple[float, float]]], float, str]] = {
    "age": (age_band, 10.0, "per decade"),
    "body height": (lambda g: size_band(g, "height"), 100.0, "per 100 mm"),
    "body weight": (lambda g: size_band(g, "weight"), 10.0, "per 10 kg"),
}


@dataclass
class Gradient:
    """One printed series over bands of a variable: the band midpoints, means, SDs and counts."""
    variable: str
    paper: str
    cohort: str
    base_key: str
    level: str
    sex: str
    x: np.ndarray
    mean: np.ndarray
    sd: np.ndarray
    n: np.ndarray

    @property
    def sd_within(self) -> float:
        return float(math.sqrt(((self.n - 1) * self.sd ** 2).sum() / (self.n - 1).sum()))

    def slope(self) -> Tuple[float, float]:
        """The weighted least-squares slope of the band means on the midpoints, in the within-band
        SD per the variable's unit, and its variance."""
        w = self.n / self.sd ** 2
        xb = (w * self.x).sum() / w.sum()
        sxx = (w * (self.x - xb) ** 2).sum()
        b = (w * (self.x - xb) * self.mean).sum() / sxx
        unit, s = VARIABLES[self.variable][1], self.sd_within
        return float(b * unit / s), float(unit ** 2 / sxx / s ** 2)


def gradients(rows: Sequence[dict], vocabulary: Dict[str, dict], variable: str) -> List[Gradient]:
    """Every series printed over two or more bands of the variable, the adult bands alone for age."""
    band_of = VARIABLES[variable][0]
    by: Dict[tuple, List[Tuple[Tuple[float, float], dict]]] = {}
    for r in rows:
        band = band_of(r["group"]) if usable(r, vocabulary) else None
        if band is None or (variable == "age" and band[0] < ADULT):
            continue
        by.setdefault(stratum_key(r, "group"), []).append((band, r))
    out = []
    for key, items in sorted(by.items()):
        bands: Dict[Tuple[float, float], dict] = {}
        for band, r in items:
            if band not in bands or r["n"] > bands[band]["n"]:
                bands[band] = r
        if len(bands) < 2:
            continue
        order = sorted(bands)
        r0 = bands[order[0]]
        out.append(Gradient(variable, r0["paper"], r0["cohort"], r0["base_key"], r0["level"], r0["sex"],
                            np.array([(lo + hi) / 2.0 for lo, hi in order]), np.array([bands[b]["mean"] for b in order]),
                            np.array([bands[b]["sd"] for b in order]), np.array([bands[b]["n"] for b in order])))
    return out


# ---- pooled across papers ----------------------------------------------------------------------------

def inverse_variance(values: Sequence[Tuple[float, float]]) -> Tuple[float, float]:
    """Independent estimates combined: the weighted mean and its variance."""
    w = np.array([1.0 / v for _, v in values])
    y = np.array([e for e, _ in values])
    return float((w * y).sum() / w.sum()), float(1.0 / w.sum())


def effect_of(item) -> Tuple[float, float]:
    return (item.g, item.var_g) if isinstance(item, Contrast) else item.slope()


def by_paper_cell(items: Sequence) -> Dict[Tuple[str, str, str], Tuple[float, float, int]]:
    """Per (paper, measure, level) the paper's strata there combined by inverse variance, with how
    many strata."""
    groups: Dict[Tuple[str, str, str], list] = {}
    for it in items:
        groups.setdefault((it.paper, it.base_key, it.level), []).append(effect_of(it))
    return {k: inverse_variance(v) + (len(v),) for k, v in groups.items()}


def paper_values(cells: Dict[Tuple[str, str, str], Tuple[float, float, int]], base_key: str,
                 level: Optional[str] = None, without: Optional[str] = None) -> Dict[str, Tuple[float, float]]:
    """One value per paper for a measure (at one level, or over its levels: the mean of its cells with
    the mean variance, since its cells share people), leaving one paper out."""
    per: Dict[str, list] = {}
    for (paper, key, lv), (e, v, _) in cells.items():
        if key == base_key and (level is None or lv == level) and paper != without:
            per.setdefault(paper, []).append((e, v))
    return {p: (float(np.mean([e for e, _ in vs])), float(np.mean([v for _, v in vs]))) for p, vs in per.items()}


def pooled(values: Dict[str, Tuple[float, float]]) -> Optional[dict]:
    """The papers' values pooled by REML, or the one paper's own with its interval; None for none."""
    if not values:
        return None
    if len(values) == 1:
        (e, v), = values.values()
        half = 1.96 * math.sqrt(v)
        return {"papers": 1, "mean": e, "se": math.sqrt(v), "ci_low": e - half, "ci_high": e + half, "tau": float("nan"),
                "pi_low": float("nan"), "pi_high": float("nan")}
    p = P.pool([e for e, _ in values.values()], [v for _, v in values.values()])
    return {"papers": p.k, "mean": p.mean, "se": p.se, "ci_low": p.mean - 1.96 * p.se, "ci_high": p.mean + 1.96 * p.se,
            "tau": p.tau, "pi_low": p.pi_low, "pi_high": p.pi_high}


def effects(items: Sequence, variable: str) -> List[dict]:
    """Per measure, the papers pooled: the effect in within-group SDs (Hedges' g for sex, the slope
    per unit otherwise) with its intervals, and how many papers, cells and strata stand behind it."""
    cells = by_paper_cell(items)
    out = []
    for key in sorted({k for _, k, _ in cells}):
        got = pooled(paper_values(cells, key))
        mine = {c: v for c, v in cells.items() if c[1] == key}
        out.append(dict(got, variable=variable, measure=key, cells=len(mine), strata=sum(v[2] for v in mine.values()),
                        levels=len({c[2] for c in mine}), papers_named=";".join(sorted({c[0] for c in mine}))))
    return out


def transfer(cells: Dict[Tuple[str, str, str], Tuple[float, float, int]], paper: str, base_key: str, level: str) -> Tuple[float, str]:
    """The effect for a held-out paper's cell from the other papers alone: the same cell pooled over
    them, else the measure over its cells; NaN and "none" where no other paper prints the measure."""
    for scope, lv in (("cell", level), ("measure", None)):
        got = pooled(paper_values(cells, base_key, lv, without=paper))
        if got is not None:
            return got["mean"], scope
    return float("nan"), "none"


# ---- held-out prediction, both ways ------------------------------------------------------------------

def binormal_auc(mu_a: float, sd_a: float, mu_b: float, sd_b: float) -> float:
    """P(a draw of a exceeds a draw of b) for two Gaussians."""
    return float(stats.norm.cdf((mu_a - mu_b) / math.sqrt(sd_a ** 2 + sd_b ** 2)))


def expected_log_loss(logit: Callable[[np.ndarray], np.ndarray], mu_m: float, sd_m: float, mu_f: float, sd_f: float) -> float:
    """The mean log loss of P(male | x) = sigmoid(logit(x)) over equal numbers of men and women."""
    xm, xf = mu_m + sd_m * NODES, mu_f + sd_f * NODES
    loss_m = (WEIGHTS * np.logaddexp(0.0, -logit(xm))).sum()
    loss_f = (WEIGHTS * np.logaddexp(0.0, logit(xf))).sum()
    return float(0.5 * (loss_m + loss_f))


def gaussian_logit(mu_m: float, sd_m: float, mu_f: float, sd_f: float) -> Callable[[np.ndarray], np.ndarray]:
    def logit(x):
        return stats.norm.logpdf(x, mu_m, sd_m) - stats.norm.logpdf(x, mu_f, sd_f)
    return logit


def sex_prediction(c: Contrast, g: float) -> dict:
    """One held-out stratum, the effect g taken from other papers. The population as a sexless table
    gives it: its mean and SD over equal numbers of men and women; the classifier puts the sexes g
    within-sex SDs apart about that mean. Scored on the stratum's own men and women."""
    mu = 0.5 * (c.mean_m + c.mean_f)
    total = math.sqrt(0.5 * (c.sd_m ** 2 + c.sd_f ** 2) + 0.25 * (c.mean_m - c.mean_f) ** 2)
    within = total / math.sqrt(1.0 + 0.25 * g * g)
    half = 0.5 * g * within
    own_auc = binormal_auc(c.mean_m, c.sd_m, c.mean_f, c.sd_f)
    auc = 0.5 if g == 0 else (own_auc if g > 0 else 1.0 - own_auc)
    loss = expected_log_loss(gaussian_logit(mu + half, within, mu - half, within), c.mean_m, c.sd_m, c.mean_f, c.sd_f)
    ceiling = expected_log_loss(gaussian_logit(c.mean_m, c.sd_m, c.mean_f, c.sd_f), c.mean_m, c.sd_m, c.mean_f, c.sd_f)
    none = 0.5 * (c.sd_m ** 2 + (c.mean_m - mu) ** 2) + 0.5 * (c.sd_f ** 2 + (c.mean_f - mu) ** 2)
    with_sex = 0.5 * (c.sd_m ** 2 + (c.mean_m - mu - half) ** 2) + 0.5 * (c.sd_f ** 2 + (c.mean_f - mu + half) ** 2)
    return {"g_own": c.g, "g_transfer": g, "auc_own": max(own_auc, 1.0 - own_auc), "auc_transfer": auc,
            "log_loss_base": math.log(2.0), "log_loss_transfer": loss, "log_loss_own": ceiling,
            "r2_transfer": 1.0 - with_sex / none, "r2_own": 1.0 - 0.5 * (c.sd_m ** 2 + c.sd_f ** 2) / none}


def gradient_prediction(gr: Gradient, slope: float) -> dict:
    """One held-out series over bands, the slope (within-band SDs per unit) taken from other papers:
    the band means predicted from the bands' midpoints about the series' own mean, the R^2 out of
    sample over its people against the series' own weighted fit; and the youngest band against the
    oldest told apart by the measure, the transferred slope's sign giving the direction."""
    unit, s = VARIABLES[gr.variable][1], gr.sd_within
    w = gr.n / gr.n.sum()
    mu, xb = float((w * gr.mean).sum()), float((w * gr.x).sum())
    none = float((w * (gr.sd ** 2 + (gr.mean - mu) ** 2)).sum())
    pred = mu + slope * s / unit * (gr.x - xb)
    own_b = gr.slope()[0]
    own = mu + own_b * s / unit * (gr.x - xb)
    auc = binormal_auc(gr.mean[-1], gr.sd[-1], gr.mean[0], gr.sd[0])
    return {"slope_own": own_b, "slope_transfer": slope,
            "r2_transfer": 1.0 - float((w * (gr.sd ** 2 + (gr.mean - pred) ** 2)).sum()) / none,
            "r2_own": 1.0 - float((w * (gr.sd ** 2 + (gr.mean - own) ** 2)).sum()) / none,
            "auc_own": max(auc, 1.0 - auc), "auc_transfer": 0.5 if slope == 0 else (auc if slope > 0 else 1.0 - auc),
            "span": float(gr.x[-1] - gr.x[0])}


def held_out(items: Sequence, variable: str) -> List[dict]:
    """Every stratum or series scored with the effect from the other papers alone."""
    cells = by_paper_cell(items)
    out = []
    for it in items:
        effect, scope = transfer(cells, it.paper, it.base_key, it.level)
        if scope == "none":
            continue
        got = sex_prediction(it, effect) if isinstance(it, Contrast) else gradient_prediction(it, effect)
        out.append(dict(got, variable=variable, paper=it.paper, cohort=it.cohort, measure=it.base_key, level=it.level,
                        stratum=getattr(it, "group", getattr(it, "sex", "")), transfer_from=scope,
                        n=float(it.n_m + it.n_f) if isinstance(it, Contrast) else float(it.n.sum())))
    return out


def summary(rows: Sequence[dict]) -> List[dict]:
    """Per variable over the held-out strata, each paper one vote (its strata's median first): the
    median AUC and R^2, transferred and own, and how often the transferred effect had the own sign."""
    out = []
    for variable in sorted({r["variable"] for r in rows}):
        rs = [r for r in rows if r["variable"] == variable]
        papers = sorted({r["paper"] for r in rs})

        def per_paper(key):
            return [float(np.median([r[key] for r in rs if r["paper"] == p])) for p in papers]
        own_key = "g_own" if variable == "sex" else "slope_own"
        tr_key = "g_transfer" if variable == "sex" else "slope_transfer"
        out.append({"variable": variable, "papers": len(papers), "strata": len(rs),
                    "auc_transfer": float(np.median(per_paper("auc_transfer"))), "auc_own": float(np.median(per_paper("auc_own"))),
                    "r2_transfer": float(np.median(per_paper("r2_transfer"))), "r2_own": float(np.median(per_paper("r2_own"))),
                    "same_sign": float(np.mean([np.sign(r[own_key]) == np.sign(r[tr_key]) for r in rs])),
                    **({"log_loss_transfer": float(np.median(per_paper("log_loss_transfer"))),
                        "log_loss_own": float(np.median(per_paper("log_loss_own"))), "log_loss_base": math.log(2.0)}
                       if variable == "sex" else {})})
    return out

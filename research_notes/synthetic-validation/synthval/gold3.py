"""Gold tier 3's real CTs on the bounds card: two cohorts measured by the morphometry engine, scored
as check() scores a generator, from the per-sex moments the grid printed.

SchwingNet's gate word `morphometry covariates` (job 40878978, 2026-10-30, at SchwingNet c656299)
joined the engine's rows for every admitted gold tier 3 CT with each person's sex and age and
printed, for each member, measure and level, the men's and the women's count, mean and SD, Hedges'
g and its variance, the correlation with the level above within each sex, and the age slope per
decade within each sex (report.txt, read whole by parse). The per-person tables stay on the grid,
so the card's tests are made here on those moments, with bounds.py's own verdicts:

- each cell's mean and SD, the two sexes pooled (pooled), against the interval for a new
  population's mean and SD, at the reference_n people check() scores every cohort at;
- each step of the card both of whose levels a member has, its sampling variance from the two
  levels' pooled SDs and their covariance, which the within-sex correlations and the sexes' shift
  give (pooled_cov) in place of the persons check() pairs;
- the sex test as check() makes it, the sign where the card's interval for a new population's
  contrast clears zero, and beside it, for every cell, whether the cohort's g lies inside that
  interval widened by its own variance;
- the age slope, standardised by each sex's SD and pooled over the sexes by inverse variance,
  against the card's interval for a new population's slope: a record, since check() makes no test
  on the age slope and the card says the slope's spread between populations is not identified.

The engine's keys are the card's base keys, except that the card names pedicle_w "pedicle",
averages a pedicle's two sides (":mean") and keeps the papers' definitions apart in brackets, of
which the engine's are the three-point disc mean and the chord along the pedicle's axis, and its
pedicle_incl_sag and pedicle_incl_trans are the engine's pedicle_angle_transverse and
pedicle_angle_sagittal (the aliases grid/bordercall/morphometry/__main__.py takes). A disc printed
between two levels is placed at the upper, as papers_table places the papers' discs.

Nothing the report prints is passed over in silence; what is not scored is named, with why
(not_scored, in each member's summary):

- a card cell of film or MRI, the cohorts being CT read at true size: the card's interpedicular
  distance is pooled from films alone (Hinck 1966, Amonoo-Kuofi 1982, Chaudhary 2015, none corrected
  for magnification), so its cells and its steps, which rest on those papers, are left out, and so
  is the MRI cell of the lower end-plate's area at L3;
- a measure the card holds under another definition: the card's spinous_length is Tan 2004's SPL,
  which is Panjabi's, from the upper end-plate's centre to the tip, where the engine's runs from the
  canal's posterior wall (bordercall's paper-tables/validation/mapping_audit.csv; scanimport's
  geometry.py);
- an engine key no paper of the card prints;
- a cell whose one sex's mean the report withholds (its disc_h_mean is shown only where its persons
  are each of its three heights' and their means are shown), and the steps that would read it.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from synthval import bounds as B

MEMBERS = ("autopet", "totalseg")
MEMBER_NAMES = {"autopet": "autoPET (ENHANCE.PET)", "totalseg": "TotalSegmentator"}
RANGE = "T10-L5"
CARD_TO_ENGINE = {
    "body_d_mid": "body_d_mid", "body_w_mid": "body_w_mid", "canal_ap": "canal_ap", "canal_area": "canal_area",
    "canal_w": "canal_w", "disc_h_ant": "disc_h_ant", "disc_h_mid": "disc_h_mid", "disc_h_post": "disc_h_post",
    "disc_h_mean [three points]": "disc_h_mean", "endplate": "endplate", "endplate_area": "endplate_area",
    "endplate_depth": "endplate_depth", "endplate_lower": "endplate_lower", "endplate_lower_area": "endplate_lower_area",
    "endplate_lower_depth": "endplate_lower_depth", "foramen_h": "foramen_h", "h_ant": "h_ant", "h_mid": "h_mid",
    "h_post": "h_post", "interpedicular": "interpedicular", "pedicle": "pedicle_w",
    "pedicle_chord [along the axis]": "pedicle_chord", "pedicle_h": "pedicle_h",
    "pedicle_incl_sag:mean": "pedicle_angle_transverse", "pedicle_area:mean": "pedicle_area",
    "pedicle_incl_trans:mean": "pedicle_angle_sagittal", "transverse_width": "transverse_width"}
CT = "bone and CT"
DEFINITION_DIFFERS = {
    "spinous_length": "the card's is Tan 2004's SPL, Panjabi's, from the upper end-plate's centre to the tip; "
                      "the engine's runs from the canal's posterior wall"}
BETWEEN_LEVELS = ("disc_h_", "foramen_h")
FIELDS = 27
FAMILIES = ("body and end plate", "disc and foramen", "pedicle and canal", "posterior elements")


def family_of(key: str) -> str:
    """The engine's families of measures, which the engine builds apart (body.py, column.py with the
    discs and foramina, pedicle.py and canal.py) and which pass or fail the card apart."""
    if key.startswith(("pedicle", "interpedicular", "canal")):
        return FAMILIES[2]
    if key.startswith(("disc_h", "foramen")):
        return FAMILIES[1]
    if key.startswith(("transverse", "spinous", "lamina", "facet")):
        return FAMILIES[3]
    return FAMILIES[0]


@dataclass(frozen=True)
class Moments:
    """One member's line at a measure and level: each sex's count, mean and SD, g and its variance,
    the correlation with the level above within each sex, and the age slope within each sex."""
    level_printed: str
    n_m: float
    mean_m: float
    sd_m: float
    n_f: float
    mean_f: float
    sd_f: float
    g: float
    var_g: float
    r_m: float
    r_f: float
    slope_m: float
    slope_se_m: float
    slope_f: float
    slope_se_f: float


def _num(text: str) -> float:
    return float("nan") if text == "-" else float(text)


def level_of(measure: str, printed: str) -> str:
    """The card's level for a printed level: a disc or a foramen between two levels at the upper."""
    if measure.startswith(BETWEEN_LEVELS) and "-" in printed and printed != RANGE:
        return printed.split("-")[0]
    return printed


def parse(text: str) -> Dict[Tuple[str, str, str], Moments]:
    """Every data line of the report, keyed by member, engine key and the card's level; a line of
    another shape is the report's prose and is passed over, a data line that does not hold its
    fields where the header says raises."""
    out: Dict[Tuple[str, str, str], Moments] = {}
    for line in text.splitlines():
        t = line.split()
        if len(t) < 2 or t[0] != "-" or t[1] not in MEMBERS + ("verse",):
            continue
        if len(t) != FIELDS or (t[4], t[8], t[12], t[15], t[20]) != ("M", "F", "g", "r", "a"):
            raise ValueError("not a data line of the join report: %r" % line)
        member, key, printed = t[1], t[2], t[3]
        v = [_num(t[i]) for i in (5, 6, 7, 9, 10, 11, 13, 14, 16, 18, 21, 22, 24, 25)]
        out[member, key, level_of(key, printed)] = Moments(printed, *v)
    return out


def pooled(m: Moments) -> Tuple[float, float, float]:
    """The two sexes as one population: its count, mean and SD (ddof 1), from each sex's moments."""
    n = m.n_m + m.n_f
    mean = (m.n_m * m.mean_m + m.n_f * m.mean_f) / n
    ss = (m.n_m - 1) * m.sd_m ** 2 + (m.n_f - 1) * m.sd_f ** 2 + m.n_m * m.n_f / n * (m.mean_m - m.mean_f) ** 2
    return n, mean, math.sqrt(ss / (n - 1))


def pooled_cov(upper: Moments, lower: Moments) -> float:
    """The covariance of the two levels over both sexes: each sex's within covariance (the lower
    line's correlation with the level above times the two SDs) and the sexes' shared shift, each
    sex weighted by its count at the lower level; nan where a sex's correlation is not printed."""
    n_m, n_f = lower.n_m, lower.n_f
    n = n_m + n_f
    within = ((n_m - 1) * lower.r_m * upper.sd_m * lower.sd_m + (n_f - 1) * lower.r_f * upper.sd_f * lower.sd_f)
    shift = n_m * n_f / n * (upper.mean_m - upper.mean_f) * (lower.mean_m - lower.mean_f)
    return (within + shift) / (n - 1)


def step_variance(upper: Moments, lower: Moments, at: float) -> float:
    """The sampling variance of a member's step at `at` people: the paired difference's variance
    where both correlations are printed, else the two levels' variances as if unpaired, as
    bounds._step_sampling falls back."""
    _, _, sd_u = pooled(upper)
    _, _, sd_l = pooled(lower)
    cov = pooled_cov(upper, lower)
    if not math.isfinite(cov):
        cov = 0.0
    return max(sd_u ** 2 + sd_l ** 2 - 2.0 * cov, 0.0) / at


def age_slope(m: Moments) -> Tuple[float, float]:
    """The slope per decade over each sex's SD, the sexes pooled by inverse variance, and its SE."""
    parts = [(s / sd, e / sd) for s, e, sd in ((m.slope_m, m.slope_se_m, m.sd_m), (m.slope_f, m.slope_se_f, m.sd_f))
             if math.isfinite(s) and math.isfinite(e) and e > 0 and sd > 0]
    if not parts:
        return float("nan"), float("nan")
    w = [1.0 / e ** 2 for _, e in parts]
    return sum(wi * s for wi, (s, _) in zip(w, parts)) / sum(w), 1.0 / math.sqrt(sum(w))


def card_cells(card: B.Card) -> List[dict]:
    """The card's cells of bone and CT whose measure the engine measures by the card's definition."""
    cells, _ = card.of_kind(B.ALL)
    return [c for c in cells if c["measure"] in CARD_TO_ENGINE and c["modality"] == CT]


def _papers(text: str) -> set:
    return {p for p in str(text).split(";") if p}


def card_steps(card: B.Card) -> List[dict]:
    """The card's steps of a measure the engine measures whose every paper holds that measure in a
    cell of bone and CT, so that no step read inside a film's papers is scored against a CT."""
    cells, steps = card.of_kind(B.ALL)
    ct_papers: Dict[str, set] = {}
    for c in cells:
        if c["modality"] == CT:
            ct_papers.setdefault(c["measure"], set()).update(_papers(c["strata_list"]))
    return [s for s in steps if s["measure"] in CARD_TO_ENGINE
            and _papers(s["papers"]) and _papers(s["papers"]) <= ct_papers.get(s["measure"], set())]


def not_scored(moments: Dict[Tuple[str, str, str], Moments], card: B.Card, member: str) -> dict:
    """What the member's report holds that the score leaves out, each with why: engine keys no
    paper of the card prints, measures the card holds under another definition, the card's film and
    MRI cells at the member's levels, and the cells whose one sex's mean the report withholds."""
    mine = {(k, lv) for m, k, lv in moments if m == member}
    keys = {k for k, _ in mine}
    engine_keys = set(CARD_TO_ENGINE.values())
    cells, _ = card.of_kind(B.ALL)
    other = {}
    for c in cells:
        key = CARD_TO_ENGINE.get(c["measure"])
        if key and c["modality"] != CT and (key, c["level"]) in mine:
            other.setdefault((c["measure"], c["modality"]), []).append(c["level"])
    withheld = sorted("%s %s" % (k, m.level_printed) for (mb, k, lv), m in moments.items()
                      if mb == member and k in engine_keys and lv != RANGE
                      and not (math.isfinite(m.mean_m) and math.isfinite(m.mean_f)))
    return {"keys_not_on_card": sorted(keys - engine_keys - set(DEFINITION_DIFFERS)),
            "definition_differs": {k: why for k, why in DEFINITION_DIFFERS.items() if k in keys},
            "cells_not_ct": [{"measure": m, "modality": mod, "levels": lvs} for (m, mod), lvs in sorted(other.items())],
            "withheld_cells": withheld}


def _cell_row(member: str, c: dict, m: Moments, at: float) -> Tuple[dict, List[dict]]:
    n, mean, sd = pooled(m)
    row = {"member": member, "measure": c["measure"], "key": CARD_TO_ENGINE[c["measure"]],
           "family": family_of(CARD_TO_ENGINE[c["measure"]]), "level": c["level"],
           "level_printed": m.level_printed, "n": n, "mean": mean, "sd": sd, "mean_m": m.mean_m, "mean_f": m.mean_f,
           "card_mean": c["mean"], "mean_low": c["mean_low"], "mean_high": c["mean_high"]}
    verdicts = []
    v = B.mean_verdict(c, at, mean, sd)
    row.update(mean_z=v["z"], mean_pass=v["passed"])
    verdicts.append(v)
    v = B.sd_verdict(c, n, sd, True, at)
    if v is not None:
        row.update(card_sd_low=c["sd_low"], card_sd_high=c["sd_high"], sd_z=v["z"], sd_pass=v["passed"])
        verdicts.append(v)
    if math.isfinite(c.get("sex_g", float("nan"))) and math.isfinite(m.g):
        spread = math.sqrt(c["sex_g_between"] ** 2 + m.var_g)
        row.update(sex_g=m.g, sex_g_se=math.sqrt(m.var_g), card_sex_g=c["sex_g"], sex_g_new_low=c["sex_g_new_low"],
                   sex_g_new_high=c["sex_g_new_high"], sex_g_papers=c["sex_g_papers"], sex_z=(m.g - c["sex_g"]) / spread,
                   sex_inside=bool(abs(m.g - c["sex_g"]) <= B.Z * spread),
                   sex_inside_card=bool(c["sex_g_new_low"] <= m.g <= c["sex_g_new_high"]))
        if B.clear_of_zero(c, "sex_g"):
            passed = bool(math.copysign(1.0, m.g) == math.copysign(1.0, c["sex_g"]))
            row.update(sex_pass=passed)
            verdicts.append({"test": "sex", "z": m.g / math.sqrt(m.var_g), "passed": passed})
    slope, se = age_slope(m)
    if math.isfinite(c.get("age_slope", float("nan"))) and math.isfinite(slope):
        spread = math.sqrt(c["age_slope_between"] ** 2 + se ** 2)
        row.update(age_slope=slope, age_slope_se=se, card_age_slope=c["age_slope"], age_new_low=c["age_slope_new_low"],
                   age_new_high=c["age_slope_new_high"], age_z=(slope - c["age_slope"]) / spread,
                   age_inside=bool(abs(slope - c["age_slope"]) <= B.Z * spread),
                   age_inside_card=bool(c["age_slope_new_low"] <= slope <= c["age_slope_new_high"]))
    return row, verdicts


def score(moments: Dict[Tuple[str, str, str], Moments], card: B.Card, member: str,
          reference_n: float = B.REFERENCE_N) -> dict:
    """One member scored on the card as check() scores a cohort: its cells, its steps and the
    summary with the verdict against the bar of every paper held out; a cell where the member has
    fewer than reference_n people is left out and counted, as check() leaves it, a cell whose one
    sex's mean the report withholds is left out and counted apart (withheld_cells), and what else
    the report holds that is not scored is named (not_scored)."""
    rows, steps, verdicts, short, withheld = [], [], [], 0, 0
    for c in card_cells(card):
        m = moments.get((member, CARD_TO_ENGINE[c["measure"]], c["level"]))
        if m is None:
            continue
        if not math.isfinite(m.mean_m) or not math.isfinite(m.mean_f):
            withheld += 1
            continue
        if m.n_m + m.n_f < reference_n:
            short += 1
            continue
        row, made = _cell_row(member, c, m, reference_n)
        rows.append(row)
        verdicts += made
    for s in card_steps(card):
        key = CARD_TO_ENGINE[s["measure"]]
        a = moments.get((member, key, s["upper"])) if key else None
        b = moments.get((member, key, s["lower"])) if key else None
        if a is None or b is None or not all(math.isfinite(x) for x in (a.mean_m, a.mean_f, b.mean_m, b.mean_f)):
            continue
        if min(a.n_m + a.n_f, b.n_m + b.n_f) < reference_n:
            continue
        step = pooled(b)[1] - pooled(a)[1]
        v = B.step_verdict(s, step, step_variance(a, b, reference_n))
        steps.append({"member": member, "measure": s["measure"], "key": key, "family": family_of(key),
                      "upper": s["upper"], "lower": s["lower"],
                      "step": step, "card_step": s["step"], "step_low": s["step_low"], "step_high": s["step_high"],
                      "step_z": v["z"], "step_pass": v["passed"]})
        verdicts.append(v)
    summary = B.summarise(verdicts, card.bar(B.ALL), bool(card.calibration))
    summary.update(reference_n=reference_n, short_cells=short, withheld_cells=withheld,
                   not_scored=not_scored(moments, card, member))
    return {"member": member, "cells": rows, "steps": steps, "summary": summary}


def covariate_record(rows: List[dict], prefix: str) -> dict:
    """How many of a member's cells carry the contrast or slope, how many lie inside the card's
    interval for a new population as the card gives it (inside_card) and inside it widened by the
    member's own error (inside), and the z-scores' mean and root mean square (1 where the card's
    spread is right)."""
    zs = [r[prefix + "_z"] for r in rows if prefix + "_z" in r and math.isfinite(r[prefix + "_z"])]
    inside = sum(bool(r[prefix + "_inside"]) for r in rows if prefix + "_inside" in r)
    inside_card = sum(bool(r[prefix + "_inside_card"]) for r in rows if prefix + "_inside_card" in r)
    if not zs:
        return {"cells": 0}
    return {"cells": len(zs), "inside_card": inside_card, "share_inside_card": inside_card / len(zs),
            "inside": inside, "share_inside": inside / len(zs), "mean_z": sum(zs) / len(zs),
            "rms_z": math.sqrt(sum(z * z for z in zs) / len(zs))}


def by_family(rows: List[dict], steps: List[dict]) -> Dict[str, Dict[str, dict]]:
    """Each test's count passed and made by family of measures, the families together first."""
    out: Dict[str, Dict[str, dict]] = {}
    for fam in ("every family",) + FAMILIES:
        mine = [r for r in rows if fam == "every family" or r["family"] == fam]
        st = [s for s in steps if fam == "every family" or s["family"] == fam]
        got = {}
        for test, items in (("mean", mine), ("sd", mine), ("step", st)):
            made = [x[test + "_pass"] for x in items if test + "_pass" in x]
            if made:
                got[test] = {"made": len(made), "passed": int(sum(made)), "rate": sum(made) / len(made)}
        out[fam] = got
    return out


def by_measure(rows: List[dict], steps: List[dict]) -> List[dict]:
    """Each engine key's cells and steps: how many pass each test and the mean z of each."""
    out = []
    for key in sorted({r["key"] for r in rows} | {s["key"] for s in steps}):
        mine = [r for r in rows if r["key"] == key]
        rec = {"key": key}
        for test in ("mean", "sd", "sex", "age"):
            zs = [r[test + "_z"] for r in mine if test + "_z" in r]
            flag = test + ("_inside" if test in ("sex", "age") else "_pass")
            if zs:
                rec.update({test + "_cells": len(zs), test + "_inside": sum(bool(r[flag]) for r in mine if flag in r),
                            test + "_mean_z": sum(zs) / len(zs)})
        st = [s for s in steps if s["key"] == key]
        if st:
            rec.update(step_cells=len(st), step_inside=sum(s["step_pass"] for s in st),
                       step_mean_z=sum(s["step_z"] for s in st) / len(st))
        if mine:
            rec["card_sex_g"] = _mean([r.get("card_sex_g", float("nan")) for r in mine])
            rec["sex_g"] = _mean([r.get("sex_g", float("nan")) for r in mine])
            rec["sex_g_new_low"] = _mean([r.get("sex_g_new_low", float("nan")) for r in mine])
            rec["sex_g_new_high"] = _mean([r.get("sex_g_new_high", float("nan")) for r in mine])
            rec["sd_ratio"] = _mean([_sd_ratio(r) for r in mine])
        out.append(rec)
    return out


def _sd_ratio(r: dict) -> float:
    """The member's pooled SD over the middle of the card's interval for a new population's SD."""
    low, high = r.get("card_sd_low", float("nan")), r.get("card_sd_high", float("nan"))
    if not (math.isfinite(low) and math.isfinite(high) and low > 0):
        return float("nan")
    return r["sd"] / math.sqrt(low * high)


def _mean(xs: List[float]) -> float:
    xs = [x for x in xs if math.isfinite(x)]
    return sum(xs) / len(xs) if xs else float("nan")

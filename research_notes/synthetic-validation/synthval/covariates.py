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
   different people and are combined by inverse variance, while two strata of the same people (one
   group read as two variants of a measure, Bach 2019's mean disc height by three points and by two
   rims) are one value, their mean with the mean variance; its cells of one measure share people, so
   a paper's value for a measure is the mean over its cells with the mean variance (no gain claimed
   for the shared people); the papers are then pooled by REML (pooling.pool), with the interval for
   the mean and, from three papers, for one more paper.

   Where the sexes come from. The full snapshot is series.csv, which keeps no man's or woman's row
   where the paper prints both with an SD and a count (the reread's series.py pools them into one
   row of sex "pooled") or prints the sexes together with an SD beside them (that row alone), so it
   holds no sex apart of Masharawi 2021's foramina, Chaudhary 2015's interpedicular distances,
   Abbas 2021's, Olsewski 1990's, Yu 2015's or a dozen other papers' tables. The contrasts read
   those rows from the sexes' snapshot beside it (papers_table.load_rows_sexes: every sex series
   series.py made from the readings and did not write, held to pool back to the snapshot's own
   rows), so every printed sex enters, and the full snapshot, which the selection's tables and the
   gradients read, stays as it is.

   Which strata, and their counts. A stratum is of adults: a group whose age band starts below ADULT
   (Bach's First Decade, his 10s, which hold people of 14) is left out of the sex contrasts as it is
   of the age gradients. One technique per cohort, measure and level, the selection's rule 4 (bone,
   then CT, MRI, film, mixed; "same" before "close"), since a paper that measures its people twice
   (Mitra 2002's cadavers on CT and directly) has one set of people. One set of people per cohort,
   technique, measure and level, the selection's rule 5: where the paper prints the sexes of the
   whole cohort (group empty), its strata's sexes are the same people again and are left out (Bach
   2019's whole 240 by sex beside his decades by sex, Duman 2026's and Griffith 2016's whole
   beside their age bands), as the selection takes the whole before its strata; the whole is also
   the reading the rule's tables meet, its within-sex SD spanning every age as a sexless table's
   does (so Chaudhary 2015's Table II, Table I's means again without the SDs under the district's
   name, is its whole's again). Two groups printing the same men's and women's means, SDs and
   counts are one, as in the selection's rule 5. At least MIN_PER_SEX people of each sex: a sex of fewer gives its own mean
   to no better than sd / sqrt(n), over 0.45 within-sex SDs, the size of the effects measured, and
   the normal approximation to g's variance that the pooling's weights rest on fails at one to
   three degrees of freedom; Mitra 2002's two women at one level gave g = 9.7, which as one cell's
   pooled g carried a quarter to a third of the synthetic per-cell gain. Every pair of both sexes
   that does not enter is recorded with why (sex_strata's dropped). A row the snapshot gives the
   cohort's whole count (literature.COHORT_COUNT: the paper printed none beside it) takes its
   stratum's own count: the count the paper prints for that group and sex elsewhere (STRATUM_COUNTS,
   from the reread's readings and cohort files), else the register's group count times the cohort's
   share of the sex where the paper counts its groups and its sexes but not the one within the
   other (register.stratum_counts), else the cohort's count split evenly over the strata it prints
   at that cell, said in the stratum's count_from. Bach's 240 CTs are 131 women and 109 men, 8 to 25
   a decade and sex (his Table 1), where every one of his decade-by-sex strata had carried 240.

   Means alone. A paper that prints a stratum's men's and women's means and counts but no SD for
   either (Eisenstein 1977, Amonoo-Kuofi 1985's mid-body depth; Mitra 2002's, two women a stratum,
   fall to MIN_PER_SEX) still gives the
   difference; its g is read against a within-sex SD made from a sexless SD: the paper's own SD
   of the same stratum with the sexes together where it prints one, the two sexes'
   pooling inverted exactly with their counts, since it is the same people measured the same way;
   else the pooled within-person SD of the other papers' series at the same measure and placed level
   in the paper's own modality class (strata._pool, as the tables pool it, the papers in `without`
   left out too), narrowed half and half by the paper's own difference, sqrt(sd^2 - d^2 / 4), as the
   tables are split into sexes. The second is the SD the rule's table reads, so the g moves a table
   by the paper's own difference in its units; it takes the paper's scale to be the pool's, true
   within a modality class to within its calibration, and a stratum whose class no other paper
   prints (Amonoo-Kuofi 1982's body widths on film), or whose difference is wider than the pool
   allows, gives no contrast. Near that edge the narrowed SD is small and the g large, though the
   table it moves still moves by the paper's own difference in millimetres or degrees, and its
   variance carries the size. Each contrast says which SD it was read against (sd_from) and carries
   it (sd_within), with where its counts came from (count_from), so that every g is made again
   from its record. A stratum printed with one sex's SD and not the other's gives none.

2. Prediction, held out by paper. For each paper, the effect is taken from the other papers alone
   (the same cell pooled over them, else the measure pooled over its cells), and applied to the
   held-out paper's population as a new population would be met: its sexes-pooled mean and SD known,
   as a published table without sexes gives them, and nothing of its own split. Shape to covariate:
   the posterior probability of male from one measure at a known level, a two-Gaussian classifier
   whose class means sit g within-sex SDs apart about the population's mean, scored on the held-out
   paper's own men and women (equal numbers): the AUC, the log loss against ln 2 for the base rate,
   and the same for the population's own split (the ceiling); only a stratum that prints both its
   SDs is scored so, since the score is over its own people's spread. Covariate to shape: the out-of-sample
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

from . import literature as L
from . import pooling as P
from .literature import EXCLUDED_GROUP

OWN_SOURCE = "this paper"          # a paper's own people; a quoted study is that study's, met where it is a paper here
KINDS = ("length", "area", "angle")
ADULT = 18.0
OPEN_SPAN = 15.0                   # years a band open at one end is taken to span (">55" is 55 to 70)
NODES, WEIGHTS = hermegauss(40)
WEIGHTS = WEIGHTS / WEIGHTS.sum()
META_POOL = "meta_pool"            # a meta-analysis's pool of other studies, which may hold any paper here

# The year a paper's ordinal decades start from where it does not mean the decade of life: Bach
# 2019's Tables 2 to 5 name Table 1's 10s to 70s First to Seventh Decade (the reread's reading of
# Table 1: "decade 10 is the 10-19 group (First Decade)").
ORDINAL_DECADE_FROM = {"bach2019": 10.0}

# Counts of people a paper prints for a stratum on a page the stratum's rows do not carry, which
# the snapshot fills with the cohort's whole count (literature.COHORT_COUNT), by (paper, cohort,
# group, sex), each with where it is printed.
BACH_TABLE_1 = "Bach 2019 Table 1 (p. e108): people per decade and sex, as the reread reads it"
BACH_DECADES = ("First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh")
BACH_WOMEN, BACH_MEN = (8, 25, 18, 23, 25, 17, 15), (8, 19, 17, 8, 23, 22, 12)
STRATUM_COUNTS: Dict[Tuple[str, str, str, str], Tuple[float, str]] = {
    **{("bach2019", "usf_ct240", "%s Decade" % d, sex): (float(n), BACH_TABLE_1)
       for sex, counts in (("female", BACH_WOMEN), ("male", BACH_MEN)) for d, n in zip(BACH_DECADES, counts)},
    **{("chen2011", "chongqing_ct83", group, sex): (n, "Chen 2011 Tables 2 and 3: 430 and 400 end-plates, ten a person "
                                                      "(the reread's cohort file)")
       for group in ("superior endplate", "inferior endplate") for sex, n in (("male", 43.0), ("female", 40.0))},
    **{("chaudhary2015", "sonepat_ap_films", "sonepat District", sex): (150.0, "Chaudhary 2015: 300 films, 150 of each sex "
                                                                            "(the reread's cohort file)")
       for sex in ("male", "female")},
}
# Counts a paper prints of items, not people, on a stratum's own rows: by (paper, cohort, sex, the count
# printed), the people it stands for and where that is printed.
ITEM_COUNTS: Dict[Tuple[str, str, str, float], Tuple[float, str]] = {
    ("chen2011", "chongqing_ct83", sex, items): (people, "Chen 2011 Tables 2 and 3: %d end-plates of %d %s, ten a "
                                                         "person (the reread's cohort file)" % (items, people, who))
    for sex, items, people, who in (("male", 430.0, 43.0, "men"), ("female", 400.0, 40.0, "women"))}
# The definitions the selection keeps (papers_table.DEFINITIONS_ALL): Panjabi's, close to it, or a key he
# does not print; a row whose measure differs from his is left out of the contrasts as it is of the tables.
DEFINITIONS = ("same", "close", "none")
MIN_PER_SEX = 5.0                  # people of each sex for a stratum's contrast to enter (the docstring says why)
EVEN_SPLIT = "the cohort's count split evenly over the strata it prints at the cell (no count of the stratum's own is printed)"
# Why a pair of both sexes gives no contrast (sex_strata's dropped).
CHILDREN = "a stratum of children (its age band starts below ADULT)"
ANOTHER_TECHNIQUE = "another technique on the same people (rule 4)"
STRATUM_OF_WHOLE = "a stratum of a cohort whose whole the paper prints by sex at the cell (rule 5)"
PRINTED_TWICE = "the same men's and women's means, SDs and counts printed again under another group"
FEW_PER_SEX = "fewer than MIN_PER_SEX people of a sex"
ONE_SD = "one sex's SD printed and not the other's"
NO_SD = "means alone, and no sexless SD to read them against (none in the paper's modality class, or the difference too wide)"
OWN_SEXLESS_SD = "the paper's own SD of the stratum, sexes together, the pooling of the sexes inverted"
OTHERS_POOLED_SD = "the other papers' pooled SD at the cell in the paper's modality class, narrowed half and half"
PRINTED_SD = "printed"


# ---- the rows a contrast may be read from -------------------------------------------------------

def usable(r: dict, vocabulary: Dict[str, dict], need_sd: bool = True) -> bool:
    """A row of a paper's own people, of a human, on a measure with a kind and a definition the
    selection keeps (DEFINITIONS), with a mean, a count of its own and, `need_sd`, an SD, in a group
    that is a population (not a stenosis, a size quartile or a figure's example) and not a
    meta-analysis's pool."""
    kind = vocabulary.get(r["base_key"], {}).get("kind")
    numbers = ("mean", "sd", "n") if need_sd else ("mean", "n")
    return (r["source_of_values"] == OWN_SOURCE and r["species"] != "pig" and kind in KINDS
            and r.get("vs_panjabi") in DEFINITIONS
            and all(isinstance(r[k], float) and math.isfinite(r[k]) for k in numbers)
            and (not need_sd or r["sd"] > 0) and r["n"] > 1 and not EXCLUDED_GROUP.search(r["group"] or "")
            and not EXCLUDED_GROUP.search(r["cohort"] or "") and r.get("technique") != META_POOL)


def adult(r: dict) -> bool:
    """A row of adults: its group names no age band, or one that starts at ADULT or later."""
    band = age_band(r["group"], r["paper"])
    return band is None or band[0] >= ADULT


def stratum_key(r: dict, *leave_out: str) -> tuple:
    """Everything that names a printed stratum but the fields left out."""
    fields = ("paper", "cohort", "technique", "key", "base_key", "level", "sex", "group", "side", "definition", "modality")
    return tuple(r[f] for f in fields if f not in leave_out)


def largest(rows: Sequence[dict]) -> dict:
    """Of a sex's rows of one stratum, the one with an SD and then the most people."""
    return max(rows, key=lambda r: (isinstance(r["sd"], float) and math.isfinite(r["sd"]), r["n"]))


# ---- each stratum's own count ----------------------------------------------------------------------

def _cell_of_row(r: dict) -> tuple:
    return tuple(r[f] for f in ("paper", "cohort", "technique", "key", "level", "side", "definition"))


def strata_printed(rows_at_cell: Sequence[dict]) -> int:
    """The strata of people a paper prints at one cell: each group's two sexes, a group printed with
    the sexes together alone, and never the cohort's whole beside its parts; where the whole cohort
    is printed by sex, its two sexes alone, as rule 5 reads them (sex_pairs)."""
    sexed = {(r["group"], r["sex"]) for r in rows_at_cell if r["sex"] in ("male", "female")}
    if {("", "male"), ("", "female")} <= sexed:
        return 2
    groups = {g for g, _ in sexed}
    whole = {(r["group"], "whole") for r in rows_at_cell if r["sex"] in L.WHOLE_SEXES and r["group"] and r["group"] not in groups}
    return max(1, len(sexed | whole))


def printed_counts() -> Dict[Tuple[str, str, str, str], Tuple[float, str]]:
    """STRATUM_COUNTS with the register's group-by-sex shares beside them (register.stratum_counts)."""
    from . import register as RG
    out = dict(RG.stratum_counts(RG.load()))
    out.update(STRATUM_COUNTS)
    return out


def own_counts(rows: Sequence[dict], printed: Optional[Dict[tuple, Tuple[float, str]]] = None) -> List[dict]:
    """The rows with each one that carries its cohort's whole count given its stratum's own, as the
    module's docstring says, and where it came from in count_from (the row's own note otherwise)."""
    at_cell: Dict[tuple, List[dict]] = {}
    for r in rows:
        at_cell.setdefault(_cell_of_row(r), []).append(r)
    out = []
    for r in rows:
        items = ITEM_COUNTS.get((r["paper"], r["cohort"], r["sex"], r["n"]))
        if items is not None:
            out.append(dict(r, n=items[0], count_from=items[1]))
            continue
        if r.get("n_note", "") != L.COHORT_COUNT:
            out.append(dict(r, count_from=r.get("n_note", "")))
            continue
        printed = printed_counts() if printed is None else printed
        got = printed.get((r["paper"], r["cohort"], r["group"], r["sex"]))
        n, why = got if got else (r["n"] / strata_printed(at_cell[_cell_of_row(r)]), EVEN_SPLIT)
        out.append(dict(r, n=float(n), count_from=why))
    return out


# ---- sex -------------------------------------------------------------------------------------------

@dataclass
class Contrast:
    """Men minus women in one printed stratum. A stratum printed with means alone carries no SD of
    either sex (NaN) and the within-sex SD it is read against in `within`, with where that came
    from in sd_from; key, technique and modality name the stratum's measure as the tables do."""
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
    within: float = float("nan")
    sd_from: str = PRINTED_SD
    count_from: str = ""
    key: str = ""
    technique: str = ""
    modality: str = ""

    @property
    def sds_printed(self) -> bool:
        return math.isfinite(self.sd_m) and math.isfinite(self.sd_f)

    @property
    def sd_within(self) -> float:
        if not self.sds_printed:
            return self.within
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


def technique_rank(r: dict) -> tuple:
    """The selection's rule 4 order of techniques on one set of people: bone, CT, MRI, film, mixed,
    then "same" before "close" before the rest."""
    definitions = ("same", "close", "none", "differs")
    return (L.MODALITY_ORDER.index(r["modality"]) if r["modality"] in L.MODALITY_ORDER else len(L.MODALITY_ORDER),
            definitions.index(r["vs_panjabi"]) if r.get("vs_panjabi") in definitions else len(definitions))


def has_sd(r: dict) -> bool:
    return isinstance(r["sd"], float) and math.isfinite(r["sd"]) and r["sd"] > 0


def one_set_of_people(pairs: Dict[tuple, Tuple[dict, dict]]) -> Tuple[Dict[tuple, Tuple[dict, dict]], List[tuple]]:
    """Rule 5 on the pairs of one technique: per cohort, technique, measure and level, the whole
    cohort's pair alone where it is printed; else every group's, a pair whose men's and women's
    means, SDs and counts another group prints again counted once, as the selection's rule 5 counts
    two such groups (two groups' means alone may agree to the 0.1 mm printed, as Eisenstein 1977's
    Zulu and Sotho canals do, and their counts tell them apart). The pairs kept, and the rest as
    (men's row, women's row, why)."""
    at: Dict[tuple, List[tuple]] = {}
    for k, (m, f) in pairs.items():
        at.setdefault((m["paper"], m["cohort"], m["technique"], m["key"], m["level"]), []).append(k)
    kept, dropped = {}, []
    for cell, keys in sorted(at.items()):
        whole = [k for k in keys if pairs[k][0]["group"] == ""]
        seen = set()
        order = sorted(keys, key=lambda k: (k not in whole, not all(has_sd(r) for r in pairs[k]),
                                            -(pairs[k][0]["n"] + pairs[k][1]["n"]), k))
        for k in order:
            m, f = pairs[k]
            means = tuple((round(r["mean"], 6), round(r["sd"], 6) if has_sd(r) else None, r["n"]) for r in (m, f))
            if whole and k not in whole:
                dropped.append((m, f, STRATUM_OF_WHOLE))
            elif means in seen:
                dropped.append((m, f, PRINTED_TWICE))
            else:
                seen.add(means)
                kept[k] = (m, f)
    return {k: kept[k] for k in sorted(kept)}, dropped


def sex_pairs(rows: Sequence[dict], vocabulary: Dict[str, dict]) -> Tuple[Dict[tuple, Tuple[dict, dict]], List[tuple]]:
    """Every stratum printed for both sexes with a mean and a count, as (men's row, women's row)
    with each stratum's own count, the row of each sex with an SD and the most people where one is
    printed twice; kept where it is of adults, on the best technique of its cohort, measure and
    level (rule 4), and the only set of its people there (one_set_of_people). The pairs kept, and
    the rest as (men's row, women's row, why)."""
    by: Dict[tuple, Dict[str, List[dict]]] = {}
    for r in own_counts(rows):
        if r["sex"] in ("male", "female") and usable(r, vocabulary, need_sd=False):
            by.setdefault(stratum_key(r, "sex"), {}).setdefault(r["sex"], []).append(r)
    pairs = {k: (largest(s["male"]), largest(s["female"])) for k, s in sorted(by.items()) if "male" in s and "female" in s}
    dropped = [(m, f, CHILDREN) for m, f in pairs.values() if not (adult(m) and adult(f))]
    pairs = {k: (m, f) for k, (m, f) in pairs.items() if adult(m) and adult(f)}
    best: Dict[tuple, tuple] = {}
    for m, _ in pairs.values():
        cell = (m["paper"], m["cohort"], m["key"], m["level"])
        best[cell] = min(best.get(cell, technique_rank(m)), technique_rank(m))
    on_best = {}
    for k, (m, f) in pairs.items():
        if technique_rank(m) == best[m["paper"], m["cohort"], m["key"], m["level"]]:
            on_best[k] = (m, f)
        else:
            dropped.append((m, f, ANOTHER_TECHNIQUE))
    kept, same = one_set_of_people(on_best)
    return kept, dropped + same


def sexless_row(m: dict, rows_at_cell: Sequence[dict]) -> Optional[dict]:
    """The paper's own row of the same stratum with the sexes together and an SD: the same group, or
    the cohort's whole where the sexes are printed under one group alone at the cell."""
    groups = {r["group"] for r in rows_at_cell if r["sex"] in ("male", "female")}
    for r in rows_at_cell:
        if (r["sex"] in L.WHOLE_SEXES and isinstance(r["sd"], float) and math.isfinite(r["sd"]) and r["sd"] > 0
                and (r["group"] == m["group"] or (r["group"] == "" and len(groups) == 1))):
            return r
    return None


def modality_class(modality: str) -> Tuple[str, ...]:
    from . import papers_table as PT
    for _, mods in PT.MODALITY_CLASSES:
        if modality in mods:
            return mods
    return (modality,)


def sexless_pools(rows: Sequence[dict]) -> Dict[Tuple[str, str], list]:
    """The selection's usable series (papers_table.select_all, on the full snapshot's rows alone,
    never the sexes' snapshot's) by measure and placed level: what a stratum printed with means
    alone is read against where it prints no SD of its own."""
    from . import papers_table as PT
    out: Dict[Tuple[str, str], list] = {}
    for s in PT.select_all([r for r in rows if not r.get("apart")])[0]:
        at = PT.place(s.key, s.level, s.paper)
        if L.usable(s) and at is not None:
            out.setdefault((s.key, at), []).append(s)
    return out


def others_pooled_sd(m: dict, pools: Dict[Tuple[str, str], list], without: Sequence[str]) -> Optional[float]:
    """The within-person SD the tables pool at the stratum's cell over the other papers' series in
    its modality class, the papers in `without` left out too; None where none is left."""
    from . import papers_table as PT
    from . import strata as ST
    mods = modality_class(m["modality"])
    rest = [s for s in pools.get((m["key"], PT.place(m["key"], m["level"], m["paper"])), [])
            if s.paper != m["paper"] and s.paper not in without and s.modality in mods]
    return ST._pool(rest).sd if rest else None


def within_of_means(m: dict, f: dict, rows_at_cell: Sequence[dict], pools: Dict[Tuple[str, str], list],
                    without: Sequence[str]) -> Optional[Tuple[float, str]]:
    """The within-sex SD of a stratum printed with means alone and what it was made from: the
    paper's own sexless SD with the two sexes' pooling inverted, ((n - 1) sd^2 - n_m n_f / n d^2) /
    (n - 2), else the others' pooled SD narrowed half and half, sd^2 - d^2 / 4; None where neither
    leaves a positive variance."""
    d = m["mean"] - f["mean"]
    whole = sexless_row(m, rows_at_cell)
    if whole is not None:
        n = m["n"] + f["n"]
        var, why = ((n - 1.0) * whole["sd"] ** 2 - m["n"] * f["n"] / n * d * d) / (n - 2.0), OWN_SEXLESS_SD
    else:
        sd = others_pooled_sd(m, pools, without)
        if sd is None:
            return None
        var, why = sd * sd - 0.25 * d * d, OTHERS_POOLED_SD
    return (math.sqrt(var), why) if var > 0 else None


def dropped_row(m: dict, f: dict, why: str) -> dict:
    """A pair of both sexes that gives no contrast, for the record."""
    return {"paper": m["paper"], "cohort": m["cohort"], "measure": m["base_key"], "key": m["key"], "level": m["level"],
            "group": m["group"], "technique": m["technique"], "mean_male": m["mean"], "sd_male": m["sd"], "n_male": m["n"],
            "mean_female": f["mean"], "sd_female": f["sd"], "n_female": f["n"],
            "count_from": m["count_from"] if m["count_from"] == f["count_from"] else "%s; %s" % (m["count_from"], f["count_from"]),
            "why": why}


def sex_contrasts(rows: Sequence[dict], vocabulary: Dict[str, dict], without: Sequence[str] = ()) -> List[Contrast]:
    """sex_strata's contrasts."""
    return sex_strata(rows, vocabulary, without)[0]


def sex_strata(rows: Sequence[dict], vocabulary: Dict[str, dict], without: Sequence[str] = ()) -> Tuple[List[Contrast], List[dict]]:
    """Every stratum of sex_pairs with at least MIN_PER_SEX people of each sex as a contrast: read
    against its own SDs where it prints both, else, where it prints neither, against
    within_of_means's SD (the papers in `without` left out of any pool it reads), a stratum with one
    sex's SD alone, or whose SD cannot be made, giving none. `rows` are the full snapshot's with the
    sexes' snapshot's beside them (papers_table.load_rows_sexes), or any rows in their shape. The
    contrasts, and every pair of both sexes that gives none, with why (dropped_row)."""
    pairs, dropped = sex_pairs(rows, vocabulary)
    dropped = [dropped_row(m, f, why) for m, f, why in dropped]
    at_cell: Dict[tuple, List[dict]] = {}
    for r in rows:
        if r["source_of_values"] == OWN_SOURCE:
            at_cell.setdefault(_cell_of_row(r), []).append(r)
    pools = None
    out = []
    for m, f in pairs.values():
        if min(m["n"], f["n"]) < MIN_PER_SEX:
            dropped.append(dropped_row(m, f, FEW_PER_SEX))
            continue
        both = [has_sd(x) for x in (m, f)]
        within, why = float("nan"), PRINTED_SD
        if not all(both):
            if any(both):
                dropped.append(dropped_row(m, f, ONE_SD))
                continue
            pools = sexless_pools(rows) if pools is None else pools
            got = within_of_means(m, f, at_cell.get(_cell_of_row(m), []), pools, without)
            if got is None:
                dropped.append(dropped_row(m, f, NO_SD))
                continue
            within, why = got
        counts = m["count_from"] if m["count_from"] == f["count_from"] else "%s; %s" % (m["count_from"], f["count_from"])
        out.append(Contrast(m["paper"], m["cohort"], m["base_key"], m["level"], m["group"],
                            m["mean"], m["sd"] if all(both) else float("nan"), m["n"],
                            f["mean"], f["sd"] if all(both) else float("nan"), f["n"],
                            within=within, sd_from=why, count_from=counts, key=m["key"], technique=m["technique"],
                            modality=m["modality"]))
    return out, dropped


# ---- age, body height and body weight ------------------------------------------------------------------

ORDINALS = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9}


def age_band(group: str, paper: str = "") -> Optional[Tuple[float, float]]:
    """The years a group names, low and high, or None: "decade 20" and "Third Decade" are 20 to 29,
    an ordinal decade counted from ORDINAL_DECADE_FROM where the paper counts them otherwise (Bach's
    "Third Decade" is 30 to 39), "18-35", "21-40 years", "age 31-49 yr" as written, ">55", "60+"
    and "age >=70 yr" open above by OPEN_SPAN, "age <=30 yr" from ADULT. A group that names no age
    is None."""
    g = (group or "").strip().lower()
    m = re.fullmatch(r"decade (\d+)", g)
    if m:
        lo = float(m.group(1))
        return lo, lo + 9.0
    m = re.fullmatch(r"(\w+) decade", g)
    if m and m.group(1) in ORDINALS:
        lo = ORDINAL_DECADE_FROM.get(paper, 0.0) + 10.0 * (ORDINALS[m.group(1)] - 1)
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


VARIABLES: Dict[str, Tuple[Callable[..., Optional[Tuple[float, float]]], float, str]] = {
    "age": (age_band, 10.0, "per decade"),
    "body height": (lambda g, paper="": size_band(g, "height"), 100.0, "per 100 mm"),
    "body weight": (lambda g, paper="": size_band(g, "weight"), 10.0, "per 10 kg"),
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
    """Every series printed over two or more bands of the variable, the adult bands alone for age,
    each band's count its stratum's own (own_counts)."""
    band_of = VARIABLES[variable][0]
    by: Dict[tuple, List[Tuple[Tuple[float, float], dict]]] = {}
    for r in own_counts(rows):
        band = band_of(r["group"], r["paper"]) if usable(r, vocabulary) else None
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


def people_of(item) -> tuple:
    """The people a stratum or series is of: its cohort and its group (a contrast) or its sex (a
    gradient), whatever variant of the measure it reads."""
    return (item.cohort, item.group) if isinstance(item, Contrast) else (item.cohort, item.sex)


def by_paper_cell(items: Sequence) -> Dict[Tuple[str, str, str], Tuple[float, float, int]]:
    """Per (paper, measure, level) the paper's strata there, with how many strata: the strata of one
    set of people (people_of) one value, their mean effect with their mean variance, and the sets
    of different people combined by inverse variance."""
    groups: Dict[Tuple[str, str, str], Dict[tuple, list]] = {}
    for it in items:
        groups.setdefault((it.paper, it.base_key, it.level), {}).setdefault(people_of(it), []).append(effect_of(it))
    out = {}
    for k, people in groups.items():
        values = [(float(np.mean([e for e, _ in v])), float(np.mean([w for _, w in v]))) for v in people.values()]
        out[k] = inverse_variance(values) + (sum(len(v) for v in people.values()),)
    return out


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
    """Every stratum or series scored with the effect from the other papers alone, the effect read
    from every stratum and a stratum scored only where it prints its two SDs (sds_printed), since
    the score is over its own people's spread."""
    cells = by_paper_cell(items)
    out = []
    for it in items:
        if isinstance(it, Contrast) and not it.sds_printed:
            continue
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

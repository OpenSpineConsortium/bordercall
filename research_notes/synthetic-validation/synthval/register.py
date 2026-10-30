"""The population register: every cohort the validation's usable series come from, tagged with
the variables the reread's cohort files state, so that the series can be grouped by any of them
and a subgroup analysis is one call (subgroups.py; greg's ask of 2026-10-29, 23:54 UTC: "continue
this splitting process into as many known populations there are, probably by author but if
there are race variables and sex variables etc make sure you can do subgroup analysis very
easily").

data/populations.csv is one row per (paper, cohort) that a usable series names under the main
selection (literature.select), read from research_notes/paper-tables/data/cohorts/<paper>.cohorts.json
as they stand on main (the reread's third reader's record of each paper's cohorts, with the
page), by two readers each: one extracted every field, a second tried to refute each against
the same file, and the rows here are the second's (the thread "Continue the Tan 2004 stratum
split", 2026-10-29). The rules: the country as the subjects text states it or, where it names
only an institution or a city, inferred from that and said so in country_basis; the ancestry
only in the paper's own word (Chinese, Caucasian, ...), never inferred from a country, so most
rows say "not stated"; the specimen cadaver, dry bone, living or mixed; the ages and counts as
printed, null where none; the evidence the cohort's page. A cohort file is a reading of a paper,
so a field here is as good as that reading, and a doubt is in notes.

Two kinds of variable: the ones the snapshot carries on every series (paper, cohort, the group a
paper printed apart, sex as the selection left it, modality, technique) and the ones the register
adds to the cohort (country, region from the country, ancestry as one word with the paper's own
words beside it, specimen, an age band from the mean age, the decade of the paper), a stratum's
ancestry from GROUP_ANCESTRY where a paper prints its ancestries apart. tag() gives one series every variable; VARIABLES names them; check() refuses a usable
series whose cohort the register does not hold or whose country REGION_OF does not place, so
the register is kept whole as the selection grows.
"""
from __future__ import annotations

import csv
import math
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from . import literature as L

POPULATIONS = os.path.join(L.DATA, "populations.csv")
COLUMNS = ["paper", "cohort", "country", "country_basis", "ancestry", "ancestry_text", "ancestry_basis", "specimen",
           "age_text", "age_mean", "age_low", "age_high", "n_people", "n_men", "n_women", "sex_text", "selection",
           "evidence", "notes", "group_counts"]
GROUP_SHARE_NOTE = "n is the group's count times the cohort's share of the sex (the paper does not split its groups by sex)"
VARIABLES = ("paper", "cohort", "group", "sex", "modality", "technique", "country", "region", "ancestry", "specimen",
             "age_band", "decade")
COHORT_VARIABLES = ("country", "region", "ancestry", "specimen", "age_band", "decade")
NOT_STATED = "not stated"

# The ancestry of a stratum a paper prints apart (literature.select with strata "apart"), by
# (paper, group), where the group's label is the paper's word for it; the cohort's ancestry
# otherwise. Eisenstein 1977's three groups print no SD, so no series of theirs is usable.
GROUP_ANCESTRY = {
    ("yu2015", "Caucasian"): "Caucasian", ("yu2015", "African American"): "African American",
    ("eisenstein1977", "Caucasoid"): "Caucasoid", ("eisenstein1977", "Sotho Negroid"): "Sotho Negroid",
    ("eisenstein1977", "Zulu Negroid"): "Zulu Negroid",
}

# The region a country is placed in, for a coarser grouping than the country; a country the
# register names must be here, or check() fails.
REGION_OF = {
    "China": "East Asia", "Hong Kong": "East Asia", "Japan": "East Asia", "Singapore": "East Asia",
    "South Korea": "East Asia", "Taiwan": "East Asia",
    "India": "South Asia", "Pakistan": "South Asia",
    "Israel": "West Asia", "Saudi Arabia": "West Asia", "Turkey": "West Asia",
    "Nigeria": "Africa",
    "Bosnia and Herzegovina": "Europe", "Germany": "Europe", "Italy": "Europe", "Netherlands": "Europe",
    "Poland": "Europe", "United Kingdom": "Europe",
    "United States": "North America", "Canada": "North America",
    "Mexico": "Latin America",
    "Australia": "Oceania", "New Zealand": "Oceania",
    NOT_STATED: NOT_STATED,
}
AGE_BANDS = ((40.0, "under 40"), (60.0, "40 to 59"), (math.inf, "60 and over"))


@dataclass
class Population:
    paper: str
    cohort: str
    country: str
    country_basis: str
    ancestry: str           # one word to group by, from the paper's words in ancestry_text
    ancestry_text: str
    ancestry_basis: str
    specimen: str
    age_text: str
    age_mean: Optional[float]
    age_low: Optional[float]
    age_high: Optional[float]
    n_people: Optional[float]
    n_men: Optional[float]
    n_women: Optional[float]
    sex_text: str
    selection: str
    evidence: str
    notes: str
    group_counts: str = ""  # the people in each group the paper prints apart, "group:n;group:n", where it counts them

    @property
    def region(self) -> str:
        return REGION_OF.get(self.country, NOT_STATED)

    @property
    def people_by_group(self) -> Dict[str, float]:
        """The count of each group the paper prints apart, from group_counts; empty where none."""
        out: Dict[str, float] = {}
        for item in filter(None, (x.strip() for x in self.group_counts.split(";"))):
            group, _, n = item.rpartition(":")
            if not group or not n.strip().isdigit():
                raise ValueError("%s %s: group_counts %r is not group:n;group:n" % (self.paper, self.cohort, self.group_counts))
            out[group.strip()] = float(n)
        return out

    @property
    def age_band(self) -> str:
        if self.age_mean is None:
            return NOT_STATED
        return next(band for top, band in AGE_BANDS if self.age_mean < top)

    @property
    def year(self) -> Optional[int]:
        digits = "".join(ch for ch in self.paper if ch.isdigit())
        return int(digits[-4:]) if len(digits) >= 4 else None

    @property
    def decade(self) -> str:
        return "%ds" % (self.year // 10 * 10) if self.year else NOT_STATED


def _number(x: str) -> Optional[float]:
    x = (x or "").strip()
    return None if x in ("", "null", "None") else float(x)


def load(path: str = POPULATIONS) -> Dict[Tuple[str, str], Population]:
    """The register by (paper, cohort)."""
    out: Dict[Tuple[str, str], Population] = {}
    with open(path, encoding="ascii", newline="") as fh:
        for r in csv.DictReader(fh):
            p = Population(**{k: (_number(r[k]) if k in NUMBERS else r[k]) for k in COLUMNS})
            if (p.paper, p.cohort) in out:
                raise ValueError("the register holds %s %s twice" % (p.paper, p.cohort))
            out[p.paper, p.cohort] = p
    return out


NUMBERS = ("age_mean", "age_low", "age_high", "n_people", "n_men", "n_women")


def write(path: str, rows: Sequence[dict]) -> None:
    """The register from rows in COLUMNS' keys, sorted by paper and cohort, ASCII and LF."""
    with open(path, "w", encoding="ascii", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in sorted(rows, key=lambda r: (r["paper"], r["cohort"])):
            w.writerow({k: ("" if r.get(k) is None else r[k]) for k in COLUMNS})


def check(series: Sequence[L.Series], register: Dict[Tuple[str, str], Population]) -> List[str]:
    """What keeps the register from holding together: a usable series whose cohort it lacks, a
    country REGION_OF does not place, a basis or specimen outside its words, an ancestry with a
    basis "not stated" that still names one."""
    problems = []
    for pair in sorted({(s.paper, s.cohort) for s in series if L.usable(s)}):
        if pair not in register:
            problems.append("no register row for %s %s" % pair)
    for p in register.values():
        if p.country not in REGION_OF:
            problems.append("%s %s: REGION_OF does not place %r" % (p.paper, p.cohort, p.country))
        if p.country_basis not in ("stated", "inferred from the institution", NOT_STATED):
            problems.append("%s %s: country_basis %r" % (p.paper, p.cohort, p.country_basis))
        if p.ancestry_basis not in ("stated", NOT_STATED):
            problems.append("%s %s: ancestry_basis %r" % (p.paper, p.cohort, p.ancestry_basis))
        if (p.ancestry == NOT_STATED) != (p.ancestry_basis == NOT_STATED) or (p.ancestry_text == NOT_STATED) != (p.ancestry == NOT_STATED):
            problems.append("%s %s: ancestry %r (%r) with basis %r" % (p.paper, p.cohort, p.ancestry, p.ancestry_text, p.ancestry_basis))
        if p.specimen not in ("cadaver", "dry bone", "living", "mixed", NOT_STATED):
            problems.append("%s %s: specimen %r" % (p.paper, p.cohort, p.specimen))
        if (p.country == NOT_STATED) != (p.country_basis == NOT_STATED):
            problems.append("%s %s: country %r with basis %r" % (p.paper, p.cohort, p.country, p.country_basis))
        try:
            groups = p.people_by_group
        except ValueError as e:
            problems.append(str(e))
            continue
        if groups and p.n_people is not None and sum(groups.values()) != p.n_people:
            problems.append("%s %s: the groups' counts sum to %g, not the cohort's %g" % (p.paper, p.cohort, sum(groups.values()), p.n_people))
    return problems


def stratum_counts(register: Dict[Tuple[str, str], Population]) -> Dict[tuple, Tuple[float, str]]:
    """The count a sex of a printed group stands for where the paper counts its groups and its
    sexes but not the sexes within the groups: the group's count times the cohort's share of the
    sex, noted as such, by (paper, cohort, group, sex), for literature.select's strata "apart".
    A paper that prints the count of each sex in each group needs nothing here, since the
    snapshot carries it on the row."""
    out: Dict[tuple, Tuple[float, str]] = {}
    for p in register.values():
        groups = p.people_by_group
        if not groups or p.n_people is None or p.n_men is None or p.n_women is None or p.n_people <= 0:
            continue
        for group, n in groups.items():
            for sex, people in (("male", p.n_men), ("female", p.n_women)):
                out[p.paper, p.cohort, group, sex] = (n * people / p.n_people, GROUP_SHARE_NOTE)
    return out


def tag(s: L.Series, register: Dict[Tuple[str, str], Population]) -> Dict[str, str]:
    """Every variable of one series: the series' own and its cohort's from the register."""
    p = register.get((s.paper, s.cohort))
    out = {"paper": s.paper, "cohort": "%s/%s" % (s.paper, s.cohort), "group": "%s/%s" % (s.paper, s.group or "whole"),
           "sex": s.sex, "modality": s.modality, "technique": "%s/%s" % (s.paper, s.technique)}
    for v in COHORT_VARIABLES:
        out[v] = getattr(p, v) if p else NOT_STATED
    out["ancestry"] = GROUP_ANCESTRY.get((s.paper, s.group), out["ancestry"])
    return out

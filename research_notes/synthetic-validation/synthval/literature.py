"""The published series the synthetic population is held to, chosen by rules written here.

The series are those of the clinical reread's paper tables (bordercall draft pull request 26,
research_notes/paper-tables/data/series.csv): every table of the 39 papers other than Panjabi's
four, read twice blind, reconciled on the page and mapped to schwingcheck's measure keys, one row
per paper, cohort, technique, source of values, sex, group, side, measure and level. This folder
keeps a snapshot of the rows it can use (data/literature_series.csv, with data/SOURCE.json naming
the branch, the commit and the sha256 of the file it was cut from), so that the validation reruns
whatever happens to that branch, and `python3 -I snapshot.py --check` says whether the snapshot still matches
a copy of the file.

A row becomes a series of the validation by these rules, each counted in the record:

1. the values are the paper's own (source_of_values "this paper"; a value a table quotes from
   another study is that study's, and may be one of the 39 already);
2. the subjects are human (a cohort with a species, Busscher's and van der Houwen's pigs, is out),
   adult and unselected: a group or a cohort of patients with a disease (stenosis, degenerative
   spondylolisthesis, Marfan), of children (an age band ending below 18), the largest or smallest
   quarter, values adjusted by a model, and one example subject are out. The cohort is read as
   well as the group because Masharawi's Table 5 labels its two cohorts' one-sided rows crosswise
   (the spondylolisthesis cohort's rows say "Control", the controls' say "DS"), so both are out;
3. the measure is one of the pool's 32 but the two end-plate inclinations, whose 20 numbers
   Panjabi's cervical and lumbar papers print twice, near certainly one set (the reread's note,
   research_notes/panjabi-endplate-inclination.md on its branch at 45130ac, checked by three
   second readers, recommends dropping both whichever paper holds the original), and its definition
   is Panjabi's or close to it (vs_panjabi "same" or "close"; "differs" and "none" are left out,
   and the power part reads the spread once more on "same" alone);
4. one technique per cohort, measure and level, since a paper that measures the same people twice
   (direct and on film, Olsewski's and Mitra's cadavers) gives one set of people: bone first, then
   CT, then MRI, then film, then a mixed pool, and "same" before "close";
5. one group per cohort where the paper prints the whole cohort (group empty): its strata (age,
   height, weight or ethnic bands of the same people) are left out; where it prints only strata,
   each is a series of its own, as disjoint people; two groups of one cohort with the same mean,
   SD and count are one;
6. one sex per series: both sexes together where printed (all, pooled, not stated); else a man's
   and a woman's row with their counts pooled, the SD taking in the difference of the means; else
   the one sex printed, flagged;
7. a series needs a mean, an SD and a count of two or more to enter a pooled estimate; one without
   is counted and left out. A row with no count of its own takes its cohort's count of people
   where the cohort file prints one (Busscher's six men, Gilad's 157), and says so; Zindrick's
   counts are of films and scans, not of people, and his rows stay without one.
8. a length or an area that breaks its own run of levels is left out: under half or over twice the
   mean of the same series at its printed levels next above and below. Tan's lower end-plate area at
   L3 (172 mm2 between 1,090.9 at L2 and 1,199.3 at L4) is the case it was written for: the page
   prints it (Table 1, p. 141), and the reread has left it out of series.csv since 0ac87fe, so at
   the pinned commit the rule finds nothing and stays as a guard.

Tan's SDs (DISPERSION_UNCERTAIN) weight the pooled means like any other series' but are left out of
the published SD a synthetic SD is held to (validate.py); the readings without Tan 2004 at all are
the sensitivity run.

Each series carries its modality class (bone, ct, mri, film, mixed), from the technique.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
SNAPSHOT = os.path.join(DATA, "literature_series.csv")
SOURCE = os.path.join(DATA, "SOURCE.json")
SOURCE_PATH = "research_notes/paper-tables/data/series.csv"
COHORTS_PATH = "research_notes/paper-tables/data/cohorts"
LEFT_OUT_MEASURES = {"endplate_incl": "one set of numbers printed for C3-C7 and for L1-L5; the reread drops both measures",
                     "endplate_lower_incl": "one set of numbers printed for C3-C7 and for L1-L5; the reread drops both measures"}
COLUMNS = ["paper", "cohort", "technique", "source_of_values", "key", "level", "sex", "group", "side", "mean", "sd",
           "n", "sd_from", "n_from", "units", "vs_panjabi", "species", "cohort_n"]
# The papers whose printed spread the reread could not settle: Tan's methods define SE as SD / n,
# which taken literally makes every SD ten times the printed SE, and the reread converted it as
# SD = SE x sqrt(n) as the usual reading (research_notes/clinical-reread/notes/tan2004.md on the
# reread's branch). Their SDs weight the means but stay out of the published SD (validate.py).
DISPERSION_UNCERTAIN = {"tan2004": "SE defined in the methods as SD / n; converted as SE x sqrt(n)"}
DEFINITIONS_MAIN = ("same", "close")
MODALITY_ORDER = ("bone", "ct", "mri", "film", "mixed")
WHOLE_SEXES = ("all", "pooled", "not stated")
EXCLUDED_GROUP = re.compile(r"stenosis|^DS$|marfan|25% (largest|smallest)|adjusted|example|figure|porcine", re.I)
CHILD_BAND = re.compile(r"^age (\d+)(\s*[-,]\s*\d+)*( ?(y|yr|years))?$", re.I)
ADULT_AGE = 18
EXAMPLE_COHORT = re.compile(r"^(fig|figure|example)", re.I)
ANATOMICAL_ORDER = tuple(["C%d" % i for i in range(1, 8)] + ["T%d" % i for i in range(1, 14)] +
                         ["L%d" % i for i in range(1, 7)] + ["S1"])
JUMP_UNITS = ("mm", "mm2")
JUMP_LIMITS = (0.5, 2.0)
BREAKS_OWN_SERIES = "breaks its own run of levels (under half or over twice its neighbours' mean)"


def modality(technique: str) -> str:
    t = technique.lower()
    if "pooled_film_and_ct" in t or "mixed" in t:
        return "mixed"
    if re.search(r"radiograph|radiolog|roentgenogram|film(?!.*ct)|xray|x-ray", t) and "ct_midpedicle_film" not in t:
        return "film"
    if re.search(r"(^|[_-])(micro)?ct([_-]|$)|mdct|microct", t) or t.startswith("ct") or "-ct" in t or "_ct" in t:
        return "ct"
    if "mri" in t:
        return "mri"
    return "bone"


# ---- the snapshot ----------------------------------------------------------------------------

def _git_show(repo: str, ref: str, path: str) -> bytes:
    return subprocess.run(["git", "-C", repo, "show", "%s:%s" % (ref, path)], check=True, capture_output=True).stdout


def _cohorts(repo: str, ref: str) -> Dict[Tuple[str, str], dict]:
    """Each cohort's species, where it is not human, and its count of people, where printed."""
    names = subprocess.run(["git", "-C", repo, "ls-tree", "--name-only", "%s:%s" % (ref, COHORTS_PATH)], check=True,
                           capture_output=True, text=True).stdout.split()
    out = {}
    for name in names:
        data = json.loads(_git_show(repo, ref, "%s/%s" % (COHORTS_PATH, name)))
        for c in data.get("cohorts", []):
            n = c.get("n_people")
            out[(data["paper"], c.get("cohort"))] = {"species": c.get("species") or "",
                                                     "n": n if isinstance(n, (int, float)) else ""}
    return out


def write_snapshot(repo: str, ref: str, keys: Sequence[str], branch: str = "claude/project-thread-adplcz") -> dict:
    """Cut the rows of the measures given from series.csv at `ref`, each with its cohort's
    species, into the snapshot, and record where they came from."""
    raw = _git_show(repo, ref, SOURCE_PATH)
    commit = subprocess.run(["git", "-C", repo, "rev-parse", ref], check=True, capture_output=True, text=True).stdout.strip()
    cohorts = _cohorts(repo, ref)
    rows = list(csv.DictReader(raw.decode("utf-8").splitlines()))
    kept = [r for r in rows if r["key"] in set(keys)]
    os.makedirs(DATA, exist_ok=True)
    with open(SNAPSHOT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, COLUMNS, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for r in kept:
            c = cohorts.get((r["paper"], r["cohort"]), {"species": "", "n": ""})
            w.writerow(dict(r, species=c["species"], cohort_n=c["n"]))
    info = {"branch": branch, "commit": commit, "path": SOURCE_PATH, "sha256": hashlib.sha256(raw).hexdigest(),
            "rows_in_source": len(rows), "rows_kept": len(kept), "keys": sorted(set(keys)),
            "cohorts_path": COHORTS_PATH,
            "non_human_cohorts": sorted("%s/%s" % k for k, c in cohorts.items() if c["species"]),
            "snapshot_sha256": _sha(SNAPSHOT)}
    with open(SOURCE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(info, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return info


def _sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def check_snapshot(source_csv: Optional[str] = None) -> List[str]:
    """What differs: the snapshot's own digest against SOURCE.json, and, given a copy of
    series.csv (as a merged reread leaves it in this repository), every kept row against it."""
    with open(SOURCE, encoding="utf-8") as fh:
        info = json.load(fh)
    problems = []
    if _sha(SNAPSHOT) != info["snapshot_sha256"]:
        problems.append("the snapshot is not the one SOURCE.json records")
    if source_csv and os.path.exists(source_csv):
        keys = set(info["keys"])
        with open(source_csv, encoding="utf-8") as fh:
            theirs = [r for r in csv.DictReader(fh) if r["key"] in keys]
        with open(SNAPSHOT, encoding="utf-8") as fh:
            ours = list(csv.DictReader(fh))
        strip = lambda r: tuple(r[c] for c in COLUMNS if c not in ("species", "cohort_n"))
        if sorted(map(strip, theirs)) != sorted(map(strip, ours)):
            problems.append("the snapshot's rows differ from %s" % source_csv)
    return problems


# ---- the series ------------------------------------------------------------------------------

@dataclass
class Series:
    paper: str
    cohort: str
    technique: str
    modality: str
    group: str
    sex: str
    key: str
    level: str
    mean: float
    sd: float
    n: float
    vs_panjabi: str
    flag: str = ""
    n_note: str = ""
    sd_uncertain: bool = False

    def as_dict(self) -> dict:
        return dict(self.__dict__)


def _num(s: str) -> float:
    try:
        return float(s)
    except (TypeError, ValueError):
        return float("nan")


def load_rows(path: str = SNAPSHOT) -> List[dict]:
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["mean"], r["sd"], r["n"] = _num(r["mean"]), _num(r["sd"]), _num(r["n"])
        r["n_note"] = ""
        if not math.isfinite(r["n"]) and math.isfinite(_num(r.get("cohort_n", ""))):
            r["n"], r["n_note"] = _num(r["cohort_n"]), "n is the cohort's people"
        r["group"] = r["group"] or ""
        r["modality"] = modality(r["technique"])
    return rows


def excluded_why(r: dict, definitions: Sequence[str]) -> Optional[str]:
    if r["source_of_values"] != "this paper":
        return "quoted from another study"
    if r["species"]:
        return "not human"
    if r["key"] in LEFT_OUT_MEASURES:
        return "end-plate inclination, one set printed for two regions"
    if r["vs_panjabi"] not in definitions:
        return "definition %s" % r["vs_panjabi"]
    g = r["group"]
    if EXCLUDED_GROUP.search(g) or EXCLUDED_GROUP.search(r["cohort"]) or EXAMPLE_COHORT.search(r["cohort"]):
        return "selected, diseased or example group"
    if CHILD_BAND.match(g) and max(int(x) for x in re.findall(r"\d+", g)) < ADULT_AGE:
        return "children"
    if r["technique"] == "meta_pool":
        return "a meta-analysis pooling other series"
    return None


def _position(level: str) -> float:
    """A level's place in a column of the usual count, T13 and L6 half a step past T12 and L5."""
    extra = {"T13": "T12", "L6": "L5"}
    usual = [lv for lv in ANATOMICAL_ORDER if lv not in extra]
    return usual.index(extra[level]) + 0.5 if level in extra else float(usual.index(level))


def _step(a: str, b: str) -> float:
    return abs(_position(b) - _position(a))


def breaks_own_series(rows: Sequence[dict]) -> set:
    """The ids of rows whose mean is under half or over twice the mean of the same series (paper,
    cohort, technique, measure, sex, group, side) at the printed levels next above and below it,
    for lengths and areas only: the series' own levels in anatomical order, so that a series that
    prints no T13 or L6 still has T12, L1 and L5 screened, but only where both neighbours are next
    to it in a column (T13 and L6 counted as half a step), since a series that prints T4, T5 and L5
    alone has no neighbour of T5 below it."""
    runs: Dict[tuple, Dict[str, dict]] = {}
    for r in rows:
        if r["units"] in JUMP_UNITS and r["level"] in ANATOMICAL_ORDER and math.isfinite(r["mean"]):
            k = (r["paper"], r["cohort"], r["technique"], r["source_of_values"], r["key"], r["sex"], r["group"], r["side"])
            runs.setdefault(k, {})[r["level"]] = r
    out = set()
    for run in runs.values():
        printed = sorted(run, key=ANATOMICAL_ORDER.index)
        for up, level, down in zip(printed, printed[1:], printed[2:]):
            if _step(up, level) > 1 or _step(level, down) > 1:
                continue
            ratio = run[level]["mean"] / ((run[up]["mean"] + run[down]["mean"]) / 2)
            if not JUMP_LIMITS[0] <= ratio <= JUMP_LIMITS[1]:
                out.add(id(run[level]))
    return out


def _pool_sexes(male: dict, female: dict) -> Optional[Tuple[float, float, float]]:
    n1, n2 = male["n"], female["n"]
    if not (n1 > 0 and n2 > 0) or not (math.isfinite(male["sd"]) and math.isfinite(female["sd"])):
        return None
    n = n1 + n2
    mean = (n1 * male["mean"] + n2 * female["mean"]) / n
    ss = (n1 - 1) * male["sd"] ** 2 + (n2 - 1) * female["sd"] ** 2 + n1 * n2 / n * (male["mean"] - female["mean"]) ** 2
    return mean, math.sqrt(ss / (n - 1)), n


def select(rows: Sequence[dict], definitions: Sequence[str] = DEFINITIONS_MAIN) -> Tuple[List[Series], Dict[str, int]]:
    """The validation's series and the count of rows left out by each rule."""
    why: Dict[str, int] = {}
    kept = []
    jumps = breaks_own_series(rows)
    for r in rows:
        w = BREAKS_OWN_SERIES if id(r) in jumps else excluded_why(r, definitions)
        if w:
            why[w] = why.get(w, 0) + 1
        else:
            kept.append(r)
    rank_mod = {m: i for i, m in enumerate(MODALITY_ORDER)}
    rank_def = {d: i for i, d in enumerate(("same", "close", "differs", "none"))}
    by_cell: Dict[tuple, List[dict]] = {}
    for r in kept:
        by_cell.setdefault((r["paper"], r["cohort"], r["key"], r["level"]), []).append(r)
    series: List[Series] = []
    for cell, rs in sorted(by_cell.items()):
        best = min(rs, key=lambda r: (rank_mod[r["modality"]], rank_def[r["vs_panjabi"]]))
        tech = [r for r in rs if r["technique"] == best["technique"]]
        dropped = len(rs) - len(tech)
        if dropped:
            why["another technique on the same people"] = why.get("another technique on the same people", 0) + dropped
        whole = [r for r in tech if r["group"] == ""]
        if whole and len(whole) < len(tech):
            why["a stratum of a cohort printed whole"] = why.get("a stratum of a cohort printed whole", 0) + len(tech) - len(whole)
            tech = whole
        groups: Dict[str, List[dict]] = {}
        for r in tech:
            groups.setdefault(r["group"], []).append(r)
        seen = set()
        for g, grs in sorted(groups.items()):
            s = _one_sex(grs, why)
            if s is None:
                continue
            sig = (round(s.mean, 6), round(s.sd, 6) if math.isfinite(s.sd) else None, s.n)
            if sig in seen:
                why["a second group with the same values"] = why.get("a second group with the same values", 0) + 1
                continue
            seen.add(sig)
            series.append(s)
    return series, why


ONE_SIDE = ("left", "right")


def measure_key(pool_key: str) -> str:
    """The reread's key for a pool measure: a two-sided measure's mean of sides is printed under
    the bare name (pedicle_w for pedicle_w:mean), with the side in its own column."""
    return pool_key.split(":")[0]


def _sides(rs: List[dict], why: Dict[str, int]) -> List[dict]:
    """One row per sex for a two-sided measure: a row of both sides (or of no side) where printed,
    left and right rows dropped beside it; else the left and right rows averaged, the mean of the
    two means with the root mean of the two variances and the smaller count."""
    if all(r["side"] not in ONE_SIDE for r in rs):
        return rs
    both = [r for r in rs if r["side"] not in ONE_SIDE]
    if both:
        why["one side printed beside both"] = why.get("one side printed beside both", 0) + len(rs) - len(both)
        return both
    out = []
    for sex in sorted({r["sex"] for r in rs}):
        left = [r for r in rs if r["sex"] == sex and r["side"] == "left"]
        right = [r for r in rs if r["sex"] == sex and r["side"] == "right"]
        if left and right:
            a, b = left[0], right[0]
            out.append(dict(a, side="left and right averaged here", mean=(a["mean"] + b["mean"]) / 2,
                            sd=math.sqrt((a["sd"] ** 2 + b["sd"] ** 2) / 2), n=min(a["n"], b["n"])))
        else:
            out.append((left or right)[0])
            why["kept with one side only"] = why.get("kept with one side only", 0) + 1
    return out


def _one_sex(rs: List[dict], why: Dict[str, int]) -> Optional[Series]:
    rs = _sides(rs, why)
    whole = [r for r in rs if r["sex"] in WHOLE_SEXES]
    flag = ""
    if whole:
        # a row with an SD before one without (Tan's text "max" values print none), then the most people
        r = max(whole, key=lambda r: (math.isfinite(r["sd"]), r["n"] if math.isfinite(r["n"]) else -1))
        if len(rs) > 1:
            why["a sex printed beside both sexes"] = why.get("a sex printed beside both sexes", 0) + len(rs) - 1
        mean, sd, n = r["mean"], r["sd"], r["n"]
    else:
        male = [r for r in rs if r["sex"] == "male"]
        female = [r for r in rs if r["sex"] == "female"]
        pooled = _pool_sexes(male[0], female[0]) if male and female else None
        if pooled:
            r = male[0]
            mean, sd, n = pooled
            flag = "sexes pooled here"
        else:
            r = (male or female or rs)[0]
            mean, sd, n = r["mean"], r["sd"], r["n"]
            flag = "one sex only (%s)" % r["sex"]
    return Series(paper=r["paper"], cohort=r["cohort"], technique=r["technique"], modality=r["modality"],
                  group=r["group"], sex=r["sex"] if not flag.startswith("sexes") else "pooled here", key=r["key"],
                  level=r["level"], mean=mean, sd=sd, n=n, vs_panjabi=r["vs_panjabi"], flag=flag,
                  n_note=r.get("n_note", ""), sd_uncertain=r["paper"] in DISPERSION_UNCERTAIN)


def usable(s: Series) -> bool:
    return math.isfinite(s.mean) and math.isfinite(s.sd) and s.sd > 0 and math.isfinite(s.n) and s.n >= 2

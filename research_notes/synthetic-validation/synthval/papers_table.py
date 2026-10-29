"""Every measure of the clinical reread, pooled level by level into the tables two more
synthetic populations are drawn from.

The validation (literature.py, validate.py) holds the generator's 32 measures, Panjabi's, to the
papers. The reread's vocabulary (research_notes/paper-tables/data/vocabulary.csv on its branch,
copied here as data/vocabulary.csv) names 106 keys: Panjabi's 49 measures and 57 more, of which
the other papers print a series for some, and some of which are no measure of a vertebra at all
(the subjects' age, a prevalence, a reliability figure). This module reads every row of the
reread's series.csv (the snapshot data/series_all.csv, cut with snapshot.py --write-all) under
literature.py's eight rules, with four changes:

1. a key Panjabi does not print (vs_panjabi "none") is kept beside his own under "same" and
   "close"; "differs", one of his measures taken another way, stays out and is counted;
2. where the papers of one key measure different things (VARIANTS), each is a measure of its own,
   written "key [variant]": Bach's three-point disc height apart from his mean of the two rims,
   Abbas's angle between the laminae apart from his lamina's inclination to the body, Griffith's
   canal-to-body area ratio apart from Alonge's ratio of depths, and so on, each with why;
3. where one paper prints the same quantity on two planes of the same people, the plane another
   measure of the paper shares is kept (PREFERRED_TECHNIQUE: Shin's sagittal foramen width, which
   his sagittal foramen height and area are read on), and the other is counted as another
   technique on the same people;
4. a disc or a foramen printed between two levels (L4-L5) is placed at the upper level (the disc
   below L4), and one printed against one vertebra only where the paper says which space it is
   (BELOW_OWN_VERTEBRA: Amonoo-Kuofi 1985's inferior vertebral notch, the upper half of the
   foramen below its own vertebra); Busscher's and Yadav's discs and Yadav's foramina, printed
   against a vertebra with no word of which disc, are pooled at their own labels and placed
   nowhere.

Each (measure, level) is pooled from one modality class, the first that has a usable series:
bone and CT together, then MRI, then film, then the mixed pool (Zindrick's films and scans), so
that no pooled mean mixes a magnified film with bone. The mean is REML-pooled (pooling.py, with
the prediction interval from three series on); the SD is the papers' as validate.literature_at
gives it (Tan 2004's left out, pooled on the log scale), or, where only Tan prints the cell, his,
flagged as uncertain (literature.DISPERSION_UNCERTAIN).
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from schwingcheck import LEVELS, SIZE_POWER
from schwingcheck import measures as MS

from . import literature as L
from . import validate as V

VOCABULARY = os.path.join(L.DATA, "vocabulary.csv")
VOCABULARY_PATH = "research_notes/paper-tables/tools/vocabulary.csv"
SNAPSHOT_ALL = os.path.join(L.DATA, "series_all.csv")
SOURCE_ALL = os.path.join(L.DATA, "SOURCE_ALL.json")
COLUMNS_ALL = L.COLUMNS + ["definition"]
DEFINITIONS_ALL = ("same", "close", "none")

# key -> {(paper, technique or "*"): the variant it measures, with why in VARIANT_WHY}; ("*", "*") is
# the variant of every paper not named
VARIANTS: Dict[str, Dict[Tuple[str, str], str]] = {
    "disc_h_mean": {("bach2019", "ct3d_midsagittal_disc_height"): "three points",
                    ("bach2019", "ct3d_midsagittal_disc_height_ap_average"): "two rims",
                    ("kunkel2011", "*"): "two rims",
                    ("twomey1985", "*"): "area over depth",
                    ("yadav2020", "*"): "not defined"},
    "lamina_angle": {("abbas2021", "ct_axial_interlaminar_angle"): "between the laminae",
                     ("abbas2021", "ct_parasagittal_laminar_inclination"): "to the body"},
    "pedicle_length": {("arockiaraj2025", "*"): "to the ligament", ("krag1988", "*"): "screw path",
                       ("masharawi2021", "*"): "proper", ("moncadahabib2025", "*"): "proper"},
    "pedicle_chord": {("hou1993", "*"): "parallel to the midline", ("*", "*"): "along the axis"},
    "body_d": {("chen2011", "*"): "end-plates' mean", ("moncadahabib2025", "*"): "through the pedicles"},
    "foramen_w": {("amonookuofi1985", "*"): "the notch", ("shin2024", "*"): "body to facet",
                  ("yadav2020", "*"): "not defined"},
    "canal_index": {("alonge2021", "*"): "depths", ("griffith2016", "*"): "areas"},
    "spinous_angle": {("busscher2010", "*"): "to the body's axis", ("gilad1985", "*"): "to the end-plate"},
    "pedicle_cortex": {("mitra2002", "*"): "medial or lateral", ("otsuki2021", "*"): "medial"},
}
VARIANT_WHY = {
    "disc_h_mean": "Bach prints three points and the two rims' mean, Kunkel the rims' mean, Twomey the median section's "
                   "area over its depth, Yadav a height he does not define",
    "lamina_angle": "Abbas's interlaminar angle (axial) and his lamina's inclination to the body (parasagittal) are two angles",
    "pedicle_length": "Masharawi and Moncada take the pedicle proper, Arockiaraj the entry point to the posterior "
                      "longitudinal ligament, Krag the screw path beside the canal",
    "pedicle_chord": "Hou's Length I runs parallel to the body's sagittal diameter, the others along the pedicle's own axis",
    "body_d": "Chen's is the mean of the two end-plates' sagittal diameters, Moncada's the depth on the axial slice "
              "through the pedicles",
    "foramen_w": "Amonoo-Kuofi spans the inferior vertebral notch of the dry vertebra, Shin the posterior body to the "
                 "inferior articular facet, Yadav gives no landmarks",
    "canal_index": "Alonge's Torg ratio is of depths, Griffith's of the canal's and the body's areas",
    "spinous_angle": "Busscher's is to a line square to the body's axis, Gilad's to the lower end-plate",
    "pedicle_cortex": "Mitra's is the medial or the lateral wall, Otsuki's the medial wall",
}
# (key, paper) -> the technique kept where the paper prints one quantity on two planes of the same people
PREFERRED_TECHNIQUE = {("foramen_w", "shin2024"): "ct_sagittal_nfd"}
DISC_OR_FORAMEN = ("disc_", "foramen_")
BELOW_OWN_VERTEBRA = {("foramen_w", "amonookuofi1985")}
COLUMN = ["C%d" % i for i in range(1, 8)] + ["T%d" % i for i in range(1, 13)] + ["L%d" % i for i in range(1, 6)] + ["S1"]
MODALITY_CLASSES = (("bone and CT", ("bone", "ct")), ("MRI", ("mri",)), ("film", ("film",)), ("mixed", ("mixed",)))
VERTEBRAL_KINDS = ("length", "area", "angle", "ratio")
NOT_OF_A_VERTEBRA = {"subject_age", "subject_height", "subject_weight", "subject_bmi", "subject_count", "prevalence",
                     "reliability", "other", "alignment", "sacrum", "rib"}
RATIO_POWER = 0


# ---- the snapshot ----------------------------------------------------------------------------

def write_snapshot_all(repo: str, ref: str, branch: str = "claude/project-thread-adplcz") -> dict:
    """Cut every row of series.csv at `ref`, each with its cohort's species and count of people and
    the reread's definition, and its vocabulary, into data/, and record where they came from."""
    raw = L._git_show(repo, ref, L.SOURCE_PATH)
    vocab = L._git_show(repo, ref, VOCABULARY_PATH)
    commit = subprocess.run(["git", "-C", repo, "rev-parse", ref], check=True, capture_output=True, text=True).stdout.strip()
    cohorts = L._cohorts(repo, ref)
    rows = list(csv.DictReader(raw.decode("utf-8").splitlines()))
    with open(SNAPSHOT_ALL, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, COLUMNS_ALL, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for r in rows:
            c = cohorts.get((r["paper"], r["cohort"]), {"species": "", "n": ""})
            w.writerow(dict(r, species=c["species"], cohort_n=c["n"]))
    with open(VOCABULARY, "wb") as fh:
        fh.write(vocab)
    info = {"branch": branch, "commit": commit, "path": L.SOURCE_PATH, "sha256": hashlib.sha256(raw).hexdigest(),
            "vocabulary_path": VOCABULARY_PATH, "vocabulary_sha256": hashlib.sha256(vocab).hexdigest(),
            "rows": len(rows), "cohorts_path": L.COHORTS_PATH, "snapshot_sha256": L._sha(SNAPSHOT_ALL)}
    with open(SOURCE_ALL, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(info, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return info


def check_snapshot_all() -> List[str]:
    """What differs between the full snapshot and its vocabulary and the digests SOURCE_ALL.json holds."""
    with open(SOURCE_ALL, encoding="utf-8") as fh:
        info = json.load(fh)
    problems = []
    if L._sha(SNAPSHOT_ALL) != info["snapshot_sha256"]:
        problems.append("the full snapshot is not the one SOURCE_ALL.json records")
    if L._sha(VOCABULARY) != info["vocabulary_sha256"]:
        problems.append("the vocabulary is not the one SOURCE_ALL.json records")
    return problems


def load_vocabulary(path: str = VOCABULARY) -> Dict[str, dict]:
    with open(path, encoding="utf-8") as fh:
        return {r["key"]: r for r in csv.DictReader(fh)}


# ---- the series of every measure --------------------------------------------------------------

def base_key(key: str) -> str:
    """The reread's key of a measure, its variant taken off."""
    return key.split(" [", 1)[0]


def variant_of(key: str, paper: str, technique: str) -> str:
    """The measure a row measures: its key, or key [variant] where VARIANTS splits the key."""
    table = VARIANTS.get(key)
    if not table:
        return key
    label = table.get((paper, technique)) or table.get((paper, "*")) or table.get(("*", "*"))
    if label is None:
        raise ValueError("no variant of %s is written for %s's %s (papers_table.VARIANTS)" % (key, paper, technique))
    return "%s [%s]" % (key, label)


def load_rows_all(path: str = SNAPSHOT_ALL) -> List[dict]:
    """Every row of the full snapshot as literature.load_rows reads it, each keyed by the measure it
    measures (variant_of), its reread key kept as base_key. The rows the reread quotes from another
    study keep their key unsplit, since they are left out (rule 1) whatever their variant."""
    rows = L.load_rows(path)
    for r in rows:
        r["base_key"] = r["key"]
        if r["source_of_values"] == "this paper":
            r["key"] = variant_of(r["key"], r["paper"], r["technique"])
    return rows


def _other_plane(r: dict) -> bool:
    kept = PREFERRED_TECHNIQUE.get((r["base_key"], r["paper"]))
    return kept is not None and r["technique"] != kept and r["source_of_values"] == "this paper"


def select_all(rows: Sequence[dict]) -> Tuple[List[L.Series], Dict[str, int]]:
    """The series of every measure, by literature.select's rules with this module's changes, and
    the count of rows left out by each rule."""
    plane = [r for r in rows if _other_plane(r)]
    kept = [r for r in rows if not _other_plane(r)]
    series, why = L.select(kept, DEFINITIONS_ALL)
    if plane:
        k = "another technique on the same people"
        why[k] = why.get(k, 0) + len(plane)
    return series, why


# ---- placing a cell in the column --------------------------------------------------------------

def next_level(level: str) -> Optional[str]:
    i = COLUMN.index(level) if level in COLUMN else -1
    return COLUMN[i + 1] if 0 <= i < len(COLUMN) - 1 else None


def place(key: str, level: str, paper: str) -> Optional[str]:
    """The level of the rule's column (C3 to L5) a cell belongs to, or None: a vertebra's own
    measure at its level; a disc or a foramen between two levels at the upper, one printed against
    one vertebra only where BELOW_OWN_VERTEBRA says the paper names the space below it."""
    base = base_key(key)
    if base.startswith(DISC_OR_FORAMEN):
        if "-" in level:
            upper, lower = level.split("-", 1)
            return upper if upper in LEVELS and next_level(upper) == lower else None
        return level if (base, paper) in BELOW_OWN_VERTEBRA and level in LEVELS else None
    return level if level in LEVELS else None


# ---- pooling every cell -----------------------------------------------------------------------

def _class_of(rows: Sequence[L.Series]) -> Tuple[str, List[L.Series]]:
    for name, mods in MODALITY_CLASSES:
        mine = [s for s in rows if s.modality in mods]
        if mine:
            return name, mine
    return "", []


def _sd_of(lit: V.Literature, rows: Sequence[L.Series]) -> Tuple[float, str]:
    """The cell's SD and where it came from: the papers' certain SDs, else all of them with Tan's,
    else the one series' own."""
    if math.isfinite(lit.sd) and lit.sd > 0:
        return lit.sd, "pooled" if lit.k_sd >= 2 else "one series"
    if lit.log_sd_all:
        return math.exp(lit.log_sd_all.mean), "Tan 2004's among them, uncertain"
    return float(rows[0].sd), "Tan 2004's alone, uncertain"


def pooled_cells(series: Sequence[L.Series]) -> List[dict]:
    """One row per (measure, level as printed) with a usable series: the modality class pooled, its
    series, papers and people, the pooled mean with its SE, tau, I2 and prediction interval, the SD
    and where it came from, and the level of the rule's column it is placed at, if any."""
    by: Dict[tuple, List[L.Series]] = {}
    for s in series:
        if L.usable(s):
            by.setdefault((s.key, s.level), []).append(s)
    out = []
    for (key, level), rows in sorted(by.items()):
        cls, mine = _class_of(rows)
        lit = V.literature_at(mine)
        sd, sd_from = _sd_of(lit, mine)
        p = lit.mean
        places = {place(key, level, s.paper) for s in mine}
        at = places.pop() if len(places) == 1 else None
        out.append({"measure": key, "base_key": base_key(key), "level": level, "placed_at": at, "modality": cls,
                    "modalities_printed": ",".join(sorted({s.modality for s in rows})), "k": lit.k,
                    "papers": lit.papers, "people": float(sum(s.n for s in mine)),
                    "mean": p.mean if p else lit.single_mean, "se": p.se if p else float("nan"),
                    "tau": p.tau if p else float("nan"), "i2": p.i2 if p else float("nan"),
                    "pi_low": p.pi_low if p else float("nan"), "pi_high": p.pi_high if p else float("nan"),
                    "sd": sd, "sd_from": sd_from, "k_sd": lit.k_sd,
                    "tau_over_sd": (p.tau / sd) if p and sd > 0 else float("nan"),
                    "flags": ";".join(sorted({s.flag for s in mine if s.flag}))})
    return out


# ---- the tables -------------------------------------------------------------------------------

@dataclass
class Table:
    """(measures, levels C3 to L5) means and SDs, NaN where no value is placed, with each measure's
    kind, its power of the size, its error and where its values came from."""
    name: str
    keys: List[str]
    kinds: List[str]
    mu: np.ndarray
    sd: np.ndarray
    sources: List[str]
    levels: List[str] = field(default_factory=lambda: list(LEVELS))
    errors_given: Optional[np.ndarray] = None    # a Panjabi measure's own error (measures.Measure.error), else None

    @property
    def power(self) -> np.ndarray:
        return np.array([SIZE_POWER.get(k, RATIO_POWER) for k in self.kinds], float)

    @property
    def error(self) -> np.ndarray:
        """Each measure's error: a Panjabi measure's own, as the registry states it (so that a draw
        from his table is the generator's to the bit), else as measures.error_of gives a kind's (1
        mm, sqrt(pi A / 2) mm2 with A the area's mean over the levels the table has, 3 degrees); a
        ratio's is not modelled (0)."""
        out = []
        for j, kind in enumerate(self.kinds):
            given = None if self.errors_given is None else self.errors_given[j]
            if given is not None and math.isfinite(given):
                out.append(float(given))
            elif kind == "length":
                out.append(MS.LENGTH_ERROR_MM)
            elif kind == "area":
                out.append(math.sqrt(math.pi * float(np.nanmean(self.mu[j])) / 2.0) * MS.LENGTH_ERROR_MM)
            elif kind == "angle":
                out.append(MS.ANGLE_ERROR_DEG)
            else:
                out.append(0.0)
        return np.array(out, float)

    def complete_over(self, levels: Sequence[str]) -> List[int]:
        """The measures with a mean and an SD at every level given."""
        idx = [self.levels.index(lv) for lv in levels]
        ok = np.isfinite(self.mu[:, idx]).all(1) & np.isfinite(self.sd[:, idx]).all(1) & (self.sd[:, idx] > 0).all(1)
        return [j for j in range(len(self.keys)) if ok[j]]

    def cells(self) -> int:
        return int((np.isfinite(self.mu) & np.isfinite(self.sd)).sum())

    def subset(self, idx: Sequence[int], name: Optional[str] = None) -> "Table":
        idx = list(idx)
        return Table(name=name or self.name, keys=[self.keys[j] for j in idx], kinds=[self.kinds[j] for j in idx],
                     mu=self.mu[idx], sd=self.sd[idx], sources=[self.sources[j] for j in idx], levels=list(self.levels),
                     errors_given=None if self.errors_given is None else self.errors_given[idx])

    def over(self, levels: Sequence[str], name: Optional[str] = None) -> "Table":
        """The same measures over a run of the column (the lumbar levels), the cells of other levels dropped."""
        idx = [self.levels.index(lv) for lv in levels]
        return Table(name=name or self.name, keys=list(self.keys), kinds=list(self.kinds), mu=self.mu[:, idx],
                     sd=self.sd[:, idx], sources=list(self.sources), levels=list(levels), errors_given=self.errors_given)


def panjabi_key(m: MS.Measure) -> str:
    """The key a Panjabi measure takes in every table: the archive's (pedicle for the mean pedicle width)."""
    return MS.archive_key(m)


def panjabi_measures() -> List[MS.Measure]:
    """Every measure of Panjabi's long table with rows and a spread at some level, each once: a
    whole measure, or a pair as its mean (the pool's 32 and the ten he prints at some levels)."""
    reg = MS.registry()
    out = []
    for name in MS.MEASURES:
        key = MS._pool_key(name, reg)
        if key is None:
            continue
        m = reg[key]
        if any(r.level in LEVELS and math.isfinite(r.sd) and r.sd > 0 for r in m.rows):
            out.append(m)
    return out


def panjabi_table() -> Table:
    """Panjabi's own table on every measure he prints with a spread, NaN at the levels he does not."""
    ms = panjabi_measures()
    mu = np.full((len(ms), len(LEVELS)), np.nan)
    sd = np.full_like(mu, np.nan)
    for j, m in enumerate(ms):
        for r in m.rows:
            if r.level in LEVELS:
                mu[j, LEVELS.index(r.level)], sd[j, LEVELS.index(r.level)] = r.mean, r.sd
    return Table(name="Panjabi's, every measure", keys=[panjabi_key(m) for m in ms], kinds=[m.kind for m in ms],
                 mu=mu, sd=sd, sources=["panjabi"] * len(ms), errors_given=np.array([m.error for m in ms], float))


def _reread_to_panjabi() -> Dict[str, str]:
    """The reread's key of each Panjabi measure -> its key in the tables."""
    return {L.measure_key(m.key): panjabi_key(m) for m in panjabi_measures()}


def papers_table(cells: Sequence[dict], vocabulary: Dict[str, dict]) -> Table:
    """The papers' pooled values at every placed cell, every measure with one; a Panjabi measure
    under its key in the tables, so that the indicators read it as they read his."""
    to_panjabi = _reread_to_panjabi()
    placed = [c for c in cells if c["placed_at"]]
    keys = sorted({c["measure"] for c in placed}, key=lambda k: (to_panjabi.get(k) is None, k))
    mu = np.full((len(keys), len(LEVELS)), np.nan)
    sd = np.full_like(mu, np.nan)
    for c in placed:
        j, i = keys.index(c["measure"]), LEVELS.index(c["placed_at"])
        if math.isfinite(mu[j, i]):
            raise ValueError("two cells of %s are placed at %s" % (c["measure"], c["placed_at"]))
        mu[j, i], sd[j, i] = c["mean"], c["sd"]
    kinds = [vocabulary[base_key(k)]["kind"] for k in keys]
    return Table(name="the papers'", keys=[to_panjabi.get(k, k) for k in keys], kinds=kinds, mu=mu, sd=sd,
                 sources=["papers"] * len(keys))


def combined_table(panjabi: Table, papers: Table) -> Table:
    """Panjabi's every measure, with the papers' values for the measures he never took."""
    extra = [j for j, k in enumerate(papers.keys) if k not in panjabi.keys]
    p = papers.subset(extra)
    return Table(name="Panjabi's and the papers'", keys=panjabi.keys + p.keys, kinds=panjabi.kinds + p.kinds,
                 mu=np.vstack([panjabi.mu, p.mu]), sd=np.vstack([panjabi.sd, p.sd]),
                 sources=panjabi.sources + p.sources, errors_given=np.concatenate([panjabi.error, p.error]))


# ---- the inventory of the 106 -----------------------------------------------------------------

def inventory(rows: Sequence[dict], series: Sequence[L.Series], cells: Sequence[dict],
              vocabulary: Dict[str, dict], tables: Dict[str, Table]) -> List[dict]:
    """One row per key of the vocabulary: what it is, whether Panjabi prints it and whether the
    generator draws it, the reread's rows, the usable series, papers and people, the pooled cells
    and the cells placed in each table, its variants, and what holds it back where nothing is drawn."""
    pool = {L.measure_key(m.key) for m in MS.pool()}
    left_out = MS.left_out()
    to_panjabi = _reread_to_panjabi()
    out = []
    for key, v in vocabulary.items():
        mine_rows = [r for r in rows if r["base_key"] == key]
        own = [r for r in mine_rows if r["source_of_values"] == "this paper"]
        usable = [s for s in series if base_key(s.key) == key and L.usable(s)]
        mine_cells = [c for c in cells if c["base_key"] == key]
        variants = sorted({c["measure"] for c in mine_cells} | {s.key for s in usable})
        row = {"key": key, "kind": v["kind"], "units": v["units"], "panjabi": v["panjabi"] == "yes",
               "in_generator": key in pool, "of_a_vertebra": key not in NOT_OF_A_VERTEBRA and v["kind"] in VERTEBRAL_KINDS,
               "definition": v["definition"], "rows": len(mine_rows), "rows_own": len(own),
               "rows_differs": sum(1 for r in own if r["vs_panjabi"] == "differs"),
               "series": len(usable), "papers": len({s.paper for s in usable}),
               "papers_list": ";".join(sorted({s.paper for s in usable})),
               "pooled_cells": len(mine_cells), "pooled_cells_k3": sum(1 for c in mine_cells if c["k"] >= 3),
               "variants": "; ".join(variants) if len(variants) > 1 else "",
               "variant_why": VARIANT_WHY.get(key, "")}
        for name, t in tables.items():
            tkeys = [to_panjabi.get(k, k) for k in variants] or [to_panjabi.get(key, key)]
            row["cells " + name] = sum(int((np.isfinite(t.mu[t.keys.index(k)])).sum()) for k in tkeys if k in t.keys)
        row["why_not_drawn"] = _why_not_drawn(row, key, left_out, mine_rows, own, usable)
        out.append(row)
    return out


def _why_not_drawn(row: dict, key: str, left_out: Dict[str, str], rows, own, usable) -> str:
    if not row["of_a_vertebra"]:
        return "not a measure of one vertebra (%s)" % row["kind"]
    if row["panjabi"] and key in left_out and not any(row[k] for k in row if k.startswith("cells ")):
        return "Panjabi: " + left_out[key]
    if any(row[k] for k in row if k.startswith("cells ")):
        return ""
    if not rows:
        return "no paper of the 39 prints a series"
    if not own:
        return "every series is quoted from another study"
    if not usable:
        return "no series with a mean, an SD and a count of two or more passes the rules"
    return "no series is placed at a level of C3 to L5"

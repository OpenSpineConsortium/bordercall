"""One imported study as a column: its bodies top down, what was measured on each, and the facts
the tiers and the scores are read from; and the files a directory of imports holds.

    <out>/columns/<study>.json   the column, whole (the record every other file is written from)
    <out>/bodies.csv             one row per body and measure, every study of the directory
    <out>/fields/<study>.csv     the study as one field in the format `python -m schwingcheck name`
                                 reads: a column `body`, a column `offset` (the body's place in the
                                 study's own count, so a body missing between two seen ones leaves
                                 a gap), one column per measure in millimetres, blank where it was
                                 not taken, and '#' lines naming the study and its levels
    <out>/studies.csv            one row per study: the facts and the tier
    <out>/MANIFEST.json          what made the directory: the command, the code's commit, the
                                 inputs' sha256, the counts

A body's name is the one its labels give it, and the study says whether those labels were
counted from C2 (`countable`): only a countable study's names are a truth anything is scored
against (the owner's rule of 2026-10-26: "I ONLY TRUST FULL SPINE C2 to PELVIS CTS!").
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import subprocess
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

from . import CERVICAL, LUMBAR, MEASURES, PLANES, ROOT, THORACIC

FORMAT = "bordercall-column/1"


@dataclass
class Body:
    level: str                                   # the name its labels give it, or "?"
    values: Dict[str, float] = field(default_factory=dict)
    methods: Dict[str, str] = field(default_factory=dict)
    flags: Dict[str, str] = field(default_factory=dict)


@dataclass
class Column:
    study: Dict[str, object]
    bodies: List[Body]

    @property
    def levels(self) -> List[str]:
        return [b.level for b in self.bodies]

    def values(self, measures: List[str]) -> List[List[float]]:
        return [[b.values.get(m, math.nan) for m in measures] for b in self.bodies]

    def to_json(self) -> dict:
        bodies = []
        for b in self.bodies:
            d = asdict(b)
            d["values"] = {k: _clean(v) for k, v in b.values.items()}
            bodies.append(d)
        return {"format": FORMAT, "study": self.study, "bodies": bodies}

    @staticmethod
    def from_json(d: dict) -> "Column":
        if d.get("format") != FORMAT:
            raise ValueError("not a %s record: %r" % (FORMAT, d.get("format")))
        bodies = [Body(level=b["level"], values={k: (math.nan if v is None else float(v)) for k, v in b["values"].items()},
                       methods=dict(b.get("methods", {})), flags=dict(b.get("flags", {}))) for b in d["bodies"]]
        return Column(study=dict(d["study"]), bodies=bodies)


def own_sequence(levels: List[str]) -> List[str]:
    """The names a column holding these levels runs through, top down: seven cervical, twelve
    thoracic and T13 where the column has one, five lumbar and L6 where it has one, the sacrum."""
    thor = THORACIC[:13] if "T13" in levels else THORACIC[:12]
    lum = LUMBAR[:6] if "L6" in levels else LUMBAR[:5]
    return CERVICAL + thor + lum + ["sacrum"]


def offsets_of(levels: List[str]) -> Optional[List[int]]:
    """Each body's place in its column's own count, from the first body; None when a body is
    unnamed or out of order, since then no gap can be told from no gap."""
    seq = own_sequence(levels)
    if any(lv not in seq for lv in levels):
        return None
    pos = [seq.index(lv) for lv in levels]
    if any(b <= a for a, b in zip(pos, pos[1:])):
        return None
    return [p - pos[0] for p in pos]


def facts_from_levels(levels: List[str], expresses: Dict[str, bool]) -> Dict[str, object]:
    """What the labels alone say about the study: whether it shows C2 and the sacrum, whether its
    names run from C2 with no body missing (so they are a count from C2), and its phenotype as far
    as its scheme can express one: an anomaly its labels name, or typical only when the count runs
    from C2 to the sacrum."""
    has_c2, has_sacrum = "C2" in levels, "sacrum" in levels
    seq = own_sequence(levels)
    named = [lv for lv in levels if lv in seq]
    run_from_c2 = False
    if has_c2 and named:
        top, bottom = seq.index("C2"), max(seq.index(lv) for lv in named)
        run_from_c2 = all(seq[i] in levels for i in range(top, bottom + 1))
    n_lumbar = sum(1 for lv in levels if lv.startswith("L"))
    if "T13" in levels:
        phen = "t13"
    elif "L6" in levels:
        phen = "six_lumbar"
    elif has_sacrum and "L4" in levels and "L5" not in levels:
        phen = "four_lumbar"
    elif has_sacrum and "L5" in levels and run_from_c2:
        phen = "typical"
    else:
        phen = "unknown"            # a column not counted from C2 may hide a T13 above what it shows
    if phen == "typical" and not (expresses.get("L6", False) and expresses.get("T13", False)):
        phen = "typical_as_far_as_the_scheme_says"
    return {"has_c2": has_c2, "has_sacrum": has_sacrum, "countable": bool(run_from_c2),
            "count_basis": "labels run from C2 with no body missing" if run_from_c2 else
            ("C2 shown but a body is missing below it" if has_c2 else "no C2: the names are not a count from C2"),
            "n_lumbar": n_lumbar, "phenotype": phen, "levels": levels}


# ---- the files ----------------------------------------------------------------------------------

def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    if os.path.isdir(path):
        for name in sorted(os.listdir(path)):
            h.update(name.encode())
            h.update(sha256_of(os.path.join(path, name)).encode())
        return h.hexdigest()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def commit_of() -> Dict[str, object]:
    try:
        head = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--", "scanimport", "archive/bordercall"],
                                    capture_output=True, text=True, check=True).stdout.strip())
        return {"commit": head, "dirty": dirty}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}


def write_column(col: Column, out: str) -> str:
    os.makedirs(os.path.join(out, "columns"), exist_ok=True)
    os.makedirs(os.path.join(out, "fields"), exist_ok=True)
    sid = str(col.study["study_id"])
    path = os.path.join(out, "columns", sid + ".json")
    with open(path, "w", newline="\n") as fh:
        json.dump(col.to_json(), fh, indent=1, sort_keys=True, allow_nan=False)
        fh.write("\n")
    write_field(col, os.path.join(out, "fields", sid + ".csv"))
    return path


def _clean(v: float) -> Optional[float]:
    return None if v is None or (isinstance(v, float) and not math.isfinite(v)) else round(float(v), 3)


def write_field(col: Column, path: str) -> None:
    offs = offsets_of(col.levels)
    with open(path, "w", newline="") as fh:
        fh.write("# study %s\n" % col.study["study_id"])
        fh.write("# levels %s\n" % " ".join(col.levels))
        fh.write("# countable %s\n" % bool(col.study.get("countable")))
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["body", "offset", "level"] + MEASURES)
        for i, b in enumerate(col.bodies):
            v = [_clean(b.values.get(m, math.nan)) for m in MEASURES]
            w.writerow([i, offs[i] if offs else "", b.level] + ["" if x is None else x for x in v])


def read_columns(directory: str) -> List[Column]:
    cdir = os.path.join(directory, "columns")
    out = []
    for name in sorted(os.listdir(cdir)) if os.path.isdir(cdir) else []:
        if name.endswith(".json"):
            with open(os.path.join(cdir, name)) as fh:
                out.append(Column.from_json(json.load(fh)))
    return out


STUDY_FIELDS = ["study_id", "subject_id", "source", "modality", "views", "annotation", "made_by", "scheme",
                "has_c2", "has_sacrum", "countable", "phenotype", "n_bodies", "n_lumbar", "scale_log_mean",
                "scale_log_sd", "grade", "tier", "tier_reason"]


def write_tables(directory: str, columns: List[Column]) -> None:
    """bodies.csv and studies.csv from every column of the directory."""
    with open(os.path.join(directory, "bodies.csv"), "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["study_id", "body", "level", "measure", "value_mm", "plane", "method", "flag"])
        for col in columns:
            for i, b in enumerate(col.bodies):
                for m in MEASURES:
                    v = _clean(b.values.get(m, math.nan))
                    if v is None and m not in b.flags:
                        continue
                    w.writerow([col.study["study_id"], i, b.level, m, "" if v is None else v,
                                col.study.get("plane_of", {}).get(m, "/".join(PLANES[m]) if col.study.get("modality") == "ct" else ""),
                                b.methods.get(m, ""), b.flags.get(m, "")])
    with open(os.path.join(directory, "studies.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=STUDY_FIELDS, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for col in columns:
            row = dict(col.study)
            row["n_bodies"] = len(col.bodies)
            row["views"] = "+".join(col.study.get("views", [])) if isinstance(col.study.get("views"), list) else col.study.get("views", "")
            w.writerow(row)


def write_manifest(directory: str, command: List[str], inputs: Dict[str, str], extra: Optional[dict] = None) -> None:
    path = os.path.join(directory, "MANIFEST.json")
    prior = {}
    if os.path.exists(path):
        with open(path) as fh:
            prior = json.load(fh)
    runs = prior.get("runs", [])
    runs.append({"command": command, "inputs": inputs, **commit_of(), **(extra or {})})
    cols = read_columns(directory)
    with open(path, "w", newline="\n") as fh:
        json.dump({"format": "bordercall-imports/1", "runs": runs, "studies": len(cols),
                   "bodies": sum(len(c.bodies) for c in cols)}, fh, indent=1, sort_keys=True)
        fh.write("\n")

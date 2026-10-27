"""The checked table of the four Panjabi papers: one long CSV, loaded as an xarray Dataset.

    python -m schwingcheck table write     # schwingcheck/data/panjabi_long.csv from provenance.csv
    python -m schwingcheck table check     # the committed CSV is what write would write

One row per value: the measure (mnemonics.py), its side, the level, the paper's mnemonic,
mean or sem, the value and its units, the kind (length, area or angle), the planes that can
read it, the number of specimens, the paper, the table and the provenance cell the value was
read from. Every row comes from the provenance record of item P step b, which holds what two
independent readers saw in the image of each cell, so one source feeds this table, the
archive's panjabi_full_spine.csv and every rule built here.

The thoracic body table (Table 3, printed page 892) is not in the scan. Its EPDl, EPWl and
VBHp means are taken from the thoracic paper's Table 8, whose Present Study column prints them
(36 cells, read twice like every other); its EPWu and EPDu means and all its standard errors
come from the archive's earlier transcription of that page, listed with that basis in
provenance/absent.csv, and the row says so in its `basis` column. Where the two differ, the
lower end-plate depth at T3 (23.2 in Table 8, 23.3 in the transcription), this table takes the
cell at hand, Table 8's, as step b recorded.

The Dataset has dimensions (level, measure, side): `mean`, `sem`, `sd` (sem times the square
root of n, the population SD the generator and the rule use) and `n`, NaN where the papers
print nothing, with the kind, the units, the planes and the definition as coordinates along
`measure` and the mnemonic along (measure, side).
"""
from __future__ import annotations

import csv
import hashlib
import math
import os
from typing import Dict, Sequence, Tuple

import numpy as np

from . import LEVELS_C2, SIDES
from .mnemonics import BY_MNEMONIC, DIMENSION_TABLES, MEASURE_INFO, MEASURES, SPECIMENS

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROVENANCE_DIR = os.path.join(ROOT, "archive", "bordercall", "reference", "provenance")
PROVENANCE_CSV = os.path.join(PROVENANCE_DIR, "provenance.csv")
ABSENT_CSV = os.path.join(PROVENANCE_DIR, "absent.csv")
LONG_CSV = os.path.join(HERE, "data", "panjabi_long.csv")

FIELDS = ["measure", "side", "level", "mnemonic", "statistic", "value", "units", "kind", "planes",
          "n", "paper", "table", "cell", "basis"]
ABSENT_TABLE = "thoracic-t3"            # the body table printed on page 892
ABSENT_MNEMONICS = ("EPWu", "EPDu", "EPWl", "EPDl", "VBHp")
# the archive's measure names for the absent table's rows, as absent.csv spells them
ARCHIVE_NAMES = {"endplate": "EPWu", "endplate_depth": "EPDu", "endplate_lower": "EPWl",
                 "endplate_lower_depth": "EPDl", "h_post": "VBHp"}


def read_csv(path: str) -> list:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _row(m, level, statistic, value, units, paper, table, cell, basis) -> dict:
    return {"measure": m.measure, "side": m.side, "level": level, "mnemonic": m.mnemonic,
            "statistic": statistic, "value": value, "units": units, "kind": m.kind,
            "planes": " ".join(m.planes), "n": str(SPECIMENS), "paper": paper, "table": table,
            "cell": cell, "basis": basis}


def rows_from_provenance(prov: Sequence[dict], absent: Sequence[dict]) -> list:
    """The long table's rows: every present-study mean and standard error of the dimension
    tables, then the absent thoracic body table from Table 8 and the transcription."""
    out = []
    for r in prov:
        if r["table"] not in DIMENSION_TABLES or r["study"] != "present":
            continue
        if r["statistic"] not in ("mean", "sem") or r["value"] == "":
            continue
        m = BY_MNEMONIC.get(r["measure"])
        if m is None:
            raise KeyError("provenance names a mnemonic mnemonics.py does not: %r in %s" % (r["measure"], r["table"]))
        if r["level"] not in LEVELS_C2:
            raise ValueError("provenance row %s is at a level outside C2-L5: %r" % (r["id"], r["level"]))
        if r["kind"] != m.kind:
            raise ValueError("provenance calls %s a %s, mnemonics.py a %s" % (r["id"], r["kind"], m.kind))
        out.append(_row(m, r["level"], r["statistic"], r["value"], r["units"], r["paper"], r["table"], r["id"], "cell"))
    # the thoracic body table: means from Table 8 where it prints them, the rest transcribed
    table8 = {(r["measure"], r["level"]): r for r in prov
              if r["table"] == "thoracic-t8a" and r["study"] == "present" and r["statistic"] == "mean"
              and r["measure"] in ABSENT_MNEMONICS and r["value"] != ""}
    for a in absent:
        if a["csv"] != "panjabi_full_spine.csv" or a["measure"] not in ARCHIVE_NAMES:
            continue
        mn = ARCHIVE_NAMES[a["measure"]]
        m = BY_MNEMONIC[mn]
        cell = table8.get((mn, a["level"]))
        if a["statistic"] == "mean" and cell is not None:
            out.append(_row(m, a["level"], "mean", cell["value"], cell["units"], "thoracic", "thoracic-t8a", cell["id"],
                            "table 8 restates the absent Table 3"))
        else:
            out.append(_row(m, a["level"], a["statistic"], a["value"], "mm", "thoracic", ABSENT_TABLE, "",
                            "transcription of the absent Table 3 (provenance/absent.csv)"))
    order = {lv: i for i, lv in enumerate(LEVELS_C2)}
    out.sort(key=lambda r: (MEASURES.index(r["measure"]), SIDES.index(r["side"]), order[r["level"]], r["statistic"]))
    seen = set()
    for r in out:
        key = (r["measure"], r["side"], r["level"], r["statistic"])
        if key in seen:
            raise ValueError("two rows for %s" % (key,))
        seen.add(key)
    return out


def write_long_csv(path: str = LONG_CSV) -> int:
    rows = rows_from_provenance(read_csv(PROVENANCE_CSV), read_csv(ABSENT_CSV))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        fh.write("# Panjabi's quantitative three-dimensional anatomy, cervical (1991), thoracic (1991),\n"
                 "# lumbar (1992) and articular facets (1993): every present-study mean and standard\n"
                 "# error of the dimension tables, written by `python -m schwingcheck table write` from\n"
                 "# archive/bordercall/reference/provenance/provenance.csv (two readings by eye of every\n"
                 "# cell) and absent.csv (the thoracic body table, not in the scan). Do not edit by hand.\n")
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def long_csv_text(rows: Sequence[dict]) -> str:
    import io
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def check_long_csv(path: str = LONG_CSV) -> list:
    """What differs between the committed CSV and what write would write now."""
    want = rows_from_provenance(read_csv(PROVENANCE_CSV), read_csv(ABSENT_CSV))
    have = read_long_csv(path)
    problems = []
    if len(want) != len(have):
        problems.append("%d rows committed, %d from the provenance" % (len(have), len(want)))
    for a, b in zip(have, want):
        if a != b:
            problems.append("committed %s, provenance gives %s" % (a, b))
            if len(problems) > 10:
                break
    return problems


def read_long_csv(path: str = LONG_CSV) -> list:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(line for line in fh if not line.startswith("#")))


def load(path: str = LONG_CSV):
    """The table as an xarray Dataset with dimensions (level, measure, side)."""
    import xarray as xr
    rows = read_long_csv(path)
    measures = [m for m in MEASURES if any(r["measure"] == m for r in rows)]
    shape = (len(LEVELS_C2), len(measures), len(SIDES))
    mean = np.full(shape, np.nan)
    sem = np.full(shape, np.nan)
    n = np.full(shape, np.nan)
    cell = np.full(shape, "", dtype=object)
    basis = np.full(shape, "", dtype=object)
    mnemonic = np.full((len(measures), len(SIDES)), "", dtype=object)
    for r in rows:
        i, j, k = LEVELS_C2.index(r["level"]), measures.index(r["measure"]), SIDES.index(r["side"])
        target = mean if r["statistic"] == "mean" else sem
        target[i, j, k] = float(r["value"])
        n[i, j, k] = float(r["n"])
        mnemonic[j, k] = r["mnemonic"]
        if r["statistic"] == "mean":
            cell[i, j, k] = r["cell"]
            basis[i, j, k] = r["basis"]
    info = [MEASURE_INFO[m] for m in measures]
    ds = xr.Dataset(
        {"mean": (("level", "measure", "side"), mean),
         "sem": (("level", "measure", "side"), sem),
         "sd": (("level", "measure", "side"), sem * np.sqrt(n)),
         "n": (("level", "measure", "side"), n),
         "cell": (("level", "measure", "side"), cell.astype(str)),
         "basis": (("level", "measure", "side"), basis.astype(str))},
        coords={"level": LEVELS_C2, "measure": measures, "side": SIDES,
                "kind": ("measure", [m.kind for m in info]),
                "units": ("measure", [{"length": "mm", "area": "mm2", "angle": "deg"}[m.kind] for m in info]),
                "planes": ("measure", [" ".join(m.planes) for m in info]),
                "definition": ("measure", [m.definition for m in info]),
                "mnemonic": (("measure", "side"), mnemonic.astype(str))},
        attrs={"source": os.path.relpath(path, ROOT), "sha256": sha256(path), "specimens": SPECIMENS,
               "sd": "sem * sqrt(n), the population SD"})
    return ds


def reference(ds, selections: Sequence[Tuple[str, str]], levels: Sequence[str]) -> Dict[str, Dict[str, tuple]]:
    """{name: {level: (mean, population SD)}} for the rule and the generator, in the archive's
    shape. A selection is (measure, side); the side `mean` is the mean of right and left, of the
    means and of the standard errors alike, as the archive's pedicle and pedicle_h were built."""
    out = {}
    for measure, side in selections:
        name = selection_name(measure, side)
        out[name] = {}
        for lv in levels:
            if side == "mean":
                r, l_ = ds["mean"].sel(level=lv, measure=measure, side="right").item(), \
                    ds["mean"].sel(level=lv, measure=measure, side="left").item()
                sr, sl = ds["sem"].sel(level=lv, measure=measure, side="right").item(), \
                    ds["sem"].sel(level=lv, measure=measure, side="left").item()
                nn = ds["n"].sel(level=lv, measure=measure, side="right").item()
                mu, sd = (r + l_) / 2.0, (sr + sl) / 2.0 * math.sqrt(nn)
            else:
                mu = ds["mean"].sel(level=lv, measure=measure, side=side).item()
                sd = ds["sd"].sel(level=lv, measure=measure, side=side).item()
            if not (np.isfinite(mu) and np.isfinite(sd)):
                raise ValueError("the table has no %s (%s) at %s" % (measure, side, lv))
            out[name][lv] = (float(mu), float(sd))
    return out


def selection_name(measure: str, side: str) -> str:
    return measure if side == "whole" else "%s:%s" % (measure, side)


def arrays(ref: Dict[str, Dict[str, tuple]], names: Sequence[str], levels: Sequence[str]) -> Tuple[np.ndarray, np.ndarray]:
    """The means and population SDs as (measures, levels) arrays."""
    mu = np.array([[ref[nm][lv][0] for lv in levels] for nm in names], float)
    sd = np.array([[ref[nm][lv][1] for lv in levels] for nm in names], float)
    return mu, sd

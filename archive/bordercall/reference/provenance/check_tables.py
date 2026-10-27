"""Hold each paper's comparison table to its own dimension tables.

    python check_tables.py       # every Present Study cell against the table it restates

Each paper closes with a table that sets its own means beside earlier studies' (cervical
Table 7, thoracic Table 8, lumbar Table 6, facets Tables 9 and 10). Its Present Study column
restates values the dimension tables print, so the two are read from different cells of
different pages and must agree: a single-sided dimension to the digit, a paired one (right
and left) as their mean, to the rounding the comparison table prints at; the facets paper's
Table 10 prints the sagittal angle of the superior facets in whole degrees as the mean of the
right and left magnitudes (Table 6 gives the right side a minus by its sign convention), and
is held within a degree. crosstable.csv is the record of every such pair with whether it
holds; where a paper's two tables disagree, the row says so, and the test holds the record
either way, as check_prose.py does for the prose.
"""
from __future__ import annotations

import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import check_prose  # noqa: E402
import tables  # noqa: E402

FIELDS = ["comparison", "level", "measure", "cells", "rule", "value", "restated", "agrees", "note"]

# the comparison table's row mnemonic -> (dimension table, mnemonics it restates, rule)
RESTATES = {
    "cervical-t7": {"EPDl": ("cervical-t2", ["EPDl"], "equal"), "EPWl": ("cervical-t2", ["EPWl"], "equal"),
                    "EPAl": ("cervical-t2", ["EPAl"], "equal"), "SCD": ("cervical-t3", ["SCD"], "equal"),
                    "SCW": ("cervical-t3", ["SCW"], "equal"), "VBH": ("cervical-t2", ["VBHp"], "equal")},
    "thoracic-t8a": {"EPDl": ("thoracic-t3", ["EPDl"], "equal"), "EPWl": ("thoracic-t3", ["EPWl"], "equal"),
                     "VBHp": ("thoracic-t3", ["VBHp"], "equal"),
                     "SCD": ("thoracic-t4", ["SCD"], "equal"), "SCW": ("thoracic-t4", ["SCW"], "equal"),
                     "PDH": ("thoracic-t5", ["PDHr", "PDHl"], "lr_mean")},
    "thoracic-t8b": {"PDH": ("thoracic-t5", ["PDHr", "PDHl"], "lr_mean"), "PDW": ("thoracic-t5", ["PDWr", "PDWl"], "lr_mean"),
                     "PDIs": ("thoracic-t5", ["PDIsr", "PDIsl"], "lr_mean"), "PDIt": ("thoracic-t5", ["PDItr", "PDItl"], "lr_mean")},
    "lumbar-t6": {"EPDl": ("lumbar-t2", ["EPDl"], "equal"), "EPWl": ("lumbar-t2", ["EPWl"], "equal"),
                  "VBHp": ("lumbar-t2", ["VBHp"], "equal"), "SCD": ("lumbar-t3", ["SCD"], "equal"),
                  "SCW": ("lumbar-t3", ["SCW"], "equal"), "PDH": ("lumbar-t4", ["PDHr", "PDHl"], "lr_mean"),
                  "PDW": ("lumbar-t4", ["PDWr", "PDWl"], "lr_mean"), "PDIs": ("lumbar-t4", ["PDIsr", "PDIsl"], "lr_mean"),
                  "PDIt": ("lumbar-t4", ["PDItr", "PDItl"], "lr_mean")},
    "facets-t9": {"FCHs": ("facets-t2", ["FCHsr", "FCHsl"], "lr_mean"), "FCWs": ("facets-t2", ["FCWsr", "FCWsl"], "lr_mean"),
                  "IFWs": ("facets-t5", ["IFWs"], "equal"), "IFH": ("facets-t5", ["IFHr", "IFHl"], "lr_mean")},
    "facets-t10": {"Ss": ("facets-t6", ["Ssr", "Ssl"], "abs_mean")},
}
TOLERANCE = {"equal": 0.05, "lr_mean": 0.1, "abs_mean": 1.0}


def read_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def pairs(prov: list[dict]) -> list[dict]:
    """Every Present Study cell of a comparison table beside the cells it restates."""
    by_key: dict[tuple, dict] = {}
    for r in prov:
        if r["statistic"] == "mean" and r["value"] != "":
            by_key[(r["table"], r["measure"], r["level"], r["study"])] = r
    out = []
    for comparison, rows in RESTATES.items():
        for r in prov:
            if r["table"] != comparison or r["study"] != "present" or r["statistic"] != "mean":
                continue
            if r["measure"] not in rows:
                continue
            source, mnemonics, rule = rows[r["measure"]]
            cells = [by_key.get((source, m, r["level"], "present")) for m in mnemonics]
            if any(c is None for c in cells) or r["value"] == "":
                out.append({"comparison": r["id"], "level": r["level"], "measure": r["measure"], "cells": "",
                            "rule": rule, "value": "", "restated": r["value"], "agrees": "",
                            "note": "no cell of %s prints %s at %s" % (source, "/".join(mnemonics), r["level"])})
                continue
            got = check_prose.evaluate(rule, [float(c["value"]) for c in cells])
            holds = abs(got - float(r["value"])) <= TOLERANCE[rule] + 1e-9
            out.append({"comparison": r["id"], "level": r["level"], "measure": r["measure"],
                        "cells": ";".join(c["id"] for c in cells), "rule": rule, "value": "%.4g" % got,
                        "restated": r["value"], "agrees": "yes" if holds else "no",
                        "note": "" if holds else "the comparison table restates %s as %s; the dimension table gives %.4g"
                        % (r["measure"], r["value"], got)})
    return out


def check(prov: list[dict], record: list[dict]) -> list[str]:
    """The record of crosstable.csv held to the cells as they are now."""
    now = {p["comparison"]: p for p in pairs(prov)}
    problems = []
    for rec in record:
        p = now.get(rec["comparison"])
        if p is None:
            problems.append("%s is in crosstable.csv but not in provenance.csv" % rec["comparison"])
        elif p["agrees"] != rec["agrees"] or p["value"] != rec["value"]:
            problems.append("%s: crosstable.csv says agrees=%s value=%s, the cells give agrees=%s value=%s"
                            % (rec["comparison"], rec["agrees"], rec["value"], p["agrees"], p["value"]))
    for cid in now:
        if cid not in {rec["comparison"] for rec in record}:
            problems.append("%s is restated by a comparison table but not in crosstable.csv" % cid)
    return problems


def main() -> int:
    prov = read_csv(os.path.join(HERE, "provenance.csv"))
    out = pairs(prov)
    with open(os.path.join(HERE, "crosstable.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    bad = [p for p in out if p["agrees"] == "no"]
    print("%d restated values, %d held to a cell, %d disagree" % (len(out), sum(1 for p in out if p["cells"]), len(bad)))
    for p in bad:
        print("  " + p["note"] + " (" + p["comparison"] + ")")
    return 0


if __name__ == "__main__":
    sys.exit(main())

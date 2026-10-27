"""Hold the reference CSVs to the provenance: every value they carry was read from a cell.

    python check_csv.py          # the report, and changes.csv beside this file

panjabi_full_spine.csv and panjabi_1992.csv were transcribed before the provenance existed.
This sets each of their values beside the value provenance.csv read from the paper's cell,
and lists every one that differs (changes.csv). A mean of left and right is derived, and is
checked against the two cells it is derived from. Until 27 October 2026 the thoracic body
table (printed page 892) was on no page the scan carried and absent.csv listed its values with
what they rested on; the owner's second scan of that page is read now (README.md), so every
value has its cell and absent.csv is gone.
"""
from __future__ import annotations

import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REFERENCE = os.path.dirname(HERE)

CSVS = ["panjabi_full_spine.csv", "panjabi_1992.csv"]
DIMENSION_TABLES = {"cervical": ("cervical-t2", "cervical-t3", "cervical-t4"),
                    "thoracic": ("thoracic-t3", "thoracic-t4", "thoracic-t5"),
                    "lumbar": ("lumbar-t2", "lumbar-t3", "lumbar-t4")}


def region_of(level: str) -> str:
    return {"C": "cervical", "T": "thoracic", "L": "lumbar"}[level[0]]


def read_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        lines = [ln for ln in fh if not ln.startswith("#")]
    return list(csv.DictReader(lines))


def load_provenance() -> list[dict]:
    return read_csv(os.path.join(HERE, "provenance.csv"))


def same(a: str, b: str) -> bool:
    try:
        return abs(float(a) - float(b)) < 1e-6
    except ValueError:
        return a.strip() == b.strip()


class Provenance:
    def __init__(self, rows: list[dict]):
        self.rows = rows
        self.index: dict[tuple, dict] = {}
        for r in rows:
            if r["study"] != "present" or r["value"] == "":
                continue
            key = (r["paper"], r["table"], r["measure"], r["level"], r["statistic"])
            self.index.setdefault(key, r)

    def value(self, paper: str, measure: str, level: str, statistic: str) -> dict | None:
        for table in DIMENSION_TABLES[paper]:
            r = self.index.get((paper, table, measure, level, statistic))
            if r is not None:
                return r
        return None


def expected(prov: Provenance, mnemonic: str, level: str, statistic: str) -> tuple[str, str] | None:
    """The provenance value a CSV row should hold, and the cell it comes from."""
    paper = region_of(level)
    if "mean of l/r" in mnemonic or mnemonic.startswith("PDW = mean("):
        base = mnemonic[:3]
        r = prov.value(paper, base + "r", level, statistic)
        l_ = prov.value(paper, base + "l", level, statistic)
        if r is None or l_ is None:
            return None
        return "%.4f" % ((float(r["value"]) + float(l_["value"])) / 2.0), r["id"] + " and " + l_["id"]
    name = mnemonic.split(" ")[0]
    r = prov.value(paper, name, level, statistic)
    if r is None:
        return None
    return r["value"], r["id"]


def check(prov: Provenance) -> tuple[list[dict], list[dict], list[dict]]:
    """Every CSV value as matched, changed or in no cell."""
    matched, changed, missing = [], [], []
    for name in CSVS:
        for row in read_csv(os.path.join(REFERENCE, name)):
            for statistic in ("mean", "sem"):
                if row[statistic] == "":
                    continue
                want = expected(prov, row["panjabi_name"], row["level"], statistic)
                record = {"csv": name, "measure": row["measure"], "level": row["level"],
                          "panjabi_name": row["panjabi_name"], "statistic": statistic,
                          "csv_value": row[statistic]}
                if want is None:
                    missing.append(record)
                    continue
                value, cell = want
                record.update({"provenance_value": value, "cell": cell})
                (matched if same(row[statistic], value) else changed).append(record)
    return matched, changed, missing


def write_changes(changed: list[dict]) -> None:
    fields = ["csv", "measure", "level", "panjabi_name", "statistic", "csv_value", "provenance_value", "cell"]
    with open(os.path.join(HERE, "changes.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in changed:
            w.writerow({k: r.get(k, "") for k in fields})


def main() -> int:
    prov = Provenance(load_provenance())
    matched, changed, missing = check(prov)
    write_changes(changed)
    print("%d CSV values match their cell, %d differ, %d are in no cell" % (len(matched), len(changed), len(missing)))
    for r in changed:
        print("  CHANGED %s %s %s %s: csv %s, paper %s (%s)" % (r["csv"], r["measure"], r["level"], r["statistic"],
                                                           r["csv_value"], r["provenance_value"], r["cell"]))
    for r in missing:
        print("  MISSING %s %s %s %s: csv %s" % (r["csv"], r["measure"], r["level"], r["statistic"], r["csv_value"]))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())

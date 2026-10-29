"""Check one mapped reading: a reconciled reading of a paper's tables with every row given its
measure in the vocabulary, its cohort and technique, and the factor that brings it to the
vocabulary's units.

Usage: python3 -I check_mapped.py <mapped.csv> <cohorts.json> [<vocabulary.csv>]

The merged table and every comparison drawn from it read these columns and nothing else, so a
row whose key is not in the vocabulary, whose cohort or technique the paper's cohorts file does
not name, or whose factor would put a length in other units than millimetres, would be merged
silently wrong. The check refuses each of those, and a value that the factor does not turn into
the canonical value the row gives.
"""

import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_reading  # noqa: E402

MAPPED = check_reading.RECONCILED + [
    "key", "cohort", "technique", "factor", "canonical_value", "canonical_units", "definition",
    "vs_panjabi", "map_note",
]
VS_PANJABI = {"same", "close", "differs", "none"}


def vocabulary(path):
    return {row["key"]: row for row in csv.DictReader(open(path, newline=""))}


def ids_in(cohorts_path):
    data = json.load(open(cohorts_path))
    cohorts = {c.get("cohort") for c in data.get("cohorts", [])}
    techniques = {t.get("technique") for t in data.get("techniques", [])}
    return cohorts, techniques


def row_problems(row, where, vocab, cohorts, techniques):
    out = []
    entry = vocab.get(row["key"])
    if entry is None:
        return ["%s: key %r is not in the vocabulary" % (where, row["key"])]
    if row["cohort"] not in cohorts:
        out.append("%s: cohort %r is not in the cohorts file" % (where, row["cohort"]))
    if row["technique"] not in techniques and row["technique"] != "none":
        out.append("%s: technique %r is not in the cohorts file" % (where, row["technique"]))
    if row["vs_panjabi"] not in VS_PANJABI:
        out.append("%s: vs_panjabi %r is not one of %s" % (where, row["vs_panjabi"], sorted(VS_PANJABI)))
    if entry["panjabi"] == "no" and row["vs_panjabi"] in ("same", "close"):
        out.append("%s: %s is not a Panjabi measure, so vs_panjabi cannot be %s" % (where, row["key"], row["vs_panjabi"]))
    out += unit_problems(row, where, entry)
    return out


def unit_problems(row, where, entry):
    if not row["value"].strip():
        return [] if not row["canonical_value"].strip() else ["%s: a canonical value with no value" % where]
    try:
        factor = float(row["factor"])
        canonical = float(row["canonical_value"])
        value = float(row["value"])
    except ValueError:
        return ["%s: factor %r or canonical_value %r is not a number" % (where, row["factor"], row["canonical_value"])]
    out = []
    dimensionless = row["statistic"] in ("n", "count", "p", "r", "icc", "kappa", "percent", "ratio")
    wanted = entry["units"]
    if not dimensionless and wanted not in ("as printed",) and row["canonical_units"] != wanted:
        out.append("%s: canonical_units %r, the vocabulary's %s are %r" % (where, row["canonical_units"], row["key"], wanted))
    if abs(value * factor - canonical) > 1e-6 * max(1.0, abs(canonical)):
        out.append("%s: value %s x factor %s is not canonical_value %s" % (where, value, factor, canonical))
    return out


def problems_of(path, cohorts_path, vocab_path):
    raw = open(path, "rb").read()
    problems = []
    if any(b > 127 for b in raw):
        problems.append("non-ASCII bytes")
    if b"\r" in raw:
        problems.append("CR line ends")
    rows = list(csv.reader(raw.decode("ascii", "replace").splitlines()))
    if not rows or rows[0] != MAPPED:
        return problems + ["header is not the mapped reading's columns in order"]
    vocab = vocabulary(vocab_path)
    cohorts, techniques = ids_in(cohorts_path)
    for number, cells in enumerate(rows[1:], start=2):
        if len(cells) != len(MAPPED):
            problems.append("line %d: %d cells, not %d" % (number, len(cells), len(MAPPED)))
            continue
        row = dict(zip(MAPPED, cells))
        problems += row_problems(row, "line %d" % number, vocab, cohorts, techniques)
    return problems


def main():
    vocab_path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "vocabulary.csv")
    problems = problems_of(sys.argv[1], sys.argv[2], vocab_path)
    for problem in problems[:200]:
        print(problem)
    if len(problems) > 200:
        print("... and %d more" % (len(problems) - 200))
    print("%s: %d problems" % (sys.argv[1], len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

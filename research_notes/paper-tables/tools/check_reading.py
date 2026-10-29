"""Check one page reading of a paper's tables before it is compared or merged.

Usage: python3 -I check_reading.py <reading.csv> [<paper id>]

A reading is one row per printed cell and statistic, as spine-program's
synthetic_spine/verification/closed_page_reading.csv was made, with two more columns: where
the values come from (this paper's own subjects, or another study a comparison table quotes)
and, in a reconciled reading, how the cell was checked. The check refuses what would make the
merged table wrong without anyone seeing it: a header out of order, a value that is not the
number its printed cell shows, a level or a statistic outside the vocabularies below, a row
twice, and any byte that is not ASCII.
"""

import csv
import re
import sys

COLUMNS = [
    "paper", "table", "pdf_page", "journal_page", "row_label", "column_label", "measure_label",
    "level", "side", "sex", "group", "statistic", "printed_as", "value", "units", "legibility",
    "source_of_values", "note",
]
RECONCILED = COLUMNS + ["check", "check_note"]
CHECKS = {"agreed", "resolved", "single"}

VERTEBRA = r"(C[1-7]|T(1[0-3]|[1-9])|L[1-6]|S[1-5]|Co[1-4]?)"
LEVEL = re.compile(r"^(%s|%s-%s|%s to %s)$" % (VERTEBRA, VERTEBRA, VERTEBRA, VERTEBRA, VERTEBRA))
STATISTICS = {
    "mean", "sd", "sem", "n", "min", "max", "median", "mode", "range", "p", "r", "icc", "kappa",
    "ci_low", "ci_high", "percent", "count", "total", "variance", "iqr", "q1", "q3",
    "percentile", "single", "ratio", "difference", "other",
}
SIDES = {"", "right", "left", "both", "mean of sides"}
NUMBER = re.compile(r"[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?")


def problems_of(path, paper=None):
    problems = []
    raw = open(path, "rb").read()
    if any(b > 127 for b in raw):
        problems.append("non-ASCII bytes")
    if b"\r" in raw:
        problems.append("CR line ends")
    rows = list(csv.reader(raw.decode("ascii", "replace").splitlines()))
    if not rows:
        return ["empty file"]
    header = rows[0]
    if header not in (COLUMNS, RECONCILED):
        problems.append("header is not the reading's columns in order: %s" % ",".join(header))
        return problems
    seen = set()
    for number, cells in enumerate(rows[1:], start=2):
        if len(cells) != len(header):
            problems.append("line %d: %d cells, not %d" % (number, len(cells), len(header)))
            continue
        row = dict(zip(header, cells))
        problems += row_problems(row, number, paper, header == RECONCILED)
        key = tuple(row[c] for c in COLUMNS if c not in ("legibility", "note"))
        if key in seen:
            problems.append("line %d: the same row twice" % number)
        seen.add(key)
    return problems


def row_problems(row, number, paper, reconciled):
    out = []
    where = "line %d" % number
    if paper and row["paper"] != paper:
        out.append("%s: paper %r, not %r" % (where, row["paper"], paper))
    for column in ("paper", "table", "pdf_page", "statistic", "source_of_values"):
        if not row[column].strip():
            out.append("%s: %s is empty" % (where, column))
    if row["pdf_page"] and not row["pdf_page"].isdigit():
        out.append("%s: pdf_page %r is not a page number" % (where, row["pdf_page"]))
    if row["level"] and not LEVEL.match(row["level"]):
        out.append("%s: level %r is outside the vocabulary" % (where, row["level"]))
    if row["statistic"] not in STATISTICS:
        out.append("%s: statistic %r is outside the vocabulary" % (where, row["statistic"]))
    if row["side"] not in SIDES:
        out.append("%s: side %r is outside the vocabulary" % (where, row["side"]))
    out += value_problems(row, where)
    if reconciled and row["check"] not in CHECKS:
        out.append("%s: check %r is not one of %s" % (where, row["check"], sorted(CHECKS)))
    return out


def value_problems(row, where):
    printed, value = row["printed_as"], row["value"]
    if not printed.strip():
        return [] if not value.strip() else ["%s: a value with nothing printed" % where]
    if not value.strip():
        return [] if not NUMBER.search(printed) else ["%s: %r is printed and no value given" % (where, printed)]
    try:
        number = float(value)
    except ValueError:
        return ["%s: value %r is not a number" % (where, value)]
    found = [float(m.group(0)) for m in NUMBER.finditer(printed.replace(",", ""))]
    found += [-x for x in found]
    if not any(abs(number - x) < 1e-9 * max(1.0, abs(x)) for x in found) and not spelled(printed):
        return ["%s: value %s is not a number %r prints" % (where, value, printed)]
    return []


def spelled(printed):
    words = "one two three four five six seven eight nine ten eleven twelve hundred thousand".split()
    return any(word in printed.lower() for word in words)


def main():
    paper = sys.argv[2] if len(sys.argv) > 2 else None
    problems = problems_of(sys.argv[1], paper)
    for problem in problems[:200]:
        print(problem)
    if len(problems) > 200:
        print("... and %d more" % (len(problems) - 200))
    print("%s: %d problems" % (sys.argv[1], len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

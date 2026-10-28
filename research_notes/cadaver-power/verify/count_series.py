# Copied for the cadaver-power note from the reviewers' verify-verify-arithmetic/count_series.py, 2026-10-28.
# Changed: the absolute paths became the command-line arguments below.
#     python3 -I verify/count_series.py SYNTHETIC_SPINE_DATA
"""Count the series in synthetic_spine's two tables, their n and cohorts, and the cells each covers."""
import csv
import collections
import os
import sys

D = os.path.join(sys.argv[1], "")


def rows(name):
    with open(D + name, newline="") as fh:
        lines = [l for l in fh if not l.startswith("#")]
    return list(csv.DictReader(lines))


level = rows("level_references.csv")
ped = rows("pedicle_width_references.csv")

print("level table rows", len(level), "pedicle rows", len(ped))
ls = collections.OrderedDict()
for r in level:
    ls.setdefault(r["series"], set()).add((r["cohort"], r["n"], r["modality"]))
ps = collections.OrderedDict()
for r in ped:
    ps.setdefault(r["series"], set()).add((r["cohort"], r["n"], r["modality"]))
print("level series", len(ls), "pedicle series", len(ps))
for s, v in ls.items():
    print("  L", s, sorted(v))
for s, v in ps.items():
    print("  P", s, sorted(v))

# Distinct series, treating "Panjabi" in the pedicle table as Panjabi 1992.
def norm(s):
    return {"Panjabi": "Panjabi 1992"}.get(s, s)

allser = set(ls) | {norm(s) for s in ps}
print("distinct series over both tables:", len(allser))
overlap = set(ls) & {norm(s) for s in ps}
print("in both:", overlap)

# Cells: measure x level with how many series give a mean.
cells = collections.defaultdict(set)
for r in level:
    cells[(r["measure"], r["level"])].add(r["series"])
for r in ped:
    cells[("PDW", r["level"])].add(norm(r["series"]))
print("\ncells (measure, level): number of series")
by_m = collections.defaultdict(list)
for (m, lv), s in sorted(cells.items()):
    by_m[m].append((lv, len(s)))
for m, v in by_m.items():
    print(" ", m, v)
print("max series in a cell:", max(len(s) for s in cells.values()))
print("cells with any series:", len(cells))
print("levels per measure:", {m: sorted({lv for lv, _ in v}) for m, v in by_m.items()})

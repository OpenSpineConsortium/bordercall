"""A run's lines.csv of two studies, as python -m morphometry run --masks DIR writes for a folder of
masks: the thin phantom's rows as study 0001 and the same rows moved 40 mm as study 0002."""
import csv
import sys
src, dst = sys.argv[1], sys.argv[2]
rows = list(csv.DictReader(open(src)))
out = []
for r in rows:
    out.append(dict(r))
    s = dict(r, study="0002")
    for k in ("ax", "bx"):
        s[k] = repr(float(s[k]) + 40.0)
    out.append(s)
with open(dst, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(out)

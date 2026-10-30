"""Probe: the new write_rows against the old one, byte for byte, for every kind of value."""
import csv, io, math, sys
import numpy as np
sys.path.insert(0, "repo")
from morphometry import __main__ as RUN

FIELDS = ["study", "level", "key", "value", "note"]

def old_write(rows, f):
    w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    for r in rows:
        v = r["value"]
        w.writerow({**r, "value": ("%.4f" % v) if isinstance(v, float) and math.isfinite(v) else
                    ("" if isinstance(v, float) else v)})

values = [1.23456789, float("nan"), float("inf"), -float("inf"), 0.0, -0.0, 3, True, False, "L5", None, "",
          np.float64(2.5), np.float64("nan"), np.float32(2.5), np.float32(1 / 3), np.float32("nan"), np.int64(7),
          np.bool_(True), np.float16(0.1), 1e300, 5e-5, -5e-5, 12345678.123456]
rows = [{"study": "0001", "level": "L3", "key": "k%d" % i, "value": v, "note": ""} for i, v in enumerate(values)]
a, b = io.StringIO(), io.StringIO()
old_write(rows, a)
w = csv.DictWriter(b, fieldnames=FIELDS, lineterminator="\n"); w.writeheader()
for r in rows:
    w.writerow({k: RUN.number(x) for k, x in r.items()})
same = a.getvalue() == b.getvalue()
print("same:", same)
for la, lb in zip(a.getvalue().splitlines(), b.getvalue().splitlines()):
    print(("   " if la == lb else "!! ") + la + ("" if la == lb else "   vs   " + lb))
# a note or a study that is a float
rows2 = [{"study": "0001", "level": "L3", "key": "x", "value": 1.0, "note": 0.5}]
a, b = io.StringIO(), io.StringIO()
old_write(rows2, a)
w = csv.DictWriter(b, fieldnames=FIELDS, lineterminator="\n"); w.writeheader()
for r in rows2:
    w.writerow({k: RUN.number(x) for k, x in r.items()})
print("float note:", repr(a.getvalue().splitlines()[1]), repr(b.getvalue().splitlines()[1]))

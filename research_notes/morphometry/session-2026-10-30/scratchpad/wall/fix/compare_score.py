"""Two score.py JSON outputs side by side: the readings that differ, and the parted counts.

  compare_score.py <before.json> <after.json>
"""
import json
import math
import sys


def main():
    a = {r["key"]: r for r in json.load(open(sys.argv[1]))}
    b = {r["key"]: r for r in json.load(open(sys.argv[2]))}
    moved = 0
    for k in sorted(a):
        ea, eb = a[k]["wall_err"], b[k]["wall_err"]
        same = (math.isnan(ea) and math.isnan(eb)) or abs(ea - eb) < 1e-9
        if not same:
            moved += 1
            print("%-40s %+7.3f -> %+7.3f  parted %s -> %s  across %s" % (
                k, ea, eb, a[k]["info"].get("parted"), b[k]["info"].get("parted"), b[k]["info"].get("across")))
    for name, rows in (("before", a), ("after", b)):
        for sp in ("thin", "thick"):
            sel = [r for r in rows.values() if r["spacing"] == sp]
            parted = sum(1 for r in sel if r["info"].get("parted") in (True, 1.0, "True"))
            print("%s %s: %d of %d parted" % (name, sp, parted, len(sel)))
    print("%d readings moved" % moved)


if __name__ == "__main__":
    main()

"""compare_rows.py A B: compare two morphometry run folders' rows/<study>.csv, value by value (the
seconds and code rows left out): how many values agree to 1e-6, how many differ and by how much,
and how many are finite in one and not the other, with the largest differences named.
"""
import csv
import math
import os
import sys

SKIP = {"seconds", "code"}


def read(folder):
    out = {}
    for name in sorted(os.listdir(os.path.join(folder, "rows"))):
        with open(os.path.join(folder, "rows", name), newline="") as fh:
            for r in csv.DictReader(fh):
                if r["key"] in SKIP:
                    continue
                out[(r["study"], r["level"], r["key"])] = (r["value"], r["note"])
    return out


def num(s):
    try:
        return float(s)
    except ValueError:
        return None


def main(a, b):
    A, B = read(a), read(b)
    same = differ = finiteness = notes = 0
    only = len(set(A) ^ set(B))
    worst = []
    for k in sorted(set(A) & set(B)):
        (va, na), (vb, nb) = A[k], B[k]
        if na != nb:
            notes += 1
        x, y = num(va), num(vb)
        if x is None or y is None:
            same += va == vb
            differ += va != vb
            continue
        fx, fy = math.isfinite(x), math.isfinite(y)
        if fx != fy:
            finiteness += 1
            worst.append((math.inf, k, va, vb))
        elif not fx or abs(x - y) <= 1e-6:
            same += 1
        else:
            differ += 1
            worst.append((abs(x - y), k, va, vb))
    print("%s vs %s: %d keys in common, %d in one only; %d agree, %d differ, %d finite in one only, %d notes differ"
          % (os.path.basename(a), os.path.basename(b), len(set(A) & set(B)), only, same, differ, finiteness, notes))
    for d, k, va, vb in sorted(worst, reverse=True)[:8]:
        print("   %s %s %s: %s vs %s" % (k[0], k[1], k[2], va, vb))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

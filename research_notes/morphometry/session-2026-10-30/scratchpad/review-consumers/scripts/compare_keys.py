"""Every (level kind, key) each engine wrote over the phantom masks, and the values that changed."""
import csv, math, sys
from collections import defaultdict

S = sys.argv[1]


def kind(level):
    if level in ("study", "column", "pelvis"):
        return level
    return "disc" if "-" in level else "vertebra"


def load(eng):
    rows = {}
    keys = defaultdict(set)
    notes = {}
    dup = defaultdict(int)
    for scheme in ("enhance", "verse"):
        for r in csv.DictReader(open(f"{S}/out/{eng}/{scheme}/rows.csv", newline="")):
            k = (r["study"], r["level"], r["key"])
            if k in rows:
                dup[k] += 1
            rows[k] = r["value"]
            notes[k] = r["note"]
            keys[kind(r["level"])].add(r["key"])
    return rows, keys, notes, dup


old, ok, onotes, odup = load("old")
new, nk, nnotes, ndup = load("new")
print("duplicates old", dict(odup), "new", dict(ndup))
for kd in sorted(set(ok) | set(nk)):
    a, b = ok.get(kd, set()), nk.get(kd, set())
    print(f"== {kd}: old {len(a)} keys, new {len(b)}")
    if a - b:
        print("   only old:", sorted(a - b))
    if b - a:
        print("   only new:", sorted(b - a))


def num(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except ValueError:
        return None


same = changed = 0
became_blank, became_value = [], []
diffs = defaultdict(list)
for k in sorted(set(old) & set(new)):
    if k[2].startswith("flag:") or k[2] in ("code", "seconds"):
        continue
    a, b = num(old[k]), num(new[k])
    if a is None and b is not None:
        became_value.append((k, old[k], onotes[k], new[k]))
    elif a is not None and b is None:
        became_blank.append((k, old[k], new[k], nnotes[k]))
    elif a is not None and b is not None:
        if abs(a - b) < 1e-9:
            same += 1
        else:
            changed += 1
            diffs[k[2]].append(b - a)
print("values equal", same, "changed", changed)
print("--- keys whose values changed (n, median new-old, max |d|):")
for key in sorted(diffs):
    d = sorted(diffs[key])
    print("  %-28s n %3d  med %+8.3f  max %7.3f" % (key, len(d), d[len(d)//2], max(abs(x) for x in d)))
unchanged = sorted({k[2] for k in set(old) & set(new) if not k[2].startswith("flag:")} - set(diffs))
print("--- keys with no value changed anywhere:", unchanged)
print("--- a value in old, blank in new:")
for k, a, b, note in became_blank:
    print("  ", k, a, "->", repr(b), "|", note[:150])
print("--- blank in old, a value in new:")
for k, a, note, b in became_value:
    print("  ", k, repr(a), "->", b, "| old note:", note[:120])

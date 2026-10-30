"""Tabulate coverage.py's rows: per alteration and slice, apart for parted and not parted."""
import glob
import json
import math
import sys

rows = []
for p in sys.argv[1:]:
    rows += json.load(open(p))
alts = sorted({r["alt"] for r in rows}, key=lambda a: (a != "clean", a))
for alt in alts:
    for sp in ("thin", "thick"):
        sel = [r for r in rows if r["alt"] == alt and r["spacing"] == sp]
        refused = [r for r in sel if not math.isfinite(r["err"])]
        read = [r for r in sel if math.isfinite(r["err"])]
        for parted in (True, False):
            g = [r for r in read if bool(r.get("parted")) == parted]
            if not g:
                continue
            inside = sum(r["free_lo_deg"] - 1e-9 <= r["truth"] <= r["free_hi_deg"] + 1e-9 for r in g)
            within = sum(abs(r["err"]) <= r["free_deg"] for r in g)
            half = sum(abs(r["err"]) <= 0.5 * r["free_deg"] for r in g)
            flagged = sum(r["free_deg"] > 3.0 for r in g)
            unfl = [r for r in g if r["free_deg"] <= 3.0]
            big = sum(abs(r["err"]) > 1.5 for r in unfl)
            worst = max(g, key=lambda r: abs(r["err"]))
            print("%-16s %-5s parted=%-5s n %2d refused(all) %d | truth in range %2d | |err|<=free %2d <=free/2 %2d"
                  " | flagged %d | unflagged |err|>1.5 %2d | max|err| %.2f (free %.2f) med free %.2f"
                  % (alt, sp, parted, len(g), len(refused), inside, within, half, flagged, big, abs(worst["err"]),
                     worst["free_deg"], sorted(r["free_deg"] for r in g)[len(g) // 2]))

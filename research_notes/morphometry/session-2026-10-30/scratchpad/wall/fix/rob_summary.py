"""The robustness rows of one reader against another's, per alteration and slice thickness: the
largest error, the readings refused, the labels parted, and the dropped share and the gate's
overshoot where the rows carry them.

  rob_summary.py <base_0.json,base_1.json> <new_0.json,new_1.json>
"""
import json
import math
import sys


def rows(arg):
    out = []
    for p in arg.split(","):
        out += json.load(open(p))
    return {(r["key"], r["alt"]): r for r in out}


def stats(sel, col):
    col = col if any(col in r for r in sel) else "proposed"
    e = [abs(r[col]) for r in sel if math.isfinite(r[col])]
    return (max(e) if e else float("nan"), sorted(e)[len(e) // 2] if e else float("nan"),
            sum(1 for r in sel if not math.isfinite(r[col])),
            sum(1 for r in sel if r.get(col + "_parted") in (1.0, True)))


BASE = sys.argv[3] if len(sys.argv) > 3 else "current"


def main():
    base, new = rows(sys.argv[1]), rows(sys.argv[2])
    alts = sorted({k[1] for k in new}, key=lambda a: (a != "clean", a))
    print("%-18s %-5s | base max  med ref part | new max  med ref part | share max  gate max" % ("alteration", "sp"))
    for alt in alts:
        for sp in ("thin", "thick"):
            b = [r for k, r in base.items() if k[1] == alt and r["spacing"] == sp]
            n = [r for k, r in new.items() if k[1] == alt and r["spacing"] == sp]
            bs, ns = stats(b, BASE), stats(n, "current")
            sh = [r.get("current_dropped_share", float("nan")) for r in n]
            gt = [r.get("current_gate_off_mm", float("nan")) for r in n]
            print("%-18s %-5s | %6.2f %5.2f %3d %3d | %6.2f %5.2f %3d %3d | %5.2f %8.2f" % (
                alt, sp, bs[0], bs[1], bs[2], bs[3], ns[0], ns[1], ns[2], ns[3],
                max([x for x in sh if math.isfinite(x)], default=float("nan")),
                max([x for x in gt if math.isfinite(x)], default=float("nan"))))


if __name__ == "__main__":
    main()

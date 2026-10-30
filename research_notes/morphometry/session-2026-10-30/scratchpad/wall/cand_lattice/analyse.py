"""Per config: candidate A's error, the range the lattice leaves free on its edges, whether the
truth lies in it, and the downstream errors against those with the true wall (the floor)."""
import json, math, os, pickle, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import score as S

rows = json.load(open(sys.argv[1]))
cache = sys.argv[2]
out = []
for r in rows:
    i = r["info"]
    lo, hi = float(i.get("free_lo_deg", "nan")), float(i.get("free_hi_deg", "nan"))
    t = r["wall_truth_frame"]
    rec = pickle.load(open(os.path.join(cache, r["key"] + ".pkl"), "rb"))
    floor = S.downstream(rec, t)
    out.append((r, lo, hi, floor))
for sp in ("thin", "thick"):
    sel = [o for o in out if o[0]["spacing"] == sp]
    w = np.array([o[2] - o[1] for o in sel])
    fin = np.isfinite(w)
    inside = sum(1 for o in sel if np.isfinite(o[1]) and o[1] - 1e-6 <= o[0]["wall_truth_frame"] <= o[2] + 1e-6)
    fitted_out = sum(1 for o in sel if np.isfinite(o[1]) and not (o[1] <= float(o[0]["info"]["fitted_deg"]) <= o[2]))
    print("%s: range found %d/%d; width min %.2f median %.2f max %.2f; truth inside %d; least-squares slope outside the range %d" % (
        sp, fin.sum(), len(sel), np.nanmin(w), np.nanmedian(w), np.nanmax(w), inside, fitted_out))
    half_ok = sum(1 for o, ww in zip(sel, w) if abs(o[0]["wall_err"]) <= 0.5 * ww + 1e-9)
    print("   error within half the range's width in %d of %d" % (half_ok, len(sel)))
    for key in ("sag_right", "sag_left", "endplate_incl", "endplate_lower_incl", "spinous"):
        c = [abs(o[0]["down"].get(key, float("nan"))) for o in sel]
        f = [abs(o[3].get(key, float("nan"))) for o in sel]
        n = [abs(x) for x in c if np.isfinite(x)]
        if n:
            print("   %-20s max %.2f median %.2f (true wall: max %.2f median %.2f) over %d" % (
                key, np.nanmax(c), np.nanmedian(c), np.nanmax(f), np.nanmedian(f), len(n)))
print()
print("%-40s %7s %7s %7s %7s %7s" % ("config", "err", "lo", "hi", "width", "edges"))
for o in sorted(out, key=lambda o: -abs(o[0]["wall_err"]))[:14]:
    r = o[0]
    print("%-40s %+7.2f %+7.2f %+7.2f %7.2f %7s" % (r["key"], r["wall_err"], o[1] - r["wall_truth_frame"], o[2] - r["wall_truth_frame"], o[2] - o[1], r["info"].get("edges")))

"""Print the scored rows sorted by |error|, with the parting's range and margin."""
import json, sys, math
rows = json.load(open(sys.argv[1]))
rows.sort(key=lambda r: -abs(r["wall_err"]) if math.isfinite(r["wall_err"]) else 1e9)
for r in rows[: int(sys.argv[2]) if len(sys.argv) > 2 else len(rows)]:
    i = r["info"]
    t = r["wall_truth_frame"]
    lo, hi = i.get("lo_deg", float("nan")), i.get("hi_deg", float("nan"))
    inside = lo - 1e-6 <= t <= hi + 1e-6 if isinstance(lo, float) else None
    print("%-36s err %+5.2f now %+5.2f width %5.2f [%+6.2f %+6.2f] truth %+6.2f in %s margin %.3f across %s %s" % (
        r["key"], r["wall_err"], r["now_err"], i.get("width_deg", float("nan")), lo, hi, t, inside,
        i.get("margin_mm", float("nan")), i.get("across"), i.get("why", "")))

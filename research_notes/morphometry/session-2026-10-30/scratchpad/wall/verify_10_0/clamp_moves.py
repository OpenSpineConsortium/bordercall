"""How far the clamp would have moved each wall reading of the noclamp run: the fitted slope
clamped into the parted range, less the fitted slope, in degrees."""
import json
import sys

rows = json.load(open(sys.argv[1]))["readings"]
moves = []
for r in rows:
    if r.get("parted") and r.get("fitted_deg") is not None:
        clamped = min(max(r["fitted_deg"], r["free_lo_deg"]), r["free_hi_deg"])
        moves.append((abs(clamped - r["fitted_deg"]), r["level"], r["fitted_deg"], clamped))
moved = [m for m in moves if m[0] > 1e-9]
print("%d readings, %d parted, %d moved by the clamp, largest %.3f" % (len(rows), len(moves), len(moved),
      max(m[0] for m in moved)))
for m in sorted(moved, reverse=True):
    print("  %s fitted %.3f clamped %.3f moved %.3f" % (m[1], m[2], m[3], m[0]))

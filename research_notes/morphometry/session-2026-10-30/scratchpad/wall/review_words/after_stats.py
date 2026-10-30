"""Counts from the implementer's score_after.json: parted, freedom over the flag, error against
half the freedom, per spacing."""
import json
import math
import sys

rows = json.load(open(sys.argv[1]))
for sp in ("thin", "thick"):
    sel = [r for r in rows if r["spacing"] == sp]
    parted = sum(1 for r in sel if r["info"].get("parted") in (1.0, "True", True))
    over3 = [(r["key"], r["info"].get("free_deg")) for r in sel if float(r["info"].get("free_deg", "nan")) > 3.0]
    half = [(r["key"], round(r["wall_err"], 2), round(float(r["info"]["free_deg"]), 2)) for r in sel
            if abs(r["wall_err"]) > 0.5 * float(r["info"]["free_deg"])]
    full = [(r["key"], round(r["wall_err"], 2), round(float(r["info"]["free_deg"]), 2)) for r in sel
            if abs(r["wall_err"]) > float(r["info"]["free_deg"])]
    print(sp, "n", len(sel), "parted", parted, "free>3", len(over3), over3)
    print("  err > free/2:", len(half), half)
    print("  err > free:", len(full), full)
    print("  info keys", sorted(sel[0]["info"]))

"""Over the implementer's alteration rows: how often the wall's error passes half its freedom,
and the freedom itself, and what the flagged readings (freedom over 3 degrees) err."""
import json
import math
import sys

rows = [r for p in sys.argv[1:] for r in json.load(open(p))]
for sp in ("thin", "thick"):
    for alt in sorted({r["alt"] for r in rows}):
        sel = [r for r in rows if r["alt"] == alt and r["spacing"] == sp and math.isfinite(r["current"])
               and math.isfinite(r.get("proposed_free_deg", math.nan))]
        half = [r for r in sel if abs(r["current"]) > 0.5 * r["proposed_free_deg"]]
        full = [r for r in sel if abs(r["current"]) > r["proposed_free_deg"]]
        flagged = [r for r in sel if r["proposed_free_deg"] > 3.0]
        fl_half = [r for r in flagged if abs(r["current"]) > 0.5 * r["proposed_free_deg"]]
        print("%-6s %-18s n %2d  err>free/2 %2d  err>free %2d  flagged %2d (err>free/2 %d)%s" % (
            sp, alt, len(sel), len(half), len(full), len(flagged), len(fl_half),
            "  e.g. " + ", ".join("%s %+.2f free %.2f" % (r["key"], r["current"], r["proposed_free_deg"]) for r in fl_half[:2]) if fl_half else ""))

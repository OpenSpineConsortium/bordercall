"""Tables over canal_line.json and coupling.json: per spacing and grid, the largest error of the
canal line, of the canal line read on raw outermost centres (no edge_gap half-step), of
body.posterior_wall_slope on the cut body and on the uncut voxels; the leaned walls' ratio of the
canal line's lean to the truth; the correlation of the canal line's error with the share of the
posterior reader's error the cut adds; rings far off the wall.

  summary.py
"""
import json
import math

import numpy as np

c = {r["key"]: r for r in json.load(open("canal_line.json"))}
k = {r["key"]: r for r in json.load(open("coupling.json"))}
keys = sorted(c)
for sp in ("thin", "thick"):
    print("== %s" % sp)
    print("   grid     | canal  raw-canal | post cut  post uncut | n")
    for g in ("aligned", "x2", "x5", "x10", "y12", "suite18", "t25", "all"):
        sel = [x for x in keys if c[x]["spacing"] == sp and (g == "all" or c[x]["grid"] == g)]
        m = lambda f, src=c: max(abs(src[x][f]) for x in sel)  # noqa: E731
        raw = max(abs(c[x]["canal_raw_deg"] - c[x]["truth"]) for x in sel)
        print("   %-8s | %5.2f  %5.2f     | %5.2f     %5.2f     | %d" % (
            g, m("canal_err"), raw, m("post_cut_err", k), m("post_uncut_err", k), len(sel)))
print("== leaned walls, canal line's lean over the truth (thin / thick)")
for ph, lean in (("straight", 5.0), ("straight", -5.0), ("shapes", 4.0)):
    row = []
    for g in ("aligned", "x2", "x5", "x10", "y12", "suite18", "t25"):
        got = []
        for sp in ("thin", "thick"):
            key = "%s_lean%+.0f_%s_%s" % (ph, lean, g, sp)
            got.append(c[key]["canal_deg"] / c[key]["truth"])
        row.append("%s %.2f/%.2f" % (g, got[0], got[1]))
    print("   %s lean %+.0f: %s" % (ph, lean, "  ".join(row)))
ce = np.array([c[x]["canal_err"] for x in keys])
leak = np.array([k[x]["post_cut_err"] - k[x]["post_uncut_err"] for x in keys])
cut = np.array([k[x]["bins_on_cut"] > 0 for x in keys])
print("== correlation of the canal line's error with the cut's share of the posterior error: all %.2f, "
      "where a bin is set by the cut %.2f (n %d)" % (np.corrcoef(ce, leak)[0, 1], np.corrcoef(ce[cut], leak[cut])[0, 1],
                                                    cut.sum()))
print("   sign agreement where a bin is set by the cut and |leak| > 0.3: %d of %d" % (
    sum(np.sign(a) == np.sign(b) for a, b in zip(ce[cut], leak[cut]) if abs(b) > 0.3),
    sum(abs(b) > 0.3 for b in leak[cut])))
gap = [abs(c[x]["canal_err"] - (c[x]["canal_raw_deg"] - c[x]["truth"])) for x in keys]
print("== edge_gap's half-step changes the canal line by more than 0.3 degrees in %d of %d configs (max %.2f), "
      "on aligned grids in %d" % (sum(g > 0.3 for g in gap), len(gap), max(gap),
                                  sum(g > 0.3 for g, x in zip(gap, keys) if c[x]["grid"] == "aligned")))
far = [(x, z, e) for x in keys for z, e in zip(c[x]["ring_z"], c[x]["ring_excess"]) if abs(e) > 3.0]
print("== rings whose anterior wall lies more than 3 mm off the wall: %d, in %d configs, all %s" % (
    len(far), len({f[0] for f in far}), sorted({c[f[0]]["phantom"] for f in far})))
for x, z, e in far[:30]:
    print("   %-36s z %+5.1f excess %+6.2f" % (x, z, e))
print("== canal line exactly 0.0 (indistinguishable from wall_slope's refusal value): %s" % (
    [x for x in keys if c[x]["canal_deg"] == 0.0]))
print("== ring span (mm) thin min %.1f max %.1f; thick min %.1f max %.1f; posterior window (mm) thin %.1f-%.1f thick %.1f-%.1f" % (
    min(c[x]["ring_span"] for x in keys if c[x]["spacing"] == "thin"), max(c[x]["ring_span"] for x in keys if c[x]["spacing"] == "thin"),
    min(c[x]["ring_span"] for x in keys if c[x]["spacing"] == "thick"), max(c[x]["ring_span"] for x in keys if c[x]["spacing"] == "thick"),
    min(c[x]["post_window"] for x in keys if c[x]["spacing"] == "thin"), max(c[x]["post_window"] for x in keys if c[x]["spacing"] == "thin"),
    min(c[x]["post_window"] for x in keys if c[x]["spacing"] == "thick"), max(c[x]["post_window"] for x in keys if c[x]["spacing"] == "thick")))
print("== rings thick: %s" % sorted({c[x]["rings"] for x in keys if c[x]["spacing"] == "thick"}))

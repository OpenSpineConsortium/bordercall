"""The canal readings a median line is drawn from: each section's width and depth in the band,
the median, the section the line is drawn in, and the band's first section, on the straight
phantom and on walls leaned 5 degrees each way."""
import sys
import numpy as np
from maskedge import edge as E
from morphometry import measure as M
from morphometry.tests import phantom as P
from morphoview import lines as LN
from scanimport import geometry as G

LEVELS = ["L2", "L3", "L4"]
for name, vert in (("straight", P.Vert()), ("lean +5", P.Vert(lean=5.0)), ("lean -5", P.Vert(lean=-5.0)),
                   ("lam_slope 35", P.Vert(lam_slope=35.0))):
    placed = {p.level: p for p in P.straight(LEVELS, vert)}
    lab, aff = P.draw(list(placed.values()), spacing=(0.8, 0.8, 1.0))
    vs = E.vertebrae(lab, G.VoxelGrid(aff, lab.shape), {P.LEVEL_IDS[lv]: lv for lv in LEVELS})
    v = vs["L3"]
    vals, _, ped = M.vertebra_values(v)
    secs, band, canal = LN.canal_reading(v)
    rows = [(s, G.canal_walls(s, v.pixel, v.fx, v.fy)) for s in secs if s.canal is not None and band[0] <= s.w <= band[1]]
    rows = [(s, r) for s, r in rows if r is not None]
    w = [r[0] for _, r in rows]; d = [r[1] for _, r in rows]
    lines = {ln.key: ln for ln in LN.checked(LN.panjabi_canal(v), vals)}
    print(name, "sections", len(rows), "band %.1f to %.1f" % band)
    print("  width: median %.4f rows %.3f..%.3f first %.4f drawn %.4f (%s)" % (canal["canal_w"], min(w), max(w), w[0], lines["canal_w"].drawn, lines["canal_w"].status))
    print("  depth: median %.4f rows %.3f..%.3f first %.4f drawn %.4f (%s)" % (canal["canal_ap"], min(d), max(d), d[0], lines["canal_ap"].drawn, lines["canal_ap"].status))
    print("  depths", " ".join("%.2f" % x for x in d))

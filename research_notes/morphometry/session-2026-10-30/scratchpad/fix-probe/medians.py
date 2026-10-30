"""How far each median line's drawn length lies from its value, on the straight phantom's L3 and
its discs, and on the leaned and steep-lamina variants."""
import numpy as np
from maskedge import edge as E
from morphometry import column as COL
from morphometry import measure as M
from morphometry.tests import phantom as P
from morphoview import lines as LN
from scanimport import geometry as G

LEVELS = ["L2", "L3", "L4"]
for name, vert in (("straight", P.Vert()), ("lean +5", P.Vert(lean=5.0)), ("lam_slope 35", P.Vert(lam_slope=35.0))):
    placed = {p.level: p for p in P.straight(LEVELS, vert)}
    lab, aff = P.draw(list(placed.values()), spacing=(0.8, 0.8, 1.0))
    vs = E.vertebrae(lab, G.VoxelGrid(aff, lab.shape), {P.LEVEL_IDS[lv]: lv for lv in LEVELS})
    v = vs["L3"]
    vals, _, ped = M.vertebra_values(v)
    lines = LN.checked(LN.vertebra_lines(v, ped, vals), vals)
    for up, low in (("L2", "L3"), ("L3", "L4")):
        lines += LN.checked(LN.discs(vs[up], vs[low]), COL.disc_heights(vs[up], vs[low]))
    print(name, " ".join("%s:%.3f" % (ln.key, ln.drawn - ln.value) for ln in lines if ln.rule == "median"))
    print("   rules", sorted({ln.rule for ln in lines}))

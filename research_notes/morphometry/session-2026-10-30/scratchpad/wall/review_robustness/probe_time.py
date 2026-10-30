"""How often measure_volume reads the wall afresh per vertebra, and what share of its time that
takes, on the suite's straight lumbar phantom at 0.8 by 0.8 by 1 mm."""
import time

from morphometry import body as BODY, measure as M
from morphometry.tests import phantom as P
from scanimport import geometry as G

LUMBAR = ["L2", "L3", "L4"]
calls, spent = [], [0.0]
real = BODY.read_wall


def counted(v, B, xc):
    t0 = time.perf_counter()
    out = real(v, B, xc)
    spent[0] += time.perf_counter() - t0
    calls.append(v.level)
    return out


BODY.read_wall = counted
placed = P.straight(LUMBAR, P.lumbar())
lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), grid_turn=((0.0, 0.0, 1.0), 7.0))
t0 = time.perf_counter()
rows = M.measure_volume(lab, G.VoxelGrid(aff, lab.shape), {P.LEVEL_IDS[lv]: lv for lv in LUMBAR}, "t", pelvis=False)
total = time.perf_counter() - t0
print("read_wall calls per level:", {lv: calls.count(lv) for lv in LUMBAR})
print("measure_volume %.1f s, of which read_wall %.3f s" % (total, spent[0]))

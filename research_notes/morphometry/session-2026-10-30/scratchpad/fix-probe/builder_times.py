import time
from morphometry import measure as M
from morphometry.tests import phantom as P
from morphoview import lines as LN
from scanimport import geometry as G
L = ["L1", "L2", "L3", "L4", "L5"]
lab, aff = P.draw(P.straight(L, P.Vert()), spacing=(0.8, 0.8, 1.0))
kept = {}
t0 = time.time()
M.measure_volume(lab, G.VoxelGrid(aff, lab.shape), {P.LEVEL_IDS[lv]: lv for lv in L}, "x", pelvis=False, keep=kept)
meas = time.time() - t0
tot = {}
for lv, v in kept["verts"].items():
    for name, draw in LN.vertebra_builders(v, kept["peds"][lv], kept["values"][lv]):
        t = time.time(); draw(); tot[name] = tot.get(name, 0) + time.time() - t
print("measure %.2f s; drawing %.2f s (%.1f%%)" % (meas, sum(tot.values()), 100 * sum(tot.values()) / meas))
for k, s in sorted(tot.items(), key=lambda kv: -kv[1]):
    print("  %-16s %.3f s" % (k, s))

"""The drawing's time with the measure's own pedicle reading and with pedicle.one_side read again,
on the export test's phantom (L2 to L4 at 0.8 by 0.8 by 1 mm) and on L1 to L5."""
import time
from morphometry import measure as M
from morphometry.tests import phantom as P
from morphoview import lines as LN
from scanimport import geometry as G

for levels in (["L2", "L3", "L4"], ["L1", "L2", "L3", "L4", "L5"]):
    lab, aff = P.draw(P.straight(levels, P.Vert()), spacing=(0.8, 0.8, 1.0))
    kept = {}
    t0 = time.process_time()
    M.measure_volume(lab, G.VoxelGrid(aff, lab.shape), {P.LEVEL_IDS[lv]: lv for lv in levels}, "x", pelvis=False, keep=kept)
    measuring = time.process_time() - t0
    for rep in range(2):
        took = {}
        for mode in ("reused", "again"):
            t = time.process_time()
            for lv, v in kept["verts"].items():
                vals = kept["values"][lv] if mode == "reused" else None
                for name, draw in LN.vertebra_builders(v, kept["peds"][lv], vals):
                    draw()
            took[mode] = time.process_time() - t
        print("%s to %s rep %d: measuring %.2f s cpu; drawing %.2f s reused, %.2f s read again; reading again is %.0f%% of that drawing; reused drawing %.1f%% of the measuring"
              % (levels[0], levels[-1], rep, measuring, took["reused"], took["again"],
                 100 * (took["again"] - took["reused"]) / took["again"], 100 * took["reused"] / measuring), flush=True)

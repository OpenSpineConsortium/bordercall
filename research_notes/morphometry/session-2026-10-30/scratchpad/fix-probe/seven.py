"""Draw every line on a few phantoms with the worktree's code and report the seven chords' status."""
import sys, time
import numpy as np
from morphometry import measure as M
from morphometry.tests import phantom as P
from morphoview import lines as LN
from scanimport import geometry as G
from scanimport import SEVEN

def column(kind):
    if kind == "straight":
        return P.straight(["L2", "L3", "L4"], P.Vert()), (0.8, 0.8, 1.0)
    if kind == "thick":
        return P.straight(["L2", "L3", "L4"], P.Vert()), (0.86, 0.86, 2.5)
    if kind == "joints":
        j = P.Joint(gap=10.0, sagittal=8.0, coronal=4.0, axial=5.0, slip=4.0)
        L = ["L2", "L3", "L4"]
        return P.chain(L, {lv: P.Vert() for lv in L}, {lv: j for lv in L[1:]}, R0=P.rotation((1.0, 0.3, 0.0), 12.0)), (0.8, 0.8, 1.0)

for kind in sys.argv[1:]:
    placed, sp = column(kind)
    lab, aff = P.draw(placed, spacing=sp, strict=False)
    kept = {}
    t0 = time.time()
    M.measure_volume(lab, G.VoxelGrid(aff, lab.shape), {P.LEVEL_IDS[p.level]: p.level for p in placed}, "x", pelvis=False, keep=kept)
    t1 = time.time()
    for lv, v in kept["verts"].items():
        vals = kept["values"][lv]
        lines = LN.checked(LN.vertebra_lines(v, kept["peds"][lv], vals), vals)
        st = {ln.key: ln.status for ln in lines}
        miss = [k for k in SEVEN if st.get(k) != "drawn"]
        bad = [(ln.key, ln.status) for ln in lines if ln.status != "drawn"]
        new = {ln.key: (round(ln.value, 4), round(ln.drawn, 4)) for ln in lines if ln.key in ("h_post", "canal_w", "canal_ap")}
        print(kind, lv, "lines", len(lines), "SEVEN not drawn:", miss, "not drawn:", bad[:4], new)
    print(kind, "measure %.1f s, draw %.1f s" % (t1 - t0, time.time() - t1))

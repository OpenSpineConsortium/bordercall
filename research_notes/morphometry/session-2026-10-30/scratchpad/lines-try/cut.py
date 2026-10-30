import collections
from morphometry.tests import phantom as P
from morphometry.tests import test_lines_export as T
from morphometry import measure as M, __main__ as RUN
from scanimport import geometry as G
lab, aff = P.draw(P.straight(T.LEVELS, P.Vert()), spacing=(0.8, 0.8, 1.0))
cl, ca = T.cut_below(lab, aff, "L4")
print(lab.shape, cl.shape)
kept = {}
rows = M.measure_volume(cl, G.VoxelGrid(ca, cl.shape), {P.LEVEL_IDS[l]: l for l in T.LEVELS}, "0002", pelvis=False, keep=kept)
print({k: len(v) for k, v in kept.items()})
lines, frames, flags = RUN.study_lines("0002", kept)
print(collections.Counter((r["level"], r["status"][:12]) for r in lines if r["part"] == ""))
print([(r["key"], r["value"], r["note"][:60]) for r in rows if r["level"] == "L4" and r["key"] in ("h_ant", "h_mid", "body_d_mid", "flag:cut", "flag:all", "flag:body")])

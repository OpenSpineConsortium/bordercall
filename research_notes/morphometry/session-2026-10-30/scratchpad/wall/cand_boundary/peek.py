"""Look at the lattice step nearest the frame's y and the loc/idx agreement on a few cached L3s."""
import pickle, sys, os, math
import numpy as np
cache = "../cache"
for f in sorted(os.listdir(cache))[:: 9]:
    rec = pickle.load(open(os.path.join(cache, f), "rb"))
    v = rec["vert"]
    A = np.asarray(v.grid.affine, float)[:3, :3]
    F = np.stack([v.frame.ex, v.frame.ey, v.frame.ez])
    Af = F @ A
    cosy = np.abs(Af[1]) / np.linalg.norm(Af, axis=0)
    i = int(np.argmax(cosy))
    loc2 = v.frame.local(v.grid.world(v.idx.astype(float)))
    rings = v.full_rings()
    ap = np.median([s.ap for s in rings]) if rings else float("nan")
    print("%-40s axis %d off-y %.2f deg step %s ap %.1f locdiff %.1e wall_slope %.3f" % (
        f, i, math.degrees(math.acos(min(1, cosy[i]))), np.round(Af[:, i], 3), ap, np.abs(loc2 - v.loc).max(), v.wall_slope))

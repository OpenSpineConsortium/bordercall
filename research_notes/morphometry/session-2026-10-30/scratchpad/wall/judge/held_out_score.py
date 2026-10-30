"""A, A_lts and A_lts_plain on candidate A's held-out phantoms (cand_lattice/heldout), against the
frame-relative truth, with the downstream angles as score.py takes them."""
import math, os, pickle, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
WALL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(WALL, "cand_lattice")); sys.path.insert(0, WALL); sys.path.insert(0, HERE)
import held_out  # noqa: F401  registers the overhang phantom
import score as S
import cand as C
import variants as V
deg = lambda t: math.degrees(math.atan(t)) if np.isfinite(t) else float("nan")
d = os.path.join(WALL, "cand_lattice", "heldout")
for f in sorted(os.listdir(d)):
    if not f.endswith(".pkl"):
        continue
    rec = pickle.load(open(os.path.join(d, f), "rb"))
    v = rec["vert"]; B = v.body_pts
    t = S.wall_truth_in_frame(rec)
    out = {}
    import proposed as PR
    for name, fn in (("A", C.slope), ("A_lts", PR.posterior_wall), ("A_lts_plain", V.A_lts_plain)):
        b, info = fn(v, B, rec["xc"])
        out[name] = deg(b) - t
        if name == "A_lts":
            dn = S.downstream(rec, deg(b)); sf = float(info.get("free_deg", float("nan")))
    print("%-40s now %+6.2f  A %+6.2f  A_lts %+6.2f  plain %+6.2f  synth_free %.2f | A_lts downstream %s" % (
        f[:-4], rec["raw"]["wall_now"] - t, out["A"], out["A_lts"], out["A_lts_plain"], sf,
        " ".join("%s %+.2f" % (k, x) for k, x in dn.items() if np.isfinite(x))))

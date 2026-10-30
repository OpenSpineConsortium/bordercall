"""Candidate A and the current reader on ragged labels: each cached L3 with a share of its
surface voxels flipped at random (bone with an air face-neighbour dropped, air with a bone
face-neighbour added, each with probability p), as a segmenter's edge is ragged where the
phantom's is an exact digitisation. The slabs, the frame and the canal's line are kept from
the clean label, so only the wall reader sees the noise; an added voxel against
the body is the body's, so the current reader, which reads the body, sees the noise too.  noise.py <cache> <p> <seed>"""
import copy, math, os, pickle, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import score as S
import cand as C
from morphometry import body as BODY

FACES = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]])


def ragged(v, p, rng):
    box, lo = v.mask_box()
    pad = np.pad(box, 1)
    air_near = np.zeros_like(pad); bone_near = np.zeros_like(pad)
    for f in FACES:
        sh = np.roll(pad, tuple(f), axis=(0, 1, 2))
        air_near |= ~sh; bone_near |= sh
    surface = pad & air_near
    shell = ~pad & bone_near
    drop = surface & (rng.random(pad.shape) < p)
    add = shell & (rng.random(pad.shape) < p)
    new = (pad & ~drop) | add
    idx = np.argwhere(new) - 1 + lo
    w = copy.copy(v)
    w._box = None
    w.idx = idx
    w.loc = v.frame.local(v.grid.world(idx.astype(float)))
    body = np.zeros_like(pad)
    body[tuple((v.idx[v.body] - lo + 1).T)] = True
    near_body = np.zeros_like(pad)
    for f in FACES:
        near_body |= np.roll(body, tuple(f), axis=(0, 1, 2))
    w.body = (body | (add & near_body))[tuple((idx - lo + 1).T)]
    return w


def main():
    cache, p, seed = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
    rng = np.random.default_rng(seed)
    deg = lambda t: math.degrees(math.atan(t)) if np.isfinite(t) else float("nan")
    rows = []
    for f in sorted(os.listdir(cache)):
        if not f.endswith(".pkl"):
            continue
        rec = pickle.load(open(os.path.join(cache, f), "rb"))
        w = ragged(rec["vert"], p, rng)
        B = w.body_pts
        t = S.wall_truth_in_frame(rec)
        a, info = C.slope(w, B, rec["xc"])
        q, _ = C.slope_plain(w, B, rec["xc"])
        n = BODY.posterior_wall_slope(w, B, rec["xc"])
        feasible = not math.isnan(float(info.get("free_lo_deg", float("nan"))))
        rows.append((f[:-4], rec["cfg"][5], deg(n) - t, deg(a) - t, deg(q) - t, feasible))
    for sp in ("thin", "thick"):
        s = [r for r in rows if r[1] == sp]
        for name, i in (("current", 2), ("candidate", 3), ("candidate, no clamp", 4)):
            e = np.abs([r[i] for r in s])
            print("p %.2f %-5s %-20s max %.2f median %.2f mean %.2f (%d read)" % (p, sp, name, np.nanmax(e), np.nanmedian(e), np.nanmean(e), np.isfinite(e).sum()))
        print("p %.2f %-5s the lattice's range found (a surface parts the edges) in %d of %d" % (p, sp, sum(r[5] for r in s), len(s)))


if __name__ == "__main__":
    main()

"""The least-crossing path and the refusals on phantom masks altered by hand: a midline notch cut
into the posterior wall, a bone speck in the canal behind it, and a lip of bone standing back
from the wall at one end of the window. The true wall plane (diag_limit/limit.truth_plane)
places each alteration; the reading is scored against the frame-relative truth as score.py does.
Phantoms only: these are not real masks."""
import copy, importlib.util, math, os, pickle, sys
import numpy as np
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(here)); sys.path.insert(0, os.path.join(os.path.dirname(here), "diag_limit"))
import score as S  # noqa: E402
import limit as L  # noqa: E402
spec = importlib.util.spec_from_file_location("cand", os.path.join(here, "cand.py"))
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)


def altered(rec, change):
    v = copy.copy(rec["vert"])
    box, lo = v.mask_box()
    box = box.copy()
    ijk = np.argwhere(np.ones(box.shape, bool)) + lo
    q = v.frame.local(v.grid.world(ijk.astype(float)))
    tp = L.truth_plane(rec)
    behind = q[:, 1] - (tp["a"] + tp["b"] * q[:, 2] + tp["c"] * q[:, 0])   # + in front of the wall
    B = v.body_pts
    strip = B[np.abs(B[:, 0] - rec["xc"]) <= 3.0]
    zm = 0.5 * (strip[:, 2].min() + strip[:, 2].max())
    win = 0.3 * (strip[:, 2].max() - strip[:, 2].min())          # half the middle 60 per cent
    dx, dz = q[:, 0] - rec["xc"], q[:, 2] - zm
    sel, val = change(dx, dz, behind, win)
    box[tuple((ijk[sel] - lo).T)] = val
    v._box = (box, lo)
    return v, body_after(rec["vert"], ijk[sel], q[sel], val)


def body_after(v, changed_ijk, changed_q, val):
    """The cut body B with the alteration: removed voxels dropped; added voxels kept where they lie
    in front of the cut (the canal's wall line), as body_in_front would keep them."""
    from morphometry import anatomy as A
    B = v.body_pts
    if not val:
        gone = {tuple(t) for t in changed_ijk}
        keep = np.array([tuple(t) not in gone for t in v.idx[v.body]])
        return B[keep]
    front = A.square_to_wall(v, changed_q)[:, 1] > v.wall_y0
    return np.vstack([B, changed_q[front]])


CHANGES = {
    "notch 6x4 mm, 1 mm deep": lambda dx, dz, w, h: ((np.abs(dx) <= 3) & (np.abs(dz) <= 2) & (w >= 0) & (w <= 1.0), False),
    "notch 6x4 mm, 2 mm deep": lambda dx, dz, w, h: ((np.abs(dx) <= 3) & (np.abs(dz) <= 2) & (w >= 0) & (w <= 2.0), False),
    "notch 4x6 mm, 3 mm deep": lambda dx, dz, w, h: ((np.abs(dx) <= 2) & (np.abs(dz) <= 3) & (w >= 0) & (w <= 3.0), False),
    "notch at the window's top, 6x3 mm, 2 mm deep": lambda dx, dz, w, h: ((np.abs(dx) <= 3) & (np.abs(dz - (h - 1.5)) <= 1.5) & (w >= 0) & (w <= 2.0), False),
    "speck 2 mm behind": lambda dx, dz, w, h: ((np.abs(dx) <= 0.5) & (np.abs(dz) <= 0.6) & (w <= -1.6) & (w >= -2.4), True),
    "lip 1 mm back over the window's top 3 mm": lambda dx, dz, w, h: ((np.abs(dx) <= 3) & (dz >= h - 3) & (dz <= h) & (w < 0) & (w >= -1.0), True),
    "lip 2 mm back over the window's top 3 mm": lambda dx, dz, w, h: ((np.abs(dx) <= 3) & (dz >= h - 3) & (dz <= h) & (w < 0) & (w >= -2.0), True),
}
def bend(sag, concave):
    """The wall bowed along z over the window, its ends on the true plane and its middle sag mm
    forward (concave, bone taken away) or back (convex, bone added); the chord keeps the slope."""
    def change(dx, dz, w, h):
        bow = sag * np.clip(1.0 - (dz / h) ** 2, 0.0, None)
        inside = (np.abs(dx) <= 4.0) & (np.abs(dz) <= h)
        if concave:
            return inside & (w >= 0) & (w < bow), False
        return inside & (w < 0) & (w >= -bow), True
    return change


for _sag in (0.4, 0.8):
    CHANGES["concave bow %.1f mm" % _sag] = bend(_sag, True)
    CHANGES["convex bow %.1f mm" % _sag] = bend(_sag, False)

KEYS = ["straight_lean+0_x5_thin", "straight_lean+5_x2_thin", "pitched_lean+0_suite18_thin",
        "straight_lean+0_x2_thick", "straight_lean+5_y12_thick"]

for key in KEYS:
    rec = pickle.load(open(os.path.join(os.path.dirname(here), "cache", key + ".pkl"), "rb"))
    t = S.wall_truth_in_frame(rec)
    v = rec["vert"]
    from morphometry import body as BODY
    b, info = C.slope(v, v.body_pts, rec["xc"])
    now = math.degrees(math.atan(BODY.posterior_wall_slope(v, v.body_pts, rec["xc"]))) - t
    print("%s: unaltered err %+.2f width %.2f (current reader %+.2f)" % (key, math.degrees(math.atan(b)) - t, info["width_deg"], now))
    for name, change in CHANGES.items():
        va, Ba = altered(rec, change)
        b, info = C.slope(va, Ba, rec["xc"])
        now = math.degrees(math.atan(BODY.posterior_wall_slope(va, Ba, rec["xc"]))) - t
        err = math.degrees(math.atan(b)) - t if math.isfinite(b) else float("nan")
        print("   %-46s err %+6.2f (current %+6.2f) across %4s of %4s near, worst %.2f mm, width %5.2f %s" % (
            name, err, now, info.get("across"), info.get("near"), info.get("worst_mm", float("nan")),
            info.get("width_deg", float("nan")), ("REFUSED: " + info["why"]) if "why" in info else ""))

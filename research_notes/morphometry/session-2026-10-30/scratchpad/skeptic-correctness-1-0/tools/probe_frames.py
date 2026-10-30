"""On the RunWithLines phantom (and a zigzag one whose L3 leans against its column's line), how
the frame the export writes sits against the phantom's own axes and the label's centroid, and
which checks tell each mutant of the written frame from the real one: the two frame tests of
test_lines_export as they stand, the reviewer's proposed checks, and signed and exact ones.

Run from a copy of the repository at the commit under review."""
import math
import sys

import numpy as np

from morphometry import measure as M
from morphometry.tests import phantom as P
from morphoview import lines as LN
from scanimport import geometry as G

LEVELS = ["L2", "L3", "L4"]
SHARE_MM = 2e-3          # what the 4-place rounding of ends and axes leaves of a shared coordinate


def r4(x):
    return np.round(np.asarray(x, float), 4)


def deg(a, b):
    return math.degrees(math.acos(min(1.0, abs(float(np.dot(a, b)) / np.linalg.norm(a) / np.linalg.norm(b)))))


def mutants(v):
    f = v.frame
    c, s = math.cos(math.radians(5.0)), math.sin(math.radians(5.0))
    col = v.column_ez if v.column_ez is not None else f.ez
    return {
        "real": f,
        "m1 column line": G.frame_from(f.origin, col, v.grid.anterior()),
        "m2 5 deg about x": G.Frame(f.origin, f.ex, c * f.ey + s * f.ez, -s * f.ey + c * f.ez),
        "m7 origin 0": G.Frame(np.zeros(3), f.ex, f.ey, f.ez),
        "m8 -x -y": G.Frame(f.origin, -f.ex, -f.ey, f.ez),
        "m12 -x -z": G.Frame(f.origin, -f.ex, f.ey, -f.ez),
        "m9 origin +15y": G.Frame(f.origin + 15.0 * f.ey, f.ex, f.ey, f.ez),
    }


def rounded(fr):
    return G.Frame(r4(fr.origin), r4(fr.ex), r4(fr.ey), r4(fr.ez))


def ends(ln):
    return r4(ln.a), r4(ln.b)


def old_tests(fr, L):
    """test_each_measured_vertebra_has_a_right_handed_frame and
    test_a_height_runs_up_its_frame_and_a_width_across_it, as written."""
    R = np.stack([fr.ex, fr.ey, fr.ez])
    ok1 = np.allclose(R @ R.T, np.eye(3), atol=4e-4) and abs(float(np.linalg.det(R)) - 1.0) <= 4e-4
    ok2 = True
    for key, axis in (("h_mid", "ez"), ("body_w_mid", "ex"), ("body_d_mid", "ey")):
        a, b = ends(L[key])
        d = b - a
        ok2 = ok2 and abs(float(d @ getattr(fr, axis))) / np.linalg.norm(d) > 0.99
    return ok1, ok2


def local(fr, p):
    return fr.local(p[None, :])[0]


def reviewer_checks(fr, L, centroid):
    """The proposed fix: h_mid's ends share local x, body_w_mid's share local y and z, the body
    at positive local y, the origin the label's voxel centroid."""
    ha, hb = (local(fr, p) for p in ends(L["h_mid"]))
    wa, wb = (local(fr, p) for p in ends(L["body_w_mid"]))
    da, db = (local(fr, p) for p in ends(L["body_d_mid"]))
    return (abs(ha[0] - hb[0]) <= SHARE_MM and abs(wa[1] - wb[1]) <= SHARE_MM and abs(wa[2] - wb[2]) <= SHARE_MM
            and 0.5 * (da[1] + db[1]) > 0 and np.linalg.norm(fr.origin - centroid) <= 1e-3)


def more_checks(fr, L):
    """What the proposal leaves out: body_d_mid's ends share local x and z, and each line runs
    along the sign of its axis (h_mid up z, body_w_mid along x, body_d_mid along y)."""
    da, db = (local(fr, p) for p in ends(L["body_d_mid"]))
    share = abs(da[0] - db[0]) <= SHARE_MM and abs(da[2] - db[2]) <= SHARE_MM
    signs = True
    for key, axis in (("h_mid", 2), ("body_w_mid", 0), ("body_d_mid", 1)):
        a, b = (local(fr, p) for p in ends(L[key]))
        signs = signs and (b - a)[axis] > 0
    return share, signs


def report(name, placed, spacing, strict=True):
    lab, aff = P.draw(placed, spacing=spacing, strict=strict)
    grid = G.VoxelGrid(aff, lab.shape)
    kept = {}
    M.measure_volume(lab, grid, {P.LEVEL_IDS[pl.level]: pl.level for pl in placed}, name, pelvis=False, keep=kept)
    print("==", name, flush=True)
    for pl in placed:
        lv = pl.level
        if lv not in kept["verts"]:
            print(lv, "not measured")
            continue
        v = kept["verts"][lv]
        f = v.frame
        centroid = grid.world(np.argwhere(lab == P.LEVEL_IDS[lv]).astype(float)).mean(0)
        print("%s axis_turn %.2f deg (column line to own axis); flags %s" % (lv, v.axis_turn, sorted(v.flags)))
        print("   frame vs phantom axes: x %.2f  y %.2f  z %.2f deg; signs %+.0f %+.0f %+.0f" % (
            deg(f.ex, pl.R[:, 0]), deg(f.ey, pl.R[:, 1]), deg(f.ez, pl.R[:, 2]),
            np.sign(f.ex @ pl.R[:, 0]), np.sign(f.ey @ pl.R[:, 1]), np.sign(f.ez @ pl.R[:, 2])))
        print("   origin to label centroid %.1e mm" % np.linalg.norm(f.origin - centroid))
        L = {ln.key: ln for ln in LN.checked(LN.vertebra_lines(v, kept["peds"][lv], kept["values"][lv]),
                                              kept["values"][lv])}
        for mname, fr in mutants(v).items():
            fr4 = rounded(fr)
            ok1, ok2 = old_tests(fr4, L)
            rev = reviewer_checks(fr4, L, centroid)
            share, signs = more_checks(fr4, L)
            print("   %-17s ez %5.2f deg off | tests as written: handed %-5s axes %-5s | proposed fix %-5s | "
                  "body_d_mid shares x,z %-5s signed %-5s" % (mname, deg(fr.ez, f.ez), ok1, ok2, rev, share, signs),
                  flush=True)


if __name__ == "__main__":
    which = sys.argv[1:] or ["straight", "zigzag"]
    if "straight" in which:
        report("straight, the RunWithLines phantom", P.straight(LEVELS, P.Vert()), (0.8, 0.8, 1.0))
    if "zigzag" in which:
        # L3 turned 10 degrees forward on L2 and L4 turned 10 back on L3, so L3 leans against the
        # line through its neighbours' centroids; the arches meet behind, so strict is off
        v = P.Vert()
        joints = {"L3": P.Joint(sagittal=10.0), "L4": P.Joint(sagittal=-10.0)}
        report("zigzag, L3 leaning", P.chain(LEVELS, {lv: v for lv in LEVELS}, joints,
                                             R0=P.rotation((1.0, 0.3, 0.0), 18.0)), (0.8, 0.8, 1.0), strict=False)

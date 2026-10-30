"""Probe: on several phantoms, (1) the lines drawn at once after vertebra_values against those the
export draws after measure_volume returns (pelvis, discs, regional run between), (2) the reused
pedicle reading against reading one_side again, (3) the frame kept against the frame at once.
Phantoms only."""
import copy
import math
import sys

import numpy as np

from morphometry import column as COL
from morphometry import measure as M
from morphometry.tests import phantom as P
from morphoview import lines as LN
from scanimport import geometry as G

LUMBAR = ["L2", "L3", "L4"]


def f(x):
    x = float(x)
    return "nan" if math.isnan(x) else x


def vec(a):
    return tuple(f(x) for x in np.asarray(a, float))


def snap_lines(lines):
    return [(ln.key, ln.level, ln.status, ln.rule, ln.panel, f(ln.value), f(ln.measured),
             vec(ln.a), vec(ln.b),
             tuple((k, vec(a), vec(b)) for k, (a, b) in ln.extra.items())) for ln in lines]


def run(name, lab, aff, levels, pelvis=False):
    grid = G.VoxelGrid(aff, lab.shape)
    names = {P.LEVEL_IDS[lv]: lv for lv in levels}
    if pelvis:
        names.update({P.SACRUM: "sacrum", P.HIP_RIGHT: "hip_right", P.HIP_LEFT: "hip_left"})
    at_once, frames_at_once, disc_at_once = {}, {}, {}
    real_vv, real_disc = M.vertebra_values, COL.disc

    def vv(v):
        vals, flags, ped = real_vv(v)
        at_once[v.level] = snap_lines(LN.checked(LN.vertebra_lines(v, ped, dict(vals)), dict(vals)))
        frames_at_once[v.level] = copy.deepcopy(v.frame)
        return vals, flags, ped

    def disc(U, L, pu, pl, d):
        out = real_disc(U, L, pu, pl, d)
        disc_at_once[(U.level, L.level)] = snap_lines(LN.checked(LN.discs(U, L), dict(out)))
        return out

    M.vertebra_values, COL.disc = vv, disc
    try:
        kept = {}
        rows = M.measure_volume(lab, grid, names, name, pelvis=pelvis, keep=kept)
    finally:
        M.vertebra_values, COL.disc = real_vv, real_disc
    problems = []
    rowvals = {(r["level"], r["key"]): r["value"] for r in rows}
    for lv, v in kept["verts"].items():
        vals = kept["values"][lv]
        later = snap_lines(LN.checked(LN.vertebra_lines(v, kept["peds"][lv], vals), vals))
        if later != at_once[lv]:
            problems.append("%s %s: lines after measure_volume differ from lines at once" % (name, lv))
        f0, f1 = frames_at_once[lv], v.frame
        for a in ("origin", "ex", "ey", "ez"):
            if not np.array_equal(getattr(f0, a), getattr(f1, a)):
                problems.append("%s %s: frame.%s moved" % (name, lv, a))
        # the values kept against the rows written
        for k, x in vals.items():
            if isinstance(x, np.ndarray):
                continue
            rv = rowvals.get((lv, k), "MISSING")
            same = (rv is x) or (isinstance(x, float) and isinstance(rv, float) and
                                 ((math.isnan(x) and math.isnan(rv)) or x == rv)) or rv == x
            if not same:
                problems.append("%s %s %s: kept %r, row %r" % (name, lv, k, x, rv))
        # the reused reading against reading again
        again = LN.checked(LN.vertebra_lines(v, kept["peds"][lv]), vals)
        reused = LN.checked(LN.vertebra_lines(v, kept["peds"][lv], vals), vals)
        ka, kr = [ln.key for ln in again], [ln.key for ln in reused]
        if ka != kr:
            problems.append("%s %s: keys differ: again only %s, reused only %s; touching=%s" % (
                name, lv, sorted(set(ka) - set(kr)), sorted(set(kr) - set(ka)), bool(v.touching.any())))
        for x in again:
            y = next((y for y in reused if y.key == x.key), None)
            if y is None:
                continue
            same_v = (math.isnan(x.value) and math.isnan(y.value)) or x.value == y.value
            if not same_v or x.status != y.status or not np.array_equal(x.a, y.a) or not np.array_equal(x.b, y.b):
                problems.append("%s %s %s: again (%r, %s) reused (%r, %s)" % (name, lv, x.key, x.value, x.status,
                                                                           y.value, y.status))
        statuses = {}
        for ln in reused:
            statuses[ln.status.split(":")[0]] = statuses.get(ln.status.split(":")[0], 0) + 1
        print("  %s %s: %d lines %s touching=%s" % (name, lv, len(reused), statuses, bool(v.touching.any())))
    for (a, b), dv in kept["discs"].items():
        later = snap_lines(LN.checked(LN.discs(kept["verts"][a], kept["verts"][b]), dv))
        if later != disc_at_once[(a, b)]:
            problems.append("%s %s-%s: disc lines differ" % (name, a, b))
    print(name, "levels", sorted(kept["verts"]), "discs", sorted(kept["discs"]))
    for p in problems:
        print("   PROBLEM", p)
    return problems


def crop_below(lab, aff, level, share=30):
    idx = np.argwhere(lab == P.LEVEL_IDS[level])
    k0 = int(np.percentile(idx[:, 2], share))
    out = np.array(aff, float)
    out[:3, 3] += out[:3, 2] * k0
    return lab[:, :, k0:], out


def main(which):
    cases = []
    if "straight" in which:
        lab, aff = P.draw(P.straight(LUMBAR, P.Vert()), spacing=(0.8, 0.8, 1.0))
        cases.append(("straight", lab, aff, LUMBAR, False))
    if "pitched" in which:
        lab, aff = P.draw(P.straight(LUMBAR, P.lumbar(ped_s=-8.0, ped_t=8.0)))
        cases.append(("pitched", lab, aff, LUMBAR, False))
    if "overhang" in which:
        lab, aff = P.draw(P.straight(LUMBAR, P.lumbar(sap_x=19.0, sap_y=-10.0, facet=0.0, sap_thk=3.5, sap_len=14.0)))
        cases.append(("overhang", lab, aff, LUMBAR, False))
    if "mass" in which:
        lab, aff = P.draw(P.straight(LUMBAR, P.lumbar(ped_waist=0.02, mass_w=8.0, mass_h=24.0, foramen_d=6.5)),
                          strict=False)
        cases.append(("lateralmass", lab, aff, LUMBAR, False))
    if "thick" in which:
        lab, aff = P.draw(P.straight(LUMBAR, P.Vert(), tilt=((1.0, 0.0, 0.0), 20.0)), spacing=(0.86, 0.86, 2.5),
                          grid_turn=((0.0, 0.0, 1.0), 0.0))
        cases.append(("thick", lab, aff, LUMBAR, False))
    if "cut" in which:
        lab, aff = P.draw(P.straight(LUMBAR, P.Vert()))
        lab, aff = crop_below(lab, aff, "L4")
        cases.append(("cut", lab, aff, LUMBAR, False))
    if "cervical" in which:
        levels = ["C2", "C3", "C4", "C5"]
        verts = {"C2": P.cervical(dens_r=4.5, dens_h=14.0, dens_y=1.5), "C3": P.cervical(), "C4": P.cervical(),
                 "C5": P.cervical()}
        placed = P.chain(levels, verts, {lv: P.Joint(gap=5.0) for lv in levels[1:]},
                         R0=P.rotation((1.0, 0.0, 0.0), 2.0))
        lab, aff = P.draw(placed, grid_turn=((0.0, 0.0, 1.0), 0.0), strict=False)
        cases.append(("cervical", lab, aff, levels, False))
    if "pelvis" in which:
        levels = ["L4", "L5"]
        placed = P.straight(levels)
        lab, aff = P.draw(placed, spacing=(1.0, 1.0, 1.0), pelvis=P.Pelvis())
        cases.append(("pelvis", lab, aff, levels, True))
    if "joints" in which:
        joint = P.Joint(gap=10.0, sagittal=8.0, coronal=4.0, axial=5.0, slip=4.0)
        placed = P.chain(LUMBAR, {lv: P.Vert() for lv in LUMBAR}, {lv: joint for lv in LUMBAR[1:]},
                         R0=P.rotation((1.0, 0.3, 0.0), 12.0))
        lab, aff = P.draw(placed, strict=False)
        cases.append(("joints", lab, aff, LUMBAR, False))
    allp = []
    for c in cases:
        allp += run(*c)
    print("TOTAL PROBLEMS", len(allp))


if __name__ == "__main__":
    main(sys.argv[1:])

"""Run with PYTHONPATH set to the repository. Trace the pedicle reading (pedicle.py v3) on a phantom's L3 or on a real study's levels:
the profile row by row, the isthmus, the axis, the parted surfaces and the band between the pedicles.

  trace_v3.py phantom <straight|mass|shapes>
  trace_v3.py real <labels.nii.gz> <L5,C5,...>
"""
import sys

import numpy as np

from morphometry import anatomy as A, measure as M, pedicle as PED, canal as CANAL   # noqa: E402
from morphometry.tests import phantom as P                                          # noqa: E402
from scanimport import geometry as G, volume as V, LEVELS                            # noqa: E402

LUMBAR = ["L2", "L3", "L4"]


def phantom_volume(which):
    if which == "mass":
        v = P.lumbar(ped_waist=0.02, mass_w=8.0, mass_h=24.0, foramen_d=6.5)
    elif which == "shapes":
        v = P.lumbar(Ha=30.0, concavity=2.0, waist=0.92, ped_t=12.0, ped_s=6.0, facet=55.0, sp_angle=32.0)
    else:
        v = P.Vert()
    placed = P.straight(LUMBAR, v)
    lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), grid_turn=((0.0, 0.0, 1.0), 7.0), strict=False)
    names = {P.LEVEL_IDS[lv]: lv for lv in LUMBAR}
    return lab, G.VoxelGrid(aff, lab.shape), names, ["L3"], P.truth(v)


def real_volume(labels, levels):
    vol, grid, names, problems, _ = V.read_labels(labels, "enhance")
    return vol, grid, names, levels, {}


def trace(lab, grid, names, levels, truth):
    vox = V.vertebra_voxels(lab, names)
    for lv in list(vox):
        vox[lv], _ = M.main_piece(vox[lv])
    order = [lv for lv in LEVELS if lv in vox]
    spine = [lv for lv in order if lv != "sacrum"]
    cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in spine]
    whole = M.whole_levels(vox, spine, lab.shape)
    axes = dict(zip(spine, M.column_line(cents, whole, grid.superior())))
    for lv in levels:
        vert = A.build(lv, vox[lv], grid, axes[lv], V.touching_edge(vox[lv], lab.shape), M.neighbours_of(vox, order, lv))
        print("=====", lv, "flags", vert.flags, "fx fy fz", round(vert.fx, 2), round(vert.fy, 2), round(vert.fz, 2))
        zb = CANAL.body_span(vert)
        zs = PED.anchors(vert, zb)
        print("body span %.1f..%.1f anchors %s wall %.2f wall_post %.2f midline %.2f depth %.1f" % (
            zb[0], zb[1], np.round(zs, 2), vert.wall, vert.wall_post, vert.midline, vert.wall - vert.wall_post))
        print("rings z: %s" % " ".join("%.1f" % s.z for s in vert.full_rings()))
        for side, name in PED.SIDES:
            print("==", name)
            m = PED.SideMap(vert, side)
            rows = PED.profile(m, zs)
            got = PED.isthmus(rows, vert, m)
            if got is None:
                print("no isthmus: %d rows" % len(rows))
                continue
            k, near, walls0 = got
            sec = float(np.median([rows[i]["w"] for i in near]))
            hgt = float(np.median([rows[i]["h"] for i in near]))
            taken, walls = PED.axis_rows(m, rows, near, k, walls0)
            rise, why, parted = PED.climb(m, rows, near, walls, sec, hgt)
            a = PED.CANAL.smoothed_values(np.array([r["w"] * r["h"] for r in rows]))
            for i, r in enumerate(rows):
                mark = "*" if i == k else ("n" if i in near else ("t" if i in taken else " "))
                print("  %s y=%6.2f u0=%6.2f u1=%6.2f w=%5.2f z=%6.2f h=%5.2f area=%6.1f run=%.2f..%.2f wall=%s" % (
                    mark, r["y"], r["u0"], r["u1"], r["w"], r["z"], r["h"], a[i], r["run"][0], r["run"][1],
                    "%.2f" % walls[i] if i in walls else "-"))
            print("surfaces: %d columns spanning %.1f mm; climb %s%s" % (
                len(parted["columns"]), parted["span"], "%.4f per mm" % rise if np.isfinite(rise) else "not read", "; " + why if why else ""))
            for name in ("top", "bottom"):
                if name in parted:
                    rec = parted[name]
                    print("  %s: bone %d air %d%s" % (name, rec["bone"], rec["air"],
                          ", margin %.3f, %d across, slope %.4f per mm" % (rec["margin"], rec["across"], rec["coefficients"][1])
                          if "margin" in rec else ""))
            out, note, info = PED.one_side(vert, side, zb)
            print("out", {kk: round(x, 2) for kk, x in out.items()}, note)
            if info:
                print("centre", np.round(info["centre"], 2), "axis", np.round(info["axis"], 3), "near", info["near"], "taken", info["taken"])
        out, flags, info = PED.measures(vert, zb)
        band = PED.band(info)
        print("band", None if band is None else {kk: (round(x, 2) if isinstance(x, float) else x) for kk, x in band.items()})
        print("flags", flags)
        for key in ("pedicle_w", "pedicle_h", "pedicle_angle_transverse", "pedicle_angle_sagittal", "pedicle_chord"):
            print("  %-26s %8.3f  truth %8.3f" % (key, out.get(key, float("nan")), truth.get(key, float("nan"))))
        if band:
            for key in ("interpedicular", "interpedicular_max"):
                print("  %-26s %8.3f  truth %8.3f" % (key, band.get(key, float("nan")), truth.get(key, float("nan"))))
        sys.stdout.flush()


if __name__ == "__main__":
    if sys.argv[1] == "phantom":
        trace(*phantom_volume(sys.argv[2]))
    else:
        trace(*real_volume(sys.argv[2], sys.argv[3].split(",")))

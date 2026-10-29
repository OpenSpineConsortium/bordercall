"""Run with PYTHONPATH set to the repository. Per near row of a real level: the medial and lateral surfaces per layer over the middle half
of the column, and candidate transverse angles: (a) the medial wall's slope, (b) the middles'
slope, (c) the middles with the lateral surface at its least over the layers, (d) the lateral
surface's slope alone."""
import sys
import numpy as np
from morphometry import anatomy as A, measure as M, pedicle as PED, canal as CANAL
from scanimport import volume as V, LEVELS

labels, levels = sys.argv[1], sys.argv[2].split(",")
vol, grid, names, problems, _ = V.read_labels(labels, "enhance")
vox = V.vertebra_voxels(vol, names)
for k in list(vox):
    vox[k], _ = M.main_piece(vox[k])
order = [k for k in LEVELS if k in vox]
spine = [k for k in order if k != "sacrum"]
cents = [grid.world(vox[k].astype(float)).mean(0) for k in spine]
whole = M.whole_levels(vox, spine, vol.shape)
axes = dict(zip(spine, M.column_line(cents, whole, grid.superior())))


def slope_angle(ys, us, side):
    if len(ys) < 3 or np.ptp(ys) < 2.0:
        return float("nan")
    a = np.polyfit(np.array(ys), side * np.array(us), 1)[0]
    d = -np.array([a, 1.0]) / np.hypot(a, 1.0)
    return np.degrees(np.arctan2(side * d[0], -d[1]))


for lv in levels:
    v = A.build(lv, vox[lv], grid, axes[lv], V.touching_edge(vox[lv], vol.shape), M.neighbours_of(vox, order, lv))
    zb = CANAL.body_span(v)
    zs = PED.anchors(v, zb)
    for side, name in PED.SIDES:
        m = PED.SideMap(v, side)
        rows = PED.profile(m, zs)
        got = PED.isthmus(rows, v)
        if got is None:
            print(lv, name, "no isthmus")
            continue
        k, near = got
        print("=====", lv, name, "near", near, "k", k)
        ys, walls, mids, mids_min, lats, lats_min = [], [], [], [], [], []
        for i in near:
            r = rows[i]
            layers = PED.layers_of(v, r["run"])
            per = []
            for z in layers:
                ch = m.chord(r["y"], float(z))
                per.append(None if ch is None else (round(ch[0], 1), round(ch[1], 1)))
            good = [c for c in per if c is not None and c[0] >= PED.MIDLINE_CLEAR_MM]
            print("  y=%6.2f w=%5.2f h=%5.2f z=%5.2f  layers: %s" % (r["y"], r["w"], r["h"], r["z"], per))
            if not good:
                continue
            u0 = float(np.median([c[0] for c in good]))
            u1 = float(np.median([c[1] for c in good]))
            u1min = float(min(c[1] for c in good))
            ys.append(r["y"]); walls.append(u0); lats.append(u1); lats_min.append(u1min)
            mids.append(0.5 * (u0 + u1)); mids_min.append(0.5 * (u0 + u1min))
        print("  angles: wall %.1f  middles %.1f  middles(lat min) %.1f  lateral %.1f  lateral(min) %.1f" % (
            slope_angle(ys, walls, side), slope_angle(ys, mids, side), slope_angle(ys, mids_min, side),
            slope_angle(ys, lats, side), slope_angle(ys, lats_min, side)))

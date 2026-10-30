"""The old construction's middles on the straight phantom at the suite's tilt: how many rows gave a
middle and what they span, against the docstring's '7.5 mm baseline'."""
import importlib.util, sys, time
import numpy as np
t0 = time.time()
from importlib.machinery import SourceFileLoader
spec = importlib.util.spec_from_file_location(
    "morphometry.pedicle_before",
    "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/pedicle.py.before", loader=SourceFileLoader("morphometry.pedicle_before", "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/pedicle.py.before"))
OLD = importlib.util.module_from_spec(spec)
sys.modules["morphometry.pedicle_before"] = OLD
spec.loader.exec_module(OLD)
from morphometry import anatomy as A, measure as M, canal as CANAL
from morphometry.tests import trace_pedicle as T
from scanimport import volume as V, LEVELS
lab, grid, names, levels, truth = T.phantom_volume("straight")
vox = V.vertebra_voxels(lab, names)
for lv in list(vox):
    vox[lv], _ = M.main_piece(vox[lv])
order = [lv for lv in LEVELS if lv in vox]
cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in order]
whole = M.whole_levels(vox, order, lab.shape)
axes = dict(zip(order, M.column_line(cents, whole, grid.superior())))
lv = "L3"
vert = A.build(lv, vox[lv], grid, axes[lv], V.touching_edge(vox[lv], lab.shape), M.neighbours_of(vox, order, lv))
zb = CANAL.body_span(vert)
for side, name in OLD.SIDES:
    m = OLD.SideMap(vert, side)
    rows = OLD.profile(m, OLD.anchors(vert, zb))
    k, near, walls0 = OLD.isthmus(rows, vert, m)
    sec = float(np.median([rows[i]["w"] for i in near]))
    hgt = float(np.median([rows[i]["h"] for i in near]))
    taken, walls, mids = OLD.axis_rows(m, rows, near, k, sec, hgt, walls0)
    ys = np.array([rows[i]["y"] for i in sorted(mids)])
    near_ys = np.array([rows[i]["y"] for i in near])
    d, note, reads = OLD.axis_from(rows, taken, walls, mids, side)
    print("%-5s near %d rows span %.1f | rows with a middle %d span %.1f | taken %d span %.1f | old sagittal %.2f (%s)" % (
        name, len(near), np.ptp(near_ys), len(mids), np.ptp(ys), len(taken),
        np.ptp([rows[i]["y"] for i in taken]), np.degrees(np.arctan2(d[2], -d[1])) - np.degrees(np.arctan(OLD.wall_slope(vert))), reads))
print("%.0f s" % (time.time() - t0))

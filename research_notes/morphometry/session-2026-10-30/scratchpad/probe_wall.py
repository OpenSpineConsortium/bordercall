"""wall_slope on the straight and pitched phantoms at several tilts about x, turn 0."""
import math, sys
import numpy as np
from morphometry import anatomy as A, measure as M, pedicle as PED, body as BODY
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS
LUMBAR = ["L2", "L3", "L4"]
for name, kw in (("straight", {}), ("pitched", dict(ped_s=10.0)), ("shapes", dict(Ha=30.0, concavity=2.0, waist=0.92, ped_t=12.0, ped_s=6.0, facet=55.0, sp_angle=32.0))):
    for tilt in (2.0, 18.0):
        v = P.lumbar(**kw)
        placed = P.straight(LUMBAR, v, tilt=((1.0, 0.0, 0.0), tilt) if tilt != 18.0 else ((1.0, 0.3, 0.0), 18.0))
        lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), grid_turn=((0.0, 0.0, 1.0), 0.0 if tilt != 18.0 else 7.0), strict=False)
        grid = G.VoxelGrid(aff, lab.shape)
        names = {P.LEVEL_IDS[lv]: lv for lv in LUMBAR}
        vox = V.vertebra_voxels(lab, names)
        for lv in list(vox):
            vox[lv], _ = M.main_piece(vox[lv])
        order = [lv for lv in LEVELS if lv in vox]
        cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in order]
        whole = M.whole_levels(vox, order, lab.shape)
        axes = dict(zip(order, M.column_line(cents, whole, grid.superior())))
        vert = A.build("L3", vox["L3"], grid, axes["L3"], V.touching_edge(vox["L3"], lab.shape), M.neighbours_of(vox, order, "L3"))
        pl = [p for p in placed if p.level == "L3"][0]
        ez = vert.frame.ez @ pl.R
        print("%-8s tilt %4.1f  wall_slope %6.2f deg  anatomy wall_slope %6.2f deg  frame ez vs phantom z %.2f deg (y component %.4f)" % (
            name, tilt, math.degrees(math.atan(PED.wall_slope(vert))), math.degrees(math.atan(vert.wall_slope)),
            math.degrees(math.acos(min(1.0, ez[2]))), ez[1]))
        sys.stdout.flush()

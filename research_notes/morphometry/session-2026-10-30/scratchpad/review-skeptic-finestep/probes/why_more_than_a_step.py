"""Why some path lengths move by more than one step: count, for each ray, how many separate runs of
'inside' the voxel-nearest test gives along it (read very finely), and set that beside how far the
start-of-step fault moved its path length."""
import math
import sys

import numpy as np

from morphoview import projection as PJ
from morphoview import shapes as SH

saved_mid, saved_start = np.load(sys.argv[1]), np.load(sys.argv[2])
h, R = 0.5, 10.0
centre = np.array([12.1, 11.9, 12.05])
grid = np.indices((48, 48, 48)).reshape(3, -1).T * h
mask = (np.linalg.norm(grid - centre, axis=1) <= R).reshape(48, 48, 48)
ball = SH.Volume(mask, np.diag([h, h, h, 1.0]))


def camera(orthographic):
    return PJ.Camera(PJ.View(rot_deg=(10.0, 20.0, 5.0), xyz_mm=(0.0, 800.0, 0.0), isocentre_mm=tuple(centre),
                             sdd=1200.0, delx=0.7, height=48, width=48, orthographic=orthographic))


to_voxel = np.linalg.inv(ball.affine)
lo, hi = ball.box()
for key, orth in (("orth", True), ("cone", False)):
    cam = camera(orth)
    moved = np.abs(saved_mid[key] - saved_start[key])
    pix = np.argwhere(moved > 1e-12)
    src, tgt = cam.rays(pix[:, ::-1] + 0.5)
    a = src @ to_voxel[:3, :3].T + to_voxel[:3, 3]
    b = tgt @ to_voxel[:3, :3].T + to_voxel[:3, 3]
    t0, t1 = SH.slab(a, b, lo, hi)
    s = np.linspace(0.0, 1.0, 20001)
    tk = t0[:, None] + s[None, :] * (t1 - t0)[:, None]
    inside = ball.inside(a[:, None, :] + tk[:, :, None] * (b - a)[:, None, :])
    runs = (np.diff(inside.astype(int), axis=1) == 1).sum(axis=1) + inside[:, 0]
    m = moved[pix[:, 0], pix[:, 1]]
    one = m <= 0.25 + 1e-12
    print("%s: %d rays moved; of those moved by at most a step, runs inside: %s; of those moved by more, runs inside: %s"
          % (key, len(m), dict(zip(*np.unique(runs[one], return_counts=True))),
             dict(zip(*np.unique(runs[~one], return_counts=True)))))

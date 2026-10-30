import math
import numpy as np
from morphoview import projection as PJ
from morphoview import shapes as SH

def cone(**more):
    view = dict(rot_deg=(0.0, 0.0, 0.0), xyz_mm=(0.0, 800.0, 0.0), isocentre_mm=(0.0, 0.0, 0.0), sdd=1200.0,
                delx=1.0, height=200, width=240)
    view.update(more)
    return PJ.Camera(PJ.View(**view))

cam = cone(orthographic=True, delx=0.8, dely=1.1)
for tilt in (0.0, 30.0, 60.0):
    t = math.radians(tilt)
    ring = SH.circle([3.0, -5.0, 2.0], [math.sin(t), math.cos(t), 0.0], 20.0, tolerance=0.001)
    area = ring.project(cam).area_px() * 0.8 * 1.1
    print("tilt %g: ratio - 1 = %.2e" % (tilt, area / (math.pi * 400.0 * math.cos(t)) - 1.0))

h, R = 0.5, 10.0
centre = np.array([12.1, 11.9, 12.05])
grid = np.indices((48, 48, 48)).reshape(3, -1).T * h
mask = (np.linalg.norm(grid - centre, axis=1) <= R).reshape(48, 48, 48)
ball = SH.Volume(mask, np.diag([h, h, h, 1.0]))
view = dict(rot_deg=(10.0, 20.0, 5.0), xyz_mm=(0.0, 800.0, 0.0), isocentre_mm=tuple(centre), sdd=1200.0, delx=0.3,
            height=110, width=110, orthographic=True)
pc = PJ.Camera(PJ.View(**view))
total = float(ball.path_length(pc).sum()) * 0.3 * 0.3
print("parallel sum / voxel volume - 1 = %.2e; voxel volume %.1f vs ball %.1f" % (total / ball.volume_mm3() - 1, ball.volume_mm3(), 4 / 3 * math.pi * R ** 3))

"""Path lengths of test_shapes' ball under the test's two cameras, from whichever tree is on the
path, saved so two trees can be compared; also the test's own bounds and median, evaluated here."""
import math
import sys

import numpy as np

from morphoview import projection as PJ
from morphoview import shapes as SH

out = sys.argv[1]
h, R = 0.5, 10.0
centre = np.array([12.1, 11.9, 12.05])
grid = np.indices((48, 48, 48)).reshape(3, -1).T * h
mask = (np.linalg.norm(grid - centre, axis=1) <= R).reshape(48, 48, 48)
ball = SH.Volume(mask, np.diag([h, h, h, 1.0]))


def camera(orthographic, **more):
    view = dict(rot_deg=(10.0, 20.0, 5.0), xyz_mm=(0.0, 800.0, 0.0), isocentre_mm=tuple(centre),
                sdd=1200.0, delx=0.7, height=48, width=48, orthographic=orthographic)
    view.update(more)
    return PJ.Camera(PJ.View(**view))


def chords(cam, radius):
    src, det = cam.rays(cam.pixel_centres())
    d = (det - src) / np.linalg.norm(det - src, axis=1, keepdims=True)
    w = centre - src
    perp = np.linalg.norm(w - (w * d).sum(axis=1, keepdims=True) * d, axis=1)
    return 2.0 * np.sqrt(np.clip(radius ** 2 - perp ** 2, 0.0, None))


step = 0.5 * h
slack = math.sqrt(3.0) / 2.0 * h
saved = {}
for orth in (True, False):
    cam = camera(orth)
    got = ball.path_length(cam)
    saved["orth" if orth else "cone"] = got
    g = got.ravel()
    low = chords(cam, R - slack) - step
    high = chords(cam, R + slack) + step
    inner = chords(cam, R - 1.0) > 0
    med = float(np.median(np.abs(g - chords(cam, R))[inner]))
    print("orthographic=%s: within the test's band %s (worst margin below %.4f, above %.4f), median |got - chord| %.4f (test asks < %.2f), nonzero %d"
          % (orth, bool((g >= low - 1e-9).all() and (g <= high + 1e-9).all()), float((g - low).min()),
             float((high - g).min()), med, h, int((g > 0).sum())))
cam = camera(True, delx=0.3, height=110, width=110)
total = float(ball.path_length(cam).sum()) * 0.3 * 0.3
saved["sum110"] = np.array([total / ball.volume_mm3()])
print("parallel sum / volume %.6f (test asks within 0.005 of 1)" % (total / ball.volume_mm3()))
np.savez(out, **saved)

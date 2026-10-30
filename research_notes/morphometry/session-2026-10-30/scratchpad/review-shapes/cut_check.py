import sys, math
sys.path.insert(0, sys.argv[1])
import numpy as np
from morphoview import projection as PJ, shapes as SH

cam = PJ.Camera(PJ.View(rot_deg=(0, 0, 0), xyz_mm=(0, 800, 0), isocentre_mm=(0, 0, 0), sdd=1200, delx=1, height=200, width=240))
src, beam = cam.source, cam.beam

def depth(p):
    return cam.camera_points(p)[:, 2]

def reference_runs(points, closed):
    """The stretches of the polyline in front of NEAR, by dense sampling: each run's vertices in order."""
    ring = np.vstack([points, points[:1]]) if closed else points
    runs, cur = [], []
    n = len(ring) - 1
    for i in range(n):
        a, b = ring[i], ring[i + 1]
        s = np.linspace(0, 1, 2001)
        seg = a + s[:, None] * (b - a)
        front = depth(seg) > SH.NEAR
        for k in range(len(s) - (0 if i == n - 1 else 1)):
            if front[k]:
                cur.append((i, s[k]))
            elif cur:
                runs.append(cur); cur = []
    if cur:
        runs.append(cur)
    if closed and len(runs) > 1 and runs[0][0] == (0, 0.0) and runs[-1][-1][1] == 1.0:
        runs[0] = runs[-1] + runs[0]; runs.pop()
    return runs

def check(points, closed, label):
    curve = SH.Curve(points, closed)
    got = curve.project(cam)
    pieces = got.pieces()
    ref = reference_runs(points, closed)
    pts3d, starts = SH.in_front(curve.segments(), cam, closed)
    ends = starts[1:] + [len(pts3d)] if starts else [len(pts3d)]
    ok = len(pieces) == len(ref)
    detail = []
    for s, e in zip(starts or [0], ends):
        piece = pts3d[s:e]
        d = depth(piece)
        # every in-front vertex of the curve lies in exactly one piece, in order; each piece's points
        # follow one another along the curve
        detail.append((len(piece), float(d.min())))
        ok &= bool((d >= SH.NEAR * 0.999).all())
    front_vertices = points[depth(points) > SH.NEAR]
    found = [int(np.sum(np.all(np.isclose(pts3d, v, atol=1e-12, rtol=0), axis=1))) for v in front_vertices]
    ok &= all(f == 1 for f in found)
    print("%-55s closed=%s pieces=%d ref=%d closed2d=%s ok=%s %s" % (label, closed, len(pieces), len(ref), got.closed, ok, detail))

t = np.linspace(0, 2 * math.pi, 37)[:-1]
# a wavy ring around the source's axis crossing the source plane four times
for phase in (0.0, 0.3, math.pi / 4 + 0.01, 1.0):
    r = 60.0
    ring = np.stack([r * np.cos(t + phase), 800.0 + 30.0 * np.cos(2 * (t + phase)) + 5.0, r * np.sin(t + phase)], axis=1)
    check(ring, True, "closed ring, two dips, phase %.2f" % phase)
    check(ring, False, "same points open, phase %.2f" % phase)
# three dips
ring3 = np.stack([60 * np.cos(t), 800.0 + 30.0 * np.cos(3 * t) + 5.0, 60 * np.sin(t)], axis=1)
check(ring3, True, "closed ring, three dips, first vertex behind")
ring3b = np.stack([60 * np.cos(t), 800.0 - 30.0 * np.cos(3 * t) + 5.0, 60 * np.sin(t)], axis=1)
check(ring3b, True, "closed ring, three dips, first vertex in front")

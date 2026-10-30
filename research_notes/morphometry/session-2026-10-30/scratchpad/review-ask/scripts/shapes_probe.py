"""Each of the ask's shapes made and projected through a camera of FleXray's kind: an arc, a plane's
patch (face on and edge on), a polygon, a spline, a ball as a Volume; and what a curved surface
and an analytic solid would need."""
import sys
import numpy as np
sys.path.insert(0, sys.argv[1])
from morphoview import projection as PJ
from morphoview import shapes as SH
cam = PJ.Camera(PJ.View(rot_deg=(20.0, -10.0, 0.0), xyz_mm=(0.0, 700.0, 0.0), isocentre_mm=(0.0, 0.0, 0.0),
                        sdd=1200.0, delx=1.5, height=256, width=256))
arc = SH.arc([0, 0, 0], [0, 0, 1], [20, 0, 0], 120.0)
a2 = arc.project(cam)
print("arc: points", len(arc.points), "pieces", len(a2.pieces()), "all in beam", bool(a2.in_beam.all()))
plane = SH.Plane([0.0, 0.0, 0.0], cam.ray_direction([0.0, 0.0, 0.0])[0])          # face on
patch = plane.patch(10.0, 5.0)
p2 = patch.project(cam)
print("face-on patch: corners match camera", np.allclose(p2.uv, cam.project(patch.corners).uv), "closed", p2.closed,
      "area px", round(p2.area_px(), 3), "seen at", round(plane.seen_at_deg(cam), 3))
edge = SH.Plane([0.0, 0.0, 0.0], np.cross(cam.ray_direction([0.0, 0.0, 0.0])[0], [0.0, 0.0, 1.0]))
e2 = edge.patch(10.0, 5.0).project(cam)
print("edge-on patch: area px", round(e2.area_px(), 6), "seen at", round(edge.seen_at_deg(cam), 6))
sp = SH.spline([[0, 0, -30], [5, 2, 0], [0, 5, 30]]).project(cam)
print("spline points", len(sp.uv))
g = np.indices((40, 40, 40)).reshape(3, -1).T * 0.5
ball = SH.Volume((np.linalg.norm(g - 10.0, axis=1) <= 8.0).reshape(40, 40, 40), np.diag([0.5, 0.5, 0.5, 1.0]))
print("ball silhouette pixels", int(ball.silhouette(cam).sum()))
print("names in shapes:", [n for n in dir(SH) if not n.startswith("_") and n[0].isupper() or n in ("arc", "circle", "ellipse", "spline", "project_points")])

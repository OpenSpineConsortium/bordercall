import json, sys
import numpy as np
sys.path.insert(0, "/home/user/bordercall")
from morphoview.projection import Camera, View
d = json.load(open(sys.argv[1]))
beads = np.array(d["beads"]["centroids_mm"])
iso = tuple(d["isocentre_mm"])
VIEWS = [
    dict(rot_deg=(90.0, 3.0, -2.0), xyz_mm=(20.0, 700.0, -15.0), sdd=1200.0, delx=1.8, height=160, width=136),
    dict(rot_deg=(20.0, -10.0, 5.0), xyz_mm=(-30.0, 650.0, 20.0), sdd=1180.0, delx=1.6, dely=1.7, x0=40.0, y0=-40.0, height=176, width=144),
    dict(rot_deg=(-140.0, 12.0, -6.0), xyz_mm=(15.0, 820.0, 10.0), sdd=1240.0, delx=1.6, height=144, width=160, orthographic=True),
]
for spec in VIEWS:
    view = View(isocentre_mm=iso, **spec)
    uv = Camera(view).project(beads).uv
    print("u %.1f..%.1f of %d   v %.1f..%.1f of %d" % (uv[:,0].min(), uv[:,0].max(), view.width, uv[:,1].min(), uv[:,1].max(), view.height))

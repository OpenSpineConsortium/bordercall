"""Re-derive the camera agreement and the bead numbers from the fixture."""
import dataclasses, json, math
import numpy as np
from morphoview import projection as PJ
from morphoview.tests import flexray_record as FR

R = json.load(open(FR.FIXTURE))
worst = {"rt": 0, "k": 0, "src": 0, "det": 0}
for v in R["views"] + R["orientations"]:
    cam = PJ.Camera(PJ.View(**v["view"]))
    rec = v["camera"]
    worst["rt"] = max(worst["rt"], float(np.abs(cam.to_world - np.array(rec["rt_inv"])).max()))
    worst["k"] = max(worst["k"], float(np.abs(np.linalg.inv(cam.intrinsics) - np.array(rec["k_inv"])).max()))
    src, det = cam.rays(cam.pixel_centres())
    n = [int(math.floor(vv)) * cam.view.width + int(math.floor(u)) for u, vv in rec["uv"]]
    worst["src"] = max(worst["src"], float(np.abs(src[n] - np.array(rec["source"])).max()))
    worst["det"] = max(worst["det"], float(np.abs(det[n] - np.array(rec["detector"])).max()))
    print(v.get("name", v["view"]["orientation"]), "pixels", len(rec["uv"]), "orientation", v["view"]["orientation"])
print("camera worst abs differences:", worst)

beads = np.array(R["beads"]["centroids_mm"])
print("beads", len(beads))
for v in R["views"]:
    cam = PJ.Camera(PJ.View(**v["view"]))
    seen = np.array(v["bead_centroids_uv"])
    err = np.linalg.norm(cam.project(beads).uv - seen, axis=1)
    print("%-45s max %.4f median %.4f mean %.4f" % (v["name"], err.max(), np.median(err), err.mean()))
    for slip in ({"x0": cam.view.x0 + 0.5 * cam.view.delx}, {"y0": cam.view.y0 + 0.5 * cam.view.pixel_y}):
        wrong = PJ.Camera(dataclasses.replace(cam.view, **slip))
        e2 = np.linalg.norm(wrong.project(beads).uv - seen, axis=1)
        print("    slipped %s: min %.4f median %.4f max %.4f" % (list(slip)[0], e2.min(), np.median(e2), e2.max()))

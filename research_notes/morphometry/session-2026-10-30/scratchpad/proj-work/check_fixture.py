import json, sys
import numpy as np
sys.path.insert(0, "/home/user/bordercall")
from morphoview.projection import Camera, View
d = json.load(open(sys.argv[1]))
beads = np.array(d["beads"]["centroids_mm"])
for v in d["views"]:
    view = View(**{k: (tuple(x) if isinstance(x, list) else x) for k, x in v["view"].items()})
    cam = Camera(view)
    rt = np.array(v["camera"]["rt_inv"]); kinv = np.array(v["camera"]["k_inv"])
    print("==", v["name"], "rt err %.2e" % np.abs(cam.to_world - rt).max(), "kinv err %.2e" % np.abs(np.linalg.inv(cam.intrinsics) - kinv).max())
    src, det = cam.rays(np.array(v["camera"]["uv"]))
    print("  rays err %.2e %.2e" % (np.abs(src - np.array(v["camera"]["source"])).max(), np.abs(det - np.array(v["camera"]["detector"])).max()))
    got = cam.project(beads)
    errs, missing = [], []
    for k, c in enumerate(v["bead_centroids_uv"]):
        if c is None:
            missing.append((k, np.round(got.uv[k], 1)))
            continue
        errs.append(np.linalg.norm(got.uv[k] - np.array(c)))
    errs = np.array(errs)
    print("  beads seen %d: error px median %.3f p95 %.3f max %.3f" % (len(errs), np.median(errs), np.percentile(errs, 95), errs.max()))
    print("  missing:", missing[:8], "...", len(missing))
    uv = got.uv
    print("  all beads u %.1f..%.1f of %d, v %.1f..%.1f of %d" % (uv[:,0].min(), uv[:,0].max(), view.width, uv[:,1].min(), uv[:,1].max(), view.height))

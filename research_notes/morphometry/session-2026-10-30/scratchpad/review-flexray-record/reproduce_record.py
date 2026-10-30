"""Re-render what the fixture records that Live does not render again: each recorded view's bead
centroids, and the label masks, read here from FleXray's own DRRRenderResult.labels at the request's
default threshold and at the runtime profile's threshold (fxr/models/camera/config.py)."""
import json
import sys

import numpy as np
import torch

torch.set_num_threads(2)
sys.path.insert(0, sys.argv[1])
from morphoview import projection as PJ  # noqa: E402
from morphoview.tests import flexray_record as FR  # noqa: E402
from fxr.drr import DRRRenderRequest, render_drr  # noqa: E402

RECORD = json.load(open(FR.FIXTURE))


def labels(hu, lab, aff, view, threshold):
    intr = {"sdd": [view.sdd], "delx": [view.delx], "dely": [view.pixel_y], "x0": [view.x0], "y0": [view.y0],
            "height": int(view.height), "width": int(view.width)}
    kw = {} if threshold is None else {"seg_threshold": threshold}
    req = DRRRenderRequest(rot=torch.tensor([view.rot_deg], dtype=torch.float32),
                           xyz=torch.tensor([view.xyz_mm], dtype=torch.float32), intrinsics=intr,
                           isocenter=torch.tensor([view.isocentre_mm], dtype=torch.float32),
                           orientation=view.orientation, n_samples=FR.N_SAMPLES, orthographic=view.orthographic, **kw)
    with torch.inference_mode():
        res = render_drr(volume=torch.from_numpy(hu.astype(np.float32))[None],
                         label=torch.from_numpy(lab.astype(np.int64))[None],
                         affine=torch.from_numpy(np.asarray(aff, np.float32)), request=req)
    return res.labels[0].double().numpy(), float(req.seg_threshold)


def main():
    lab, aff = FR.phantom()
    print("phantom digest matches record:", FR.digest(lab, aff) == RECORD["phantom"]["sha256"])
    print("record versions:", RECORD["versions"])
    beads = np.array(RECORD["beads"]["centroids_mm"])
    balls, centroids = FR.bead_labels(lab.shape, aff, beads)
    print("bead truth equals record:", float(np.abs(centroids - beads).max()))
    bone = np.where(lab > 0, FR.BONE_HU, FR.AIR_HU)
    hu_balls = np.where(balls > 0, FR.BONE_HU, FR.AIR_HU)
    for v in RECORD["views"]:
        view = PJ.View(**v["view"])
        shape = (view.height, view.width)
        rendered = FR.render(hu_balls, balls, aff, view, FR.BEAD_SAMPLES)
        seen = [FR.channel_centroid(rendered[k + 1]) for k in range(len(beads))]
        rec = v["bead_centroids_uv"]
        d = [float(np.linalg.norm(np.array(a) - np.array(b))) for a, b in zip(seen, rec) if a is not None and b is not None]
        none_mismatch = sum((a is None) != (b is None) for a, b in zip(seen, rec))
        print(v["name"], "bead centroids again vs record: max %.2e px, None mismatches %d" % (max(d), none_mismatch))
        for threshold in (None, 0.0):
            got, used = labels(bone, lab, aff, view, threshold)
            for level, i in RECORD["phantom"]["ids"].items():
                mask = FR.unpack(v["masks"][level], shape)
                sup = FR.unpack(v["supports"][level], shape)
                fx = got[i] > 0.5
                print("   %-8s threshold %.1f: FleXray labels vs record masks differ %d px, vs supports differ %d px;"
                      " supports %d px, record masks %d px" % (level, used, int((fx ^ mask).sum()), int((fx ^ sup).sum()),
                                                              int(sup.sum()), int(mask.sum())))


if __name__ == "__main__":
    main()

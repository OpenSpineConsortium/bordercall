"""A CT taller than one of FleXray's 256-slice crops, rendered as SchwingNet's blocks engine renders
a view (tools/render_blocks.py: cut, crop_affine, request, render_drr), with the manifest row it
would write, a lines.csv on three levels, and FleXray's own channels for each level."""
import json
import os
import sys

import nibabel as nib
import numpy as np
import torch
from fxr.datasets.ct_crops import plan_z_crops
from fxr.drr import DRRRenderRequest, render_drr

out = sys.argv[1]
os.makedirs(os.path.join(out, "images"), exist_ok=True)
shape = (32, 32, 400)
aff = np.diag([3.0, 3.0, 1.0, 1.0])
aff[:3, 3] = (-48.0, -48.0, -200.0)
lab = np.zeros(shape, np.int16)
lab[8:24, 8:24, 100:140] = 20     # L1, wholly inside the crop [0, 256)
lab[8:24, 8:24, 226:266] = 22     # L3, cut by the crop's end at slice 256
lab[8:24, 8:24, 270:300] = 23     # L4, wholly outside the crop
hu = np.where(lab > 0, 1000.0, -1000.0).astype(np.float32)
nib.save(nib.Nifti1Image(lab, aff), os.path.join(out, "mask.nii.gz"))

spec = plan_z_crops(shape[2], 256, max_overlap=0.5)[0]
crop = {"z_start": spec.z_start, "z_stop": spec.z_stop, "pad_before": spec.z_pad_before, "pad_after": spec.z_pad_after}
print("crop", crop)
# render_blocks.cut and crop_affine
vol_c = hu[..., crop["z_start"]:crop["z_stop"]]
lab_c = lab[..., crop["z_start"]:crop["z_stop"]]
aff_c = aff.copy()
aff_c[:3, 3] += aff_c[:3, :3] @ np.array([0.0, 0.0, float(crop["z_start"] - crop["pad_before"])])
aff_c = aff_c.astype(np.float32)
iso = (aff @ np.array([16.0, 16.0, 200.0, 1.0]))[:3]          # a point in the crop
pose = {"rot_deg": [90.0, 0.0, 0.0], "xyz_mm": [0.0, 700.0, 0.0], "orthographic": False, "sdd": 1200.0,
        "delx": 2.25, "grid": None}
detector, samples = 160, 500
intr = {"sdd": [pose["sdd"]], "delx": [pose["delx"]], "dely": [pose["delx"]], "x0": [0.0], "y0": [0.0],
        "height": detector, "width": detector}
req = DRRRenderRequest(rot=torch.tensor([pose["rot_deg"]]), xyz=torch.tensor([pose["xyz_mm"]]), intrinsics=intr,
                       isocenter=torch.tensor([iso.tolist()], dtype=torch.float32), orientation="AP",
                       n_samples=samples, orthographic=False)
with torch.inference_mode():
    res = render_drr(volume=torch.from_numpy(vol_c)[None], label=torch.from_numpy(lab_c.astype(np.int64)),
                     affine=torch.from_numpy(aff_c), request=req, max_label=23)
rendered = res.rendered[0].double().numpy()
support = {name: (rendered[v] > 0) for name, v in (("L1", 20), ("L3", 22), ("L4", 23))}
np.savez_compressed(os.path.join(out, "flexray_support.npz"), image=res.images[0, 0].double().numpy(), **support)
print("FleXray support pixels:", {k: int(s.sum()) for k, s in support.items()})
row = {"file": "images/s_v00.png", "subject": "s", "view": 0, "seed": 1, "crop": crop,
       "isocentre": {"label": None, "name": None, "point_mm": [float(v) for v in np.float32(iso)]},
       "pose": pose, "attenuation": None}
blocks = {"hu_window": "flexray", "air_clamp": "flexray", "crop": "flexray-axial", "crop_sampler": "uniform",
          "pose": "flexray-moose", "isocentre": "random-label", "projection": "flexray-mix",
          "attenuation": "off", "scale": "minmax", "edit": "none", "segmenter": "spineps", "views": 1,
          "detector": detector, "ray_samples": samples}
with open(os.path.join(out, "manifest.json"), "w") as fh:
    json.dump({"blocks": blocks, "engine": "blocks", "views": [row]}, fh, indent=1)


def world(i, j, k):
    return (aff @ np.array([i, j, k, 1.0]))[:3]


lines = [("L1", world(10, 16, 110), world(22, 16, 130)),
         ("L3", world(10, 16, 236), world(10, 16, 262)),   # one end inside the crop, one beyond its end
         ("L4", world(10, 16, 275), world(22, 16, 295))]
with open(os.path.join(out, "lines.csv"), "w") as fh:
    fh.write("study,level,key,part,rule,panel,value,measured,drawn,status,a_end,ax,ay,az,b_end,bx,by,bz\n")
    for lv, a, b in lines:
        fh.write("s,%s,body_height,,r,p,1,1,1,drawn,top,%r,%r,%r,bottom,%r,%r,%r\n" % ((lv,) + tuple(float(x) for x in a) + tuple(float(x) for x in b)))

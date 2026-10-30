"""One view of the thin phantom as SchwingNet's blocks engine makes it under its default recipe
(crop flexray-axial, isocentre random-label): the crops planned as schwingnet.render_blocks.plan_crops
plans them, the first crop drawn, the volume cut and the affine moved as tools/render_blocks.py's
cut and crop_affine do, the isocentre at L4's centroid in the crop, a pose inside FleXray's MOOSE
ranges, the request as tools/render_blocks.py's request builds it, rendered by fxr.drr.render_drr;
the manifest row written in tools/flexray_render.py's layout. The arithmetic of the three
SchwingNet functions is copied here verbatim, since their modules import beartype and fxr."""
import json
import math
import os
import sys
import numpy as np
import torch

out = sys.argv[1]
torch.set_num_threads(2)
lab = np.load(os.path.join(out, "lab.npy"))
aff = np.load(os.path.join(out, "aff.npy"))
CROP_DEPTH, AIR_HU = 256, -1000.0


def plan_crops(depth, overlap=0.5):          # schwingnet/render_blocks.py, plan_crops
    if depth <= CROP_DEPTH:
        before = (CROP_DEPTH - depth) // 2
        return ((0, depth, before, CROP_DEPTH - depth - before),)
    last = depth - CROP_DEPTH
    step = math.ceil(CROP_DEPTH * (1.0 - overlap))
    if last < step:
        starts = [0, last]
    else:
        intervals = math.ceil(last / step)
        starts = [round(i * last / intervals) for i in range(intervals + 1)]
        starts[0], starts[-1] = 0, last
    return tuple((s, s + CROP_DEPTH, 0, 0) for s in starts)


def cut(array, crop, fill):                  # tools/render_blocks.py, cut
    window = array[..., crop["z_start"]:crop["z_stop"]]
    if crop["pad_before"] or crop["pad_after"]:
        pad = [(0, 0)] * (array.ndim - 1) + [(crop["pad_before"], crop["pad_after"])]
        window = np.pad(window, pad, constant_values=fill)
    return np.ascontiguousarray(window)


def crop_affine(affine, crop):               # tools/render_blocks.py, crop_affine
    shifted = np.array(affine, dtype=np.float64)
    offset = float(crop["z_start"] - crop["pad_before"])
    shifted[:3, 3] += shifted[:3, :3] @ np.array([0.0, 0.0, offset])
    return shifted.astype(np.float32)


plan = plan_crops(lab.shape[2])
print("planned crops", plan)
start, stop, before, after = plan[0]
crop = {"z_start": start, "z_stop": stop, "pad_before": before, "pad_after": after}
caff = crop_affine(aff, crop)
clab = cut(lab, crop, 0)
held = sorted(int(v) for v in np.unique(clab) if v)
print("the crop drawn", crop, "holds label ids", held)
# random-label: the centroid of a structure the crop holds, in the crop's voxels, to the world
ijk = np.argwhere(clab == 23).mean(axis=0)
point = (caff.astype(np.float64) @ np.append(ijk, 1.0))[:3]
pose = {"rot_deg": [90.0, 5.0, 0.0], "xyz_mm": [10.0, 700.0, -20.0], "orthographic": False,
        "sdd": 1200.0, "delx": 1.5, "grid": None}
row = {"file": "images/0001_v00.png", "subject": "0001", "view": 0, "seed": 1, "crop": crop,
       "isocentre": {"label": 23, "name": "vertebra_l4", "point_mm": [float(v) for v in point]},
       "pose": pose, "attenuation": None}
blocks = {"hu_window": "flexray", "air_clamp": "flexray", "crop": "flexray-axial",
          "crop_sampler": "inverse-label-frequency", "pose": "flexray-moose", "isocentre": "random-label",
          "projection": "flexray-mix", "attenuation": "off", "scale": "minmax", "edit": "none",
          "segmenter": "spineps", "views": 1, "detector": 256, "ray_samples": 500}
with open(os.path.join(out, "manifest.json"), "w") as fh:
    json.dump({"blocks": blocks, "engine": "blocks", "segmenter": "spineps", "views": [row]}, fh, indent=1)

from fxr.drr import DRRRenderRequest, render_drr
hu = np.where(lab > 0, 1000.0, AIR_HU).astype(np.float32)
chu = cut(hu, crop, AIR_HU)
intr = {"sdd": [pose["sdd"]], "delx": [pose["delx"]], "dely": [pose["delx"]], "x0": [0.0], "y0": [0.0],
        "height": 256, "width": 256}
request = DRRRenderRequest(rot=torch.tensor([pose["rot_deg"]], dtype=torch.float32),
                           xyz=torch.tensor([pose["xyz_mm"]], dtype=torch.float32), intrinsics=intr,
                           isocenter=torch.tensor([row["isocentre"]["point_mm"]], dtype=torch.float32),
                           orientation="AP", n_samples=500, orthographic=False)
with torch.inference_mode():
    result = render_drr(volume=torch.from_numpy(chu)[None], label=torch.from_numpy(clab.astype(np.int64))[None],
                        affine=torch.from_numpy(caff), request=request)
rendered = result.rendered[0].double().numpy()
image = result.images[0, 0].double().numpy()
image = (image - image.min()) / max(image.max() - image.min(), 1e-6)   # scale_minmax
np.save(os.path.join(out, "image.npy"), image)
np.save(os.path.join(out, "supports.npy"), np.stack([rendered[i] > 0 for i in (21, 22, 23)]))
print("render", image.shape, "support pixels L2 L3 L4:", [int((rendered[i] > 0).sum()) for i in (21, 22, 23)])

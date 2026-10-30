"""Our numpy reading of FleXray's camera against FleXray's own matrices and rays, for random views."""
import math, sys
import numpy as np
import torch
from fxr.drr.rendering import _make_rt_inv_per_view, _resolve_intrinsics
from nanodrr.drr.renderer import _make_tgt, _make_src

AP = np.array([[-1, 0, 0, 0], [0, 0, -1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], float)


def zxy(deg):
    a, b, c = np.radians(deg)
    rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, math.cos(b), -math.sin(b)], [0, math.sin(b), math.cos(b)]])
    ry = np.array([[math.cos(c), 0, math.sin(c)], [0, 1, 0], [-math.sin(c), 0, math.cos(c)]])
    return rz @ rx @ ry


rng = np.random.default_rng(7)
worst = {"rt": 0.0, "k": 0.0, "uv": 0.0}
for trial in range(200):
    rot = np.array([rng.uniform(-180, 180), rng.uniform(-30, 30), rng.uniform(-10, 10)])
    xyz = np.array([rng.uniform(-100, 100), rng.uniform(500, 900), rng.uniform(-100, 100)])
    iso = rng.uniform(-200, 200, 3)
    sdd, delx = rng.uniform(1150, 1250), rng.uniform(1.25, 2.25)
    h, w = 64, 48
    ortho = bool(trial % 5 == 0)
    rt = _make_rt_inv_per_view(torch.tensor([rot], dtype=torch.float64), torch.tensor([xyz], dtype=torch.float64),
                               orientation="AP", isocenter=torch.tensor(iso, dtype=torch.float64))[0].numpy()
    intr = _resolve_intrinsics({"sdd": [sdd], "delx": [delx], "dely": [delx], "x0": [0.0], "y0": [0.0],
                                "height": h, "width": w}, num_views=1, reference=torch.zeros(1, dtype=torch.float64),
                               orthographic_override=ortho)
    R = zxy(rot)
    pose = np.eye(4)
    pose[:3, :3] = R
    pose[:3, 3] = R @ xyz + iso
    ours = pose @ AP
    worst["rt"] = max(worst["rt"], float(np.abs(ours - rt).max()))
    fx = sdd / delx
    K = np.array([[fx, 0, w / 2.0], [0, fx, h / 2.0], [0, 0, 1]])
    worst["k"] = max(worst["k"], float(np.abs(np.linalg.inv(K) - intr.k_inv[0].numpy()).max()))
    # nanoDRR's rays for every pixel, in the world; a point along each ray must project to its pixel
    tgt = _make_tgt(intr.k_inv, intr.sdd, h, w, torch.device("cpu"), torch.float64)
    src = _make_src(ortho, tgt, intr.sdd)
    tgt_w = (rt[:3, :3] @ tgt[0].numpy().T).T + rt[:3, 3]
    src_w = (rt[:3, :3] @ src[0].numpy().T).T + rt[:3, 3]
    s = rng.uniform(0.2, 0.9, (tgt_w.shape[0], 1))
    pts = src_w + s * (tgt_w - src_w)
    to_cam = np.linalg.inv(ours)
    cam = (to_cam[:3, :3] @ pts.T).T + to_cam[:3, 3]
    if ortho:
        uv = np.stack([cam[:, 0] / delx + w / 2.0, cam[:, 1] / delx + h / 2.0], 1)
    else:
        uv = np.stack([fx * cam[:, 0] / cam[:, 2] + w / 2.0, fx * cam[:, 1] / cam[:, 2] + h / 2.0], 1)
    vv, uu = np.meshgrid(np.arange(h) + 0.5, np.arange(w) + 0.5, indexing="ij")
    want = np.stack([uu.ravel(), vv.ravel()], 1)
    worst["uv"] = max(worst["uv"], float(np.abs(uv - want).max()))
print({k: "%.3g" % v for k, v in worst.items()})

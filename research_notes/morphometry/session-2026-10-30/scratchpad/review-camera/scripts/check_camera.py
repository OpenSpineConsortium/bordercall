"""Hold morphoview.projection's camera to FleXray's own functions over random views:
the camera-to-world matrix, the intrinsics, nanoDRR's rays through every pixel, and that a point
on each ray projects back onto its pixel's centre."""
import sys

import numpy as np
import torch

sys.path.insert(0, sys.argv[1])
from morphoview import projection as PJ  # noqa: E402
from fxr.drr.rendering import _make_rt_inv_per_view, _resolve_intrinsics  # noqa: E402
from nanodrr.drr.renderer import _make_src, _make_tgt  # noqa: E402
import roma  # noqa: E402

rng = np.random.default_rng(7)
f64 = torch.float64
worst = {"zxy": 0.0, "rt": 0.0, "k": 0.0, "src": 0.0, "tgt": 0.0, "back": 0.0, "order": 0.0}
for trial in range(300):
    rot = rng.uniform([-180, -30, -45], [180, 30, 45])
    xyz = rng.uniform([-100, 500, -100], [100, 900, 100])
    iso = rng.uniform(-300, 300, 3)
    sdd = float(rng.uniform(1150, 1250))
    delx = float(rng.uniform(0.5, 2.25))
    dely = float(rng.uniform(0.5, 2.25)) if trial % 3 else None
    x0, y0 = (float(rng.uniform(-50, 50)), float(rng.uniform(-50, 50))) if trial % 4 == 1 else (0.0, 0.0)
    h, w = int(rng.integers(5, 40)), int(rng.integers(5, 40))
    ortho = bool(trial % 5 == 0)
    orient = ("AP", "PA", None)[trial % 3]
    view = PJ.View(rot_deg=rot, xyz_mm=xyz, isocentre_mm=iso, sdd=sdd, delx=delx, dely=dely, x0=x0, y0=y0,
                   height=h, width=w, orthographic=ortho, orientation=orient)
    cam = PJ.Camera(view)
    r = roma.euler_to_rotmat("ZXY", torch.tensor(np.radians(rot), dtype=f64)).numpy()
    worst["zxy"] = max(worst["zxy"], float(np.abs(r - PJ.zxy(rot)).max()))
    rt = _make_rt_inv_per_view(torch.tensor([rot], dtype=f64), torch.tensor([xyz], dtype=f64),
                               orientation=orient, isocenter=torch.tensor(iso, dtype=f64))[0].numpy()
    worst["rt"] = max(worst["rt"], float(np.abs(rt - cam.to_world).max()))
    intr = _resolve_intrinsics({"sdd": [sdd], "delx": [delx], "dely": [view.pixel_y], "x0": [x0], "y0": [y0],
                                "height": h, "width": w}, num_views=1, reference=torch.zeros(1, dtype=f64),
                               orthographic_override=ortho)
    worst["k"] = max(worst["k"], float(np.abs(intr.k_inv[0].numpy() - np.linalg.inv(cam.intrinsics)).max()))
    tgt = _make_tgt(intr.k_inv, intr.sdd, h, w, "cpu", f64)
    src = _make_src(ortho, tgt, intr.sdd)
    tgt_w = (tgt[0].numpy() @ rt[:3, :3].T + rt[:3, 3])
    src_c = src[0].numpy()
    if src_c.shape[0] == 1:
        src_c = np.repeat(src_c, h * w, axis=0)
    src_w = src_c @ rt[:3, :3].T + rt[:3, 3]
    s, t = cam.rays(cam.pixel_centres())
    worst["src"] = max(worst["src"], float(np.abs(s - src_w).max()))
    worst["tgt"] = max(worst["tgt"], float(np.abs(t - tgt_w).max()))
    frac = rng.uniform(0.05, 0.95, (h * w, 1))
    pts = src_w + frac * (tgt_w - src_w)
    got = cam.project(pts)
    worst["back"] = max(worst["back"], float(np.abs(got.uv - cam.pixel_centres()).max()))
    # the order of pixels: ray n is row n // w, column n % w
    n = np.arange(h * w)
    worst["order"] = max(worst["order"], float(np.abs(np.floor(got.uv[:, 1]) - n // w).max()
                                               + np.abs(np.floor(got.uv[:, 0]) - n % w).max()))
    assert got.in_beam.all(), (trial, got.depth.min(), got.depth.max())
print({k: "%.3g" % v for k, v in worst.items()})

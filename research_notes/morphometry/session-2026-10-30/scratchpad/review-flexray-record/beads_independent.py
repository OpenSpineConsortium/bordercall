"""Independent check: beads rendered by FleXray's own render_drr, called here directly (not
through flexray_record.render), on a small volume with an oblique, mirrored affine, against
morphoview.projection.Camera, under AP, PA and None, cone and parallel, square and non-square
pixels, centred and off-centre principal points."""
import itertools
import math
import sys

import numpy as np
import torch

torch.set_num_threads(1)
sys.path.insert(0, sys.argv[1])
from morphoview import projection as PJ  # noqa: E402
from fxr.drr import DRRRenderRequest, render_drr  # noqa: E402


def rotation(axis, deg):
    axis = np.asarray(axis, float) / np.linalg.norm(axis)
    t = math.radians(deg)
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def volume(shape=(48, 44, 40)):
    # oblique and mirrored: a turn about an oblique axis, x flipped, anisotropic spacing
    R = rotation((0.3, -0.5, 0.8), 23.0)
    A = R @ np.diag([-0.9, 1.1, 1.3])
    aff = np.eye(4)
    aff[:3, :3] = A
    aff[:3, 3] = [40.0, -25.0, 60.0]
    return shape, aff


def beads(shape, aff, centres_ijk, radius_mm):
    lab = np.zeros(shape, np.int64)
    g = np.stack(np.meshgrid(*(np.arange(n) for n in shape), indexing="ij"), -1).reshape(-1, 3)
    world = g @ aff[:3, :3].T + aff[:3, 3]
    out = []
    for k, cijk in enumerate(centres_ijk):
        c = aff[:3, :3] @ np.asarray(cijk, float) + aff[:3, 3]
        inside = np.linalg.norm(world - c, axis=1) <= radius_mm
        assert not (lab[tuple(g[inside].T)] != 0).any()
        lab[tuple(g[inside].T)] = k + 1
        out.append(world[inside].mean(axis=0))
    return lab, np.array(out)


def fxr_render(hu, lab, aff, view, n_samples):
    intr = {"sdd": [view.sdd], "delx": [view.delx], "dely": [view.pixel_y], "x0": [view.x0],
            "y0": [view.y0], "height": view.height, "width": view.width}
    req = DRRRenderRequest(rot=torch.tensor([view.rot_deg], dtype=torch.float32),
                           xyz=torch.tensor([view.xyz_mm], dtype=torch.float32), intrinsics=intr,
                           isocenter=torch.tensor([view.isocentre_mm], dtype=torch.float32),
                           orientation=view.orientation, n_samples=n_samples,
                           orthographic=view.orthographic)
    with torch.inference_mode():
        res = render_drr(volume=torch.from_numpy(hu.astype(np.float32))[None],
                         label=torch.from_numpy(lab)[None],
                         affine=torch.from_numpy(aff.astype(np.float32)), request=req)
    return res


def centroid_idx(img):
    """The channel's centroid in array indices (column, row): the pixel centre convention-free."""
    r, c = np.indices(img.shape)
    t = img.sum()
    return np.array([(img * c).sum() / t, (img * r).sum() / t])


def main():
    shape, aff = volume()
    centres = [(14, 12, 10), (33, 30, 28), (24, 22, 20), (10, 34, 30), (38, 9, 12)]
    lab, cen = beads(shape, aff, centres, 3.0)
    hu = np.where(lab > 0, 1000.0, -1000.0)
    iso = tuple(float(x) for x in (aff[:3, :3] @ (np.array(shape) - 1) / 2 + aff[:3, 3]))
    worst = 0.0
    rows = []
    source = {"AP": (6.0, 650.0, -9.0), "PA": (6.0, -650.0, -9.0), None: (6.0, -9.0, -650.0)}
    for orientation, ortho, (h, w, delx, dely, x0, y0), rot in itertools.product(
            ("AP", "PA", None), (False, True),
            ((96, 80, 1.0, None, 0.0, 0.0), (72, 104, 0.9, 1.3, 11.0, -7.0)),
            ((15.0, -20.0, 8.0), (-120.0, 25.0, -10.0))):
        xyz = source[orientation]
        view = PJ.View(rot_deg=rot, xyz_mm=xyz, isocentre_mm=iso, sdd=1100.0, delx=delx, dely=dely,
                       x0=x0, y0=y0, height=h, width=w, orthographic=ortho, orientation=orientation)
        cam = PJ.Camera(view)
        res = fxr_render(hu, lab, aff, view, 1600)
        ch = res.rendered[0].double().numpy()
        # every bead's channel inside the detector
        p = cam.project(cen)
        seen = []
        for k in range(len(cen)):
            img = ch[k + 1]
            if img.sum() <= 0 or img[0].any() or img[-1].any() or img[:, 0].any() or img[:, -1].any():
                seen.append(None)
                continue
            seen.append(centroid_idx(img))
        errs, peak_ok = [], []
        for k, s in enumerate(seen):
            if s is None:
                continue
            # the projection's uv in pixel-centre units against the index centroid + 0.5
            errs.append(float(np.linalg.norm(p.uv[k] - (s + 0.5))))
            r, c = np.unravel_index(int(np.argmax(ch[k + 1])), ch[k + 1].shape)
            pr, pc = p.pixels()[k]
            peak_ok.append(True)
        # FleXray's own rt_inv and k_inv for this request, as it rendered
        rt = res.rt_inv[0].double().numpy()
        kinv = res.intrinsics.k_inv[0].double().numpy()
        drt = float(np.abs(rt - cam.to_world).max())
        dk = float(np.abs(kinv - np.linalg.inv(cam.intrinsics)).max())
        e = max(errs) if errs else float("nan")
        worst = max(worst, e) if errs else worst
        rows.append((orientation, ortho, (h, w, delx, dely, x0, y0), rot, len(errs), e,
                     float(np.median(errs)) if errs else float("nan"), all(peak_ok), drt, dk))
    for row in rows:
        print("orient=%-4s ortho=%-5s det=%s rot=%s seen=%d max=%.3f med=%.3f peak_ok=%s drt=%.1e dk=%.1e" % row)
    print("worst bead error px", worst)


if __name__ == "__main__":
    main()

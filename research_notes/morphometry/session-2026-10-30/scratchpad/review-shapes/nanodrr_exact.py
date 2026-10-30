"""path_length(n_samples) against FleXray's render_drr on a volume of one attenuation everywhere,
where a label's channel is mu times the step times the count of its points."""
import sys, math
sys.path.insert(0, sys.argv[1])
import numpy as np, torch
from fxr.drr import DRRRenderRequest, render_drr
from morphoview import projection as PJ, shapes as SH

MU = 0.0573  # hu_to_mu(1000) with nanoDRR's defaults

def render64(hu, lab, aff, view, n):
    intr = {"sdd": [view.sdd], "delx": [view.delx], "dely": [view.pixel_y], "x0": [view.x0], "y0": [view.y0],
            "height": int(view.height), "width": int(view.width)}
    req = DRRRenderRequest(rot=torch.tensor([view.rot_deg], dtype=torch.float64),
                           xyz=torch.tensor([view.xyz_mm], dtype=torch.float64), intrinsics=intr,
                           isocenter=torch.tensor([view.isocentre_mm], dtype=torch.float64),
                           orientation=view.orientation, n_samples=int(n), orthographic=view.orthographic)
    with torch.inference_mode():
        res = render_drr(volume=torch.from_numpy(hu.astype(np.float64))[None],
                         label=torch.from_numpy(lab.astype(np.int64))[None],
                         affine=torch.from_numpy(np.asarray(aff, np.float64)), request=req)
    return res.rendered[0].numpy()

rng = np.random.default_rng(0)
shape = (26, 30, 22)
lab = np.zeros(shape, np.int64)
# an irregular blob well inside the grid, and a thin plate
g = np.indices(shape).transpose(1, 2, 3, 0).astype(float)
blob = np.linalg.norm((g - [13, 15, 11]) / [7, 9, 6], axis=-1) <= 1.0
blob &= rng.random(shape) > 0.15
lab[blob] = 1
lab[4:22, 5:7, 3:19] = 2
hu = np.full(shape, 1000.0)
# an oblique affine: rotated, anisotropic, one axis flipped
t = math.radians(23.0)
rot = np.array([[math.cos(t), -math.sin(t), 0], [math.sin(t), math.cos(t), 0], [0, 0, 1]])
aff = np.eye(4)
aff[:3, :3] = rot @ np.diag([0.7, -0.9, 1.3])
aff[:3, 3] = [-5.0, 12.0, 3.0]
centre = aff[:3, :3] @ (np.array(shape) / 2.0) + aff[:3, 3]

views = [
    PJ.View(rot_deg=(15.0, -20.0, 8.0), xyz_mm=(4.0, 600.0, -6.0), isocentre_mm=tuple(centre), sdd=1000.0,
            delx=0.6, dely=0.75, x0=5.0, y0=-3.0, height=70, width=64),
    PJ.View(rot_deg=(100.0, 5.0, -12.0), xyz_mm=(-2.0, 700.0, 9.0), isocentre_mm=tuple(centre), sdd=1100.0,
            delx=0.8, height=56, width=60, orthographic=True),
    PJ.View(rot_deg=(-30.0, 40.0, 0.0), xyz_mm=(0.0, -500.0, 0.0), isocentre_mm=tuple(centre), sdd=900.0,
            delx=0.5, height=64, width=64, orientation="PA"),
]
if __name__ == "__main__":
  for view in views:
        cam = PJ.Camera(view)
        for n in (500, 123):
            rendered = render64(hu, lab, aff, view, n)
            for value in (1, 2):
                vol = SH.Volume.from_labels(lab, aff, value, largest=False)
                ours = vol.path_length(cam, n_samples=n)
                theirs = rendered[value] / MU
                err = np.abs(ours - theirs)
                print("view %s n=%d label %d: max |ours - theirs| %.3g mm, silhouettes differ %d px, shadow %d px"
                      % ("ortho" if view.orthographic else view.orientation, n, value, err.max(),
                         int(((ours > 0) ^ (theirs > 0)).sum()), int((theirs > 0).sum())))

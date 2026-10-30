import sys, math
sys.path.insert(0, sys.argv[1]); sys.path.insert(0, sys.argv[2])
import numpy as np
from morphoview import projection as PJ, shapes as SH
from nanodrr_exact import render64, MU  # noqa: E402  (runs that file's checks first, quietly)

shape = (40, 36, 30)
lab = np.zeros(shape, np.int64)
lab[3:37, 4:32, 3:27] = 1
lab[10:30, 10:26, 8:22] = 2
hu = np.full(shape, 1000.0)
aff = np.diag([1.5, 1.4, 1.6, 1.0])
centre = aff[:3, :3] @ (np.array(shape) / 2.0)

def compare(name, view, n=300):
    cam = PJ.Camera(view)
    rendered = render64(hu, lab, aff, view, n)
    for value in (1, 2):
        vol = SH.Volume.from_labels(lab, aff, value, largest=False)
        try:
            ours = vol.path_length(cam, n_samples=n)
        except ValueError as e:
            print("%-48s label %d: refused (%s); FleXray's shadow %d px" % (name, value, e, int((rendered[value] > 0).sum())))
            continue
        theirs = rendered[value] / MU
        print("%-48s label %d: max |ours - theirs| %.3g mm, silhouettes differ %d of %d px"
              % (name, value, np.abs(ours - theirs).max(), int(((ours > 0) ^ (theirs > 0)).sum()), int((theirs > 0).sum())))

# the detector plane runs through the volume: source 600 mm from the centre, sdd 620
compare("cone, detector plane through the volume", PJ.View(rot_deg=(0, 0, 0), xyz_mm=(0, 600, 0), isocentre_mm=tuple(centre),
        sdd=620.0, delx=1.2, height=60, width=60))
# parallel rays whose source plane runs through the volume
compare("parallel, source plane through the volume", PJ.View(rot_deg=(10, 0, 0), xyz_mm=(0, 10, 0), isocentre_mm=tuple(centre),
        sdd=500.0, delx=1.2, height=60, width=60, orthographic=True))
# a detector smaller than the shadow, the principal point far off
compare("cone, shadow runs off the detector", PJ.View(rot_deg=(5, 5, 5), xyz_mm=(0, 400, 0), isocentre_mm=tuple(centre),
        sdd=900.0, delx=1.0, height=40, width=50, x0=30.0, y0=20.0))
# the source close to the volume, wide angles
compare("cone, source 60 mm from the centre", PJ.View(rot_deg=(0, 30, 0), xyz_mm=(0, 60, 0), isocentre_mm=tuple(centre),
        sdd=300.0, delx=2.0, height=64, width=64))
# the source inside the volume's box but outside the label
compare("cone, source inside the box", PJ.View(rot_deg=(0, 0, 0), xyz_mm=(0, 5, 0), isocentre_mm=tuple(centre),
        sdd=300.0, delx=2.0, height=64, width=64))

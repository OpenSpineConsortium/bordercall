"""The notch phantom's gate reach about the canal's line and its pedicles' notes, unpatched.

  PYTHONPATH=<bordercall> python probe_notch.py
"""
import numpy as np

from morphometry import body as BODY, canal as CANAL, pedicle as PED
from morphometry.tests import phantom as P
from morphometry.tests.test_morphometry import LUMBAR, built

v = P.lumbar(notch_w=5.0, notch_h=6.0, notch_d=4.0)
vert = built(P.straight(LUMBAR, v), LUMBAR, "L3")
B = vert.body_pts
xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
place, why = BODY.wall_window(vert, B, xc)
print("half %.2f reach %.2f window %.2f to %.2f" % place)
print("canal ap of the full rings:", np.round(sorted(s.ap for s in vert.full_rings()), 2))
out, flags, _ = PED.measures(vert, CANAL.body_span(vert))
print({k: round(x, 2) for k, x in out.items() if "sagittal" in k}, flags)

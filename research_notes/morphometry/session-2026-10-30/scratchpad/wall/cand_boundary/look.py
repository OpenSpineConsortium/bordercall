"""Print the wall pairs' midpoints of one cached config against the true wall, by layer."""
import math, os, pickle, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score as S
import cand as C
key = sys.argv[1]
rec = pickle.load(open("../cache/%s.pkl" % key, "rb"))
v, B, xc = rec["vert"], rec["vert"].body_pts, rec["xc"]
band = B[np.abs(B[:, 0] - xc) <= 3]
z0, z1 = band[:, 2].min(), band[:, 2].max()
lo, hi = z0 + 0.2 * (z1 - z0), z0 + 0.8 * (z1 - z0)
m, step_f = C.wall_pairs(v, xc, lo, hi)
t = math.tan(math.radians(S.wall_truth_in_frame(rec)))
got, info = C.slope(v, B, xc)
print(key, "truth deg %.2f got %.2f step %s" % (math.degrees(math.atan(t)), math.degrees(math.atan(got)), np.round(step_f, 3)), info)
# the true wall's offset: fit the intercept with the true slope
a_true = np.median(m[:, 1] - t * m[:, 2])
r = m[:, 1] - (a_true + t * m[:, 2])
order = np.argsort(m[:, 2])
for zq in np.unique(np.round(m[:, 2] / 0.5) * 0.5):
    sel = np.abs(m[:, 2] - zq) <= 0.25
    xs = np.round(m[sel, 0] - xc, 1)
    print("z %+6.2f n %2d  residual about the true slope: %s" % (zq, sel.sum(), " ".join("%+.2f" % x for x in r[sel][np.argsort(xs)])))

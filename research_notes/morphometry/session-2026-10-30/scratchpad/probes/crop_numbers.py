"""The crop view's numbers for the README: differing pixels per level, ends in and out."""
import sys
sys.path.insert(0, sys.argv[1])
import numpy as np  # noqa: E402
from morphoview import __main__ as MV  # noqa: E402
from morphoview.tests import test_projection as T  # noqa: E402

C = T.Crops
C.setUpClass()
mask = MV.read_mask(C.mask, "verse")
ours = MV.shadows(mask, C.crop, C.cam, list(T.RECORD["phantom"]["ids"]), T.RECORD["n_samples"])
for lv in T.RECORD["phantom"]["ids"]:
    theirs = T.support(C.rec, [lv])
    print(lv, "differ", int((ours[lv] ^ theirs).sum()), "support", int(theirs.sum()))
flags = [g[e + "_in_volume"] for g in C.got for e in "ab"]
print("ends in", flags.count("True"), "out", flags.count("False"), "of", len(flags))
print(C.said.strip())
far = [float(g[e + "_off_px"]) for g in C.got for e in "ab" if g[e + "_in_volume"] == "True"]
print("in-crop ends off the shadow: max %.2f" % max(far))

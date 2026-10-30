"""The command's shadows (morphoview.__main__.shadows) beside FleXray's channel supports."""
import json, sys
import numpy as np
sys.path.insert(0, sys.argv[1])
from morphoview import __main__ as MV
from morphoview import projection as PJ
C = sys.argv[2]
man = json.load(open(C + "/manifest.json"))
view = PJ.View.from_manifest(man["views"][0], man["blocks"]["detector"])
cam = PJ.Camera(view)
shade = MV.shadows(C + "/mask.nii.gz", "enhance", cam, ["L1", "L3", "L4"], man["blocks"]["ray_samples"])
fx = np.load(C + "/flexray_support.npz")
for lv in ("L1", "L3", "L4"):
    ours, theirs = shade[lv], fx[lv]
    print(lv, "ours", int(ours.sum()), "FleXray", int(theirs.sum()), "ours only", int((ours & ~theirs).sum()),
          "FleXray only", int((theirs & ~ours).sum()))

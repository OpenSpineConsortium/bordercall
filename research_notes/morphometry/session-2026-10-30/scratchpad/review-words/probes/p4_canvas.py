import json
import numpy as np
from morphoview import projection as PJ
from morphoview.tests import flexray_record as FR
R = json.load(open(FR.FIXTURE))
size = R["canvas"]["image_size"][0]
print("sizes", len(R["canvas"]["boxes"]), "spots", len(R["canvas"]["spots"]))
for box in R["canvas"]["boxes"]:
    h, w = box["height"], box["width"]
    (left, top), (right, bottom) = PJ.to_canvas([[0.0, 0.0], [w, h]], h, w, size)
    print(h, w, "ours (top, left, bottom, right) = (%.3f, %.3f, %.3f, %.3f)" % (top, left, bottom, right), "theirs", box["content_box"])
worst = 0.0
for spot in R["canvas"]["spots"]:
    want = PJ.to_canvas(spot["uv"], spot["height"], spot["width"], size)[0]
    for path, got in spot["canvas_uv"].items():
        d = float(np.abs(np.array(got) - want).max())
        worst = max(worst, d)
        print(spot["height"], spot["width"], path, "ours", want, "theirs", got, "diff %.5f" % d)
print("worst %.5f" % worst)

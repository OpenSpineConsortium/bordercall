import sys, json
import numpy as np
from morphoview.tests import test_projection as T
from morphoview.tests import flexray_record as FR
tmp, mask, lines, frames, rows = T.exported()
fr = T.read_csv(frames)
for f in fr:
    print({k: f[k] for k in f})
lab, aff, same = T.phantom()
print("same", same, lab.shape, aff.tolist())
ids = T.RECORD["phantom"]["ids"]
print(ids)
for lv, i in ids.items():
    idx = np.argwhere(lab == i)
    w = idx @ aff[:3, :3].T + aff[:3, 3]
    print(lv, w.min(axis=0), w.max(axis=0), w.mean(axis=0))
for v in T.RECORD["views"]:
    print(v["name"], v["view"])

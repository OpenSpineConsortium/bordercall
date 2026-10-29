"""The CT check of verse_ctcheck.py, held to one release: a mask under MASKS/verse19 is set beside the
CT of the same name in OSF node 923ap only, one under MASKS/verse20 beside node b2wxj only, so a name
published in both releases cannot pass on the other release's CT."""
import json, os, sys
import nibabel as nib
import numpy as np

NODE = {"verse19": "923ap", "verse20": "b2wxj"}
masks, headers = sys.argv[1], sys.argv[2]
cts = {}
for row in json.load(open(headers)):
    name = os.path.basename(row["path"])[:-len(".nii.gz")]
    cts.setdefault((row["node"], name), []).append(row)
same, differ, missing, several = 0, [], [], []
for release in sorted(os.listdir(masks)):
    for f in sorted(os.listdir(os.path.join(masks, release))):
        name = f[:-len("_seg.nii.gz")]
        h = nib.load(os.path.join(masks, release, f)).header
        shape, affine = [int(x) for x in h.get_data_shape()], np.array(h.get_best_affine())
        rows = cts.get((NODE[release], name), [])
        if len(rows) > 1:
            several.append(f"{release}/{f}")
        if not rows:
            missing.append(f"{release}/{f}")
        elif all(r.get("shape") == shape and np.allclose(np.array(r["affine"]), affine, atol=1e-3) for r in rows):
            same += 1
        else:
            differ.append(f"{release}/{f}")
print(json.dumps({"same": same, "differ": differ, "missing": missing, "several_cts_of_one_name": several}))

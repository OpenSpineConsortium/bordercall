"""Gather the 374 chosen VerSe masks, as their int16 copies or, where VerSe wrote integers
already, as published, into one folder for the grid, with a manifest and SHA256SUMS.

    python -I build_carry.py OUT.jsonl DL_DIR CHOSEN_DIR CONVERT_LOGS_GLOB TO_INT16_PY DEST
"""
import csv
import glob
import hashlib
import json
import os
import shutil
import sys

import nibabel as nib
import numpy as np


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main(out_jsonl, dl, chosen, logs_glob, script, dest):
    os.makedirs(os.path.join(dest, "masks"), exist_ok=False)
    converted = {}
    for p in glob.glob(logs_glob):
        for line in open(p):
            r = json.loads(line)
            if "src_bytes" in r:
                converted[r["id"]] = r
    rows = []
    for line in open(out_jsonl):
        r = json.loads(line)
        (name,) = r["files"]
        src = os.path.join(dl, r["release"], name)
        rec = r["files"][name]
        assert os.path.getsize(src) == rec["bytes"] and sha256(src) == rec["sha256"], r["id"]
        here = os.path.realpath(os.path.join(chosen, r["id"] + ".nii.gz"))
        out = os.path.join(dest, "masks", r["id"] + ".nii.gz")
        shutil.copyfile(here, out)
        img = nib.load(out)
        labels = sorted(int(v) for v in np.unique(np.asanyarray(img.dataobj)) if v)
        as_published = os.path.samefile(here, src)
        assert as_published or r["id"] in converted, r["id"]
        rows.append({"series": r["id"], "release": r["release"], "source_file": name,
                     "source_bytes": rec["bytes"], "source_sha256": rec["sha256"],
                     "file": "masks/" + r["id"] + ".nii.gz", "how": "as published" if as_published else "int16 copy",
                     "dtype_in": converted[r["id"]]["dtype_in"] if r["id"] in converted else str(img.get_data_dtype()),
                     "dtype": str(img.get_data_dtype()), "shape": "x".join(map(str, img.shape)),
                     "bytes": os.path.getsize(out), "sha256": sha256(out), "labels": " ".join(map(str, labels))})
    with open(os.path.join(dest, "MANIFEST.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    shutil.copyfile(script, os.path.join(dest, "to_int16.py"))
    print(len(rows), "masks;", sum(r["source_bytes"] for r in rows), "bytes as published,",
          sum(r["bytes"] for r in rows), "bytes here;", sum(1 for r in rows if r["how"] == "int16 copy"), "int16 copies")


if __name__ == "__main__":
    main(*sys.argv[1:7])

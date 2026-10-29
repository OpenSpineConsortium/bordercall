"""Write each chosen VerSe mask as an int16 NIfTI with the same affine, so that the measuring
code reads it without the float64 temporaries that would not fit in the container's memory.

The copy is lossless or it is not written: every voxel must be a whole number in int16's range
(checked exactly, slab by slab), and the reloaded copy must carry the same affine and shape.

    python -I to_int16.py OUT.jsonl DL_DIR CHOSEN_DIR LOG.jsonl
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import nibabel as nib
import numpy as np

# a mask whose float64 voxels pass this is converted alone: nibabel holds the decompressed bytes
# and the array together, and two of the largest at once do not fit in 15 GB
BIG_BYTES = 1.2e9


def chosen_files(out_jsonl, dl):
    for line in open(out_jsonl):
        r = json.loads(line)
        (name,) = r["files"]
        yield r["id"], os.path.join(dl, r["release"], name), r["files"][name]


def convert(job):
    sid, src, rec, dst = job
    if os.path.exists(dst):
        return {"id": sid, "skipped": "exists"}
    img = nib.load(src)
    data = np.asanyarray(img.dataobj)
    out = np.empty(data.shape, np.int16)
    bad = 0
    for k in range(0, data.shape[-1], 16):
        slab = data[..., k:k + 16]
        r = np.round(slab)
        bad += int(np.count_nonzero(slab != r))
        if r.size and (r.min() < 0 or r.max() > 32767):
            bad += 1
        out[..., k:k + 16] = r.astype(np.int16)
    affine = np.asarray(img.affine, float)
    del data
    if bad:
        return {"id": sid, "error": "%d voxels are not whole numbers in int16's range" % bad}
    hdr = img.header.copy()
    hdr.set_data_dtype(np.int16)
    hdr["scl_slope"], hdr["scl_inter"] = 1.0, 0.0
    new = nib.Nifti1Image(out, affine, header=hdr)
    new.set_qform(img.get_qform(), code=int(img.header["qform_code"]))
    new.set_sform(img.get_sform(), code=int(img.header["sform_code"]))
    tmp = dst + ".tmp.nii.gz"
    nib.save(new, tmp)
    back = nib.load(tmp)
    same = (back.shape == img.shape and np.array_equal(np.asarray(back.affine, float), affine)
            and np.array_equal(np.asarray(back.dataobj), out))
    if not same:
        os.remove(tmp)
        return {"id": sid, "error": "the reloaded copy differs in shape, affine or voxels"}
    os.replace(tmp, dst)
    labels = np.unique(out)
    return {"id": sid, "src_bytes": os.path.getsize(src), "src_sha256_listed": rec["sha256"],
            "dtype_in": str(img.get_data_dtype()), "labels": [int(v) for v in labels if v]}


def main(out_jsonl, dl, chosen, log):
    os.makedirs(chosen, exist_ok=True)
    jobs = []
    for sid, src, rec in chosen_files(out_jsonl, dl):
        dst = os.path.join(chosen, sid + ".nii.gz")
        if os.path.getsize(src) != rec["bytes"]:
            print("size differs from the record:", sid, flush=True)
            continue
        if np.issubdtype(nib.load(src).get_data_dtype(), np.integer):
            if not os.path.exists(dst):
                os.symlink(src, dst)
            continue
        jobs.append((sid, src, rec, dst))
    shape_bytes = lambda j: np.prod(nib.load(j[1]).shape)
    jobs.sort(key=shape_bytes, reverse=True)
    print("%d float masks to convert" % len(jobs), flush=True)
    big = [j for j in jobs if shape_bytes(j) * 8 > BIG_BYTES]
    small = [j for j in jobs if shape_bytes(j) * 8 <= BIG_BYTES]
    with open(log, "a") as f:
        for part, workers in ((big, 1), (small, 3)):
            with ProcessPoolExecutor(workers) as pool:
                for res in pool.map(convert, part):
                    f.write(json.dumps(res, sort_keys=True) + "\n")
                    f.flush()
                    print(res["id"], res.get("error", "ok"), flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:5])

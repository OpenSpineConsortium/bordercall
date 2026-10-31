"""Meng et al. 2020's spine model, from its two large pickles to NumPy files the branch `meshes` can
hold (bordercall #55; greg's direction of 2026-10-31 00:37 UTC, a latent shape model with a mesh
decoder in place of seven hand-picked measures).

fetch.py meng clones the model's repository and keeps every file one commit can hold. The model itself,
vertebra_smpl_v10.pkl (1.1 GB), and its probabilistic PCA, vertebra_smpl_v10_ppca_metadata.pkl
(729 MB), are larger, so meshes.yml runs this script after fetch.py on GitHub's runner:

    python3 extract_meng.py MODELS_DIR OUT

which writes

    OUT/DESCRIBE.md     every key of both pickles, its type, shape, dtype and bytes, and what was kept
    OUT/smpl/KEY.npy    each array of the model, the shape space's directions (shapedirs) cut to the
                        first MODES; the pose correctives (posedirs) are left out, since a phantom
                        places each bone rigidly
    OUT/ppca/KEY.npy    each array of the PCA, its loadings (C) cut to the first MODES columns

Floats over SINGLE bytes are kept as float32. A sparse matrix is kept as KEY.data.npy,
KEY.indices.npy, KEY.indptr.npy and KEY.shape.npy, its kind named in DESCRIBE.md. An array still over
LIMIT is split along its first axis into KEY.partNN.npy, and one over BUDGET is left out and named.

Both pickles were written by Python 2 with chumpy and scipy objects inside, and neither library is
needed: a stand-in class takes each such object's state, where a chumpy array keeps its values under
'x' and a compressed sparse matrix under 'data', 'indices' and 'indptr'. NumPy below 2 reads the
arrays of a Python 2 pickle as they were written.
"""
import hashlib
import math
import os
import pickle
import sys

import numpy as np

FOREIGN = ("chumpy", "scipy", "psbody", "smpl_webuser", "opendr", "cv2")
SINGLE = 16 * 1024 * 1024        # floats above this are kept as float32
LIMIT = 90 * 1024 * 1024         # one file, below GitHub's 100 MB refusal
BUDGET = 4 * LIMIT               # one array, parts and all; above it the array is named, not kept
MODES = 40                       # the directions kept of a shape space; Meng's variances fall sevenfold after 10
CUT = {"shapedirs": MODES, "C": MODES}
LEAVE = {"posedirs"}
PICKLES = {"smpl": "vertebra_smpl_v10.pkl", "ppca": "vertebra_smpl_v10_ppca_metadata.pkl"}


class Stand:
    """An object of a module this script does not import, holding the state its pickle gave it."""
    kind = ""
    args = ()
    state = None

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj.args = args
        return obj

    def __init__(self, *args, **kwargs):
        pass

    def __setstate__(self, state):
        if isinstance(state, tuple) and len(state) == 2 and isinstance(state[0], dict):
            state = state[0]
        self.state = state


class Loader(pickle.Unpickler):
    def find_class(self, module, name):
        if module.split(".")[0] in FOREIGN:
            return type(name, (Stand,), {"kind": "%s.%s" % (module, name)})
        return super().find_class(module, name)


def load(path):
    with open(path, "rb") as fh:
        return Loader(fh, encoding="latin1").load()


def leaves(value, prefix=""):
    """(key, value) for every value of nested dicts, keys joined by dots."""
    if isinstance(value, dict):
        for k in sorted(value, key=str):
            yield from leaves(value[k], "%s.%s" % (prefix, k) if prefix else str(k))
    else:
        yield prefix, value


def arrays_of(value):
    """What of one value can be kept: {suffix: array}, empty when nothing can."""
    if isinstance(value, np.ndarray):
        return {} if value.dtype == object else {"": value}
    if isinstance(value, (bool, int, float)):
        return {"": np.asarray(value)}
    if isinstance(value, (list, tuple)) and value and all(isinstance(v, (int, float)) for v in value):
        return {"": np.asarray(value)}
    if isinstance(value, Stand) and isinstance(value.state, dict):
        st = value.state
        if "x" in st:
            return arrays_of(st["x"])
        if {"data", "indices", "indptr"} <= set(st):
            shape = st.get("_shape", st.get("shape"))
            return {".data": np.asarray(st["data"]), ".indices": np.asarray(st["indices"]),
                    ".indptr": np.asarray(st["indptr"]), ".shape": np.asarray(shape)}
    return {}


def what_it_is(value):
    if isinstance(value, np.ndarray):
        return "ndarray %s %s, %d bytes" % (value.dtype, value.shape, value.nbytes)
    if isinstance(value, Stand):
        keys = sorted(value.state) if isinstance(value.state, dict) else type(value.state).__name__
        return "%s, state %s" % (value.kind, keys)
    text = repr(value)
    return "%s %s" % (type(value).__name__, text if len(text) <= 80 else text[:77] + "...")


def shaped(key, arr):
    """The array as it is kept: cut where the key is a shape space, float32 where large."""
    base = key.split(".")[-1]
    if base in CUT and arr.ndim >= 2 and arr.shape[-1] > CUT[base]:
        arr = arr[..., :CUT[base]]
    if arr.dtype.kind == "f" and arr.nbytes > SINGLE:
        arr = arr.astype(np.float32)
    return np.asarray(arr, order="C")         # keeps a 0-d value 0-d, as ascontiguousarray does not


def keep(folder, name, arr):
    """Save one array, split along its first axis when one file cannot hold it; the files written."""
    os.makedirs(folder, exist_ok=True)
    if arr.nbytes <= LIMIT or arr.ndim == 0:
        path = os.path.join(folder, name + ".npy")
        np.save(path, arr)
        return [path]
    parts = math.ceil(arr.nbytes / LIMIT)
    paths = []
    for i, chunk in enumerate(np.array_split(arr, parts, axis=0)):
        paths.append(os.path.join(folder, "%s.part%02d.npy" % (name, i)))
        np.save(paths[-1], np.ascontiguousarray(chunk))
    return paths


def reduce_one(label, path, out):
    """Every key of one pickle kept or named; the lines DESCRIBE.md gives it."""
    lines = ["## %s: %s" % (label, os.path.basename(path)), "",
             "%d bytes, md5 %s" % (os.path.getsize(path), md5_of(path)), "",
             "| key | what it is | kept |", "|---|---|---|"]
    for key, value in leaves(load(path)):
        kept = []
        if key.split(".")[-1] in LEAVE:
            kept = ["left out: not needed"]
        for suffix, arr in arrays_of(value).items() if not kept else []:
            arr = shaped(key, arr)
            if arr.nbytes > BUDGET:
                kept.append("left out: %d bytes as kept" % arr.nbytes)
                continue
            files = keep(os.path.join(out, label), key + suffix, arr)
            kept.append("%s %s %s in %d file%s" % (key + suffix, arr.dtype, arr.shape, len(files),
                                                  "" if len(files) == 1 else "s"))
        lines.append("| %s | %s | %s |" % (key, what_it_is(value), "; ".join(kept) or "nothing to keep"))
    return lines + [""]


def md5_of(path):
    digest = hashlib.md5()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 22), b""):
            digest.update(block)
    return digest.hexdigest()


def main(argv):
    if len(argv) != 3:
        raise SystemExit(__doc__)
    models, out = argv[1], argv[2]
    lines = ["# Meng et al. 2020's spine model, reduced", "",
             "Written by research_notes/open-vertebra-meshes/extract_meng.py on GitHub's runner, from",
             "gitlab.inria.fr/spine/spine_model. Arrays are .npy files; float32 where the original was",
             "float64 and over %d bytes; shapedirs and C cut to their first %d modes." % (SINGLE, MODES), ""]
    for label, name in PICKLES.items():
        lines += reduce_one(label, os.path.join(models, name), out)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "DESCRIBE.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main(sys.argv)

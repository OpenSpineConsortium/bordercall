"""Bring the open vertebra models of this note onto the branch `meshes`, for templates (#55).

greg's word of 2026-10-31 00:09 UTC cleared both for use, the non-commercial one included: "i dont
care about licenses use these if they help". This cloud container's proxy refuses zenodo.org and
gitlab.inria.fr, so .github/workflows/meshes.yml runs this script on GitHub's runner and commits what
it writes to the branch `meshes`, which a session then fetches like any other branch.

    python3 fetch.py list  OUT     what each source holds, names and sizes, written to OUT/LISTING.md
    python3 fetch.py upf   OUT     the 42 patients' surface meshes of the UPF repository (Zenodo 8108354),
                                   with both records' per-patient sheets (Descriptive_List*.xlsx)
    python3 fetch.py meng  OUT     the full spine model of Meng et al. 2020 (gitlab.inria.fr/spine/spine_model)

A file larger than GitHub's limit for one file is listed and left out, never split; extract_meng.py
reduces Meng's two large pickles. UPF's STL files are kept as indexed meshes (OUT/upf/.../NAME.npz:
v, float32 millimetres as written, and f, int32), a third of the STL's bytes. The standard library,
NumPy for the meshes, and git and an extractor of RAR archives from the runner.
"""
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import urllib.request

ZENODO = "https://zenodo.org/api/records/%s"
UPF_STL, UPF_FE = "8108354", "10994164"
MENG_GIT = "https://gitlab.inria.fr/spine/spine_model.git"
FILE_LIMIT = 95 * 1024 * 1024          # below GitHub's 100 MB refusal
UPF_WANTED = "42"                      # the archive of the 42 patients' meshes; its name holds the count


def zenodo_files(record):
    with urllib.request.urlopen(ZENODO % record, timeout=60) as r:
        meta = json.load(r)
    return meta.get("metadata", {}).get("title", ""), [
        {"key": f["key"], "size": int(f["size"]), "checksum": f.get("checksum", ""),
         "url": f["links"]["self"]} for f in meta.get("files", [])]


def download(url, path, checksum=""):
    digest = hashlib.md5()
    with urllib.request.urlopen(url, timeout=600) as r, open(path, "wb") as out:
        for block in iter(lambda: r.read(1 << 20), b""):
            digest.update(block)
            out.write(block)
    if checksum.startswith("md5:") and digest.hexdigest() != checksum[4:]:
        raise SystemExit("md5 mismatch for %s" % url)


def clone_meng(where):
    if os.path.isdir(where):
        return 0
    return subprocess.call(["git", "clone", "--depth", "1", MENG_GIT, where])


def sizes_under(root):
    rows = []
    for base, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d != ".git"]
        for n in names:
            p = os.path.join(base, n)
            rows.append((os.path.relpath(p, root), os.path.getsize(p)))
    return sorted(rows)


def listing(out):
    lines = ["# What the open vertebra models hold", "",
             "Written by research_notes/open-vertebra-meshes/fetch.py on GitHub's runner.", ""]
    for record in (UPF_STL, UPF_FE):
        try:
            title, files = zenodo_files(record)
        except Exception as e:                       # the listing says what failed and goes on
            lines += ["## Zenodo %s" % record, "", "not read: %s" % e, ""]
            continue
        lines += ["## Zenodo %s: %s" % (record, title), "", "| file | bytes |", "|---|---|"]
        lines += ["| %s | %d |" % (f["key"], f["size"]) for f in files] + [""]
    lines += ["## %s" % MENG_GIT, ""]
    rc = clone_meng("/tmp/meng")
    if rc:
        lines += ["git clone failed with %d" % rc, ""]
    else:
        lines += ["| file | bytes |", "|---|---|"] + ["| %s | %d |" % r for r in sizes_under("/tmp/meng")] + [""]
    write(out, "LISTING.md", "\n".join(lines))


def upf(out):
    _, files = zenodo_files(UPF_STL)
    wanted = [f for f in files if UPF_WANTED in f["key"] and f["key"].lower().endswith(".rar")
              and f["size"] <= 2 * 1024 ** 3]
    if not wanted:
        raise SystemExit("no archive of the 42 patients in Zenodo %s: %s" % (UPF_STL, [f["key"] for f in files]))
    sheets = [f for f in files + zenodo_files(UPF_FE)[1] if f["key"].lower().endswith(".xlsx")]
    for f in sheets:
        os.makedirs(os.path.join(out, "upf", "sheets"), exist_ok=True)
        download(f["url"], os.path.join(out, "upf", "sheets", f["key"]), f["checksum"])
    os.makedirs("/tmp/upf", exist_ok=True)
    for f in wanted:
        archive = os.path.join("/tmp/upf", f["key"])
        download(f["url"], archive, f["checksum"])
        unpack(archive, "/tmp/upf/x")
    keep(out, "upf", "/tmp/upf/x", as_mesh=True)


def unpack(archive, where):
    """Extract a RAR archive with the first extractor the runner has that takes it."""
    os.makedirs(where, exist_ok=True)
    tries = [["7z", "x", "-y", "-o" + where, archive], ["7zz", "x", "-y", "-o" + where, archive],
             ["unrar", "x", "-o+", archive, where + "/"], ["bsdtar", "-xf", archive, "-C", where]]
    for cmd in tries:
        if shutil.which(cmd[0]) and subprocess.call(cmd, stdout=subprocess.DEVNULL) == 0:
            return
    raise SystemExit("no extractor on the runner opened %s" % archive)


def read_stl(path):
    """An STL file's triangles, binary or ASCII, as an (n, 3, 3) float32 array."""
    import numpy as np
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) >= 84:
        n = struct.unpack_from("<I", data, 80)[0]
        if len(data) == 84 + 50 * n:
            record = np.dtype([("normal", "<f4", (3,)), ("v", "<f4", (3, 3)), ("attribute", "<u2")])
            return np.frombuffer(data, dtype=record, count=n, offset=84)["v"].copy()
    words = data.decode("ascii", "replace").split()
    xyz = [words[i + 1:i + 4] for i, w in enumerate(words) if w == "vertex"]
    return np.asarray(xyz, dtype=np.float32).reshape(-1, 3, 3)


def indexed(triangles):
    """The shared vertices and the faces of a triangle soup."""
    import numpy as np
    v, inverse = np.unique(triangles.reshape(-1, 3), axis=0, return_inverse=True)
    return v, inverse.reshape(-1, 3).astype(np.int32)


def keep_mesh(source, dest):
    """An STL kept as an indexed mesh, NAME.npz in place of NAME.stl."""
    import numpy as np
    v, f = indexed(read_stl(source))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    np.savez_compressed(os.path.splitext(dest)[0] + ".npz", v=v, f=f)


def meng(out):
    if clone_meng("/tmp/meng"):
        raise SystemExit("git clone of %s failed" % MENG_GIT)
    keep(out, "meng", "/tmp/meng")


def keep(out, name, root, as_mesh=False):
    """Copy every file under root into OUT/name, leaving out what one commit cannot hold; with
    as_mesh, an STL is kept as an indexed mesh instead."""
    left = []
    for rel, size in sizes_under(root):
        dest = os.path.join(out, name, rel)
        if as_mesh and rel.lower().endswith(".stl"):
            keep_mesh(os.path.join(root, rel), dest)
            continue
        if size > FILE_LIMIT:
            left.append("| %s | %d |" % (rel, size))
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(os.path.join(root, rel), dest)
    note = ["# Left out of %s" % name, "", "Files over %d bytes, which one commit cannot hold." % FILE_LIMIT, "",
            "| file | bytes |", "|---|---|"] + left
    write(os.path.join(out, name), "LEFT_OUT.md", "\n".join(note))


def write(folder, name, text):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(text + "\n")


def main(argv):
    if len(argv) != 3 or argv[1] not in ("list", "upf", "meng"):
        raise SystemExit(__doc__)
    {"list": listing, "upf": upf, "meng": meng}[argv[1]](argv[2])


if __name__ == "__main__":
    main(sys.argv)

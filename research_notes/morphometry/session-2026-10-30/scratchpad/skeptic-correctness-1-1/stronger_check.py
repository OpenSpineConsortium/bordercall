"""Run the export on the test's own phantom with the commit's code, then ask of the written frames
what the builders placed there (the checks the finding proposes), on the frames as written and on
the four mutants' frames made from them, to see whether a test that bites is possible at all."""
import csv
import math
import os
import shutil
import subprocess
import sys

import nibabel as nib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "base")
sys.path.insert(0, BASE)

from morphometry.tests import phantom as P  # noqa: E402
from morphometry.tests import test_lines_export as T  # noqa: E402
from scanimport import geometry as G  # noqa: E402

OUT = os.path.join(HERE, "stronger")


def export() -> None:
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    masks = os.path.join(OUT, "masks")
    os.makedirs(masks)
    T.masks(masks)
    subprocess.run([sys.executable, "-m", "morphometry", "run", "--masks", masks, "--scheme", "verse",
                    "--out", os.path.join(OUT, "out"), "--workers", "1", "--lines"], cwd=BASE, check=True,
                   env={**os.environ, "PYTHONPATH": BASE})


def read(name: str) -> list:
    with open(os.path.join(OUT, "out", name), newline="") as fh:
        return list(csv.DictReader(fh))


def frame_of(r: dict) -> G.Frame:
    vec = lambda p: np.array([float(r[p + a]) for a in "xyz"])  # noqa: E731
    return G.Frame(vec("o"), vec("ex"), vec("ey"), vec("ez"))


def centroid(study: str, level: str) -> np.ndarray:
    img = nib.load(os.path.join(OUT, "masks", study + ".nii.gz"))
    lab = np.asarray(img.dataobj)
    idx = np.argwhere(lab == P.LEVEL_IDS[level]).astype(float)
    return (img.affine[:3, :3] @ idx.T).T.mean(0) + img.affine[:3, 3]


def ends(r: dict) -> np.ndarray:
    return np.array([[float(r[p + a]) for a in "xyz"] for p in "ab"])


def problems(f: G.Frame, study: str, level: str, lines: dict) -> list:
    """What the builders placed in the frame and the frame does not show."""
    out = []
    o_err = float(np.linalg.norm(f.origin - centroid(study, level)))
    if o_err > 0.01:
        out.append("origin %.2f mm off the label's voxel centroid" % o_err)
    for key, same, along in (("h_mid", [0], 2), ("body_w_mid", [1, 2], 0), ("body_d_mid", [0, 2], 1)):
        a, b = f.local(ends(lines[key]))
        for k in same:
            if abs(a[k] - b[k]) > 0.01:
                out.append("%s ends differ by %.3f mm in local %s" % (key, abs(a[k] - b[k]), "xyz"[k]))
        if b[along] - a[along] <= 0:
            out.append("%s runs the wrong way along local %s" % (key, "xyz"[along]))
    a, b = f.local(ends(lines["body_d_mid"]))
    if 0.5 * (a[1] + b[1]) <= 0:
        out.append("the body's middle is not at positive local y")
    return out


def turned_about_x(f: G.Frame, deg: float) -> G.Frame:
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return G.Frame(f.origin, f.ex, c * f.ey + s * f.ez, -s * f.ey + c * f.ez)


def main() -> None:
    if "--again" not in sys.argv:
        export()
    frames = read("frames.csv")
    lines = read("lines.csv")
    for r in frames:
        study, level = r["study"], r["level"]
        if (study, level) == ("0002", "L4"):
            continue                      # the cut level draws no line its rows do not hold
        mine = {ln["key"]: ln for ln in lines if (ln["study"], ln["level"], ln["part"]) == (study, level, "")}
        f = frame_of(r)
        for name, g in (("as written", f),
                        ("m2 5 deg about x", turned_about_x(f, 5.0)),
                        ("m7 origin at 0", G.Frame(0.0 * f.origin, f.ex, f.ey, f.ez)),
                        ("m8 -x -y", G.Frame(f.origin, -f.ex, -f.ey, f.ez)),
                        ("m3 -x -z", G.Frame(f.origin, -f.ex, f.ey, -f.ez))):
            got = problems(g, study, level, mine)
            print("%s %s %-18s %s" % (study, level, name, "; ".join(got) if got else "no problem"))


if __name__ == "__main__":
    main()

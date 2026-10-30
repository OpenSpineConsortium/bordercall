"""Which way each exported line runs from a to b in its vertebra's frame, on the test phantom's L3,
beside the end names autoanatomist/specs.py gives the seven chords and the two extras."""
import os
import tempfile

import numpy as np

from morphometry import __main__ as RUN
from morphometry import measure as M
from morphometry.tests import test_lines_export as T

SPEC_ENDS = {"endplate": ("right", "left"), "endplate_depth": ("posterior", "anterior"),
             "endplate_lower": ("right", "left"), "endplate_lower_depth": ("posterior", "anterior"),
             "h_post": ("superior", "inferior"), "canal_w": ("right", "left"), "canal_ap": ("posterior", "anterior"),
             "tp_span": ("right", "left"), "spinous_length": ("canal", "tip")}
WORDS = {"x": ("left", "right"), "y": ("posterior", "anterior"), "z": ("inferior", "superior")}


def main():
    folder = tempfile.mkdtemp()
    T.masks(folder)
    kept = {}
    M.measure_file(os.path.join(folder, "0001.nii.gz"), "verse", "0001", keep=kept)
    lines, frames, _ = RUN.study_lines("0001", kept)
    f = kept["verts"]["L3"].frame
    for r in lines:
        if r["level"] != "L3" or r["part"]:
            continue
        d = np.array([r["bx"] - r["ax"], r["by"] - r["ay"], r["bz"] - r["az"]])
        local = np.array([d @ f.ex, d @ f.ey, d @ f.ez])
        k = int(np.argmax(np.abs(local)))
        axis = "xyz"[k]
        a_end, b_end = WORDS[axis] if local[k] > 0 else WORDS[axis][::-1]
        spec = SPEC_ENDS.get(r["key"])
        print("%-24s a=%-9s b=%-9s along %s (share %.2f)%s" % (
            r["key"], a_end, b_end, axis, abs(local[k]) / np.linalg.norm(d),
            "   specs.py names (%s, %s)" % spec if spec else ""))


if __name__ == "__main__":
    main()

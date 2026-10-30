"""Which of PR 45's seven chords (EPWu, EPDu, EPWl, EPDl, VBHp, SCW, SCD: endplate, endplate_depth,
endplate_lower, endplate_lower_depth, h_post, canal_w, canal_ap) get a line in the export."""
import math
import os
import tempfile

from morphometry import __main__ as RUN
from morphometry import measure as M
from morphometry.tests import test_lines_export as T

SEVEN = ("endplate", "endplate_depth", "endplate_lower", "endplate_lower_depth", "h_post", "canal_w", "canal_ap")


def main():
    folder = tempfile.mkdtemp()
    T.masks(folder)
    kept = {}
    rows = M.measure_file(os.path.join(folder, "0001.nii.gz"), "verse", "0001", keep=kept)
    lines, frames, flags = RUN.study_lines("0001", kept)
    drawn = {r["key"]: r["status"] for r in lines if r["level"] == "L3" and r["part"] == ""}
    vals = {r["key"]: r["value"] for r in rows if r["level"] == "L3"}
    for k in SEVEN:
        print("%-22s row value %-10s line: %s" % (k, ("%.3f" % vals[k]) if isinstance(vals.get(k), float) else vals.get(k),
                                                  drawn.get(k, "none")))
    print("line keys at L3:", sorted(drawn))
    have = {k for k, v in vals.items() if isinstance(v, float) and math.isfinite(v)}
    print("keys with a value and no line at L3:", sorted(have - set(drawn)))


if __name__ == "__main__":
    main()

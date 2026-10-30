"""Compare the pedicles' lines drawn on the measure's own reading with the lines read again,
on the test module's two phantoms (whole column and the column cut through L4's body)."""
import math
import os
import sys
import tempfile

import numpy as np

from morphometry import measure as M
from morphometry.tests import test_lines_export as T
from morphoview import lines as LN


def same(x, y):
    """Bitwise for floats (NaN equal to NaN)."""
    if isinstance(x, float) and isinstance(y, float):
        return (math.isnan(x) and math.isnan(y)) or x == y
    return x == y


def compare(path, study):
    kept = {}
    M.measure_file(path, "verse", study, keep=kept)
    for lv, v in kept["verts"].items():
        ped, vals = kept["peds"][lv], kept["values"][lv]
        again = LN.checked(LN.vertebra_lines(v, ped), vals)
        reused = LN.checked(LN.vertebra_lines(v, ped, vals), vals)
        ka, kr = [ln.key for ln in again], [ln.key for ln in reused]
        touching = bool(v.touching.any())
        print("%s %s touching=%s lines again=%d reused=%d" % (study, lv, touching, len(ka), len(kr)))
        if ka != kr:
            print("  keys only read again:", sorted(set(ka) - set(kr)), " only reused:", sorted(set(kr) - set(ka)))
        byk = {ln.key: ln for ln in reused}
        for x in again:
            y = byk.get(x.key)
            if y is None:
                print("  missing in reused: %s value=%r status=%r" % (x.key, x.value, x.status))
                continue
            diffs = []
            if not same(float(x.value), float(y.value)):
                diffs.append("value %r vs %r" % (x.value, y.value))
            if x.status != y.status:
                diffs.append("status %r vs %r" % (x.status, y.status))
            if not (np.array_equal(x.a, y.a) and np.array_equal(x.b, y.b)):
                diffs.append("ends differ")
            if diffs:
                print("  %s: %s" % (x.key, "; ".join(diffs)))


def main():
    folder = tempfile.mkdtemp()
    T.masks(folder)
    for study in ("0001", "0002"):
        compare(os.path.join(folder, study + ".nii.gz"), study)


if __name__ == "__main__":
    main()

"""The mask-free mode's error table in README.md, from synthetic CTs of known size:

    python -m scanimport.tests.bench_mask_free                       # every phantom, Markdown rows to stdout
    python -m scanimport.tests.bench_mask_free "default"             # one
    python -m scanimport.tests.bench_mask_free --density "thin dense"  # with the density trial's columns

Each phantom is three vertebrae (tests/phantom.py, hu_column), so one body lies between two
discs; each row gives that body's chord minus the truth, in millimetres, by the half-maximum edge
alone and with the blurred-step fit (edges.py). With --density, two more columns give the errors
with the cortical density fitted per kind of surface as well (edges.fit_density, the trial
edges.py describes and does not use) and the densities it chose, so that trial can be run again.
No random number enters but the phantom's noise, drawn from a fixed seed, so the table comes out
the same on every run on the same machine and numpy, scipy and BLAS build (intensity.py says
what may differ in the last bits elsewhere).
"""
import re
import sys
import time
from typing import List

import numpy as np

from scanimport import intensity as I
from scanimport.readers import Volume
from scanimport.tests import phantom as P

SEVEN = ("endplate", "endplate_lower", "endplate_depth", "endplate_lower_depth", "h_post", "canal_w", "canal_ap")
CERVICAL = P.Shape(W=17, D=15, H=13, CW=24, CD=14, T=3, TP=52, LS=14)
PHANTOMS = {
    "default: 0.9 x 0.9 x 1.4 mm, column tilted 18 degrees, blur 0.6 mm, 1 mm cortex of 800 HU": {},
    "aligned 1 mm voxels": dict(tilt=((1, 0, 0), 0.0), grid_turn=((0, 0, 1), 0.0), spacing=(1, 1, 1)),
    "osteoporotic: trabecular 100 HU, 2 mm slices, blur 1.0, noise 25 HU":
        dict(trabecular=100.0, noise_hu=25.0, blur_mm=1.0, spacing=(0.7, 0.7, 2.0)),
    "3 mm slices, tilted 10 degrees": dict(tilt=((1, 0, 0), 10.0), spacing=(0.7, 0.7, 3.0), grid_turn=((0, 0, 1), 0.0)),
    "cervical body, 0.6 x 0.6 x 1 mm": dict(shape=CERVICAL, gap=18.0, spacing=(0.6, 0.6, 1.0)),
    "clinical blur 1.2 mm, noise 15 HU": dict(blur_mm=1.2, noise_hu=15.0),
    "thin dense cortex, 0.5 mm of 1,500 HU, blur 1.0, noise 15": dict(blur_mm=1.0, cortex=1500.0, cortex_mm=0.5, noise_hu=15.0),
    "thick light cortex, 2 mm of 900 HU, blur 1.2, noise 15": dict(blur_mm=1.2, cortex=900.0, cortex_mm=2.0, noise_hu=15.0),
}
HEADER = "| Phantom | Half-maximum only: EPWu EPWl EPDu EPDl VBHp SCW SCD | With the blurred-step fit |"
DENSITY_HEADER = " With the density fitted too | Densities chosen (HU) |"


def truth(shape: P.Shape) -> dict:
    return dict(zip(SEVEN, (shape.W, shape.W, shape.D, shape.D, shape.H, shape.CW, shape.CD)))


def densities_chosen(methods: dict) -> str:
    """The density each kind of surface was fitted at, read from the chords' methods."""
    pattern = r"(\w+) [+-]\d+\.\d+ mm, blur SD [\d.]+ mm, cortex fitted at (\d+) HU"
    found = re.findall(pattern, " ".join(methods.values()))
    return ", ".join("%s %s" % kd for kd in sorted(set(found))) or "no believable fit"


def cells(hu: np.ndarray, affine: np.ndarray, want: dict, density: bool = False) -> List[str]:
    """One phantom's cells: the errors by the half-maximum edge, with the fit, and, with density,
    with the density fitted too and the densities chosen; or why nothing was measured."""
    out = []
    modes = [(False, False), (True, False)] + ([(True, True)] if density else [])
    for fit, fit_density in modes:
        vol = Volume(hu=hu, affine=affine, source="phantom")
        bodies, found = I.measure(vol, fit_edges=fit, fit_density=fit_density)
        measured = [b for b in bodies if b.values]
        if not measured:
            return ["nothing measured: %s" % "; ".join(found.problems)]
        out.append(" ".join("%+.2f" % (measured[0].values[m] - want[m]) for m in SEVEN))
    if density:
        out.append(densities_chosen(measured[0].methods))
    return out


def row(name: str, kw: dict, density: bool = False) -> str:
    hu, affine = P.hu_column(n=3, **kw)
    return "| %s | %s |" % (name, " | ".join(cells(hu, affine, truth(kw.get("shape", P.Shape())), density)))


def main(argv) -> None:
    density = "--density" in argv
    names = [a for a in argv if not a.startswith("--")]
    print(HEADER + (DENSITY_HEADER if density else ""))
    print("| --- | --- | --- |" + (" --- | --- |" if density else ""))
    for name, kw in PHANTOMS.items():
        if names and not any(n in name for n in names):
            continue
        t = time.time()
        print(row(name, kw, density), flush=True)
        print("  (%.0f s)" % (time.time() - t), file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])

"""The benchmarks the morphometrics are held to, each against a truth of its own kind, and the
figures that show them.

- The phantom (python -m morphobench phantom): L2 to L4 drawn from shapes whose every measure is
  known (morphometry/tests/phantom.py, truth), on four voxel grids from 0.8 by 0.8 by 1 mm to 0.98
  by 0.98 by 5 mm, the column tilted 0, 10 and 20 degrees against the scanner and the grid turned
  0 and 11 degrees about the scanner's axis; each measure's error is its value less the truth.
- The mask's edge (python -m morphobench maskedge-phantom): maskedge on the same phantom with a CT
  drawn from it, the exact mask and the mask grown and shrunk by one voxel, beside maskedge's rows
  from the three ENHANCE.PET CTs.
- Thick slices: morphometry's thicken on three thin studies, each measure read again on every
  second and every fourth slice, so a reader sees what a clinical 2.5 or 5 mm scan does to it.
- The papers: the run's comparison with the paper tables, ours by level beside each paper's mean.
- VerSe: the readers' Genant grades set against our height ratios, measured in a thread with full
  network access, its aggregates only.

    python -m morphobench phantom --out records/.../phantom-truth.csv [--workers 1]
    python -m morphobench maskedge-phantom --out records/.../maskedge-phantom.csv
    python -m morphobench figures --records records/morphometry-2026-10-29 --out records/.../figures

Nothing here reads a CT or a mask that is not given to it, and nothing it writes holds more than
aggregates of the studies.
"""

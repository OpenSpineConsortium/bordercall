"""Restate the research note's passages on the posterior wall and the canal's line."""
import sys

PATH = sys.argv[1] + "/research_notes/morphometry/README.md"


def swap(text, old, new):
    assert text.count(old) == 1, old[:60]
    return text.replace(old, new)


t = open(PATH).read()
t = swap(t,
         "and those on a grid within a few degrees of the vertebra's frame, where the posterior wall's slope reads 1.8 "
         "to 4.2 degrees off and the angle 2.5 to 3.4 high (body.posterior_wall_slope, to be traced next; the "
         "end-plates' inclinations take the same error).",
         "and those on a grid within a few degrees of the vertebra's frame, where the posterior wall's slope, as it "
         "was then read, stood 1.8 to 4.2 degrees off and the angle 2.5 to 3.4 high (the next item).")
t = swap(t,
         "pedicle.py's docstring, handoff.md's pass of 30 October).\n",
         "pedicle.py's docstring, handoff.md's pass of 30 October).\n"
         "- The posterior wall's slope, which the end-plates' inclinations, the pedicles' sagittal angles and the "
         "spinous process's angle are all taken against, followed the lattice's staircase: read as the hindmost body "
         "voxel of each layer, over 98 phantom vertebrae on seven grids at 1 and 2.5 mm slices it erred up to 4.14 "
         "degrees on 1 mm slices and 5.66 on 2.5 mm, worst on a grid 2 degrees off the vertebra's frame, and a "
         "basivertebral notch 4 mm deep put it 18.2 degrees off. It is now read on the scan's own lattice from the "
         "label (body.posterior_wall): the last bone of each scan line in a band across the midline, a trimmed and "
         "reweighted fit of a gently curved surface through those edges, and its slope clamped into the range of "
         "slopes whose surfaces part the label's bone from air. On the same vertebrae it errs at most 0.35 and 0.79 "
         "degrees, and 0.20 past the notch; where it is not read the four angles are not either, each flagged, in "
         "place of the 0.0 the wall once stood in with. Its alterations, its bounds and what still moves it (a "
         "segmenter's ragged edge, a lip on thick slices) are in its docstring.\n")
t = swap(t,
         "and the slabs' canal walls lean half as far as the posterior wall does, a cause in scanimport not found and "
         "worked around by reading corners from all the voxels in front of the canal's middle.",
         "and the canal's line (anatomy.wall_slope), which cuts the body from the arch and sets Panjabi's depths, "
         "reads each slab's wall on the same staircase the posterior wall was read on and leans on its own (18.7 "
         "degrees on the phantom with the notch), worked around for the corners by reading them from all the voxels "
         "in front of the canal's middle; it is the next to be read on the lattice.")
open(PATH, "w").write(t)
print("done")

"""Restate pedicle.py's module paragraph on the wall's error, and column.wall_corner's docstring."""
import sys

ROOT = sys.argv[1]


def swap(path, old, new):
    text = open(path).read()
    assert text.count(old) == 1, (path, text.count(old))
    open(path, "w").write(text.replace(old, new))


swap(ROOT + "/morphometry/pedicle.py",
     """all the chord and the transverse angle are not read. Where the grid lies within a few degrees of
the vertebra's own frame, as on most supine lumbar studies, the posterior wall's slope reads 1.8 to
4.2 degrees off on the phantoms' vertical walls (body.posterior_wall_slope), and the sagittal
angle takes that error with it (2.5 to 3.4 degrees high on the pitched phantoms at a tilt of 2
degrees); that reading of the wall is the next to be traced. The chord is the length of
""",
     """all the chord and the transverse angle are not read. The posterior wall is read on the scan's own
lattice from the vertebra's label (body.posterior_wall, which says how): on the wall study's
phantoms it read within 0.35 degrees on 1 mm slices and 0.79 on 2.5 mm ones, worst on grids
within 2 degrees of the vertebra's frame, where the reading it replaced, the front-most body
voxel of each layer, traced the lattice's staircase and erred up to 4.14 and 5.66, and the
sagittal angle with it. Where the wall is not read the sagittal angle is not either, with a note
saying why. The canal line the body is cut from the arch along (anatomy.wall_slope) still traces
that staircase and is the next to be fixed. The chord is the length of
""")

swap(ROOT + "/morphometry/column.py",
     """    and the plate the body's extreme along the plate's normal. All of v's voxels there and not
    only the body's: the body is cut from the arch along a line the canal's slabs give, which on
    the joint phantom leans half as far as the wall does, and so still shaves the wall's end
    where the column's line tilts against the vertebra's own axis.\"\"\"""",
     """    and the plate the body's extreme along the plate's normal. All of v's voxels there and not
    only the body's: the body is cut from the arch along the canal line (anatomy.wall_slope),
    which traces the lattice's staircase as the old reading of the wall did and leans on its own,
    18.7 degrees on a phantom with a basivertebral notch 4 mm deep, and so can shave the wall's
    end; that line is the next to be fixed.\"\"\"""")
print("done")

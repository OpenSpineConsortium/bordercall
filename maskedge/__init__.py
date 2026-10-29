"""Where a vertebra mask's surface lies against the bone's own edge in its CT.

Every measure morphometry takes is a measure of the mask, and a mask that reaches a millimetre
beyond the bone at each end-plate reads every height 2 mm tall and every disc 2 mm short, which
no comparison with the papers can tell from a population that is simply larger. The CT tells
them apart: along the surface's outward normal the bone's cortex is a peak and what lies
outside, the disc, the muscle or the fat, a level below it, and the bone's edge is where the
CT falls through half-way between the two, the half-maximum edge a reader's caliper on a
bone window is set to. The mask's own surface on the same line is where its linear
interpolation crosses one half, half-way between the last voxel centre inside and the first
outside. Their difference, read region by region of the vertebra (the two end-plates, the
body's lateral, anterior and posterior walls, the arch), is how far the mask stands off the
bone and so how far each height, width, depth and disc is off.

    python -m maskedge measure --ct CT.nii.gz --labels MASK.nii.gz --scheme enhance --study 0004 --out rows.csv
    python -m maskedge summary --rows rows.csv [more.csv ...]

The CT is read where it lies and never kept: nothing here is written but the rows. On the
morphometry phantom with a CT drawn from the same shapes, each voxel the mean of 27 points
inside it and blurred as a scanner blurs (tests/test_edge.py), the exact mask reads +0.14 to
+0.20 mm in every region, the half-maximum edge of a 0.8 mm cortex lying that much outside the
true surface; a mask grown by one voxel reads 0.74 to 1.04 mm further in and one shrunk by a
voxel 0.82 to 1.01 mm further out, each within 0.1 mm of the face cross's support along the
region's normal (0.76 to 0.95 mm), which is how far a one-voxel growth moves a surface.
"""

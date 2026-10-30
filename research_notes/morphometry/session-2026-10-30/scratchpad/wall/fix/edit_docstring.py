"""Rewrites posterior_wall's docstring from its second paragraph's cache sentence on; run once by path."""
import sys

path = sys.argv[1]
text = open(path).read()
start = text.index("    own and so shaved the wall's first row at one end.")
end = text.index("    gates the edges.\"\"\"") + len("    gates the edges.\"\"\"")
new = '''    own and so shaved the wall's first row at one end. Over the 98 phantom vertebrae of the
    cache of 30 October (four phantoms, the wall upright, leaned 5 degrees either way or 4
    forward, on seven grids from aligned with the frame to 25 degrees off, at 1 and 2.5 mm
    slices; research_notes/morphometry/handoff.md, its section of 30 October, records how it was
    built) that reading erred by up to 4.14 degrees on 1 mm slices and 5.66 on 2.5 mm, the worst
    on the grid tilted 2 degrees against the vertebra, and the angles taken against it carried
    the error one for one.

    It is now read on the scan's own lattice from the vertebra's whole label, not from the cut
    body, which gives only the window. Along the scan axis nearest the frame's y, stepping back
    (scan_step_back), a voxel of the label is the wall's last bone on its scan line where air
    lies one step behind it, bone fills WALL_RUN_MM in front of it and it lies within
    WALL_GATE_SHARE of the canal's depth of the canal's line (4.0 to 4.6 mm on the cache); the
    edge is half a step behind its centre, where a clean digitisation's surface lies on the mean;
    and of each scan line in the band (WALL_BAND_SHARE of the canal's width either side of the
    midline, at most WALL_BAND_MAX_MM either side) and the window (the middle WALL_HEIGHT_SHARE of
    the height the body's points in the band span) the most posterior edge is kept (wall_edges).
    At C2 the window ends at the top of the canal's full rings, so that the dens above the body,
    whose back stands a millimetre or two in front of the wall, does not reach it: on a cervical
    phantom on a grid 2 degrees off, a dens standing 1.5 mm in front read the wall 8.1 degrees off
    on 1 mm slices and 7.8 on 2.5 mm where the window ran up the dens, and 0.02 and 0.05 with it
    ended there (wall_window). The edges are fitted by the surface y = a + b z + c x + d x^2, x
    from the midline, by least trimmed squares, keeping WALL_TRIM_KEEP of them, from the whole set
    and from the window's lower, middle and upper halves (trimmed_start), polished by Tukey's
    biweight at a scale of WALL_BIWEIGHT_STEPS lattice steps along y (biweight), so that a notch
    or a hole's rim holding fewer than a quarter of the edges, at mid-height or off it, does not
    pull it; b is the wall's slope, and the edges more than a step off the fitted surface are left
    out of what follows. A notch holding more does pull it, and then leaves many edges off: one 8
    mm wide, 6 tall and 5 deep at mid-height read 29.2 degrees off on 1 mm slices and 29.5 on 2.5
    mm, with 66 and 69 per cent of the band's edges more than a step off, so the wall is not read
    where more than WALL_DROPPED_SHARE are (fit_refused). No reading of the cache, clean or
    altered as below, left more than 26 per cent off on 1 mm slices or 36 on 2.5 mm; the rule
    refuses some sound readings too, as a notch 5 mm wide, 10 tall and 4 deep on 1 mm slices,
    which left 51 per cent off and which the fit read 0.19 degrees off.

    The clamp: where some surface of that family keeps every edge's bone centre in front of it and
    its air centre behind it, by more than WALL_PART_MM, the label parts, and the slopes b of the
    surfaces that part it form a range (wall_slope_range: a program for the widest margin, then
    two for the range's ends) in which the true wall lies if the label is its clean digitisation;
    b is clamped into it. One voxel of bone behind the wall keeps the whole label from parting, so
    where it does not part, the one, two or at most WALL_ACROSS_MAX edges the fitted surface
    leaves furthest across (fit_crossing) are set aside in turn and the rest asked again
    (wall_freedom): with six such specks on each of the cache's vertebrae, 3 of the 294 labels so
    altered no longer parted on 1 mm slices and 1 of 294 on 2.5 mm, against 169 of 288 and 155 of
    294 with none set aside, and no speck moved a reading past 1.30 degrees. The clean phantoms'
    labels all part, one of the 98 with an edge set aside, and the truth lies in the range on 97
    of them; there the clamped reading errs by at most 0.35 degrees on 1 mm slices and 0.79 on 2.5
    mm (medians 0.07 and 0.19), where the fit alone erred by up to 1.24 and 1.18 (medians 0.10 and
    0.19). With the boundary's voxels flipped at random, or a ragged edge, the labels mostly do not
    part, and there the fit stands alone.

    The freedom is the range's width in degrees, or where the label does not part, the width of
    the range a clean digitisation of the fitted surface would leave on the same scan lines
    (clean_digitisation): how far the lattice pins the slope. Where the label parts it bounds the
    reading, which may lie anywhere in the range; where it does not, it bounds nothing, since the
    truth lay inside that range on only 21 of the 49 readings with flipped voxels on 1 mm slices
    and 31 of 49 on 2.5 mm, and 7 of 49 and 16 of 47 with the 0.3 mm ragged edge. Nor does it rank
    readings: over the cache's phantoms altered as below the rank correlation of the error with it
    was 0.18 on 1 mm slices and 0.12 on 2.5 mm, so a tight bound would refuse good readings with
    the bad. The wall is not read where the freedom passes WALL_FREEDOM_DEG, the bound
    pedicle.FREEDOM_DEG sets on the pedicle's climb, and measures flags a wall whose freedom
    passes WALL_FREE_FLAG_DEG (wall_flags), as on 3 of the 49 clean phantoms at 2.5 mm and none
    at 1 mm. Nor is it read without a full ring of the canal to place it, with fewer than
    G.MIN_CHORD_POINTS (eight) body points at the midline, edges in the band or edges within a
    step of the fitted surface, or where those edges span less than half the window.

    Over alterations of the cache's labels that keep the wall's slope (three notches, holes, an
    osteophyte, an axial scallop, a sagittal bow, flipped boundary voxels, the volume's edge across
    the body) the reading errs by at most 1.64 and 3.03 degrees, both on the bow, and none is
    refused for its dropped share. Two alterations go further. A segmenter's ragged edge leans the
    label's own wall, which no reader of the label tells from the wall: an edge rough by 0.3 mm
    over 3 mm moved the reading up to 2.56 and 3.97 degrees, and 0.74 and 1.67 less that lean;
    one rough by 0.5 mm over 4 mm up to 5.43 and 6.97, and 1.05 and 2.57 less its lean. A lip
    standing 1.5 mm proud of the wall from 3 mm inside the window's top, on 2.5 mm slices one or
    two of its six or seven layers, is told by none of the fit's statistics and reads up to 11.7
    degrees off there, 1.61 on 1 mm slices. On the cervical phantom (canal 24 mm wide over a body
    17 mm wide) the band is the whole WALL_BAND_MAX_MM either side, 12 of the body's 17 mm, and the
    wall read within 1.47 degrees on 1 mm slices and 1.32 on 2.5 mm; a band of a quarter of the
    body's width either side read within 0.92 and 1.72, better on one thickness and worse on the
    other, and was not taken. The canal's line shares the staircase, up to 3.7 degrees off the
    clean wall on 1 mm slices and 7.7 on 2.5 mm over the cache, and is the next to read on the
    lattice, since it still sets the body's cut, Panjabi's depths, canal_ap_lateral_film and the
    drawn lines, though here it only gates the edges."""'''
assert text.count("    own and so shaved the wall's first row at one end.") == 1
open(path, "w").write(text[:start] + new + text[end:])
